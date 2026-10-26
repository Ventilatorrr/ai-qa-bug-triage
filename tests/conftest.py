import os

import jwt
import pytest

from fastapi.testclient import TestClient

TEST_JWT_SECRET = "test-only-jwt-secret-not-for-production"


@pytest.fixture
def test_database(tmp_path, monkeypatch):
    database_path = (tmp_path / "test_bugtriage.db").resolve()
    assert not database_path.exists()
    monkeypatch.setenv("DATABASE_NAME", str(database_path))

    # Configure before importing the app; imports themselves do not open SQLite.
    # Rebind the cached setting too, whether database was imported earlier or not.
    from app import database

    monkeypatch.setattr(database, "DATABASE_NAME", str(database_path))
    assert database.DATABASE_NAME == os.environ["DATABASE_NAME"] == str(database_path)
    try:
        yield database_path
    finally:
        # Dependent TestClient fixtures exit lifespan before this teardown runs.
        database_path.unlink(missing_ok=True)


@pytest.fixture
def test_client(test_database, monkeypatch):
    monkeypatch.setenv("JWT_SECRET_KEY", TEST_JWT_SECRET)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("AI_DAILY_USER_LIMIT", raising=False)
    monkeypatch.delenv("AI_DAILY_GLOBAL_LIMIT", raising=False)

    from app.main import app
    from app import database

    assert database.DATABASE_NAME == str(test_database)
    with TestClient(app) as client:
        yield client


@pytest.fixture
def user_factory(test_client):
    def create_user(
        email="user@example.com",
        password="Password1"
    ):
        user = {
            "email": email,
            "password": password
        }

        response = test_client.post(
            "/register",
            json=user
        )

        assert response.status_code == 201

        return user

    return create_user


@pytest.fixture
def authenticated_user_factory(test_client, user_factory):
    def create_authenticated_user(
        email="user@example.com",
        password="Password1"
    ):
        user = user_factory(
            email=email,
            password=password
        )

        response = test_client.post(
            "/login",
            json=user
        )

        assert response.status_code == 200

        token = response.json()["access_token"]

        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )

        return {
            "user": user,
            "user_id": payload["user_id"],
            "token": token
        }

    return create_authenticated_user


@pytest.fixture
def project_factory(test_client):
    def create_project(token, name="QA Bug Triage"):
        response = test_client.post(
            "/projects",
            json={
                "name": name
            },
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 201

        return response.json()

    return create_project


@pytest.fixture
def member_factory(test_client):
    def add_member(token, project_id, email, role):
        response = test_client.post(
            f"/projects/{project_id}/members",
            json={
                "email": email,
                "role": role
            },
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        assert response.status_code == 201

        return response.json()

    return add_member
