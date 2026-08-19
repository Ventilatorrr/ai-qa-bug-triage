import os

import pytest
from fastapi.testclient import TestClient

TEST_DATABASE = "test_bugtriage.db"


@pytest.fixture
def test_client(monkeypatch):
    monkeypatch.setenv("DATABASE_NAME", TEST_DATABASE)

    from app.main import app
    from app.database import create_tables

    create_tables()

    yield TestClient(app)

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)
