def test_create_project(test_client):
    user = {
        "email": "project@example.com",
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

    response = test_client.post(
        "/projects",
        json={
            "name": "QA Bug Triage"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "QA Bug Triage"
    assert data["owner_id"] > 0


def test_get_projects(test_client):
    user = {
        "email": "projects@example.com",
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

    create_response = test_client.post(
        "/projects",
        json={
            "name": "QA Bug Triage"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert create_response.status_code == 201

    response = test_client.get(
        "/projects",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    projects = response.json()

    assert len(projects) == 1
    assert projects[0]["name"] == "QA Bug Triage"


def test_user_only_sees_own_projects(test_client):
    user1 = {
        "email": "user1@example.com",
        "password": "Password1"
    }

    user2 = {
        "email": "user2@example.com",
        "password": "Password1"
    }

    test_client.post("/register", json=user1)
    test_client.post("/register", json=user2)

    login1 = test_client.post("/login", json=user1)
    token1 = login1.json()["access_token"]

    login2 = test_client.post("/login", json=user2)
    token2 = login2.json()["access_token"]

    response1 = test_client.post(
        "/projects",
        json={"name": "User 1 Project"},
        headers={"Authorization": f"Bearer {token1}"}
    )

    assert response1.status_code == 201

    response2 = test_client.post(
        "/projects",
        json={"name": "User 2 Project"},
        headers={"Authorization": f"Bearer {token2}"}
    )

    assert response2.status_code == 201

    response = test_client.get(
        "/projects",
        headers={"Authorization": f"Bearer {token1}"}
    )

    assert response.status_code == 200

    projects = response.json()

    assert len(projects) == 1
    assert projects[0]["name"] == "User 1 Project"
