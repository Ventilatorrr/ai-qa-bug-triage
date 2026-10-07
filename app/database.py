import os
import re
import sqlite3
from contextlib import closing


DATABASE_NAME = os.getenv("DATABASE_NAME", "bugtriage.db")
SCHEMA_VERSION = 1


def get_connection():
    return sqlite3.connect(DATABASE_NAME)


def _create_schema(conn):
    conn.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            next_bug_number INTEGER NOT NULL DEFAULT 1
                CHECK(typeof(next_bug_number) = 'integer' AND next_bug_number > 0)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE project_members (
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role VARCHAR(50) NOT NULL,
            PRIMARY KEY (project_id, user_id),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE bugs (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            title VARCHAR(255) NOT NULL,
            affected_version VARCHAR(20),
            environment TEXT,
            description TEXT,
            steps_to_reproduce TEXT,
            expected_result TEXT,
            actual_result TEXT,
            severity VARCHAR(10),
            priority VARCHAR(10),
            assignee_id INTEGER,
            fix_version VARCHAR(20),
            status VARCHAR(20) NOT NULL DEFAULT 'Triage',
            resolution VARCHAR(20),
            created_by INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            bug_number INTEGER NOT NULL
                CHECK(typeof(bug_number) = 'integer' AND bug_number > 0),
            UNIQUE(project_id, bug_number),
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (assignee_id) REFERENCES users(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """
    )


BUG_COLUMNS = (
    "id", "project_id", "title", "affected_version", "environment", "description",
    "steps_to_reproduce", "expected_result", "actual_result", "severity", "priority",
    "assignee_id", "fix_version", "status", "resolution", "created_by", "created_at", "updated_at",
)


def _schema_properties(conn):
    """Compare schema properties, independently of column order and DDL formatting."""
    objects = conn.execute(
        "SELECT type, name FROM sqlite_schema WHERE name NOT GLOB 'sqlite_*' AND type != 'index'"
    ).fetchall()
    properties = {"objects": sorted(objects)}
    for kind, table in objects:
        if kind != "table" or table not in ("users", "projects", "project_members", "bugs"):
            continue
        columns = sorted(
            (name, re.sub(r"\s+", "", declared_type.upper()), required, default, primary)
            for _, name, declared_type, required, default, primary, *rest
            in conn.execute(f'PRAGMA table_xinfo("{table}")')
            # Hidden/generated columns are unexpected too.
            if not rest or rest[0] == 0
        )
        foreign_keys = sorted(row[2:] for row in conn.execute(f'PRAGMA foreign_key_list("{table}")'))
        indexes = []
        for _, name, unique, origin, partial in conn.execute(f'PRAGMA index_list("{table}")'):
            escaped = name.replace('"', '""')
            index_columns = tuple(
                (row[2], row[3], row[4], row[5])
                for row in conn.execute(f'PRAGMA index_xinfo("{escaped}")')
            )
            indexes.append((unique, origin, partial, index_columns))
        sql = conn.execute("SELECT sql FROM sqlite_schema WHERE type='table' AND name=?", (table,)).fetchone()[0]
        normalized = re.sub(r"\s+", "", sql.lower())
        checks = []
        for field in ("bug_number", "next_bug_number"):
            expression = f"check(typeof({field})='integer'and{field}>0)"
            if expression in normalized:
                checks.append(field)
        flags = (len(re.findall(r"\bcheck\s*\(", sql, re.I)), checks,
                 bool(re.search(r"\bautoincrement\b", sql, re.I)))
        table_options = next(row[4:] for row in conn.execute("PRAGMA table_list") if row[0] == "main" and row[1] == table)
        # Column count includes generated columns, even if omitted from columns above.
        count = len(conn.execute(f'PRAGMA table_xinfo("{table}")').fetchall())
        properties[table] = (columns, foreign_keys, sorted(indexes), flags, table_options, count)
    return properties


def _verify_schema(conn, version):
    with closing(sqlite3.connect(":memory:")) as reference:
        _create_schema(reference)
        if version == 0:
            # Derive the legacy properties from the same maintained schema.
            reference.execute("ALTER TABLE projects DROP COLUMN next_bug_number")
            sql = reference.execute("SELECT sql FROM sqlite_schema WHERE name='bugs'").fetchone()[0]
            sql = re.sub(r"bug_number INTEGER NOT NULL\s+CHECK\(typeof\(bug_number\) = 'integer' AND bug_number > 0\),\s+UNIQUE\(project_id, bug_number\),", "", sql)
            reference.execute("DROP TABLE bugs")
            reference.execute(sql)
        if _schema_properties(conn) != _schema_properties(reference):
            raise RuntimeError(f"Unexpected or partial database schema at version {version}; migration refused.")


def _verify_data(conn):
    if conn.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise RuntimeError("Invalid database relationships; migration refused.")
    if conn.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
        raise RuntimeError("Invalid database schema or data integrity; migration refused.")


def _verify_counters(conn):
    invalid = conn.execute("""
        SELECT p.id FROM projects p
        WHERE typeof(p.next_bug_number) != 'integer' OR p.next_bug_number <= 0
           OR p.next_bug_number <= COALESCE((SELECT MAX(b.bug_number) FROM bugs b WHERE b.project_id=p.id), 0)
        LIMIT 1
    """).fetchone()
    if invalid is not None:
        raise RuntimeError("Invalid project bug-number counter; startup refused without repair.")


def _migrate_legacy(conn):
    columns = ", ".join(BUG_COLUMNS)
    original = conn.execute(f"SELECT {columns} FROM bugs ORDER BY id").fetchall()
    conn.execute("""
        ALTER TABLE projects ADD COLUMN next_bug_number INTEGER NOT NULL DEFAULT 1
        CHECK(typeof(next_bug_number) = 'integer' AND next_bug_number > 0)
    """)
    with closing(sqlite3.connect(":memory:")) as reference:
        _create_schema(reference)
        sql = reference.execute("SELECT sql FROM sqlite_schema WHERE name='bugs'").fetchone()[0]
    conn.execute(sql.replace("CREATE TABLE bugs", "CREATE TABLE bugs_numbered", 1))
    counters = {}
    for row in conn.execute(f"SELECT {columns} FROM bugs ORDER BY project_id, id").fetchall():
        project = row[1]
        number = counters.get(project, 1)
        conn.execute(
            f"INSERT INTO bugs_numbered ({columns}, bug_number) VALUES ({', '.join('?' for _ in range(len(BUG_COLUMNS) + 1))})",
            (*row, number),
        )
        counters[project] = number + 1
    for project, next_number in counters.items():
        conn.execute("UPDATE projects SET next_bug_number=? WHERE id=?", (next_number, project))

    # Compare every original value, including IDs and timestamps, before replacement.
    copied = conn.execute(f"SELECT {columns} FROM bugs_numbered ORDER BY id").fetchall()
    if copied != original:
        raise RuntimeError("Database migration copy validation failed.")
    _verify_data(conn)  # Also checks the new table's relationships and CHECK/UNIQUE constraints.
    conn.execute("DROP TABLE bugs")
    conn.execute("ALTER TABLE bugs_numbered RENAME TO bugs")


def create_tables():
    """Initialize or upgrade atomically on a dedicated startup connection."""
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version not in (0, SCHEMA_VERSION):
            raise RuntimeError(f"Unsupported database schema version {version}.")
        has_objects = conn.execute("SELECT 1 FROM sqlite_schema WHERE name NOT GLOB 'sqlite_*'").fetchone()
        if version == 0 and not has_objects:
            _create_schema(conn)
        elif version == 0:
            _verify_schema(conn, 0)
            _verify_data(conn)
            _migrate_legacy(conn)
        _verify_schema(conn, SCHEMA_VERSION)
        _verify_data(conn)
        _verify_counters(conn)
        if version == 0:
            conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
        conn.commit()
    except BaseException:
        conn.rollback()
        raise
    finally:
        conn.close()

