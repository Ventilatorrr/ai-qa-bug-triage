import json

import pytest

from playwright.sync_api import expect

from tests.e2e.helpers import api_call, bug_path, detail, login, open_bug, seed_bug, unique_name
from tests.e2e.pages import BugForm


# TC-378 | AC-011.1 — BUG-34 creation confirmation wraps without overflow
@pytest.mark.parametrize("width", [1280, 375], ids=["desktop", "narrow"])
# The unbroken title uses the 255-character maximum (AC-011.5).
@pytest.mark.parametrize("title", ["Synthetic bug", "W" * 255], ids=["normal", "unbroken"])
def test_bug_creation_confirmation_wraps(page, e2e_api, workspace, tmp_path, width, title):
    form = BugForm(page)
    page.set_viewport_size({"width": width, "height": 900})
    login(page, workspace["owner"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    page.get_by_role("button", name="New Bug", exact=True).click()
    form.title.fill(title)

    collection = f"/projects/{workspace['project']['id']}/bugs"
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url.endswith(collection)
    ) as created:
        form.create.click()
    assert created.value.status == 201
    bug = created.value.json()
    message = page.locator("#bug-message")
    expect(message).to_have_text(f'BUG-{bug["bug_number"]} "{title}" created successfully.')
    expect(message).to_be_visible()
    expect(page.locator("#bug-form")).to_be_hidden()
    expect(page.get_by_role("link", name=f'BUG-{bug["bug_number"]}', exact=True)).to_be_visible()
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"])["title"] == title

    # Check actual text line boxes: a fitting paragraph alone cannot prove readability.
    layout = message.evaluate("""element => {
        const range = document.createRange();
        range.selectNodeContents(element);
        const box = element.getBoundingClientRect();
        const style = getComputedStyle(element);
        return {
            viewport: document.documentElement.clientWidth,
            pageWidth: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth),
            left: box.left, right: box.right,
            clientWidth: element.clientWidth, scrollWidth: element.scrollWidth,
            clientHeight: element.clientHeight, scrollHeight: element.scrollHeight,
            whiteSpace: style.whiteSpace, overflowX: style.overflowX, overflowY: style.overflowY,
            textOverflow: style.textOverflow, textAlign: style.textAlign,
            lines: Array.from(range.getClientRects(), rect => ({
                left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom
            })),
            top: box.top, bottom: box.bottom
        };
    }""")
    (tmp_path / "confirmation-layout.json").write_text(json.dumps(layout, indent=2), encoding="utf-8")
    assert layout["pageWidth"] <= layout["viewport"], layout
    assert 0 <= layout["left"] < layout["right"] <= layout["viewport"], layout
    assert layout["scrollWidth"] <= layout["clientWidth"], layout
    assert layout["scrollHeight"] <= layout["clientHeight"], layout
    assert layout["whiteSpace"] == "normal"
    assert layout["overflowX"] == layout["overflowY"] == "visible"
    assert layout["textOverflow"] != "ellipsis"
    assert layout["textAlign"] == "center"
    assert "message-success" in message.get_attribute("class").split()
    assert layout["lines"]
    for line in layout["lines"]:
        assert layout["left"] - 1 <= line["left"] < line["right"] <= layout["right"] + 1, layout
        assert layout["top"] - 1 <= line["top"] < line["bottom"] <= layout["bottom"] + 1, layout
    if len(title) == 2000:
        assert len(layout["lines"]) > 1
    else:
        assert len(layout["lines"]) == 1


# TC-335 | AC-011.1, AC-013.1, AC-014.1, AC-015.1 — Bug create edit assign and confirmed delete
def test_bug_create_edit_assign_and_confirmed_delete(page, e2e_api, workspace):
    form = BugForm(page)
    login(page, workspace["owner"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    page.get_by_role("button", name="New Bug", exact=True).click()

    title = unique_name("Browser bug")
    form.title.fill(title)
    form.environment.fill("Synthetic Chromium environment")
    form.description.fill("Synthetic reproduction")
    form.severity.select_option("Minor")
    form.create.click()

    page.get_by_role("link", name="BUG-1", exact=True).click()
    expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()
    expect(detail(page, "Status")).to_have_text("Triage")

    page.get_by_role("button", name="Edit", exact=True).click()
    revised = unique_name("Revised bug")
    form.title.fill(revised)
    form.priority.select_option("High")
    form.assignee.select_option(str(workspace["developer"]["id"]))
    form.save.click()
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
    expect(form.save).to_be_visible()
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]) == bug

    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Delete", exact=True).click()
    expect(page).to_have_url(f"/project.html?id={workspace['project']['id']}")
    expect(page.get_by_role("link", name="BUG-1", exact=True)).to_have_count(0)
    api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"], expected=404)


# TC-336 | AC-017.2, AC-017.3, AC-017.4, AC-017.5, AC-017.7 — Bug handoff pass and reopen
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


# TC-337 | AC-017.5 — Failed testing returns to selected developer
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


# TC-338 | AC-011.4, AC-013.2, AC-017.5, AC-017.6 — Fix version eligibility persistence and form reset
def test_fix_version_eligibility_persistence_and_form_reset(page, e2e_api, workspace):
    owner = workspace["owner"]
    title = unique_name("Fix Version eligibility")
    collection = f"/projects/{workspace['project']['id']}/bugs"
    form = BugForm(page)
    fix_version = form.fix_version

    login(page, owner)
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    page.get_by_role("button", name="New Bug", exact=True).click()
    expect(fix_version).to_have_count(0)
    form.title.fill(title)
    form.create.click()
    page.get_by_role("link", name="BUG-1", exact=True).click()
    expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()

    bug = api_call(e2e_api, "GET", collection, owner)[0]
    path = bug_path(workspace, bug)
    assert api_call(e2e_api, "GET", path, owner)["fix_version"] is None

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
        form.description.fill(f"Edited in {state}")

        with page.expect_request(
            lambda request: request.method == "PATCH" and request.url.endswith(path)
        ) as save:
            form.save.click()
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
        form.save.click()
        expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible()
        stored = api_call(e2e_api, "GET", path, owner)
        assert (stored["fix_version"] or "") == version
        assert (stored["status"], stored["resolution"]) == ("Closed", "Fixed")
        page.reload()
        expect(detail(page, "Fix Version")).to_have_text(version or "Not provided")
        previous = version

    page.get_by_role("button", name="Edit", exact=True).click()
    fix_version.fill("9.9.9")
    form.cancel.click()
    assert not api_call(e2e_api, "GET", path, owner)["fix_version"]
    page.get_by_role("button", name="Move to Triage", exact=True).click()
    expect(detail(page, "Status")).to_have_text("Triage")

    page.get_by_role("button", name="Edit", exact=True).click()
    expect(fix_version).to_be_hidden()
    expect(fix_version).to_have_value("")
    form.description.fill("Saved after reopening")
    with page.expect_request(
        lambda request: request.method == "PATCH" and request.url.endswith(path)
    ) as save:
        form.save.click()
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
    form.description.fill("Saved without a fix")
    with page.expect_request(
        lambda request: request.method == "PATCH" and request.url.endswith(path)
    ) as save:
        form.save.click()
    expect(page.get_by_role("button", name="Edit", exact=True)).to_be_visible()
    assert "fix_version" not in save.value.post_data_json
    stored = api_call(e2e_api, "GET", path, owner)
    assert stored["fix_version"] is None
    assert stored["description"] == "Saved without a fix"
