import re
from uuid import uuid4

from playwright.sync_api import expect


def unique_name(prefix):
    return f"{prefix}-{uuid4().hex[:12]}"


def api_call(api, method, path, account=None, expected=200, **kwargs):
    headers = {"Authorization": f"Bearer {account['token']}"} if account else {}
    response = api.fetch(path, method=method, headers=headers, **kwargs)
    assert response.status == expected, f"{method} {path}: {response.status} {response.text()}"
    return response.json() if expected != 204 else None


def login(page, account):
    if page.url != "about:blank" and page.evaluate("localStorage.getItem('access_token')"):
        page.get_by_role("button", name="Logout", exact=True).click()
        expect(page).to_have_url("/login.html")

    page.goto("/login.html")
    page.get_by_label("Email:", exact=True).fill(account["email"])
    page.get_by_label("Password:", exact=True).fill(account["password"])
    page.get_by_role("button", name="Login", exact=True).click()
    expect(page).to_have_url("/projects.html")


def seed_bug(api, workspace, **fields):
    return api_call(
        api, "POST", f"/projects/{workspace['project']['id']}/bugs",
        workspace["owner"], expected=201,
        data={"title": unique_name("Synthetic bug")} | fields,
    )


def bug_path(workspace, bug):
    return f"/projects/{workspace['project']['id']}/bugs/{bug['bug_number']}"


def open_bug(page, workspace, bug):
    page.goto(f"/bugs.html?project_id={workspace['project']['id']}&bug_number={bug['bug_number']}")
    expect(page.get_by_role("heading", name=bug["title"], exact=True)).to_be_visible()


def detail(page, label):
    # Values have no standalone accessible name: use their semantic definition-list term.
    term = page.get_by_role("term").filter(has_text=re.compile(f"^{re.escape(label)}$"))
    return page.locator("dl > div").filter(has=term).get_by_role("definition")
