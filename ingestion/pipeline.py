from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import sys
from typing import Any, Iterable

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import INGEST_BATCH_SIZE, INGEST_MAX_RECORDS, JIRA_DATA_DIR, R2_OBJECT_KEY
from app.database.connection import initialize_database
from app.database.repository import IncidentRepository
from app.services.embedding import EmbeddingModel

from ingestion.embedding_pipeline import embed_batch
from ingestion.jira_reader import iter_batches
from ingestion.jira_transformer import transform_jira_issues
from ingestion.postgres_loader import upsert_batch
from ingestion.r2_reader import dataset_file
from ingestion.r2_batches import iter_prepared_batches
from app.services.r2_storage import R2Storage


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
    accepted = 0

    limit = None if max_records == 0 else max_records
    for raw_batch in iter_batches(source, batch_size=batch_size, max_records=limit, collection=collection, skip_records=skip_records):
        stats.discovered += len(raw_batch)
        stats.read += len(raw_batch)
        transformed = []
        for record in transform_jira_issues(raw_batch, source_url=source_url):
            key = record["incident_id"].lower()
            if key in seen:
                continue
            seen.add(key)
            transformed.append(record)
        if max_records > 0:
            remaining = max_records - accepted
            transformed = transformed[:remaining]
        accepted += len(transformed)
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
        if max_records > 0 and accepted >= max_records:
            break
    return stats.as_dict()


def ingest_prepared_r2(
    *,
    batch_size: int = INGEST_BATCH_SIZE,
    max_records: int = INGEST_MAX_RECORDS,
    replace_source: bool = False,
) -> dict[str, int]:
    initialize_database()
    repository = IncidentRepository()
    if replace_source:
        repository.delete_source("zenodo-public-jira-dataset-v7")
    embedder = EmbeddingModel()
    stats = IngestionStats()
    seen: set[str] = set()
    accepted = 0
    storage = R2Storage()
    for _, raw_records in iter_prepared_batches(storage):
        raw_batch: list[dict[str, Any]] = []
        for raw in raw_records:
            raw_batch.append(raw)
            if len(raw_batch) >= batch_size:
                result = _ingest_prepared_batch(raw_batch, repository, embedder, seen, stats, max_records - accepted if max_records > 0 else None)
                accepted += result
                raw_batch = []
                if max_records > 0 and accepted >= max_records:
                    return stats.as_dict()
        if raw_batch:
            accepted += _ingest_prepared_batch(raw_batch, repository, embedder, seen, stats, max_records - accepted if max_records > 0 else None)
        if max_records > 0 and accepted >= max_records:
            break
    return stats.as_dict()


def _ingest_prepared_batch(raw_batch, repository, embedder, seen, stats, remaining):
    transformed = []
    for record in transform_jira_issues(raw_batch):
        key = record["incident_id"].casefold()
        if key in seen:
            stats.skipped += 1
            continue
        seen.add(key)
        transformed.append(record)
    if remaining is not None:
        transformed = transformed[:remaining]
    if not transformed:
        return 0
    existing = repository.existing_incident_ids([record["incident_id"] for record in transformed])
    transformed = [record for record in transformed if record["incident_id"] not in existing]
    stats.transformed += len(transformed)
    stats.discovered += len(raw_batch)
    stats.read += len(raw_batch)
    embedded, failed = embed_batch(transformed, embedder)
    stats.failed += len(failed)
    stats.embeddings += len(embedded)
    if embedded:
        count = upsert_batch(embedded, repository)
        stats.inserted += count
        stats.processed += count
        return len(transformed)
    return 0


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Ingest Jira incidents into PostgreSQL + pgvector.")
    parser.add_argument("source", type=Path, nargs="?", default=Path(JIRA_DATA_DIR), help="Local BSON/ZIP path (used with --source local).")
    parser.add_argument("--source", choices=("local", "r2"), default="local", dest="source_type")
    parser.add_argument("--r2-key", default=R2_OBJECT_KEY, help="R2 object key (used with --source r2).")
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
    if args.source_type == "r2":
        result = ingest_prepared_r2(
            batch_size=args.batch_size,
            max_records=args.max_records,
            replace_source=args.replace_source,
        )
    else:
        if args.source is None:
            parser.error("a local source path is required when --source local is selected")
        result = ingest(
            args.source,
            batch_size=args.batch_size,
            max_records=args.max_records,
            collection=args.collection,
            replace_source=args.replace_source,
            skip_records=args.skip_records,
        )
    result["source"] = args.source_type
    result["dataset"] = "prepared-r2-jsonl" if args.source_type == "r2" else str(args.source)
    result["status"] = "completed"
    print(json.dumps(result, indent=2))
