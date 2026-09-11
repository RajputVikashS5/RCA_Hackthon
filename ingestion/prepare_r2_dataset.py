from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import JIRA_DATA_DIR, R2_OBJECT_KEY
from ingestion.r2_batches import prepare_r2_dataset
from app.services.r2_storage import R2Storage


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare the R2 Jira ZIP into incremental JSONL batches.")
    parser.add_argument("--source", choices=("r2", "local"), default="r2")
    parser.add_argument("path", type=Path, nargs="?", default=Path(JIRA_DATA_DIR))
    parser.add_argument("--r2-key", default=R2_OBJECT_KEY)
    parser.add_argument("--batch-size", type=int, default=1000)
    parser.add_argument("--collection")
    parser.add_argument("--max-records", type=int)
    parser.add_argument("--prefix")
    parser.add_argument("--catalog-key")
    args = parser.parse_args()
    storage = R2Storage()
    if args.source == "r2":
        from app.config import R2_BATCH_CATALOG_KEY, R2_BATCH_PREFIX
        catalog_key = args.catalog_key or R2_BATCH_CATALOG_KEY
        prefix = args.prefix or R2_BATCH_PREFIX
        if storage.object_exists(catalog_key):
            parser.error(f"{catalog_key} already exists; choose a new --catalog-key.")
        if storage.list_objects(prefix):
            parser.error(f"R2 already contains objects under {prefix}; choose a new --prefix.")
        result = prepare_r2_dataset(
            None,
            storage,
            batch_size=args.batch_size,
            collection=args.collection,
            max_records=args.max_records,
            r2_object_key=args.r2_key,
            prefix=prefix,
            catalog_key=catalog_key,
        )
    else:
        result = prepare_r2_dataset(
            args.path,
            storage,
            batch_size=args.batch_size,
            collection=args.collection,
            max_records=args.max_records,
            prefix=args.prefix or "incidents/",
        )
    print(result)


if __name__ == "__main__":
    main()
