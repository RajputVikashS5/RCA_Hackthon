from __future__ import annotations

import argparse
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import INGEST_BATCH_SIZE, INGEST_MAX_RECORDS
from pipeline import ingest


def load(source: Path, batch_size: int = INGEST_BATCH_SIZE, max_records: int = INGEST_MAX_RECORDS) -> int:
    return ingest(source, batch_size=batch_size, max_records=max_records)["processed"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch-transform, embed, and upsert local Jira data into PostgreSQL.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--batch-size", type=int, default=INGEST_BATCH_SIZE)
    parser.add_argument("--max-records", type=int, default=INGEST_MAX_RECORDS)
    args = parser.parse_args()
    print(f"Loaded {load(args.source, args.batch_size, args.max_records)} incidents.")
