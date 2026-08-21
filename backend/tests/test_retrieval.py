import numpy as np

from app.services.database_retriever import DatabaseRetriever


class FakeEmbeddingModel:
    def embed_query(self, question):
        return np.ones(384, dtype=np.float32)


class FakeRepository:
    def search(self, embedding, top_k=5):
        assert len(embedding) == 384
        return [
            {"incident_id": "INC-1", "similarity_score": 0.92},
            {"incident_id": "INC-2", "similarity_score": 0.71},
        ][:top_k]


def test_database_retriever_returns_repository_ordered_results():
    retriever = DatabaseRetriever(repository=FakeRepository())
    retriever.embedding_model = FakeEmbeddingModel()

    results = retriever.retrieve("Payment checkout fails", top_k=5)

    assert [item["incident_id"] for item in results] == ["INC-1", "INC-2"]
    assert results[0]["similarity_score"] > results[1]["similarity_score"]


def test_database_retriever_supports_no_results():
    class EmptyRepository:
        def search(self, embedding, top_k=5):
            return []

    retriever = DatabaseRetriever(repository=EmptyRepository())
    retriever.embedding_model = FakeEmbeddingModel()

    assert retriever.retrieve("No matching incident") == []


def test_database_retriever_filters_low_similarity_matches():
    class MixedRepository:
        def search(self, embedding, top_k=5):
            return [
                {"incident_id": "INC-relevant", "similarity_score": 0.35},
                {"incident_id": "INC-irrelevant", "similarity_score": 0.34},
            ]

    retriever = DatabaseRetriever(repository=MixedRepository())
    retriever.embedding_model = FakeEmbeddingModel()

    assert [item["incident_id"] for item in retriever.retrieve("Payment outage")] == ["INC-relevant"]
