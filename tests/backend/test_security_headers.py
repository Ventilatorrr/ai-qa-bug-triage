import pytest

from app.middleware import MAX_REQUEST_BODY_BYTES


EXPECTED = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "DENY",
    "content-security-policy": "frame-ancestors 'none'",
    "referrer-policy": "same-origin",
}


# TC-490 | — — API, static page and rejected responses carry the minimal security headers
@pytest.mark.parametrize("request_kind", ["api", "static", "unauthenticated", "too_large"])
def test_responses_carry_minimal_security_headers(test_client, request_kind):
    response = {
        "api": lambda: test_client.get("/version"),
        "static": lambda: test_client.get("/login.html"),
        "unauthenticated": lambda: test_client.get("/projects"),
        "too_large": lambda: test_client.post(
            "/projects", content=b"x" * (MAX_REQUEST_BODY_BYTES + 1), headers={"Content-Type": "application/json"}
        ),
    }[request_kind]()
    assert response.status_code == {"api": 200, "static": 200, "unauthenticated": 401, "too_large": 413}[request_kind]
    for name, value in EXPECTED.items():
        assert response.headers.get(name) == value
