# AC-005.1 — Successful Project Creation
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

    protected_response = test_client.get(
        "/protected",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert protected_response.status_code == 200

    user_id = protected_response.json()["user_id"]

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
    assert data["owner_id"] == user_id


# AC-005.2 — Invalid Project Name
def test_create_project_with_empty_name(test_client):
    user = {
        "email": "invalid-project@example.com",
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
            "name": ""
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Project name is required."
    }


# AC-005.3 — Unauthenticated User
def test_unauthenticated_user_cannot_create_project(test_client):
    response = test_client.post(
        "/projects",
        json={
            "name": "QA Bug Triage"
        }
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Authentication required."
    }
    

# AC-006.1 — View Project List
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


# AC-006.2 — Project List Authorization
def test_user_only_sees_own_projects(test_client):
    user1 = {
        "email": "user1@example.com",
        "password": "Password1"
    }

    user2 = {
        "email": "user2@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=user1
    )
    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=user2
    )
    assert registration2.status_code == 201

    login1 = test_client.post(
        "/login",
        json=user1
    )
    assert login1.status_code == 200
    token1 = login1.json()["access_token"]

    login2 = test_client.post(
        "/login",
        json=user2
    )
    assert login2.status_code == 200
    token2 = login2.json()["access_token"]

    response1 = test_client.post(
        "/projects",
        json={
            "name": "User 1 Project"
        },
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )
    assert response1.status_code == 201

    response2 = test_client.post(
        "/projects",
        json={
            "name": "User 2 Project"
        },
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )
    assert response2.status_code == 201

    response = test_client.get(
        "/projects",
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    assert response.status_code == 200

    projects = response.json()
    assert len(projects) == 1
    assert projects[0]["name"] == "User 1 Project"


# AC-006.3 — Open Project
def test_get_project(test_client):
    user = {
        "email": "single-project@example.com",
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
            "name": "Single Project"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    project = response.json()
    assert project["id"] == project_id
    assert project["name"] == "Single Project"


# AC-006.4 — Unauthorized Project Access
def test_user_cannot_access_another_users_project(test_client):
    user1 = {
        "email": "owner@example.com",
        "password": "Password1"
    }

    user2 = {
        "email": "other@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=user1
    )
    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=user2
    )
    assert registration2.status_code == 201

    login1 = test_client.post(
        "/login",
        json=user1
    )
    assert login1.status_code == 200
    token1 = login1.json()["access_token"]

    login2 = test_client.post(
        "/login",
        json=user2
    )
    assert login2.status_code == 200
    token2 = login2.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Private Project"
        },
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )
    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )

    assert response.status_code == 404
