from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import zenodo as zenodo_module
from app.main import app
from app.services import zenodo_service as service_module


def _record_response():
    return SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {
            "id": 15719919,
            "metadata": {
                "title": "The Public Jira Dataset",
                "description": "An anonymized public Jira dataset v7.",
                "access_right": "open",
            },
            "files": [
                {"key": "events.metadata.json.gz", "size": 10, "links": {"self": "https://metadata"}},
                {"key": "2025-06-23 ThePublicJiraDataset.zip", "size": 5813135238, "links": {"self": "https://archive"}},
            ],
        },
    )


def test_zenodo_status_selects_mongodb_archive(monkeypatch):
    monkeypatch.setattr(service_module.requests, "get", lambda url, timeout: _record_response())
    zenodo_module.service._cache.clear()

    response = TestClient(app).get("/api/zenodo/status")

    assert response.status_code == 200
    payload = response.json()
    assert payload["connected"] is True
    assert payload["record_id"] == "15719919"
    assert payload["dataset_access"] == "available"
    assert payload["dataset_archive"]["name"] == "2025-06-23 ThePublicJiraDataset.zip"
    assert payload["dataset_archive"]["size"] == 5813135238
    assert len(payload["files"]) == 2
    assert payload["files"][0]["download_url"] == "https://metadata"


def test_zenodo_test_does_not_download_archive(monkeypatch):
    calls = []

    def fake_get(url, timeout):
        calls.append(url)
        return _record_response()

    monkeypatch.setattr(service_module.requests, "get", fake_get)
    zenodo_module.service._cache.clear()
    response = TestClient(app).get("/api/zenodo/test")

    assert response.status_code == 200
    assert response.json()["connection"] == "metadata-only"
    assert response.json()["datasetFile"] == "2025-06-23 ThePublicJiraDataset.zip"
    assert len(calls) == 1


def test_zenodo_inspect_accepts_json_payload(monkeypatch):
    def fake_inspect(record_id, sample_size):
        assert record_id == "15719919"
        assert sample_size == 3
        return {
            "archive_type": "mongodb",
            "collections": ["issues"],
            "sample_records": [{"key": "PAY-1"}],
            "fields": ["key"],
            "sample_count": 1,
        }

    monkeypatch.setattr(zenodo_module.service, "inspect_dataset", fake_inspect)

    response = TestClient(app).post("/api/zenodo/inspect", json={"record_id": "15719919", "sample_size": 3})

    assert response.status_code == 200
    payload = response.json()
    assert payload["archive_type"] == "mongodb"
    assert payload["collections"] == ["issues"]
    assert payload["sample_count"] == 1


def test_zenodo_ingest_is_accepted_without_running_inline(monkeypatch):
    monkeypatch.setattr(zenodo_module, "get_database_status", lambda: {"connected": True})

    response = TestClient(app).post("/api/zenodo/ingest", json={"limit": 100})

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "accepted"
    assert payload["mode"] == "offline-cli"
    assert payload["limit"] == 100
    assert "does not download" in payload["message"]


def test_inspect_requires_explicit_local_archive(monkeypatch, tmp_path):
    monkeypatch.setattr(service_module, "JIRA_DATA_DIR", str(tmp_path))
    monkeypatch.setattr(service_module.requests, "get", lambda url, timeout: _record_response())
    zenodo_module.service._cache.clear()

    response = TestClient(app).post("/api/zenodo/inspect")

    assert response.status_code == 502
    assert "not downloaded locally" in response.json()["detail"]["error"]
