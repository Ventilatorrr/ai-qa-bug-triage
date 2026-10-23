import pytest


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
