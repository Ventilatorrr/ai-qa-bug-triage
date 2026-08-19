import sqlite3

import bcrypt


# AC-001.1 — Successful Registration
def test_successful_registration(test_client):
    user = {
        "email": "newuser@example.com",
        "password": "Password1"
    }

    response = test_client.post("/register", json=user)

    assert response.status_code == 201
    assert response.json() == {
        "message": "User registered successfully."
    }


# AC-001.2 — Duplicate Email
def test_registration_with_duplicate_email(test_client):
    user = {
        "email": "existing@example.com",
        "password": "Password1"
    }

    first_response = test_client.post("/register", json=user)

    assert first_response.status_code == 201

    second_response = test_client.post("/register", json=user)

    assert second_response.status_code == 409
    assert second_response.json() == {
        "detail": "Email already registered."
    }


# AC-001.3 — Invalid Email
def test_registration_with_invalid_email(test_client):
    user = {
        "email": "not-an-email",
        "password": "Password1"
    }

    response = test_client.post("/register", json=user)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "email"]


# AC-001.4 — Invalid Password: Fewer Than 8 Characters
def test_registration_with_short_password(test_client):
    user = {
        "email": "short@example.com",
        "password": "Pass1"
    }

    response = test_client.post("/register", json=user)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must be at least 8 characters long." in response.json()["detail"][0]["msg"]


# AC-001.4 — Invalid Password: Missing Uppercase Letter
def test_registration_without_uppercase_password(test_client):
    user = {
        "email": "uppercase@example.com",
        "password": "password1"
    }

    response = test_client.post("/register", json=user)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must contain at least one uppercase letter." in response.json()["detail"][0]["msg"]


# AC-001.4 — Invalid Password: Missing Lowercase Letter
def test_registration_without_lowercase_password(test_client):
    user = {
        "email": "lowercase@example.com",
        "password": "PASSWORD1"
    }

    response = test_client.post("/register", json=user)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must contain at least one lowercase letter." in response.json()["detail"][0]["msg"]


# AC-001.4 — Invalid Password: Missing Number
def test_registration_without_number_password(test_client):
    user = {
        "email": "number@example.com",
        "password": "Password"
    }

    response = test_client.post("/register", json=user)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "password"]
    assert "Password must contain at least one number." in response.json()["detail"][0]["msg"]


# AC-001.5 — Password Security
def test_password_is_not_stored_as_plain_text(test_client):
    user = {
        "email": "security@example.com",
        "password": "Password1"
    }

    response = test_client.post("/register", json=user)

    assert response.status_code == 201

    conn = sqlite3.connect("test_bugtriage.db")

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
    