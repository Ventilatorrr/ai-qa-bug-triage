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

    with TestClient(app) as client:
        yield client

    if os.path.exists(TEST_DATABASE):
        os.remove(TEST_DATABASE)


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

        return {
            "user": user,
            "token": response.json()["access_token"]
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
    