from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
for path in (PROJECT_ROOT, BACKEND_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.config import (  # noqa: E402
    EMBEDDING_DIMENSION,
    JIRA_DATA_DIR,
    ZENODO_RECORD_ID,
    ZENODO_RECORD_URL,
)
from app.database.connection import get_connection, initialize_database  # noqa: E402
from app.database.repository import IncidentRepository  # noqa: E402
from app.services.embedding import EmbeddingModel  # noqa: E402
from ingestion.download_zenodo import download_latest  # noqa: E402
from ingestion.embedding_pipeline import embed_batch  # noqa: E402
from ingestion.jira_reader import iter_batches  # noqa: E402
from ingestion.jira_transformer import transform_jira_issues  # noqa: E402
from ingestion.postgres_loader import upsert_batch  # noqa: E402


SOURCE = "zenodo"


def find_archive(data_dir: Path) -> Path | None:
    candidates = sorted(data_dir.rglob("*.bson.gz")) + sorted(data_dir.rglob("*.bson"))
    return candidates[0] if candidates else None


def source_count() -> int:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM incidents WHERE source = %s", (SOURCE,))
            return int(cursor.fetchone()[0])


def ingest_zenodo(
    source: Path,
    *,
    target_count: int,
    batch_size: int,
    source_url: str,
) -> dict[str, int]:
    initialize_database()
    repository = IncidentRepository()
    embedder = EmbeddingModel()
    processed = valid = inserted = already_existing = skipped = failed = 0
    seen: set[str] = set()
    current_source_count = source_count()

    if current_source_count >= target_count:
        return {
            "processed": 0,
            "inserted": 0,
            "skipped": 0,
            "failed": 0,
            "postgres_total": current_source_count,
            "zenodo_total": current_source_count,
        }

    for raw_batch in iter_batches(source, batch_size=batch_size, max_records=None):
        transformed = list(transform_jira_issues(raw_batch, source_url=source_url))
        skipped += len(raw_batch) - len(transformed)
        valid += len(transformed)
        keys = []
        unique: list[dict[str, Any]] = []
        for record in transformed:
            key = str(record["incident_id"]).strip().casefold()
            if not key or key in seen:
                skipped += 1
                continue
            seen.add(key)
            keys.append(record["incident_id"])
            unique.append(record)

        existing = repository.existing_incident_ids(keys)
        new_records = [record for record in unique if record["incident_id"] not in existing]
        already_existing += len(unique) - len(new_records)
        remaining = max(0, target_count - current_source_count)
        new_records = new_records[:remaining]
        processed += len(raw_batch)

        if new_records:
            embedded, embedding_failures = embed_batch(new_records, embedder)
            failed += len(embedding_failures)
            bad_dimensions = [
                record for record in embedded
                if len(record.get("embedding", [])) != EMBEDDING_DIMENSION
            ]
            if bad_dimensions:
                failed += len(bad_dimensions)
                embedded = [record for record in embedded if record not in bad_dimensions]
            if embedded:
                inserted += upsert_batch(embedded, repository)

        current_source_count = source_count()
        print(
            f"Downloaded/processed: {processed}\n"
            f"Valid incidents: {valid}\n"
            f"Inserted: {inserted}\n"
            f"Already existing: {already_existing}\n"
            f"Skipped: {skipped}\n"
            f"Failed: {failed}\n"
            f"PostgreSQL Zenodo incidents: {current_source_count}",
            flush=True,
        )
        if current_source_count >= target_count:
            break

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM incidents")
            total = int(cursor.fetchone()[0])
    return {
        "processed": processed,
        "valid": valid,
        "inserted": inserted,
        "already_existing": already_existing,
        "skipped": skipped,
        "failed": failed,
        "postgres_total": total,
        "zenodo_total": source_count(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Incrementally ingest Zenodo Jira incidents into PostgreSQL.")
    parser.add_argument("--max-records", type=int, default=5000, help="Target number of Zenodo incidents in PostgreSQL.")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--data-dir", type=Path, default=Path(JIRA_DATA_DIR))
    parser.add_argument("--record-id", default=ZENODO_RECORD_ID)
    args = parser.parse_args()
    if args.max_records <= 0 or args.batch_size <= 0:
        parser.error("--max-records and --batch-size must be positive.")

    source = find_archive(args.data_dir)
    if source is None:
        source = download_latest(args.data_dir, f"{ZENODO_RECORD_URL.rstrip('/')}")
    result = ingest_zenodo(
        source,
        target_count=args.max_records,
        batch_size=args.batch_size,
        source_url=f"https://zenodo.org/records/{args.record_id}",
    )
    print(result)


if __name__ == "__main__":
    main()
