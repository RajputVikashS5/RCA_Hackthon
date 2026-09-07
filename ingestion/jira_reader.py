from __future__ import annotations

import gzip
from pathlib import Path
from typing import Any, Iterator
from zipfile import ZipFile

try:
    from bson import decode_file_iter
except ImportError:  # pragma: no cover - dependency is required for ingestion
    decode_file_iter = None


def _archive_path(source: Path) -> Path:
    if source.is_file():
        return source
    archives = sorted(source.glob("*.zip"))
    if not archives:
        bson_files = sorted(source.rglob("*.bson")) + sorted(source.rglob("*.bson.gz"))
        if not bson_files:
            raise FileNotFoundError(f"No ZIP or BSON archive found under {source}")
        return bson_files[0]
    explicit = [
        archive for archive in archives
        if any(token in archive.name.lower() for token in ("jira", "issue", "publicjira"))
    ]
    if not explicit:
        raise FileNotFoundError(
            f"No explicit Jira dataset ZIP found under {source}; pass the BSON file or Jira archive path directly."
        )
    return explicit[0]


def _issue_member(names: list[str], collection: str | None = None) -> str:
    bson_names = [name for name in names if name.lower().endswith(".bson")]
    if collection:
        matches = [name for name in bson_names if Path(name).stem.lower() == collection.lower()]
        if matches:
            return matches[0]
    priorities = ("issues.bson", "issue.bson", "jira_issue.bson", "jira.bson")
    for priority in priorities:
        matches = [name for name in bson_names if Path(name).name.lower() == priority]
        if matches:
            return matches[0]
    issue_matches = [name for name in bson_names if "issue" in Path(name).stem.lower()]
    if issue_matches:
        return issue_matches[0]
    raise FileNotFoundError("No Jira issue BSON collection was found in the archive.")


def iter_issue_documents(
    source: Path,
    *,
    collection: str | None = None,
    max_records: int | None = None,
    skip_records: int = 0,
) -> Iterator[dict[str, Any]]:
    if decode_file_iter is None:
        raise RuntimeError("pymongo is required to read BSON files.")
    path = _archive_path(source)
    yielded = 0
    skipped = 0
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            member = _issue_member(archive.namelist(), collection)
            with archive.open(member, "r") as handle:
                try:
                    records = decode_file_iter(handle)
                    for record in records:
                        if not isinstance(record, dict):
                            continue
                        if skipped < skip_records:
                            skipped += 1
                            continue
                        yield record
                        yielded += 1
                        if max_records is not None and max_records > 0 and yielded >= max_records:
                            return
                except Exception as exc:
                    if yielded == 0:
                        raise RuntimeError(f"Unable to parse Jira BSON collection '{member}': {exc}") from exc
        return
    opener = gzip.open if path.name.lower().endswith(".gz") else open
    with opener(path, "rb") as handle:
        for record in decode_file_iter(handle):
            if not isinstance(record, dict):
                continue
            if skipped < skip_records:
                skipped += 1
                continue
            yield record
            yielded += 1
            if max_records is not None and max_records > 0 and yielded >= max_records:
                return


def iter_batches(
    source: Path,
    *,
    batch_size: int = 100,
    max_records: int = 1000,
    collection: str | None = None,
    skip_records: int = 0,
) -> Iterator[list[dict[str, Any]]]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    batch: list[dict[str, Any]] = []
    for record in iter_issue_documents(source, collection=collection, max_records=max_records, skip_records=skip_records):
        batch.append(record)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
