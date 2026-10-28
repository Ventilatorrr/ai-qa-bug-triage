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
REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


# --- Normal auth flow uses configured secret ---

# TC-169 | AC-002.1 — Login and access with configured secret
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


# TC-170 | Technical — Token signed with configured secret
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

# TC-171 | AC-003.3 — Forged token with old secret is rejected
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



# TC-172 | AC-003.3 — Correctly signed expired token is rejected
@pytest.mark.parametrize("endpoint", ["/protected", "/projects"])
def test_correctly_signed_expired_token_is_rejected(
    test_client, authenticated_user_factory, endpoint
):
    auth = authenticated_user_factory(email="expired-token@example.com")
    payload = {
        "user_id": auth["user_id"],
        "exp": datetime.now(timezone.utc) - timedelta(minutes=5),
    }
    token = jwt.encode(payload, key=TEST_JWT_SECRET, algorithm="HS256")

    # Verify the signature independently; expiry is the only disabled check.
    decoded = jwt.decode(
        token, key=TEST_JWT_SECRET, algorithms=["HS256"],
        options={"verify_exp": False},
    )
    assert decoded["user_id"] == auth["user_id"]
    with pytest.raises(jwt.ExpiredSignatureError):
        jwt.decode(token, key=TEST_JWT_SECRET, algorithms=["HS256"])

    valid = test_client.get(
        endpoint, headers={"Authorization": f"Bearer {auth['token']}"}
    )
    response = test_client.get(
        endpoint, headers={"Authorization": f"Bearer {token}"}
    )

    assert valid.status_code == 200
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token."}


# --- Missing configuration fails securely ---

# TC-173 | Technical — Missing or blank JWT secret key stops startup before the database is touched
@pytest.mark.parametrize(
    "secret", [None, "", " " * 32, "\t\r\n" * 12],
    ids=["missing", "empty", "spaces", "mixed-whitespace"],
)
def test_missing_or_blank_jwt_secret_key_stops_startup(tmp_path, secret):
    """Configuration failures cannot cache database settings in the suite."""
    # Isolate imports as well as files: app.database caches DATABASE_NAME.
    # TemporaryDirectory removes the database even when the assertion fails.
    with TemporaryDirectory(dir=tmp_path) as directory:
        database_path = Path(directory) / "jwt.db"
        environment = os.environ.copy()
        environment["DATABASE_NAME"] = str(database_path)
        if secret is None:
            environment.pop("JWT_SECRET_KEY", None)
        else:
            environment["JWT_SECRET_KEY"] = secret

        result = subprocess.run(
            [sys.executable, "-c", dedent("""
                import pytest
                from fastapi.testclient import TestClient
                from app.main import app

                with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
                    with TestClient(app):
                        pass
            """)],
            cwd=REPOSITORY_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        # Startup stopped before creating or migrating the database.
        assert not database_path.exists()

    assert list(tmp_path.iterdir()) == []


# --- Secret not exposed in HTTP responses ---

# TC-174 | Technical — Secret not in login response
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


# TC-175 | Technical — Secret not in protected response
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


# TC-176 | Technical — Secret not in error response
def test_secret_not_in_error_response(test_client):
    """The JWT secret must not appear in 401 error responses."""
    response = test_client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401

    response_text = response.text
    assert TEST_JWT_SECRET not in response_text


# TC-484 | AC-003.3 — A correctly signed token for a missing account is rejected and writes nothing (BUG-48 regression)
def test_token_for_missing_account_is_rejected(test_client, test_database, authenticated_user_factory):
    from tests.backend.test_demo import table_counts

    existing = authenticated_user_factory(email="existing-account@example.com")
    token = jwt.encode(
        {"user_id": existing["user_id"] + 1000, "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
        key=TEST_JWT_SECRET,
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}
    before = table_counts(test_database)

    for method, path, body in [("GET", "/projects", None), ("POST", "/projects", {"name": "Orphan"})]:
        response = test_client.request(method, path, headers=headers, json=body)
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token."}

    assert table_counts(test_database) == before
    # The existing account's own token is unaffected.
    valid = {"Authorization": f"Bearer {existing['token']}"}
    assert test_client.get("/projects", headers=valid).status_code == 200
