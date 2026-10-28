import pytest


BUG_TEXT_LIMITS = [
    ("title", "Title", 255),
    ("affected_version", "Affected Version", 50),
    ("environment", "Environment", 5000),
    ("description", "Description", 5000),
    ("steps_to_reproduce", "Steps to Reproduce", 5000),
    ("expected_result", "Expected Result", 5000),
    ("actual_result", "Actual Result", 5000),
]


@pytest.fixture
def owner_project(authenticated_user_factory, project_factory):
    owner = authenticated_user_factory(email="limits-owner@example.com")
    project = project_factory(owner["token"], name="Limits Project")
    return {
        "base": f"/projects/{project['id']}",
        "headers": {"Authorization": f"Bearer {owner['token']}"},
    }


# TC-478 | AC-011.5, AC-013.2 — Bug text over its limit is rejected on create and edit, naming the field; values at the limit are saved
@pytest.mark.parametrize("field,label,limit", BUG_TEXT_LIMITS)
@pytest.mark.parametrize("operation", ["create", "edit"])
def test_bug_text_length_limits(test_client, owner_project, operation, field, label, limit):
    base, headers = owner_project["base"], owner_project["headers"]
    if operation == "edit":
        created = test_client.post(f"{base}/bugs", headers=headers, json={"title": "Original title"})
        assert created.status_code == 201
        url = f"{base}/bugs/{created.json()['bug_number']}"
        before = created.json()

        def send(value):
            return test_client.patch(url, headers=headers, json={field: value})
    else:
        def send(value):
            return test_client.post(f"{base}/bugs", headers=headers, json={"title": "Limit title", field: value})

    response = send("x" * (limit + 1))
    assert response.status_code == 422
    assert f"{label} must be {limit:,} characters or fewer." in response.json()["detail"][0]["msg"]
    bugs = test_client.get(f"{base}/bugs", headers=headers).json()
    if operation == "edit":
        assert test_client.get(url, headers=headers).json() == before  # Nothing was saved.
    else:
        assert bugs == []

    response = send("x" * limit)
    assert response.status_code in (200, 201)
    assert response.json()[field] == "x" * limit


# TC-480 | AC-005.2, AC-007.3 — Project names over 255 characters are rejected on create and edit; 255 is accepted
def test_project_name_length_limit(test_client, owner_project):
    headers = owner_project["headers"]
    message = {"detail": "Project name must be 255 characters or fewer."}

    response = test_client.post("/projects", headers=headers, json={"name": "p" * 256})
    assert response.status_code == 422
    assert response.json() == message
    assert [project["name"] for project in test_client.get("/projects", headers=headers).json()] == ["Limits Project"]

    response = test_client.put(owner_project["base"], headers=headers, json={"name": "p" * 256})
    assert response.status_code == 422
    assert response.json() == message
    assert test_client.get(owner_project["base"], headers=headers).json()["name"] == "Limits Project"

    for method, url in [("POST", "/projects"), ("PUT", owner_project["base"])]:
        response = test_client.request(method, url, headers=headers, json={"name": "p" * 255})
        assert response.status_code in (200, 201)
        assert response.json()["name"] == "p" * 255
