from playwright.sync_api import expect

from tests.e2e.helpers import api_call, bug_path, login, open_bug, seed_bug


# TC-331 | AC-006.4, AC-009.1, AC-009.2, AC-009.5, AC-009.6 — Owner manages membership and removed user loses access
def test_owner_manages_membership_and_removed_user_loses_access(
    page, e2e_api, workspace, account_factory,
):
    member = account_factory()
    project = workspace["project"]
    added = sorted(
        [account_factory() for _ in range(4)],
        key=lambda account: account["email"], reverse=True,
    )
    # Interleave roles and insert both additional email pairs in descending order.
    for account, role in zip(added, ["QA Analyst", "Developer", "QA Analyst", "Developer"]):
        api_call(
            e2e_api, "POST", f"/projects/{project['id']}/members",
            workspace["owner"], expected=201,
            data={"email": account["email"], "role": role},
        )

    login(page, workspace["owner"])
    page.get_by_role("link", name=project["name"], exact=True).click()
    page.get_by_role("button", name="Show Members").click()

    page.get_by_role("button", name="Add Member", exact=True).click()
    page.get_by_label("Email:", exact=True).fill(member["email"])
    page.get_by_label("Role:", exact=True).select_option("Developer")
    page.get_by_role("button", name="Add", exact=True).click()
    expect(page.get_by_text(member["email"], exact=True)).to_be_visible()

    login(page, member)
    page.get_by_role("link", name=project["name"], exact=True).click()
    expect(page.get_by_role("heading", name=project["name"], exact=True)).to_be_visible()
    page.get_by_role("button", name="Show Members").click()
    expect(page.get_by_role("button", name="Add Member", exact=True)).to_be_hidden()

    qa_emails = sorted([workspace["qa"]["email"], added[0]["email"], added[2]["email"]])
    developer_emails = sorted([
        workspace["developer"]["email"], member["email"], added[1]["email"], added[3]["email"],
    ])
    expected_members = [f"{workspace['owner']['email']} (Project Owner)"]
    expected_members += [f"{email} (QA Analyst)" for email in qa_emails]
    expected_members += [f"{email} (Developer)" for email in developer_emails]

    # Member entries have no named container role; assert their rendered text/order.
    # Each entry's first child holds "email (role)"; any action button follows it.
    expect(page.locator("#members")).to_be_visible()
    expect(page.locator("#members > div > div")).to_have_text(expected_members)
    # The Developer cannot remove anyone and can leave only from their own entry (AC-009.6).
    expect(page.get_by_role("button", name="Remove", exact=True)).to_have_count(0)
    expect(page.get_by_role("button", name="Leave Project", exact=True)).to_have_count(1)
    own_entry = page.locator("#members > div").filter(has=page.get_by_text(member["email"], exact=True))
    expect(own_entry.get_by_role("button", name="Leave Project", exact=True)).to_be_visible()

    login(page, workspace["owner"])
    page.get_by_role("link", name=project["name"], exact=True).click()
    page.get_by_role("button", name="Show Members").click()
    # Dynamically rendered member entries have no named container role.
    member_entry = page.locator("#members > div").filter(
        has=page.get_by_text(member["email"], exact=True)
    )
    page.once("dialog", lambda dialog: dialog.accept())
    member_entry.get_by_role("button", name="Remove", exact=True).click()
    expect(page.get_by_text(member["email"], exact=True)).to_have_count(0)

    login(page, member)
    expect(page.get_by_role("link", name=project["name"], exact=True)).to_have_count(0)
    page.goto(f"/project.html?id={project['id']}")
    expect(page).to_have_url("/projects.html")
    expect(page.get_by_role("link", name=project["name"], exact=True)).to_have_count(0)
    api_call(e2e_api, "GET", f"/projects/{project['id']}", member, expected=404)


# TC-332 | AC-012.3, AC-014.2, AC-022.1 — Developer cannot delete or request AI and outsider cannot open bug
def test_developer_cannot_delete_or_request_ai_and_outsider_cannot_open_bug(
    page, e2e_api, workspace, account_factory,
):
    bug = seed_bug(e2e_api, workspace)

    login(page, workspace["developer"])
    expect(page.get_by_role("link", name=workspace["project"]["name"], exact=True)).to_be_visible()
    expect(
        page.get_by_role("button", name=f"Edit project {workspace['project']['name']}")
    ).to_have_count(0)

    open_bug(page, workspace, bug)
    page.get_by_role("button", name="Edit", exact=True).click()
    expect(page.get_by_role("button", name="Delete", exact=True)).to_be_hidden()
    expect(page.get_by_role("button", name="AI Assist", exact=True)).to_be_hidden()

    api_call(e2e_api, "DELETE", bug_path(workspace, bug), workspace["developer"], expected=403)
    snapshot = {
        field: bug.get(field) or "" for field in (
            "title", "affected_version", "environment", "description", "steps_to_reproduce",
            "expected_result", "actual_result", "severity", "priority",
        )
    } | {"assignee_id": bug["assignee_id"]}
    api_call(
        e2e_api, "POST", bug_path(workspace, bug) + "/ai-assist", workspace["developer"],
        expected=403, data=snapshot,
    )
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]) == bug

    outsider = account_factory()
    login(page, outsider)
    page.goto(f"/bugs.html?project_id={workspace['project']['id']}&bug_number={bug['bug_number']}")
    expect(page).to_have_url("/projects.html")
    expect(page.get_by_role("heading", name=bug["title"], exact=True)).to_have_count(0)
    api_call(e2e_api, "GET", bug_path(workspace, bug), outsider, expected=404)
