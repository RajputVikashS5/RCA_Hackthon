from __future__ import annotations

import pytest

from app.services.embedding import EmbeddingModel
from app.services.retriever import Retriever
from app.services import vector_store as vector_store_module


def test_top_five_retrieval_is_sorted_and_scored(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store_module, "INCIDENT_VECTOR_DB_DIR", str(tmp_path))

    store = vector_store_module.VectorStore()
    embedder = EmbeddingModel()

    texts = [
        "Incident ID: INC-1\nTitle: Payment service failure\nDescription: HTTP 500 errors during checkout\nRoot Cause: Database connection pool exhaustion\nResolution: Increase pool size",
        "Incident ID: INC-2\nTitle: Cache outage\nDescription: Cache invalidation failed\nRoot Cause: Cache node memory pressure\nResolution: Restart cache cluster",
        "Incident ID: INC-3\nTitle: Login issue\nDescription: Authentication timeouts\nRoot Cause: Identity service degradation\nResolution: Restart identity service",
    ]

    embeddings = embedder.embed_documents(texts)
    metadata = [
        {"incident_id": "INC-1", "title": "Payment service failure", "description": "HTTP 500 errors during checkout", "root_cause": "Database connection pool exhaustion", "resolution": "Increase pool size"},
        {"incident_id": "INC-2", "title": "Cache outage", "description": "Cache invalidation failed", "root_cause": "Cache node memory pressure", "resolution": "Restart cache cluster"},
        {"incident_id": "INC-3", "title": "Login issue", "description": "Authentication timeouts", "root_cause": "Identity service degradation", "resolution": "Restart identity service"},
    ]

    store.create_index(embeddings, metadata)
    store.save()
    store.load()

    results = store.search(embedder.embed_query("Payment checkout returns HTTP 500 errors"), top_k=5)

    assert len(results) == 3
    assert results[0]["incident_id"] == "INC-1"
    assert results[0]["similarity_score"] >= results[1]["similarity_score"] >= results[2]["similarity_score"]
    assert -1.0 <= results[0]["similarity_score"] <= 1.0


def test_empty_index_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(vector_store_module, "INCIDENT_VECTOR_DB_DIR", str(tmp_path))

    retriever = Retriever()

    with pytest.raises(RuntimeError):
        retriever.retrieve("Any query")
