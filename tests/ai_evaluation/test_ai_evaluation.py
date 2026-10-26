"""Offline harness verification only; no test may create a live provider client."""

from copy import deepcopy
import json
import os
from pathlib import Path
import socket
import sqlite3
import sys

import httpx2
import pytest

from app.ai_openai import MAX_OUTPUT_TOKENS
from tests.ai_evaluation import run_evaluation as runner
from tests.ai_evaluation.scenarios import load_scenarios
from tests.ai_evaluation.quality_scenarios import load_quality_scenarios


DEFAULT_OUTPUT_ROOT = runner.OUTPUT_ROOT


@pytest.fixture(autouse=True)
def offline_only(monkeypatch, tmp_path):
    # Independent protection around the runner's own guards, even with inherited keys.
    for name in ("OPENAI_API_KEY", "AI_EVALUATION_ALLOW_LIVE", "OPENAI_BASE_URL", "OPENAI_LOG"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(socket.socket, "connect", runner.blocked_io)
    monkeypatch.setattr(socket.socket, "connect_ex", runner.blocked_io)
    monkeypatch.setattr(socket, "create_connection", runner.blocked_io)
    monkeypatch.setattr(sqlite3, "connect", runner.blocked_io)
    monkeypatch.setattr(runner, "OUTPUT_ROOT", tmp_path / "evidence")


# TC-357 | AC — — Default CLI exercises real prompt/adapter/validator with zero external IO.
def test_evaluation_offline_records_production_contracts(monkeypatch):
    requests = []
    original = runner.offline_response
    clients = []
    original_client = runner.create_client

    def record(request, scenario):
        requests.append(json.loads(request.content))
        return original(request, scenario)

    def create_client(**kwargs):
        client = original_client(**kwargs)
        clients.append(client)
        return client

    monkeypatch.setattr(runner, "offline_response", record)
    monkeypatch.setattr(runner, "create_client", create_client)
    scenarios_before = load_scenarios()

    assert runner.main([]) == 0

    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    assert report["mode"] == "offline"
    assert report["live_model_evaluated"] is False
    assert report["database_created"] is False
    assert report["stop_reason"] is None
    assert report["not_run"] == []
    assert report["dataset_sha256"] == runner.fingerprint(scenarios_before)
    assert len(report["protocol_sha256"]) == 64
    assert report["client_config"] == {"timeout_seconds": 60.0, "max_retries": 0}
    assert report["dataset_versions"] == ["1"]
    assert report["reasoning_effort"] is report["service_tier"] is None
    assert "explicit_medium" not in report
    assert "coverage" not in report
    assert len(requests) == len(report["attempts"]) == 6
    assert len(clients) == 6 and all(client.is_closed() for client in clients)
    assert [item["tc_id"] for item in report["attempts"]] == [f"TC-{number}" for number in range(351, 357)]
    assert "offline_suggestions" not in json.dumps(report["scenarios"])
    assert "dummy-key" not in json.dumps(report)

    for scenario, record, request in zip(scenarios_before, report["attempts"], requests, strict=True):
        assert request == record["request"]
        # Default evaluation sends production's generation settings unchanged.
        assert set(request) == {
            "model", "reasoning", "service_tier", "max_output_tokens", "instructions", "input", "text", "store",
        }
        assert request["max_output_tokens"] == MAX_OUTPUT_TOKENS
        assert request["reasoning"] == {"effort": "medium"}
        assert request["service_tier"] == "fast"
        assert record["requested_service_tier"] == "fast"
        assert record["dataset_version"] == "1"
        assert request["model"] == "gpt-6-luna"
        assert record["client_config"] == report["client_config"]
        assert request["store"] is False
        assert request["text"]["format"]["strict"] is True
        assert request["text"]["format"]["schema"] == record["generation_input"]["output_contract"]["schema"]
        assert request["instructions"].startswith(record["generation_input"]["instructions"])
        assert json.loads(request["input"][0]["content"]) == scenario["context"]
        assert record["provider"]["output_text"] == json.dumps(record["decoded_response"])
        assert record["provider"]["usage"]["input_tokens"] == 1200
        assert record["execution"] == "completed"
        assert all(record["mechanical_checks"].values())
        assert record["assessment"]["status"] == "offline_fixture_only"
        assert all(score["status"] == "Not assessed" for score in record["assessment"]["dimensions"].values())

    assert report["attempts"][3]["validated_output"]["suggestions"] == {
        "environment": "TestOS 4 / Aster Browser 12", "affected_version": "0.8.2",
        "severity": "Moderate", "priority": "Medium", "assignee_id": 12,
    }
    assert report["attempts"][3]["review_flags"] == []
    assert report["attempts"][4]["validated_output"] == {"outcome": "no_usable_suggestions", "suggestions": {}}
    assert load_scenarios() == scenarios_before


# TC-358 | AC — — Live mode cannot run under pytest/CI or without explicit opt-in.
@pytest.mark.parametrize("gate", ["pytest", "pytest_environment", "ci", "no_opt_in", "custom_endpoint"])
def test_evaluation_live_gates_precede_client_creation(monkeypatch, gate):
    def unexpected(*args, **kwargs):
        pytest.fail("A forbidden live invocation must not construct a client or evidence directory.")

    monkeypatch.setattr(runner, "new_output_directory", unexpected)
    monkeypatch.setenv("AI_EVALUATION_ALLOW_LIVE", "1")
    if gate != "pytest":
        monkeypatch.delitem(sys.modules, "pytest")
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    monkeypatch.delenv("CI", raising=False)
    if gate == "pytest_environment":
        monkeypatch.setenv("PYTEST_CURRENT_TEST", "fictional pytest test")
    elif gate == "ci":
        monkeypatch.setenv("CI", "true")
    elif gate == "no_opt_in":
        monkeypatch.delenv("AI_EVALUATION_ALLOW_LIVE")
    elif gate == "custom_endpoint":
        monkeypatch.setenv("OPENAI_BASE_URL", "https://invalid.example/v1")

    with pytest.raises(SystemExit) as error:
        runner.main(["--live"])

    assert error.value.code == 2
    with pytest.raises(RuntimeError):
        runner.create_client(live=True, scenario=load_scenarios()[0])
    with pytest.raises(RuntimeError):
        runner.run_evaluation(Path("unused"), live=True, pass_number=1)


# TC-359 | AC — — All SQLite access is blocked, including with cached configuration.
def test_evaluation_database_guard_restores_cached_configuration(monkeypatch):
    # Set a synthetic path before the first import too; never inspect an existing DB.
    monkeypatch.setenv("DATABASE_NAME", "fictional-cached-setting.db")
    from app import database

    monkeypatch.setattr(database, "DATABASE_NAME", "fictional-cached-setting.db")
    monkeypatch.setenv("OPENAI_API_KEY", "fictional-key-must-not-be-used")

    with runner.isolated_application(live=False) as path:
        assert path.is_absolute() and not path.exists()
        assert database.DATABASE_NAME == os.environ["DATABASE_NAME"] == str(path)
        assert "OPENAI_API_KEY" not in os.environ
        with pytest.raises(RuntimeError, match="forbidden"):
            database.get_connection()
        with pytest.raises(RuntimeError, match="forbidden"):
            sqlite3.connect("another-fictional-path.db")
        assert not path.exists()

    assert not path.parent.exists()
    assert database.DATABASE_NAME == "fictional-cached-setting.db"
    assert os.environ["DATABASE_NAME"] == "fictional-cached-setting.db"
    assert os.environ["OPENAI_API_KEY"] == "fictional-key-must-not-be-used"


# TC-360 | AC — — Failed calls stop once, retain safe evidence, and never retry.
@pytest.mark.parametrize("failure", ["timeout", "http_error", "malformed", "malformed_envelope", "refusal", "missing_usage", "wrong_model", "interrupt"])
def test_evaluation_records_errors_without_leaking_or_retrying(monkeypatch, failure):
    original = runner.offline_response
    requests = []
    clients = []
    original_client = runner.create_client
    private_text = "fictional-private-error-do-not-log"

    def create_client(**kwargs):
        client = original_client(**kwargs)
        clients.append(client)
        return client

    def fail(request, scenario):
        requests.append(request)
        if failure == "timeout":
            raise httpx2.ReadTimeout(private_text, request=request)
        if failure == "interrupt":
            raise KeyboardInterrupt(private_text)
        if failure == "http_error":
            return httpx2.Response(500, json={"error": {"message": private_text}})
        response = original(request, scenario)
        body = response.json()
        if failure == "malformed":
            body["output"][0]["content"][0]["text"] = "not JSON"
        elif failure == "malformed_envelope":
            body["output"][0]["content"][0]["text"] = json.dumps({"unexpected": []})
        elif failure == "refusal":
            body["output"][0]["content"] = [{"type": "refusal", "refusal": "Synthetic refusal"}]
        elif failure == "missing_usage":
            body.pop("usage")
        elif failure == "wrong_model":
            body["model"] = "unexpected-fictional-model"
        return httpx2.Response(200, json=body)

    monkeypatch.setattr(runner, "offline_response", fail)
    monkeypatch.setattr(runner, "create_client", create_client)

    try:
        result = runner.main(["--offline"])
    except KeyboardInterrupt:
        pytest.fail("Runner lost the interrupted attempt instead of saving failure evidence.")

    assert result == 1

    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    assert len(requests) == len(report["attempts"]) == 1
    assert len(clients) == 1 and clients[0].is_closed()
    assert report["stop_reason"]
    assert report["not_run"] == [f"EVAL-{letter}" for letter in "BCDEF"]
    assert report["attempts"][0]["execution"] == "error"
    assert set(report["attempts"][0]["error"]) == {"type", "http_status"}
    assert private_text not in json.dumps(report)
    assert report["live_model_evaluated"] is False
    assert report["database_created"] is False


# TC-361 | AC — — Review flags distinguish relevant support from conflict/contamination.
@pytest.mark.parametrize("index,suggestions,flagged", [
    (0, {"environment": "Unknown"}, True),
    (2, {"affected_version": "0.5.0"}, True),
    (3, {"environment": "TestOS 4 / Aster Browser 12", "affected_version": "0.8.2",
         "severity": "Moderate", "priority": "Medium", "assignee_id": 12}, False),
    (5, {"environment": "LegacyPrintOS 9"}, True),
])
def test_evaluation_review_flags_are_prompts_not_semantic_scores(index, suggestions, flagged):
    before = deepcopy(suggestions)

    flags = runner.review_flags(load_scenarios()[index], suggestions)

    assert bool(flags) is flagged
    assert suggestions == before
    # Even "Unknown" may be valid uncertainty; flagged values require human review.
    assert all(isinstance(flag, str) for flag in flags)


# TC-362 | AC — — Evidence output refuses overwrites and paths outside its owned root.
@pytest.mark.parametrize("destination", ["existing", "root", "outside"])
def test_evaluation_output_directory_is_new_and_confined(destination, tmp_path):
    assert DEFAULT_OUTPUT_ROOT == runner.ROOT / "ai-evaluation-results"
    assert not DEFAULT_OUTPUT_ROOT.is_relative_to(runner.ROOT / "test-results")

    runner.OUTPUT_ROOT.mkdir()
    existing = runner.OUTPUT_ROOT / "existing"
    existing.mkdir()
    sentinel = existing / "preserve.txt"
    sentinel.write_text("fictional existing evidence", encoding="utf-8")
    requested = {"existing": existing, "root": runner.OUTPUT_ROOT, "outside": tmp_path / "outside"}[destination]

    with pytest.raises((ValueError, FileExistsError)):
        runner.new_output_directory(str(requested))

    assert sentinel.read_text(encoding="utf-8") == "fictional existing evidence"
    assert not (tmp_path / "outside").exists()


# TC-363 | AC — — Stop subsequent requests at the observed-cost pause threshold.
# Standard-rate fallback reaches the threshold exactly; Fast/priority is billed at 2x.
@pytest.mark.parametrize("returned_tier,multiplier", [("default", 1), ("priority", 2)])
def test_evaluation_pauses_after_observed_spend_threshold(monkeypatch, returned_tier, multiplier):
    original = runner.offline_response
    requests = []

    def expensive(request, scenario):
        requests.append(request)
        body = original(request, scenario).json()
        body["usage"] = {"input_tokens": 1_000_000, "output_tokens": 0, "total_tokens": 1_000_000}
        body["service_tier"] = returned_tier
        return httpx2.Response(200, json=body)

    monkeypatch.setattr(runner, "offline_response", expensive)

    assert runner.main([]) == 1

    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    assert len(requests) == len(report["attempts"]) == 1
    assert report["attempts"][0]["execution"] == "completed"
    assert report["estimated_cost_usd"] == runner.SPEND_PAUSE_USD * multiplier
    assert "spend" in report["stop_reason"]


# TC-373 | AC — — Quality fixtures use the production schema; frozen A–F remain unchanged.
def test_quality_scenarios_preserve_schema_identity_and_baseline():
    cases = load_quality_scenarios()
    assert [case["id"] for case in cases] == ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6", "Q7", "Q11", "Q12"]
    assert [case["tc_id"] for case in cases] == [f"TC-{number}" for number in range(364, 373)]
    assert runner.fingerprint(load_scenarios()) == "f7ad0ba5cd12a4a612fe73f65ebd8821b19ffbadab09e156b63c84680376bbcc"
    with runner.isolated_application(live=False):
        from app.ai_context import AiTriageContext
        from app.ai_generation import build_generation_input

        for case in cases:
            context = AiTriageContext.model_validate(case["context"])
            generation = build_generation_input(context)
            assert generation["context"] == case["context"]
            assert len(context.recent_bugs) <= 5
            assert set(generation["context"]) == {"current_form", "recent_bugs", "eligible_assignees"}
            assert case["review"] not in json.dumps(generation)
            assert "INJECTION-WON" not in generation["instructions"]
    # Guard the revised Q2/Q3 identities and the distinguishing risk inputs.
    assert "INJECTION-WON-HISTORY" in cases[1]["context"]["recent_bugs"][0]["description"]
    assert '"role":"system"' in cases[2]["context"]["current_form"]["description"]
    assert len(cases[6]["context"]["recent_bugs"]) == 5
    assert cases[8]["context"]["recent_bugs"][0]["environment"] == "TestOS 4 (ARM64) / Aster Browser 12"
    cases[0]["context"]["current_form"]["title"] = "mutated local copy"
    assert load_quality_scenarios()[0]["context"]["current_form"]["title"] != "mutated local copy"


# TC-374 | AC — — Named/default/subset selection preserves order and independent repeats.
@pytest.mark.parametrize("selection,expected", [
    ({}, [f"EVAL-{letter}" for letter in "ABCDEF"]),
    ({"scenario_set": "baseline"}, [f"EVAL-{letter}" for letter in "ABCDEF"]),
    ({"scenario_set": "quality-batch-1"}, ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]),
    ({"scenario_set": "quality-batch-2"}, ["Q7", "Q11", "Q12", "Q11"]),
    ({"scenario_ids": ["Q11", "EVAL-D", "Q11"]}, ["Q11", "EVAL-D", "Q11"]),
])
def test_evaluation_selection_preserves_order_and_independent_repeats(selection, expected):
    selected = runner.select_scenarios(**selection)
    assert [case["id"] for case in selected] == expected
    before = deepcopy(selected)
    selected[0]["context"]["current_form"]["title"] = "changed in only this execution"
    assert selected[1:] == before[1:]
    assert runner.select_scenarios(**selection) == before


# TC-375 | AC — — Invalid/oversized selections fail before evidence, application or client IO.
@pytest.mark.parametrize("arguments,selection", [
    (["--scenario-set", "missing"], {"scenario_set": "missing"}),
    (["--scenarios", "Q9"], {"scenario_ids": ["Q9"]}),
    (["--scenarios"], {"scenario_ids": []}),
    (["--scenarios", ""], {"scenario_ids": [""]}),
    (["--scenarios"] + ["Q11"] * 7, {"scenario_ids": ["Q11"] * 7}),
    (["--scenario-set", "baseline", "--scenarios", "Q1"],
     {"scenario_set": "baseline", "scenario_ids": ["Q1"]}),
])
def test_evaluation_invalid_selection_precedes_io(monkeypatch, arguments, selection):
    def unexpected(*args, **kwargs):
        pytest.fail("Invalid selection must not perform application, evidence or provider IO.")

    monkeypatch.setattr(runner, "new_output_directory", unexpected)
    monkeypatch.setattr(runner, "isolated_application", unexpected)
    monkeypatch.setattr(runner, "create_client", unexpected)
    with pytest.raises(ValueError):
        runner.run_evaluation(Path("unused"), live=False, pass_number=1, **selection)
    with pytest.raises(SystemExit) as error:
        runner.main(arguments)
    assert error.value.code == 2
    assert not runner.OUTPUT_ROOT.exists()


# TC-376 | AC — — Each offline invocation runs only its selected batch and preserves evidence.
@pytest.mark.parametrize("arguments,expected", [
    (["--scenario-set", "quality-batch-1"], ["Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]),
    (["--scenario-set", "quality-batch-2"], ["Q7", "Q11", "Q12", "Q11"]),
    (["--scenarios", "Q11", "EVAL-D", "Q11"], ["Q11", "EVAL-D", "Q11"]),
])
def test_quality_offline_batches_record_production_requests_and_unique_executions(monkeypatch, arguments, expected):
    requests = []
    clients = []
    original_response = runner.offline_response
    original_client = runner.create_client

    def record(request, scenario):
        requests.append(json.loads(request.content))
        return original_response(request, scenario)

    def create_client(**kwargs):
        assert kwargs["live"] is False
        client = original_client(**kwargs)
        clients.append(client)
        return client

    monkeypatch.setattr(runner, "offline_response", record)
    monkeypatch.setattr(runner, "create_client", create_client)
    # Offline mode must ignore inherited live opt-in, credentials and endpoint.
    monkeypatch.setenv("AI_EVALUATION_ALLOW_LIVE", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "fictional-inherited-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://invalid.example/v1")
    assert runner.main(["--offline"] + arguments) == 0
    evidence = next(runner.OUTPUT_ROOT.glob("*/run.json"))
    report = json.loads(evidence.read_text(encoding="utf-8"))
    assert [item["scenario_id"] for item in report["attempts"]] == expected
    assert report["selection"]["scenario_ids"] == expected
    assert report["dataset_versions"] == sorted({"1" if item.startswith("EVAL-") else "quality-1" for item in expected})
    assert [item["dataset_version"] for item in report["attempts"]] == [
        "1" if item.startswith("EVAL-") else "quality-1" for item in expected
    ]
    assert len(requests) == len(clients) == len(expected) <= report["request_limit"] == 6
    assert all(client.is_closed() for client in clients)
    assert report["not_run"] == report["not_run_execution_ids"] == []
    assert report["stop_reason"] is None
    assert report["database_created"] is report["live_model_evaluated"] is False
    assert "coverage" not in report
    execution_ids = [item["execution_id"] for item in report["attempts"]]
    assert len(execution_ids) == len(set(execution_ids))
    assert execution_ids == [item["execution_id"] for item in report["execution_plan"]]
    for request, attempt, scenario in zip(requests, report["attempts"], report["scenarios"], strict=True):
        assert request == attempt["request"]
        assert json.loads(request["input"][0]["content"]) == scenario["context"]
        assert request["instructions"].startswith(attempt["generation_input"]["instructions"])
        assert request["store"] is False and request["text"]["format"]["strict"] is True
        assert attempt["client_config"] == {"timeout_seconds": 60.0, "max_retries": 0}
        assert attempt["execution"] == "completed" and all(attempt["mechanical_checks"].values())
        assert json.loads(attempt["provider"]["output_text"]) == attempt["decoded_response"]
        assert attempt["validator_exclusions"] == []
        assert attempt["assessment"]["status"] == "offline_fixture_only"
        assert all(value["status"] == "Not assessed" for value in attempt["assessment"]["dimensions"].values())
        assert "offline_suggestions" not in scenario
    repeats = [item for item in report["attempts"] if item["scenario_id"] == "Q11"]
    if repeats:
        assert [item["execution_id"] for item in repeats] == ["Q11:1", "Q11:2"]
        assert repeats[0]["tc_id"] == repeats[1]["tc_id"] == "TC-371"
        assert repeats[0]["generation_sha256"] == repeats[1]["generation_sha256"]
        assert repeats[0]["request"] == repeats[1]["request"]
        assert {"usefulness", "consistency"} <= repeats[0]["assessment"]["dimensions"].keys()
    assert "fictional-inherited-key" not in evidence.read_text(encoding="utf-8")
    before = evidence.read_bytes()
    # A refused overwrite or escaped destination must not issue another request.
    assert runner.main(["--offline", "--output", str(evidence.parent)] + arguments) == 2
    outside = runner.OUTPUT_ROOT.parent / "outside-evidence"
    assert runner.main(["--offline", "--output", str(outside)] + arguments) == 2
    assert not outside.exists() and evidence.read_bytes() == before
    assert len(requests) == len(expected)


# TC-377 | AC — — Raw model/contract failures survive filtering; selected failure stops once.
@pytest.mark.parametrize("failure", ["filtered", "malformed"])
def test_quality_raw_failures_remain_visible_without_semantic_pass(monkeypatch, failure):
    original = runner.offline_response
    requests = []
    attack = {"suggestions": [
        {"field": "status", "value": "Closed"},
        {"field": "title", "value": "INJECTION-WON-CONTRACT"},
    ]} if failure == "filtered" else {"status": "Closed"}

    def respond(request, scenario):
        requests.append(request)
        response = original(request, scenario)
        if scenario["id"] == "Q3":
            body = response.json()
            body["output"][0]["content"][0]["text"] = json.dumps(attack)
            return httpx2.Response(200, json=body)
        return response

    monkeypatch.setattr(runner, "offline_response", respond)
    assert runner.main(["--offline", "--scenarios", "Q3", "Q11", "Q11"]) == (0 if failure == "filtered" else 1)
    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    attempt = report["attempts"][0]
    assert attempt["decoded_response"] == json.loads(attempt["provider"]["output_text"]) == attack
    assert attempt["assessment"]["status"] == "offline_fixture_only"
    assert attempt["assessment"]["dimensions"]["injection_resistance"]["status"] == "Not assessed"
    assert attempt["assessment"]["critical_failure"] is None
    if failure == "filtered":
        assert attempt["validated_output"]["suggestions"] == {"title": "INJECTION-WON-CONTRACT"}
        assert attempt["validator_exclusions"] == [{"field": "status", "value": "Closed"}]
        assert len(requests) == 3
    else:
        assert attempt["execution"] == "error" and "validated_output" not in attempt
        assert len(requests) == 1 and report["stop_reason"]
        assert report["not_run"] == ["Q11", "Q11"]
        assert report["not_run_execution_ids"] == ["Q11:1", "Q11:2"]


# TC-379 | AC — — Explicit overrides change only the selected reasoning effort and/or service tier.
@pytest.mark.parametrize("reasoning_effort,service_tier", [
    ("low", None), ("medium", None), ("high", None),
    (None, "fast"), (None, "standard"), ("high", "standard"),
])
def test_evaluation_overrides_change_only_selected_settings(monkeypatch, reasoning_effort, service_tier):
    original = runner.offline_response
    requests = []

    def respond(request, scenario):
        requests.append(json.loads(request.content))
        return original(request, scenario)

    monkeypatch.setattr(runner, "offline_response", respond)
    overrides = ((["--reasoning-effort", reasoning_effort] if reasoning_effort else [])
                 + (["--service-tier", service_tier] if service_tier else []))
    assert runner.main(["--offline", "--scenarios", "EVAL-D", *overrides]) == 0
    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    attempt = report["attempts"][0]
    assert report["reasoning_effort"] == reasoning_effort and report["service_tier"] == service_tier

    from app.ai_openai import request_openai_suggestions

    scenario = runner.select_scenarios(scenario_ids=["EVAL-D"])[0]
    with runner.create_client(live=False, scenario=scenario) as client:
        request_openai_suggestions(deepcopy(attempt["generation_input"]), client=client)
    expected = dict(requests[-1])  # The production adapter's own request.
    if reasoning_effort:
        expected["reasoning"] = {"effort": reasoning_effort}
    if service_tier == "standard":
        expected.pop("service_tier")
    assert attempt["request"] == requests[0] == expected
    assert attempt["requested_service_tier"] == expected.get("service_tier")
    assert attempt["execution"] == "completed" and all(attempt["mechanical_checks"].values())


# TC-380 | AC — — Unsupported reasoning effort is rejected before evidence, application or provider IO.
@pytest.mark.parametrize("reasoning_effort", ["xhigh", ""])
def test_evaluation_invalid_reasoning_precedes_io(monkeypatch, reasoning_effort):
    def unexpected(*args, **kwargs):
        pytest.fail("Invalid reasoning configuration must not perform IO.")

    monkeypatch.setattr(runner, "new_output_directory", unexpected)
    monkeypatch.setattr(runner, "isolated_application", unexpected)
    monkeypatch.setattr(runner, "create_client", unexpected)
    with pytest.raises(ValueError):
        runner.run_evaluation(Path("unused"), live=False, pass_number=1, reasoning_effort=reasoning_effort)
    with pytest.raises(SystemExit) as error:
        runner.main(["--reasoning-effort", reasoning_effort])
    assert error.value.code == 2
    assert not runner.OUTPUT_ROOT.exists()


# TC-381 | AC — — SDK latency excludes setup; timing, raw failures and exclusions survive stops.
@pytest.mark.parametrize("failure", ["success", "filtered", "timeout", "http_error", "malformed"])
def test_evaluation_records_timing_and_failure_evidence(monkeypatch, failure):
    clock = [100.0]
    requests = []
    original_response = runner.offline_response
    original_client = runner.create_client
    private_text = "fictional-private-error-do-not-log"

    def create_client(**kwargs):
        clock[0] += 2.0
        return original_client(**kwargs)

    def respond(request, scenario):
        requests.append(json.loads(request.content))
        clock[0] += 3.0
        if failure == "timeout":
            raise httpx2.ReadTimeout(private_text, request=request)
        if failure == "http_error":
            return httpx2.Response(500, json={"error": {"message": private_text}})
        body = original_response(request, scenario).json()
        if failure == "malformed":
            body["output"][0]["content"][0]["text"] = "not JSON"
        elif failure == "filtered":
            raw = json.loads(body["output"][0]["content"][0]["text"])
            raw["suggestions"].append({"field": "status", "value": "Closed"})
            body["output"][0]["content"][0]["text"] = json.dumps(raw)
        return httpx2.Response(200, json=body)

    monkeypatch.setattr(runner, "monotonic", lambda: clock[0])
    monkeypatch.setattr(runner, "create_client", create_client)
    monkeypatch.setattr(runner, "offline_response", respond)
    succeeded = failure in {"success", "filtered"}
    assert runner.main(["--offline", "--scenarios", "Q1", "Q11"]) == (0 if succeeded else 1)
    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    assert len(requests) == len(report["attempts"]) == (2 if succeeded else 1)
    assert report["total_elapsed_seconds"] == (10.0 if succeeded else 5.0)
    assert report["not_run"] == ([] if succeeded else ["Q11"])
    assert report["not_run_execution_ids"] == ([] if succeeded else ["Q11:1"])
    for attempt in report["attempts"]:
        assert attempt["provider_call_seconds"] == 3.0
        assert attempt["elapsed_seconds"] == 5.0
        if failure in {"timeout", "http_error"}:
            assert attempt["provider_error"] == attempt["error"]
            assert attempt["provider_error"]["http_status"] == (500 if failure == "http_error" else None)
            assert "provider" not in attempt
        else:
            assert "provider_error" not in attempt
            assert "output_text" in attempt["provider"]
        if failure == "malformed":
            assert attempt["provider"]["output_text"] == "not JSON"
        if succeeded:
            assert attempt["validator_exclusions"] == ([{"field": "status", "value": "Closed"}] if failure == "filtered" else [])
            assert "status" not in attempt["validated_output"]["suggestions"]
    assert report["database_created"] is report["live_model_evaluated"] is False
    assert private_text not in json.dumps(report)


# TC-382 | AC — — Returned tier, cache-aware cost and usage details survive SDK serialization; unknown tiers cost 2x.
@pytest.mark.parametrize("returned_tier", ["fast", "priority", "default", "standard", None, "unknown"])
def test_evaluation_records_returned_tier_and_conservative_cost(monkeypatch, returned_tier):
    original_response = runner.offline_response

    def respond(request, scenario):
        body = original_response(request, scenario).json()
        if returned_tier is not None:
            body["service_tier"] = returned_tier
        body["usage"]["input_tokens_details"] = {"cached_tokens": 200, "cache_write_tokens": 300}
        body["usage"]["output_tokens_details"] = {"reasoning_tokens": 40}
        return httpx2.Response(200, json=body)

    monkeypatch.setattr(runner, "offline_response", respond)
    assert runner.main(["--offline", "--scenarios", "EVAL-D", "Q11"]) == 0
    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    multiplier = 1 if returned_tier in {"default", "standard"} else 2
    expected_cost = round(multiplier * (700 * 0.10 + 200 * 0.01 + 300 * 0.125 + 120 * 0.50) / 1_000_000, 8)
    assert len(report["attempts"]) == 2 and report["stop_reason"] is None
    for attempt in report["attempts"]:
        assert attempt["requested_service_tier"] == "fast"
        assert attempt["provider"]["service_tier"] == returned_tier
        assert attempt["provider"]["usage"]["input_tokens_details"]["cached_tokens"] == 200
        assert attempt["provider"]["usage"]["output_tokens_details"]["reasoning_tokens"] == 40
        assert attempt["estimated_cost_usd"] == expected_cost
        assert attempt["cost_estimate_basis"] == (
            "returned_service_tier" if returned_tier in {"fast", "priority", "default", "standard"}
            else "fast_rate_upper_bound_unconfirmed_tier"
        )
    assert report["estimated_cost_usd"] == round(2 * expected_cost, 8)


# TC-383 | AC — — Unsupported service-tier selectors are rejected before evidence, application or provider IO.
@pytest.mark.parametrize("service_tier", ["priority", ""])
def test_evaluation_invalid_service_tier_precedes_io(monkeypatch, service_tier):
    def unexpected(*args, **kwargs):
        pytest.fail("Invalid service tier must not perform IO.")

    monkeypatch.setattr(runner, "new_output_directory", unexpected)
    monkeypatch.setattr(runner, "isolated_application", unexpected)
    monkeypatch.setattr(runner, "create_client", unexpected)
    with pytest.raises(ValueError):
        runner.run_evaluation(Path("unused"), live=False, pass_number=1, service_tier=service_tier)
    with pytest.raises(SystemExit) as error:
        runner.main(["--service-tier", service_tier])
    assert error.value.code == 2
    assert not runner.OUTPUT_ROOT.exists()


# TC-384 | AC — — The recorded evaluation request equals the production adapter's own wire request.
def test_evaluation_default_request_matches_production_adapter(monkeypatch):
    ids = ["EVAL-D", "EVAL-F", "Q1", "Q5", "Q7", "Q11"]
    original = runner.offline_response
    requests = []

    def respond(request, scenario):
        requests.append(json.loads(request.content))
        return original(request, scenario)

    monkeypatch.setattr(runner, "offline_response", respond)
    assert runner.main(["--offline", "--scenarios", *ids]) == 0
    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    assert [a["scenario_id"] for a in report["attempts"]] == ids
    from app.ai_openai import request_openai_suggestions

    for attempt, wire in zip(report["attempts"], requests[:6], strict=True):
        assert attempt["request"] == wire
        # The production adapter's own wire request, with no evaluation recorder.
        scenario = runner.select_scenarios(scenario_ids=[attempt["scenario_id"]])[0]
        with runner.create_client(live=False, scenario=scenario) as client:
            raw = request_openai_suggestions(deepcopy(attempt["generation_input"]), client=client)
        assert requests[-1] == wire
        assert raw == attempt["decoded_response"]
        assert wire["reasoning"] == {"effort": "medium"} and wire["service_tier"] == "fast"
    assert len(requests) == 12


# TC-385 retired: --explicit-medium was removed; the default already sends Medium Fast.
