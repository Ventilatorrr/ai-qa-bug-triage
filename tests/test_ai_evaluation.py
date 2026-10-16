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

from tests.ai_evaluation import run_evaluation as runner
from tests.ai_evaluation.scenarios import load_scenarios


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
    assert len(requests) == len(report["attempts"]) == 6
    assert len(clients) == 6 and all(client.is_closed() for client in clients)
    assert [item["tc_id"] for item in report["attempts"]] == [f"TC-{number}" for number in range(351, 357)]
    assert "offline_suggestions" not in json.dumps(report["scenarios"])
    assert "dummy-key" not in json.dumps(report)

    for scenario, record, request in zip(scenarios_before, report["attempts"], requests, strict=True):
        assert request == record["request"]
        assert set(request) == {"model", "instructions", "input", "text", "store"}
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
def test_evaluation_pauses_after_observed_spend_threshold(monkeypatch):
    original = runner.offline_response
    requests = []

    def expensive(request, scenario):
        requests.append(request)
        body = original(request, scenario).json()
        body["usage"] = {"input_tokens": 1_000_000, "output_tokens": 0, "total_tokens": 1_000_000}
        return httpx2.Response(200, json=body)

    monkeypatch.setattr(runner, "offline_response", expensive)

    assert runner.main([]) == 1

    report = json.loads(next(runner.OUTPUT_ROOT.glob("*/run.json")).read_text(encoding="utf-8"))
    assert len(requests) == len(report["attempts"]) == 1
    assert report["attempts"][0]["execution"] == "completed"
    assert report["estimated_cost_usd"] == runner.SPEND_PAUSE_USD
    assert "spend" in report["stop_reason"]
