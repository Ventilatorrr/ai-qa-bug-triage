"""Explicit CLI only. Default execution uses an in-memory SDK transport."""

import argparse
from contextlib import ExitStack, contextmanager
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
import os
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import tempfile
from time import monotonic
from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from tests.ai_evaluation.scenarios import DATASET_VERSION, load_scenarios


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_ROOT = ROOT / "test-results" / "ai-evaluation"
DIMENSIONS = ("factual_grounding", "current_form_primacy", "history_use", "abstention", "schema_validity")
SPEND_PAUSE_USD = 0.10  # Observed usage threshold, not a per-request monetary cap.


def blocked_io(*args, **kwargs):
    raise RuntimeError("Evaluation attempted forbidden database/network access.")


def require_live_authorization():
    if "pytest" in sys.modules or "PYTEST_CURRENT_TEST" in os.environ or "CI" in os.environ:
        raise RuntimeError("Live evaluation is forbidden under pytest or CI.")
    if os.getenv("AI_EVALUATION_ALLOW_LIVE") != "1":
        raise RuntimeError("Live execution needs AI_EVALUATION_ALLOW_LIVE=1 after human approval.")
    if "OPENAI_BASE_URL" in os.environ:
        raise RuntimeError("Custom provider endpoints are not supported by this evaluation.")


@contextmanager
def isolated_application(*, live):
    """Configure before imports; rebind cached configuration; never open SQLite."""
    with tempfile.TemporaryDirectory(prefix="ai-qa-evaluation-") as directory, ExitStack() as stack:
        path = (Path(directory) / "unused-evaluation.db").resolve()
        assert not path.exists()
        stack.enter_context(patch.dict(os.environ, {"DATABASE_NAME": str(path)}))
        stack.enter_context(patch.object(sqlite3, "connect", blocked_io))
        if not live:
            # No inherited provider credentials or endpoint can influence offline SDK setup.
            for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_ORG_ID", "OPENAI_PROJECT_ID"):
                os.environ.pop(name, None)
            for name in ("connect", "connect_ex"):
                stack.enter_context(patch.object(socket.socket, name, blocked_io))
            stack.enter_context(patch.object(socket, "create_connection", blocked_io))

        from app import database

        stack.enter_context(patch.object(database, "DATABASE_NAME", str(path)))
        assert database.DATABASE_NAME == os.environ["DATABASE_NAME"] == str(path)
        yield path
        assert not path.exists(), "Evaluation must never create a SQLite database."


def offline_response(request, scenario):
    """Synthetic SDK response only; this is not model-quality evidence."""
    import httpx2

    return httpx2.Response(200, json={
        "id": "resp_offline_evaluation", "object": "response", "created_at": 0,
        "model": "gpt-6-luna", "status": "completed",
        "usage": {"input_tokens": 1200, "output_tokens": 120, "total_tokens": 1320},
        "output": [{
            "id": "msg_offline_evaluation", "type": "message", "role": "assistant", "status": "completed",
            "content": [{"type": "output_text", "text": json.dumps({
                "suggestions": scenario["offline_suggestions"],
            }), "annotations": []}],
        }],
    })


def create_client(*, live, scenario):
    if live:
        require_live_authorization()
        from app.ai_triage import create_openai_client

        key = (os.getenv("OPENAI_API_KEY") or "").strip()
        if not key:
            raise RuntimeError("OPENAI_API_KEY is required; never pass it on the command line.")
        client = create_openai_client(key)
        if str(client.base_url) != "https://api.openai.com/v1/":
            client.close()
            raise RuntimeError("Unexpected provider endpoint; no request was sent.")
        return client

    import httpx2
    from openai import OpenAI

    return OpenAI(
        api_key="offline-evaluation-dummy-key", base_url="https://api.openai.com/v1",
        timeout=60.0, max_retries=0,
        http_client=httpx2.Client(transport=httpx2.MockTransport(lambda request: offline_response(request, scenario))),
    )


class RecordingResponses:
    """Forward the production request unchanged; retain allowlisted evidence only."""

    def __init__(self, client, record):
        self.client = client
        self.record = record

    def create(self, **kwargs):
        self.record["request"] = deepcopy(kwargs)
        response = self.client.responses.create(**kwargs)
        self.record["provider"] = {
            "response_id": response.id, "request_id": getattr(response, "_request_id", None),
            "model": response.model, "status": response.status,
            "output_text": response.output_text,
            "output": [item.model_dump(mode="json") for item in response.output],
            "usage": response.usage.model_dump(mode="json") if response.usage else None,
        }
        return response


def review_flags(scenario, suggestions):
    """Conservative review prompts, never automatic semantic pass/fail scores."""
    flags = []
    if scenario["id"] in {"EVAL-A", "EVAL-E"} and {"environment", "affected_version"} & suggestions.keys():
        flags.append("Review proposed factual fields with no supporting history: uncertainty or unsupported invention?")
    if scenario["id"] == "EVAL-C" and (
        suggestions.get("affected_version") == "0.5.0"
        or suggestions.get("environment") == "TestOS 2 / Aster Browser 9"
    ):
        flags.append("Historical field value conflicts with explicit current retest information.")
    if scenario["id"] == "EVAL-F" and (
        suggestions.get("affected_version") == "0.2.0" or suggestions.get("environment") == "LegacyPrintOS 9"
    ):
        flags.append("Unrelated historical field value needs grounding review.")
    return flags


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def new_output_directory(requested):
    path = (Path(requested) if requested else OUTPUT_ROOT / (
        datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8]
    )).resolve()
    if not path.is_relative_to(OUTPUT_ROOT.resolve()) or path == OUTPUT_ROOT.resolve():
        raise ValueError("Output must be a new child directory under test-results/ai-evaluation.")
    path.mkdir(parents=True, exist_ok=False)
    return path


def run_evaluation(output, *, live, pass_number):
    """Six serial attempts at most. All semantic assessments begin unassessed."""
    if live:
        require_live_authorization()
    scenarios = load_scenarios()
    protocol = (ROOT / "docs" / "ai-testing-strategy.md").read_text(encoding="utf-8")
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "diff", "--quiet", "HEAD"], cwd=ROOT).returncode != 0
    report = {
        "mode": "live" if live else "offline", "live_model_evaluated": False,
        "date_utc": datetime.now(timezone.utc).isoformat(), "revision": revision, "tracked_changes": dirty,
        "sdk_version": version("openai"), "dataset_version": DATASET_VERSION,
        "dataset_sha256": fingerprint(scenarios), "protocol_sha256": sha256(protocol.encode()).hexdigest(),
        "scenarios": [{key: value for key, value in case.items() if key != "offline_suggestions"} for case in scenarios],
        "protocol": protocol, "pass_number": pass_number, "request_limit": 6,
        "client_config": {"timeout_seconds": 60.0, "max_retries": 0},
        "cost_assumption": "USD, Standard short context, $0.10/M input + $0.50/M output; 2026-10-16 public pricing; offline usage synthetic",
        "coverage": "AC-019.2 remains Partial pending live execution and human review.",
        "attempts": [], "not_run": [case["id"] for case in scenarios],
        "estimated_cost_usd": 0.0, "stop_reason": None,
    }
    with isolated_application(live=live) as database_path:
        from app.ai_context import AiTriageContext
        from app.ai_generation import build_generation_input
        from app.ai_openai import request_openai_suggestions
        from app.ai_response import process_provider_response

        if len(scenarios) != 6:
            raise RuntimeError("This protocol requires exactly six scenarios.")
        contexts = [AiTriageContext.model_validate(case["context"]) for case in scenarios]
        for scenario, context in zip(scenarios, contexts, strict=True):
            record = {
                "scenario_id": scenario["id"], "tc_id": scenario["tc_id"],
                "date_utc": datetime.now(timezone.utc).isoformat(),
                "purpose": scenario["purpose"], "review_guidance": scenario["review"],
                "assessment": {"status": "pending_human_review" if live else "offline_fixture_only",
                               "dimensions": {name: {"status": "Not assessed", "rationale": ""} for name in DIMENSIONS},
                               "critical_failure": None, "reviewer": None},
            }
            report["attempts"].append(record)
            started = monotonic()
            try:
                before = context.model_dump(mode="json")
                generation_input = build_generation_input(context)
                record["generation_input"] = generation_input
                record["generation_sha256"] = fingerprint(generation_input)
                with create_client(live=live, scenario=scenario) as client:
                    record["client_config"] = {"timeout_seconds": client.timeout, "max_retries": client.max_retries}
                    if record["client_config"] != report["client_config"]:
                        raise RuntimeError("Unexpected client timeout/retry configuration; no request sent.")
                    raw = request_openai_suggestions(
                        generation_input, client=SimpleNamespace(responses=RecordingResponses(client, record)),
                    )
                record["decoded_response"] = raw
                result = process_provider_response(context, raw)
                record["validated_output"] = {"outcome": result.outcome, "suggestions": result.suggestions}
                record["validator_exclusions"] = [entry for entry in raw["suggestions"] if (
                    entry["field"] not in result.suggestions
                    or type(entry.get("value")) is not type(result.suggestions[entry["field"]])
                    or entry.get("value") != result.suggestions[entry["field"]]
                )]
                record["review_flags"] = review_flags(scenario, result.suggestions)
                provider = record["provider"]
                usage = provider["usage"]
                checks = {
                    "context_unchanged": before == context.model_dump(mode="json"),
                    "provider_model_matches": provider["model"] == record["request"]["model"] or provider["model"].startswith(record["request"]["model"] + "-"),
                    "usage_recorded": usage is not None and all(
                        type(usage.get(name)) is int and usage[name] >= 0 for name in ("input_tokens", "output_tokens")
                    ),
                }
                record["mechanical_checks"] = checks
                if not all(checks.values()):
                    raise RuntimeError("Mechanical evidence checks failed.")
                record["execution"] = "completed"
            except (Exception, KeyboardInterrupt) as error:
                # No exception messages, HTTP headers or environment values in evidence/stdout.
                record["execution"] = "error"
                record["error"] = {"type": type(error).__name__, "http_status": getattr(error, "status_code", None)}
                report["stop_reason"] = "Attempt failed; no retry. Remaining scenarios were not run."
            usage = record.get("provider", {}).get("usage")
            if usage and all(type(usage.get(name)) is int and usage[name] >= 0 for name in ("input_tokens", "output_tokens")):
                record["estimated_cost_usd"] = round((usage["input_tokens"] * 0.10 + usage["output_tokens"] * 0.50) / 1_000_000, 8)
                report["estimated_cost_usd"] = round(report["estimated_cost_usd"] + record["estimated_cost_usd"], 8)
            if live and "provider" in record:
                report["live_model_evaluated"] = True
            record["elapsed_seconds"] = round(monotonic() - started, 3)
            if report["estimated_cost_usd"] >= SPEND_PAUSE_USD:
                report["stop_reason"] = "Observed estimated spend reached pause threshold; no further request."
            report["not_run"] = [case["id"] for case in scenarios[len(report["attempts"]):]]
            report["database_created"] = database_path.exists()
            (output / "run.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if report["stop_reason"]:
                break
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--offline", action="store_true", help="Default: synthetic responses, no external network.")
    mode.add_argument("--live", action="store_true", help="Requires separate human approval and explicit environment opt-in.")
    parser.add_argument("--output", help="New child directory under test-results/ai-evaluation.")
    parser.add_argument("--pass-number", type=int, choices=(1, 2), default=1)
    args = parser.parse_args(argv)
    if args.live:
        try:
            require_live_authorization()
        except RuntimeError as error:
            parser.error(str(error))
    try:
        output = new_output_directory(args.output)
        report = run_evaluation(output, live=args.live, pass_number=args.pass_number)
    except Exception as error:
        print(f"Evaluation stopped: {type(error).__name__}; no exception details logged.", file=sys.stderr)
        return 2
    print(f"{report['mode']}: {len(report['attempts'])}/6 attempts; evidence: {output / 'run.json'}")
    print("No semantic pass claimed; AC-019.2 remains Partial.")
    return 1 if report["stop_reason"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
