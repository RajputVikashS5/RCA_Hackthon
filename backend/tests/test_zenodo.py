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
    assert response.json()["filesFound"] == 1
    assert response.json()["sampleRecords"][0]["incident_id"] == "INC-1"
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

    assert response.status_code == 502
    assert response.json()["detail"]["connection"] == "failed"
    assert "no publicly downloadable files" in response.json()["detail"]["error"]


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

    assert response.status_code == 502
    assert "supported format" in response.json()["detail"]["error"]