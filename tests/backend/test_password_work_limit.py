import threading

import pytest

from tests.backend.test_demo import start_demo, table_counts


BUSY = {"detail": "The server is busy. Please try again shortly."}


# TC-475 | — — Password hashing beyond the process-wide limit is refused with 503 and changes nothing
@pytest.mark.parametrize("endpoint", ["/register", "/login", "/demo"])
def test_password_work_beyond_limit_is_refused(
    test_client, test_database, user_factory, monkeypatch, endpoint
):
    from app.api import auth, demo

    user = user_factory(email="busy-guard@example.com")
    payload = {
        "/register": {"email": "busy-new@example.com", "password": "Password1"},
        "/login": user,
        "/demo": None,
    }[endpoint]
    before = table_counts(test_database)
    exhausted = threading.BoundedSemaphore(1)
    exhausted.acquire()

    with monkeypatch.context() as patch:
        patch.setattr(auth, "_password_work", exhausted)
        response = test_client.post(endpoint, json=payload)

    assert response.status_code == 503
    assert response.json() == BUSY
    assert table_counts(test_database) == before
    assert len(demo._recent_starts) == 0  # A refused Demo frees its hourly slot.

    # The same request succeeds once hashing capacity is available again.
    if endpoint == "/demo":
        start_demo(test_client)
    else:
        assert test_client.post(endpoint, json=payload).status_code in (200, 201)
