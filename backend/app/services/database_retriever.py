from __future__ import annotations

from app.config import DEFAULT_TOP_K
from app.database.repository import IncidentRepository
from app.services.embedding import EmbeddingModel


class DatabaseRetriever:
    def __init__(self, repository: IncidentRepository | None = None):
        self.embedding_model = EmbeddingModel()
        self.repository = repository or IncidentRepository()

    def retrieve(self, question: str, top_k: int = DEFAULT_TOP_K) -> list[dict]:
        query_embedding = self.embedding_model.embed_query(question)
        return self.repository.search(query_embedding, top_k=top_k)
