from contextlib import closing
import sqlite3

import pytest


# TC-139, TC-140 | Technical — Bug update response captured inside the write transaction, before commit
@pytest.mark.parametrize("operation", ["edit", "status"])
@pytest.mark.parametrize("delete_after_commit", [False, True], ids=["normal", "deleted"])
def test_bug_update_response_captured_before_commit(
    test_client, authenticated_user_factory, project_factory, member_factory,
    monkeypatch, operation, delete_after_commit,
):
    from app import database
    from app.api import bugs

    owner = authenticated_user_factory(email="readback-owner@example.com")
    developer = authenticated_user_factory(email="readback-developer@example.com")
    project = project_factory(owner["token"])
    member_factory(owner["token"], project["id"], developer["user"]["email"], "Developer")
    headers = {"Authorization": f"Bearer {owner['token']}"}
    created = test_client.post(
        f"/projects/{project['id']}/bugs", headers=headers,
        json={"title": "Original report", "affected_version": "1.2.0"},
    )
    assert created.status_code == 201
    before = created.json()
    url = f"/projects/{project['id']}/bugs/{before['bug_number']}"
    payload = {"title": "Edited report"} if operation == "edit" else {
        "status": "Open", "assignee_id": developer["user_id"],
    }
    original = ("Original report", "Triage", None)
    expected = ("Edited report", "Triage", None) if operation == "edit" else (
        "Original report", "Open", developer["user_id"],
    )
    durable = "SELECT title, status, assignee_id FROM bugs WHERE project_id=? AND bug_number=?"
    events = []

    class ReadbackConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            if " ".join(sql.split()).startswith("SELECT id, project_id,"):
                # The response is read inside the update's write transaction, before commit:
                # this connection sees the change, while another connection does not yet.
                assert self.in_transaction
                assert parameters == (project["id"], before["bug_number"])
                events.append("readback")
                with closing(database.get_connection()) as concurrent:
                    assert concurrent.execute(durable, parameters).fetchone() == original
            return super().execute(sql, parameters)

        def commit(self):
            super().commit()
            assert not self.in_transaction
            events.append("commit")
            with closing(database.get_connection()) as concurrent:
                # The committed change is durable and matches the captured response.
                assert concurrent.execute(durable, (project["id"], before["bug_number"])).fetchone() == expected
                if delete_after_commit:
                    # The project is deleted, as Delete Project does, right after the update commits.
                    for sql in ("DELETE FROM bugs WHERE project_id=?", "DELETE FROM project_members WHERE project_id=?",
                                "DELETE FROM projects WHERE id=?"):
                        concurrent.execute(sql, (project["id"],))
                    concurrent.commit()

    with monkeypatch.context() as patch:
        patch.setattr(bugs, "get_connection", lambda: sqlite3.connect(
            database.DATABASE_NAME, factory=ReadbackConnection,
        ))
        response = test_client.patch(
            url if operation == "edit" else f"{url}/status", headers=headers, json=payload,
        )

    assert events == ["readback", "commit"]
    # The retained response is the authorized change, whether or not the project still exists.
    assert response.status_code == 200
    result = response.json()
    assert (result["title"], result["status"], result["assignee_id"]) == expected
    for field in ["id", "project_id", "bug_number", "created_by", "created_at", "affected_version", "fix_version", "resolution"]:
        assert result[field] == before[field]
    assert result["updated_at"] != before["updated_at"]
    stored = test_client.get(url, headers=headers)
    if delete_after_commit:
        assert (stored.status_code, stored.json()) == (404, {"detail": "Project not found."})
    else:
        assert stored.status_code == 200 and stored.json() == result
