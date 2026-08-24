from fastapi.testclient import TestClient

from app.main import app


def test_health_does_not_expose_database_credentials(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "Unavailable"
    assert payload["database"] == "Unavailable"
    assert "DATABASE_URL" not in str(payload)
