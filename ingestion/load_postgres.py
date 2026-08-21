from __future__ import annotations

import argparse
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import INGEST_BATCH_SIZE, INGEST_MAX_RECORDS
from app.database.connection import initialize_database
from app.database.repository import IncidentRepository
from app.services.embedding import EmbeddingModel
from process_jira import process


def load(source: Path, batch_size: int = INGEST_BATCH_SIZE, max_records: int = INGEST_MAX_RECORDS) -> int:
    initialize_database()
    repository = IncidentRepository()
    embedder = EmbeddingModel()
    batch = []
    loaded = 0
    for record in process(source, max_records=max_records):
        batch.append(record)
        if len(batch) < batch_size:
            continue
        _load_batch(batch, embedder, repository)
        loaded += len(batch)
        batch = []
    if batch:
        _load_batch(batch, embedder, repository)
        loaded += len(batch)
    return loaded


def _load_batch(batch: list[dict], embedder: EmbeddingModel, repository: IncidentRepository) -> None:
    embeddings = embedder.embed_documents([record["search_text"] for record in batch])
    for record, embedding in zip(batch, embeddings):
        record["embedding"] = embedding.tolist()
        record.pop("search_text", None)
    repository.upsert_batch(batch)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch-transform, embed, and upsert local Jira data into PostgreSQL.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--batch-size", type=int, default=INGEST_BATCH_SIZE)
    parser.add_argument("--max-records", type=int, default=INGEST_MAX_RECORDS)
    args = parser.parse_args()
    print(f"Loaded {load(args.source, args.batch_size, args.max_records)} incidents.")
