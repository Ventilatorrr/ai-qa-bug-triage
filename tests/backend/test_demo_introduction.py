"""Demo identity checks use a wholly fictional stand-in for the historical seed."""
from contextlib import closing
from copy import deepcopy
import json
from pathlib import Path


# TC-461 | AC-024.4, AC-024.7 — Only a seeded historical project gets the server-owned marker
def test_historical_demo_marker_is_seeded_persistent_and_not_name_based(
    test_client, test_database, authenticated_user_factory, monkeypatch,
):
    from app import database
    from app.api import demo

    seed = json.loads((Path(__file__).resolve().parents[2] / "app/demo_data/demo_ecommerce.json").read_text(encoding="utf-8"))
    historical = deepcopy(seed)
    historical["project"] = "AI QA Bug Triage"
    historical["bugs"] = [historical["bugs"][0] | {"title": "Entirely fictional marker test"}]
    monkeypatch.setattr(demo, "load_seeds", lambda: [seed, historical])
    response = test_client.post("/demo")
    assert response.status_code == 201
    headers = {"Authorization": "Bearer " + response.json()["access_token"]}
    projects = test_client.get("/projects", headers=headers).json()
    history_id = next(p["id"] for p in projects if p["name"] == "AI QA Bug Triage")
    ecommerce_id = next(p["id"] for p in projects if p["name"] == "E-Commerce Demo")
    assert test_client.get(f"/projects/{history_id}", headers=headers).json()["demo_kind"] == "history"
    assert "demo_kind" not in test_client.get(f"/projects/{ecommerce_id}", headers=headers).json()

    ordinary = authenticated_user_factory(email="ordinary@example.com")
    ordinary_headers = {"Authorization": f"Bearer {ordinary['token']}"}
    response = test_client.post("/projects", headers=ordinary_headers, json={"name": "AI QA Bug Triage", "demo_kind": "history"})
    assert response.status_code == 201
    assert "demo_kind" not in test_client.get(f"/projects/{response.json()['id']}", headers=ordinary_headers).json()
    assert test_client.get(f"/projects/{history_id}", headers=ordinary_headers).status_code == 404
    assert test_client.get(f"/projects/{history_id}").status_code == 401

    assert test_client.put(f"/projects/{history_id}", headers=headers, json={"name": "Renamed Demo"}).status_code == 200
    assert database.DATABASE_NAME == str(test_database)
    database.create_tables()  # Startup checks must retain the marker and existing rows.
    assert test_client.get(f"/projects/{history_id}", headers=headers).json() == {
        "id": history_id, "name": "Renamed Demo", "demo_kind": "history",
    }
    with closing(database.get_connection()) as conn:
        assert conn.execute("SELECT COUNT(*) FROM bugs WHERE project_id=?", (history_id,)).fetchone() == (1,)
