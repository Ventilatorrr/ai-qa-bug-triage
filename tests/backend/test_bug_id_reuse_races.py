import sqlite3
import threading

import pytest


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
