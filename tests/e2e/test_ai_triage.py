import pytest
from playwright.sync_api import expect

from tests.e2e.helpers import api_call, bug_path, detail, login, open_bug, seed_bug, unique_name


def test_new_ai_review_applies_only_selected_suggestions_before_create(
    page, e2e_api, workspace,
):
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
    page.get_by_label("Title:", exact=True).fill(title)
    page.get_by_label("Description:", exact=True).fill("Manual description")
    page.get_by_label("Severity:", exact=True).select_option("Minor")
    expect(page.get_by_role("button", name="AI Assist", exact=True)).to_be_visible()
    assert ai_requests == []

    page.get_by_role("button", name="AI Assist", exact=True).click()
    expect(page.get_by_role("article", name="AI suggestion: Title", exact=True)).to_contain_text(
        f"Reviewed {title}"
    )
    expect(page.get_by_label("Title:", exact=True)).to_have_value(title)

    page.get_by_role("button", name="Use Title suggestion", exact=True).click()
    expect(page.get_by_label("Title:", exact=True)).to_have_value(f"Reviewed {title}")

    revised = unique_name("Manually revised AI title")
    page.get_by_label("Title:", exact=True).fill(revised)
    page.get_by_role("button", name="Dismiss Description suggestion", exact=True).click()
    page.get_by_role("button", name="Use All", exact=True).click()
    expect(page.get_by_label("Title:", exact=True)).to_have_value(revised)
    expect(page.get_by_label("Description:", exact=True)).to_have_value("Manual description")
    expect(page.get_by_label("Severity:", exact=True)).to_have_value("Major")
    assert len(ai_requests) == 1
    collection = f"/projects/{workspace['project']['id']}/bugs"
    assert api_call(e2e_api, "GET", collection, workspace["owner"]) == []

    page.get_by_role("button", name="Create", exact=True).click()
    page.get_by_role("link", name="BUG-1", exact=True).click()

    page.reload()
    expect(page.get_by_role("heading", name=revised, exact=True)).to_be_visible()
    expect(detail(page, "Description")).to_have_text("Manual description")
    expect(detail(page, "Priority")).to_have_text("High")


def test_edit_ai_cancel_discards_changes_then_save_persists_review(page, e2e_api, workspace):
    bug = seed_bug(e2e_api, workspace, description="Stored description", severity="Minor")

    login(page, workspace["qa"])
    open_bug(page, workspace, bug)
    page.get_by_role("button", name="Edit", exact=True).click()

    page.get_by_role("button", name="AI Assist", exact=True).click()
    page.get_by_role("button", name="Use Title suggestion", exact=True).click()
    page.get_by_role("button", name="Dismiss All", exact=True).click()
    expect(page.get_by_label("Title:", exact=True)).to_have_value(f"Reviewed {bug['title']}")
    expect(page.get_by_label("Description:", exact=True)).to_have_value("Stored description")

    page.get_by_role("button", name="Cancel", exact=True).click()
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]) == bug

    page.get_by_role("button", name="Edit", exact=True).click()
    expect(page.get_by_label("Title:", exact=True)).to_have_value(bug["title"])
    expect(page.get_by_role("article", name="AI suggestion: Title", exact=True)).to_have_count(0)

    page.get_by_role("button", name="AI Assist", exact=True).click()
    page.get_by_role("button", name="Use All", exact=True).click()
    revised = unique_name("Saved reviewed edit")
    page.get_by_label("Title:", exact=True).fill(revised)
    assert api_call(e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]) == bug

    page.get_by_role("button", name="Save", exact=True).click()
    expect(page.get_by_role("heading", name=revised, exact=True)).to_be_visible()

    page.reload()
    expect(page.get_by_role("heading", name=revised, exact=True)).to_be_visible()
    expect(detail(page, "Severity")).to_have_text("Major")
    assert api_call(
        e2e_api, "GET", bug_path(workspace, bug), workspace["owner"]
    )["title"] == revised


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
    login(page, workspace["owner"])
    page.get_by_role("link", name=workspace["project"]["name"], exact=True).click()
    page.get_by_role("button", name="New Bug", exact=True).click()

    title = unique_name("Manual continuation")
    page.get_by_label("Title:", exact=True).fill(title)
    page.get_by_label("Description:", exact=True).fill(f"E2E:{outcome}")
    page.get_by_role("button", name="AI Assist", exact=True).click()

    expect(page.get_by_text(message, exact=outcome == "failure")).to_be_visible()
    expect(page.get_by_label("Title:", exact=True)).to_have_value(title)
    expect(page.get_by_label("Description:", exact=True)).to_have_value(f"E2E:{outcome}")
    expect(page.get_by_role("button", name="AI Assist", exact=True)).to_be_enabled()
    assert api_call(
        e2e_api, "GET", f"/projects/{workspace['project']['id']}/bugs", workspace["owner"]
    ) == []

    with page.expect_response(
        lambda response: response.url.endswith("/ai-assist") and response.request.method == "POST"
    ) as retry:
        page.get_by_role("button", name="AI Assist", exact=True).click()
    assert retry.value.status == (502 if outcome == "failure" else 200)
    expect(page.get_by_text(message, exact=outcome == "failure")).to_be_visible()

    page.get_by_label("Description:", exact=True).fill("Manual recovery details")
    page.get_by_role("button", name="Create", exact=True).click()
    page.get_by_role("link", name="BUG-1", exact=True).click()

    expect(page.get_by_role("heading", name=title, exact=True)).to_be_visible()
    expect(detail(page, "Description")).to_have_text("Manual recovery details")
