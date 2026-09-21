from app.version import APP_VERSION


def test_application_version_is_shared_by_openapi_and_endpoint(test_client):
    assert APP_VERSION == "0.1.0"

    openapi_response = test_client.get("/openapi.json")
    version_response = test_client.get("/version")

    assert openapi_response.status_code == 200
    assert openapi_response.json()["info"]["version"] == APP_VERSION
    assert version_response.status_code == 200
    assert version_response.json() == {"version": APP_VERSION}


def test_about_page_includes_application_version_loader(test_client):
    response = test_client.get("/about.html")

    assert response.status_code == 200
    assert 'id="app-version"' in response.text
    assert '<script src="js/about.js"></script>' in response.text
