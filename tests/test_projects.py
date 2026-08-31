import pytest


# AC-005.1 — Successful Project Creation
def test_create_project(test_client, authenticated_user_factory, project_factory):
    authenticated_user = authenticated_user_factory(
        email="project@example.com",
        password="Password1"
    )

    project = project_factory(
        authenticated_user["token"],
        name="QA Bug Triage"
    )

    assert project["name"] == "QA Bug Triage"


# AC-005.2 — Invalid Project Name
def test_create_project_with_empty_name(test_client, authenticated_user_factory):
    authenticated_user = authenticated_user_factory(
        email="invalid-project@example.com",
        password="Password1"
    )

    response = test_client.post(
        "/projects",
        json={
            "name": ""
        },
        headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
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
def test_get_projects(test_client, authenticated_user_factory, project_factory):
    authenticated_user = authenticated_user_factory(
        email="projects@example.com",
        password="Password1"
    )

    project_factory(
        authenticated_user["token"],
        name="QA Bug Triage"
    )

    response = test_client.get(
        "/projects",
        headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        }
    )

    assert response.status_code == 200

    projects = response.json()

    assert len(projects) == 1
    assert projects[0]["name"] == "QA Bug Triage"


# AC-006.2 — Project List Authorization
def test_user_only_sees_own_projects(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user1 = authenticated_user_factory(
        email="user1@example.com",
        password="Password1"
    )
    user2 = authenticated_user_factory(
        email="user2@example.com",
        password="Password1"
    )

    project_factory(
        user1["token"],
        name="User 1 Project"
    )
    project_factory(
        user2["token"],
        name="User 2 Project"
    )

    response = test_client.get(
        "/projects",
        headers={
            "Authorization": f"Bearer {user1['token']}"
        }
    )

    assert response.status_code == 200

    projects = response.json()

    assert len(projects) == 1
    assert projects[0]["name"] == "User 1 Project"


# AC-006.3 — Open Project
def test_get_project(test_client, authenticated_user_factory, project_factory):
    authenticated_user = authenticated_user_factory(
        email="single-project@example.com",
        password="Password1"
    )

    project = project_factory(
        authenticated_user["token"],
        name="Single Project"
    )

    project_id = project["id"]

    response = test_client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        }
    )

    assert response.status_code == 200

    project = response.json()

    assert project["id"] == project_id
    assert project["name"] == "Single Project"


# AC-006.4 — Unauthorized Project Access
def test_user_cannot_access_another_users_project(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user1 = authenticated_user_factory(
        email="owner@example.com",
        password="Password1"
    )
    user2 = authenticated_user_factory(
        email="other@example.com",
        password="Password1"
    )

    project = project_factory(
        user1["token"],
        name="Private Project"
    )

    response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {user2['token']}"
        }
    )

    assert response.status_code == 404


# AC-007.1 — Successful Project Name Editing
def test_edit_project_name(test_client, authenticated_user_factory, project_factory):
    authenticated_user = authenticated_user_factory(
        email="edit-project@example.com",
        password="Password1"
    )

    project = project_factory(
        authenticated_user["token"],
        name="Original Project"
    )

    response = test_client.put(
        f"/projects/{project['id']}",
        json={
            "name": "Updated Project"
        },
        headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project["id"]
    assert data["name"] == "Updated Project"


# AC-007.2 — Unauthorized Project Name Editing
def test_user_cannot_edit_another_users_project_name(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user1 = authenticated_user_factory(
        email="project-owner@example.com",
        password="Password1"
    )
    user2 = authenticated_user_factory(
        email="project-other@example.com",
        password="Password1"
    )

    project = project_factory(
        user1["token"],
        name="Original Project"
    )

    response = test_client.put(
        f"/projects/{project['id']}",
        json={
            "name": "Unauthorized Change"
        },
        headers={
            "Authorization": f"Bearer {user2['token']}"
        }
    )

    assert response.status_code == 404

    get_response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {user1['token']}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Original Project"


# AC-008.1 — Successful Project Deletion
def test_delete_project(test_client, authenticated_user_factory, project_factory):
    authenticated_user = authenticated_user_factory(
        email="delete-project@example.com",
        password="Password1"
    )

    project = project_factory(
        authenticated_user["token"],
        name="Project To Delete"
    )

    response = test_client.delete(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Project deleted successfully."

    get_response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {authenticated_user['token']}"
        }
    )

    assert get_response.status_code == 404


# AC-008.2 — Unauthorized Project Deletion
def test_user_cannot_delete_another_users_project(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user1 = authenticated_user_factory(
        email="delete-owner@example.com",
        password="Password1"
    )
    user2 = authenticated_user_factory(
        email="delete-other@example.com",
        password="Password1"
    )

    project = project_factory(
        user1["token"],
        name="Protected Project"
    )

    response = test_client.delete(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {user2['token']}"
        }
    )

    assert response.status_code == 404

    get_response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {user1['token']}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Protected Project"


# AC-009.1 — Add Member
def test_owner_can_add_project_member(
    test_client,
    authenticated_user_factory,
    project_factory,
    user_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="member-owner@example.com",
        password="Password1"
    )
    member = user_factory(
        email="project-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Member Test Project"
    )

    member_data = member_factory(
        owner["token"],
        project["id"],
        member["email"],
        "QA Analyst"
    )

    assert member_data["project_id"] == project["id"]
    assert member_data["email"] == member["email"]
    assert member_data["role"] == "QA Analyst"


# AC-009.1 — Add Member
def test_added_member_can_access_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="access-owner@example.com",
        password="Password1"
    )
    member = authenticated_user_factory(
        email="access-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Member Access Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        member["user"]["email"],
        "QA Analyst"
    )

    response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {member['token']}"
        }
    )

    assert response.status_code == 200
    assert response.json()["id"] == project["id"]
    assert response.json()["name"] == "Member Access Project"


# AC-009.2 — Remove Member
def test_owner_can_remove_project_member(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="remove-owner@example.com",
        password="Password1"
    )
    member = authenticated_user_factory(
        email="remove-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Remove Member Project"
    )

    member_data = member_factory(
        owner["token"],
        project["id"],
        member["user"]["email"],
        "QA Analyst"
    )

    response = test_client.delete(
        f"/projects/{project['id']}/members/{member_data['user_id']}",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert response.status_code == 200


# AC-009.2 — Remove Member
def test_removed_member_can_no_longer_access_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="remove-access-owner@example.com",
        password="Password1"
    )
    member = authenticated_user_factory(
        email="remove-access-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Remove Access Project"
    )

    member_data = member_factory(
        owner["token"],
        project["id"],
        member["user"]["email"],
        "QA Analyst"
    )

    delete_response = test_client.delete(
        f"/projects/{project['id']}/members/{member_data['user_id']}",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert delete_response.status_code == 200

    response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {member['token']}"
        }
    )

    assert response.status_code == 404


# AC-009.3 — Invalid Member
def test_project_owner_cannot_add_user_who_does_not_have_an_account(
    test_client,
    authenticated_user_factory,
    project_factory
):
    owner = authenticated_user_factory(
        email="invalid-member-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Invalid Member Project"
    )

    response = test_client.post(
        f"/projects/{project['id']}/members",
        json={
            "email": "nonexistent@example.com",
            "role": "QA Analyst"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "User not found."


# AC-009.4 — Duplicate Member
def test_project_owner_cannot_add_same_user_more_than_once(
    test_client,
    authenticated_user_factory,
    project_factory,
    user_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="duplicate-owner@example.com",
        password="Password1"
    )
    member = user_factory(
        email="duplicate-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Duplicate Member Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        member["email"],
        "QA Analyst"
    )

    second_response = test_client.post(
        f"/projects/{project['id']}/members",
        json={
            "email": member["email"],
            "role": "Developer"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "This user is already a member of this project."


# AC-010.4 — Unauthorized Project Member Management
@pytest.mark.parametrize("role", ["QA Analyst", "Developer"])
def test_non_owner_cannot_manage_project_members(
    test_client,
    authenticated_user_factory,
    project_factory,
    user_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(
        email="manage-owner@example.com",
        password="Password1"
    )
    non_owner = authenticated_user_factory(
        email="manage-non-owner@example.com",
        password="Password1"
    )
    existing_member = user_factory(
        email="manage-existing-member@example.com",
        password="Password1"
    )
    new_user = user_factory(
        email="manage-new-user@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Member Management Authorization Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        non_owner["user"]["email"],
        role
    )

    existing_member_data = member_factory(
        owner["token"],
        project["id"],
        existing_member["email"],
        "Developer"
    )

    response = test_client.post(
        f"/projects/{project['id']}/members",
        json={
            "email": new_user["email"],
            "role": "Developer"
        },
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404

    response = test_client.delete(
        f"/projects/{project['id']}/members/{existing_member_data['user_id']}",
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404


# AC-010.5 — Unauthorized Project Actions
@pytest.mark.parametrize("role", ["QA Analyst", "Developer"])
def test_non_owner_cannot_edit_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(
        email="edit-owner@example.com",
        password="Password1"
    )
    non_owner = authenticated_user_factory(
        email="edit-non-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Edit Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        non_owner["user"]["email"],
        role
    )

    response = test_client.put(
        f"/projects/{project['id']}",
        json={
            "name": "Unauthorized Change"
        },
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404

    get_response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Protected Edit Project"


# AC-010.5 — Unauthorized Project Actions
@pytest.mark.parametrize("role", ["QA Analyst", "Developer"])
def test_non_owner_cannot_delete_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(
        email="delete-owner@example.com",
        password="Password1"
    )
    non_owner = authenticated_user_factory(
        email="delete-non-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Delete Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        non_owner["user"]["email"],
        role
    )

    response = test_client.delete(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404

    get_response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Protected Delete Project"


# AC-009.5 — View Project Members
def test_project_member_can_view_project_members(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="members-owner@example.com",
        password="Password1"
    )
    qa_analyst = authenticated_user_factory(
        email="members-qa@example.com",
        password="Password1"
    )
    developer = authenticated_user_factory(
        email="members-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Project Members Test"
    )

    member_factory(
        owner["token"],
        project["id"],
        qa_analyst["user"]["email"],
        "QA Analyst"
    )
    member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    response = test_client.get(
        f"/projects/{project['id']}/members",
        headers={
            "Authorization": f"Bearer {qa_analyst['token']}"
        }
    )

    assert response.status_code == 200

    members = response.json()

    assert len(members) == 3

    assert members[0]["email"] == owner["user"]["email"]
    assert members[0]["role"] == "Project Owner"

    assert members[1]["email"] == qa_analyst["user"]["email"]
    assert members[1]["role"] == "QA Analyst"

    assert members[2]["email"] == developer["user"]["email"]
    assert members[2]["role"] == "Developer"


# Additional security test — Project Owner Self-Removal
def test_project_owner_cannot_remove_themselves(
    test_client,
    authenticated_user_factory,
    project_factory
):
    owner = authenticated_user_factory(
        email="self-remove-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Owner Self-Removal Project"
    )

    members_response = test_client.get(
        f"/projects/{project['id']}/members",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert members_response.status_code == 200

    members = members_response.json()

    owner_member = next(
        member
        for member in members
        if member["email"] == owner["user"]["email"]
    )

    response = test_client.delete(
        f"/projects/{project['id']}/members/{owner_member['user_id']}",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == (
        "Project Owner cannot be removed from the project."
    )

    members_response = test_client.get(
        f"/projects/{project['id']}/members",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert members_response.status_code == 200

    members = members_response.json()

    owner_member = next(
        member
        for member in members
        if member["email"] == owner["user"]["email"]
    )

    assert owner_member["role"] == "Project Owner"


# AC-010.1 — Project Owner Role
def test_project_creator_is_project_owner(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="creator-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Owner Role Project"
    )

    response = test_client.get(
        f"/projects/{project['id']}/members",
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert response.status_code == 200

    members = response.json()

    owner = next(
        member
        for member in members
        if member["email"] == user["user"]["email"]
    )

    assert owner["role"] == "Project Owner"


# AC-010.2 — QA Analyst Role
def test_qa_analyst_can_access_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="qa-access-owner@example.com",
        password="Password1"
    )
    qa_analyst = authenticated_user_factory(
        email="qa-access-user@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="QA Analyst Access Project"
    )

    member_data = member_factory(
        owner["token"],
        project["id"],
        qa_analyst["user"]["email"],
        "QA Analyst"
    )

    assert member_data["role"] == "QA Analyst"

    response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {qa_analyst['token']}"
        }
    )

    assert response.status_code == 200

    project_data = response.json()

    assert project_data["id"] == project["id"]
    assert project_data["name"] == "QA Analyst Access Project"


# AC-010.3 — Developer Role
def test_developer_can_access_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="developer-access-owner@example.com",
        password="Password1"
    )
    developer = authenticated_user_factory(
        email="developer-access-user@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Developer Access Project"
    )

    member_data = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    assert member_data["role"] == "Developer"

    response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert response.status_code == 200

    project_data = response.json()

    assert project_data["id"] == project["id"]
    assert project_data["name"] == "Developer Access Project"


# AC-010.4 — Unauthorized Project Member Management
@pytest.mark.parametrize("role", ["QA Analyst", "Developer"])
def test_non_owner_cannot_manage_project_members(
    test_client,
    authenticated_user_factory,
    project_factory,
    user_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(
        email="manage-owner@example.com",
        password="Password1"
    )
    non_owner = authenticated_user_factory(
        email="manage-non-owner@example.com",
        password="Password1"
    )
    existing_member = user_factory(
        email="manage-existing-member@example.com",
        password="Password1"
    )
    new_user = user_factory(
        email="manage-new-user@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Member Management Authorization Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        non_owner["user"]["email"],
        role
    )

    existing_member_data = member_factory(
        owner["token"],
        project["id"],
        existing_member["email"],
        "Developer"
    )

    response = test_client.post(
        f"/projects/{project['id']}/members",
        json={
            "email": new_user["email"],
            "role": "Developer"
        },
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404

    response = test_client.delete(
        f"/projects/{project['id']}/members/{existing_member_data['user_id']}",
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404


# AC-010.5 — Unauthorized Project Actions
@pytest.mark.parametrize("role", ["QA Analyst", "Developer"])
def test_non_owner_cannot_edit_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(
        email="edit-owner@example.com",
        password="Password1"
    )
    non_owner = authenticated_user_factory(
        email="edit-non-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Edit Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        non_owner["user"]["email"],
        role
    )

    response = test_client.put(
        f"/projects/{project['id']}",
        json={
            "name": "Unauthorized Change"
        },
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404

    get_response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Protected Edit Project"


# AC-010.5 — Unauthorized Project Actions
@pytest.mark.parametrize("role", ["QA Analyst", "Developer"])
def test_non_owner_cannot_delete_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(
        email="delete-owner@example.com",
        password="Password1"
    )
    non_owner = authenticated_user_factory(
        email="delete-non-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Delete Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        non_owner["user"]["email"],
        role
    )

    response = test_client.delete(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404

    get_response = test_client.get(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Protected Delete Project"
