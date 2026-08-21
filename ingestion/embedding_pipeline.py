from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Iterable

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.embedding import EmbeddingModel


def embed_batch(records: list[dict[str, Any]], embedder: EmbeddingModel | None = None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not records:
        return [], []
    model = embedder or EmbeddingModel()
    try:
        vectors = model.embed_documents([record.get("search_text", "") for record in records])
    except Exception:
        return [], records
    embedded = []
    failed = []
    for record, vector in zip(records, vectors):
        try:
            updated = dict(record)
            updated["embedding"] = vector.tolist()
            updated.pop("search_text", None)
            embedded.append(updated)
        except Exception:
            failed.append(record)
    return embedded, failed


def embed_records(records: Iterable[dict[str, Any]], batch_size: int = 100) -> Iterable[dict[str, Any]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    batch: list[dict[str, Any]] = []
    model = EmbeddingModel()
    for record in records:
        batch.append(record)
        if len(batch) >= batch_size:
            embedded, _ = embed_batch(batch, model)
            yield from embedded
            batch = []
    if batch:
        embedded, _ = embed_batch(batch, model)
        yield from embedded
