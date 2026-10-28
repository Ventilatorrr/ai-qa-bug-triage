import os
from pathlib import Path
import subprocess
import sys
from textwrap import dedent

from tests.conftest import TEST_JWT_SECRET


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def run_application_script(tmp_path, script):
    database_path = tmp_path / "lifecycle.db"
    environment = os.environ.copy()
    environment["DATABASE_NAME"] = str(database_path)
    # Startup requires a signing secret; CI does not set one in the environment.
    environment["JWT_SECRET_KEY"] = TEST_JWT_SECRET
    result = subprocess.run(
        [sys.executable, "-c", dedent(script)],
        cwd=REPOSITORY_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return database_path


# TC-143 | Technical — Importing application does not create database
def test_importing_application_does_not_create_database(tmp_path):
    database_path = run_application_script(tmp_path, """
        import app.main
    """)

    assert not database_path.exists()
    assert list(tmp_path.iterdir()) == []


# TC-144 | Technical — Application lifespan initializes schema before requests
def test_application_lifespan_initializes_schema_before_requests(tmp_path):
    database_path = run_application_script(tmp_path, """
        from contextlib import closing
        import os
        from pathlib import Path
        import sqlite3
        from unittest.mock import patch

        from fastapi.testclient import TestClient
        from app.main import app, create_tables

        database_path = Path(os.environ["DATABASE_NAME"])
        with patch("app.main.create_tables", wraps=create_tables) as initialize:
            with TestClient(app) as client:
                initialize.assert_called_once_with()
                assert database_path.exists()
                with closing(sqlite3.connect(database_path)) as connection:
                    tables = {row[0] for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )}
                assert tables == {"users", "projects", "project_members", "bugs", "ai_requests"}
                response = client.post("/register", json={
                    "email": "lifecycle@example.com", "password": "Password1"
                })
                assert response.status_code == 201, response.text
            initialize.assert_called_once_with()
    """)

    assert database_path.exists()
