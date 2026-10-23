import pytest


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
