from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from typing import Any, Iterator
from zipfile import ZipFile

try:
    from bson import decode_file_iter
except ImportError:  # pragma: no cover - dependency is required for ingestion
    decode_file_iter = None


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value[:20]]
    return str(value)


def _fields(records: list[dict[str, Any]]) -> list[str]:
    names: set[str] = set()
    for record in records:
        names.update(str(key) for key in record)
    return sorted(names)


def _collection_name(path: Path) -> str:
    name = path.name
    for suffix in (".bson.gz", ".bson", ".gz"):
        if name.lower().endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name or path.stem


def _bson_records(handle: Any, sample_size: int) -> Iterator[dict[str, Any]]:
    if decode_file_iter is None:
        raise RuntimeError("pymongo is required to inspect BSON files.")
    for index, record in enumerate(decode_file_iter(handle)):
        if index >= sample_size:
            return
        if isinstance(record, dict):
            yield record


def _inspect_zip(path: Path, sample_size: int) -> dict[str, Any]:
    with ZipFile(path) as archive:
        members = [item for item in archive.infolist() if not item.is_dir()]
        bson_members = [item for item in members if item.filename.lower().endswith(".bson")]
        bson_members.sort(key=lambda item: ("issue" not in Path(item.filename).stem.lower(), item.filename.lower()))
        collections = [Path(item.filename).stem for item in bson_members]
        samples: list[dict[str, Any]] = []
        collection_details: list[dict[str, Any]] = []
        for member in bson_members:
            if len(samples) >= sample_size:
                break
            with archive.open(member, "r") as handle:
                records = list(_bson_records(handle, min(sample_size, sample_size - len(samples))))
            samples.extend(records)
            collection_details.append(
                {
                    "name": Path(member.filename).stem,
                    "archive_member": member.filename,
                    "sample_count": len(records),
                    "fields": _fields(records),
                    "sample_records": [_json_safe(item) for item in records[:sample_size]],
                }
            )
        return {
            "path": str(path),
            "archive_type": "mongodb",
            "collections": collections,
            "bson_files": [item.filename for item in bson_members],
            "collection_details": collection_details,
            "sample_records": [_json_safe(item) for item in samples[:sample_size]],
            "fields": _fields(samples),
            "sample_count": len(samples[:sample_size]),
            "files": [{"name": item.filename, "bytes": item.file_size} for item in members],
        }


def _inspect_bson(path: Path, sample_size: int) -> dict[str, Any]:
    collection_name = _collection_name(path)
    opener = gzip.open if path.name.lower().endswith(".gz") else open
    with opener(path, "rb") as handle:
        records = list(_bson_records(handle, sample_size))
    return {
        "path": str(path),
        "archive_type": "mongodb",
        "collections": [collection_name],
        "bson_files": [path.name],
        "collection_details": [{"name": collection_name, "sample_count": len(records), "fields": _fields(records)}],
        "sample_records": [_json_safe(item) for item in records],
        "fields": _fields(records),
        "sample_count": len(records),
        "files": [{"name": path.name, "bytes": path.stat().st_size}],
    }


def inspect_path(path: Path, sample_size: int = 5) -> dict[str, Any]:
    sample_size = max(1, min(int(sample_size), 100))
    if path.suffix.lower() == ".zip":
        return _inspect_zip(path, sample_size)
    if path.name.lower().endswith((".bson", ".bson.gz")):
        return _inspect_bson(path, sample_size)
    if path.is_dir():
        archives = sorted(path.glob("*.zip"))
        if archives:
            return _inspect_zip(archives[0], sample_size)
        bson_files = sorted(path.rglob("*.bson")) + sorted(path.rglob("*.bson.gz"))
        if bson_files:
            return _inspect_bson(bson_files[0], sample_size)
    raise ValueError(f"No ZIP or BSON MongoDB archive found at {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a bounded sample of a Jira MongoDB archive.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--sample-size", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(inspect_path(args.path, args.sample_size), indent=2, ensure_ascii=False))
