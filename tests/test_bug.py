import pytest


# AC-011.1 — Successful Bug Creation
def test_project_member_can_create_bug(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="bug-creator@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Bug Creation Project"
    )

    response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Login button does not work"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["project_id"] == project["id"]
    assert data["title"] == "Login button does not work"
    assert data["status"] == "Triage"
    assert data["created_by"] == user["user_id"]
    assert data["created_at"] is not None
    assert data["updated_at"] is not None

    bug_id = data["id"]

    view_response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_id}",
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert view_response.status_code == 200

    viewed_bug = view_response.json()

    assert viewed_bug["id"] == bug_id
    assert viewed_bug["project_id"] == project["id"]
    assert viewed_bug["title"] == "Login button does not work"
    assert viewed_bug["status"] == "Triage"
    assert viewed_bug["created_by"] == user["user_id"]


# AC-011.2 — Missing Bug Title
def test_bug_creation_rejected_without_title(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="missing-title@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Missing Title Project"
    )

    response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": ""
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["body", "title"]
    assert "Bug title is required." in response.json()["detail"][0]["msg"]


# AC-011.3 — Unauthorized Bug Creation
def test_non_member_cannot_create_bug(
    test_client,
    authenticated_user_factory,
    project_factory
):
    owner = authenticated_user_factory(
        email="bug-owner@example.com",
        password="Password1"
    )

    non_member = authenticated_user_factory(
        email="bug-non-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Bug Project"
    )

    response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Unauthorized bug"
        },
        headers={
            "Authorization": f"Bearer {non_member['token']}"
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found."
    }


# AC-011.4 — Optional Bug Information
def test_bug_can_be_created_with_optional_information(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="optional-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="optional-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Optional Bug Information Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Login button does not work",
            "affected_version": "1.2.0",
            "environment": "Windows 11, Chrome 152, Desktop",
            "description": "Clicking the login button has no effect.",
            "steps_to_reproduce": (
                "1. Open the login page. "
                "2. Enter valid credentials. "
                "3. Click Login."
            ),
            "expected_result": "The user should be logged in.",
            "actual_result": "Nothing happens after clicking Login.",
            "severity": "Blocker",
            "priority": "High",
            "assignee_id": developer_member["user_id"],
            "fix_version": "1.3.0"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Login button does not work"
    assert data["affected_version"] == "1.2.0"
    assert data["environment"] == "Windows 11, Chrome 152, Desktop"
    assert data["description"] == "Clicking the login button has no effect."
    assert data["steps_to_reproduce"] == (
        "1. Open the login page. "
        "2. Enter valid credentials. "
        "3. Click Login."
    )
    assert data["expected_result"] == "The user should be logged in."
    assert data["actual_result"] == "Nothing happens after clicking Login."
    assert data["severity"] == "Blocker"
    assert data["priority"] == "High"
    assert data["assignee_id"] == developer_member["user_id"]
    assert data["fix_version"] == "1.3.0"



# AC-012.1 — View Bug List
def test_project_member_can_view_bug_list(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="bug-list-user@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Bug List Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Login button does not work",
            "severity": "Blocker",
            "priority": "High"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert create_response.status_code == 201

    response = test_client.get(
        f"/projects/{project['id']}/bugs",
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert response.status_code == 200

    bugs = response.json()

    assert len(bugs) == 1

    assert bugs[0]["id"] == create_response.json()["id"]
    assert bugs[0]["title"] == "Login button does not work"
    assert bugs[0]["severity"] == "Blocker"
    assert bugs[0]["priority"] == "High"
    assert bugs[0]["status"] == "Triage"
    assert bugs[0]["assignee_id"] is None
    assert bugs[0]["updated_at"] is not None


# AC-012.2 — Open Bug Report
def test_project_member_can_open_bug_report(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="bug-detail-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="bug-detail-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Bug Detail Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Login button does not work",
            "affected_version": "1.2.0",
            "environment": "Windows 11, Chrome 152, Desktop",
            "description": "Clicking the login button has no effect.",
            "steps_to_reproduce": (
                "1. Open login page. "
                "2. Enter credentials. "
                "3. Click Login."
            ),
            "expected_result": "The user should be logged in.",
            "actual_result": "Nothing happens.",
            "severity": "Blocker",
            "priority": "High",
            "assignee_id": developer_member["user_id"],
            "fix_version": "1.3.0"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_id}",
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == bug_id
    assert data["project_id"] == project["id"]
    assert data["title"] == "Login button does not work"
    assert data["severity"] == "Blocker"
    assert data["priority"] == "High"
    assert data["status"] == "Triage"
    assert data["assignee_id"] == developer_member["user_id"]
    assert data["affected_version"] == "1.2.0"
    assert data["fix_version"] == "1.3.0"
    assert data["environment"] == "Windows 11, Chrome 152, Desktop"
    assert data["description"] == "Clicking the login button has no effect."
    assert data["steps_to_reproduce"] == (
        "1. Open login page. "
        "2. Enter credentials. "
        "3. Click Login."
    )
    assert data["expected_result"] == "The user should be logged in."
    assert data["actual_result"] == "Nothing happens."
    assert data["created_by"] == owner["user_id"]
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


# AC-012.3 — Unauthorized Bug Access
def test_non_member_cannot_open_bug_report(
    test_client,
    authenticated_user_factory,
    project_factory
):
    owner = authenticated_user_factory(
        email="bug-access-owner@example.com",
        password="Password1"
    )

    non_member = authenticated_user_factory(
        email="bug-access-non-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Bug Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Protected bug"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_id}",
        headers={
            "Authorization": f"Bearer {non_member['token']}"
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found."
    }


# AC-012.4 — Sort Bug Reports
def test_bug_list_defaults_to_most_recently_updated_first(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="bug-sort-user@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Bug Sort Project"
    )

    first_bug_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "First bug"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert first_bug_response.status_code == 201
    first_bug_id = first_bug_response.json()["id"]

    second_bug_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Second bug"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert second_bug_response.status_code == 201
    second_bug_id = second_bug_response.json()["id"]

    response = test_client.get(
        f"/projects/{project['id']}/bugs",
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert response.status_code == 200

    bugs = response.json()

    assert len(bugs) == 2
    assert bugs[0]["id"] == second_bug_id
    assert bugs[0]["title"] == "Second bug"
    assert bugs[1]["id"] == first_bug_id
    assert bugs[1]["title"] == "First bug"

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{first_bug_id}",
        json={
            "description": "Updated first bug"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert update_response.status_code == 200

    response = test_client.get(
        f"/projects/{project['id']}/bugs",
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert response.status_code == 200

    bugs = response.json()

    assert len(bugs) == 2
    assert bugs[0]["id"] == first_bug_id
    assert bugs[0]["title"] == "First bug"
    assert bugs[1]["id"] == second_bug_id
    assert bugs[1]["title"] == "Second bug"


# AC-013.1 — Edit Bug Report
def test_project_member_can_edit_bug_report(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="bug-editor@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Bug Editing Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Login button does not work",
            "description": "Original description."
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "title": "Login button still does not work",
            "description": "Updated description."
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["id"] == bug_id
    assert data["title"] == "Login button still does not work"
    assert data["description"] == "Updated description."
    assert data["status"] == "Triage"
    assert data["updated_at"] != original_updated_at


# AC-013.2 — Optional Bug Information
def test_project_member_can_update_optional_bug_information(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="optional-editor@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Optional Bug Editing Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Login button does not work"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "affected_version": "1.2.0",
            "environment": "macOS Sonoma, Safari",
            "severity": "Blocker",
            "priority": "High",
            "fix_version": "1.3.0"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["affected_version"] == "1.2.0"
    assert data["environment"] == "macOS Sonoma, Safari"
    assert data["severity"] == "Blocker"
    assert data["priority"] == "High"
    assert data["fix_version"] == "1.3.0"


# AC-013.3 — Unauthorized Bug Editing
def test_non_member_cannot_edit_bug_report(
    test_client,
    authenticated_user_factory,
    project_factory
):
    owner = authenticated_user_factory(
        email="edit-owner@example.com",
        password="Password1"
    )

    non_member = authenticated_user_factory(
        email="edit-non-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Bug Editing Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Protected bug"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "title": "Unauthorized change"
        },
        headers={
            "Authorization": f"Bearer {non_member['token']}"
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found."
    }


# AC-014.1 — Successful Bug Deletion
@pytest.mark.parametrize("role", ["Project Owner", "QA Analyst"])
def test_authorized_member_can_delete_bug(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(
        email=f"delete-owner-{role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Bug Deletion {role} Project"
    )

    actor = owner

    if role == "QA Analyst":
        qa = authenticated_user_factory(
            email="delete-qa@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            qa["user"]["email"],
            "QA Analyst"
        )

        actor = qa

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug to delete"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    delete_response = test_client.delete(
        f"/projects/{project['id']}/bugs/{bug_id}",
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert delete_response.status_code == 204

    get_response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_id}",
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Bug not found."
    }


# AC-014.2 — Unauthorized Bug Deletion
@pytest.mark.parametrize("role", ["Developer", "non-member"])
def test_unauthorized_member_cannot_delete_bug(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    role
):
    owner = authenticated_user_factory(
        email="delete-security-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Bug Deletion Project"
    )

    actor = authenticated_user_factory(
        email=f"delete-{role.lower()}@example.com",
        password="Password1"
    )

    if role == "Developer":
        member_factory(
            owner["token"],
            project["id"],
            actor["user"]["email"],
            "Developer"
        )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Protected bug"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    delete_response = test_client.delete(
        f"/projects/{project['id']}/bugs/{bug_id}",
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    if role == "Developer":
        assert delete_response.status_code == 403
        assert delete_response.json() == {
            "detail": "You are not authorized to delete bugs."
        }
    else:
        assert delete_response.status_code == 404
        assert delete_response.json() == {
            "detail": "Project not found."
        }


# AC-015.1 — Assign and Unassign Bugs
@pytest.mark.parametrize(
    "actor_role, assignee_role",
    [
        ("Project Owner", "QA Analyst"),
        ("Project Owner", "Developer"),
        ("QA Analyst", "QA Analyst"),
        ("QA Analyst", "Developer"),
        ("Developer", "QA Analyst"),
        ("Developer", "Developer"),
    ]
)
def test_authorized_member_can_assign_bug(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor_role,
    assignee_role
):

    owner = authenticated_user_factory(
        email=f"assign-owner-{actor_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Bug Assignment {actor_role} Project"
    )

    actor = owner

    if actor_role == "QA Analyst":
        qa = authenticated_user_factory(
            email="assign-qa@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            qa["user"]["email"],
            "QA Analyst"
        )

        actor = qa

    elif actor_role == "Developer":
        developer = authenticated_user_factory(
            email="assign-developer@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            developer["user"]["email"],
            "Developer"
        )

        actor = developer

    assignee = authenticated_user_factory(
        email=f"assignee-{assignee_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    assignee_member = member_factory(
        owner["token"],
        project["id"],
        assignee["user"]["email"],
        assignee_role
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug to assign"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "assignee_id": assignee_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["assignee_id"] == assignee_member["user_id"]
    assert data["updated_at"] != original_updated_at


# AC-015.1 — Assign and Unassign Bugs
@pytest.mark.parametrize(
    "actor_role",
    ["Project Owner", "QA Analyst", "Developer"]
)
def test_authorized_member_can_unassign_bug(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor_role
):

    owner = authenticated_user_factory(
        email=f"unassign-owner-{actor_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Bug Unassignment {actor_role} Project"
    )

    actor = owner

    if actor_role == "QA Analyst":
        qa = authenticated_user_factory(
            email="unassign-qa@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            qa["user"]["email"],
            "QA Analyst"
        )

        actor = qa

    elif actor_role == "Developer":
        developer = authenticated_user_factory(
            email="unassign-developer@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            developer["user"]["email"],
            "Developer"
        )

        actor = developer

    assignee = authenticated_user_factory(
        email=f"unassign-assignee-{actor_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    assignee_member = member_factory(
        owner["token"],
        project["id"],
        assignee["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug to unassign",
            "assignee_id": assignee_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "assignee_id": None
        },
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["assignee_id"] is None
    assert data["updated_at"] != original_updated_at


# AC-015.2 — Invalid Assignment
@pytest.mark.parametrize("assignee_type", ["Project Owner", "non-member"])
def test_bug_cannot_be_assigned_to_invalid_member(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    assignee_type
):

    owner = authenticated_user_factory(
        email=f"invalid-assignee-owner-{assignee_type.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Invalid Bug Assignee {assignee_type} Project"
    )

    if assignee_type == "Project Owner":

        assignee_id = owner["user_id"]

    else:

        non_member = authenticated_user_factory(
            email="invalid-assignee-non-member@example.com",
            password="Password1"
        )

        assignee_id = non_member["user_id"]

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug with invalid assignee"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "assignee_id": assignee_id
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert update_response.status_code == 422

    assert update_response.json() == {
        "detail": "Invalid bug assignee."
    }


# AC-015.3 — Unauthorized Bug Assignment
def test_non_member_cannot_assign_bug(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):

    owner = authenticated_user_factory(
        email="assign-security-owner@example.com",
        password="Password1"
    )

    non_member = authenticated_user_factory(
        email="assign-non-member@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="assign-target-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Bug Assignment Project"
    )

    target_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Protected assignment bug"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "assignee_id": target_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {non_member['token']}"
        }
    )

    assert update_response.status_code == 404

    assert update_response.json() == {
        "detail": "Project not found."
    }


# AC-015.4 — Change Bug Assignee
def test_authorized_member_can_reassign_bug(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):

    owner = authenticated_user_factory(
        email="reassign-owner@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="reassign-qa@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="reassign-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Bug Reassignment Project"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug to reassign",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["assignee_id"] == developer_member["user_id"]
    assert data["updated_at"] != original_updated_at


# AC-016.1 — Set Bug Severity
@pytest.mark.parametrize(
    "actor_role",
    ["Project Owner", "QA Analyst", "Developer"]
)
@pytest.mark.parametrize(
    "severity",
    ["Blocker", "Critical", "Major", "Minor"]
)
def test_project_member_can_set_bug_severity(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor_role,
    severity
):

    owner = authenticated_user_factory(
        email=f"severity-owner-{actor_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Bug Severity {actor_role} Project"
    )

    actor = owner

    if actor_role == "QA Analyst":
        qa = authenticated_user_factory(
            email="severity-qa@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            qa["user"]["email"],
            "QA Analyst"
        )

        actor = qa

    elif actor_role == "Developer":
        developer = authenticated_user_factory(
            email="severity-developer@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            developer["user"]["email"],
            "Developer"
        )

        actor = developer

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug to classify"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "severity": severity
        },
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["severity"] == severity


# AC-016.2 — Set Bug Priority
@pytest.mark.parametrize(
    "actor_role",
    ["Project Owner", "QA Analyst", "Developer"]
)
@pytest.mark.parametrize(
    "priority",
    ["Urgent", "High", "Medium", "Low"]
)
def test_project_member_can_set_bug_priority(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor_role,
    priority
):

    owner = authenticated_user_factory(
        email=f"priority-owner-{actor_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Bug Priority {actor_role} Project"
    )

    actor = owner

    if actor_role == "QA Analyst":
        qa = authenticated_user_factory(
            email="priority-qa@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            qa["user"]["email"],
            "QA Analyst"
        )

        actor = qa

    elif actor_role == "Developer":
        developer = authenticated_user_factory(
            email="priority-developer@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            developer["user"]["email"],
            "Developer"
        )

        actor = developer

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug to prioritize"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "priority": priority
        },
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["priority"] == priority


# AC-016.3 — Update Bug Classification
@pytest.mark.parametrize(
    "actor_role",
    ["Project Owner", "QA Analyst", "Developer"]
)
def test_project_member_can_update_bug_classification(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor_role
):

    owner = authenticated_user_factory(
        email=f"classification-owner-{actor_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Bug Classification {actor_role} Project"
    )

    actor = owner

    if actor_role == "QA Analyst":
        qa = authenticated_user_factory(
            email="classification-qa@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            qa["user"]["email"],
            "QA Analyst"
        )

        actor = qa

    elif actor_role == "Developer":
        developer = authenticated_user_factory(
            email="classification-developer@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            developer["user"]["email"],
            "Developer"
        )

        actor = developer

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug to update classification",
            "severity": "Minor",
            "priority": "Low"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "severity": "Blocker",
            "priority": "High"
        },
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["severity"] == "Blocker"
    assert data["priority"] == "High"
    assert data["updated_at"] != original_updated_at


# AC-016.4 — Unauthorized Bug Classification
def test_non_member_cannot_update_bug_classification(
    test_client,
    authenticated_user_factory,
    project_factory
):

    owner = authenticated_user_factory(
        email="classification-security-owner@example.com",
        password="Password1"
    )

    non_member = authenticated_user_factory(
        email="classification-security-non-member@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Bug Classification Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Protected classification bug"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "severity": "Blocker",
            "priority": "High"
        },
        headers={
            "Authorization": f"Bearer {non_member['token']}"
        }
    )

    assert update_response.status_code == 404

    assert update_response.json() == {
        "detail": "Project not found."
    }


# Additional Validation Test
@pytest.mark.parametrize(
    "severity",
    ["High", "Urgent", "Invalid"]
)
def test_bug_rejects_invalid_severity(
    test_client,
    authenticated_user_factory,
    project_factory,
    severity
):

    user = authenticated_user_factory(
        email=f"invalid-severity-{severity.lower()}@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name=f"Invalid Severity {severity} Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug with invalid severity"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "severity": severity
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert update_response.status_code == 422

    detail = update_response.json()["detail"]

    assert detail[0]["loc"] == ["body", "severity"]
    assert "Invalid severity." in detail[0]["msg"]


# Additional Validation Test
@pytest.mark.parametrize(
    "priority",
    ["Critical", "Blocker", "Invalid"]
)
def test_bug_rejects_invalid_priority(
    test_client,
    authenticated_user_factory,
    project_factory,
    priority
):

    user = authenticated_user_factory(
        email=f"invalid-priority-{priority.lower()}@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name=f"Invalid Priority {priority} Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug with invalid priority"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}",
        json={
            "priority": priority
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert update_response.status_code == 422

    detail = update_response.json()["detail"]

    assert detail[0]["loc"] == ["body", "priority"]
    assert "Invalid priority." in detail[0]["msg"]


# AC-017.1 — Bug Status
def test_new_bug_starts_in_triage(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="status-user@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Bug Status Project"
    )

    response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "New lifecycle bug"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["status"] == "Triage"
    assert data["resolution"] is None


# AC-017.2 — Triage to Open
@pytest.mark.parametrize(
    "actor_role",
    ["Project Owner", "QA Analyst"]
)
def test_project_owner_or_qa_can_move_bug_from_triage_to_open(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor_role
):
    owner = authenticated_user_factory(
        email=f"triage-owner-{actor_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Triage to Open {actor_role} Project"
    )

    actor = owner

    if actor_role == "QA Analyst":
        qa = authenticated_user_factory(
            email="triage-qa@example.com",
            password="Password1"
        )

        member_factory(
            owner["token"],
            project["id"],
            qa["user"]["email"],
            "QA Analyst"
        )

        actor = qa

    developer = authenticated_user_factory(
        email="triage-developer@example.com",
        password="Password1"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug ready for triage",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["status"] == "Open"
    assert data["assignee_id"] == developer_member["user_id"]


# AC-017.2 — Triage to Open
def test_developer_cannot_move_bug_from_triage_to_open(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="triage-security-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="triage-security-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Triage Project"
    )

    member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Developer cannot move this bug"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert update_response.status_code == 403

    assert update_response.json() == {
        "detail": "You are not authorized to move bugs from Triage to Open."
    }


# AC-017.2 — Triage to Open
def test_bug_without_assignee_cannot_move_from_triage_to_open(
    test_client,
    authenticated_user_factory,
    project_factory
):
    owner = authenticated_user_factory(
        email="triage-no-assignee-owner@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Triage No Assignee Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug without assignee"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert update_response.status_code == 422

    assert update_response.json() == {
        "detail": "Bug must have a QA Analyst or Developer assigned before it can be moved to Open."
    }


# AC-017.3 — Open to Development
def test_qa_analyst_cannot_move_bug_from_open_to_development(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="development-security-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="development-security-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="development-security-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Open to Development Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "QA cannot move this bug",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert development_response.status_code == 403

    assert development_response.json() == {
        "detail": "Only the assigned Developer or Project Owner can move a bug from Open to Development."
    }


# AC-017.3 — Open to Development
def test_project_owner_can_move_bug_from_open_to_development(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="owner-development-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="owner-development-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Owner Open to Development Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Owner moves bug to development",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert development_response.status_code == 200

    data = development_response.json()

    assert data["status"] == "Development"
    assert data["assignee_id"] == developer_member["user_id"]


# AC-017.3 — Open to Development
def test_non_assigned_developer_cannot_move_bug_from_open_to_development(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="development-owner-2@example.com",
        password="Password1"
    )

    assigned_developer = authenticated_user_factory(
        email="assigned-developer@example.com",
        password="Password1"
    )

    other_developer = authenticated_user_factory(
        email="other-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Assigned Developer Project"
    )

    assigned_developer_member = member_factory(
        owner["token"],
        project["id"],
        assigned_developer["user"]["email"],
        "Developer"
    )

    member_factory(
        owner["token"],
        project["id"],
        other_developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Only assigned developer can move this bug",
            "assignee_id": assigned_developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {other_developer['token']}"
        }
    )

    assert development_response.status_code == 403

    assert development_response.json() == {
        "detail": "Only the assigned Developer or Project Owner can move a bug from Open to Development."
    }


# AC-017.4 — Development to Testing
def test_assigned_developer_can_move_bug_from_development_to_testing(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="testing-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="testing-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="testing-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Development to Testing Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug ready for testing",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200
    assert development_response.json()["status"] == "Development"

    original_updated_at = development_response.json()["updated_at"]

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    data = testing_response.json()

    assert data["status"] == "Testing"
    assert data["assignee_id"] == qa_member["user_id"]
    assert data["updated_at"] != original_updated_at


# AC-017.4 — Development to Testing
def test_project_owner_can_move_bug_from_development_to_testing(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="owner-testing-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="owner-testing-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="owner-testing-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Owner Development to Testing Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Owner moves bug to testing",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Open"},
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert testing_response.status_code == 200

    data = testing_response.json()

    assert data["status"] == "Testing"
    assert data["assignee_id"] == qa_member["user_id"]


# AC-017.4 — Development to Testing
def test_non_assigned_developer_cannot_move_bug_from_development_to_testing(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="testing-security-owner@example.com",
        password="Password1"
    )

    assigned_developer = authenticated_user_factory(
        email="testing-assigned-developer@example.com",
        password="Password1"
    )

    other_developer = authenticated_user_factory(
        email="testing-other-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="testing-security-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Development to Testing Project"
    )

    assigned_developer_member = member_factory(
        owner["token"],
        project["id"],
        assigned_developer["user"]["email"],
        "Developer"
    )

    member_factory(
        owner["token"],
        project["id"],
        other_developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Only assigned developer can send to testing",
            "assignee_id": assigned_developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {assigned_developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {other_developer['token']}"
        }
    )

    assert testing_response.status_code == 403

    assert testing_response.json() == {
        "detail": "Only the assigned Developer or Project Owner can move a bug from Development to Testing."
    }


# AC-017.4 — Development to Testing
def test_bug_cannot_move_to_testing_with_developer_assignee(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="testing-validation-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="testing-validation-developer@example.com",
        password="Password1"
    )

    other_developer = authenticated_user_factory(
        email="testing-validation-other-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Testing Assignee Validation Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    other_developer_member = member_factory(
        owner["token"],
        project["id"],
        other_developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Testing must have QA assignee",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": other_developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 422

    assert testing_response.json() == {
        "detail": "Invalid QA Analyst assignee."
    }


# AC-017.5 — Testing Outcome
def test_assigned_qa_can_pass_bug_and_close_it(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="outcome-pass-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="outcome-pass-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="outcome-pass-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Testing Outcome Pass Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug that passes testing",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Open"},
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200
    assert testing_response.json()["status"] == "Testing"
    assert testing_response.json()["assignee_id"] == qa_member["user_id"]

    original_updated_at = testing_response.json()["updated_at"]

    pass_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed",
            "testing_outcome": "Passed"
        },
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert pass_response.status_code == 200

    data = pass_response.json()

    assert data["status"] == "Closed"
    assert data["testing_outcome"] == "Passed" if "testing_outcome" in data else True
    assert data["resolution"] == "Fixed"
    assert data["assignee_id"] == qa_member["user_id"]
    assert data["updated_at"] != original_updated_at


# AC-017.5 — Testing Outcome
def test_project_owner_can_pass_bug_and_close_it(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="owner-pass-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="owner-pass-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="owner-pass-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Owner Testing Pass Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Owner passes bug",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    bug_id = create_response.json()["id"]

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Development"},
        headers={"Authorization": f"Bearer {developer['token']}"}
    ).status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    pass_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed",
            "testing_outcome": "Passed"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert pass_response.status_code == 200

    data = pass_response.json()

    assert data["status"] == "Closed"
    assert data["resolution"] == "Fixed"
    assert data["assignee_id"] == qa_member["user_id"]


# AC-017.5 — Testing Outcome
def test_assigned_qa_can_fail_bug_and_return_it_to_development(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="outcome-fail-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="outcome-fail-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="outcome-fail-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Testing Outcome Fail Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug that fails testing",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Open"},
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    original_updated_at = testing_response.json()["updated_at"]

    fail_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development",
            "testing_outcome": "Failed",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert fail_response.status_code == 200

    data = fail_response.json()

    assert data["status"] == "Development"
    assert data["assignee_id"] == developer_member["user_id"]
    assert data["resolution"] is None
    assert data["updated_at"] != original_updated_at


# AC-017.5 — Testing Outcome
def test_project_owner_can_fail_bug_and_return_it_to_development(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="owner-fail-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="owner-fail-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="owner-fail-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Owner Testing Fail Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Owner fails bug",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    bug_id = create_response.json()["id"]

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Development"},
        headers={"Authorization": f"Bearer {developer['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    ).status_code == 200

    fail_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development",
            "testing_outcome": "Failed",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert fail_response.status_code == 200

    data = fail_response.json()

    assert data["status"] == "Development"
    assert data["resolution"] is None
    assert data["assignee_id"] == developer_member["user_id"]


# AC-017.5 — Testing Outcome
def test_non_assigned_qa_cannot_record_testing_outcome(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="outcome-security-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="outcome-security-developer@example.com",
        password="Password1"
    )

    assigned_qa = authenticated_user_factory(
        email="outcome-security-assigned-qa@example.com",
        password="Password1"
    )

    other_qa = authenticated_user_factory(
        email="outcome-security-other-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Protected Testing Outcome Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    assigned_qa_member = member_factory(
        owner["token"],
        project["id"],
        assigned_qa["user"]["email"],
        "QA Analyst"
    )

    member_factory(
        owner["token"],
        project["id"],
        other_qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Only assigned QA can test",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Open"},
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": assigned_qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    outcome_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed",
            "testing_outcome": "Passed"
        },
        headers={
            "Authorization": f"Bearer {other_qa['token']}"
        }
    )

    assert outcome_response.status_code == 403

    assert outcome_response.json() == {
        "detail": "Only the assigned QA Analyst or Project Owner can record the testing outcome."
    }


# AC-017.5 — Testing Outcome
@pytest.mark.parametrize(
    "status",
    ["Closed", "Development"]
)
def test_testing_outcome_is_required(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    status
):
    owner = authenticated_user_factory(
        email=f"outcome-required-owner-{status.lower()}@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email=f"outcome-required-developer-{status.lower()}@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email=f"outcome-required-qa-{status.lower()}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Testing Outcome Required {status} Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Testing outcome is required",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    payload = {
        "status": status
    }

    if status == "Development":
        payload["assignee_id"] = developer_member["user_id"]

    outcome_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json=payload,
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert outcome_response.status_code == 422

    assert outcome_response.json() == {
        "detail": "Testing outcome is required."
    }


# AC-017.5 — Testing Outcome
def test_invalid_testing_outcome_is_rejected(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="outcome-invalid-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="outcome-invalid-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="outcome-invalid-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Testing Outcome Invalid Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Invalid testing outcome",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    outcome_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed",
            "testing_outcome": "Invalid"
        },
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert outcome_response.status_code == 422

    detail = outcome_response.json()["detail"]

    assert detail[0]["loc"] == ["body", "testing_outcome"]
    assert "Input should be 'Passed' or 'Failed'" in detail[0]["msg"]


# AC-017.6 — Close Without Fixing
@pytest.mark.parametrize(
    "resolution",
    ["Won't Fix", "Duplicate", "Cannot Reproduce", "Not a Bug"]
)
def test_assigned_developer_can_close_bug_without_fixing(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    resolution
):
    owner = authenticated_user_factory(
        email=f"close-developer-owner-{resolution.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email=f"close-developer-{resolution.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Developer Close {resolution} Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug to close without fixing",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    original_updated_at = development_response.json()["updated_at"]

    close_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed",
            "resolution": resolution
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert close_response.status_code == 200

    data = close_response.json()

    assert data["status"] == "Closed"
    assert data["resolution"] == resolution
    assert data["assignee_id"] == developer_member["user_id"]
    assert data["updated_at"] != original_updated_at


# AC-017.6 — Close Without Fixing
@pytest.mark.parametrize(
    "resolution",
    ["Won't Fix", "Duplicate", "Cannot Reproduce", "Not a Bug"]
)
def test_project_owner_can_close_bug_without_fixing(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    resolution
):
    owner = authenticated_user_factory(
        email=f"close-owner-{resolution.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email=f"close-owner-developer-{resolution.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name=f"Owner Close {resolution} Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug for owner closure",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    original_updated_at = development_response.json()["updated_at"]

    close_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed",
            "resolution": resolution
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert close_response.status_code == 200

    data = close_response.json()

    assert data["status"] == "Closed"
    assert data["resolution"] == resolution
    assert data["assignee_id"] == developer_member["user_id"]
    assert data["updated_at"] != original_updated_at


# AC-017.6 — Close Without Fixing
def test_bug_cannot_be_closed_without_resolution(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="close-required-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="close-required-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Resolution Required Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Resolution is required",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    close_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert close_response.status_code == 422

    assert close_response.json() == {
        "detail": "Resolution is required when closing a bug without fixing it."
    }


# AC-017.6 — Close Without Fixing
def test_fixed_resolution_cannot_be_manually_selected_when_closing_bug(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="close-fixed-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="close-fixed-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Fixed Resolution Validation Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Fixed cannot be manually selected",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    close_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed",
            "resolution": "Fixed"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert close_response.status_code == 422

    detail = close_response.json()["detail"]

    assert detail[0]["loc"] == ["body", "resolution"]
    assert "Input should be" in detail[0]["msg"]
    assert "Won't Fix" in detail[0]["msg"]
    assert "Duplicate" in detail[0]["msg"]
    assert "Cannot Reproduce" in detail[0]["msg"]
    assert "Not a Bug" in detail[0]["msg"]


# AC-017.7 — Closed Bugs
def test_closed_bug_cannot_be_moved_to_another_status(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="closed-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="closed-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="closed-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Closed Bug Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Closed bug cannot reopen",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    close_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Closed",
            "testing_outcome": "Passed"
        },
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert close_response.status_code == 200
    assert close_response.json()["status"] == "Closed"
    assert close_response.json()["resolution"] == "Fixed"

    reopen_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert reopen_response.status_code == 422

    assert reopen_response.json() == {
        "detail": "Closed bugs cannot be moved to another status."
    }


# AC-017.8 — Invalid Status Transitions
def test_bug_cannot_skip_from_triage_to_development(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="invalid-transition-triage-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="invalid-transition-triage-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Invalid Triage Transition Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Cannot skip Open",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "Invalid bug status transition."
    }


# AC-017.8 — Invalid Status Transitions
def test_bug_cannot_skip_from_open_to_testing(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="invalid-transition-open-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="invalid-transition-open-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="invalid-transition-open-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Invalid Open Transition Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Cannot skip Development",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "Invalid bug status transition."
    }


# AC-017.8 — Invalid Status Transitions
def test_bug_cannot_move_from_development_back_to_open(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="invalid-transition-development-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="invalid-transition-development-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Invalid Development Transition Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Cannot move backwards",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "Invalid bug status transition."
    }


# AC-017.8 — Invalid Status Transitions
def test_bug_cannot_move_from_testing_back_to_open(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="invalid-transition-testing-open-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="invalid-transition-testing-open-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="invalid-transition-testing-open-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Invalid Testing to Open Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Testing cannot return to Open",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "Invalid bug status transition."
    }


# AC-017.8 — Invalid Status Transitions
def test_bug_cannot_move_from_testing_back_to_triage(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="invalid-transition-testing-triage-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="invalid-transition-testing-triage-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="invalid-transition-testing-triage-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Invalid Testing to Triage Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Testing cannot return to Triage",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert testing_response.status_code == 200

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Triage"
        },
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "Invalid bug status transition."
    }


# AC-017.9 — Status Update Timestamp
def test_changing_bug_status_updates_last_updated_timestamp(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="timestamp-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="timestamp-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Status Timestamp Project"
    )

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Status timestamp bug",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    original_updated_at = create_response.json()["updated_at"]

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_id}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Open"
    assert data["updated_at"] != original_updated_at
