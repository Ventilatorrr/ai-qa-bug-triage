from playwright.sync_api import expect

from tests.e2e.helpers import api_call, login, unique_name


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
