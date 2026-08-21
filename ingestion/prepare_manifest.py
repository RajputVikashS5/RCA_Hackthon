from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict

from ingestion.zenodo_client import ZenodoClient, ZenodoClientError
from app.config import JIRA_DATA_DIR


def prepare_manifest(record_id: str, only_bson: bool = False) -> Dict[str, Any]:
    client = ZenodoClient()
    record = client.get_record(record_id)
    files = client.list_files(record)
    bson_files = client.bson_files(files)

    if only_bson:
        selected_files = bson_files
    else:
        selected_files = files

    record_dir = Path(JIRA_DATA_DIR) / str(record_id)
    record_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = record_dir / "manifest.json"

    manifest: Dict[str, Any] = {
        "record_id": str(record.get("id") or record_id),
        "title": (record.get("metadata") or {}).get("title"),
        "doi": (record.get("metadata") or {}).get("doi"),
        "files": selected_files,
        "bson_files": bson_files,
    }

    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    return {"manifest_path": str(manifest_path), "record_dir": str(record_dir)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare a local manifest for a Zenodo record (metadata-only).")
    parser.add_argument("record_id", help="Zenodo record ID to prepare manifest for")
    parser.add_argument("--only-bson", action="store_true", help="Only include BSON-like files in the manifest")
    args = parser.parse_args(argv)

    try:
        result = prepare_manifest(args.record_id, only_bson=args.only_bson)
        print("Manifest written:", result["manifest_path"])
        return 0
    except ZenodoClientError as exc:
        print("Unable to fetch Zenodo metadata:", exc)
        return 2
    except Exception as exc:  # pragma: no cover - defensive
        print("Unexpected error:", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
