import pytest


# TC-066 | AC-011.1 — Project member can create bug
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
    bug_number = data["bug_number"]

    view_response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# TC-067 | AC-011.2 — Bug creation rejected without title
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


# TC-068 | AC-011.3 — Non member cannot create bug
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


# TC-069 | AC-011.4 — Bug can be created with optional information
@pytest.mark.parametrize("severity", ["Blocker", "Major", "Moderate", "Minor"])
def test_bug_can_be_created_with_optional_information(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    severity
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
            "severity": severity,
            "priority": "High",
            "assignee_id": developer_member["user_id"]
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
    assert data["severity"] == severity
    assert data["priority"] == "High"
    assert data["assignee_id"] == developer_member["user_id"]
    assert data["fix_version"] is None



# TC-070 | AC-012.1 — Project member can view bug list
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
    assert bugs[0]["resolution"] is None
    assert bugs[0]["assignee_id"] is None
    assert bugs[0]["updated_at"] is not None


# TC-071 | AC-012.2 — Project member can open bug report
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
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    bug_number = create_response.json()["bug_number"]

    qa = authenticated_user_factory(email="bug-detail-qa@example.com")
    member_factory(owner["token"], project["id"], qa["user"]["email"], "QA Analyst")
    for payload in [
        {"status": "Open"},
        {"status": "Development"},
        {"status": "Testing", "assignee_id": qa["user_id"]},
        {"status": "Closed", "testing_outcome": "Passed", "fix_version": "1.3.0"},
    ]:
        transition = test_client.patch(
            f"/projects/{project['id']}/bugs/{bug_number}/status",
            headers={"Authorization": f"Bearer {owner['token']}"}, json=payload,
        )
        assert transition.status_code == 200

    response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
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
    assert data["status"] == "Closed"
    assert data["resolution"] == "Fixed"
    assert data["assignee_id"] == qa["user_id"]
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


# TC-072 | AC-012.3 — Non member cannot open bug report
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
    bug_number = create_response.json()["bug_number"]

    response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={
            "Authorization": f"Bearer {non_member['token']}"
        }
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Project not found."
    }


# TC-073 | AC-012.3 — Non member cannot retrieve another projects bug collection
def test_non_member_cannot_retrieve_another_projects_bug_collection(
    test_client, authenticated_user_factory, project_factory
):
    owner = authenticated_user_factory(email="collection-owner@example.com")
    outsider = authenticated_user_factory(email="collection-outsider@example.com")
    private_project = project_factory(owner["token"], name="Private fictional project")
    own_project = project_factory(outsider["token"], name="Outsider's own project")
    owner_headers = {"Authorization": f"Bearer {owner['token']}"}
    outsider_headers = {"Authorization": f"Bearer {outsider['token']}"}
    created = []
    for project, headers, title in [
        (private_project, owner_headers, "Private synthetic report"),
        (own_project, outsider_headers, "Accessible synthetic report"),
    ]:
        response = test_client.post(
            f"/projects/{project['id']}/bugs", json={"title": title}, headers=headers
        )
        assert response.status_code == 201
        created.append(response.json())

    denied = test_client.get(
        f"/projects/{private_project['id']}/bugs", headers=outsider_headers
    )
    accessible = test_client.get(
        f"/projects/{own_project['id']}/bugs", headers=outsider_headers
    )
    private = test_client.get(
        f"/projects/{private_project['id']}/bugs", headers=owner_headers
    )

    assert denied.status_code == 404
    assert denied.json() == {"detail": "Project not found."}
    assert accessible.status_code == private.status_code == 200
    assert [bug["id"] for bug in accessible.json()] == [created[1]["id"]]
    assert [bug["id"] for bug in private.json()] == [created[0]["id"]]
    assert created[0]["bug_number"] == created[1]["bug_number"] == 1


# TC-074 | AC-012.4 — Bug list defaults to most recently updated first
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
        f"/projects/{project['id']}/bugs/{first_bug_response.json()['bug_number']}",
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


# TC-075 | AC-013.1 — Project member can edit bug report
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
    bug_number = create_response.json()["bug_number"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# Additional validation regression — Null title during bug editing
# TC-076 | Technical — Bug update rejected with null title
def test_bug_update_rejected_with_null_title(
    test_client,
    authenticated_user_factory,
    project_factory
):
    user = authenticated_user_factory(
        email="null-title-editor@example.com",
        password="Password1"
    )

    project = project_factory(
        user["token"],
        name="Null Title Bug Editing Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Original bug title",
            "description": "Original description."
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert create_response.status_code == 201

    original_bug = create_response.json()
    bug_id = original_bug["id"]
    bug_number = original_bug["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
        json={
            "title": None
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert update_response.status_code == 422

    detail = update_response.json()["detail"]

    assert detail[0]["loc"] == ["body", "title"]
    assert "Bug title is required." in detail[0]["msg"]

    get_response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert get_response.status_code == 200
    assert get_response.json() == original_bug


# TC-077 | AC-013.2 — Project member can update optional bug information
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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
        json={
            "affected_version": "1.2.0",
            "environment": "macOS Sonoma, Safari",
            "steps_to_reproduce": "1. Open the page.\n2. Select Login.",
            "expected_result": "The account dashboard is displayed.",
            "actual_result": "The login page remains visible.",
            "severity": "Blocker",
            "priority": "High"
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["affected_version"] == "1.2.0"
    assert data["environment"] == "macOS Sonoma, Safari"
    assert data["steps_to_reproduce"] == "1. Open the page.\n2. Select Login."
    assert data["expected_result"] == "The account dashboard is displayed."
    assert data["actual_result"] == "The login page remains visible."
    assert data["severity"] == "Blocker"
    assert data["priority"] == "High"
    assert data["fix_version"] is None

    url = f"/projects/{project['id']}/bugs/{bug_number}"
    headers = {"Authorization": f"Bearer {user['token']}"}
    stored = test_client.get(url, headers=headers)
    assert stored.status_code == 200
    assert stored.json() == data

    revised = {
        "steps_to_reproduce": "1. Reload the page.\n2. Retry Login using Enter.",
        "expected_result": "The dashboard opens after keyboard submission.",
        "actual_result": "An error appears after keyboard submission.",
    }
    response = test_client.patch(url, json=revised, headers=headers)
    readback = test_client.get(url, headers=headers)

    assert response.status_code == readback.status_code == 200
    assert readback.json() == response.json()
    for field, value in revised.items():
        assert readback.json()[field] == value
    for field in ["title", "environment", "affected_version", "severity", "priority", "created_at"]:
        assert readback.json()[field] == data[field]


# TC-078 | AC-013.3 — Non member cannot edit bug report
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
    bug_number = create_response.json()["bug_number"]

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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

    stored = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={"Authorization": f"Bearer {owner['token']}"}
    )
    assert stored.status_code == 200
    assert stored.json() == create_response.json()


# TC-079 | AC-014.1 — Authorized member can delete bug
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
    bug_number = create_response.json()["bug_number"]

    delete_response = test_client.delete(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert delete_response.status_code == 204

    get_response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={
            "Authorization": f"Bearer {actor['token']}"
        }
    )

    assert get_response.status_code == 404
    assert get_response.json() == {
        "detail": "Bug not found."
    }


# TC-080, TC-081 | AC-014.2 — Unauthorized member cannot delete bug
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
    bug_number = create_response.json()["bug_number"]

    delete_response = test_client.delete(
        f"/projects/{project['id']}/bugs/{bug_number}",
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

    stored = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={"Authorization": f"Bearer {owner['token']}"}
    )
    assert stored.status_code == 200
    assert stored.json() == create_response.json()


# TC-082 | AC-015.1 — Authorized member can assign bug
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
    bug_number = create_response.json()["bug_number"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# TC-083 | AC-015.1 — Authorized member can unassign bug
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
    bug_number = create_response.json()["bug_number"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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

    stored = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={"Authorization": f"Bearer {owner['token']}"}
    )
    assert stored.status_code == 200
    assert stored.json() == data


# TC-084 | AC-015.1 — Bug unassignment is rejected outside triage
@pytest.mark.parametrize("actor_role", ["Project Owner", "QA Analyst", "Developer"])
@pytest.mark.parametrize("state,detail", [
    ("Open", "Open bugs must have an assignee."),
    ("Development", "Development bugs must have a Developer assigned."),
    ("Testing", "Testing bugs must have a QA Analyst assigned."),
    ("Closed", "Closed bugs cannot be reassigned."),
])
def test_bug_unassignment_is_rejected_outside_triage(
    test_client, authenticated_user_factory, project_factory, member_factory,
    actor_role, state, detail,
):
    owner = authenticated_user_factory(email="state-owner@example.com")
    developer = authenticated_user_factory(email="state-developer@example.com")
    qa = authenticated_user_factory(email="state-qa@example.com")
    project = project_factory(owner["token"])
    for user, role in [(developer, "Developer"), (qa, "QA Analyst")]:
        member_factory(owner["token"], project["id"], user["user"]["email"], role)
    owner_headers = {"Authorization": f"Bearer {owner['token']}"}
    created = test_client.post(
        f"/projects/{project['id']}/bugs", headers=owner_headers,
        json={"title": "Lifecycle unassignment", "assignee_id": developer["user_id"]},
    )
    assert created.status_code == 201
    url = f"/projects/{project['id']}/bugs/{created.json()['bug_number']}"
    transitions = [{"status": "Open"}]
    if state != "Open":
        transitions.append({"status": "Development"})
    if state in ("Testing", "Closed"):
        transitions.append({"status": "Testing", "assignee_id": qa["user_id"]})
    if state == "Closed":
        transitions.append({"status": "Closed", "testing_outcome": "Passed"})
    for payload in transitions:
        transition = test_client.patch(url + "/status", json=payload, headers=owner_headers)
        assert transition.status_code == 200
    before = test_client.get(url, headers=owner_headers)
    assert before.status_code == 200
    assert before.json()["status"] == state
    actor = {"Project Owner": owner, "QA Analyst": qa, "Developer": developer}[actor_role]

    response = test_client.patch(
        url, json={"assignee_id": None},
        headers={"Authorization": f"Bearer {actor['token']}"},
    )
    stored = test_client.get(url, headers=owner_headers)

    assert response.status_code == 422
    assert response.json() == {"detail": detail}
    assert stored.status_code == 200
    assert stored.json() == before.json()


# TC-085 | AC-015.2 — Bug cannot be assigned to invalid member
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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# TC-086 | AC-015.1, AC-015.3 — Non member cannot assign bug
@pytest.mark.parametrize("unassign", [False, True], ids=["assign", "unassign"])
def test_non_member_cannot_assign_bug(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    unassign,
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
            "title": "Protected assignment bug",
            "assignee_id": target_member["user_id"] if unassign else None,
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
        json={
            "assignee_id": None if unassign else target_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {non_member['token']}"
        }
    )

    assert update_response.status_code == 404

    assert update_response.json() == {
        "detail": "Project not found."
    }

    stored = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={"Authorization": f"Bearer {owner['token']}"},
    )
    assert stored.status_code == 200
    assert stored.json() == create_response.json()


# TC-087 | AC-015.4 — Authorized member can reassign bug
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
    bug_number = create_response.json()["bug_number"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# TC-088 | AC-016.1 — Project member can set bug severity
@pytest.mark.parametrize(
    "actor_role",
    ["Project Owner", "QA Analyst", "Developer"]
)
@pytest.mark.parametrize(
    "severity",
    ["Blocker", "Major", "Moderate", "Minor"]
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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# TC-089 | AC-016.2 — Project member can set bug priority
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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# TC-090 | AC-016.3 — Project member can update bug classification
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
    bug_number = create_response.json()["bug_number"]
    original_updated_at = create_response.json()["updated_at"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# TC-091 | AC-016.4 — Non member cannot update bug classification
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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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
# TC-092 | Technical — Bug rejects invalid severity
@pytest.mark.parametrize(
    "severity",
    ["High", "Urgent", "Invalid", "Critical"]
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

    invalid_create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Bug with invalid severity",
            "severity": severity
        },
        headers={
            "Authorization": f"Bearer {user['token']}"
        }
    )

    assert invalid_create_response.status_code == 422
    create_detail = invalid_create_response.json()["detail"]
    assert create_detail[0]["loc"] == ["body", "severity"]
    assert "Invalid severity." in create_detail[0]["msg"]

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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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
# TC-093 | Technical — Bug rejects invalid priority
@pytest.mark.parametrize(
    "priority",
    ["Moderate", "Blocker", "Invalid"]
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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}",
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


# TC-094 | AC-017.1 — New bug starts in triage
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


# TC-095 | AC-017.2 — Project owner or QA can move bug from triage to open
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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-096 | AC-017.2 — Triage to open can assign eligible project member
@pytest.mark.parametrize("assignee_role", ["QA Analyst", "Developer"])
def test_triage_to_open_can_assign_eligible_project_member(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    assignee_role
):
    owner = authenticated_user_factory(
        email=f"triage-selected-{assignee_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )
    assignee = authenticated_user_factory(
        email=f"selected-{assignee_role.lower().replace(' ', '-')}@example.com",
        password="Password1"
    )
    project = project_factory(
        owner["token"],
        name=f"Triage Selected {assignee_role} Project"
    )
    member = member_factory(
        owner["token"],
        project["id"],
        assignee["user"]["email"],
        assignee_role
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={"title": f"Assign {assignee_role} while opening"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert create_response.status_code == 201

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{create_response.json()['bug_number']}/status",
        json={
            "status": "Open",
            "assignee_id": member["user_id"]
        },
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Open"
    assert update_response.json()["assignee_id"] == member["user_id"]


# TC-097 | AC-017.2 — Triage to open rejects ineligible assignee
@pytest.mark.parametrize("invalid_assignee", ["project_owner", "non_member"])
def test_triage_to_open_rejects_ineligible_assignee(
    test_client,
    authenticated_user_factory,
    project_factory,
    invalid_assignee
):
    owner = authenticated_user_factory(
        email=f"triage-invalid-{invalid_assignee}-owner@example.com",
        password="Password1"
    )
    outsider = authenticated_user_factory(
        email=f"triage-invalid-{invalid_assignee}-outsider@example.com",
        password="Password1"
    )
    project = project_factory(
        owner["token"],
        name=f"Triage Invalid {invalid_assignee} Project"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={"title": "Reject invalid assignee while opening"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert create_response.status_code == 201

    assignee_id = (
        owner["user_id"]
        if invalid_assignee == "project_owner"
        else outsider["user_id"]
    )
    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{create_response.json()['bug_number']}/status",
        json={
            "status": "Open",
            "assignee_id": assignee_id
        },
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert update_response.status_code == 422
    assert update_response.json() == {
        "detail": "Bug must have a QA Analyst or Developer assigned before it can be moved to Open."
    }


# TC-098 | AC-017.2 — Developer cannot move bug from triage to open
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

    developer_member = member_factory(
        owner["token"],
        project["id"],
        developer["user"]["email"],
        "Developer"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Developer cannot move this bug",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    assert create_response.json()["status"] == "Triage"
    assert create_response.json()["assignee_id"] == developer_member["user_id"]

    bug_id = create_response.json()["id"]
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-099 | AC-017.2 — Bug without assignee cannot move from triage to open
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
    bug_number = create_response.json()["bug_number"]

    update_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-100 | AC-017.3 — QA analyst cannot move bug from open to development
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-101 | AC-017.3 — Project owner can move bug from open to development
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

    qa = authenticated_user_factory(
        email="owner-development-qa@example.com",
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

    qa_member = member_factory(
        owner["token"],
        project["id"],
        qa["user"]["email"],
        "QA Analyst"
    )

    create_response = test_client.post(
        f"/projects/{project['id']}/bugs",
        json={
            "title": "Owner moves bug to development",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert development_response.status_code == 200

    data = development_response.json()

    assert data["status"] == "Development"
    assert data["assignee_id"] == developer_member["user_id"]


# TC-102 | AC-017.3 — Open to development requires valid developer assignee
@pytest.mark.parametrize("selected_assignee", ["missing", "qa_analyst"])
def test_open_to_development_requires_valid_developer_assignee(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    selected_assignee
):
    owner = authenticated_user_factory(
        email=f"development-invalid-{selected_assignee}-owner@example.com",
        password="Password1"
    )
    qa = authenticated_user_factory(
        email=f"development-invalid-{selected_assignee}-qa@example.com",
        password="Password1"
    )
    project = project_factory(
        owner["token"],
        name=f"Development Invalid {selected_assignee} Project"
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
            "title": "Require Developer while starting development",
            "assignee_id": qa_member["user_id"]
        },
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    bug_number = create_response.json()["bug_number"]
    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert open_response.status_code == 200

    payload = {"status": "Development"}

    if selected_assignee == "qa_analyst":
        payload["assignee_id"] = qa_member["user_id"]

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json=payload,
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert development_response.status_code == 422
    assert development_response.json() == {
        "detail": "A Developer must be assigned before the bug can be moved to Development."
    }


# TC-103 | AC-017.3 — Non assigned developer cannot move bug from open to development
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-104 | AC-017.4 — Assigned developer can move bug from development to testing
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-105 | AC-017.4 — Project owner can move bug from development to testing
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-106 | AC-017.4 — Non assigned developer cannot move bug from development to testing
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {assigned_developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-107 | AC-017.4 — Bug cannot move to testing with developer assignee
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-108 | AC-017.5 — Assigned QA can pass bug and close it
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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

    # Passed is a transition input; the resulting state is Closed with resolution Fixed.
    assert data["status"] == "Closed"
    assert data["resolution"] == "Fixed"
    assert data["assignee_id"] == qa_member["user_id"]
    assert data["updated_at"] != original_updated_at

    get_response = test_client.get(
        f"/projects/{project['id']}/bugs/{bug_number}",
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert get_response.status_code == 200
    stored_bug = get_response.json()
    assert stored_bug["status"] == "Closed"
    assert stored_bug["resolution"] == "Fixed"
    assert stored_bug["assignee_id"] == qa_member["user_id"]
    assert stored_bug["updated_at"] == data["updated_at"]

    list_response = test_client.get(
        f"/projects/{project['id']}/bugs",
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert list_response.status_code == 200
    assert list_response.json()[0]["status"] == "Closed"
    assert list_response.json()[0]["resolution"] == "Fixed"


# TC-109 | AC-017.5 — Project owner can pass bug and close it
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
    bug_number = create_response.json()["bug_number"]

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Development"},
        headers={"Authorization": f"Bearer {developer['token']}"}
    ).status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-110 | AC-017.5 — Assigned QA can fail bug and return it to development
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-111 | AC-017.5 — Project owner can fail bug and return it to development
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
    bug_number = create_response.json()["bug_number"]

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Development"},
        headers={"Authorization": f"Bearer {developer['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    ).status_code == 200

    fail_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-112 | AC-017.5 — Failed testing requires valid developer assignee
@pytest.mark.parametrize(
    ("failed_update", "expected_detail"),
    [
        (
            {
                "status": "Development",
                "testing_outcome": "Failed"
            },
            "A Developer must be assigned when testing fails."
        ),
        (
            {
                "status": "Development",
                "testing_outcome": "Failed",
                "assignee_id": "qa"
            },
            "Invalid Developer assignee."
        )
    ]
)
def test_failed_testing_requires_valid_developer_assignee(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    failed_update,
    expected_detail
):
    owner = authenticated_user_factory(
        email="failed-assignee-owner@example.com",
        password="Password1"
    )

    developer = authenticated_user_factory(
        email="failed-assignee-developer@example.com",
        password="Password1"
    )

    qa = authenticated_user_factory(
        email="failed-assignee-qa@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Failed Testing Assignee Validation Project"
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
            "title": "Failed testing needs a Developer",
            "assignee_id": qa_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    bug_id = create_response.json()["id"]
    bug_number = create_response.json()["bug_number"]

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development",
            "assignee_id": developer_member["user_id"]
        },
        headers={"Authorization": f"Bearer {owner['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Testing",
            "assignee_id": qa_member["user_id"]
        },
        headers={"Authorization": f"Bearer {developer['token']}"}
    ).status_code == 200

    request_data = dict(failed_update)

    if request_data.get("assignee_id") == "qa":
        request_data["assignee_id"] = qa_member["user_id"]

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json=request_data,
        headers={"Authorization": f"Bearer {owner['token']}"}
    )

    assert response.status_code == 422
    assert response.json() == {"detail": expected_detail}


# TC-113 | AC-017.5 — Non assigned QA cannot record testing outcome
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-114 | AC-017.5 — Testing outcome is required
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json=payload,
        headers={
            "Authorization": f"Bearer {qa['token']}"
        }
    )

    assert outcome_response.status_code == 422

    assert outcome_response.json() == {
        "detail": "Testing outcome is required."
    }


# TC-115 | AC-017.5 — Invalid testing outcome is rejected
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-116 | AC-017.6 — Assigned developer can close bug without fixing
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-117 | AC-017.6 — Project owner can close bug without fixing
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-118 | AC-017.6 — Non assigned developer cannot close bug without fixing
def test_non_assigned_developer_cannot_close_bug_without_fixing(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    owner = authenticated_user_factory(
        email="close-non-assigned-owner@example.com",
        password="Password1"
    )

    assigned_developer = authenticated_user_factory(
        email="close-assigned-developer@example.com",
        password="Password1"
    )

    other_developer = authenticated_user_factory(
        email="close-other-developer@example.com",
        password="Password1"
    )

    project = project_factory(
        owner["token"],
        name="Non-assigned Developer Close Project"
    )

    assigned_member = member_factory(
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
            "title": "Bug another Developer cannot close",
            "assignee_id": assigned_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201
    bug_id = create_response.json()["id"]
    bug_number = create_response.json()["bug_number"]

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Open"},
        headers={"Authorization": f"Bearer {owner['token']}"}
    ).status_code == 200

    assert test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={"status": "Development"},
        headers={
            "Authorization": f"Bearer {assigned_developer['token']}"
        }
    ).status_code == 200

    close_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Closed",
            "resolution": "Duplicate"
        },
        headers={
            "Authorization": f"Bearer {other_developer['token']}"
        }
    )

    assert close_response.status_code == 403
    assert close_response.json() == {
        "detail": "Only the assigned Developer can close this bug."
    }


# TC-119 | AC-017.6 — Bug cannot be closed without resolution
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    close_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-120 | AC-017.6 — Fixed resolution cannot be manually selected when closing bug
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    close_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


def _create_closed_bug_for_lifecycle_test(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    resolution,
    remove_assignee=False
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
            "title": "Closed bug returns to triage",
            "assignee_id": developer_member["user_id"]
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert create_response.status_code == 201

    bug_id = create_response.json()["id"]
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    if resolution == "Fixed":
        testing_response = test_client.patch(
            f"/projects/{project['id']}/bugs/{bug_number}/status",
            json={
                "status": "Testing",
                "assignee_id": qa_member["user_id"]
            },
            headers={
                "Authorization": f"Bearer {owner['token']}"
            }
        )

        assert testing_response.status_code == 200

        close_response = test_client.patch(
            f"/projects/{project['id']}/bugs/{bug_number}/status",
            json={
                "status": "Closed",
                "testing_outcome": "Passed"
            },
            headers={
                "Authorization": f"Bearer {owner['token']}"
            }
        )
        expected_assignee_id = qa_member["user_id"]
    else:
        close_response = test_client.patch(
            f"/projects/{project['id']}/bugs/{bug_number}/status",
            json={
                "status": "Closed",
                "resolution": resolution
            },
            headers={
                "Authorization": f"Bearer {owner['token']}"
            }
        )
        expected_assignee_id = developer_member["user_id"]

    assert close_response.status_code == 200
    assert close_response.json()["status"] == "Closed"
    assert close_response.json()["resolution"] == resolution

    closed_bug = close_response.json()

    if remove_assignee:
        remove_response = test_client.delete(
            f"/projects/{project['id']}/members/{expected_assignee_id}",
            headers={"Authorization": f"Bearer {owner['token']}"}
        )

        assert remove_response.status_code == 200

        closed_bug_response = test_client.get(
            f"/projects/{project['id']}/bugs/{bug_number}",
            headers={"Authorization": f"Bearer {owner['token']}"}
        )

        assert closed_bug_response.status_code == 200
        closed_bug = closed_bug_response.json()
        assert closed_bug["assignee_id"] is None
        assert closed_bug["resolution"] == resolution
        expected_assignee_id = None

    return {
        "owner": owner,
        "developer": developer,
        "qa": qa,
        "project_id": project["id"],
        "bug_number": bug_number,
        "assignee_id": expected_assignee_id,
        "closed_bug": closed_bug
    }


# TC-121 | AC-017.7 — Project owner can move closed bug to triage
@pytest.mark.parametrize("resolution", ["Fixed", "Duplicate"])
def test_project_owner_can_move_closed_bug_to_triage(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    resolution
):
    setup = _create_closed_bug_for_lifecycle_test(
        test_client,
        authenticated_user_factory,
        project_factory,
        member_factory,
        resolution
    )

    response = test_client.patch(
        f"/projects/{setup['project_id']}/bugs/{setup['bug_number']}/status",
        json={
            "status": "Triage"
        },
        headers={
            "Authorization": f"Bearer {setup['owner']['token']}"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "Triage"
    assert data["resolution"] is None
    assert data["assignee_id"] == setup["assignee_id"]
    assert data["updated_at"] != setup["closed_bug"]["updated_at"]


# TC-122 | AC-017.7 — Project owner can move unassigned closed bug to triage
def test_project_owner_can_move_unassigned_closed_bug_to_triage(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory
):
    setup = _create_closed_bug_for_lifecycle_test(
        test_client,
        authenticated_user_factory,
        project_factory,
        member_factory,
        "Duplicate",
        remove_assignee=True
    )

    assert setup["closed_bug"]["assignee_id"] is None

    response = test_client.patch(
        f"/projects/{setup['project_id']}/bugs/{setup['bug_number']}/status",
        json={"status": "Triage"},
        headers={"Authorization": f"Bearer {setup['owner']['token']}"}
    )

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "Triage"
    assert data["assignee_id"] is None
    assert data["resolution"] is None
    assert data["updated_at"] != setup["closed_bug"]["updated_at"]


# TC-123 | AC-017.7 — Unauthorized user cannot move closed bug to triage
@pytest.mark.parametrize(
    ("actor", "expected_status", "expected_detail"),
    [
        (
            "qa",
            403,
            "Only a Project Owner can move a bug from Closed to Triage."
        ),
        (
            "developer",
            403,
            "Only a Project Owner can move a bug from Closed to Triage."
        ),
        (
            "non_member",
            404,
            "Project not found."
        )
    ]
)
def test_unauthorized_user_cannot_move_closed_bug_to_triage(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    actor,
    expected_status,
    expected_detail
):
    setup = _create_closed_bug_for_lifecycle_test(
        test_client,
        authenticated_user_factory,
        project_factory,
        member_factory,
        "Duplicate"
    )

    if actor == "non_member":
        outsider = authenticated_user_factory(
            email="closed-outsider@example.com",
            password="Password1"
        )
        token = outsider["token"]
    else:
        token = setup[actor]["token"]

    response = test_client.patch(
        f"/projects/{setup['project_id']}/bugs/{setup['bug_number']}/status",
        json={
            "status": "Triage"
        },
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == expected_status
    assert response.json() == {
        "detail": expected_detail
    }


# TC-124 | AC-017.7 — Closed bug rejects invalid direct transition
@pytest.mark.parametrize("requested_status", ["Open", "Development", "Testing"])
def test_closed_bug_rejects_invalid_direct_transition(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    requested_status
):
    setup = _create_closed_bug_for_lifecycle_test(
        test_client,
        authenticated_user_factory,
        project_factory,
        member_factory,
        "Duplicate"
    )

    response = test_client.patch(
        f"/projects/{setup['project_id']}/bugs/{setup['bug_number']}/status",
        json={
            "status": requested_status
        },
        headers={
            "Authorization": f"Bearer {setup['owner']['token']}"
        }
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "Invalid bug status transition."
    }


# TC-125 | AC-017.7 — Closed to triage rejects extra transition data
@pytest.mark.parametrize(
    "extra_data",
    ["assignee_id", "testing_outcome", "resolution"]
)
def test_closed_to_triage_rejects_extra_transition_data(
    test_client,
    authenticated_user_factory,
    project_factory,
    member_factory,
    extra_data
):
    setup = _create_closed_bug_for_lifecycle_test(
        test_client,
        authenticated_user_factory,
        project_factory,
        member_factory,
        "Duplicate"
    )

    payload = {
        "status": "Triage"
    }

    if extra_data == "assignee_id":
        payload[extra_data] = setup["assignee_id"]
    elif extra_data == "testing_outcome":
        payload[extra_data] = "Passed"
    else:
        payload[extra_data] = "Duplicate"

    response = test_client.patch(
        f"/projects/{setup['project_id']}/bugs/{setup['bug_number']}/status",
        json=payload,
        headers={
            "Authorization": f"Bearer {setup['owner']['token']}"
        }
    )

    assert response.status_code == 422

    assert response.json() == {
        "detail": "Invalid status update data."
    }


# TC-126 | AC-017.8 — Bug cannot skip from triage to development
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
    bug_number = create_response.json()["bug_number"]

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-127 | AC-017.8 — Bug cannot skip from open to testing
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-128 | AC-017.8 — Bug cannot move from development back to open
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-129 | AC-017.8 — Bug cannot move from testing back to open
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-130 | AC-017.8 — Bug cannot move from testing back to triage
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
    bug_number = create_response.json()["bug_number"]

    open_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Open"
        },
        headers={
            "Authorization": f"Bearer {owner['token']}"
        }
    )

    assert open_response.status_code == 200

    development_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
        json={
            "status": "Development"
        },
        headers={
            "Authorization": f"Bearer {developer['token']}"
        }
    )

    assert development_response.status_code == 200

    testing_response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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


# TC-131 | AC-017.9 — Changing bug status updates last updated timestamp
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
    bug_number = create_response.json()["bug_number"]
    original_updated_at = create_response.json()["updated_at"]

    response = test_client.patch(
        f"/projects/{project['id']}/bugs/{bug_number}/status",
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
