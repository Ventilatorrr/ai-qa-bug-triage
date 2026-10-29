from contextlib import closing
from datetime import datetime, timedelta, timezone
import sqlite3
import threading
import time

from fastapi.testclient import TestClient
import pytest

from tests.backend.test_demo import demo_projects, start_demo, team_refs
from tests.conftest import TEST_JWT_SECRET


def connect(test_database):
    from app import database

    assert database.DATABASE_NAME == str(test_database)
    return closing(database.get_connection())


def marks(values):
    return ", ".join("?" for _ in values)


def demo_record(client, test_database, headers):
    """The server-side Demo record of a visitor's token: its ID, creation time, accounts and projects."""
    owner = client.get("/protected", headers=headers).json()["user_id"]
    with connect(test_database) as connection:
        demo_id, created = connection.execute(
            "SELECT d.id, d.created_at FROM demos d JOIN demo_accounts a ON a.demo_id = d.id WHERE a.user_id = ?",
            (owner,),
        ).fetchone()
        accounts = [row[0] for row in connection.execute("SELECT user_id FROM demo_accounts WHERE demo_id = ?", (demo_id,))]
        projects = [row[0] for row in connection.execute(
            f"SELECT project_id FROM project_members WHERE role = 'Project Owner' AND user_id IN ({marks(accounts)})",
            accounts,
        )]
    return {"id": demo_id, "created": datetime.fromisoformat(created), "owner": owner,
            "accounts": accounts, "projects": projects}


def queries(record, inside):
    """Each table's rows that belong (inside) or do not belong to the Demo."""
    accounts, projects, demo_id = record["accounts"], record["projects"], [record["id"]]
    negate = "" if inside else "NOT "
    return {
        "users": (f"SELECT * FROM users WHERE id {negate}IN ({marks(accounts)})", accounts),
        "projects": (f"SELECT * FROM projects WHERE id {negate}IN ({marks(projects)})", projects),
        "project_members": (f"SELECT * FROM project_members WHERE project_id {negate}IN ({marks(projects)})", projects),
        "bugs": (f"SELECT * FROM bugs WHERE project_id {negate}IN ({marks(projects)})", projects),
        "ai_requests": (f"SELECT * FROM ai_requests WHERE user_id {negate}IN ({marks(accounts)})", accounts),
        "demos": (f"SELECT * FROM demos WHERE id {negate}IN (?)", demo_id),
        "demo_accounts": (f"SELECT * FROM demo_accounts WHERE demo_id {negate}IN (?)", demo_id),
    }


def rows(test_database, record, inside):
    with connect(test_database) as connection:
        return {table: sorted(connection.execute(sql, parameters).fetchall())
                for table, (sql, parameters) in queries(record, inside).items()}


def record_usage(test_database, *user_ids):
    from app import ai_usage

    with connect(test_database) as connection:
        connection.executemany("INSERT INTO ai_requests (user_id, usage_date) VALUES (?, ?)",
                               [(user_id, ai_usage.utc_today()) for user_id in user_ids])
        connection.commit()


def bearer(headers):
    return headers["Authorization"].removeprefix("Bearer ")


# TC-500 | AC-024.9 — A Demo records its creation and marks exactly its five accounts; only stored Demos use capacity
def test_demo_marks_its_accounts_and_only_stored_demos_use_capacity(test_client, test_database, user_factory, monkeypatch):
    from app.api import demo

    monkeypatch.setattr(demo, "DEMO_TOTAL_LIMIT", 1)
    # Ordinary accounts that look like generated Demo addresses are never marked or counted.
    for alias in ("abcd", "efgh", "ijkl", "nopq", "rstu"):
        user_factory(email=f"{alias}@example.com")
    before = datetime.now(timezone.utc)
    headers = start_demo(test_client)
    record = demo_record(test_client, test_database, headers)
    team = team_refs(test_client, headers, demo_projects(test_client, headers)["AI QA Bug Triage"])
    assert sorted(record["accounts"]) == sorted(team) and record["owner"] in team
    assert before <= record["created"] <= datetime.now(timezone.utc)
    with connect(test_database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM demos").fetchone() == (1,)
        assert connection.execute("SELECT COUNT(*) FROM demo_accounts").fetchone() == (5,)
    assert test_client.post("/demo").status_code == 503  # One stored Demo fills a cap of one.


# TC-501 | AC-024.9 — An expired Demo is deleted completely at the retention boundary; nothing else changes
@pytest.mark.parametrize("age", ["just_before", "at_retention"])
def test_expired_demo_is_deleted_completely(
    test_client, test_database, authenticated_user_factory, project_factory, monkeypatch, age,
):
    from app.api import demo
    from app.main import app

    monkeypatch.setattr(demo, "DEMO_TOTAL_LIMIT", 2)
    expiring = start_demo(test_client)
    projects = demo_projects(test_client, expiring)
    renamed = test_client.put(f"/projects/{projects['E-Commerce Demo']}", headers=expiring, json={"name": "Renamed"})
    assert renamed.status_code == 200
    teammate = next(member for member in team_refs(test_client, expiring, projects["AI QA Bug Triage"]).values()
                    if member["role"] == "Developer")
    own = project_factory(bearer(expiring), name="Visitor project")["id"]
    added = test_client.post(f"/projects/{own}/members", headers=expiring,
                             json={"email": teammate["email"], "role": "Developer"})
    assert added.status_code == 201
    assert test_client.post(f"/projects/{own}/bugs", headers=expiring, json={"title": "Visitor report"}).status_code == 201
    newer = start_demo(test_client)
    ordinary = authenticated_user_factory(email="ordinary@example.org")
    ordinary_project = project_factory(ordinary["token"])["id"]
    ordinary_headers = {"Authorization": f"Bearer {ordinary['token']}"}
    assert test_client.post(f"/projects/{ordinary_project}/bugs", headers=ordinary_headers,
                            json={"title": "Ordinary report"}).status_code == 201
    record = demo_record(test_client, test_database, expiring)
    record_usage(test_database, record["owner"], ordinary["user_id"])
    assert len(record["projects"]) == 3 and own in record["projects"]
    others, own_rows = rows(test_database, record, inside=False), rows(test_database, record, inside=True)
    assert test_client.post("/demo").status_code == 503  # Both stored Demos use the capacity.

    now = record["created"] + demo.DEMO_RETENTION - (timedelta(seconds=1) if age == "just_before" else timedelta(0))
    if age == "just_before":
        assert demo.delete_expired_demos(now) == (0, [])
        assert rows(test_database, record, inside=True) == own_rows
        assert test_client.get("/projects", headers=expiring).status_code == 200
        return
    assert demo.delete_expired_demos(now) == (1, [])
    assert all(not table_rows for table_rows in rows(test_database, record, inside=True).values())
    assert rows(test_database, record, inside=False) == others
    assert test_client.get("/projects", headers=expiring).status_code == 401
    with connect(test_database) as connection:
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    # A restart reruns the startup schema, relationship and counter checks.
    with TestClient(app) as restarted:
        assert restarted.get("/projects", headers=newer).status_code == 200
    start_demo(test_client)  # The deleted Demo's capacity is available again.


# TC-502 | AC-024.9 — A Demo with unexpected relationships or a failed deletion is kept whole, logged, reported and retried
@pytest.mark.parametrize("fault", [
    "demo_member_of_ordinary_project", "ordinary_member_of_demo_project", "demo_bug_in_ordinary_project", "failed_delete",
])
def test_unexpected_relationships_or_failures_keep_the_demo_whole(
    test_client, test_database, authenticated_user_factory, project_factory, monkeypatch, caplog, capsys, fault,
):
    from app import admin, database
    from app.api import demo

    faulty_headers = start_demo(test_client)
    healthy = demo_record(test_client, test_database, start_demo(test_client))
    faulty = demo_record(test_client, test_database, faulty_headers)
    ordinary = authenticated_user_factory(email="ordinary@example.org")
    ordinary_project = project_factory(ordinary["token"])["id"]
    teammate = next(user_id for user_id in faulty["accounts"] if user_id != faulty["owner"])
    remove = None
    with connect(test_database) as connection:
        if fault == "demo_member_of_ordinary_project":
            connection.execute("INSERT INTO project_members VALUES (?, ?, 'Developer')", (ordinary_project, teammate))
            remove = ("DELETE FROM project_members WHERE project_id = ? AND user_id = ?", (ordinary_project, teammate))
        elif fault == "ordinary_member_of_demo_project":
            connection.execute("INSERT INTO project_members VALUES (?, ?, 'Developer')",
                               (faulty["projects"][0], ordinary["user_id"]))
        elif fault == "demo_bug_in_ordinary_project":
            connection.execute(
                "INSERT INTO bugs (project_id, title, created_by, created_at, updated_at, bug_number) VALUES (?, ?, ?, ?, ?, 1)",
                (ordinary_project, "Inserted report", faulty["owner"], "2026-10-01T00:00:00+00:00", "2026-10-01T00:00:00+00:00"),
            )
            connection.execute("UPDATE projects SET next_bug_number = 2 WHERE id = ?", (ordinary_project,))
            remove = ("DELETE FROM bugs WHERE project_id = ? AND created_by = ?", (ordinary_project, faulty["owner"]))
        connection.commit()
    before = rows(test_database, healthy, inside=False)  # The faulty Demo and the ordinary data.
    now = max(faulty["created"], healthy["created"]) + demo.DEMO_RETENTION

    class FailingConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            # Fails after the faulty Demo's bugs, memberships and projects were already deleted.
            if sql.startswith("DELETE FROM users") and faulty["owner"] in parameters:
                raise sqlite3.OperationalError("Injected cleanup failure")
            return super().execute(sql, parameters)

    with monkeypatch.context() as patch, caplog.at_level("ERROR", logger="app.api.demo"):
        if fault == "failed_delete":
            patch.setattr(demo, "get_connection",
                          lambda: sqlite3.connect(database.DATABASE_NAME, factory=FailingConnection))
        assert demo.delete_expired_demos(now) == (1, [faulty["id"]])
    assert rows(test_database, healthy, inside=False) == before
    assert all(not table_rows for table_rows in rows(test_database, healthy, inside=True).values())
    assert f"Expired Demo {faulty['id']} (created" in caplog.text and "Manual resolution is needed" in caplog.text
    assert "example" not in caplog.text  # No email addresses in the log.
    # Operators can list what is still waiting: the faulty Demo only.
    with monkeypatch.context() as patch:
        patch.setattr(demo, "retention_cutoff", lambda now=None: faulty["created"] + timedelta(hours=3))
        assert admin.main(["status"]) == 0
    output = capsys.readouterr().out
    assert f"Demo {faulty['id']}, created" in output and "3.0 hours past" in output
    assert f"Demo {healthy['id']}," not in output

    if fault == "ordinary_member_of_demo_project":
        # Resolved by hand, as Remove Member would: the ordinary account leaves the Demo project.
        remove = ("DELETE FROM project_members WHERE user_id = ?", (ordinary["user_id"],))
    if remove:
        with connect(test_database) as connection:
            connection.execute(*remove)
            connection.commit()
    assert demo.delete_expired_demos(now) == (1, [])
    assert all(not table_rows for table_rows in rows(test_database, faulty, inside=True).values())


# TC-503 | AC-024.9 — Concurrent and repeated cleanup runs delete each expired Demo exactly once
def test_concurrent_and_repeated_cleanup_deletes_each_demo_once(test_client, test_database):
    from app.api import demo

    records = [demo_record(test_client, test_database, start_demo(test_client)) for _ in range(2)]
    now = max(record["created"] for record in records) + demo.DEMO_RETENTION
    barrier, results = threading.Barrier(2), []

    def run():
        barrier.wait()
        results.append(demo.delete_expired_demos(now))

    threads = [threading.Thread(target=run) for _ in range(2)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(timeout=30)
    assert sorted(deleted for deleted, _ in results) in ([0, 2], [1, 1])
    assert [failed for _, failed in results] == [[], []]
    assert demo.delete_expired_demos(now) == (0, [])
    with connect(test_database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM demos").fetchone() == (0,)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


# TC-504 | AC-024.9, AC-025.7 — Retention runs at startup and then on its interval; one failing task does not stop the other
def test_retention_runs_at_startup_and_on_interval(test_database, monkeypatch, caplog):
    from app import ai_usage, retention
    from app.api import demo
    from app.main import app

    monkeypatch.setenv("JWT_SECRET_KEY", TEST_JWT_SECRET)
    calls = []

    def failing_demo_cleanup(now=None):
        calls.append("demos")
        raise RuntimeError("Injected cleanup failure")

    monkeypatch.setattr(demo, "delete_expired_demos", failing_demo_cleanup)
    monkeypatch.setattr(ai_usage, "delete_old_ai_usage", lambda: calls.append("usage"))
    monkeypatch.setattr(retention, "RETENTION_INTERVAL_SECONDS", 0.01)
    with caplog.at_level("ERROR", logger="app.retention"), TestClient(app):
        assert calls[:2] == ["demos", "usage"]  # Completed during startup, before any request.
        deadline = time.monotonic() + 10
        while calls.count("usage") < 3 and time.monotonic() < deadline:
            time.sleep(0.01)
    assert calls.count("usage") >= 3 and calls.count("demos") >= 3
    assert "Retention task failing_demo_cleanup failed" in caplog.text


# TC-509 | AC-024.9 — A Demo without exactly five account records is kept whole, and no other account is deleted with it
@pytest.mark.parametrize("change", ["missing_account_record", "extra_account_record"])
def test_demo_without_exactly_five_accounts_is_not_deleted(
    test_client, test_database, authenticated_user_factory, project_factory, caplog, change,
):
    from app.api import demo

    record = demo_record(test_client, test_database, start_demo(test_client))
    ordinary = authenticated_user_factory(email="ordinary@example.org")
    project_factory(ordinary["token"])
    tables = ("users", "projects", "project_members", "bugs", "ai_requests", "demos", "demo_accounts")
    with connect(test_database) as connection:
        if change == "missing_account_record":
            teammate = next(user_id for user_id in record["accounts"] if user_id != record["owner"])
            connection.execute("DELETE FROM demo_accounts WHERE user_id = ?", (teammate,))
        else:
            # An ordinary account wrongly recorded as part of the Demo must never be deleted with it.
            connection.execute("INSERT INTO demo_accounts (user_id, demo_id) VALUES (?, ?)", (ordinary["user_id"], record["id"]))
        connection.commit()
        before = {table: sorted(connection.execute(f"SELECT * FROM {table}").fetchall()) for table in tables}
    with caplog.at_level("ERROR", logger="app.api.demo"):
        assert demo.delete_expired_demos(record["created"] + demo.DEMO_RETENTION) == (0, [record["id"]])
    with connect(test_database) as connection:
        assert {table: sorted(connection.execute(f"SELECT * FROM {table}").fetchall()) for table in tables} == before
    assert f"Expired Demo {record['id']} (created" in caplog.text and "instead of 5" in caplog.text
