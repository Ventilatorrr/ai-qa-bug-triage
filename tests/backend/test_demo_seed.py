from datetime import datetime
import json
from pathlib import Path
import re

import pytest

from app.schemas import BugCreate


SEED_PATH = Path(__file__).resolve().parents[2] / "app" / "demo_data" / "demo_ecommerce.json"
GENUINE_PATH = SEED_PATH.with_name("ai_qa_bug_triage.json")
TEAM = {"owner": "Project Owner", "qa1": "QA Analyst", "qa2": "QA Analyst", "dev1": "Developer", "dev2": "Developer"}
CONTENT_FIELDS = (
    "title", "affected_version", "environment", "description", "steps_to_reproduce",
    "expected_result", "actual_result", "severity", "priority",
)
BUG_KEYS = {
    "number", *CONTENT_FIELDS, "status", "resolution", "fix_version", "assignee", "created_by",
    "created_at", "updated_at",
}


@pytest.fixture(scope="module")
def seed():
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def genuine():
    return json.loads(GENUINE_PATH.read_text(encoding="utf-8"))


def lifecycle_path(bug, user_id):
    """Existing status transitions, performed by the Project Owner, that reach the seeded state."""
    status, resolution = bug["status"], bug["resolution"]
    if status == "Triage":
        return []
    path = [{"status": "Open"}]
    if status == "Open":
        return path
    path.append({"status": "Development"})
    if status == "Development":
        return path
    if status == "Closed" and resolution != "Fixed":
        return path + [{"status": "Closed", "resolution": resolution}]
    path.append({"status": "Testing", "assignee_id": user_id(bug["assignee"])})
    if status == "Testing":
        return path
    return path + [{"status": "Closed", "testing_outcome": "Passed", "fix_version": bug["fix_version"]}]


# TC-438 | AC-024.3, AC-024.5 — E-Commerce seed has twenty well-formed bugs with valid values
def test_ecommerce_seed_has_twenty_well_formed_bugs(seed):
    assert seed["project"] == "E-Commerce Demo"
    assert seed["team"] == TEAM
    bugs = seed["bugs"]
    assert len(bugs) == 20
    assert [bug["number"] for bug in bugs] == list(range(1, 21))
    for bug in bugs:
        number = bug["number"]
        assert BUG_KEYS <= set(bug) <= BUG_KEYS | {"intentional_issues"}, number
        BugCreate(**{field: bug[field] for field in CONTENT_FIELDS})  # Existing field validation.
        assert bug["title"] == bug["title"].strip(), number
        assert all(bug[field] is None or len(bug[field]) <= 20 for field in ("affected_version", "fix_version")), number
        assert bug["created_by"] in seed["team"], number
        assert bug["assignee"] is None or seed["team"][bug["assignee"]] in ("QA Analyst", "Developer"), number
        created, updated = (datetime.fromisoformat(bug[field]) for field in ("created_at", "updated_at"))
        assert created.tzinfo and created <= updated, number
        assert (created.year, created.month, updated.year, updated.month) == (2026, 10, 2026, 10), number
    created = [bug["created_at"] for bug in bugs]
    assert created == sorted(created)  # Bug numbers follow reporting order.
    # Version chronology: every 2.3.0 report precedes 2.3.1 reports, which precede 2.4.0 reports.
    by_version = [[bug["created_at"] for bug in bugs if bug["affected_version"] == version] for version in ("2.3.0", "2.3.1", "2.4.0")]
    assert all(max(earlier) < min(later) for earlier, later in zip(by_version, by_version[1:]))
    # The newest report is also the most recently updated; the same-day Autumn Sale fix stays on 20 October.
    latest = max(bugs, key=lambda bug: bug["updated_at"])
    assert latest["number"] == 20 and latest["created_at"][:10] == latest["updated_at"][:10] == "2026-10-27"
    assert bugs[13]["created_at"][:10] == bugs[13]["updated_at"][:10] == "2026-10-20"


# TC-439 | AC-024.3 — E-Commerce seed covers a realistic workflow with intentional Triage examples
def test_ecommerce_seed_covers_realistic_workflow_with_intentional_triage_examples(seed):
    bugs = seed["bugs"]
    assert {bug["status"] for bug in bugs} == {"Triage", "Open", "Development", "Testing", "Closed"}
    assert {bug["assignee"] for bug in bugs} == {"qa1", "qa2", "dev1", "dev2", None}
    resolutions = {bug["resolution"] for bug in bugs if bug["status"] == "Closed"}
    assert "Fixed" in resolutions and resolutions - {"Fixed"}
    for field in ("severity", "priority"):
        assert len({bug[field] for bug in bugs} - {None}) > 1
    imperfect = [bug for bug in bugs if "intentional_issues" in bug]
    assert len(imperfect) >= 2
    for bug in imperfect:
        assert bug["status"] == "Triage", bug["number"]
        assert bug["intentional_issues"] and all(issue.strip() for issue in bug["intentional_issues"]), bug["number"]
    # The remaining reports are complete examples of good QA documentation.
    for bug in bugs:
        if bug not in imperfect:
            assert all(bug[field] for field in CONTENT_FIELDS), bug["number"]


# TC-440 | AC-024.3, AC-024.5 — E-Commerce seed bugs are reachable through the existing lifecycle API
def test_ecommerce_seed_bugs_are_reachable_through_existing_lifecycle_api(
    seed, test_client, authenticated_user_factory, project_factory, member_factory,
):
    team = {ref: authenticated_user_factory(email=f"{ref}@example.com") for ref in seed["team"]}
    owner = team["owner"]
    project = project_factory(owner["token"], name=seed["project"])
    for ref, role in seed["team"].items():
        if role != "Project Owner":
            member_factory(owner["token"], project["id"], team[ref]["user"]["email"], role)

    def user_id(ref):
        return None if ref is None else team[ref]["user_id"]

    base = f"/projects/{project['id']}/bugs"
    as_owner = {"Authorization": f"Bearer {owner['token']}"}
    for bug in seed["bugs"]:
        # Developer work precedes Testing; the seed records only the final assignee.
        first_assignee = "dev1" if bug["status"] == "Testing" or bug["resolution"] == "Fixed" else bug["assignee"]
        response = test_client.post(
            base, headers={"Authorization": f"Bearer {team[bug['created_by']]['token']}"},
            json={field: bug[field] for field in CONTENT_FIELDS} | {"assignee_id": user_id(first_assignee)},
        )
        assert response.status_code == 201, (bug["number"], response.text)
        assert response.json()["bug_number"] == bug["number"]
        for update in lifecycle_path(bug, user_id):
            response = test_client.patch(f"{base}/{bug['number']}/status", headers=as_owner, json=update)
            assert response.status_code == 200, (bug["number"], update, response.text)
        stored = test_client.get(f"{base}/{bug['number']}", headers=as_owner).json()
        expected = {field: bug[field] for field in CONTENT_FIELDS} | {
            "status": bug["status"], "resolution": bug["resolution"], "fix_version": bug["fix_version"],
            "assignee_id": user_id(bug["assignee"]), "created_by": user_id(bug["created_by"]),
        }
        assert {field: stored[field] for field in expected} == expected, bug["number"]


# TC-458 | AC-019.2, AC-024.3 — Fictional BUG-19 reference reaches BUG-13 metadata through project-local history numbers
def test_ecommerce_related_report_reaches_ai_context(
    seed, test_client, test_database, authenticated_user_factory, project_factory, monkeypatch,
):
    from contextlib import closing

    from app import ai_triage, database
    from app.ai_generation import build_generation_input
    from app.ai_suggestions import SuggestionResult
    from app.api.demo import insert_seeded_project

    assert database.DATABASE_NAME == str(test_database)
    team = {ref: authenticated_user_factory(email=f"{ref}@example.com") for ref in seed["team"]}
    headers = {"Authorization": f"Bearer {team['owner']['token']}"}
    other = project_factory(team["owner"]["token"], name="Unrelated fictional project")
    assert test_client.post(
        f"/projects/{other['id']}/bugs", headers=headers, json={"title": "Unrelated fictional report"},
    ).status_code == 201  # Make database IDs differ from the local report numbers.
    with closing(database.get_connection()) as conn:
        insert_seeded_project(conn, seed, {ref: user["user_id"] for ref, user in team.items()})
        project_id = conn.execute("SELECT id FROM projects WHERE name=?", (seed["project"],)).fetchone()[0]
        bug_ids = dict(conn.execute("SELECT bug_number, id FROM bugs WHERE project_id=?", (project_id,)))
        conn.commit()

    captured = []

    def capture(context, **kwargs):
        captured.append(build_generation_input(context)["context"])
        return SuggestionResult({})

    monkeypatch.setattr(ai_triage, "request_suggestions", capture)
    current = next(bug for bug in seed["bugs"] if bug["number"] == 19)
    form = {field: current[field] or "" for field in CONTENT_FIELDS}
    form["assignee_id"] = None
    response = test_client.post(
        f"/projects/{project_id}/bugs/19/ai-assist", headers=headers, json=form,
    )
    assert response.status_code == 200
    context = captured[0]
    assert context["current_form"] == form
    assert form["affected_version"] == form["environment"] == form["severity"] == form["priority"] == ""
    assert [bug["id"] for bug in context["recent_bugs"]] == [bug_ids[n] for n in (20, 10, 13, 12, 11)]
    assert [bug["bug_number"] for bug in context["recent_bugs"]] == [20, 10, 13, 12, 11]
    related = next(bug for bug in context["recent_bugs"] if bug["bug_number"] == 13)
    assert related["id"] != related["bug_number"]
    assert form["description"] == "Price low to high puts some expensive things first. Saw this while testing the filters problem in bug 13."
    assert related["affected_version"] == "2.4.0"
    assert related["environment"] == "Production, Safari, iOS 26, iPhone 17"


def required_assignee_role(bug):
    """Assignee role that a bug's final state requires under the existing lifecycle rules."""
    if bug["status"] == "Development" or (bug["status"] == "Closed" and bug["resolution"] != "Fixed"):
        return "Developer"
    if bug["status"] == "Testing" or (bug["status"] == "Closed" and bug["resolution"] == "Fixed"):
        return "QA Analyst"
    return None


# TC-441 | AC-024.4, AC-024.5 — Genuine snapshot keeps valid numbered bugs, original timestamps and lifecycle values
def test_genuine_snapshot_keeps_valid_numbered_bugs_and_original_timestamps(genuine):
    assert genuine["project"] == "AI QA Bug Triage"
    assert genuine["team"] == TEAM
    bugs = genuine["bugs"]
    numbers = [bug["number"] for bug in bugs]
    assert len(bugs) == genuine["snapshot"]["bug_count"] > 0
    assert numbers == sorted(set(numbers)) and numbers[0] >= 1  # Unique original numbers; gaps are allowed.
    for bug in bugs:
        number = bug["number"]
        assert set(bug) == BUG_KEYS, number
        BugCreate(**{field: bug[field] for field in CONTENT_FIELDS})  # Existing field validation.
        assert all(bug[field] is None or len(bug[field]) <= 20 for field in ("affected_version", "fix_version")), number
        created, updated = (datetime.fromisoformat(bug[field]) for field in ("created_at", "updated_at"))
        assert created.tzinfo and updated.tzinfo and created <= updated, number
        assert bug["status"] in {"Triage", "Open", "Development", "Testing", "Closed"}, number
        if bug["status"] == "Closed":
            assert bug["resolution"] in {"Fixed", "Won't Fix", "Duplicate", "Cannot Reproduce", "Not a Bug"}, number
        else:
            assert bug["resolution"] is None, number
        assert bug["fix_version"] is None or bug["resolution"] == "Fixed", number
        assert bug["created_by"] in TEAM, number
        if bug["assignee"] is not None:
            role = TEAM[bug["assignee"]]
            assert role in {"QA Analyst", "Developer"} and required_assignee_role(bug) in {None, role}, number


# TC-442 | AC-024.4 — Genuine snapshot contains no obvious private emails, credentials or local user paths
def test_genuine_snapshot_contains_no_obvious_private_data(genuine):
    private_patterns = {
        "local user path": re.compile(r"(?i)\\Users\\|(?<![\w.])/(?:home|Users)/"),
        "API key": re.compile(r"\bsk-[\w-]{8,}"),
        "JWT": re.compile(r"\beyJ[\w-]{8,}\.[\w-]{8,}"),
        "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        "password value": re.compile(r"(?i)\bpassword\s*[:=]\s*\S+"),
    }
    # Example addresses in reproduction steps are allowed only on reserved example domains.
    reserved_domain = re.compile(r"(?i)^(?:[\w-]+\.)*(?:example(?:\.(?:com|net|org))?|test|invalid|localhost)$")
    for bug in genuine["bugs"]:
        text = "\n".join(bug[field] or "" for field in CONTENT_FIELDS if field not in ("severity", "priority"))
        for category, pattern in private_patterns.items():
            assert not pattern.search(text), (bug["number"], category)
        for email in re.findall(r"[\w.%+-]+@([\w-]+(?:\.[\w-]+)+)", text):
            assert reserved_domain.match(email), (bug["number"], "email domain")
