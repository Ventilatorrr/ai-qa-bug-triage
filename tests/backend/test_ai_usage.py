from contextlib import closing
from datetime import datetime, timezone
import threading

from fastapi.testclient import TestClient
import pytest

from tests.backend.test_ai_assist import ai_project, blank_form, headers, request_url
from tests.backend.test_ai_triage import offline_provider, persisted_state


USER_LIMIT_MESSAGE = "You have reached your daily AI Assist limit. Try again after 00:00 UTC."
GLOBAL_LIMIT_MESSAGE = "AI Assist has reached its daily limit for all users. Try again after 00:00 UTC."
MISCONFIGURED_MESSAGE = "AI assistance is unavailable because its usage limits are misconfigured."


@pytest.fixture
def qa_analyst(ai_project, authenticated_user_factory, member_factory):
    owner, _, project, _, _ = ai_project
    qa = authenticated_user_factory(email="qa@example.com")
    member_factory(owner["token"], project["id"], qa["user"]["email"], "QA Analyst")
    return qa


def ai_request(client, context, user, form, edit=False):
    return client.post(request_url(context, edit), headers=headers(user), json=form)


def seed_usage(test_database, user_id, count):
    # Seeding prior usage directly keeps default-limit tests fast; only the disposable DB is used.
    from app import ai_usage, database

    assert database.DATABASE_NAME == str(test_database)
    with closing(database.get_connection()) as connection:
        connection.executemany(
            "INSERT INTO ai_requests (user_id, usage_date) VALUES (?, ?)",
            [(user_id, ai_usage.utc_today())] * count,
        )
        connection.commit()


# TC-425 | AC-025.1, AC-025.5 — AI usage enforces per-account daily limit across projects
def test_ai_usage_enforces_per_account_daily_limit_across_projects(
    test_client, ai_project, blank_form, offline_provider, qa_analyst, project_factory, monkeypatch,
):
    monkeypatch.setenv("AI_DAILY_USER_LIMIT", "2")
    owner, _, _, _, base = ai_project
    second = project_factory(owner["token"], name="Second AI project")
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200
    response = test_client.post(f"/projects/{second['id']}/ai-assist", headers=headers(owner), json=blank_form)
    assert response.status_code == 200
    before = persisted_state(test_client, ai_project)
    form = blank_form | {"title": "Unsaved title"}
    for _ in range(2):  # Retrying stays rejected until the limit resets.
        for edit in (False, True):
            response = ai_request(test_client, ai_project, owner, form, edit)
            assert response.status_code == 429
            assert response.json() == {"detail": USER_LIMIT_MESSAGE}
    assert len(offline_provider["requests"]) == 2
    assert persisted_state(test_client, ai_project) == before
    # The user can continue manually, and another account keeps its own allowance.
    assert test_client.post(f"{base}/bugs", headers=headers(owner), json={"title": form["title"]}).status_code == 201
    assert ai_request(test_client, ai_project, qa_analyst, blank_form).status_code == 200
    assert len(offline_provider["requests"]) == 3


# TC-426 | AC-025.2, AC-025.5 — AI usage enforces global daily limit across accounts
def test_ai_usage_enforces_global_daily_limit_across_accounts(
    test_client, ai_project, blank_form, offline_provider, qa_analyst, monkeypatch,
):
    monkeypatch.setenv("AI_DAILY_GLOBAL_LIMIT", "2")
    owner = ai_project[0]
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200
    assert ai_request(test_client, ai_project, qa_analyst, blank_form).status_code == 200
    before = persisted_state(test_client, ai_project)
    for user in (owner, qa_analyst):
        response = ai_request(test_client, ai_project, user, blank_form)
        assert response.status_code == 429
        assert response.json() == {"detail": GLOBAL_LIMIT_MESSAGE}
    assert len(offline_provider["requests"]) == 2
    assert persisted_state(test_client, ai_project) == before


# TC-427 | AC-025.3 — AI usage applies default limits when not configured
@pytest.mark.parametrize("value", [None, "", "  "], ids=["unset", "empty", "blank"])
@pytest.mark.parametrize("scope", ["user", "global"])
def test_ai_usage_applies_default_limits_when_not_configured(
    test_client, test_database, ai_project, blank_form, offline_provider, qa_analyst, monkeypatch, value, scope,
):
    from app import ai_usage

    assert (ai_usage.DEFAULT_USER_LIMIT, ai_usage.DEFAULT_GLOBAL_LIMIT) == (50, 500)
    if value is not None:
        monkeypatch.setenv("AI_DAILY_USER_LIMIT" if scope == "user" else "AI_DAILY_GLOBAL_LIMIT", value)
    owner = ai_project[0]
    if scope == "user":
        seed_usage(test_database, owner["user_id"], ai_usage.DEFAULT_USER_LIMIT - 1)
    else:
        seed_usage(test_database, qa_analyst["user_id"], ai_usage.DEFAULT_GLOBAL_LIMIT - 1)
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200
    response = ai_request(test_client, ai_project, owner, blank_form)
    assert response.status_code == 429
    assert response.json() == {"detail": USER_LIMIT_MESSAGE if scope == "user" else GLOBAL_LIMIT_MESSAGE}
    assert len(offline_provider["requests"]) == 1


# TC-428 | AC-025.3 — AI usage applies configured limits
@pytest.mark.parametrize("value,allowed", [(" 1 ", 1), ("0", 0)])
@pytest.mark.parametrize("name", ["AI_DAILY_USER_LIMIT", "AI_DAILY_GLOBAL_LIMIT"])
def test_ai_usage_applies_configured_limits(
    test_client, ai_project, blank_form, offline_provider, monkeypatch, name, value, allowed,
):
    monkeypatch.setenv(name, value)
    owner = ai_project[0]
    for _ in range(allowed):
        assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 429
    assert len(offline_provider["requests"]) == allowed


# TC-429 | AC-025.3, AC-025.4 — AI usage invalid configuration blocks only AI Assist without counting
@pytest.mark.parametrize("value", ["-1", "abc", "1.5", "10a", "1e3", "１"])
@pytest.mark.parametrize("name", ["AI_DAILY_USER_LIMIT", "AI_DAILY_GLOBAL_LIMIT"])
def test_ai_usage_invalid_configuration_blocks_only_ai_assist_without_counting(
    test_client, ai_project, blank_form, offline_provider, monkeypatch, name, value,
):
    monkeypatch.setenv(name, value)
    owner, _, _, _, base = ai_project
    before = persisted_state(test_client, ai_project)
    response = ai_request(test_client, ai_project, owner, blank_form | {"title": "Unsaved title"})
    assert response.status_code == 503
    assert response.json() == {"detail": MISCONFIGURED_MESSAGE}
    assert offline_provider["requests"] == []
    assert persisted_state(test_client, ai_project) == before
    # The rest of the application remains available.
    assert test_client.get("/projects", headers=headers(owner)).status_code == 200
    assert test_client.post(f"{base}/bugs", headers=headers(owner), json={"title": "Still works"}).status_code == 201
    monkeypatch.setenv(name, "1")
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200


# TC-430 | AC-025.4, AC-025.5, AC-025.6 — AI usage does not count requests rejected before the provider
def test_ai_usage_does_not_count_requests_rejected_before_provider(
    test_client, ai_project, blank_form, offline_provider, authenticated_user_factory, monkeypatch,
):
    from app.ai_context import FORM_TEXT_LIMIT

    monkeypatch.setenv("AI_DAILY_USER_LIMIT", "1")
    owner, developer, _, bug, base = ai_project
    outsider = authenticated_user_factory(email="outsider@example.com")
    response = test_client.patch(
        f"{base}/bugs/{bug['bug_number']}/status", headers=headers(owner),
        json={"status": "Open", "assignee_id": developer["user_id"]},
    )
    assert response.status_code == 200
    rejected = [
        ({}, False, blank_form, 401),
        (headers(developer), False, blank_form, 403),
        (headers(outsider), False, blank_form, 404),
        (headers(owner), True, blank_form, 409),
        (headers(owner), False, blank_form | {"severity": "Severe"}, 422),
        (headers(owner), False, blank_form | {"description": "x" * (FORM_TEXT_LIMIT + 1)}, 422),
    ]
    for request_headers, edit, form, status in rejected:
        assert test_client.post(request_url(ai_project, edit), headers=request_headers, json=form).status_code == status
    monkeypatch.delenv("OPENAI_API_KEY")
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 503
    monkeypatch.setenv("OPENAI_API_KEY", "integration-test-key")
    assert offline_provider["requests"] == []
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200
    for _ in range(2):
        assert ai_request(test_client, ai_project, owner, blank_form).status_code == 429
    # Raising the limit by one admits exactly one more request: the 429 rejections were not counted.
    monkeypatch.setenv("AI_DAILY_USER_LIMIT", "2")
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 429
    assert len(offline_provider["requests"]) == 2


def fail_sdk_context(patch, stage):
    """Wrap the offline client so its context manager fails once, on entry or exit."""
    from app import ai_triage

    create = ai_triage.create_openai_client
    failures = []

    class FailingContext:
        def __init__(self, client):
            self.client = client

        def __enter__(self):
            if stage == "enter":
                self.client.close()
                raise RuntimeError("SDK context failure")
            return self.client

        def __exit__(self, *exc_info):
            self.client.close()
            if stage == "exit" and not failures:
                failures.append(stage)
                raise RuntimeError("SDK context failure")
            return False

    patch.setattr(ai_triage, "create_openai_client", lambda api_key: FailingContext(create(api_key)))


# TC-431 | AC-025.4 — AI usage counts requests that fail at the provider
@pytest.mark.parametrize("failure", ["error", "timeout", "malformed", "truncated", "context_exit"])
def test_ai_usage_counts_requests_that_fail_at_the_provider(
    test_client, ai_project, blank_form, offline_provider, monkeypatch, failure,
):
    monkeypatch.setenv("AI_DAILY_USER_LIMIT", "1")
    if failure == "context_exit":
        fail_sdk_context(monkeypatch, "exit")
    elif failure == "error":
        offline_provider["error"] = "Provider failure"
    elif failure == "timeout":
        offline_provider["timeout_error"] = "Provider timeout"
    elif failure == "malformed":
        offline_provider["raw"] = {"unexpected": True}
    else:
        offline_provider["status"] = "incomplete"
        offline_provider["incomplete_details"] = {"reason": "max_output_tokens"}
    owner = ai_project[0]
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 502
    response = ai_request(test_client, ai_project, owner, blank_form)
    assert response.status_code == 429
    assert response.json() == {"detail": USER_LIMIT_MESSAGE}
    assert len(offline_provider["requests"]) == 1


# TC-437 | AC-025.4 — AI usage does not count local preparation failures before the provider
@pytest.mark.parametrize("failure", ["generation_input", "client", "context_enter"])
def test_ai_usage_does_not_count_local_preparation_failures(
    test_client, ai_project, blank_form, offline_provider, monkeypatch, failure,
):
    from app import ai_triage

    def fail(*args, **kwargs):
        raise RuntimeError("Local preparation failure")

    monkeypatch.setenv("AI_DAILY_USER_LIMIT", "1")
    owner = ai_project[0]
    with monkeypatch.context() as patch:
        if failure == "generation_input":
            patch.setattr(ai_triage, "build_generation_input", fail)
            with pytest.raises(RuntimeError, match="Local preparation failure"):
                ai_request(test_client, ai_project, owner, blank_form)
        else:
            if failure == "client":
                patch.setattr(ai_triage, "create_openai_client", fail)
            else:
                fail_sdk_context(patch, "enter")
            response = ai_request(test_client, ai_project, owner, blank_form)
            assert response.status_code == 502
            assert response.json() == {"detail": "AI assistance could not generate suggestions. Please try again."}
    assert offline_provider["requests"] == []
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 429
    assert len(offline_provider["requests"]) == 1


# TC-432 | AC-025.4 — AI usage persists across restart and resets at UTC midnight
def test_ai_usage_persists_across_restart_and_resets_at_utc_midnight(
    test_client, ai_project, blank_form, offline_provider, monkeypatch,
):
    from app import ai_usage
    from app.main import app

    clock = {"now": datetime(2026, 10, 26, 23, 59, 59, tzinfo=timezone.utc)}

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            # A local-time implementation would see a different date here outside UTC.
            return clock["now"].astimezone(tz)

    monkeypatch.setattr(ai_usage, "datetime", FrozenDatetime)
    monkeypatch.setenv("AI_DAILY_USER_LIMIT", "1")
    owner = ai_project[0]
    assert ai_request(test_client, ai_project, owner, blank_form).status_code == 200
    # A new application lifespan reruns startup against the same disposable database.
    with TestClient(app) as restarted:
        assert ai_request(restarted, ai_project, owner, blank_form).status_code == 429
        clock["now"] = datetime(2026, 10, 27, 0, 0, tzinfo=timezone.utc)
        assert ai_request(restarted, ai_project, owner, blank_form).status_code == 200
        assert ai_request(restarted, ai_project, owner, blank_form).status_code == 429
    assert len(offline_provider["requests"]) == 2


# TC-433 | AC-025.4 — AI usage concurrent reservations cannot exceed limits
@pytest.mark.parametrize("scope", ["user", "global"])
def test_ai_usage_concurrent_reservations_cannot_exceed_limits(
    test_client, test_database, authenticated_user_factory, monkeypatch, scope,
):
    from app import ai_usage, database

    assert database.DATABASE_NAME == str(test_database)
    users = [authenticated_user_factory(email=f"concurrent{index}@example.com")["user_id"] for index in range(2)]
    monkeypatch.setenv("AI_DAILY_USER_LIMIT" if scope == "user" else "AI_DAILY_GLOBAL_LIMIT", "3")
    attempts = 16
    barrier = threading.Barrier(attempts)
    outcomes = []

    def reserve(user_id):
        barrier.wait()
        try:
            ai_usage.reserve_ai_request(user_id)
            outcomes.append("counted")
        except ai_usage.AiUsageLimitReached:
            outcomes.append("rejected")
        except Exception as error:  # Surface lock or other errors as a failed assertion.
            outcomes.append(repr(error))

    threads = [
        threading.Thread(target=reserve, args=(users[0] if scope == "user" else users[index % 2],))
        for index in range(attempts)
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert sorted(outcomes) == ["counted"] * 3 + ["rejected"] * (attempts - 3)
    with closing(database.get_connection()) as connection:
        assert connection.execute("SELECT COUNT(*) FROM ai_requests").fetchone() == (3,)
