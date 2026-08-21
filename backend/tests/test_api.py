from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.api import upload as upload_module
from app.api import chat as chat_module
from app.api import test_retriever as similar_module
from app.services import rag_pipeline as rag_pipeline_module


class FakeModelRunner:
    def __init__(self, response_text: str):
        self.response_text = response_text

    def generate_content(self, *args, **kwargs):
        return SimpleNamespace(text=self.response_text)


class FakeGeminiClient:
    def __init__(self, response_text: str):
        self.models = FakeModelRunner(response_text)


def patch_storage(monkeypatch, tmp_path):
    incident_dir = tmp_path / "incidents"
    vector_dir = tmp_path / "vector_db"
    incident_dir.mkdir(parents=True, exist_ok=True)
    vector_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(rag_pipeline_module, "INCIDENTS_DIR", str(incident_dir))
    monkeypatch.setattr(upload_module, "INCIDENTS_DIR", str(incident_dir))

    upload_module.pipeline.vector_store.index_path = str(vector_dir / "faiss.index")
    upload_module.pipeline.vector_store.metadata_path = str(vector_dir / "metadata.json")

    chat_module.retriever.vector_store.index_path = str(vector_dir / "faiss.index")
    chat_module.retriever.vector_store.metadata_path = str(vector_dir / "metadata.json")

    similar_module.retriever.vector_store.index_path = str(vector_dir / "faiss.index")
    similar_module.retriever.vector_store.metadata_path = str(vector_dir / "metadata.json")


def test_upload_analyze_similar_and_health_endpoints(tmp_path, monkeypatch):
    patch_storage(monkeypatch, tmp_path)
    client = TestClient(app)

    dataset = (
        "incident_id,title,description,root_cause,resolution,component,severity,environment\n"
        "INC-1001,Payment service failure,HTTP 500 errors during checkout,Database connection pool exhaustion,Increase pool size,Payment Service,High,Production\n"
        "INC-1002,Cache outage,Cache invalidation failed,Cache node memory pressure,Restart cache cluster,Cache,Medium,Production\n"
    )

    response = client.post(
        "/api/incidents/upload",
        files={"file": ("incidents.csv", dataset.encode("utf-8"), "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["indexed_incidents"] == 2

    chat_module.llm.client = FakeGeminiClient(
        json.dumps(
            {
                "root_cause": "Database connection pool exhaustion",
                "resolution": "Increase the database connection pool size and restart the affected service.",
                "evidence_strength": "High",
                "summary": "The new incident matches historical payment failures caused by database pool exhaustion.",
                "supporting_incident_ids": ["INC-1001"],
            }
        )
    )

    analyze_response = client.post(
        "/api/incidents/analyze",
        json={
            "description": "Payment checkout is failing with HTTP 500 errors in production.",
            "component": "Payment Service",
            "severity": "High",
            "environment": "Production",
            "incident_type": "Service Outage",
        },
    )

    assert analyze_response.status_code == 200
    analysis = analyze_response.json()
    assert analysis["root_cause"] == "Database connection pool exhaustion"
    assert analysis["similar_incidents"]
    assert analysis["evidence_incidents"][0]["incident_id"] == "INC-1001"

    similar_response = client.post(
        "/api/incidents/similar",
        json={
            "description": "Payment checkout is failing with HTTP 500 errors in production.",
            "component": "Payment Service",
            "severity": "High",
            "environment": "Production",
            "incident_type": "Service Outage",
        },
    )

    assert similar_response.status_code == 200
    assert len(similar_response.json()["incidents"]) == 2

    health_response = client.get("/api/health")
    assert health_response.status_code == 200
    assert health_response.json()["status"] == "Healthy"
