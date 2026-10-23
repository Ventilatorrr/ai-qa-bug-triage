import pytest


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
