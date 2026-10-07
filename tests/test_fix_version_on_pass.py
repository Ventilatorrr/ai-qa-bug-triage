import pytest


@pytest.fixture
def lifecycle_bug(test_client, authenticated_user_factory, project_factory, member_factory):
    owner = authenticated_user_factory(email="version-owner@example.com")
    developer = authenticated_user_factory(email="version-developer@example.com")
    qa = authenticated_user_factory(email="version-qa@example.com")
    project = project_factory(owner["token"])
    for actor, role in [(developer, "Developer"), (qa, "QA Analyst")]:
        member_factory(owner["token"], project["id"], actor["user"]["email"], role)
    actors = {"owner": owner, "developer": developer, "qa": qa}

    def create(state="Testing", fix_version=None):
        headers = {"Authorization": f"Bearer {owner['token']}"}
        response = test_client.post(
            f"/projects/{project['id']}/bugs", headers=headers,
            json={"title": "Bug for version transition", "assignee_id": developer["user_id"],
                  "affected_version": "0.1.0", "fix_version": fix_version},
        )
        assert response.status_code == 201
        number = response.json()["bug_number"]
        url = f"/projects/{project['id']}/bugs/{response.json()['bug_number']}"
        for payload in [
            {"status": "Open"},
            {"status": "Development"},
            {"status": "Testing", "assignee_id": qa["user_id"]},
            {"status": "Closed", "testing_outcome": "Passed"},
        ]:
            if response.json()["status"] == state:
                break
            response = test_client.patch(f"{url}/status", headers=headers, json=payload)
            assert response.status_code == 200
            assert response.json()["bug_number"] == number
        assert response.json()["status"] == state
        return url, response.json(), actors

    return create


@pytest.mark.parametrize("actor,current_version,version_payload,expected", [
    pytest.param("qa", None, {"fix_version": "1.3.0"}, "1.3.0", id="qa-supplied"),
    pytest.param("owner", None, {"fix_version": "1.3.0"}, "1.3.0", id="owner-supplied"),
    pytest.param("qa", None, {"fix_version": None}, None, id="blank"),
    pytest.param("qa", "1.2.0", {"fix_version": None}, None, id="clear-existing"),
    pytest.param("qa", "1.2.0", {"fix_version": "1.2.0"}, "1.2.0", id="unchanged"),
    pytest.param("qa", "1.2.0", {"fix_version": "1.3.0"}, "1.3.0", id="replace-existing"),
    pytest.param("qa", "1.2.0", {}, "1.2.0", id="omitted-preserves"),
    pytest.param("qa", None, {}, None, id="omitted-blank"),
    pytest.param("qa", None, {"fix_version": " 1.3.0 "}, " 1.3.0 ", id="no-trimming"),
    pytest.param("qa", None, {"fix_version": " \t "}, " \t ", id="whitespace-unchanged"),
    pytest.param("qa", "1.2.0", {"fix_version": ""}, "", id="api-empty-string"),
])
def test_passed_transition_persists_optional_fix_version(
    test_client, lifecycle_bug, actor, current_version, version_payload, expected,
):
    url, before, actors = lifecycle_bug(fix_version=current_version)
    headers = {"Authorization": f"Bearer {actors[actor]['token']}"}
    response = test_client.patch(
        f"{url}/status", headers=headers,
        json={"status": "Closed", "testing_outcome": "Passed"} | version_payload,
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "Closed"
    assert result["bug_number"] == before["bug_number"]
    assert result["resolution"] == "Fixed"
    assert result["fix_version"] == expected
    assert result["assignee_id"] == actors["qa"]["user_id"]
    assert result["affected_version"] == before["affected_version"]
    assert result["created_at"] == before["created_at"]
    assert result["updated_at"] != before["updated_at"]
    stored = test_client.get(url, headers=headers)
    assert stored.status_code == 200
    assert stored.json() == result


def test_failed_transition_preserves_fix_version(test_client, lifecycle_bug):
    url, before, actors = lifecycle_bug(fix_version="1.2.0")
    headers = {"Authorization": f"Bearer {actors['qa']['token']}"}
    response = test_client.patch(
        f"{url}/status", headers=headers,
        json={"status": "Development", "testing_outcome": "Failed",
              "assignee_id": actors["developer"]["user_id"]},
    )
    assert response.status_code == 200
    result = response.json()
    assert result["status"] == "Development"
    assert result["bug_number"] == before["bug_number"]
    assert result["resolution"] is None
    assert result["assignee_id"] == actors["developer"]["user_id"]
    assert result["fix_version"] == before["fix_version"]
    assert result["updated_at"] != before["updated_at"]
    stored = test_client.get(url, headers=headers)
    assert stored.status_code == 200
    assert stored.json() == result


@pytest.mark.parametrize("state,payload,fix_version", [
    ("Triage", {"status": "Open"}, "2.0.0"),
    ("Open", {"status": "Development"}, None),
    ("Development", {"status": "Testing", "assignee_id": "qa"}, "2.0.0"),
    ("Development", {"status": "Closed", "resolution": "Duplicate"}, "2.0.0"),
    ("Testing", {"status": "Development", "testing_outcome": "Failed", "assignee_id": "developer"}, "2.0.0"),
    ("Closed", {"status": "Triage"}, None),
])
def test_fix_version_is_rejected_outside_passed_transition(
    test_client, lifecycle_bug, state, payload, fix_version,
):
    url, before, actors = lifecycle_bug(state, fix_version="1.2.0")
    payload = payload.copy()
    if "assignee_id" in payload:
        payload["assignee_id"] = actors[payload["assignee_id"]]["user_id"]
    headers = {"Authorization": f"Bearer {actors['owner']['token']}"}
    response = test_client.patch(
        f"{url}/status", headers=headers, json=payload | {"fix_version": fix_version},
    )
    assert response.status_code == 422
    assert response.json() == {"detail": "Fix Version can only be set when testing is Passed."}
    stored = test_client.get(url, headers=headers)
    assert stored.status_code == 200
    assert stored.json() == before


@pytest.mark.parametrize("actor,expected_status", [("developer", 403), ("non_member", 404)])
def test_passed_fix_version_preserves_authorization(
    test_client, lifecycle_bug, authenticated_user_factory, actor, expected_status,
):
    url, before, actors = lifecycle_bug()
    if actor == "non_member":
        actors[actor] = authenticated_user_factory(email="version-outsider@example.com")
    response = test_client.patch(
        f"{url}/status", headers={"Authorization": f"Bearer {actors[actor]['token']}"},
        json={"status": "Closed", "testing_outcome": "Passed", "fix_version": "1.3.0"},
    )
    assert response.status_code == expected_status
    stored = test_client.get(url, headers={"Authorization": f"Bearer {actors['owner']['token']}"})
    assert stored.status_code == 200
    assert stored.json() == before
