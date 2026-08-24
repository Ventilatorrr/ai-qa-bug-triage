# AC-002.1 — Successful Login
def test_successful_login(test_client):
    user = {
        "email": "login@example.com",
        "password": "Password1"
    }

    registration_response = test_client.post(
        "/register",
        json=user
    )
    assert registration_response.status_code == 201

    response = test_client.post(
        "/login",
        json=user
    )

    assert response.status_code == 200

    response_data = response.json()
    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


# AC-002.2 — Invalid Credentials: Incorrect Password
def test_login_with_incorrect_password(test_client):
    user = {
        "email": "wrong-password@example.com",
        "password": "Password1"
    }

    registration_response = test_client.post(
        "/register",
        json=user
    )
    assert registration_response.status_code == 201

    invalid_user = {
        "email": user["email"],
        "password": "WrongPassword1"
    }

    response = test_client.post(
        "/login",
        json=invalid_user
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password."
    }


# AC-002.2 — Invalid Credentials: Unknown Email
def test_login_with_unknown_email(test_client):
    user = {
        "email": "unknown@example.com",
        "password": "Password1"
    }

    response = test_client.post(
        "/login",
        json=user
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password."
    }


# AC-003.1 — Authenticated Access
def test_authenticated_user_can_access_protected_endpoint(test_client):
    user = {
        "email": "protected@example.com",
        "password": "Password1"
    }

    registration_response = test_client.post(
        "/register",
        json=user
    )
    assert registration_response.status_code == 201

    login_response = test_client.post(
        "/login",
        json=user
    )
    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    response = test_client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    response_data = response.json()
    assert response_data["message"] == "You are authenticated."


# AC-003.2 — Unauthenticated Access
def test_unauthenticated_user_cannot_access_protected_endpoint(test_client):
    response = test_client.get("/protected")

    assert response.status_code == 401


# AC-003.3 — Invalid Authentication
def test_invalid_token_cannot_access_protected_endpoint(test_client):
    response = test_client.get(
        "/protected",
        headers={
            "Authorization": "Bearer invalid-token"
        }
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or expired token."
    }
    