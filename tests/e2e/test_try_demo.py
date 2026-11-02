from playwright.sync_api import Page, expect

from tests.e2e.pages import BugList


DEMO_NOTE = (
    "Some bug reports in Triage intentionally contain incomplete information, unclear wording, or questionable "
    "classifications. To try AI Assist, open a bug with Status set to Triage and click Edit, or select New Bug and "
    "enter a report. Then click AI Assist to review suggested improvements."
)
HISTORY_NOTE = (
    "This project contains real defects discovered during development of AI QA Bug Triage. "
    "Explore the reports to see how these defects were documented, classified, and tracked through to closure."
)
DEMO_INSTRUCTIONS = (
    "To explore AI Assist, open E-Commerce Demo. "
    "To review real defects tracked during development, open AI QA Bug Triage."
)


# TC-453 | AC-024.1, AC-024.3, AC-024.4, AC-024.6, AC-012.4 — Try Demo opens both seeded projects with their introductions
def test_try_demo_opens_seeded_projects_with_demo_note(page: Page):
    page.goto("/")
    expect(page).to_have_url("/login.html")  # The root page goes straight to Login without a session.
    expect(page.get_by_text("Your Demo work can't be accessed after logout or session expiry.")).to_be_visible()
    page.get_by_role("button", name="Try Demo", exact=True).click()

    expect(page).to_have_url("/projects.html")
    expect(page.get_by_role("link", name="E-Commerce Demo", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="AI QA Bug Triage", exact=True)).to_be_visible()
    expect(page.locator("#demo-instructions")).to_have_text(DEMO_INSTRUCTIONS)
    expect(page.locator("#demo-instructions")).to_be_visible()

    note = page.locator("#demo-note")
    page.get_by_role("link", name="E-Commerce Demo", exact=True).click()
    expect(page.get_by_role("heading", level=2, name="E-Commerce Demo", exact=True)).to_be_visible()
    expect(note).to_be_visible()
    expect(note).to_have_text(DEMO_NOTE)
    expect(page.locator("#demo-history-note")).to_be_hidden()
    # Expanded Members stay above the introduction, which stays above New Bug.
    page.get_by_role("button", name="Show Members", exact=True).click()
    members_bottom = page.locator("#members-content").bounding_box()
    note_box = note.bounding_box()
    assert members_bottom["y"] + members_bottom["height"] <= note_box["y"]
    assert note_box["y"] + note_box["height"] <= page.locator("#show-bug-form").bounding_box()["y"]
    page.get_by_role("button", name="Hide Members", exact=True).click()
    expect(page.get_by_text("Showing 1–10 of 20")).to_be_visible()
    # Default order is Bug ID descending: the newest report and BUG-14 are both on page one.
    bugs = BugList(page)
    expect(bugs.column_header("Bug ID")).to_have_attribute("aria-sort", "descending")
    expect(bugs.rows.nth(1)).to_contain_text("BUG-20")
    expect(bugs.table).to_contain_text("BUG-14")
    # Generated teammate addresses fit the original Assignee column without an ellipsis.
    clipped = page.evaluate("""() => [...document.querySelectorAll("td[data-label='Assignee']")]
        .filter(cell => cell.scrollWidth > cell.clientWidth).map(cell => cell.textContent)""")
    assert clipped == []

    page.go_back()
    page.get_by_role("link", name="AI QA Bug Triage", exact=True).click()
    expect(page.get_by_role("heading", level=2, name="AI QA Bug Triage", exact=True)).to_be_visible()
    expect(page.get_by_text("Showing 1–10 of 54")).to_be_visible()
    expect(note).to_be_hidden()
    expect(page.locator("#demo-history-note")).to_have_text(HISTORY_NOTE)
    expect(page.locator("#demo-history-note")).to_be_visible()

    # The Demo session is a normal session: it survives reload, and the root page now opens Projects.
    page.reload()
    expect(page.get_by_role("heading", level=2, name="AI QA Bug Triage", exact=True)).to_be_visible()
    page.goto("/")
    expect(page).to_have_url("/projects.html")

    # Following the E-Commerce Demo instructions reaches AI Assist on a Triage bug.
    page.get_by_role("link", name="E-Commerce Demo", exact=True).click()
    triage_row = BugList(page).rows.filter(has=page.locator("td[data-label='Status']", has_text="Triage")).first
    triage_row.get_by_role("link").first.click()
    expect(page.locator("#bug-status-detail")).to_have_text("Triage")
    page.get_by_role("button", name="Edit", exact=True).click()
    expect(page.get_by_role("button", name="AI Assist", exact=True)).to_be_visible()
