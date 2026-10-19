# TC-177 | AC-002.1 — Successful login
def test_successful_login(test_client, user_factory):
    user = user_factory(
        email="login@example.com",
        password="Password1"
    )

    response = test_client.post(
        "/login",
        json=user
    )

    assert response.status_code == 200

    response_data = response.json()

    assert "access_token" in response_data
    assert response_data["token_type"] == "bearer"


# TC-178 | AC-002.2 — Login with incorrect password
def test_login_with_incorrect_password(test_client, user_factory):
    user = user_factory(
        email="wrong-password@example.com",
        password="Password1"
    )

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


# TC-179 | AC-002.2 — Login with unknown email
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


# TC-180 | AC-003.1 — Authenticated user can access protected endpoint
def test_authenticated_user_can_access_protected_endpoint(test_client, authenticated_user_factory):
    authenticated_user = authenticated_user_factory(
        email="protected@example.com",
        password="Password1"
    )

    response = test_client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        }
    )

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["message"] == "You are authenticated."


# TC-181 | AC-003.2 — Unauthenticated user cannot access protected endpoint
def test_unauthenticated_user_cannot_access_protected_endpoint(test_client):
    response = test_client.get("/protected")

    assert response.status_code == 401


# TC-182 | AC-003.3 — Invalid token cannot access protected endpoint
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
