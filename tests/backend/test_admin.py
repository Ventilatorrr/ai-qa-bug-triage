from contextlib import closing
import sqlite3

from fastapi.testclient import TestClient
import pytest

from tests.backend.test_demo import demo_projects, start_demo, team_refs


TABLES = ("users", "projects", "project_members", "bugs", "ai_requests", "demos", "demo_accounts")


def snapshot(test_database):
    from app import database

    assert database.DATABASE_NAME == str(test_database)
    with closing(database.get_connection()) as connection:
        return {table: sorted(connection.execute(f"SELECT * FROM {table}").fetchall()) for table in TABLES}


def auth(user):
    return {"Authorization": f"Bearer {user['token']}"}


@pytest.fixture
def accounts(test_client, test_database, authenticated_user_factory, project_factory, member_factory):
    """The account to delete owns a shared project and contributes to someone else's project."""
    from app import ai_usage, database

    target = authenticated_user_factory(email="target@example.org")
    colleague = authenticated_user_factory(email="colleague@example.org")
    other = authenticated_user_factory(email="other@example.org")
    owned = project_factory(target["token"], name="Owned")["id"]
    member_factory(target["token"], owned, "colleague@example.org", "Developer")
    for user in (target, colleague):
        assert test_client.post(f"/projects/{owned}/bugs", headers=auth(user), json={"title": "Owned report"}).status_code == 201
    shared = project_factory(other["token"], name="Shared")["id"]
    member_factory(other["token"], shared, "target@example.org", "QA Analyst")
    authored = test_client.post(f"/projects/{shared}/bugs", headers=auth(target), json={"title": "Written by target"}).json()
    assigned = test_client.post(f"/projects/{shared}/bugs", headers=auth(other),
                                json={"title": "Assigned to target", "assignee_id": target["user_id"]}).json()
    with closing(database.get_connection()) as connection:
        connection.executemany("INSERT INTO ai_requests (user_id, usage_date) VALUES (?, ?)",
                               [(user["user_id"], ai_usage.utc_today()) for user in (target, other)])
        connection.commit()
    return {"target": target, "colleague": colleague, "other": other, "owned": owned, "shared": shared,
            "authored": authored, "assigned": assigned}


# TC-506 | AC-026.3 — Read-only mode refuses every write before it reaches the application; reads still work
@pytest.mark.parametrize("setting", [None, "1"], ids=["off_by_default", "on"])
def test_read_only_mode_refuses_writes(test_client, authenticated_user_factory, monkeypatch, setting):
    from app.middleware import READ_ONLY_MESSAGE

    user = authenticated_user_factory()
    monkeypatch.delenv("READ_ONLY_MODE", raising=False)
    if setting:
        monkeypatch.setenv("READ_ONLY_MODE", setting)
    response = test_client.post("/projects", headers=auth(user), json={"name": "Written"})
    if setting is None:
        assert response.status_code == 201
        return
    assert (response.status_code, response.json()) == (503, {"detail": READ_ONLY_MESSAGE})
    assert response.headers["x-frame-options"] == "DENY"
    for method, url in (("POST", "/demo"), ("POST", "/register"), ("PUT", "/projects/1"), ("DELETE", "/projects/1")):
        assert test_client.request(method, url, headers=auth(user)).status_code == 503
    assert test_client.get("/projects", headers=auth(user)).json() == []
    assert test_client.get("/version").status_code == 200
    assert test_client.get("/login.html").status_code == 200


# TC-507 | AC-026.1, AC-026.2, AC-026.3 — A dry run changes nothing; confirmed deletion leaves a placeholder and keeps others' records
def test_account_deletion_dry_run_and_confirmed_deletion(test_client, test_database, accounts, monkeypatch, capsys):
    from app import admin, database
    from app.main import app

    target, other = accounts["target"], accounts["other"]
    before = snapshot(test_database)
    assert admin.main(["delete-account", "target@example.org"]) == 0
    output = capsys.readouterr().out
    assert f"Database: {test_database}" in output and "Dry run: nothing was changed" in output
    assert "Owned projects to delete with all their reports and memberships: 1" in output
    assert "Reports created in other projects, kept without attribution: 1" in output
    assert snapshot(test_database) == before

    monkeypatch.setenv("READ_ONLY_MODE", "1")
    assert admin.main(["delete-account", "target@example.org", "--confirm"]) == 0
    monkeypatch.delenv("READ_ONLY_MODE")
    with closing(database.get_connection()) as connection:
        email, password_hash, deleted_at = connection.execute(
            "SELECT email, password_hash, deleted_at FROM users WHERE id = ?", (target["user_id"],)).fetchone()
        assert email == f"deleted-{target['user_id']}@deleted.invalid" and deleted_at is not None
        assert password_hash != next(row[2] for row in before["users"] if row[0] == target["user_id"])
        assert connection.execute("SELECT COUNT(*) FROM project_members WHERE user_id = ?", (target["user_id"],)).fetchone() == (0,)
        assert connection.execute("SELECT user_id FROM ai_requests").fetchall() == [(other["user_id"],)]
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    # The owned project is gone for everyone; the other project keeps its records.
    assert test_client.get(f"/projects/{accounts['owned']}", headers=auth(accounts["colleague"])).status_code == 404
    shared = f"/projects/{accounts['shared']}"
    members = test_client.get(f"{shared}/members", headers=auth(other)).json()
    assert [member["email"] for member in members] == ["other@example.org"]
    authored = test_client.get(f"{shared}/bugs/{accounts['authored']['bug_number']}", headers=auth(other)).json()
    assert authored["created_by"] == target["user_id"] and authored["title"] == "Written by target"
    assigned = test_client.get(f"{shared}/bugs/{accounts['assigned']['bug_number']}", headers=auth(other)).json()
    assert assigned["assignee_id"] is None and assigned["updated_at"] != accounts["assigned"]["updated_at"]
    # The old token and password no longer work; the address can register again with a new ID.
    assert test_client.get("/projects", headers=auth(target)).status_code == 401
    credentials = {"email": "target@example.org", "password": "Password1"}
    assert test_client.post("/login", json=credentials).status_code == 401
    assert test_client.post("/register", json=credentials).status_code == 201
    new_id = test_client.get("/protected", headers={
        "Authorization": f"Bearer {test_client.post('/login', json=credentials).json()['access_token']}"
    }).json()["user_id"]
    assert new_id > target["user_id"]
    with TestClient(app) as restarted:  # Startup integrity checks pass.
        assert restarted.get("/projects", headers=auth(other)).status_code == 200


# TC-508 | AC-026.3 — Account deletion refuses unsafe or invalid requests and rolls back failures, changing nothing
@pytest.mark.parametrize("case", [
    "not_read_only", "unknown_email", "already_deleted", "demo_account", "missing_database", "wrong_schema_version",
    "failed_delete",
])
def test_account_deletion_refusals_and_failures_change_nothing(
    test_client, test_database, accounts, monkeypatch, capsys, tmp_path, case,
):
    from app import admin, database

    monkeypatch.setenv("READ_ONLY_MODE", "1")
    email = "target@example.org"
    if case == "already_deleted":
        assert admin.main(["delete-account", email, "--confirm"]) == 0
    elif case == "unknown_email":
        email = "nobody@example.org"
    elif case == "demo_account":
        monkeypatch.delenv("READ_ONLY_MODE")
        headers = start_demo(test_client)
        email = next(iter(team_refs(test_client, headers, demo_projects(test_client, headers)["AI QA Bug Triage"]).values()))["email"]
        monkeypatch.setenv("READ_ONLY_MODE", "1")
    elif case == "not_read_only":
        monkeypatch.delenv("READ_ONLY_MODE")
    elif case == "wrong_schema_version":
        with closing(database.get_connection()) as connection:
            connection.execute("PRAGMA user_version = 3")
            connection.commit()
    before = snapshot(test_database)
    capsys.readouterr()

    if case == "failed_delete":
        class FailingConnection(sqlite3.Connection):
            def execute(self, sql, parameters=()):
                # Fails after the owned project, memberships and usage were already deleted.
                if sql.startswith("UPDATE users"):
                    raise sqlite3.OperationalError("Injected deletion failure")
                return super().execute(sql, parameters)

        with monkeypatch.context() as patch:
            patch.setattr(database, "get_connection",
                          lambda: sqlite3.connect(database.DATABASE_NAME, factory=FailingConnection))
            with pytest.raises(sqlite3.OperationalError, match="Injected"):
                admin.main(["delete-account", email, "--confirm"])
    else:
        if case == "missing_database":
            missing = tmp_path / "missing.db"
            monkeypatch.setattr(database, "DATABASE_NAME", str(missing))
        assert admin.main(["delete-account", email, "--confirm"]) == 1
        if case == "missing_database":
            assert not missing.exists()  # Never creates a database.
            monkeypatch.setattr(database, "DATABASE_NAME", str(test_database))
        expected = {
            "not_read_only": "READ_ONLY_MODE=1", "unknown_email": "No active account",
            "already_deleted": "No active account", "demo_account": "Demo account",
            "missing_database": "does not exist", "wrong_schema_version": "schema version",
        }[case]
        assert expected in capsys.readouterr().err
    assert snapshot(test_database) == before
