import re

from playwright.sync_api import expect

from tests.e2e.helpers import api_call, login, seed_bug, unique_name


def test_sort_pagination_and_page_size_survive_navigation_and_reload(page, e2e_api, workspace):
    for number in range(11):
        seed_bug(e2e_api, workspace, title=f"Synthetic report {number:02d}")

    login(page, workspace["owner"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    table = page.get_by_role("table")
    expect(table.get_by_role("row")).to_have_count(11)
    expect(page.get_by_role("button", name="Previous", exact=True)).to_be_disabled()

    page.get_by_role("button", name="Next", exact=True).click()
    expect(table.get_by_role("row")).to_have_count(2)
    expect(page.get_by_role("button", name="Next", exact=True)).to_be_disabled()

    page.get_by_role("button", name=re.compile(r"^Title")).click()
    expect(table.get_by_role("row")).to_have_count(11)
    expect(page.get_by_role("button", name="Previous", exact=True)).to_be_disabled()
    expect(table.get_by_role("row").filter(has_text="Synthetic report 00")).to_be_visible()
    expect(
        table.get_by_role("cell").filter(has_text=re.compile(r"^Synthetic report"))
    ).to_have_text([f"Synthetic report {number:02d}" for number in range(10)])

    page.get_by_label("Bugs per page:").select_option("20")
    expect(table.get_by_role("row")).to_have_count(12)

    # Ordinary row clicks and the native link must resolve the same local report.
    row = table.get_by_role("row").filter(has_text="Synthetic report 00")
    destination = row.get_by_role("link", name="BUG-1", exact=True).get_attribute("href")
    row.get_by_role("cell", name="Synthetic report 00", exact=True).click()
    expect(page).to_have_url(destination)
    expect(page.get_by_role("heading", name="Synthetic report 00", exact=True)).to_be_visible()

    page.go_back()
    expect(page.get_by_label("Bugs per page:")).to_have_value("20")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(12)
    expect(page.get_by_role("columnheader", name="Title", exact=True)).to_have_attribute(
        "aria-sort", "ascending"
    )

    page.reload()
    expect(page.get_by_label("Bugs per page:")).to_have_value("20")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(12)


def test_page_size_preferences_persist_and_are_isolated_by_user(page, e2e_api, workspace):
    owner = workspace["owner"]
    second = api_call(
        e2e_api, "POST", "/projects", owner, expected=201,
        data={"name": unique_name("Preference project")},
    )
    for project in [workspace["project"], second]:
        for number in range(21):
            seed_bug(e2e_api, workspace | {"project": project}, title=f"Preference {number:02d}")

    login(page, owner)
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    size = page.get_by_label("Bugs per page:")
    expect(size).to_have_value("10")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(11)
    page.get_by_role("button", name=re.compile(r"^Title")).click()
    page.get_by_role("button", name=re.compile(r"^Title")).click()
    size.select_option("20")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(21)
    expect(page.get_by_role("columnheader", name="Title", exact=True)).to_have_attribute(
        "aria-sort", "descending"
    )

    page.get_by_role("link", name="BUG-21", exact=True).click()
    page.go_back()
    expect(size).to_have_value("20")
    page.reload()
    expect(size).to_have_value("20")
    expect(page.get_by_role("columnheader", name="Title", exact=True)).to_have_attribute(
        "aria-sort", "descending"
    )

    page.goto("/projects.html")
    page.get_by_role("link", name=second["name"], exact=True).click()
    expect(size).to_have_value("20")
    expect(page.get_by_role("columnheader", name="Last Updated", exact=True)).to_have_attribute(
        "aria-sort", "descending"
    )
    page.get_by_role("button", name=re.compile(r"^Bug ID")).click()
    size.select_option("50")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(22)
    expect(page.get_by_role("navigation", name="Bug report pages")).to_be_hidden()

    login(page, owner)
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(size).to_have_value("50")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(22)
    expect(page.get_by_role("columnheader", name="Title", exact=True)).to_have_attribute(
        "aria-sort", "descending"
    )

    login(page, workspace["qa"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(size).to_have_value("10")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(11)
    expect(page.get_by_role("columnheader", name="Last Updated", exact=True)).to_have_attribute(
        "aria-sort", "descending"
    )
    size.select_option("20")
    page.reload()
    expect(size).to_have_value("20")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(21)

    login(page, owner)
    page.get_by_role("link", name=second["name"], exact=True).click()
    expect(size).to_have_value("50")
    expect(page.get_by_role("columnheader", name="Bug ID", exact=True)).to_have_attribute(
        "aria-sort", "ascending"
    )

    login(page, workspace["qa"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    expect(size).to_have_value("20")
    expect(page.get_by_role("table").get_by_role("row")).to_have_count(21)
