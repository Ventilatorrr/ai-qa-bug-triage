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
