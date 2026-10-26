import pytest


@pytest.fixture
def blank_form():
    return dict.fromkeys([
        "title", "affected_version", "environment", "description",
        "steps_to_reproduce", "expected_result", "actual_result", "severity", "priority",
    ], "") | {"assignee_id": None}


def headers(user):
    return {"Authorization": f"Bearer {user['token']}"}


@pytest.fixture
def ai_project(test_client, authenticated_user_factory, project_factory, member_factory):
    owner = authenticated_user_factory(email="owner@example.com")
    developer = authenticated_user_factory(email="developer@example.com")
    project = project_factory(owner["token"])
    member_factory(owner["token"], project["id"], developer["user"]["email"], "Developer")
    base = f"/projects/{project['id']}"
    other = project_factory(owner["token"], name="Global ID offset")
    assert test_client.post(
        f"/projects/{other['id']}/bugs", headers=headers(owner), json={"title": "Other-project report"},
    ).status_code == 201
    response = test_client.post(
        f"{base}/bugs", headers=headers(developer),
        json={"title": "Stored title", "description": "Stored description",
              "assignee_id": developer["user_id"]},
    )
    assert response.status_code == 201
    assert response.json()["id"] != response.json()["bug_number"]
    return owner, developer, project, response.json(), base


@pytest.fixture
def service_calls(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    from app import ai_triage

    calls = []
    original = ai_triage.request_triage

    def record(project_id, bug_id, form):
        calls.append((project_id, bug_id, form.model_dump()))
        return original(project_id, bug_id, form)

    monkeypatch.setattr(ai_triage, "request_triage", record)
    return calls


def request_url(context, edit):
    return (f"{context[4]}/bugs/{context[3]['bug_number']}" if edit else context[4]) + "/ai-assist"


# TC-001, TC-002, TC-003 | AC-018.1, AC-022.1 — AI assist requires authorized project role
@pytest.mark.parametrize("edit", [False, True])
@pytest.mark.parametrize("role", ["Project Owner", "QA Analyst", "Developer", "non-member"])
def test_ai_assist_requires_authorized_project_role(
    test_client, ai_project, blank_form, service_calls,
    authenticated_user_factory, member_factory, role, edit,
):
    owner, developer, project, bug, base = ai_project
    if role == "Project Owner":
        actor = owner
    elif role == "Developer":
        actor = developer
    else:
        actor = authenticated_user_factory(email="actor@example.com")
        if role == "QA Analyst":
            member_factory(owner["token"], project["id"], actor["user"]["email"], role)
    response = test_client.post(request_url(ai_project, edit), headers=headers(actor), json=blank_form)
    expected = {"Project Owner": 503, "QA Analyst": 503, "Developer": 403, "non-member": 404}
    assert response.status_code == expected[role]
    if role in ("Project Owner", "QA Analyst"):
        assert actor["user_id"] not in (bug["created_by"], bug["assignee_id"])
        assert service_calls == [(project["id"], bug["id"] if edit else None, blank_form)]
        assert response.json() == {"detail": "AI assistance is not configured yet."}
    else:
        assert service_calls == []


# TC-004 | AC-018.1, AC-022.1 — AI assist requires authentication
@pytest.mark.parametrize("edit", [False, True])
@pytest.mark.parametrize("authorization", [None, "Bearer invalid"])
def test_ai_assist_requires_authentication(test_client, ai_project, blank_form, service_calls, edit, authorization):
    response = test_client.post(
        request_url(ai_project, edit), json=blank_form,
        headers={} if authorization is None else {"Authorization": authorization},
    )
    assert response.status_code == 401
    assert service_calls == []


# TC-005 | AC-018.1, AC-022.1 — AI assist checks current bug status
@pytest.mark.parametrize("status", ["Open", "Development", "Testing", "Closed", "Triage"])
def test_ai_assist_checks_current_bug_status(
    test_client, ai_project, blank_form, service_calls,
    authenticated_user_factory, member_factory, status,
):
    owner, developer, project, bug, base = ai_project
    qa = authenticated_user_factory(email="qa@example.com")
    member_factory(owner["token"], project["id"], qa["user"]["email"], "QA Analyst")
    transitions = [{"status": "Open"}]
    if status != "Open":
        transitions.append({"status": "Development"})
    if status == "Testing":
        transitions.append({"status": "Testing", "assignee_id": qa["user_id"]})
    if status in ("Closed", "Triage"):
        transitions.append({"status": "Closed", "resolution": "Won't Fix"})
    if status == "Triage":
        transitions.append({"status": "Triage"})
    for transition in transitions:
        response = test_client.patch(f"{base}/bugs/{bug['bug_number']}/status", headers=headers(owner), json=transition)
        assert response.status_code == 200
    response = test_client.post(request_url(ai_project, True), headers=headers(qa), json=blank_form)
    assert response.status_code == (503 if status == "Triage" else 409)
    assert len(service_calls) == (1 if status == "Triage" else 0)


# TC-006 | AC-018.1, AC-022.1 — AI assist rechecks membership
def test_ai_assist_rechecks_membership(test_client, ai_project, blank_form, service_calls, authenticated_user_factory, member_factory):
    owner, _, project, _, base = ai_project
    qa = authenticated_user_factory(email="qa@example.com")
    member_factory(owner["token"], project["id"], qa["user"]["email"], "QA Analyst")
    for edit in (False, True):
        assert test_client.post(request_url(ai_project, edit), headers=headers(qa), json=blank_form).status_code == 503
    response = test_client.delete(f"{base}/members/{qa['user_id']}", headers=headers(owner))
    assert response.status_code == 200
    service_calls.clear()
    for edit in (False, True):
        assert test_client.post(request_url(ai_project, edit), headers=headers(qa), json=blank_form).status_code == 404
    assert service_calls == []


# TC-007 | AC-018.1, AC-022.1 — AI assist rejects bug outside project
def test_ai_assist_rejects_bug_outside_project(test_client, ai_project, project_factory, blank_form, service_calls):
    owner, _, _, bug, _ = ai_project
    other = project_factory(owner["token"], name="Other project")
    for bug_number in (bug["bug_number"], bug["bug_number"] + 100):
        response = test_client.post(
            f"/projects/{other['id']}/bugs/{bug_number}/ai-assist", headers=headers(owner), json=blank_form,
        )
        assert response.status_code == 404
    assert service_calls == []


# TC-008 | AC-018.3, AC-023.1 — AI assist preserves current form without saving
@pytest.mark.parametrize("edit", [False, True])
@pytest.mark.parametrize("populated", [False, True])
def test_ai_assist_preserves_current_form_without_saving(test_client, ai_project, blank_form, service_calls, edit, populated):
    owner, developer, project, bug, base = ai_project
    form = blank_form.copy()
    if populated:
        form.update(title="  Unsaved title  ", affected_version="0.2", environment="  Windows  ",
                    description="Unsaved\ncontent", steps_to_reproduce="1. Click", expected_result=" ",
                    actual_result="Failure", severity="Major", priority="High", assignee_id=developer["user_id"])
    response = test_client.post(request_url(ai_project, edit), headers=headers(owner), json=form)
    assert response.status_code == 503
    assert service_calls == [(project["id"], bug["id"] if edit else None, form)]
    stored = test_client.get(f"{base}/bugs/{bug['bug_number']}", headers=headers(owner)).json()
    assert stored == bug
    bugs = test_client.get(f"{base}/bugs", headers=headers(owner)).json()
    assert len(bugs) == 1


# TC-009, TC-010 | AC-018.3 — AI assist rejects invalid context
@pytest.mark.parametrize("field,value", [
    ("fix_version", "1.0"), ("status", "Triage"), ("resolution", "Fixed"),
    ("created_at", "today"), ("updated_at", "today"), ("title", 12),
    ("assignee_id", "3"), ("assignee_id", True), ("severity", "Severe"), ("priority", "Critical"),
])
def test_ai_assist_rejects_invalid_context(test_client, ai_project, blank_form, service_calls, field, value):
    response = test_client.post(request_url(ai_project, False), headers=headers(ai_project[0]), json=blank_form | {field: value})
    assert response.status_code == 422
    assert service_calls == []


# TC-011 | AC-018.3 — AI assist requires complete snapshot
def test_ai_assist_requires_complete_snapshot(test_client, ai_project, blank_form, service_calls):
    del blank_form["description"]
    response = test_client.post(request_url(ai_project, True), headers=headers(ai_project[0]), json=blank_form)
    assert response.status_code == 422
    assert service_calls == []


# TC-422 | AC-025.6, AC-023.1 — AI assist rejects oversized current form text before the provider
@pytest.mark.parametrize("edit", [False, True])
@pytest.mark.parametrize("field,label", [
    ("title", "Title"), ("affected_version", "Affected Version"), ("environment", "Environment"),
    ("description", "Description"), ("steps_to_reproduce", "Steps to Reproduce"),
    ("expected_result", "Expected Result"), ("actual_result", "Actual Result"),
])
def test_ai_assist_rejects_oversized_form_text_before_provider(
    test_client, ai_project, blank_form, service_calls, field, label, edit,
):
    from app.ai_context import FORM_TEXT_LIMIT

    owner, developer, project, bug, base = ai_project
    at_limit = blank_form | {field: "x" * FORM_TEXT_LIMIT}
    response = test_client.post(request_url(ai_project, edit), headers=headers(owner), json=at_limit)
    assert response.status_code == 503
    assert len(service_calls) == 1

    oversized = blank_form | {field: "x" * (FORM_TEXT_LIMIT + 1)}
    response = test_client.post(request_url(ai_project, edit), headers=headers(owner), json=oversized)
    assert response.status_code == 422
    assert response.json() == {"detail": f"{label} is too long for AI Assist (maximum 5,000 characters)."}
    # Authorization still comes first, so oversized input reveals nothing to a Developer.
    response = test_client.post(request_url(ai_project, edit), headers=headers(developer), json=oversized)
    assert response.status_code == 403
    assert len(service_calls) == 1
    assert test_client.get(f"{base}/bugs/{bug['bug_number']}", headers=headers(owner)).json() == bug
    assert len(test_client.get(f"{base}/bugs", headers=headers(owner)).json()) == 1
