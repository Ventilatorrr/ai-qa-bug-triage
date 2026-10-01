from copy import deepcopy
import socket
import sqlite3

import pytest

from app import ai_response
from app.ai_suggestions import MalformedSuggestionResponse, validate_suggestions
from app.schemas import AiAssistRequest


@pytest.fixture
def response_context(test_client):
    # Import database-dependent context models after disposable fixture setup.
    from app.ai_context import AiTriageContext, AssignableMemberContext, HistoricalBugContext
    from app.database import DATABASE_NAME

    assert DATABASE_NAME == "test_bugtriage.db"
    form = AiAssistRequest(
        title="Unsaved title", affected_version="", environment="",
        description="Current draft", steps_to_reproduce="",
        expected_result="", actual_result="", severity="",
        priority="", assignee_id=None,
    )
    return AiTriageContext(
        current_form=form,
        recent_bugs=[HistoricalBugContext(**(form.model_dump() | {
            "id": 12, "title": "Historical bug", "assignee_id": 99,
        }))],
        eligible_assignees=[
            AssignableMemberContext(user_id=7, email="qa@example.com", role="QA Analyst"),
            AssignableMemberContext(user_id=8, email="dev@example.com", role="Developer"),
        ],
    )


def test_ai_response_delegates_to_validator_and_returns_its_result(response_context, monkeypatch):
    raw = {"suggestions": [{"field": "title", "value": "Suggested title"}]}
    validated = validate_suggestions(raw, eligible_assignee_ids={7, 8})
    calls = []

    def validator(data, *, eligible_assignee_ids):
        calls.append((data, eligible_assignee_ids))
        return validated

    monkeypatch.setattr(ai_response, "validate_suggestions", validator)
    assert ai_response.process_provider_response(response_context, raw) is validated
    assert len(calls) == 1
    assert calls[0][0] is raw
    assert calls[0][1] == response_context.eligible_assignee_ids


def test_ai_response_retains_partial_valid_suggestions(response_context):
    raw = {"suggestions": [
        {"field": "title", "value": "Better title"},
        {"field": "priority", "value": "High"},
        {"field": "severity", "value": "Critical"},
        {"field": "description", "value": 42},
        {"field": "status", "value": "Closed"},
    ]}
    result = ai_response.process_provider_response(response_context, raw)
    assert result.outcome == "suggestions"
    assert result.suggestions == {"title": "Better title", "priority": "High"}


@pytest.mark.parametrize("assignee_id,accepted", [(7, True), (8, True), (99, False), (98, False)])
def test_ai_response_uses_only_context_assignee_eligibility(response_context, assignee_id, accepted):
    # 99 appears in history; 98 represents a no-longer-eligible member.
    raw = {"suggestions": [{"field": "assignee_id", "value": assignee_id}]}
    result = ai_response.process_provider_response(response_context, raw)
    assert result.suggestions == ({"assignee_id": assignee_id} if accepted else {})
    if accepted:
        response_context.eligible_assignees = [
            member for member in response_context.eligible_assignees if member.user_id != assignee_id
        ]
        assert ai_response.process_provider_response(response_context, raw).outcome == "no_usable_suggestions"


@pytest.mark.parametrize("entries", [[], [
    {"field": "title", "value": " "},
    {"field": "environment", "value": None},
    {"field": "priority", "value": "Invalid"},
]])
def test_ai_response_preserves_no_usable_suggestions_outcome(response_context, entries):
    result = ai_response.process_provider_response(response_context, {"suggestions": entries})
    assert result.outcome == "no_usable_suggestions"
    assert result.suggestions == {}


@pytest.mark.parametrize("raw", [None, {"suggestions": {}}, {"suggestions": ["title"]}, {
    "suggestions": [{"field": "assignee_id", "value": 99}], "eligible_assignee_ids": [99],
}])
def test_ai_response_propagates_malformed_response(response_context, raw):
    with pytest.raises(MalformedSuggestionResponse):
        ai_response.process_provider_response(response_context, raw)


def test_ai_response_preserves_conflicting_duplicate_behavior(response_context):
    result = ai_response.process_provider_response(response_context, {"suggestions": [
        {"field": "title", "value": "First title"},
        {"field": "title", "value": "Conflicting title"},
        {"field": "severity", "value": "Minor"},
    ]})
    assert result.suggestions == {"severity": "Minor"}


def test_ai_response_has_no_mutation_database_or_provider_side_effects(response_context, monkeypatch):
    from app import ai_context, ai_triage, database

    def unexpected(*args, **kwargs):
        pytest.fail("Response processing must not access the database or call a provider.")

    raw = {"suggestions": [{"field": "title", "value": "Suggested title"}]}
    raw_before = deepcopy(raw)
    context_before = response_context.model_dump(mode="json")
    with monkeypatch.context() as guards:
        guards.setattr(ai_context, "get_connection", unexpected)
        guards.setattr(database, "get_connection", unexpected)
        guards.setattr(sqlite3, "connect", unexpected)
        guards.setattr(ai_triage, "request_suggestions", unexpected)
        guards.setattr(socket, "socket", unexpected)
        result = ai_response.process_provider_response(response_context, raw)
    assert result.suggestions == {"title": "Suggested title"}
    assert raw == raw_before
    assert response_context.model_dump(mode="json") == context_before
    result.suggestions["title"] = "Changed result"
    assert raw == raw_before
    assert response_context.model_dump(mode="json") == context_before
