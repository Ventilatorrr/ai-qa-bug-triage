from playwright.sync_api import expect

from tests.e2e.helpers import api_call, bug_path, detail, login, open_bug, seed_bug, unique_name


def test_bug_create_edit_assign_and_confirmed_delete(page, e2e_api, workspace):
    login(page, workspace["owner"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    page.get_by_role("button", name="New Bug", exact=True).click()

    title = unique_name("Browser bug")
    page.get_by_label("Title:", exact=True).fill(title)
    page.get_by_label("Environment:", exact=True).fill("Synthetic Chromium environment")
    page.get_by_label("Description:", exact=True).fill("Synthetic reproduction")
    page.get_by_label("Severity:", exact=True).select_option("Minor")
    page.get_by_role("button", name="Create", exact=True).click()

    page.get_by_role("link", name="BUG-1", exact=True).click()
    expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()
    expect(detail(page, "Status")).to_have_text("Triage")

    page.get_by_role("button", name="Edit", exact=True).click()
    revised = unique_name("Revised bug")
    page.get_by_label("Title:", exact=True).fill(revised)
    page.get_by_label("Priority:", exact=True).select_option("High")
    page.get_by_label("Assignee:", exact=True).select_option(str(workspace["developer"]["id"]))
    page.get_by_role("button", name="Save", exact=True).click()
    expect(page.get_by_role("heading", name=revised, exact=True)).to_be_visible()

    page.reload()
    expect(detail(page, "Assignee")).to_contain_text(workspace["developer"]["email"])
    expect(detail(page, "Priority")).to_have_text("High")
    expect(detail(page, "Environment")).to_have_text("Synthetic Chromium environment")
    bug = api_call(
        e2e_api, "GET", f"/projects/{workspace['project']['id']}/bugs/1", workspace["owner"]
    )

    page.get_by_role("button", name="Edit", exact=True).click()
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Delete", exact=True).click()
    expect(page.get_by_role("button", name="Save", exact=True)).to_be_visible()
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]) == bug

    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Delete", exact=True).click()
    expect(page).to_have_url(f"/project.html?id={workspace['project']['id']}")
    expect(page.get_by_role("link", name="BUG-1", exact=True)).to_have_count(0)
    api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"], expected=404)


def test_bug_handoff_pass_and_reopen(page, e2e_api, workspace):
    bug = seed_bug(e2e_api, workspace)

    login(page, workspace["owner"])
    open_bug(page, workspace, bug)
    expect(page.get_by_role("button", name="Move to Open", exact=True)).to_be_disabled()
    page.get_by_label("Assignee for lifecycle transition").select_option(
        str(workspace["developer"]["id"])
    )
    page.get_by_role("button", name="Move to Open", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Open")

    login(page, workspace["developer"])
    open_bug(page, workspace, bug)
    page.get_by_label("Assignee for lifecycle transition").select_option(
        str(workspace["developer"]["id"])
    )
    page.get_by_role("button", name="Move to Development", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Development")

    page.get_by_label("QA Analyst for testing").select_option(str(workspace["qa"]["id"]))
    page.get_by_role("button", name="Send to Testing", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Testing")

    login(page, workspace["qa"])
    open_bug(page, workspace, bug)
    page.get_by_label("Fix Version (optional)").fill("0.1.0")
    page.get_by_role("button", name="Pass", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Closed")
    expect(detail(page, "Resolution")).to_have_text("Fixed")

    page.reload()
    expect(detail(page, "Fix Version")).to_have_text("0.1.0")

    login(page, workspace["owner"])
    open_bug(page, workspace, bug)
    page.get_by_role("button", name="Move to Triage", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Triage")

    saved = api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"])
    assert saved["resolution"] is None and saved["fix_version"] is None
    assert saved["assignee_id"] == workspace["qa"]["id"]


def test_failed_testing_returns_to_selected_developer(page, e2e_api, workspace):
    bug = seed_bug(e2e_api, workspace, assignee_id=workspace["developer"]["id"])
    for payload in [
        {"status": "Open"},
        {"status": "Development"},
        {"status": "Testing", "assignee_id": workspace["qa"]["id"]},
    ]:
        api_call(
            e2e_api, "PATCH", bug_path(workspace, bug) + "/status", workspace["owner"],
            data=payload,
        )

    login(page, workspace["qa"])
    open_bug(page, workspace, bug)
    expect(page.get_by_role("button", name="Fail", exact=True)).to_be_disabled()
    page.get_by_label("Developer for failed testing").select_option(
        str(workspace["developer"]["id"])
    )
    page.get_by_role("button", name="Fail", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Development")

    page.reload()
    expect(detail(page, "Assignee")).to_contain_text(workspace["developer"]["email"])
    saved = api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"])
    assert saved["status"] == "Development" and saved["resolution"] is None


def test_fix_version_eligibility_persistence_and_form_reset(page, e2e_api, workspace):
    owner = workspace["owner"]
    title = unique_name("Fix Version eligibility")
    collection = f"/projects/{workspace['project']['id']}/bugs"

    login(page, owner)
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    page.get_by_role("button", name="New Bug", exact=True).click()
    expect(page.get_by_label("Fix Version:", exact=True)).to_have_count(0)
    page.get_by_label("Title:", exact=True).fill(title)
    page.get_by_role("button", name="Create", exact=True).click()
    page.get_by_role("link", name="BUG-1", exact=True).click()
    expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()

    bug = api_call(e2e_api, "GET", collection, owner)[0]
    path = bug_path(workspace, bug)
    assert api_call(e2e_api, "GET", path, owner)["fix_version"] is None
    fix_version = page.get_by_label("Fix Version:", exact=True)

    for state, transition in [
        ("Triage", None),
        ("Open", {"status": "Open", "assignee_id": workspace["developer"]["id"]}),
        ("Development", {"status": "Development"}),
        ("Testing", {"status": "Testing", "assignee_id": workspace["qa"]["id"]}),
    ]:
        if transition:
            api_call(e2e_api, "PATCH", path + "/status", owner, data=transition)
            page.reload()
        expect(detail(page, "Status")).to_have_text(state)
        page.get_by_role("button", name="Edit", exact=True).click()
        expect(fix_version).to_be_hidden()
        expect(fix_version).to_have_value("")
        page.get_by_label("Description:", exact=True).fill(f"Edited in {state}")

        with page.expect_request(
            lambda request: request.method == "PATCH" and request.url.endswith(path)
        ) as save:
            page.get_by_role("button", name="Save", exact=True).click()
        expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible()
        assert "fix_version" not in save.value.post_data_json
        stored = api_call(e2e_api, "GET", path, owner)
        assert stored["description"] == f"Edited in {state}"
        assert stored["fix_version"] is None

    expect(page.get_by_label("Fix Version (optional)")).to_be_editable()
    page.get_by_role("button", name="Pass", exact=True).click()
    expect(detail(page, "Resolution")).to_have_text("Fixed")
    assert api_call(e2e_api, "GET", path, owner)["fix_version"] is None

    previous = ""
    for version in ["0.1.0", "0.1.1", ""]:
        page.get_by_role("button", name="Edit", exact=True).click()
        expect(fix_version).to_be_editable()
        expect(fix_version).to_have_value(previous)
        fix_version.fill(version)
        page.get_by_role("button", name="Save", exact=True).click()
        expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible()
        stored = api_call(e2e_api, "GET", path, owner)
        assert (stored["fix_version"] or "") == version
        assert (stored["status"], stored["resolution"]) == ("Closed", "Fixed")
        page.reload()
        expect(detail(page, "Fix Version")).to_have_text(version or "Not provided")
        previous = version

    page.get_by_role("button", name="Edit", exact=True).click()
    fix_version.fill("9.9.9")
    page.get_by_role("button", name="Cancel", exact=True).click()
    assert not api_call(e2e_api, "GET", path, owner)["fix_version"]
    page.get_by_role("button", name="Move to Triage", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Triage")

    page.get_by_role("button", name="Edit", exact=True).click()
    expect(fix_version).to_be_hidden()
    expect(fix_version).to_have_value("")
    page.get_by_label("Description:", exact=True).fill("Saved after reopening")
    with page.expect_request(
        lambda request: request.method == "PATCH" and request.url.endswith(path)
    ) as save:
        page.get_by_role("button", name="Save", exact=True).click()
    expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible()
    assert "fix_version" not in save.value.post_data_json
    stored = api_call(e2e_api, "GET", path, owner)
    assert stored["fix_version"] is None
    assert stored["description"] == "Saved after reopening"

    for transition in [
        {"status": "Open", "assignee_id": workspace["developer"]["id"]},
        {"status": "Development"},
        {"status": "Closed", "resolution": "Duplicate"},
    ]:
        api_call(e2e_api, "PATCH", path + "/status", owner, data=transition)
    page.reload()
    expect(detail(page, "Resolution")).to_have_text("Duplicate")
    page.get_by_role("button", name="Edit", exact=True).click()
    expect(fix_version).to_be_hidden()
    expect(fix_version).to_have_value("")
    page.get_by_label("Description:", exact=True).fill("Saved without a fix")
    with page.expect_request(
        lambda request: request.method == "PATCH" and request.url.endswith(path)
    ) as save:
        page.get_by_role("button", name="Save", exact=True).click()
    expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible()
    assert "fix_version" not in save.value.post_data_json
    stored = api_call(e2e_api, "GET", path, owner)
    assert stored["fix_version"] is None
    assert stored["description"] == "Saved without a fix"
