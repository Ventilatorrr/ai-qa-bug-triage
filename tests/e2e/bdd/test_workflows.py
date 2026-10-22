"""Bind all five scenarios across the four BDD feature files."""

import pytest
from playwright.sync_api import expect
from pytest_bdd import given, scenario, then, when

from tests.e2e.helpers import api_call, bug_path, detail, login, open_bug, seed_bug, unique_name
from tests.e2e.pages import BugForm


# TC-386 | AC-001.1 — Successful Registration
@scenario("features/authentication.feature", "Successfully register an account")
def test_successful_registration():
    """Register through the UI and prove the new credentials work."""


# TC-387 | AC-005.1 — Successful Project Creation
@scenario("features/project_management.feature", "Successfully create a project")
def test_successful_project_creation():
    """Create through the UI and verify persistent ownership."""


# TC-388 | AC-007.2, AC-008.2, AC-010.5 — Non-owner project modification is forbidden
@scenario("features/project_management.feature", "Non-owner cannot modify a project")
def test_non_owner_cannot_modify_project():
    """Check UI restrictions and authoritative rename/delete authorization."""


# TC-389 | AC-011.1, AC-017.2, AC-017.3, AC-017.4, AC-017.5 — QA/Developer handoff
@scenario("features/bug_lifecycle.feature", "QA Analyst manages a bug lifecycle")
def test_qa_bug_lifecycle():
    """Create, open, develop, test and close a fictional bug report."""


# TC-390 | AC-018.1, AC-018.2, AC-020.1, AC-020.2, AC-020.3, AC-020.7 — AI review/save
@scenario("features/ai_review.feature", "Review and apply AI suggestions")
def test_review_ai_suggestions():
    """Exercise provider-mocked AI review through the actual form and Save."""


@pytest.fixture
def workflow():
    # Function scope keeps each scenario independent, including separate invocations.
    return {}


@given("I am on the registration page")
def registration_page(page, workflow):
    workflow["account"] = {
        "email": f"{unique_name('bdd-visitor')}@example.com",
        "password": "TestPassword123!",
    }
    page.goto("/register.html")
    expect(page.get_by_role("button", name="Register", exact=True)).to_be_visible()


@when("I register with a unique email address and a valid password")
def register(page, workflow):
    account = workflow["account"]
    page.get_by_label("Email:", exact=True).fill(account["email"])
    page.get_by_label("Password:", exact=True).fill(account["password"])
    with page.expect_response(
        lambda response: response.request.method == "POST" and response.url.endswith("/register")
    ) as registered:
        page.get_by_role("button", name="Register", exact=True).click()
    assert registered.value.status == 201


@then("my user account should be created")
def registered_account(page, workflow):
    expect(page).to_have_url("/login.html")
    login(page, workflow["account"])
    expect(page.get_by_role("heading", name="My Projects", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Logout", exact=True)).to_be_visible()


@given("I am an authenticated user")
def authenticated_user(page, account_factory, workflow):
    workflow["account"] = account_factory()
    login(page, workflow["account"])


@when("I create a project with a valid project name")
def create_project(page, workflow):
    workflow["name"] = unique_name("BDD project")
    page.get_by_role("button", name="New Project", exact=True).click()
    page.get_by_label("Project name:", exact=True).fill(workflow["name"])
    with page.expect_response(
        lambda response: response.request.method == "POST" and response.url.endswith("/projects")
    ) as created:
        page.get_by_role("button", name="Create", exact=True).click()
    assert created.value.status == 201
    workflow["project"] = created.value.json()


@then("the project should be created")
def project_created(page, e2e_api, workflow):
    expect(page.get_by_role("link", name=workflow["name"], exact=True)).to_be_visible()
    page.reload()
    expect(page.get_by_role("link", name=workflow["name"], exact=True)).to_be_visible()
    stored = api_call(e2e_api, "GET", f"/projects/{workflow['project']['id']}", workflow["account"])
    assert stored["name"] == workflow["name"]


@then("I should become the Project Owner of the project")
def project_owner(page, e2e_api, workflow):
    members = api_call(
        e2e_api, "GET", f"/projects/{workflow['project']['id']}/members", workflow["account"]
    )
    member = next(member for member in members if member["user_id"] == workflow["account"]["id"])
    assert member["role"] == "Project Owner"
    page.get_by_role("link", name=workflow["name"], exact=True).click()
    page.get_by_role("button", name="Show Members", exact=True).click()
    expect(page.locator("#members").get_by_text(
        f"{workflow['account']['email']} (Project Owner)", exact=True,
    )).to_be_visible()


@given("a QA Analyst is a non-owner member of an existing project")
def non_owner_project(page, e2e_api, workspace, workflow):
    workflow["original_project"] = api_call(
        e2e_api, "GET", f"/projects/{workspace['project']['id']}", workspace["owner"]
    )
    login(page, workspace["qa"])
    expect(page.get_by_role("link", name=workspace["project"]["name"], exact=True)).to_be_visible()


@when("the QA Analyst attempts to rename or delete the project")
def attempt_project_modification(page, e2e_api, workspace, workflow):
    expect(
        page.get_by_role("button", name=f"Edit project {workspace['project']['name']}", exact=True)
    ).to_have_count(0)
    # The UI offers neither action. Valid direct requests prove backend enforcement.
    path = f"/projects/{workspace['project']['id']}"
    headers = {"Authorization": f"Bearer {workspace['qa']['token']}"}
    workflow["denied"] = [
        e2e_api.put(path, headers=headers, data={"name": "Unauthorized rename"}),
        e2e_api.delete(path, headers=headers),
    ]


@then("project modification is forbidden")
def project_modification_forbidden(workflow):
    for response in workflow["denied"]:
        # Project owner-only endpoints conceal the resource with 404 by contract.
        assert response.status == 404, response.text()
        assert response.json() == {"detail": "Project not found."}


@then("the project's existing data remains unchanged")
def project_unchanged(page, e2e_api, workspace, workflow):
    stored = api_call(e2e_api, "GET", f"/projects/{workspace['project']['id']}", workspace["owner"])
    assert stored == workflow["original_project"]
    page.reload()
    page.get_by_role("link", name=stored["name"], exact=True).click()
    expect(page.get_by_role("heading", name=stored["name"], exact=True)).to_be_visible()


@given("a QA Analyst has access to a project with a Developer")
def qa_project(page, workspace):
    login(page, workspace["qa"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(page.get_by_role("heading", name=workspace["project"]["name"], exact=True)).to_be_visible()


@when("the QA Analyst creates a valid bug report")
def qa_create_bug(page, workspace, workflow):
    form = BugForm(page)
    page.get_by_role("button", name="New Bug", exact=True).click()
    title = unique_name("BDD lifecycle bug")
    form.title.fill(title)
    form.description.fill("Fictional lifecycle reproduction")
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url.endswith(f"/projects/{workspace['project']['id']}/bugs")
    ) as created:
        form.create.click()
    assert created.value.status == 201
    workflow["bug"] = created.value.json()
    assert workflow["bug"]["title"] == title
    page.get_by_role("link", name=f"BUG-{workflow['bug']['bug_number']}", exact=True).click()


@then("the new bug report is in Triage")
def bug_in_triage(page, e2e_api, workspace, workflow):
    expect(detail(page, "Status")).to_have_text("Triage")
    bug = api_call(e2e_api, "GET", bug_path(workspace, workflow["bug"]), workspace["qa"])
    assert bug["status"] == "Triage"
    assert bug["created_by"] == workspace["qa"]["id"]
    assert bug["project_id"] == workspace["project"]["id"]
    assert bug["created_at"] and bug["updated_at"]


@when("the QA Analyst assigns the bug to the Developer and moves it to Open")
def qa_open_bug(page, workspace):
    page.get_by_label("Assignee for lifecycle transition").select_option(
        str(workspace["developer"]["id"])
    )
    page.get_by_role("button", name="Move to Open", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Open")
    expect(detail(page, "Assignee")).to_contain_text(workspace["developer"]["email"])


@when("the Developer moves the bug through Development and hands it to the QA Analyst for Testing")
def developer_handoff(page, workspace, workflow):
    login(page, workspace["developer"])
    open_bug(page, workspace, workflow["bug"])
    page.get_by_label("Assignee for lifecycle transition").select_option(
        str(workspace["developer"]["id"])
    )
    page.get_by_role("button", name="Move to Development", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Development")
    page.get_by_label("QA Analyst for testing").select_option(str(workspace["qa"]["id"]))
    page.get_by_role("button", name="Send to Testing", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Testing")
    expect(detail(page, "Assignee")).to_contain_text(workspace["qa"]["email"])


@when("the QA Analyst passes testing")
def qa_pass_testing(page, workspace, workflow):
    login(page, workspace["qa"])
    open_bug(page, workspace, workflow["bug"])
    page.get_by_role("button", name="Pass", exact=True).click()


@then("the bug report is Closed with resolution Fixed")
def closed_fixed(page):
    expect(detail(page, "Status")).to_have_text("Closed")
    expect(detail(page, "Resolution")).to_have_text("Fixed")


@then("the lifecycle result is persisted correctly")
def lifecycle_persisted(page, e2e_api, workspace, workflow):
    page.reload()
    closed_fixed(page)
    expect(detail(page, "Assignee")).to_contain_text(workspace["qa"]["email"])
    saved = api_call(e2e_api, "GET", bug_path(workspace, workflow["bug"]), workspace["qa"])
    assert (saved["status"], saved["resolution"], saved["assignee_id"]) == (
        "Closed", "Fixed", workspace["qa"]["id"],
    )
    assert saved["title"] == workflow["bug"]["title"]
    assert saved["description"] == "Fictional lifecycle reproduction"
    assert saved["fix_version"] is None  # This fictional fix has no released version.


@given("a QA Analyst is editing a Triage bug report with deterministic AI suggestions available")
def edit_triage_bug(page, e2e_api, workspace, workflow):
    # Inherited e2e_base_url validates the provider-mocked server before any request.
    workflow["bug"] = seed_bug(
        e2e_api, workspace, description="Original fictional description", severity="Minor",
    )
    workflow["ai_requests"] = []
    page.on(
        "request",
        lambda request: workflow["ai_requests"].append(request.url)
        if request.url.endswith("/ai-assist") else None,
    )
    login(page, workspace["qa"])
    open_bug(page, workspace, workflow["bug"])
    page.get_by_role("button", name="Edit", exact=True).click()
    expect(BugForm(page).ai_assist).to_be_visible()
    assert workflow["ai_requests"] == []


@when("the QA Analyst requests AI assistance")
def request_ai(page):
    with page.expect_response(
        lambda response: response.request.method == "POST" and response.url.endswith("/ai-assist")
    ) as suggestions:
        BugForm(page).ai_assist.click()
    assert suggestions.value.status == 200


@then("the suggestions are available for review without changing the report")
def review_ai(page, e2e_api, workspace, workflow):
    bug = workflow["bug"]
    form = BugForm(page)
    expect(form.suggestion("Title")).to_contain_text(f"Reviewed {bug['title']}")
    expect(form.suggestion("Description")).to_contain_text("Clear synthetic reproduction details")
    expect(form.title).to_have_value(bug["title"])
    expect(form.description).to_have_value(bug["description"])
    assert len(workflow["ai_requests"]) == 1
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["qa"]) == bug


@when("the QA Analyst uses the Title suggestion and dismisses the Description suggestion")
def use_and_dismiss_ai(page):
    form = BugForm(page)
    form.use_suggestion("Title")
    form.dismiss_suggestion("Description")


@then("only the accepted suggestion changes the form and the report remains unsaved")
def ai_unsaved(page, e2e_api, workspace, workflow):
    bug = workflow["bug"]
    form = BugForm(page)
    expect(form.title).to_have_value(f"Reviewed {bug['title']}")
    expect(form.description).to_have_value(bug["description"])
    expect(form.severity).to_have_value("Minor")
    expect(form.suggestion("Title")).to_have_count(0)
    expect(form.suggestion("Description")).to_have_count(0)
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["qa"]) == bug


@when("the QA Analyst saves the bug report")
def save_ai(page, workspace, workflow):
    with page.expect_response(
        lambda response: response.request.method == "PATCH"
        and response.url.endswith(bug_path(workspace, workflow["bug"]))
    ) as saved:
        BugForm(page).save.click()
    assert saved.value.status == 200
    expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible()


@then("the saved report contains the accepted title and the original description")
def ai_persisted(page, e2e_api, workspace, workflow):
    bug = workflow["bug"]
    page.reload()
    expect(page.get_by_role("heading", name=f"Reviewed {bug['title']}", exact=True)).to_be_visible()
    expect(detail(page, "Description")).to_have_text(bug["description"])
    saved = api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["qa"])
    assert saved["title"] == f"Reviewed {bug['title']}"
    assert saved["description"] == bug["description"]
    assert saved["severity"] == "Minor"
    assert saved["priority"] == bug["priority"]
    assert saved["status"] == "Triage"
