from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.api import zenodo as zenodo_module
from app.main import app
from app.services import zenodo_service as service_module
from app import config
from ingestion.zenodo_client import ZenodoClient


def test_default_source_is_apache_jira_dataset():
    assert config.ZENODO_RECORD_ID == "7740379"
    assert "7740379" in config.ZENODO_RECORD_URL
    assert "Apache Jira" in config.ZENODO_SOURCE_NAME


def test_zenodo_client_uses_bearer_token_header_when_configured(monkeypatch):
    seen = {}

    def fake_get(url, timeout, headers=None):
        seen["url"] = url
        seen["headers"] = headers
        return SimpleNamespace(status_code=200, raise_for_status=lambda: None, json=lambda: {"id": 7740379, "metadata": {"title": "Apache Jira Issue Tracking Dataset"}, "files": []})

    monkeypatch.setattr("ingestion.zenodo_client.requests.get", fake_get)
    client = ZenodoClient(access_token="secret-token")
    payload = client.get_record("7740379")
    assert seen["headers"]["Authorization"] == "Bearer secret-token"
    assert payload["id"] == 7740379
    assert "secret-token" not in str(payload)


def test_public_record_has_only_archive_metadata_and_no_direct_issue_api(monkeypatch):
    payload = {
        "id": 7740379,
        "metadata": {"title": "Apache Jira Issue Tracking Dataset", "access_right": "open"},
        "files": [
            {"key": "issues.metadata.json.gz", "size": 172, "links": {"self": "https://zenodo.org/api/records/7740379/files/issues.metadata.json.gz/content"}},
            {"key": "issues.bson.gz", "size": 764648860, "links": {"self": "https://zenodo.org/api/records/7740379/files/issues.bson.gz/content"}},
        ],
    }
    monkeypatch.setattr(service_module.requests, "get", lambda url, timeout: SimpleNamespace(raise_for_status=lambda: None, json=lambda: payload))
    info = zenodo_module.client.get_record("7740379")
    files = zenodo_module.client.list_files(info)
    assert any(f["key"] == "issues.metadata.json.gz" for f in files)
    assert any(f["key"] == "issues.bson.gz" for f in files)
    assert zenodo_module.client.bson_files(files)
    assert not zenodo_module.client.supports_record_level_issue_access(files)
    resp = TestClient(app).get("/api/zenodo/test")
    assert resp.status_code == 200
    assert resp.json()["data"]["supportsRecordLevelAccess"] is False
    assert "downloading the BSON archive" in resp.json()["data"]["message"]


def _record_response():
    return SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {
            "id": 7740379,
            "metadata": {
                "title": "Apache Jira Issue Tracking Dataset",
                "description": "Apache Jira issue tracking data.",
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
    assert payload["record_id"] == "7740379"
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
    data = response.json()["data"]
    assert data["status"] == "restricted"
    assert data["supportsRecordLevelAccess"] is False
    assert data["filesFound"] == 2
    assert "sampleRecords" not in data or not data.get("sampleRecords")
    assert len(calls) == 1


def test_zenodo_inspect_accepts_json_payload(monkeypatch):
    def fake_inspect(record_id, sample_size):
        assert record_id == "7740379"
        assert sample_size == 3
        return {
            "archive_type": "mongodb",
            "collections": ["issues"],
            "sample_records": [{"key": "PAY-1"}],
            "fields": ["key"],
            "sample_count": 1,
        }

    monkeypatch.setattr(zenodo_module.service, "inspect_dataset", fake_inspect)

    response = TestClient(app).post("/api/zenodo/inspect", json={"record_id": "7740379", "sample_size": 3})

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
