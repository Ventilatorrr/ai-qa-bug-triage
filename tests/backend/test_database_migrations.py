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
    path = Path(__file__).resolve().parents[2] / "app" / "database.py"
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


def drop_version_4(connection):
    """Remove the version-4 objects, to derive an earlier schema from the current one."""
    connection.execute("DROP TABLE demo_accounts")
    connection.execute("DROP TABLE demos")
    connection.execute("ALTER TABLE users DROP COLUMN deleted_at")


# TC-145 | Technical — Fresh database creates numbering schema
def test_fresh_database_creates_numbering_schema(database):
    database.create_tables()
    with closing(database.get_connection()) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (database.SCHEMA_VERSION,)
        assert {row[1] for row in connection.execute("PRAGMA table_info(bugs)")} == {*BUG_COLUMNS, "bug_number"}
        assert [row[1] for row in connection.execute("PRAGMA table_info(ai_requests)")] == ["id", "user_id", "usage_date"]
        connection.execute("INSERT INTO projects(name) VALUES('New')")
        assert connection.execute("SELECT next_bug_number FROM projects").fetchall() == [(1,)]
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []


# TC-146 | Technical — Legacy backfill preserves every field and is idempotent
@pytest.mark.parametrize("appended", [False, True], ids=["source-order", "actual-legacy-order"])
def test_legacy_backfill_preserves_every_field_and_is_idempotent(database, appended):
    legacy_database(database, appended)
    with closing(database.get_connection()) as connection:
        before = connection.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall()
        # Legacy columns only: version 4 adds an empty users.deleted_at.
        queries = ("SELECT id, email, password_hash FROM users", "SELECT * FROM project_members")
        unrelated = {query: connection.execute(query).fetchall() for query in queries}
    database.create_tables()
    with closing(database.get_connection()) as connection:
        assert connection.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall() == before
        assert connection.execute("SELECT id,project_id,bug_number FROM bugs ORDER BY id").fetchall() == [(2, 1, 1), (7, 2, 1), (11, 1, 2), (40, 2, 2)]
        assert connection.execute("SELECT id,next_bug_number FROM projects ORDER BY id").fetchall() == [(1, 3), (2, 3), (3, 1)]
        for query, values in unrelated.items():
            assert connection.execute(query).fetchall() == values
        assert connection.execute("PRAGMA user_version").fetchone() == (database.SCHEMA_VERSION,)
        assert connection.execute("SELECT COUNT(*) FROM ai_requests").fetchone() == (0,)
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


# TC-147 | Technical — Migration failure rolls back schema data and version
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
            assert self.execute("PRAGMA user_version").fetchone() == (database.SCHEMA_VERSION,)
            assert self.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall() == original_rows
            assert self.execute("SELECT id,project_id,bug_number FROM bugs ORDER BY id").fetchall() == [(2, 1, 1), (7, 2, 1), (11, 1, 2), (40, 2, 2)]
            assert self.execute("SELECT id,next_bug_number FROM projects ORDER BY id").fetchall() == [(1, 3), (2, 3), (3, 1)]
            assert self.execute("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name").fetchall() == [("ai_requests",), ("bugs",), ("demo_accounts",), ("demos",), ("project_members",), ("projects",), ("users",)]
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
        assert connection.execute("PRAGMA user_version").fetchone() == (database.SCHEMA_VERSION,)
        assert connection.execute(f"SELECT {', '.join(BUG_COLUMNS)} FROM bugs ORDER BY id").fetchall() == original_rows
        assert connection.execute("SELECT id,project_id,bug_number FROM bugs ORDER BY id").fetchall() == [(2, 1, 1), (7, 2, 1), (11, 1, 2), (40, 2, 2)]
        assert connection.execute("SELECT id,next_bug_number FROM projects ORDER BY id").fetchall() == [(1, 3), (2, 3), (3, 1)]


# TC-148, TC-149, TC-150 | Technical — Migration rejects unexpected partial or inconsistent legacy schema
@pytest.mark.parametrize("mutation", [
    "ALTER TABLE bugs ADD COLUMN bug_number INTEGER",
    "ALTER TABLE projects ADD COLUMN next_bug_number INTEGER",
    "ALTER TABLE bugs ADD COLUMN unexpected TEXT",
    "CREATE INDEX unexpected ON bugs(title)",
    "CREATE TRIGGER unexpected AFTER INSERT ON bugs BEGIN SELECT 1; END",
    "CREATE VIEW unexpected AS SELECT id FROM bugs",
    "CREATE TABLE sqlitex_extra(id INTEGER)",
    "PRAGMA user_version=99",
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


def version_1_database(database, origin):
    """Synthetic version-1 database: the current schema without the version-2 usage table.

    "legacy" reproduces a database that version-1 code upgraded from version 0;
    "fresh" reproduces one that version-1 code created directly.
    """
    if origin == "legacy":
        legacy_database(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        drop_version_4(connection)
        connection.execute("ALTER TABLE projects DROP COLUMN demo_kind")
        if origin == "fresh":
            connection.executemany("INSERT INTO users VALUES(?,?,?)", [(1, "owner@example.com", "hash"), (2, "qa@example.com", "hash")])
            connection.execute("INSERT INTO projects VALUES(1, 'Fresh', 3)")
            connection.executemany("INSERT INTO project_members VALUES(?,?,?)", [(1, 1, "Project Owner"), (1, 2, "QA Analyst")])
            for bug_id, number in [(5, 1), (9, 2)]:
                values = (bug_id, 1, f"Report {number}: 'quoted' Ω", "1.0", "Chrome", "Line one\nLine two", None,
                          "Expected", "Actual", "Minor", "Low", 2 if number == 2 else None, None,
                          "Testing" if number == 2 else "Triage", None, 1,
                          "2026-03-01T00:00:00+00:00", "2026-03-02T00:00:00+00:00", number)
                connection.execute(f"INSERT INTO bugs ({', '.join(BUG_COLUMNS)}, bug_number) VALUES ({', '.join('?' for _ in values)})", values)
        connection.execute("DROP TABLE ai_requests")
        connection.execute("PRAGMA user_version=1")
        connection.commit()


# TC-434 | Technical — Version 1 upgrade adds usage table and preserves all existing data
@pytest.mark.parametrize("origin", ["fresh", "legacy"])
def test_version_1_upgrade_adds_usage_table_and_preserves_all_data(database, origin):
    version_1_database(database, origin)
    version, before = snapshot(database)
    assert version == 1
    database.create_tables()
    version, after = snapshot(database)
    assert version == database.SCHEMA_VERSION
    # The additive upgrade keeps all values; compare original tables without the new nullable marker.
    with closing(database.get_connection()) as connection:
        assert connection.execute("SELECT DISTINCT demo_kind FROM projects").fetchall() == [(None,)]
        connection.execute("BEGIN")
        drop_version_4(connection)
        connection.execute("ALTER TABLE projects DROP COLUMN demo_kind")
        original_tables = tuple(connection.iterdump())
        connection.rollback()
    assert [line for line in original_tables if "ai_requests" not in line] == list(before)
    assert [line for line in after if "ai_requests" in line] == [line for line in after if line.startswith('CREATE TABLE ai_requests')]
    with closing(database.get_connection()) as connection:
        assert connection.execute("SELECT COUNT(*) FROM ai_requests").fetchone() == (0,)
        assert connection.execute("PRAGMA integrity_check").fetchone() == ("ok",)
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
    upgraded = snapshot(database)
    database.create_tables()
    assert snapshot(database) == upgraded


# TC-435 | Technical — Version 1 upgrade failure rolls back table and version
def test_version_1_upgrade_failure_rolls_back_table_and_version(database, monkeypatch):
    version_1_database(database, "legacy")
    before = snapshot(database)
    reached = []

    class FailingConnection(sqlite3.Connection):
        def commit(self):
            # The uncommitted upgrade has created the table and set the version.
            assert self.execute("PRAGMA user_version").fetchone() == (database.SCHEMA_VERSION,)
            assert self.execute("SELECT COUNT(*) FROM sqlite_schema WHERE name='ai_requests'").fetchone() == (1,)
            reached.append("before-commit")
            raise sqlite3.OperationalError("Injected upgrade commit failure")

    with monkeypatch.context() as patch:
        patch.setattr(database, "get_connection", lambda: sqlite3.connect(database.DATABASE_NAME, factory=FailingConnection))
        with pytest.raises(sqlite3.DatabaseError):
            database.create_tables()
    assert reached == ["before-commit"]
    assert snapshot(database) == before
    database.create_tables()
    assert snapshot(database)[0] == database.SCHEMA_VERSION


# TC-436 | Technical — Startup rejects unexpected version 1 or version 2 schema without changes
@pytest.mark.parametrize("version,mutation", [
    (1, "CREATE TABLE ai_requests (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, usage_date TEXT NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id))"),
    (1, "ALTER TABLE bugs ADD COLUMN unexpected TEXT"),
    (2, "ALTER TABLE ai_requests ADD COLUMN unexpected TEXT"),
    (2, "CREATE INDEX unexpected ON ai_requests(usage_date)"),
    (2, "INSERT INTO ai_requests (user_id, usage_date) VALUES (99, '2026-10-26')"),
])
def test_startup_rejects_unexpected_version_1_or_2_schema(database, version, mutation):
    if version == 1:
        version_1_database(database, "fresh")
    else:
        legacy_database(database)
        database.create_tables()
        with closing(database.get_connection()) as connection:
            drop_version_4(connection)
            connection.execute("ALTER TABLE projects DROP COLUMN demo_kind")
            connection.execute("PRAGMA user_version=2")
            connection.commit()
    with closing(database.get_connection()) as connection:
        connection.execute(mutation)
        connection.commit()
    before = snapshot(database)
    with pytest.raises(RuntimeError, match="schema|version|relationship"):
        database.create_tables()
    assert snapshot(database) == before


# TC-151, TC-152 | Technical — Numbering constraints reject invalid storage
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


# TC-153 | Technical — Numbering uniqueness is scoped to project
def test_numbering_uniqueness_is_scoped_to_project(database):
    legacy_database(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        assert connection.execute("SELECT COUNT(*) FROM bugs WHERE bug_number=1").fetchone() == (2,)
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute("UPDATE bugs SET bug_number=1 WHERE id=11")


# TC-154 | Technical — Current schema rejects invalid counter without repair
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


def version_2_database(database):
    legacy_database(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        drop_version_4(connection)
        connection.execute("ALTER TABLE projects DROP COLUMN demo_kind")
        connection.execute("PRAGMA user_version=2")
        connection.commit()


# TC-459 | Technical — Version 2 upgrade adds only an empty Demo marker and preserves data across restart
def test_version_2_upgrade_adds_demo_marker_without_changing_existing_values(database):
    version_2_database(database)
    _, before = snapshot(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (database.SCHEMA_VERSION,)
        assert connection.execute("SELECT DISTINCT demo_kind FROM projects").fetchall() == [(None,)]
        connection.execute("BEGIN")
        drop_version_4(connection)
        connection.execute("ALTER TABLE projects DROP COLUMN demo_kind")
        old_values = tuple(connection.iterdump())
        connection.rollback()
    assert old_values == before
    upgraded = snapshot(database)
    database.create_tables()
    assert snapshot(database) == upgraded


# TC-460 | Technical — A failed version 2 Demo-marker upgrade rolls back both schema and version
def test_version_2_demo_marker_upgrade_failure_rolls_back(database, monkeypatch):
    version_2_database(database)
    before = snapshot(database)

    class FailingConnection(sqlite3.Connection):
        def commit(self):
            assert self.execute("PRAGMA user_version").fetchone() == (database.SCHEMA_VERSION,)
            assert self.execute("SELECT DISTINCT demo_kind FROM projects").fetchall() == [(None,)]
            raise sqlite3.OperationalError("Synthetic marker migration failure")

    with monkeypatch.context() as patch:
        patch.setattr(database, "get_connection", lambda: sqlite3.connect(database.DATABASE_NAME, factory=FailingConnection))
        with pytest.raises(sqlite3.OperationalError, match="Synthetic marker"):
            database.create_tables()
    assert snapshot(database) == before


# TC-499 | AC-024.9 — Version 3 upgrade adds empty Demo records, keeps every value and leaves earlier accounts active and unmarked
def test_version_3_upgrade_adds_demo_records_and_keeps_existing_accounts(database):
    legacy_database(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        drop_version_4(connection)
        connection.execute("UPDATE projects SET demo_kind='ecommerce' WHERE id=1")  # A Demo created by version 3.
        connection.execute("PRAGMA user_version=3")
        connection.commit()
    _, before = snapshot(database)
    database.create_tables()
    with closing(database.get_connection()) as connection:
        assert connection.execute("PRAGMA user_version").fetchone() == (database.SCHEMA_VERSION,)
        assert connection.execute("SELECT COUNT(*) FROM demos").fetchone() == (0,)
        assert connection.execute("SELECT COUNT(*) FROM demo_accounts").fetchone() == (0,)
        assert connection.execute("SELECT DISTINCT deleted_at FROM users").fetchall() == [(None,)]
        connection.execute("BEGIN")
        drop_version_4(connection)
        old_values = tuple(connection.iterdump())
        connection.rollback()
    assert old_values == before
    upgraded = snapshot(database)
    database.create_tables()
    assert snapshot(database) == upgraded
