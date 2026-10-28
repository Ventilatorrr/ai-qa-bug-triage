import pytest

from app.middleware import MAX_REQUEST_BODY_BYTES


JSON = {"Content-Type": "application/json"}


def project_body(size):
    """A JSON project body of exactly `size` bytes."""
    prefix, suffix = b'{"name": "', b'"}'
    return prefix + b"x" * (size - len(prefix) - len(suffix)) + suffix


# TC-477 | — — Oversized request bodies are rejected with 413 before parsing or authentication
@pytest.mark.parametrize("transfer", ["declared", "streamed"])
def test_oversized_request_body_is_rejected_before_authentication(test_client, transfer):
    oversized = project_body(MAX_REQUEST_BODY_BYTES + 1)
    # A generator body is sent without Content-Length, so it is counted as it streams.
    content = oversized if transfer == "declared" else iter([oversized[:65536], oversized[65536:]])

    response = test_client.post("/projects", content=content, headers=JSON)
    assert response.status_code == 413
    assert response.json() == {"detail": "Request body is too large."}

    # A body exactly at the limit still reaches the endpoint, which then requires authentication.
    response = test_client.post("/projects", content=project_body(MAX_REQUEST_BODY_BYTES), headers=JSON)
    assert response.status_code == 401
