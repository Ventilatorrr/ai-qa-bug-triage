import jwt
import pytest

from datetime import datetime, timedelta, timezone

from tests.conftest import TEST_JWT_SECRET


OLD_REPO_SECRET = "dev-secret-key-for-local-testing-only"


# --- Normal auth flow uses configured secret ---

def test_login_and_access_with_configured_secret(
    test_client, authenticated_user_factory
):
    """Registration, login, and authenticated access work when
    JWT_SECRET_KEY is configured."""
    auth = authenticated_user_factory(
        email="configured@example.com",
        password="Password1"
    )

    response = test_client.get(
        "/protected",
        headers={"Authorization": f"Bearer {auth['token']}"}
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == auth["user_id"]


def test_token_signed_with_configured_secret(
    test_client, authenticated_user_factory
):
    """Tokens returned by login are verifiable with the test secret."""
    auth = authenticated_user_factory(
        email="verify@example.com",
        password="Password1"
    )

    payload = jwt.decode(
        auth["token"],
        key=TEST_JWT_SECRET,
        algorithms=["HS256"]
    )

    assert payload["user_id"] == auth["user_id"]


# --- Old repository-known secret rejected ---

def test_forged_token_with_old_secret_is_rejected(test_client, user_factory):
    """A token forged with the old published secret must be rejected
    when the application uses a different configured secret."""
    user_factory(email="victim@example.com", password="Password1")

    forged_token = jwt.encode(
        {
            "user_id": 1,
            "exp": datetime.now(timezone.utc) + timedelta(hours=1)
        },
        key=OLD_REPO_SECRET,
        algorithm="HS256"
    )

    response = test_client.get(
        "/protected",
        headers={"Authorization": f"Bearer {forged_token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token."


# --- Missing configuration fails securely ---

def test_missing_jwt_secret_key_raises_on_login(monkeypatch, tmp_path):
    """When JWT_SECRET_KEY is not set, login must fail with a clear
    RuntimeError rather than silently using a default."""
    db_path = str(tmp_path / "jwt_missing.db")

    monkeypatch.delenv("JWT_SECRET_KEY", raising=False)

    from app.main import app

    monkeypatch.setattr("app.database.DATABASE_NAME", db_path)

    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        client.post(
            "/register",
            json={
                "email": "missing-secret@example.com",
                "password": "Password1"
            }
        )

        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            client.post(
                "/login",
                json={
                    "email": "missing-secret@example.com",
                    "password": "Password1"
                }
            )


def test_empty_jwt_secret_key_raises_on_login(monkeypatch, tmp_path):
    """An empty JWT_SECRET_KEY must be treated as missing."""
    db_path = str(tmp_path / "jwt_empty.db")

    monkeypatch.setenv("JWT_SECRET_KEY", "")

    from app.main import app

    monkeypatch.setattr("app.database.DATABASE_NAME", db_path)

    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        client.post(
            "/register",
            json={
                "email": "empty-secret@example.com",
                "password": "Password1"
            }
        )

        with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
            client.post(
                "/login",
                json={
                    "email": "empty-secret@example.com",
                    "password": "Password1"
                }
            )


# --- Secret not exposed in HTTP responses ---

def test_secret_not_in_login_response(
    test_client, authenticated_user_factory
):
    """The JWT secret must not appear in any login response field."""
    auth = authenticated_user_factory(
        email="leak-check@example.com",
        password="Password1"
    )

    login_response = test_client.post(
        "/login",
        json={
            "email": "leak-check@example.com",
            "password": "Password1"
        }
    )

    response_text = login_response.text
    assert TEST_JWT_SECRET not in response_text


def test_secret_not_in_protected_response(
    test_client, authenticated_user_factory
):
    """The JWT secret must not appear in authenticated endpoint responses."""
    auth = authenticated_user_factory(
        email="leak-protected@example.com",
        password="Password1"
    )

    response = test_client.get(
        "/protected",
        headers={"Authorization": f"Bearer {auth['token']}"}
    )

    response_text = response.text
    assert TEST_JWT_SECRET not in response_text


def test_secret_not_in_error_response(test_client):
    """The JWT secret must not appear in 401 error responses."""
    response = test_client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401

    response_text = response.text
    assert TEST_JWT_SECRET not in response_text
