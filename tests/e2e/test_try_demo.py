from playwright.sync_api import Page, expect

from tests.e2e.pages import BugList


DEMO_NOTE = (
    "Some bug reports in Triage intentionally contain incomplete information, unclear wording, or questionable "
    "classifications. AI Assist can help identify potential improvements to these reports."
)
HISTORY_NOTE = (
    "This project showcases the testing and quality assurance work behind AI QA Bug Triage. "
    "It contains genuine reports of defects discovered during development."
)


# TC-453 | AC-024.1, AC-024.3, AC-024.4, AC-024.6, AC-012.4 — Try Demo opens both seeded projects with their introductions
def test_try_demo_opens_seeded_projects_with_demo_note(page: Page):
    page.goto("/")
    expect(page).to_have_url("/login.html")  # The root page goes straight to Login without a session.
    expect(page.get_by_text("Demo work won't be accessible after logout or session expiry.")).to_be_visible()
    page.get_by_role("button", name="Try Demo", exact=True).click()

    expect(page).to_have_url("/projects.html")
    expect(page.get_by_role("link", name="E-Commerce Demo", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="AI QA Bug Triage", exact=True)).to_be_visible()

    note = page.locator("#demo-note")
    page.get_by_role("link", name="E-Commerce Demo", exact=True).click()
    expect(page.get_by_role("heading", level=2, name="E-Commerce Demo", exact=True)).to_be_visible()
    expect(note).to_be_visible()
    expect(note).to_have_text(DEMO_NOTE)
    expect(page.locator("#demo-history-note")).to_be_hidden()
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
    expect(page.get_by_text("Showing 1–10 of 41")).to_be_visible()
    expect(note).to_be_hidden()
    expect(page.locator("#demo-history-note")).to_have_text(HISTORY_NOTE)
    expect(page.locator("#demo-history-note")).to_be_visible()

    # The Demo session is a normal session: it survives reload, and the root page now opens Projects.
    page.reload()
    expect(page.get_by_role("heading", level=2, name="AI QA Bug Triage", exact=True)).to_be_visible()
    page.goto("/")
    expect(page).to_have_url("/projects.html")
