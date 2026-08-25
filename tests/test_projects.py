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


# AC-007.1 — Successful Project Name Editing
def test_update_project_name(test_client):
    user = {
        "email": "edit-project@example.com",
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
            "name": "Original Project"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.put(
        f"/projects/{project_id}",
        json={
            "name": "Updated Project"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id
    assert data["name"] == "Updated Project"
    assert data["owner_id"] > 0

    get_response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Updated Project"


# AC-007.2 — Unauthorized Project Name Editing
def test_user_cannot_update_another_users_project(test_client):
    user1 = {
        "email": "project-owner@example.com",
        "password": "Password1"
    }

    user2 = {
        "email": "project-other@example.com",
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
            "name": "Original Project"
        },
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )
    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.put(
        f"/projects/{project_id}",
        json={
            "name": "Unauthorized Change"
        },
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )

    assert response.status_code == 404

    get_response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Original Project"


# AC-008.1 — Successful Project Deletion
def test_delete_project(test_client):
    user = {
        "email": "delete-project@example.com",
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
            "name": "Project To Delete"
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.delete(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Project deleted successfully."

    get_response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    assert get_response.status_code == 404


# AC-008.2 — Unauthorized Project Deletion
def test_user_cannot_delete_another_users_project(test_client):
    user1 = {
        "email": "delete-owner@example.com",
        "password": "Password1"
    }

    user2 = {
        "email": "delete-other@example.com",
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
            "name": "Protected Project"
        },
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )
    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.delete(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {token2}"
        }
    )

    assert response.status_code == 404

    get_response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {token1}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Protected Project"


# AC-009.1 — Add Member
def test_owner_can_add_project_member(test_client):

    owner = {
        "email": "member-owner@example.com",
        "password": "Password1"
    }

    member = {
        "email": "project-member@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=owner
    )

    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=member
    )

    assert registration2.status_code == 201

    login = test_client.post(
        "/login",
        json=owner
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Member Test Project"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": member["email"]
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["project_id"] == project_id
    assert data["email"] == member["email"]


# AC-009.1 — Add Member
def test_added_member_can_access_project(test_client):

    owner = {
        "email": "access-owner@example.com",
        "password": "Password1"
    }

    member = {
        "email": "access-member@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=owner
    )

    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=member
    )

    assert registration2.status_code == 201

    owner_login = test_client.post(
        "/login",
        json=owner
    )

    assert owner_login.status_code == 200

    owner_token = owner_login.json()["access_token"]

    member_login = test_client.post(
        "/login",
        json=member
    )

    assert member_login.status_code == 200

    member_token = member_login.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Member Access Project"
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    add_response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": member["email"]
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert add_response.status_code == 201

    response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {member_token}"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == project_id
    assert response.json()["name"] == "Member Access Project"


# AC-009.2 — Remove Member
def test_owner_can_remove_project_member(test_client):

    owner = {
        "email": "remove-owner@example.com",
        "password": "Password1"
    }

    member = {
        "email": "remove-member@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=owner
    )

    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=member
    )

    assert registration2.status_code == 201

    owner_login = test_client.post(
        "/login",
        json=owner
    )

    assert owner_login.status_code == 200

    owner_token = owner_login.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Remove Member Project"
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    add_response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": member["email"]
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert add_response.status_code == 201

    member_id = add_response.json()["user_id"]

    response = test_client.delete(
        f"/projects/{project_id}/members/{member_id}",
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert response.status_code == 200


# AC-009.2 — Remove Member
def test_removed_member_can_no_longer_access_project(test_client):

    owner = {
        "email": "remove-access-owner@example.com",
        "password": "Password1"
    }

    member = {
        "email": "remove-access-member@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=owner
    )

    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=member
    )

    assert registration2.status_code == 201

    owner_login = test_client.post(
        "/login",
        json=owner
    )

    assert owner_login.status_code == 200

    owner_token = owner_login.json()["access_token"]

    member_login = test_client.post(
        "/login",
        json=member
    )

    assert member_login.status_code == 200

    member_token = member_login.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Remove Access Project"
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    add_response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": member["email"]
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert add_response.status_code == 201

    member_id = add_response.json()["user_id"]

    delete_response = test_client.delete(
        f"/projects/{project_id}/members/{member_id}",
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert delete_response.status_code == 200

    response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {member_token}"
        }
    )

    assert response.status_code == 404


# AC-009.3 — Invalid Member
def test_project_owner_cannot_add_user_who_does_not_have_an_account(test_client):

    owner = {
        "email": "invalid-member-owner@example.com",
        "password": "Password1"
    }

    registration = test_client.post(
        "/register",
        json=owner
    )

    assert registration.status_code == 201

    login = test_client.post(
        "/login",
        json=owner
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Invalid Member Project"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": "nonexistent@example.com"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


# AC-009.4 — Unauthorized Member Management
def test_user_who_is_not_project_owner_cannot_add_project_members(test_client):

    owner = {
        "email": "unauthorized-owner@example.com",
        "password": "Password1"
    }

    user = {
        "email": "unauthorized-user@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=owner
    )

    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=user
    )

    assert registration2.status_code == 201

    owner_login = test_client.post(
        "/login",
        json=owner
    )

    assert owner_login.status_code == 200

    owner_token = owner_login.json()["access_token"]

    user_login = test_client.post(
        "/login",
        json=user
    )

    assert user_login.status_code == 200

    user_token = user_login.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Unauthorized Member Project"
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": owner["email"]
        },
        headers={
            "Authorization": f"Bearer {user_token}"
        }
    )

    assert response.status_code == 404


# AC-009.4 — Unauthorized Member Management
def test_user_who_is_not_project_owner_cannot_remove_project_members(test_client):

    owner = {
        "email": "unauthorized-remove-owner@example.com",
        "password": "Password1"
    }

    member = {
        "email": "unauthorized-remove-member@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=owner
    )

    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=member
    )

    assert registration2.status_code == 201

    owner_login = test_client.post(
        "/login",
        json=owner
    )

    assert owner_login.status_code == 200

    owner_token = owner_login.json()["access_token"]

    member_login = test_client.post(
        "/login",
        json=member
    )

    assert member_login.status_code == 200

    member_token = member_login.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Unauthorized Remove Project"
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    add_response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": member["email"]
        },
        headers={
            "Authorization": f"Bearer {owner_token}"
        }
    )

    assert add_response.status_code == 201

    member_id = add_response.json()["user_id"]

    response = test_client.delete(
        f"/projects/{project_id}/members/{member_id}",
        headers={
            "Authorization": f"Bearer {member_token}"
        }
    )

    assert response.status_code == 404


# AC-009.5 — Duplicate Member
def test_project_owner_cannot_add_same_user_more_than_once(test_client):

    owner = {
        "email": "duplicate-owner@example.com",
        "password": "Password1"
    }

    member = {
        "email": "duplicate-member@example.com",
        "password": "Password1"
    }

    registration1 = test_client.post(
        "/register",
        json=owner
    )

    assert registration1.status_code == 201

    registration2 = test_client.post(
        "/register",
        json=member
    )

    assert registration2.status_code == 201

    login = test_client.post(
        "/login",
        json=owner
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    create_response = test_client.post(
        "/projects",
        json={
            "name": "Duplicate Member Project"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    first_response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": member["email"]
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert first_response.status_code == 201

    second_response = test_client.post(
        f"/projects/{project_id}/members",
        json={
            "email": member["email"]
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "This user is already a member of this project."
