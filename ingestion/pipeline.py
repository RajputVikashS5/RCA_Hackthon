from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import INGEST_BATCH_SIZE, INGEST_MAX_RECORDS
from app.database.connection import initialize_database
from app.database.repository import IncidentRepository
from app.services.embedding import EmbeddingModel

from ingestion.embedding_pipeline import embed_batch
from ingestion.jira_reader import iter_batches
from ingestion.jira_transformer import transform_jira_issues
from ingestion.postgres_loader import upsert_batch


@dataclass
class IngestionStats:
    discovered: int = 0
    read: int = 0
    transformed: int = 0
    processed: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    embeddings: int = 0
    failed: int = 0

    def as_dict(self) -> dict[str, int]:
        return asdict(self)


def ingest(
    source: Path,
    *,
    batch_size: int = INGEST_BATCH_SIZE,
    max_records: int = INGEST_MAX_RECORDS,
    collection: str | None = None,
    source_url: str | None = None,
    initialize: bool = True,
    replace_source: bool = False,
    skip_records: int = 0,
) -> dict[str, int]:
    if initialize:
        initialize_database()
    repository = IncidentRepository()
    if replace_source:
        repository.delete_source("zenodo-public-jira-dataset-v7")
    embedder = EmbeddingModel()
    stats = IngestionStats()
    seen: set[str] = set()

    for raw_batch in iter_batches(source, batch_size=batch_size, max_records=max_records, collection=collection, skip_records=skip_records):
        stats.discovered += len(raw_batch)
        stats.read += len(raw_batch)
        transformed = []
        for record in transform_jira_issues(raw_batch, source_url=source_url):
            key = record["incident_id"].lower()
            if key in seen:
                continue
            seen.add(key)
            transformed.append(record)
        stats.transformed += len(transformed)
        stats.skipped += len(raw_batch) - len(transformed)
        embedded, failed = embed_batch(transformed, embedder)
        stats.failed += len(failed)
        stats.embeddings += len(embedded)
        if not embedded:
            continue
        try:
            count = upsert_batch(embedded, repository)
        except Exception:
            stats.failed += len(embedded)
            continue
        stats.inserted += count
        stats.processed += count
    return stats.as_dict()


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Ingest bounded Jira BSON batches into PostgreSQL + pgvector.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--batch-size", type=int, default=INGEST_BATCH_SIZE)
    parser.add_argument("--max-records", type=int, default=INGEST_MAX_RECORDS)
    parser.add_argument("--collection")
    parser.add_argument("--skip-records", type=int, default=0)
    parser.add_argument(
        "--replace-source",
        action="store_true",
        help="Delete existing Apache Jira records before rebuilding this source.",
    )
    args = parser.parse_args()
    print(json.dumps(ingest(args.source, batch_size=args.batch_size, max_records=args.max_records, collection=args.collection, replace_source=args.replace_source, skip_records=args.skip_records), indent=2))
