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
def test_project_member_can_set_bug_severity(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor_role
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
            "severity": "Blocker"
        },
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["severity"] == "Blocker"


# AC-016.2 — Set Bug Priority
@pytest.mark.parametrize(
    "actor_role",
    ["Project Owner", "QA Analyst", "Developer"]
)
def test_project_member_can_set_bug_priority(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor_role
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
            "priority": "High"
        },
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["priority"] == "High"


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
    ["Critical", "High", "Invalid"]
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
    ["Critical", "Urgent", "Invalid"]
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

