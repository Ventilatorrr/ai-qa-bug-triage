from copy import deepcopy

import pytest

from app.ai_suggestions import MalformedSuggestionResponse, validate_suggestions
from app.schemas import BugCreate


TEXT_FIELDS = [
    "title", "affected_version", "environment", "description",
    "steps_to_reproduce", "expected_result", "actual_result",
]


def validate(entries, eligible_ids=None):
    return validate_suggestions({"suggestions": entries}, eligible_assignee_ids=eligible_ids or set())


def test_ai_suggestions_accept_partial_set_without_mutating_input():
    raw = {"suggestions": [{"field": "description", "value": "  Observed\nbehavior  "}]}
    original = deepcopy(raw)
    result = validate_suggestions(raw, eligible_assignee_ids=set())
    assert result.outcome == "suggestions"
    assert result.suggestions == {"description": "  Observed\nbehavior  "}
    assert raw == original


def test_ai_suggestions_accept_all_supported_fields():
    expected = {field: f"Suggested {field}" for field in TEXT_FIELDS}
    expected.update(severity="Major", priority="High", assignee_id=7)
    result = validate([{"field": field, "value": value} for field, value in expected.items()], {7})
    assert result.suggestions == expected


@pytest.mark.parametrize("field", ["fix_version", "status", "resolution", "created_at", "updated_at", "unknown", "Title", "assignee"])
def test_ai_suggestions_exclude_unsupported_or_unmapped_fields(field):
    result = validate([{"field": field, "value": "Forbidden"}, {"field": "title", "value": "Valid"}])
    assert result.suggestions == {"title": "Valid"}


@pytest.mark.parametrize("field", TEXT_FIELDS)
@pytest.mark.parametrize("value", [12, True, [], {}])
def test_ai_suggestions_exclude_non_string_text_without_losing_valid_field(field, value):
    result = validate([{"field": field, "value": value}, {"field": "severity", "value": "Minor"}])
    assert result.suggestions == {"severity": "Minor"}


@pytest.mark.parametrize("field", TEXT_FIELDS + ["severity", "priority", "assignee_id"])
@pytest.mark.parametrize("value", [None, "", " \t\n"])
def test_ai_suggestions_omit_blank_values_without_clearing_fields(field, value):
    result = validate([{"field": field, "value": value}, {"field": "description", "value": "Valid"}])
    assert result.suggestions == {"description": "Valid"}


@pytest.mark.parametrize("field,value", [
    ("severity", "Critical"), ("severity", "major"), ("severity", " Major "),
    ("severity", []), ("priority", "Major"), ("priority", "high"), ("priority", {}),
])
def test_ai_suggestions_exclude_invalid_classification_without_losing_valid_field(field, value):
    result = validate([{"field": field, "value": value}, {"field": "title", "value": "Valid"}])
    assert result.suggestions == {"title": "Valid"}


@pytest.mark.parametrize("field,value", [
    ("severity", "Blocker"), ("severity", "Major"), ("severity", "Moderate"), ("severity", "Minor"),
    ("priority", "Urgent"), ("priority", "High"), ("priority", "Medium"), ("priority", "Low"),
])
def test_ai_suggestions_accept_classification_matching_bug_validation(field, value):
    result = validate([{"field": field, "value": value}])
    assert result.suggestions == {field: value}
    assert getattr(BugCreate(title="Valid", **result.suggestions), field) == value


@pytest.mark.parametrize("value", [1, 2, 3, 0, -1, "7", 7.0, True, [], {}])
def test_ai_suggestions_exclude_ineligible_or_non_integer_assignee(value):
    result = validate([{"field": "assignee_id", "value": value}, {"field": "title", "value": "Valid"}], {7})
    assert result.suggestions == {"title": "Valid"}


@pytest.mark.parametrize("values", [["One", "Two"], ["Valid", 12], [7, True], [7, 7.0]])
def test_ai_suggestions_exclude_conflicting_duplicate_field(values):
    field = "title" if isinstance(values[0], str) else "assignee_id"
    result = validate([{"field": field, "value": value} for value in values] +
                      [{"field": "priority", "value": "High"}], {7})
    assert result.suggestions == {"priority": "High"}


def test_ai_suggestions_collapse_identical_duplicates_and_ignore_blank_entries():
    result = validate([{"field": "title", "value": value} for value in ["Valid", None, "", " ", "Valid"]])
    assert result.suggestions == {"title": "Valid"}


@pytest.mark.parametrize("raw", [
    None, "not structured", [], {}, {"suggestions": None}, {"suggestions": {}},
    {"suggestions": [], "extra": True}, {"suggestions": ["title"]},
    {"suggestions": [{"value": "Missing field"}]}, {"suggestions": [{"field": []}]},
    {"suggestions": [{"field": "title", "value": "Valid", "extra": True}]},
])
def test_ai_suggestions_report_malformed_structure_as_error(raw):
    with pytest.raises(MalformedSuggestionResponse):
        validate_suggestions(raw, eligible_assignee_ids=set())


@pytest.mark.parametrize("entries", [
    [], [{"field": "title"}], [{"field": "title", "value": " "}],
    [{"field": "title", "value": None}], [{"field": "severity", "value": "Critical"}],
    [{"field": "status", "value": "Open"}],
    [{"field": "title", "value": "One"}, {"field": "title", "value": "Two"}],
])
def test_ai_suggestions_report_no_usable_suggestions_for_valid_structure(entries):
    result = validate(entries)
    assert result.outcome == "no_usable_suggestions"
    assert result.suggestions == {}


def test_ai_suggestions_use_current_assignable_project_member_context(
    test_client, authenticated_user_factory, project_factory, member_factory,
):
    owner = authenticated_user_factory(email="owner@example.com")
    qa = authenticated_user_factory(email="qa@example.com")
    developer = authenticated_user_factory(email="dev@example.com")
    outsider = authenticated_user_factory(email="outsider@example.com")
    project = project_factory(owner["token"])
    other = project_factory(owner["token"], name="Other")
    headers = {"Authorization": f"Bearer {owner['token']}"}
    base = f"/projects/{project['id']}/members"
    member_factory(owner["token"], project["id"], qa["user"]["email"], "QA Analyst")
    member_factory(owner["token"], project["id"], developer["user"]["email"], "Developer")
    member_factory(owner["token"], other["id"], outsider["user"]["email"], "Developer")
    for removed in (False, True):
        if removed:
            assert test_client.delete(f"{base}/{qa['user_id']}", headers=headers).status_code == 200
        response = test_client.get(base, headers=headers)
        assert response.status_code == 200
        eligible = {member["user_id"] for member in response.json() if member["role"] in ("QA Analyst", "Developer")}
        for user, valid in [(owner, False), (qa, not removed), (developer, True), (outsider, False)]:
            result = validate([{"field": "assignee_id", "value": user["user_id"]}], eligible)
            assert result.suggestions == ({"assignee_id": user["user_id"]} if valid else {})
