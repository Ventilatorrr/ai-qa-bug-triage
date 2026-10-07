from contextlib import closing
import sqlite3

import pytest


@pytest.mark.parametrize("operation", ["edit", "status"])
@pytest.mark.parametrize("delete_before_readback", [False, True], ids=["normal", "deleted"])
def test_bug_update_response_readback_after_commit(
    test_client, authenticated_user_factory, project_factory, member_factory,
    monkeypatch, operation, delete_before_readback,
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
        json={"title": "Original report", "fix_version": "1.2.0"},
    )
    assert created.status_code == 201
    before = created.json()
    url = f"/projects/{project['id']}/bugs/{before['bug_number']}"
    payload = {"title": "Edited report"} if operation == "edit" else {
        "status": "Open", "assignee_id": developer["user_id"],
    }
    expected = ("Edited report", "Triage", None) if operation == "edit" else (
        "Original report", "Open", developer["user_id"],
    )
    events = []

    class ReadbackConnection(sqlite3.Connection):
        committed = False

        def commit(self):
            super().commit()
            assert not self.in_transaction
            self.committed = True
            events.append("commit")

        def execute(self, sql, parameters=()):
            if self.committed:
                # Intercept only the response SELECT, after the real update commit.
                assert " ".join(sql.split()).startswith("SELECT id, project_id,")
                assert parameters == (project["id"], before["bug_number"])
                self.committed = False
                events.append("readback")
                with closing(database.get_connection()) as concurrent:
                    # A separate connection proves the update is already durable.
                    persisted = concurrent.execute(
                        "SELECT title, status, assignee_id FROM bugs WHERE project_id=? AND bug_number=?",
                        parameters,
                    ).fetchone()
                    assert persisted == expected
                    if delete_before_readback:
                        deleted = concurrent.execute(
                            "DELETE FROM bugs WHERE project_id=? AND bug_number=?", parameters,
                        )
                        assert deleted.rowcount == 1
                        concurrent.commit()
            return super().execute(sql, parameters)

    with monkeypatch.context() as patch:
        patch.setattr(bugs, "get_connection", lambda: sqlite3.connect(
            database.DATABASE_NAME, factory=ReadbackConnection,
        ))
        response = test_client.patch(
            url if operation == "edit" else f"{url}/status", headers=headers, json=payload,
        )

    assert events == ["commit", "readback"]
    stored = test_client.get(url, headers=headers)
    if delete_before_readback:
        assert response.status_code == stored.status_code == 404
        assert response.json() == stored.json() == {"detail": "Bug not found."}
    else:
        assert response.status_code == stored.status_code == 200
        result = response.json()
        assert stored.json() == result
        assert (result["title"], result["status"], result["assignee_id"]) == expected
        for field in ["id", "project_id", "bug_number", "created_at", "fix_version", "resolution"]:
            assert result[field] == before[field]
        assert result["updated_at"] != before["updated_at"]
