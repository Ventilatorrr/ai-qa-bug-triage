import pytest


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
