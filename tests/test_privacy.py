def test_privacy_policy_is_public_without_authentication(test_client):
    from app.database import DATABASE_NAME

    assert DATABASE_NAME == "test_bugtriage.db"
    response = test_client.get("/privacy.html", follow_redirects=False)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "<h2>Privacy Policy</h2>" in response.text
    assert "Pre-deployment draft" in response.text
    assert 'href="/login.html"' in response.text
