from fastapi.testclient import TestClient


def test_api_key_optional_by_default(client: TestClient):
    # API_KEY unset => endpoints should be accessible (dev mode)
    resp = client.get("/health")
    assert resp.status_code == 200


def test_api_key_required_when_configured(monkeypatch):
    # API_KEY configured => protected endpoints require X-API-Key.
    monkeypatch.setenv("API_KEY", "secret")

    from app.main import app

    client = TestClient(app)

    # Missing key
    resp = client.post("/chat/", json={"message": "hi"})
    assert resp.status_code == 401

    # Wrong key
    resp = client.post("/chat/", json={"message": "hi"}, headers={"X-API-Key": "nope"})
    assert resp.status_code == 401

    # Correct key
    resp = client.post("/chat/", json={"message": "hi"}, headers={"X-API-Key": "secret"})
    assert resp.status_code == 200
