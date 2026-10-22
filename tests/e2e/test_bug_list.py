import re

from playwright.sync_api import expect

from tests.e2e.helpers import api_call, login, seed_bug, unique_name
from tests.e2e.pages import BugList


# TC-333 | AC-012.2, AC-012.4, AC-012.5, AC-012.6 — Sort pagination and page size survive navigation and reload
def test_sort_pagination_and_page_size_survive_navigation_and_reload(page, e2e_api, workspace):
    for number in range(11):
        seed_bug(e2e_api, workspace, title=f"Synthetic report {number:02d}")
    bugs = BugList(page)

    login(page, workspace["owner"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(bugs.rows).to_have_count(11)
    expect(bugs.previous_page).to_be_disabled()

    bugs.next_page.click()
    expect(bugs.rows).to_have_count(2)
    expect(bugs.next_page).to_be_disabled()

    bugs.sort_by("Title")
    expect(bugs.rows).to_have_count(11)
    expect(bugs.previous_page).to_be_disabled()
    expect(bugs.rows.filter(has_text="Synthetic report 00")).to_be_visible()
    expect(
        bugs.table.get_by_role("cell").filter(has_text=re.compile(r"^Synthetic report"))
    ).to_have_text([f"Synthetic report {number:02d}" for number in range(10)])

    bugs.page_size.select_option("20")
    expect(bugs.rows).to_have_count(12)

    # Ordinary row clicks and the native link must resolve the same local report.
    row = bugs.rows.filter(has_text="Synthetic report 00")
    destination = row.get_by_role("link", name="BUG-1", exact=True).get_attribute("href")
    row.get_by_role("cell", name="Synthetic report 00", exact=True).click()
    expect(page).to_have_url(destination)
    expect(page.get_by_role("heading", name="Synthetic report 00", exact=True)).to_be_visible()

    page.go_back()
    expect(bugs.page_size).to_have_value("20")
    expect(bugs.rows).to_have_count(12)
    expect(bugs.column_header("Title")).to_have_attribute("aria-sort", "ascending")

    page.reload()
    expect(bugs.page_size).to_have_value("20")
    expect(bugs.rows).to_have_count(12)


# TC-334 | AC-012.5, AC-012.6 — Page size preferences persist and are isolated by user
def test_page_size_preferences_persist_and_are_isolated_by_user(page, e2e_api, workspace):
    owner = workspace["owner"]
    second = api_call(
        e2e_api, "POST", "/projects", owner, expected=201,
        data={"name": unique_name("Preference project")},
    )
    for project in [workspace["project"], second]:
        for number in range(21):
            seed_bug(e2e_api, workspace | {"project": project}, title=f"Preference {number:02d}")
    bugs = BugList(page)

    login(page, owner)
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(bugs.page_size).to_have_value("10")
    expect(bugs.rows).to_have_count(11)
    bugs.sort_by("Title")
    bugs.sort_by("Title")
    bugs.page_size.select_option("20")
    expect(bugs.rows).to_have_count(21)
    expect(bugs.column_header("Title")).to_have_attribute("aria-sort", "descending")

    page.get_by_role("link", name="BUG-21", exact=True).click()
    page.go_back()
    expect(bugs.page_size).to_have_value("20")
    page.reload()
    expect(bugs.page_size).to_have_value("20")
    expect(bugs.column_header("Title")).to_have_attribute("aria-sort", "descending")

    page.goto("/projects.html")
    page.get_by_role("link", name=second["name"], exact=True).click()
    expect(bugs.page_size).to_have_value("20")
    expect(bugs.column_header("Last Updated")).to_have_attribute("aria-sort", "descending")
    bugs.sort_by("Bug ID")
    bugs.page_size.select_option("50")
    expect(bugs.rows).to_have_count(22)
    expect(page.get_by_role("navigation", name="Bug report pages")).to_be_hidden()

    login(page, owner)
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(bugs.page_size).to_have_value("50")
    expect(bugs.rows).to_have_count(22)
    expect(bugs.column_header("Title")).to_have_attribute("aria-sort", "descending")

    login(page, workspace["qa"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(bugs.page_size).to_have_value("10")
    expect(bugs.rows).to_have_count(11)
    expect(bugs.column_header("Last Updated")).to_have_attribute("aria-sort", "descending")
    bugs.page_size.select_option("20")
    page.reload()
    expect(bugs.page_size).to_have_value("20")
    expect(bugs.rows).to_have_count(21)

    login(page, owner)
    page.get_by_role("link", name=second["name"], exact=True).click()
    expect(bugs.page_size).to_have_value("50")
    expect(bugs.column_header("Bug ID")).to_have_attribute("aria-sort", "ascending")

    login(page, workspace["qa"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(bugs.page_size).to_have_value("20")
    expect(bugs.rows).to_have_count(21)
