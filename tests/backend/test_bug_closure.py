import pytest


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
