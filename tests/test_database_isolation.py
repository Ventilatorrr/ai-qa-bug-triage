import os
from pathlib import Path
import sqlite3

import pytest


def test_client_rebinds_cached_database_before_startup(tmp_path, monkeypatch, request):
    # Simulate an earlier import with another setting, using only a synthetic path.
    stale_path = tmp_path / "must-not-open.db"
    monkeypatch.setenv("DATABASE_NAME", str(stale_path))
    from app import database

    monkeypatch.setattr(database, "DATABASE_NAME", str(stale_path))
    expected_path = (tmp_path / "test_bugtriage.db").resolve()
    connect = sqlite3.connect
    opened = []

    def guarded_connect(path, *args, **kwargs):
        # Reject a wrong target before SQLite can open or create it.
        # Schema verification also builds a disposable in-memory reference.
        if path != ":memory:":
            assert Path(path) == expected_path
            opened.append(Path(path))
        return connect(path, *args, **kwargs)

    def assert_database_removed():
        assert not expected_path.exists()

    # Register before requesting the client so its dependent fixtures finish first.
    request.addfinalizer(assert_database_removed)
    monkeypatch.setattr(sqlite3, "connect", guarded_connect)
    client = request.getfixturevalue("test_client")
    assert database.DATABASE_NAME == os.environ["DATABASE_NAME"] == str(expected_path)
    assert request.getfixturevalue("test_database") == expected_path
    assert opened, "Application lifespan must initialize the disposable database."
    assert not stale_path.exists()
    assert client.get("/version").status_code == 200


@pytest.mark.parametrize("attempt", [1, 2])
def test_client_starts_with_fresh_database(test_client, test_database, authenticated_user_factory, attempt):
    # Both cases register the same account and create the same project. Each
    # must succeed independently; a reused database would reject registration.
    auth = authenticated_user_factory(email="isolation@example.com")
    headers = {"Authorization": f"Bearer {auth['token']}"}
    response = test_client.get("/projects", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
    created = test_client.post("/projects", headers=headers, json={"name": f"Isolation project {attempt}"})
    assert created.status_code == 201
    assert test_database.is_absolute()
    assert test_database.exists()
