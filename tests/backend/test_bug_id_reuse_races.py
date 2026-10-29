import json
import sqlite3
import threading

import pytest

from tests.backend.test_ai_assist import blank_form
from tests.backend.test_ai_triage import offline_provider


# TC-485 | AC-012.3, AC-014.2, AC-009.5 — Bug deletion and bug/member reads authorized before a concurrent Delete Project cannot act on another user's project that reuses the deleted id (BUG-49 regression)
@pytest.mark.parametrize("operation", ["delete_bug", "list_bugs", "get_bug", "list_members"])
def test_bug_operation_cannot_affect_project_that_reuses_deleted_id(
    test_client, authenticated_user_factory, project_factory, monkeypatch, operation
):
    from app import database
    from app.api import bugs, projects

    owner = authenticated_user_factory(email="reuse-owner@example.com")
    victim = authenticated_user_factory(email="reuse-victim@example.com")
    owner_headers = {"Authorization": f"Bearer {owner['token']}"}
    victim_headers = {"Authorization": f"Bearer {victim['token']}"}
    project = project_factory(owner["token"], name="Owner Throwaway")
    base = f"/projects/{project['id']}"
    assert test_client.post(f"{base}/bugs", headers=owner_headers, json={"title": "Owner bug"}).status_code == 201
    gap = {}

    def delete_and_recycle():
        gap["delete"] = test_client.delete(base, headers=owner_headers)
        gap["victim"] = project_factory(victim["token"], name="Victim Private")
        gap["victim_bug"] = test_client.post(
            f"/projects/{gap['victim']['id']}/bugs", headers=victim_headers, json={"title": "Victim bug"},
        )

    module, next_sql = (projects, "JOIN users") if operation == "list_members" else (bugs, "FROM bugs")

    class GapConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            # After the membership check: delete the project and let another user's new
            # project recycle its id. Without a held lock this completes first.
            if next_sql in sql and "thread" not in gap:
                gap["thread"] = threading.Thread(target=delete_and_recycle)
                gap["thread"].start()
                gap["thread"].join(timeout=1)
            return super().execute(sql, parameters)

    request = {
        "delete_bug": ("DELETE", f"{base}/bugs/1"),
        "list_bugs": ("GET", f"{base}/bugs"),
        "get_bug": ("GET", f"{base}/bugs/1"),
        "list_members": ("GET", f"{base}/members"),
    }[operation]

    with monkeypatch.context() as patch:
        patch.setattr(module, "get_connection", lambda: sqlite3.connect(database.DATABASE_NAME, factory=GapConnection))
        response = test_client.request(*request, headers=owner_headers)
        gap["thread"].join(timeout=10)

    assert not gap["thread"].is_alive()
    assert gap["delete"].status_code == 200
    assert gap["victim"]["id"] == project["id"]  # SQLite reused the deleted maximum id.
    assert gap["victim_bug"].status_code == 201

    # The authorized request saw only the owner's original project.
    if operation == "delete_bug":
        assert response.status_code == 204
    elif operation == "list_bugs":
        assert [bug["title"] for bug in response.json()] == ["Owner bug"]
    elif operation == "get_bug":
        assert response.json()["title"] == "Owner bug"
    else:
        assert [member["email"] for member in response.json()] == ["reuse-owner@example.com"]

    # The other user's project and bug are untouched.
    victim_bug = test_client.get(f"{base}/bugs/1", headers=victim_headers)
    assert victim_bug.status_code == 200
    assert victim_bug.json()["title"] == "Victim bug"


# TC-510 | AC-012.3 — A bug edit or status update returns the authorized report it changed, never another user's report in a project that reuses the deleted project id and bug number after the update commits
@pytest.mark.parametrize("operation", ["edit", "status"])
def test_bug_update_response_never_returns_report_from_project_that_reuses_deleted_id(
    test_client, authenticated_user_factory, project_factory, member_factory, monkeypatch, operation
):
    from app import database
    from app.api import bugs

    owner = authenticated_user_factory(email="update-owner@example.com")
    developer = authenticated_user_factory(email="update-developer@example.com")
    victim = authenticated_user_factory(email="update-victim@example.com")
    owner_headers = {"Authorization": f"Bearer {owner['token']}"}
    victim_headers = {"Authorization": f"Bearer {victim['token']}"}
    project = project_factory(owner["token"], name="Owner Throwaway")
    base = f"/projects/{project['id']}"
    member_factory(owner["token"], project["id"], developer["user"]["email"], "Developer")
    assert test_client.post(f"{base}/bugs", headers=owner_headers, json={"title": "Owner bug"}).status_code == 201
    gap = {}

    def delete_and_recycle():
        gap["delete"] = test_client.delete(base, headers=owner_headers)
        gap["victim"] = project_factory(victim["token"], name="Victim Private")
        gap["victim_bug"] = test_client.post(
            f"/projects/{gap['victim']['id']}/bugs", headers=victim_headers,
            json={"title": "Victim private bug", "description": "Victim secret"},
        )

    class GapConnection(sqlite3.Connection):
        def commit(self):
            super().commit()
            # Once the update has committed and released its lock: delete the project and let
            # another user's new project reuse its id and bug number before anything else runs.
            if "thread" not in gap:
                gap["thread"] = threading.Thread(target=delete_and_recycle)
                gap["thread"].start()
                gap["thread"].join(timeout=10)

    url, body = {
        "edit": (f"{base}/bugs/1", {"title": "Owner edited"}),
        "status": (f"{base}/bugs/1/status", {"status": "Open", "assignee_id": developer["user_id"]}),
    }[operation]
    with monkeypatch.context() as patch:
        patch.setattr(bugs, "get_connection", lambda: sqlite3.connect(database.DATABASE_NAME, factory=GapConnection))
        response = test_client.patch(url, headers=owner_headers, json=body)
        gap["thread"].join(timeout=10)

    assert not gap["thread"].is_alive()
    assert gap["delete"].status_code == 200
    assert gap["victim"]["id"] == project["id"]  # SQLite reused the deleted maximum id.
    assert gap["victim_bug"].status_code == 201 and gap["victim_bug"].json()["bug_number"] == 1

    # The response is the owner's updated report, not the report now stored under the same numbers.
    assert response.status_code == 200
    updated = response.json()
    assert "Victim" not in response.text
    assert (updated["title"], updated["created_by"]) == ("Owner edited" if operation == "edit" else "Owner bug", owner["user_id"])
    if operation == "status":
        assert (updated["status"], updated["assignee_id"]) == ("Open", developer["user_id"])

    victim_bug = test_client.get(f"{base}/bugs/1", headers=victim_headers).json()
    assert (victim_bug["title"], victim_bug["status"]) == ("Victim private bug", "Triage")


# TC-511 | AC-022.1, AC-022.2 — AI Assist authorized before a concurrent Delete Project sends only the authorized project's reports and members to the offline provider, and does not accept an assignee from a project that reuses the deleted id
@pytest.mark.parametrize("edit", [False, True])
def test_ai_assist_never_uses_project_that_reuses_deleted_id(
    test_client, authenticated_user_factory, project_factory, member_factory, offline_provider, blank_form,
    monkeypatch, edit,
):
    from app import ai_context, database
    from app.api import ai_assist

    owner = authenticated_user_factory(email="assist-owner@example.com")
    developer = authenticated_user_factory(email="assist-developer@example.com")
    victim = authenticated_user_factory(email="assist-victim@example.com")
    victim_developer = authenticated_user_factory(email="assist-victim-developer@example.com")
    owner_headers = {"Authorization": f"Bearer {owner['token']}"}
    victim_headers = {"Authorization": f"Bearer {victim['token']}"}
    project = project_factory(owner["token"], name="Owner Throwaway")
    base = f"/projects/{project['id']}"
    member_factory(owner["token"], project["id"], developer["user"]["email"], "Developer")
    for title in ("Owner report", "Owner history"):
        assert test_client.post(f"{base}/bugs", headers=owner_headers, json={"title": title}).status_code == 201
    offline_provider["raw"] = {"suggestions": [
        {"field": "assignee_id", "value": victim_developer["user_id"]},
        {"field": "title", "value": "Suggested title"},
    ]}
    gap = {}

    def delete_and_recycle():
        gap["delete"] = test_client.delete(base, headers=owner_headers)
        gap["victim"] = project_factory(victim["token"], name="Victim Private")
        member_factory(victim["token"], gap["victim"]["id"], victim_developer["user"]["email"], "Developer")
        gap["victim_bug"] = test_client.post(
            f"/projects/{gap['victim']['id']}/bugs", headers=victim_headers, json={"title": "Victim private report"},
        )

    class GapConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            # After authorization, before the history read: delete the project and let another
            # user's new project reuse its id. A held read snapshot makes the deletion wait.
            if "ORDER BY updated_at DESC" in sql and "thread" not in gap:
                gap["thread"] = threading.Thread(target=delete_and_recycle)
                gap["thread"].start()
                gap["thread"].join(timeout=1)
            return super().execute(sql, parameters)

    # The provider answers only once the replacement exists, so validation after generation sees it.
    offline_provider["on_request"] = lambda: gap["thread"].join(timeout=10)
    url = f"{base}/bugs/1/ai-assist" if edit else f"{base}/ai-assist"
    with monkeypatch.context() as patch:
        connect = lambda: sqlite3.connect(database.DATABASE_NAME, factory=GapConnection)
        patch.setattr(ai_assist, "get_connection", connect)
        patch.setattr(ai_context, "get_connection", connect)
        response = test_client.post(url, headers=owner_headers, json=blank_form)
        gap["thread"].join(timeout=10)

    assert not gap["thread"].is_alive()
    assert gap["delete"].status_code == 200
    assert gap["victim"]["id"] == project["id"]  # SQLite reused the deleted maximum id.
    assert gap["victim_bug"].status_code == 201

    # Only the authorized project's reports and members reached the provider.
    assert len(offline_provider["requests"]) == 1
    sent = json.loads(offline_provider["requests"][0]["input"][0]["content"])
    assert [bug["title"] for bug in sent["recent_bugs"]] == (["Owner history"] if edit else ["Owner history", "Owner report"])
    assert [member["user_id"] for member in sent["eligible_assignees"]] == [developer["user_id"]]
    assert "victim" not in json.dumps(offline_provider["requests"]).lower()
    # The replacement project's member is not accepted as an assignee suggestion.
    assert response.status_code == 200
    assert response.json() == {"outcome": "suggestions", "suggestions": {"title": "Suggested title"}}
