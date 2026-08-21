from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import zenodo as zenodo_module
from app.services import zenodo_service as service_module
from app.main import app


def test_zenodo_connection_returns_metadata_and_sample(monkeypatch):
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        if url.endswith("/7182101"):
            return SimpleNamespace(
                raise_for_status=lambda: None,
                json=lambda: {
                    "id": 7182101,
                    "metadata": {"title": "Public Jira Dataset"},
                    "files": [{"key": "incidents.json", "size": 20, "links": {"self": "https://download"}}],
                },
            )
        return SimpleNamespace(
            raise_for_status=lambda: None,
            content=b'[{"incident_id": "INC-1", "title": "Example"}]',
        )

    monkeypatch.setattr(service_module.requests, "get", fake_get)
    zenodo_module.service._cache.clear()
    response = TestClient(app).get("/api/zenodo/test")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "available"
    assert data["filesFound"] == 1
    assert data["sampleRecords"][0]["incident_id"] == "INC-1"
    assert len(calls) == 2


def test_zenodo_connection_reports_record_without_public_files(monkeypatch):
    monkeypatch.setattr(
        service_module.requests,
        "get",
        lambda url, timeout: SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"id": 7182101, "metadata": {"title": "Restricted"}, "files": []},
        ),
    )
    zenodo_module.service._cache.clear()
    response = TestClient(app).get("/api/zenodo/test")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "restricted"
    assert data["metadataAvailable"] is True
    assert data["filesAvailable"] is False


def test_zenodo_connection_reports_unsupported_file_format(monkeypatch):
    monkeypatch.setattr(
        service_module.requests,
        "get",
        lambda url, timeout: SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {
                "id": 7182101,
                "metadata": {"title": "Archive"},
                "files": [{"key": "jira-dump.archive", "links": {"self": "https://download"}}],
            },
        ),
    )
    zenodo_module.service._cache.clear()
    response = TestClient(app).get("/api/zenodo/test")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "restricted"


def test_zenodo_connection_reports_metadata_failure_as_unavailable(monkeypatch):
    def unavailable(url, timeout):
        raise service_module.requests.ConnectionError("network unavailable")

    monkeypatch.setattr(service_module.requests, "get", unavailable)
    zenodo_module.service._cache.clear()

    response = TestClient(app).get("/api/zenodo/test")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "unavailable"
    assert data["metadataAvailable"] is False


def test_zenodo_connection_caches_a_restricted_source(monkeypatch):
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        return SimpleNamespace(
            raise_for_status=lambda: None,
            json=lambda: {"id": 7182101, "metadata": {"title": "Restricted"}, "files": []},
        )

    monkeypatch.setattr(service_module.requests, "get", fake_get)
    zenodo_module.service._cache.clear()

    client = TestClient(app)
    assert client.get("/api/zenodo/test").json()["data"]["status"] == "restricted"
    assert client.get("/api/zenodo/test").json()["data"]["status"] == "restricted"
    assert len(calls) == 1
