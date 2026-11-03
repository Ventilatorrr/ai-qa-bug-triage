import pytest

from app.version import APP_VERSION, read_build_commit


COMMIT = "0123456789abcdef0123456789abcdef01234567"


# TC-227 | Technical — Application version is shared by openapi and endpoint
def test_application_version_is_shared_by_openapi_and_endpoint(test_client):
    assert APP_VERSION == "1.0.1"

    openapi_response = test_client.get("/openapi.json")
    version_response = test_client.get("/version")

    assert openapi_response.status_code == 200
    assert openapi_response.json()["info"]["version"] == APP_VERSION
    assert version_response.status_code == 200
    # Local and test runs have no build-commit file, so the commit is null.
    assert version_response.json() == {"version": APP_VERSION, "commit": None}


# TC-514 | Technical — /version reports the build commit only when the image recorded a full SHA
@pytest.mark.parametrize("content,expected", [
    (f"{COMMIT}\n", COMMIT),
    (COMMIT, COMMIT),
    (None, None),
    ("", None),
    (COMMIT.upper(), None),
    (COMMIT[:12], None),
    (f"{COMMIT} extra", None),
])
def test_version_reports_only_a_valid_build_commit(test_client, tmp_path, monkeypatch, content, expected):
    path = tmp_path / "BUILD_COMMIT"
    if content is not None:
        path.write_text(content, encoding="utf-8")

    commit = read_build_commit(path)
    assert commit == expected

    import app.main
    monkeypatch.setattr(app.main, "BUILD_COMMIT", commit)
    response = test_client.get("/version")
    assert response.status_code == 200
    assert response.json() == {"version": APP_VERSION, "commit": expected}


# TC-228 | Technical — About page includes application version loader
def test_about_page_includes_application_version_loader(test_client):
    response = test_client.get("/about.html")

    assert response.status_code == 200
    assert 'id="app-version"' in response.text
    assert '<script src="js/about.js"></script>' in response.text
