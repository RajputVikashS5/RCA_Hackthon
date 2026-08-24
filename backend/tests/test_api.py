import json
from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import app
from app.api import chat as chat_module
from app.api import test_retriever as similar_module


class FakeSentenceTransformerEmbeddingService:
    def embed_query(self, question):
        return [0.0] * 384


class FakeRepository:
    def search(self, embedding, top_k=5):
        return [
            {
                "incident_id": "INC-1001",
                "title": "Payment failure",
                "description": "HTTP 500 during checkout",
                "root_cause": "Connection pool exhaustion",
                "resolution": "Increase pool size",
                "similarity_score": 0.94,
                "metadata": {},
            },
            {
                "incident_id": "INC-1002",
                "title": "Cache outage",
                "description": "Cache invalidation failed",
                "root_cause": None,
                "resolution": "Restart cache cluster",
                "similarity_score": 0.70,
                "metadata": {},
            },
        ][:top_k]


class FakeModelRunner:
    def generate_content(self, *args, **kwargs):
        return SimpleNamespace(
            text=json.dumps(
                {
                    "root_cause": "Connection pool exhaustion",
                    "resolution": "Increase the database connection pool size.",
                    "evidence_strength": "High",
                    "summary": "The payment incident matches the first historical record.",
                    "supporting_incident_ids": ["INC-1001"],
                }
            )
        )


class FakeGeminiClient:
    def __init__(self):
        self.models = FakeModelRunner()


class FakeAnalysisRepository:
    def create(self, request, result):
        return {"id": "f4e08625-025d-4b5c-b3c7-1834f3b67c6b"}


def configure_runtime_doubles(monkeypatch):
    for module in (chat_module, similar_module):
        module.retriever.repository = FakeRepository()
        module.retriever.embedding_model = FakeSentenceTransformerEmbeddingService()
    chat_module.llm.client = FakeGeminiClient()
    chat_module.analysis_repository = FakeAnalysisRepository()


def test_analyze_similar_and_disabled_upload_contracts(monkeypatch):
    configure_runtime_doubles(monkeypatch)
    client = TestClient(app)
    payload = {"description": "Payment checkout returns HTTP 500 errors."}

    analyze_response = client.post("/api/incidents/analyze", json=payload)
    assert analyze_response.status_code == 200
    assert analyze_response.json()["root_cause"] == "Connection pool exhaustion"
    assert analyze_response.json()["evidence_incidents"][0]["incident_id"] == "INC-1001"
    assert analyze_response.json()["analysis_id"] == "f4e08625-025d-4b5c-b3c7-1834f3b67c6b"

    similar_response = client.post("/api/incidents/similar", json=payload)
    assert similar_response.status_code == 200
    assert len(similar_response.json()["incidents"]) == 2

    upload_response = client.post("/api/incidents/upload")
    assert upload_response.status_code == 410
