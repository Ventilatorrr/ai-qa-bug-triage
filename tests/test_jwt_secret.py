import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from textwrap import dedent
from datetime import datetime, timedelta, timezone

import jwt
import pytest

from tests.conftest import TEST_JWT_SECRET


OLD_REPO_SECRET = "dev-secret-key-for-local-testing-only"
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


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


@pytest.mark.parametrize("secret", [TEST_JWT_SECRET, f"  {TEST_JWT_SECRET}  "])
def test_token_signed_with_configured_secret(
    test_client, authenticated_user_factory, monkeypatch, secret
):
    """Signing preserves the exact configured secret, including padding."""
    monkeypatch.setenv("JWT_SECRET_KEY", secret)
    auth = authenticated_user_factory(
        email="verify@example.com",
        password="Password1"
    )

    payload = jwt.decode(
        auth["token"],
        key=secret,
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

@pytest.mark.parametrize(
    "secret", [None, "", " " * 32, "\t\r\n" * 12],
    ids=["missing", "empty", "spaces", "mixed-whitespace"],
)
@pytest.mark.parametrize("endpoint", ["/login", "/protected"])
def test_missing_or_blank_jwt_secret_key_rejects_authentication(
    tmp_path, secret, endpoint
):
    """Configuration failures cannot cache database settings in the suite."""
    # Isolate imports as well as files: app.database caches DATABASE_NAME.
    # TemporaryDirectory removes the database even when the assertion fails.
    with TemporaryDirectory(dir=tmp_path) as directory:
        environment = os.environ.copy()
        environment["DATABASE_NAME"] = str(Path(directory) / "jwt.db")
        if secret is None:
            environment.pop("JWT_SECRET_KEY", None)
        else:
            environment["JWT_SECRET_KEY"] = secret

        result = subprocess.run(
            [sys.executable, "-c", dedent("""
                import sys
                import jwt
                import pytest
                from fastapi.testclient import TestClient
                from tests.conftest import TEST_JWT_SECRET
                from app.main import app

                with TestClient(app) as client:
                    user = {
                        "email": "invalid-secret@example.com",
                        "password": "Password1",
                    }
                    response = client.post("/register", json=user)
                    assert response.status_code == 201, response.text
                    token = jwt.encode(
                        {"user_id": 1}, TEST_JWT_SECRET, algorithm="HS256"
                    )
                    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
                        if sys.argv[1] == "/login":
                            client.post("/login", json=user)
                        else:
                            client.get(
                                "/protected",
                                headers={"Authorization": f"Bearer {token}"},
                            )
            """), endpoint],
            cwd=REPOSITORY_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr

    assert list(tmp_path.iterdir()) == []


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
