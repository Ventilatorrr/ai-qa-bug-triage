import sqlite3

import bcrypt
import pytest


# TC-217 | AC-001.1 — Successful registration
def test_successful_registration(test_client):
    user = {
        "email": "newuser@example.com",
        "password": "Password1"
    }

    response = test_client.post(
        "/register",
        json=user
    )

    assert response.status_code == 201
    assert response.json() == {
        "message": "User registered successfully."
    }


# TC-218 | AC-001.2 — Registration with duplicate email
def test_registration_with_duplicate_email(test_client, user_factory):
    user = user_factory(
        email="existing@example.com",
        password="Password1"
    )

    second_response = test_client.post(
        "/register",
        json=user
    )

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Email already registered."
    }


# TC-219 | AC-001.3 — Registration with invalid email
@pytest.mark.parametrize("email", ["not-an-email", "user@", "@example.com"])
def test_registration_with_invalid_email(test_client, email):
    user = {
        "email": email,
        "password": "Password1"
    }

    response = test_client.post(
        "/register",
        json=user
    )

    assert response.status_code == 422
    errors = response.json()["detail"]
    assert len(errors) == 1
    assert errors[0]["loc"] == ["body", "email"]
    assert "not a valid email address" in errors[0]["msg"]


# TC-220 | AC-001.4 — Registration with short password
def test_registration_with_short_password(test_client):
    user = {
        "email": "short@example.com",
        "password": "Pass1"
    }

    response = test_client.post(
        "/register",
        json=user
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must be at least 8 characters long." in response.json()["detail"][0]["msg"]


# TC-221 | AC-001.4 — Registration without uppercase password
def test_registration_without_uppercase_password(test_client):
    user = {
        "email": "uppercase@example.com",
        "password": "password1"
    }

    response = test_client.post(
        "/register",
        json=user
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must contain at least one uppercase letter." in response.json()["detail"][0]["msg"]


# TC-222 | AC-001.4 — Registration without lowercase password
def test_registration_without_lowercase_password(test_client):
    user = {
        "email": "lowercase@example.com",
        "password": "PASSWORD1"
    }

    response = test_client.post(
        "/register",
        json=user
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must contain at least one lowercase letter." in response.json()["detail"][0]["msg"]


# TC-223 | AC-001.4 — Registration without number password
def test_registration_without_number_password(test_client):
    user = {
        "email": "number@example.com",
        "password": "Password"
    }

    response = test_client.post(
        "/register",
        json=user
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must contain at least one number." in response.json()["detail"][0]["msg"]


# Additional validation test
# TC-224 | Technical — Registration rejects invalid password for existing email
def test_registration_rejects_invalid_password_for_existing_email(test_client, user_factory):
    user = user_factory(
        email="existing@example.com",
        password="Password1"
    )

    invalid_user = {
        "email": user["email"],
        "password": "rs3Tss"
    }

    response = test_client.post(
        "/register",
        json=invalid_user
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must be at least 8 characters long." in response.json()["detail"][0]["msg"]


# TC-225 | AC-001.5 — Password is not stored as plain text
def test_password_is_not_stored_as_plain_text(test_client, test_database, user_factory):
    user = user_factory(
        email="security@example.com",
        password="Password1"
    )

    conn = sqlite3.connect(test_database)

    row = conn.execute(
        "SELECT password_hash FROM users WHERE email = ?",
        (user["email"],)
    ).fetchone()

    conn.close()

    assert row[0] != user["password"]
    assert bcrypt.checkpw(
        user["password"].encode("utf-8"),
        row[0].encode("utf-8")
    )

# Regression Test — Registration rejects passwords over bcrypt's 72-byte limit
# TC-226 | Technical — Registration rejects password over bcrypt limit
def test_registration_rejects_password_over_bcrypt_limit(test_client):
    response = test_client.post(
        "/register",
        json={
            "email": "long-password@example.com",
            "password": ("A" * 71) + "a1"
        }
    )

    assert response.status_code == 422

    detail = response.json()["detail"]

    assert detail[0]["loc"] == ["body", "password"]
    assert "Password must be 72 bytes or fewer." in detail[0]["msg"]

