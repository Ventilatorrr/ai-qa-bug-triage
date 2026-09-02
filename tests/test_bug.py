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
            "steps_to_reproduce": "1. Open the login page. 2. Enter valid credentials. 3. Click Login.",
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
        "1. Open the login page. 2. Enter valid credentials. 3. Click Login."
    )
    assert data["expected_result"] == "The user should be logged in."
    assert data["actual_result"] == "Nothing happens after clicking Login."
    assert data["severity"] == "Blocker"
    assert data["priority"] == "High"
    assert data["assignee_id"] == developer_member["user_id"]
    assert data["fix_version"] == "1.3.0"
