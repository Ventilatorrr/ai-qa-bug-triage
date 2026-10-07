from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
import sqlite3
from threading import Barrier

import pytest


@pytest.fixture
def numbering_project(test_client, authenticated_user_factory, project_factory):
    owner = authenticated_user_factory()
    project = project_factory(owner["token"])
    headers = {"Authorization": f"Bearer {owner['token']}"}
    return project, headers


def create(test_client, project_id, headers, **fields):
    response = test_client.post(
        f"/projects/{project_id}/bugs", headers=headers,
        json={"title": "Numbered report", **fields},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_bug_numbers_are_independent_and_routes_use_local_numbers(
    test_client, numbering_project, project_factory,
):
    project, headers = numbering_project
    other = project_factory(headers["Authorization"].removeprefix("Bearer "))
    assert "next_bug_number" not in project and "next_bug_number" not in other
    reports = []
    for number in range(1, 4):
        for current in (project, other):
            bug = create(test_client, current["id"], headers, bug_number=999)
            assert bug["bug_number"] == number
            reports.append(bug)
            viewed = test_client.get(
                f"/projects/{current['id']}/bugs/{bug['bug_number']}", headers=headers,
            )
            assert viewed.json() == bug
    assert len({bug["id"] for bug in reports}) == 6
    assert test_client.get(
        f"/projects/{other['id']}/bugs/1", headers=headers,
    ).json()["id"] == reports[1]["id"]
    assert test_client.get(
        f"/projects/{project['id']}/bugs/1", headers=headers,
    ).json()["id"] == reports[0]["id"]
    for current in (project, other):
        listed = test_client.get(f"/projects/{current['id']}/bugs", headers=headers).json()
        assert {bug["bug_number"] for bug in listed} == {1, 2, 3}
        assert {bug["id"] for bug in listed} == {bug["id"] for bug in reports if bug["project_id"] == current["id"]}


@pytest.mark.parametrize("delete_all", [False, True])
def test_deleted_bug_numbers_are_not_reused(test_client, numbering_project, delete_all):
    project, headers = numbering_project
    bugs = [create(test_client, project["id"], headers) for _ in range(3)]
    for bug in bugs if delete_all else bugs[-1:]:
        assert test_client.delete(
            f"/projects/{project['id']}/bugs/{bug['bug_number']}", headers=headers,
        ).status_code == 204
    assert create(test_client, project["id"], headers)["bug_number"] == 4


def test_bug_number_is_preserved_on_edit(test_client, numbering_project):
    project, headers = numbering_project
    bug = create(test_client, project["id"], headers)
    url = f"/projects/{project['id']}/bugs/{bug['bug_number']}"
    response = test_client.patch(url, headers=headers, json={"title": "Edited", "bug_number": 999})
    assert response.status_code == 200
    assert response.json()["bug_number"] == bug["bug_number"]
    assert response.json()["id"] == bug["id"]
    assert test_client.get(url, headers=headers).json() == response.json()


@pytest.mark.parametrize("operation", ["details", "edit", "status", "delete", "ai-assist"])
def test_public_bug_routes_use_local_number_and_isolate_projects(
    test_client, numbering_project, project_factory, authenticated_user_factory,
    member_factory, monkeypatch, operation,
):
    from app import ai_triage
    from app.ai_suggestions import SuggestionResult

    project, headers = numbering_project
    first = create(test_client, project["id"], headers)
    for _ in range(4):
        create(test_client, project["id"], headers)
    token = headers["Authorization"].removeprefix("Bearer ")
    other = project_factory(token, name="Other numbering project")
    developer = authenticated_user_factory(email="numbering-dev@example.com")
    member_factory(token, other["id"], developer["user"]["email"], "Developer")
    target = create(test_client, other["id"], headers)
    history = create(test_client, other["id"], headers)
    assert first["bug_number"] == target["bug_number"] == 1
    assert target["id"] == 6 and target["id"] != target["bug_number"]
    captured = []

    def suggestions(context, *, project_id):
        captured.append((project_id, [bug.id for bug in context.recent_bugs]))
        return SuggestionResult(suggestions={})

    monkeypatch.setattr(ai_triage, "request_suggestions", suggestions)
    form = dict.fromkeys([
        "title", "affected_version", "environment", "description", "steps_to_reproduce",
        "expected_result", "actual_result", "severity", "priority",
    ], "") | {"assignee_id": None}
    method, suffix, payload, expected = {
        "details": ("GET", "", None, 200),
        "edit": ("PATCH", "", {"title": "Edited local resource"}, 200),
        "status": ("PATCH", "/status", {"status": "Open", "assignee_id": developer["user_id"]}, 200),
        "delete": ("DELETE", "", None, 204),
        "ai-assist": ("POST", "/ai-assist", form, 200),
    }[operation]
    base = f"/projects/{other['id']}/bugs"
    # A global ID exists, but it must not resolve as this project's public number.
    assert test_client.request(method, f"{base}/{target['id']}{suffix}", headers=headers, json=payload).status_code == 404
    assert captured == []
    assert test_client.get(f"{base}/1", headers=headers).json() == target
    response = test_client.request(method, f"{base}/1{suffix}", headers=headers, json=payload)
    assert response.status_code == expected
    if operation in ("details", "edit", "status"):
        assert response.json()["id"] == target["id"]
        assert response.json()["bug_number"] == 1
        assert response.json()["project_id"] == other["id"]
    elif operation == "delete":
        assert test_client.get(f"{base}/1", headers=headers).status_code == 404
    else:
        # Edit exclusion and history still use internal global IDs.
        assert captured == [(other["id"], [history["id"]])]
        assert test_client.get(f"{base}/1", headers=headers).json() == target
    assert test_client.get(f"/projects/{project['id']}/bugs/1", headers=headers).json() == first


@pytest.mark.parametrize("failure_point", ["before-counter-update", "before-commit"])
def test_failed_creation_rolls_back_bug_and_counter(test_client, numbering_project, monkeypatch, failure_point):
    from app import database
    from app.api import bugs

    project, headers = numbering_project
    create(test_client, project["id"], headers)
    for payload in ({"title": " "}, {"title": "Invalid assignee", "assignee_id": 999}):
        assert test_client.post(f"/projects/{project['id']}/bugs", headers=headers, json=payload).status_code == 422
    assert test_client.post(f"/projects/{project['id']}/bugs", json={"title": "Unauthorized"}).status_code == 401
    with closing(database.get_connection()) as connection:
        before_counter = connection.execute("SELECT next_bug_number FROM projects WHERE id=?", (project["id"],)).fetchone()[0]
    assert before_counter == 2
    before_reports = test_client.get(f"/projects/{project['id']}/bugs", headers=headers).json()
    reached = []

    class FailingConnection(sqlite3.Connection):
        def execute(self, sql, parameters=()):
            if failure_point == "before-counter-update" and "UPDATE projects" in sql and "next_bug_number" in sql:
                reached.append("before-counter-update")
                raise sqlite3.OperationalError("Injected counter failure")
            return super().execute(sql, parameters)

        def commit(self):
            assert failure_point == "before-commit"
            assert self.in_transaction
            assert self.execute("SELECT next_bug_number FROM projects WHERE id=?", (project["id"],)).fetchone() == (before_counter + 1,)
            assert self.execute("SELECT bug_number FROM bugs WHERE project_id=? ORDER BY bug_number", (project["id"],)).fetchall() == [(1,), (before_counter,)]
            reached.append("before-commit")
            raise sqlite3.OperationalError("Injected creation commit failure")

    with monkeypatch.context() as patch:
        patch.setattr(bugs, "get_connection", lambda: sqlite3.connect(database.DATABASE_NAME, factory=FailingConnection))
        with pytest.raises(sqlite3.OperationalError, match="Injected (counter|creation commit) failure"):
            create(test_client, project["id"], headers)
    assert reached == [failure_point]
    assert test_client.get(f"/projects/{project['id']}/bugs", headers=headers).json() == before_reports
    with closing(database.get_connection()) as connection:
        assert connection.execute("SELECT next_bug_number FROM projects WHERE id=?", (project["id"],)).fetchone() == (before_counter,)
    assert create(test_client, project["id"], headers)["bug_number"] == before_counter
    assert len(test_client.get(f"/projects/{project['id']}/bugs", headers=headers).json()) == 2


def test_concurrent_creation_allocates_unique_bug_numbers(
    test_client, numbering_project, tmp_path, monkeypatch,
):
    from app import database

    project, headers = numbering_project
    assert database.DATABASE_NAME == "test_bugtriage.db"
    temporary = tmp_path / "concurrent.db"
    with closing(database.get_connection()) as source, closing(sqlite3.connect(temporary)) as destination:
        source.backup(destination)
    monkeypatch.setattr(database, "DATABASE_NAME", str(temporary))
    barrier = Barrier(4)
    def request(_):
        barrier.wait(timeout=10)
        return create(test_client, project["id"], headers)
    with ThreadPoolExecutor(max_workers=4) as pool:
        created = list(pool.map(request, range(4)))
    assert sorted(bug["bug_number"] for bug in created) == [1, 2, 3, 4]
    assert len({bug["id"] for bug in created}) == 4
    with closing(database.get_connection()) as connection:
        assert connection.execute("SELECT next_bug_number FROM projects WHERE id=?", (project["id"],)).fetchone() == (5,)
