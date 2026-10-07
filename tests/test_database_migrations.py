from contextlib import closing
import importlib.util
from pathlib import Path
import sqlite3

import pytest


BUG_COLUMNS = (
    "id", "project_id", "title", "affected_version", "environment", "description",
    "steps_to_reproduce", "expected_result", "actual_result", "severity", "priority",
    "assignee_id", "fix_version", "status", "resolution", "created_by", "created_at", "updated_at",
)


@pytest.fixture
def database(tmp_path, monkeypatch):
    # Load independently so migration tests cannot change the API module's cached database path.
    monkeypatch.setenv("DATABASE_NAME", str(tmp_path / "migration.db"))
    path = Path(__file__).resolve().parents[1] / "app" / "database.py"
    spec = importlib.util.spec_from_file_location("migration_test_database", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def legacy_database(database, appended=True):
    columns = [
        "id INTEGER PRIMARY KEY", "project_id INTEGER NOT NULL", "title VARCHAR(255) NOT NULL",
        "affected_version VARCHAR(20)", "environment TEXT", "description TEXT", "steps_to_reproduce TEXT",
        "expected_result TEXT", "actual_result TEXT", "severity VARCHAR(10)", "priority VARCHAR(10)",
        "assignee_id INTEGER", "fix_version VARCHAR(20)", "status VARCHAR(20) NOT NULL DEFAULT 'Triage'",
        "resolution VARCHAR(20)", "created_by INTEGER NOT NULL", "created_at TEXT NOT NULL", "updated_at TEXT NOT NULL",
    ]
    if appended:
        columns = [column for column in columns if not column.startswith(("environment ", "resolution "))] + ["resolution VARCHAR(20)", "environment TEXT"]
    columns += ["FOREIGN KEY (project_id) REFERENCES projects(id)",
                "FOREIGN KEY (assignee_id) REFERENCES users(id)", "FOREIGN KEY (created_by) REFERENCES users(id)"]
    with closing(database.get_connection()) as connection:
        for sql in (
            "CREATE TABLE users (id INTEGER PRIMARY KEY, email VARCHAR(255) UNIQUE NOT NULL, password_hash VARCHAR(255) NOT NULL)",
            "CREATE TABLE projects (id INTEGER PRIMARY KEY, name VARCHAR(255) NOT NULL)",
            "CREATE TABLE project_members (project_id INTEGER NOT NULL, user_id INTEGER NOT NULL, role VARCHAR(50) NOT NULL, PRIMARY KEY(project_id,user_id), FOREIGN KEY(project_id) REFERENCES projects(id), FOREIGN KEY(user_id) REFERENCES users(id))",
            f"CREATE TABLE bugs ({', '.join(columns)})",
        ):
            connection.execute(sql)
        connection.executemany("INSERT INTO users VALUES(?,?,?)", [(1, "owner@example.com", "hash"), (2, "dev@example.com", "hash")])
        connection.executemany("INSERT INTO projects VALUES(?,?)", [(1, "One"), (2, "Two"), (3, "Empty")])
        connection.executemany("INSERT INTO project_members VALUES(?,?,?)", [(project, user, role) for project in (1, 2, 3) for user, role in ((1, "Project Owner"), (2, "Developer"))])
        for bug_id, project in [(2, 1), (7, 2), (11, 1), (40, 2)]:
            values = (bug_id, project, f"Report {bug_id}: 'quoted' Ω", None if bug_id == 2 else "0.4",
                      "Windows", "Line one\nLine two",
                      'Open report\nClick "Save"' if bug_id == 11 else None,
                      "Expected", "Actual", "Major", "High" if bug_id == 11 else None,
                      None if bug_id == 2 else 2, "0.5" if bug_id == 40 else None,
                      "Closed" if bug_id == 40 else "Triage", "Fixed" if bug_id == 40 else None,
                      1, "2026-01-01T00:00:00+00:00", "2026-02-01T00:00:00+00:00")
            connection.execute(f"INSERT INTO bugs ({', '.join(BUG_COLUMNS)}) VALUES ({', '.join('?' for _ in BUG_COLUMNS)})", values)
        connection.commit()


def snapshot(database):
    with closing(database.get_connection()) as connection:
        return connection.execute("PRAGMA user_version").fetchone()[0], tuple(connection.iterdump())


def test_fresh_database_creates_numbering_schema(database):
    database.create_tables()
    with closing(database.get_connection()) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (1,)
        assert {row[1] for row in connection.execute("PRAGMA table_info(bugs)")} == {*BUG_COLUMNS, "bug_number"}
        connection.execute("INSERT INTO projects(name) VALUES('New')")
        assert connection.execute("SELECT next_bug_number FROM projects").fetchall() == [(1,)]
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


@pytest.mark.parametrize("appended", [False, True], ids=["source-order", "actual-legacy-order"])
def test_legacy_backfill_preserves_every_field_and_is_idempotent(database, appended):
    legacy_database(database, appended)
    with closing(database.get_connection()) as connection:
        before = connection.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall()
        unrelated = {table: connection.execute(f"SELECT * FROM {table}").fetchall() for table in ("users", "project_members")}
    database.create_tables()
    with closing(database.get_connection()) as connection:
        assert connection.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall() == before
        assert connection.execute("SELECT id,project_id,bug_number FROM bugs ORDER BY id").fetchall() == [(2, 1, 1), (7, 2, 1), (11, 1, 2), (40, 2, 2)]
        assert connection.execute("SELECT id,next_bug_number FROM projects ORDER BY id").fetchall() == [(1, 3), (2, 3), (3, 1)]
        for table, values in unrelated.items():
            assert connection.execute(f"SELECT * FROM {table}").fetchall() == values
        assert connection.execute("PRAGMA user_version").fetchone() == (1,)
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    upgraded = snapshot(database)
    database.create_tables()
    assert snapshot(database) == upgraded
    with closing(database.get_connection()) as connection:
        connection.execute("DELETE FROM bugs WHERE project_id=1")
        connection.execute("UPDATE projects SET next_bug_number=9 WHERE id=2")
        connection.commit()
    after_deletion = snapshot(database)
    database.create_tables()
    assert snapshot(database) == after_deletion


@pytest.mark.parametrize("failure_point", ["before-drop", "before-commit"])
def test_migration_failure_rolls_back_schema_data_and_version(database, monkeypatch, failure_point):
    legacy_database(database)
    before = snapshot(database)
    original = database.get_connection
    with closing(original()) as connection:
        original_rows = connection.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall()
    reached = []

    class FailingConnection(sqlite3.Connection):
        def commit(self):
            # Inspect the uncommitted state to prove replacement and version writes happened.
            assert self.in_transaction
            assert self.execute("PRAGMA user_version").fetchone() == (1,)
            assert self.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall() == original_rows
            assert self.execute("SELECT id,project_id,bug_number FROM bugs ORDER BY id").fetchall() == [(2, 1, 1), (7, 2, 1), (11, 1, 2), (40, 2, 2)]
            assert self.execute("SELECT id,next_bug_number FROM projects ORDER BY id").fetchall() == [(1, 3), (2, 3), (3, 1)]
            assert self.execute("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name").fetchall() == [("bugs",), ("project_members",), ("projects",), ("users",)]
            reached.append("before-commit")
            raise sqlite3.OperationalError("Injected migration commit failure")

    def failing_connection():
        if failure_point == "before-commit":
            return sqlite3.connect(database.DATABASE_NAME, factory=FailingConnection)
        connection = original()
        def authorize(action, first, *_):
            if action == sqlite3.SQLITE_DROP_TABLE and first == "bugs":
                reached.append("before-drop")
                return sqlite3.SQLITE_DENY
            return sqlite3.SQLITE_OK
        connection.set_authorizer(authorize)
        return connection
    with monkeypatch.context() as patch:
        patch.setattr(database, "get_connection", failing_connection)
        with pytest.raises(sqlite3.DatabaseError):
            database.create_tables()
    assert reached == [failure_point]
    assert snapshot(database) == before
    with closing(original()) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (0,)
        assert {row[1] for row in connection.execute("PRAGMA table_info(bugs)")} == set(BUG_COLUMNS)
        assert {row[1] for row in connection.execute("PRAGMA table_info(projects)")} == {"id", "name"}
        assert connection.execute("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name").fetchall() == [("bugs",), ("project_members",), ("projects",), ("users",)]
    database.create_tables()
    with closing(original()) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (1,)
        assert connection.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall() == original_rows
        assert connection.execute("SELECT id,project_id,bug_number FROM bugs ORDER BY id").fetchall() == [(2, 1, 1), (7, 2, 1), (11, 1, 2), (40, 2, 2)]
        assert connection.execute("SELECT id,next_bug_number FROM projects ORDER BY id").fetchall() == [(1, 3), (2, 3), (3, 1)]


@pytest.mark.parametrize("mutation", [
    "ALTER TABLE bugs ADD COLUMN bug_number INTEGER",
    "ALTER TABLE projects ADD COLUMN next_bug_number INTEGER",
    "ALTER TABLE bugs ADD COLUMN unexpected TEXT",
    "CREATE INDEX unexpected ON bugs(title)",
    "CREATE TRIGGER unexpected AFTER INSERT ON bugs BEGIN SELECT 1; END",
    "CREATE VIEW unexpected AS SELECT id FROM bugs",
    "CREATE TABLE sqlitex_extra(id INTEGER)",
    "PRAGMA user_version=2",
    "DELETE FROM users WHERE id=2",
])
def test_migration_rejects_unexpected_partial_or_inconsistent_legacy_schema(database, mutation):
    legacy_database(database)
    with closing(database.get_connection()) as connection:
        connection.execute(mutation)
        connection.commit()
    before = snapshot(database)
    with pytest.raises(RuntimeError, match="schema|version|relationship"):
        database.create_tables()
    assert snapshot(database) == before


@pytest.mark.parametrize("field,value", [
    ("bug_number", None), ("bug_number", 0), ("bug_number", -1), ("bug_number", 1.5), ("bug_number", "invalid"),
    ("next_bug_number", None), ("next_bug_number", 0), ("next_bug_number", -1), ("next_bug_number", 1.5),
])
def test_numbering_constraints_reject_invalid_storage(database, field, value):
    legacy_database(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            if field == "bug_number":
                connection.execute("UPDATE bugs SET bug_number=? WHERE id=2", (value,))
            else:
                connection.execute("UPDATE projects SET next_bug_number=? WHERE id=1", (value,))


def test_numbering_uniqueness_is_scoped_to_project(database):
    legacy_database(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        assert connection.execute("SELECT COUNT(*) FROM bugs WHERE bug_number=1").fetchone() == (2,)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("UPDATE bugs SET bug_number=1 WHERE id=11")


def test_current_schema_rejects_invalid_counter_without_repair(database):
    legacy_database(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        connection.execute("UPDATE projects SET next_bug_number=1 WHERE id=1")
        connection.commit()
    before = snapshot(database)
    with pytest.raises(RuntimeError, match="counter"):
        database.create_tables()
    assert snapshot(database) == before
