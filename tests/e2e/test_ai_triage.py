import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import api_call, bug_path, detail, login, open_bug, seed_bug, unique_name
from tests.e2e.pages import BugForm


# TC-325 | AC-018.2, AC-018.3, AC-020.1, AC-020.2, AC-020.3, AC-020.4, AC-020.7 — New AI review applies only selected suggestions before create
def test_new_ai_review_applies_only_selected_suggestions_before_create(
    page, e2e_api, workspace,
):
    form = BugForm(page)
    login(page, workspace["owner"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()

    ai_requests = []
    page.on(
        "request",
        lambda request: ai_requests.append(request.url)
        if request.url.endswith("/ai-assist") else None,
    )
    page.get_by_role("button", name="New Bug", exact=True).click()

    title = unique_name("AI draft")
    form.title.fill(title)
    form.description.fill("Manual description")
    form.severity.select_option("Minor")
    expect(form.ai_assist).to_be_visible()
    assert ai_requests == []

    form.ai_assist.click()
    expect(form.suggestion("Title")).to_contain_text(f"Reviewed {title}")
    expect(form.title).to_have_value(title)

    form.use_suggestion("Title")
    expect(form.title).to_have_value(f"Reviewed {title}")

    revised = unique_name("Manually revised AI title")
    form.title.fill(revised)
    form.dismiss_suggestion("Description")
    form.use_all()
    expect(form.title).to_have_value(revised)
    expect(form.description).to_have_value("Manual description")
    expect(form.severity).to_have_value("Major")
    assert len(ai_requests) == 1
    collection = f"/projects/{workspace['project']['id']}/bugs"
    assert api_call(e2e_api, "GET", collection, workspace["owner"]) == []

    form.create.click()
    page.get_by_role("link", name="BUG-1", exact=True).click()

    page.reload()
    expect(page.get_by_role("heading", name=revised, exact=True)).to_be_visible()
    expect(detail(page, "Description")).to_have_text("Manual description")
    expect(detail(page, "Priority")).to_have_text("High")


# TC-326 | AC-020.5, AC-020.7, AC-020.8 — Edit AI cancel discards changes then save persists review
def test_edit_ai_cancel_discards_changes_then_save_persists_review(page, e2e_api, workspace):
    bug = seed_bug(e2e_api, workspace, description="Stored description", severity="Minor")
    form = BugForm(page)

    login(page, workspace["qa"])
    open_bug(page, workspace, bug)
    page.get_by_role("button", name="Edit", exact=True).click()

    form.ai_assist.click()
    form.use_suggestion("Title")
    form.dismiss_all()
    expect(form.title).to_have_value(f"Reviewed {bug['title']}")
    expect(form.description).to_have_value("Stored description")

    form.cancel.click()
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]) == bug

    page.get_by_role("button", name="Edit", exact=True).click()
    expect(form.title).to_have_value(bug["title"])
    expect(form.suggestion("Title")).to_have_count(0)

    form.ai_assist.click()
    form.use_all()
    revised = unique_name("Saved reviewed edit")
    form.title.fill(revised)
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]) == bug

    form.save.click()
    expect(page.get_by_role("heading", name=revised, exact=True)).to_be_visible()

    page.reload()
    expect(page.get_by_role("heading", name=revised, exact=True)).to_be_visible()
    expect(detail(page, "Severity")).to_have_text("Major")
    assert api_call(
        e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]
    )["title"] == revised


# TC-327, TC-328 | AC-018.4, AC-019.4, AC-023.1, AC-023.2 — AI failure or empty result preserves manual work and allows retry
@pytest.mark.parametrize(
    "outcome,message",
    [
        ("failure", "AI assistance could not generate suggestions. Please try again."),
        ("empty", "No usable AI suggestions are available."),
    ],
)
def test_ai_failure_or_empty_result_preserves_manual_work_and_allows_retry(
    page, e2e_api, workspace, outcome, message,
):
    form = BugForm(page)
    login(page, workspace["owner"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    page.get_by_role("button", name="New Bug", exact=True).click()

    title = unique_name("Manual continuation")
    form.title.fill(title)
    form.description.fill(f"E2E:{outcome}")
    form.ai_assist.click()

    expect(page.get_by_text(message, exact=outcome == "failure")).to_be_visible()
    expect(form.title).to_have_value(title)
    expect(form.description).to_have_value(f"E2E:{outcome}")
    expect(form.ai_assist).to_be_enabled()
    assert api_call(
        e2e_api, "GET", f"/projects/{workspace['project']['id']}/bugs", workspace["owner"]
    ) == []

    with page.expect_response(
        lambda response: response.url.endswith("/ai-assist") and response.request.method == "POST"
    ) as retry:
        form.ai_assist.click()
    assert retry.value.status == (502 if outcome == "failure" else 200)
    expect(page.get_by_text(message, exact=outcome == "failure")).to_be_visible()

    form.description.fill("Manual recovery details")
    form.create.click()
    page.get_by_role("link", name="BUG-1", exact=True).click()

    expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()
    expect(detail(page, "Description")).to_have_text("Manual recovery details")


# TC-463 | AC-025.5 — Daily AI limit response shows its message, preserves the form and allows manual work and retry
@pytest.mark.parametrize(
    "form_kind,message",
    [
        ("edit", "You have reached your daily AI Assist limit. Try again after 00:00 UTC."),
        ("new", "AI Assist has reached its daily limit for all users. Try again after 00:00 UTC."),
    ],
    ids=["account-limit-edit-bug", "global-limit-new-bug"],
)
def test_ai_daily_limit_preserves_form_and_allows_manual_work_and_retry(
    page, e2e_api, workspace, form_kind, message,
):
    form = BugForm(page)
    collection = f"/projects/{workspace['project']['id']}/bugs"
    if form_kind == "edit":
        bug = seed_bug(e2e_api, workspace, description="Stored description")
        login(page, workspace["qa"])
        open_bug(page, workspace, bug)
        page.get_by_role("button", name="Edit", exact=True).click()
        unchanged = lambda: api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]) == bug
        submit = form.save
    else:
        login(page, workspace["owner"])
        page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
        page.get_by_role("button", name="New Bug", exact=True).click()
        unchanged = lambda: api_call(e2e_api, "GET", collection, workspace["owner"]) == []
        submit = form.create

    title = unique_name("Limit reached")
    form.title.fill(title)
    form.description.fill("Unsaved manual description")

    # Only the AI Assist response is simulated, exactly as the backend returns a reached limit.
    limited = []

    def daily_limit(route):
        if route.request.method != "POST":
            route.fallback()
            return
        limited.append(route.request.post_data_json)
        route.fulfill(status=429, json={"detail": message})

    page.route("**/ai-assist", daily_limit)
    for attempt in (1, 2):  # Retrying is possible but rejected until the limit resets.
        form.ai_assist.click()
        expect(form.ai_assist).to_be_enabled()
        expect(page.get_by_text(message, exact=True)).to_be_visible()
        assert len(limited) == attempt
        assert limited[-1]["title"] == title
        assert limited[-1]["description"] == "Unsaved manual description"
        expect(form.title).to_have_value(title)
        expect(form.description).to_have_value("Unsaved manual description")
        expect(form.suggestion("Title")).to_have_count(0)
        assert unchanged()

    page.unroute("**/ai-assist")  # After the limit resets, the same form can request AI Assist again.
    form.ai_assist.click()
    expect(form.suggestion("Title")).to_contain_text(f"Reviewed {title}")
    form.dismiss_all()
    expect(form.title).to_have_value(title)
    assert unchanged()

    form.description.fill("Manually continued description")
    submit.click()
    if form_kind == "edit":
        expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()
    else:
        page.get_by_role("link", name="BUG-1", exact=True).click()
        [bug] = api_call(e2e_api, "GET", collection, workspace["owner"])
    saved = api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"])
    assert (saved["title"], saved["description"]) == (title, "Manually continued description")
