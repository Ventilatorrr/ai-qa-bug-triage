import pytest

from playwright.sync_api import expect

from tests.e2e.helpers import api_call, login, unique_name


# Text line boxes, as in TC-378: a fitting element alone cannot prove readability.
TEXT_LAYOUT = """element => {
    const range = document.createRange();
    range.selectNodeContents(element);
    const box = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return {
        viewport: document.documentElement.clientWidth,
        pageWidth: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth),
        left: box.left, right: box.right, top: box.top, bottom: box.bottom,
        clientWidth: element.clientWidth, scrollWidth: element.scrollWidth,
        overflowX: style.overflowX, textOverflow: style.textOverflow,
        lines: Array.from(range.getClientRects(), rect => ({
            left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom
        }))
    };
}"""


def assert_text_within_viewport(locator, wrapped):
    layout = locator.evaluate(TEXT_LAYOUT)
    assert layout["pageWidth"] <= layout["viewport"], layout
    assert 0 <= layout["left"] < layout["right"] <= layout["viewport"], layout
    assert layout["scrollWidth"] <= layout["clientWidth"], layout
    assert layout["overflowX"] == "visible" and layout["textOverflow"] != "ellipsis", layout
    assert layout["lines"], layout
    for line in layout["lines"]:
        assert layout["left"] - 1 <= line["left"] < line["right"] <= layout["right"] + 1, layout
        assert layout["top"] - 1 <= line["top"] < line["bottom"] <= layout["bottom"] + 1, layout
    if wrapped:
        assert len({round(line["top"]) for line in layout["lines"]}) > 1, layout


# TC-339 | AC-005.1, AC-005.2, AC-007.1, AC-008.1 — Project create rename and confirmed delete
def test_project_create_rename_and_confirmed_delete(page, e2e_api, account_factory):
    owner = account_factory()

    login(page, owner)
    name = unique_name("Browser project")
    page.get_by_role("button", name="New Project").click()

    page.get_by_label("Project name:", exact=True).fill("   ")
    page.get_by_role("button", name="Create", exact=True).click()
    expect(page.get_by_role("status")).to_have_text("Project name is required.")

    page.get_by_label("Project name:", exact=True).fill(name)
    expect(page.get_by_text("Project name is required.", exact=True)).to_have_count(0)
    page.get_by_role("button", name="Create", exact=True).click()

    expect(page.get_by_role("link", name=name, exact=True)).to_be_visible()
    page.reload()

    page.get_by_role("button", name=f"Edit project {name}").click()
    renamed = unique_name("Renamed project")
    page.get_by_role("textbox", name="Project name", exact=True).fill(renamed)
    page.get_by_role("button", name="Save", exact=True).click()

    expect(page.get_by_role("link", name=renamed, exact=True)).to_be_visible()
    page.reload()
    project = next(
        p for p in api_call(e2e_api, "GET", "/projects", owner) if p["name"] == renamed
    )

    page.get_by_role("button", name=f"Edit project {renamed}").click()
    page.once("dialog", lambda dialog: dialog.dismiss())
    page.get_by_role("button", name="Delete", exact=True).click()
    expect(page.get_by_role("textbox", name="Project name", exact=True)).to_have_value(renamed)
    assert api_call(e2e_api, "GET", f"/projects/{project['id']}", owner)["name"] == renamed

    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Delete", exact=True).click()
    expect(page.get_by_role("status")).to_contain_text("deleted successfully")

    page.reload()
    expect(page.get_by_role("link", name=renamed, exact=True)).to_have_count(0)
    api_call(e2e_api, "GET", f"/projects/{project['id']}", owner, expected=404)


# TC-409 | AC-005.1, AC-006.3, AC-009.1 — Audit B4 project and member text wraps without overflow
@pytest.mark.parametrize("width", [1280, 375], ids=["desktop", "narrow"])
@pytest.mark.parametrize("unbroken", [False, True], ids=["normal", "unbroken"])
def test_project_and_member_text_wraps(page, e2e_api, account_factory, width, unbroken):
    owner = account_factory()
    if unbroken:
        name = unique_name("P" * 200)
        email = (f"{unique_name('m' * 40)}"
                 "@overflowtestingsubdomainalpha.overflowtestingsubdomainbeta.example.com")
    else:
        name = unique_name("Browser project")
        email = f"{unique_name('member')}@example.com"
    api_call(e2e_api, "POST", "/register", expected=201,
             data={"email": email, "password": "TestPassword123!"})

    page.set_viewport_size({"width": width, "height": 900})
    login(page, owner)
    page.get_by_role("button", name="New Project", exact=True).click()
    page.get_by_label("Project name:", exact=True).fill(name)
    page.get_by_role("button", name="Create", exact=True).click()
    project_message = page.locator("#message")
    expect(project_message).to_have_text(f'Project "{name}" created successfully.')
    assert_text_within_viewport(project_message, unbroken)

    page.get_by_role("link", name=name, exact=True).click()
    heading = page.get_by_role("heading", name=name, exact=True, level=2)
    expect(heading).to_be_visible()
    assert_text_within_viewport(heading, unbroken)

    page.get_by_role("button", name="Show Members", exact=True).click()
    page.get_by_role("button", name="Add Member", exact=True).click()
    page.get_by_label("Email:", exact=True).fill(email)
    page.get_by_label("Role:", exact=True).select_option("Developer")
    page.get_by_role("button", name="Add", exact=True).click()
    member_message = page.locator("#member-message")
    expect(member_message).to_have_text(f'Member "{email}" (Developer) added successfully.')
    assert_text_within_viewport(member_message, unbroken)
    expect(page.locator("#members").get_by_text(email, exact=True)).to_be_visible()
