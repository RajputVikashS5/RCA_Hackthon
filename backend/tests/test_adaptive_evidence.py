from __future__ import annotations

import io
import json

import numpy as np

from app.services.adaptive_evidence import (
    AdaptiveEvidenceService,
    R2CandidateDiscovery,
    evaluate_evidence,
)
from app.services.r2_storage import R2Storage


class CatalogClient:
    def __init__(self, payload: dict):
        self.payload = json.dumps(payload).encode()

    def head_object(self, Bucket, Key):
        return {"ContentLength": len(self.payload)}

    def get_object(self, Bucket, Key):
        return {"Body": io.BytesIO(self.payload)}


def test_evidence_strength_rewards_agreeing_documented_incidents():
    result = evaluate_evidence(
        [
            {"similarity_score": 0.78, "root_cause": "pool exhaustion", "resolution": "increase pool"},
            {"similarity_score": 0.74, "root_cause": "pool exhaustion", "resolution": "restart workers"},
        ]
    )

    assert result.state == "STRONG"
    assert result.incidents_with_root_cause == 2


def test_r2_catalog_search_is_bounded_and_does_not_read_dataset_archive():
    storage = R2Storage(
        client=CatalogClient(
            {
                "incidents": [
                    {
                        "incident_id": "PAY-1001",
                        "summary": "Payment checkout returns HTTP 500",
                        "description": "Database connection pool failures",
                        "root_cause": "Connection pool exhaustion",
                        "resolution": "Increase pool size",
                    }
                ]
            }
        )
    )
    discovery = R2CandidateDiscovery(storage=storage, catalog_key="catalog.json", max_candidates=1)

    matches = discovery.search({"description": "production payment HTTP 500 database failures"})

    assert [match["incident_id"] for match in matches] == ["PAY-1001"]
    assert matches[0]["metadata"]["provenance"] == "r2-adaptive"


def test_adaptive_retrieval_ingests_candidates_and_runs_second_search():
    class Embedder:
        def embed_documents(self, texts):
            return np.ones((len(texts), 384), dtype=np.float32)

    class Repository:
        def __init__(self):
            self.records = []

        def existing_incident_ids(self, ids):
            return set()

        def upsert_batch(self, records):
            self.records.extend(records)

    class Retriever:
        def __init__(self, repository):
            self.repository = repository
            self.calls = 0

        def retrieve(self, query, top_k=5):
            self.calls += 1
            return (
                [{"incident_id": "PAY-1001", "similarity_score": 0.9, "root_cause": "pool exhaustion", "resolution": "increase pool"}]
                if self.calls > 1
                else [{"incident_id": "weak", "similarity_score": 0.36, "root_cause": "unclear", "resolution": "unclear"}]
            )

    class Discovery:
        def search(self, incident):
            return [{
                "incident_id": "PAY-1001",
                "title": "Payment failure",
                "description": "Database pool failure",
                "root_cause": "pool exhaustion",
                "resolution": "increase pool",
                "_catalog_score": 0.9,
            }]

    repository = Repository()
    retriever = Retriever(repository)
    service = AdaptiveEvidenceService(
        retriever,
        repository=repository,
        embedding_model=Embedder(),
        discovery=Discovery(),
    )

    result = service.retrieve("payment failure", {"description": "payment failure"})

    assert result.expansion_used is True
    assert result.r2_incidents_ingested == 1
    assert retriever.calls == 2
    assert repository.records[0]["source"] == "r2-adaptive"
