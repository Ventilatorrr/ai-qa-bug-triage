from contextlib import closing
from datetime import datetime, timedelta, timezone
import re
import sqlite3

from fastapi.testclient import TestClient
import pytest

from app.api.demo import SEEDED_FIELDS, load_seeds
from tests.backend.test_ai_assist import blank_form
from tests.backend.test_ai_triage import offline_provider
from tests.backend.test_ai_usage import GLOBAL_LIMIT_MESSAGE, USER_LIMIT_MESSAGE


SEEDS = {seed["project"]: seed for seed in load_seeds()}
EMAIL = re.compile(r"^(o|q1|q2|d1|d2)([a-z0-9]{5})@example\.com$")
ROLE_BY_PREFIX = {"o": "owner", "q1": "qa1", "q2": "qa2", "d1": "dev1", "d2": "dev2"}
FAILURE_MESSAGE = "The Demo could not be created. Please try again."


def start_demo(client):
    response = client.post("/demo")
    assert response.status_code == 201, response.text
    # The visitor receives only their own token; teammate credentials are never returned.
    assert set(response.json()) == {"access_token", "token_type"}
    assert response.json()["token_type"] == "bearer"
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def demo_projects(client, headers):
    response = client.get("/projects", headers=headers)
    assert response.status_code == 200
    return {project["name"]: project["id"] for project in response.json()}


def team_refs(client, headers, project_id):
    """Map each member's user ID to its Demo role reference, read from the generated email."""
    response = client.get(f"/projects/{project_id}/members", headers=headers)
    assert response.status_code == 200
    return {member["user_id"]: member for member in response.json()}


def table_counts(test_database):
    from app import database

    assert database.DATABASE_NAME == str(test_database)
    with closing(database.get_connection()) as connection:
        return {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                for table in ("users", "projects", "project_members", "bugs")}


# TC-443 | AC-024.1, AC-024.2, AC-024.3, AC-024.4, AC-024.5 — Demo creates the team, both projects and seeded bugs
def test_demo_creates_team_projects_and_seeded_bugs(test_client):
    before = datetime.now(timezone.utc)
    headers = start_demo(test_client)
    after = datetime.now(timezone.utc)
    owner_id = test_client.get("/protected", headers=headers).json()["user_id"]
    projects = demo_projects(test_client, headers)
    assert set(projects) == set(SEEDS) == {"Demo E-Commerce Platform", "AI QA Bug Triage"}
    teams = []
    for name, project_id in projects.items():
        seed = SEEDS[name]
        members = team_refs(test_client, headers, project_id)
        matches = {user_id: EMAIL.match(member["email"]) for user_id, member in members.items()}
        assert all(matches.values()), [member["email"] for member in members.values()]
        assert len({match.group(2) for match in matches.values()}) == 1  # One suffix per Demo.
        ids = {ROLE_BY_PREFIX[match.group(1)]: user_id for user_id, match in matches.items()}
        assert set(ids) == set(seed["team"]) and ids["owner"] == owner_id
        assert all(members[ids[ref]]["role"] == role for ref, role in seed["team"].items())
        teams.append(sorted(members))
        listed = test_client.get(f"/projects/{project_id}/bugs", headers=headers).json()
        assert sorted(bug["bug_number"] for bug in listed) == [bug["number"] for bug in seed["bugs"]]
        for bug in seed["bugs"]:
            stored = test_client.get(f"/projects/{project_id}/bugs/{bug['number']}", headers=headers).json()
            expected = {field: bug[field] for field in SEEDED_FIELDS} | {
                "assignee_id": ids.get(bug["assignee"]), "created_by": ids[bug["created_by"]],
            }
            assert {field: stored[field] for field in expected} == expected, (name, bug["number"])
            if "created_at" in bug:
                assert (stored["created_at"], stored["updated_at"]) == (bug["created_at"], bug["updated_at"])
            else:
                for field, days in (("created_at", bug["created_days_ago"]), ("updated_at", bug["updated_days_ago"])):
                    stamp = datetime.fromisoformat(stored[field])
                    assert before - timedelta(days=days) <= stamp <= after - timedelta(days=days), (name, bug["number"])
    assert teams[0] == teams[1]  # The same five accounts belong to both projects.


# TC-444 | AC-024.5 — Demo bug numbering continues after the highest seeded number and passes startup checks
def test_demo_numbering_continues_after_highest_seeded_number(test_client):
    from app.main import app

    headers = start_demo(test_client)
    projects = demo_projects(test_client, headers)
    for name, seed in SEEDS.items():
        response = test_client.post(f"/projects/{projects[name]}/bugs", headers=headers, json={"title": "Visitor report"})
        assert response.status_code == 201
        assert response.json()["bug_number"] == max(bug["number"] for bug in seed["bugs"]) + 1
    # Restarting reruns the schema, relationship and counter integrity checks on the seeded data.
    with TestClient(app) as restarted:
        assert restarted.get("/projects", headers=headers).status_code == 200


# TC-445 | AC-024.2, AC-024.6 — Demo owner uses existing workflows and permissions on seeded data
def test_demo_owner_uses_existing_workflows_on_seeded_data(test_client):
    headers = start_demo(test_client)
    projects = demo_projects(test_client, headers)
    shop, genuine = projects["Demo E-Commerce Platform"], projects["AI QA Bug Triage"]
    response = test_client.patch(f"/projects/{shop}/bugs/6/status", headers=headers, json={"status": "Development"})
    assert response.status_code == 200 and response.json()["status"] == "Development"
    response = test_client.patch(f"/projects/{genuine}/bugs/1/status", headers=headers, json={"status": "Triage"})
    assert response.status_code == 200
    assert (response.json()["status"], response.json()["resolution"], response.json()["fix_version"]) == ("Triage", None, None)
    response = test_client.patch(f"/projects/{shop}/bugs/16", headers=headers, json={"title": "Edited by the visitor"})
    assert response.status_code == 200 and response.json()["title"] == "Edited by the visitor"
    assert test_client.delete(f"/projects/{shop}/bugs/16", headers=headers).status_code == 204
    # Generated addresses satisfy the existing email rules: a removed teammate can be added again.
    qa2 = next(member for member in team_refs(test_client, headers, shop).values() if member["email"].startswith("q2"))
    assert test_client.delete(f"/projects/{shop}/members/{qa2['user_id']}", headers=headers).status_code == 200
    response = test_client.post(
        f"/projects/{shop}/members", headers=headers, json={"email": qa2["email"], "role": "QA Analyst"},
    )
    assert response.status_code == 201
    assert test_client.get("/projects", headers={}).status_code == 401


# TC-446 | AC-024.7 — Demo environments are independent and later Demos receive unmodified seed data
def test_demo_environments_are_independent(test_client):
    first, second = start_demo(test_client), start_demo(test_client)
    first_projects, second_projects = demo_projects(test_client, first), demo_projects(test_client, second)
    assert set(first_projects.values()).isdisjoint(second_projects.values())
    first_team = team_refs(test_client, first, first_projects["AI QA Bug Triage"])
    second_team = team_refs(test_client, second, second_projects["AI QA Bug Triage"])
    assert set(first_team).isdisjoint(second_team)
    for project_id in second_projects.values():
        assert test_client.get(f"/projects/{project_id}", headers=first).status_code == 404
        assert test_client.get(f"/projects/{project_id}/bugs/1", headers=first).status_code == 404
    shop, genuine = first_projects["Demo E-Commerce Platform"], first_projects["AI QA Bug Triage"]
    assert test_client.patch(f"/projects/{shop}/bugs/1", headers=first, json={"title": "Changed in first Demo"}).status_code == 200
    last = SEEDS["AI QA Bug Triage"]["bugs"][-1]["number"]
    assert test_client.delete(f"/projects/{genuine}/bugs/{last}", headers=first).status_code == 204
    third = start_demo(test_client)
    for headers in (second, third):
        projects = demo_projects(test_client, headers)
        response = test_client.get(f"/projects/{projects['Demo E-Commerce Platform']}/bugs/1", headers=headers)
        assert response.json()["title"] == SEEDS["Demo E-Commerce Platform"]["bugs"][0]["title"]
        assert test_client.get(f"/projects/{projects['AI QA Bug Triage']}/bugs/{last}", headers=headers).status_code == 200


# TC-447 | AC-024.8 — Demo creation failure rolls back every account, project, membership and bug
@pytest.mark.parametrize("failure", ["second_project", "token"])
def test_demo_creation_failure_rolls_back_everything(test_client, test_database, monkeypatch, failure):
    from app.api import demo

    start_demo(test_client)
    before = table_counts(test_database)
    with monkeypatch.context() as patch:
        if failure == "second_project":
            original, inserted = demo.insert_seeded_project, []

            def fail_on_second(conn, seed, user_ids, now):
                if inserted:
                    raise sqlite3.IntegrityError("Injected seed failure")
                inserted.append(seed["project"])
                return original(conn, seed, user_ids, now)

            patch.setattr(demo, "insert_seeded_project", fail_on_second)
        else:
            def fail_token(user_id):
                raise RuntimeError("Injected token failure")

            patch.setattr(demo, "create_access_token", fail_token)
        response = test_client.post("/demo")
    assert response.status_code == 500
    assert response.json() == {"detail": FAILURE_MESSAGE}
    assert table_counts(test_database) == before
    start_demo(test_client)  # The visitor can try again.


# TC-448 | AC-024.2 — Demo creation retries when a generated email address is already registered
def test_demo_retries_when_generated_email_is_taken(test_client, user_factory, monkeypatch):
    from app.api import demo

    user_factory(email="q2taken@example.com", password="Password1")
    suffixes = iter(["taken", "fresh"])
    monkeypatch.setattr(demo, "new_suffix", lambda: next(suffixes))
    headers = start_demo(test_client)
    project_id = demo_projects(test_client, headers)["AI QA Bug Triage"]
    emails = {member["email"] for member in team_refs(test_client, headers, project_id).values()}
    assert emails == {f"{prefix}fresh@example.com" for prefix in ROLE_BY_PREFIX}
    response = test_client.post("/login", json={"email": "q2taken@example.com", "password": "Password1"})
    assert response.status_code == 200  # The existing account is untouched.


# TC-449 | AC-025.1, AC-025.2, AC-024.6 — Demo accounts share the regular AI usage limits
def test_demo_accounts_share_regular_ai_usage_limits(
    test_client, offline_provider, blank_form, authenticated_user_factory, project_factory, monkeypatch,
):
    monkeypatch.setenv("AI_DAILY_USER_LIMIT", "1")
    monkeypatch.setenv("AI_DAILY_GLOBAL_LIMIT", "2")

    def triage_url(headers):
        return f"/projects/{demo_projects(test_client, headers)['Demo E-Commerce Platform']}/bugs/17/ai-assist"

    demo_owner = start_demo(test_client)
    assert test_client.post(triage_url(demo_owner), headers=demo_owner, json=blank_form).status_code == 200
    response = test_client.post(triage_url(demo_owner), headers=demo_owner, json=blank_form)
    assert response.status_code == 429 and response.json() == {"detail": USER_LIMIT_MESSAGE}
    normal = authenticated_user_factory(email="normal@example.com")
    project = project_factory(normal["token"])
    normal_headers = {"Authorization": f"Bearer {normal['token']}"}
    assert test_client.post(f"/projects/{project['id']}/ai-assist", headers=normal_headers, json=blank_form).status_code == 200
    another_demo = start_demo(test_client)
    response = test_client.post(triage_url(another_demo), headers=another_demo, json=blank_form)
    assert response.status_code == 429 and response.json() == {"detail": GLOBAL_LIMIT_MESSAGE}
    assert len(offline_provider["requests"]) == 2
