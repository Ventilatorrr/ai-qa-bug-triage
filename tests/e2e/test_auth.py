from uuid import uuid4

from playwright.sync_api import Page, expect

from tests.e2e.helpers import login


# TC-329 | AC-001.1, AC-002.1, AC-003.1, AC-003.2, AC-004.1, AC-004.2 — Registration login logout
def test_registration_login_logout(page: Page, e2e_base_url):
    email = f"e2e-{uuid4().hex}@example.com"
    password = "TestPassword123!"

    page.goto(f"{e2e_base_url}/register.html")

    page.get_by_label("Email:", exact=True).fill(email)
    page.get_by_label("Password:", exact=True).fill(password)
    page.get_by_role("button", name="Register", exact=True).click()

    expect(page).to_have_url(f"{e2e_base_url}/login.html")

    page.get_by_label("Email:", exact=True).fill(email)
    page.get_by_label("Password:", exact=True).fill(password)
    page.get_by_role("button", name="Login", exact=True).click()

    expect(page).to_have_url(f"{e2e_base_url}/projects.html")
    expect(page.get_by_role("button", name="Logout")).to_be_visible()

    page.get_by_role("button", name="Logout").click()

    expect(page).to_have_url(f"{e2e_base_url}/login.html")
    assert page.evaluate("localStorage.getItem('access_token')") is None

    page.goto(f"{e2e_base_url}/projects.html")
    expect(page).to_have_url(f"{e2e_base_url}/login.html")


# TC-330 | AC-002.2 — Invalid login feedback allows correction
def test_invalid_login_feedback_allows_correction(page, account_factory):
    account = account_factory()

    page.goto("/login.html")
    page.get_by_label("Email:", exact=True).fill(account["email"])
    page.get_by_label("Password:", exact=True).fill("WrongPassword123!")
    page.get_by_role("button", name="Login", exact=True).click()

    expect(page.get_by_role("alert")).to_have_text("Invalid email or password.")
    expect(page).to_have_url("/login.html")
    assert page.evaluate("localStorage.getItem('access_token')") is None

    login(page, account)
    page.reload()
    expect(page.get_by_role("heading", name="My Projects")).to_be_visible()
