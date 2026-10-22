import pytest


# TC-184 | AC-005.1 — Create project
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


# TC-185 | AC-005.2 — Create project with empty name
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


# TC-186 | AC-005.2 — Project creation rejects whitespace only name
def test_project_creation_rejects_whitespace_only_name(
    test_client,
    authenticated_user_factory
):
    user = authenticated_user_factory(
        email="whitespace-project@example.com",
        password="Password1"
    )

    response = test_client.post(
        "/projects",
        json={
            "name": "   "
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"] == "Project name is required."


# TC-187 | AC-005.2 — Project creation rejects non string name
@pytest.mark.parametrize("name", [123, True, ["QA"], {"name": "QA"}, None])
def test_project_creation_rejects_non_string_name(
    test_client, authenticated_user_factory, name
):
    user = authenticated_user_factory()
    headers = {"Authorization": f"Bearer {user['token']}"}

    response = test_client.post("/projects", json={"name": name}, headers=headers)
    projects = test_client.get("/projects", headers=headers)

    assert projects.status_code == 200
    assert projects.json() == []
    assert response.status_code == 422
    assert response.json() == {"detail": "Project name is required."}


# TC-188 | AC-005.1 — Project creation preserves padded name
def test_project_creation_preserves_padded_name(test_client, authenticated_user_factory):
    user = authenticated_user_factory()
    headers = {"Authorization": f"Bearer {user['token']}"}
    name = "  QA Project  "

    response = test_client.post("/projects", json={"name": name}, headers=headers)

    assert response.status_code == 201
    assert response.json()["name"] == name
    stored = test_client.get(f"/projects/{response.json()['id']}", headers=headers)
    assert stored.status_code == 200
    assert stored.json()["name"] == name


# TC-189 | AC-005.3 — Unauthenticated user cannot create project
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


# TC-190 | AC-006.1 — Get projects
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


# TC-191 | AC-006.2 — User only sees own projects
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


# TC-192 | AC-006.3 — Get project
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


# TC-193 | AC-006.4 — User cannot access another users project
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


# TC-194 | AC-007.1 — Edit project name
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


# TC-195 | AC-007.3 — Project edit rejects empty or whitespace only name
@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_project_edit_rejects_empty_or_whitespace_only_name(
    test_client, authenticated_user_factory, project_factory, name
):
    user = authenticated_user_factory()
    project = project_factory(user["token"], name="Original Project")
    headers = {"Authorization": f"Bearer {user['token']}"}

    response = test_client.put(
        f"/projects/{project['id']}", json={"name": name}, headers=headers
    )
    stored = test_client.get(f"/projects/{project['id']}", headers=headers)

    assert stored.status_code == 200
    assert stored.json()["name"] == "Original Project"
    assert response.status_code == 422
    assert response.json() == {"detail": "Project name is required."}


# TC-196 | AC-007.3 — Project edit rejects non string name
@pytest.mark.parametrize("name", [123, True, ["QA"], {"name": "QA"}, None])
def test_project_edit_rejects_non_string_name(
    test_client, authenticated_user_factory, project_factory, name
):
    user = authenticated_user_factory()
    project = project_factory(user["token"], name="Original Project")
    headers = {"Authorization": f"Bearer {user['token']}"}

    response = test_client.put(
        f"/projects/{project['id']}", json={"name": name}, headers=headers
    )
    stored = test_client.get(f"/projects/{project['id']}", headers=headers)

    assert stored.status_code == 200
    assert stored.json()["name"] == "Original Project"
    assert response.status_code == 422
    assert response.json() == {"detail": "Project name is required."}


# TC-197 | AC-007.1 — Project edit preserves padded name
def test_project_edit_preserves_padded_name(
    test_client, authenticated_user_factory, project_factory
):
    user = authenticated_user_factory()
    project = project_factory(user["token"], name="Original Project")
    headers = {"Authorization": f"Bearer {user['token']}"}
    name = "  Updated Project  "

    response = test_client.put(
        f"/projects/{project['id']}", json={"name": name}, headers=headers
    )

    assert response.status_code == 200
    assert response.json()["name"] == name
    stored = test_client.get(f"/projects/{project['id']}", headers=headers)
    assert stored.status_code == 200
    assert stored.json()["name"] == name


# TC-198 | AC-007.2 — User cannot edit another users project name
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


# TC-199 | AC-008.1 — Delete project
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


# TC-200 | AC-008.1 — New project owner cannot access bugs from deleted project
def test_new_project_owner_cannot_access_bugs_from_deleted_project(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user1 = authenticated_user_factory(
        email="deleted-project-owner@example.com",
        password="Password1"
    )
    user2 = authenticated_user_factory(
        email="new-project-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        user1["token"],
        name="Project To Delete"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug from deleted project"
        },
        headers={
            "Authorization": f"Bearer {user1['token']}"
        }
    )

    assert create_response.status_code == 201

    delete_response = test_client.delete(
        f"/projects/{project['id']}",
        headers={
            "Authorization": f"Bearer {user1['token']}"
        }
    )

    assert delete_response.status_code == 200

    new_project = project_factory(
        user2["token"],
        name="New Owner Project"
    )

    assert new_project["id"] == project["id"]

    response = test_client.get(
        f"/projects/{new_project['id']}/bugs",
        headers={
            "Authorization": f"Bearer {user2['token']}"
        }
    )

    assert response.status_code == 200
    assert response.json() == []


# TC-201 | AC-008.2 — User cannot delete another users project
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


# TC-202 | AC-009.1 — Owner can add project member
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


# TC-203 | AC-009.1 — Added member can access project
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


# TC-204 | AC-009.2 — Owner can remove project member
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


# TC-205 | AC-009.2, AC-015.1 — Removing member unassigns only their bugs in that project
@pytest.mark.parametrize("role", ["QA Analyst", "Developer"])
def test_removing_member_unassigns_only_their_bugs_in_that_project(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(email="remove-assigned-owner@example.com")
    member = authenticated_user_factory(email="remove-assigned-member@example.com")
    other_member = authenticated_user_factory(email="remaining-member@example.com")
    project = project_factory(owner["token"], name="Member Removal Project")
    other_project = project_factory(owner["token"], name="Other Project")

    for member_project in [project, other_project]:
        member_factory(
            owner["token"],
            member_project["id"],
            member["user"]["email"],
            role
        )

    member_factory(
        owner["token"],
        project["id"],
        other_member["user"]["email"],
        role
    )

    bugs = []
    for bug_project, assignee in [
        (project, member),
        (project, member),
        (project, other_member),
        (other_project, member)
    ]:
        response = test_client.post(
            f"/projects/{bug_project['id']}/bugs",
            json={
                "title": "Assigned bug before member removal",
                "assignee_id": assignee["user_id"],
                "severity": "Major",
                "priority": "High"
            },
            headers={"Authorization": f"Bearer {owner['token']}"}
        )

        assert response.status_code == 201
        assert response.json()["assignee_id"] == assignee["user_id"]
        bugs.append(response.json())

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bugs[0]['bug_number']}/status",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Open"
    bugs[0] = response.json()

    response = test_client.delete(
        f"/projects/{project['id']}/members/{member['user_id']}",
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Project member removed successfully."}

    for bug in bugs:
        response = test_client.get(
            f"/projects/{bug['project_id']}/bugs/{bug['bug_number']}",
            headers={"Authorization": f"Bearer {owner['token']}"}
        )

        assert response.status_code == 200
        expected_bug = bug.copy()
        if bug["project_id"] == project["id"] and bug["assignee_id"] == member["user_id"]:
            assert response.json()["updated_at"] != bug["updated_at"]
            expected_bug["assignee_id"] = None
            expected_bug["updated_at"] = response.json()["updated_at"]

        assert response.json()["status"] == bug["status"]
        assert response.json() == expected_bug


    # Automatic removal may leave Open unassigned; ordinary edits still cannot.
    url = f"/projects/{project['id']}/bugs/{bugs[0]['bug_number']}"
    owner_headers = {"Authorization": f"Bearer {owner['token']}"}
    before = test_client.get(url, headers=owner_headers)
    assert before.status_code == 200
    assert before.json()["status"] == "Open"
    assert before.json()["assignee_id"] is None

    rejected = test_client.patch(url, json={"assignee_id": None}, headers=owner_headers)
    stored = test_client.get(url, headers=owner_headers)

    assert rejected.status_code == 422
    assert rejected.json() == {"detail": "Open bugs must have an assignee."}
    assert stored.status_code == 200
    assert stored.json() == before.json()


# TC-206 | AC-009.2 — Removed member can no longer access project
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


# TC-207 | AC-009.3 — Project owner cannot add user who does not have an account
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


# TC-208 | AC-009.4 — Project owner cannot add same user more than once
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


# TC-209 | AC-009.5 — Project member can view project members
def test_project_member_can_view_project_members(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(email="zulu-owner@example.com")
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

    # Interleave roles and reverse email order, including equal local parts.
    added = []
    for role, email in [
        ("Developer", "alpha.dev@example.net"),
        ("QA Analyst", "alpha.qa@example.net"),
        ("Developer", "alpha.dev@example.com"),
        ("QA Analyst", "alpha.qa@example.com"),
    ]:
        user = authenticated_user_factory(email=email)
        added.append(member_factory(owner["token"], project["id"], email, role))

    response = test_client.get(
        f"/projects/{project['id']}/members",
        headers={"Authorization": f"Bearer {qa_analyst['token']}"}
    )

    assert response.status_code == 200
    expected = [(owner["user"]["email"], "Project Owner")]
    for role, original in [("QA Analyst", qa_analyst), ("Developer", developer)]:
        emails = [original["user"]["email"]] + [
            member["email"] for member in added if member["role"] == role
        ]
        expected.extend((email, role) for email in sorted(emails))
    assert [(member["email"], member["role"]) for member in response.json()] == expected


# Additional security test — Project Owner Self-Removal
# TC-210 | Technical — Project owner cannot remove themselves
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


# TC-211 | AC-010.1 — Project creator is project owner
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


# TC-212 | AC-010.2 — QA analyst can access project
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


# TC-213 | AC-010.3 — Developer can access project
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


# TC-214 | AC-010.4 — Non owner cannot manage project members
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

    members_url = f"/projects/{project['id']}/members"
    owner_headers = {"Authorization": f"Bearer {owner['token']}"}
    before = test_client.get(members_url, headers=owner_headers)
    assert before.status_code == 200

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

    after_add = test_client.get(members_url, headers=owner_headers)
    assert after_add.status_code == 200
    assert after_add.json() == before.json()

    response = test_client.delete(
        f"/projects/{project['id']}/members/{existing_member_data['user_id']}",
        headers={
            "Authorization": f"Bearer {non_owner['token']}"
        }
    )

    assert response.status_code == 404

    after_remove = test_client.get(members_url, headers=owner_headers)
    assert after_remove.status_code == 200
    assert after_remove.json() == before.json()


# TC-215 | AC-010.5 — Non owner cannot edit project
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


# TC-216 | AC-010.5 — Non owner cannot delete project
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


# TC-403 | Technical — Add member rejects empty or non string email (audit B2 regression)
@pytest.mark.parametrize(
    "email",
    [
        ["qa@example.com"],
        {"email": "qa@example.com"},
        123,
        True,
        None,
        ""
    ]
)
def test_add_member_rejects_empty_or_non_string_email(
    test_client,
    authenticated_user_factory,
    project_factory,
    user_factory,
    email
):
    owner = authenticated_user_factory(
        email="malformed-email-owner@example.com",
        password="Password1"
    )
    user_factory(
        email="qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Malformed Member Email Project"
    )

    members_url = f"/projects/{project['id']}/members"
    headers = {"Authorization": f"Bearer {owner['token']}"}
    before = test_client.get(members_url, headers=headers)
    assert before.status_code == 200

    response = test_client.post(
        members_url,
        json={
            "email": email,
            "role": "Developer"
        },
        headers=headers
    )

    assert response.status_code == 422
    assert response.json() == {"detail": "Member email is required."}

    after = test_client.get(members_url, headers=headers)
    assert after.status_code == 200
    assert after.json() == before.json()


def stored_memberships(project_id, user_id):
    from contextlib import closing

    from app import database

    with closing(database.get_connection()) as connection:
        return connection.execute(
            "SELECT role FROM project_members WHERE project_id = ? AND user_id = ?",
            (project_id, user_id)
        ).fetchall()


# TC-404 | Technical — Competing add member requests return one 201 and one 409
def test_competing_add_member_requests_return_one_created_and_one_conflict(
    test_client,
    authenticated_user_factory,
    project_factory,
    monkeypatch
):
    import sqlite3

    from app import database
    from app.api import projects

    owner = authenticated_user_factory(email="race-owner@example.com")
    member = authenticated_user_factory(email="race-member@example.com")
    project = project_factory(owner["token"], name="Competing Member Project")
    members_url = f"/projects/{project['id']}/members"
    headers = {"Authorization": f"Bearer {owner['token']}"}
    competing = {}

    class CompetingConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            # The competing request passes its own duplicate check and commits
            # after this request's check, immediately before this insert.
            if "INSERT INTO project_members" in sql and not competing:
                competing["started"] = True
                competing["response"] = test_client.post(
                    members_url,
                    json={"email": member["user"]["email"], "role": "QA Analyst"},
                    headers=headers
                )
            return super().execute(sql, parameters)

    with monkeypatch.context() as patch:
        patch.setattr(
            projects,
            "get_connection",
            lambda: sqlite3.connect(database.DATABASE_NAME, factory=CompetingConnection)
        )
        response = test_client.post(
            members_url,
            json={"email": member["user"]["email"], "role": "Developer"},
            headers=headers
        )

    assert competing["response"].status_code == 201
    assert competing["response"].json()["role"] == "QA Analyst"
    assert response.status_code == 409
    assert response.json() == {"detail": "This user is already a member of this project."}
    assert stored_memberships(project["id"], member["user_id"]) == [("QA Analyst",)]

    members = test_client.get(members_url, headers=headers)
    assert members.status_code == 200
    assert [row["email"] for row in members.json()] == [
        "race-owner@example.com",
        "race-member@example.com"
    ]

    duplicate = test_client.post(
        members_url,
        json={"email": member["user"]["email"], "role": "Developer"},
        headers=headers
    )
    assert duplicate.status_code == 409


# TC-405 | Technical — Add member does not report unrelated integrity failures as conflicts
def test_add_member_does_not_report_unrelated_integrity_failure_as_conflict(
    test_client,
    authenticated_user_factory,
    project_factory,
    user_factory,
    monkeypatch
):
    import sqlite3

    from app import database
    from app.api import projects

    owner = authenticated_user_factory(email="integrity-owner@example.com")
    user_factory(email="integrity-member@example.com")
    project = project_factory(owner["token"], name="Integrity Failure Project")
    members_url = f"/projects/{project['id']}/members"
    headers = {"Authorization": f"Bearer {owner['token']}"}
    before = test_client.get(members_url, headers=headers)
    assert before.status_code == 200

    class NullRoleConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            if "INSERT INTO project_members" in sql:
                parameters = (parameters[0], parameters[1], None)
            return super().execute(sql, parameters)

    with monkeypatch.context() as patch:
        patch.setattr(
            projects,
            "get_connection",
            lambda: sqlite3.connect(database.DATABASE_NAME, factory=NullRoleConnection)
        )
        with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
            test_client.post(
                members_url,
                json={"email": "integrity-member@example.com", "role": "Developer"},
                headers=headers
            )

    after = test_client.get(members_url, headers=headers)
    assert after.status_code == 200
    assert after.json() == before.json()
