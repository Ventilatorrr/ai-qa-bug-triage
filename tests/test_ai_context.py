import pytest

from app.ai_suggestions import validate_suggestions
from app.schemas import AiAssistRequest


@pytest.fixture
def blank_snapshot():
    return dict.fromkeys([
        "title", "affected_version", "environment", "description",
        "steps_to_reproduce", "expected_result", "actual_result", "severity", "priority",
    ], "") | {"assignee_id": None}


@pytest.fixture
def disposable_database(test_client, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from app.database import DATABASE_NAME

    assert DATABASE_NAME == "test_bugtriage.db"


@pytest.fixture
def context_project(disposable_database, authenticated_user_factory, project_factory, member_factory):
    owner = authenticated_user_factory(email="owner@example.com")
    qa = authenticated_user_factory(email="qa@example.com")
    developer = authenticated_user_factory(email="dev@example.com")
    project = project_factory(owner["token"])
    for user, role in [(qa, "QA Analyst"), (developer, "Developer")]:
        member_factory(owner["token"], project["id"], user["user"]["email"], role)
    return {
        "owner": owner, "qa": qa, "developer": developer, "project": project,
        "base": f"/projects/{project['id']}",
        "headers": {"Authorization": f"Bearer {owner['token']}"},
    }


@pytest.fixture
def captured_contexts(monkeypatch, disposable_database):
    from app import ai_triage

    contexts = []
    original = ai_triage.request_suggestions

    def record(context, **kwargs):
        contexts.append(context)
        return original(context, **kwargs)

    monkeypatch.setattr(ai_triage, "request_suggestions", record)
    return contexts


def create_bug(client, context, **fields):
    response = client.post(f"{context['base']}/bugs", headers=context["headers"], json={"title": "Stored title"} | fields)
    assert response.status_code == 201
    return response.json()


def request_context(client, context, snapshot, captured, bug_number=None):
    url = context["base"] + (f"/bugs/{bug_number}" if bug_number is not None else "") + "/ai-assist"
    response = client.post(url, headers=context["headers"], json=snapshot)
    assert response.status_code == 503
    assert response.json() == {"detail": "AI assistance is not configured yet."}
    return captured[-1]


@pytest.mark.parametrize("edit", [False, True])
@pytest.mark.parametrize("populated", [False, True])
def test_ai_context_preserves_submitted_form_and_persisted_bugs(
    test_client, context_project, blank_snapshot, captured_contexts, edit, populated,
):
    from app.ai_context import build_triage_context

    stored = create_bug(
        test_client, context_project, description="Stored description", affected_version="0.1",
        environment="Stored environment", fix_version="0.2", assignee_id=context_project["developer"]["user_id"],
    )
    snapshot = blank_snapshot.copy()
    if populated:
        snapshot.update(
            title="  Unsaved title  ", affected_version="0.3", environment="  Unsaved environment  ",
            description="Unsaved\ncontent", steps_to_reproduce="1. Click", expected_result=" ",
            actual_result="Failure", severity="Moderate", priority="High", assignee_id=context_project["qa"]["user_id"],
        )
    context = request_context(
        test_client, context_project, snapshot, captured_contexts, stored["bug_number"] if edit else None,
    )
    assert len(captured_contexts) == 1
    assert context.current_form.model_dump() == snapshot
    assert [bug.id for bug in context.recent_bugs] == ([] if edit else [stored["id"]])
    if not edit:
        assert context.recent_bugs[0].model_dump() == {"id": stored["id"]} | {field: stored[field] for field in snapshot}
    assert set(context.model_dump()) == {"current_form", "recent_bugs", "eligible_assignees"}
    response = test_client.get(f"{context_project['base']}/bugs/{stored['bug_number']}", headers=context_project["headers"])
    assert response.status_code == 200
    assert response.json() == stored
    assert len(test_client.get(f"{context_project['base']}/bugs", headers=context_project["headers"]).json()) == 1

    form = AiAssistRequest(**snapshot)
    independent = build_triage_context(context_project["project"]["id"], stored["id"] if edit else None, form)
    independent.current_form.title = "Changed only in returned context"
    assert form.model_dump() == snapshot


@pytest.mark.parametrize("edit", [False, True])
def test_ai_context_retrieves_bounded_deterministic_same_project_history(
    test_client, context_project, project_factory, blank_snapshot, captured_contexts, edit,
):
    from app.ai_context import RECENT_BUG_LIMIT
    from app.database import get_connection

    bugs = [create_bug(test_client, context_project, title=f"History {index}") for index in range(RECENT_BUG_LIMIT + 3)]
    other = project_factory(context_project["owner"]["token"], name="Other project")
    foreign = test_client.post(
        f"/projects/{other['id']}/bugs", headers=context_project["headers"],
        json={"title": "Other-project history", "environment": "Other-project environment"},
    )
    assert foreign.status_code == 201
    # The API cannot set timestamps: set a tie and a newest low ID in the disposable database.
    conn = get_connection()
    try:
        conn.execute("UPDATE bugs SET updated_at = ? WHERE project_id = ?", ("2026-01-01T00:00:00+00:00", context_project["project"]["id"]))
        conn.execute("UPDATE bugs SET updated_at = ? WHERE id = ?", ("2026-01-02T00:00:00+00:00", bugs[0]["id"]))
        conn.commit()
    finally:
        conn.close()
    ordered_ids = [bugs[0]["id"]] + [bug["id"] for bug in reversed(bugs[1:])]
    excluded_id = bugs[0]["id"] if edit else None
    expected = [bug_id for bug_id in ordered_ids if bug_id != excluded_id][:RECENT_BUG_LIMIT]
    before = test_client.get(f"{context_project['base']}/bugs", headers=context_project["headers"]).json()
    for _ in range(2):
        context = request_context(test_client, context_project, blank_snapshot, captured_contexts, bugs[0]["bug_number"] if edit else None)
        assert [bug.id for bug in context.recent_bugs] == expected
        assert len(context.recent_bugs) == RECENT_BUG_LIMIT
        assert foreign.json()["id"] not in [bug.id for bug in context.recent_bugs]
    assert test_client.get(f"{context_project['base']}/bugs", headers=context_project["headers"]).json() == before


def test_ai_context_includes_only_current_assignable_project_members(
    test_client, context_project, authenticated_user_factory, project_factory, member_factory,
    blank_snapshot, captured_contexts,
):
    outsider = authenticated_user_factory(email="other@example.com")
    removed = authenticated_user_factory(email="removed@example.com")
    other = project_factory(context_project["owner"]["token"], name="Other project")
    member_factory(context_project["owner"]["token"], other["id"], outsider["user"]["email"], "QA Analyst")
    member_factory(context_project["owner"]["token"], context_project["project"]["id"], removed["user"]["email"], "Developer")
    for after_removal in (False, True):
        if after_removal:
            response = test_client.delete(
                f"{context_project['base']}/members/{removed['user_id']}", headers=context_project["headers"],
            )
            assert response.status_code == 200
        context = request_context(test_client, context_project, blank_snapshot, captured_contexts)
        expected = [
            {"user_id": context_project["qa"]["user_id"], "email": "qa@example.com", "role": "QA Analyst"},
            {"user_id": context_project["developer"]["user_id"], "email": "dev@example.com", "role": "Developer"},
        ] + ([] if after_removal else [{"user_id": removed["user_id"], "email": "removed@example.com", "role": "Developer"}])
        assert [member.model_dump() for member in context.eligible_assignees] == expected
        for user in (context_project["owner"], context_project["qa"], context_project["developer"], outsider, removed):
            result = validate_suggestions(
                {"suggestions": [{"field": "assignee_id", "value": user["user_id"]}]},
                eligible_assignee_ids=context.eligible_assignee_ids,
            )
            assert result.suggestions == ({"assignee_id": user["user_id"]} if user["user_id"] in {member["user_id"] for member in expected} else {})


def test_ai_context_supports_empty_project_history_and_assignees(
    test_client, authenticated_user_factory, project_factory, blank_snapshot, captured_contexts,
):
    owner = authenticated_user_factory()
    project = project_factory(owner["token"])
    context = request_context(
        test_client, {"base": f"/projects/{project['id']}", "headers": {"Authorization": f"Bearer {owner['token']}"}},
        blank_snapshot, captured_contexts,
    )
    assert context.current_form.model_dump() == blank_snapshot
    assert context.recent_bugs == []
    assert context.eligible_assignees == []
    assert context.eligible_assignee_ids == set()


@pytest.mark.parametrize("rejection,status", [
    ("missing_token", 401), ("invalid_token", 401), ("developer", 403),
    ("non_member", 404), ("removed_member", 404), ("wrong_project_bug", 404), ("non_triage", 409),
])
def test_ai_context_is_not_constructed_for_rejected_requests(
    test_client, context_project, authenticated_user_factory, project_factory,
    blank_snapshot, monkeypatch, rejection, status,
):
    from app import ai_triage

    def unexpected(*args):
        pytest.fail("Context must not be constructed before successful authorization.")

    monkeypatch.setattr(ai_triage, "build_triage_context", unexpected)
    headers = context_project["headers"]
    url = f"{context_project['base']}/ai-assist"
    if rejection == "missing_token":
        headers = {}
    elif rejection == "invalid_token":
        headers = {"Authorization": "Bearer invalid"}
    elif rejection in ("developer", "removed_member", "non_member"):
        actor = context_project["developer"] if rejection == "developer" else context_project["qa"]
        if rejection == "removed_member":
            assert test_client.delete(f"{context_project['base']}/members/{actor['user_id']}", headers=headers).status_code == 200
        elif rejection == "non_member":
            actor = authenticated_user_factory(email="nonmember@example.com")
        headers = {"Authorization": f"Bearer {actor['token']}"}
    else:
        bug = create_bug(test_client, context_project, assignee_id=context_project["developer"]["user_id"])
        if rejection == "wrong_project_bug":
            other = project_factory(context_project["owner"]["token"], name="Other project")
            url = f"/projects/{other['id']}/bugs/{bug['bug_number']}/ai-assist"
        else:
            assert test_client.patch(f"{context_project['base']}/bugs/{bug['bug_number']}/status", headers=headers, json={"status": "Open"}).status_code == 200
            url = f"{context_project['base']}/bugs/{bug['bug_number']}/ai-assist"
    response = test_client.post(url, headers=headers, json=blank_snapshot)
    assert response.status_code == status
