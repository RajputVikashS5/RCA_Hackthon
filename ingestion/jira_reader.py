from __future__ import annotations

import gzip
from pathlib import Path
from typing import Any, Iterator
from zipfile import ZipFile

try:
    from bson import decode_file_iter
    import bson
except ImportError:  # pragma: no cover - dependency is required for ingestion
    decode_file_iter = None
    bson = None


def _archive_path(source: Path) -> Path:
    if source.is_file():
        return source
    archives = sorted(source.glob("*.zip"))
    if not archives:
        bson_files = sorted(source.rglob("*.bson")) + sorted(source.rglob("*.bson.gz")) + sorted(source.rglob("*.archive"))
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
    candidates = [
        name for name in names
        if name.lower().endswith((".bson", ".archive")) or "mongodump" in name.lower()
    ]
    if collection:
        matches = [name for name in candidates if Path(name).stem.lower() == collection.lower()]
        if matches:
            return matches[0]
    priorities = (
        "mongodump-jirareposanon.archive",
        "issues.bson",
        "issue.bson",
        "jira_issue.bson",
        "jira.bson",
    )
    for priority in priorities:
        matches = [name for name in candidates if Path(name).name.lower() == priority]
        if matches:
            return matches[0]
    issue_matches = [
        name for name in candidates
        if any(token in Path(name).name.lower() for token in ("issue", "jira", "dump", "archive"))
    ]
    if issue_matches:
        return issue_matches[0]
    if candidates:
        return candidates[0]
    raise FileNotFoundError("No Jira issue BSON or archive collection was found in the archive.")


def _iter_stream_bson(handle: Any, max_records: int | None = None, skip_records: int = 0) -> Iterator[dict[str, Any]]:
    if bson is None:
        raise RuntimeError("pymongo is required to read BSON files.")
    buf = bytearray()
    yielded = 0
    skipped = 0
    while True:
        chunk = handle.read(1024 * 1024)
        if not chunk:
            break
        buf.extend(chunk)
        offset = 0
        while offset < len(buf):
            if offset + 4 > len(buf):
                break
            doc_len = int.from_bytes(buf[offset:offset+4], "little")
            if doc_len <= 4:
                offset += 1
                continue
            if offset + doc_len > len(buf):
                break
            try:
                doc = bson.BSON(buf[offset:offset+doc_len]).decode()
                offset += doc_len
                if isinstance(doc, dict) and ("key" in doc or "fields" in doc or "summary" in doc or "description" in doc):
                    if skipped < skip_records:
                        skipped += 1
                        continue
                    yield doc
                    yielded += 1
                    if max_records is not None and max_records > 0 and yielded >= max_records:
                        return
            except Exception:
                offset += 1
        buf = buf[offset:]


def iter_issue_documents(
    source: Path,
    *,
    collection: str | None = None,
    max_records: int | None = None,
    skip_records: int = 0,
) -> Iterator[dict[str, Any]]:
    if decode_file_iter is None or bson is None:
        raise RuntimeError("pymongo is required to read BSON files.")
    path = _archive_path(source)
    yielded = 0
    skipped = 0
    if path.suffix.lower() == ".zip":
        with ZipFile(path) as archive:
            member = _issue_member(archive.namelist(), collection)
            with archive.open(member, "r") as raw_handle:
                header = raw_handle.read(2)
                raw_handle.seek(0)
                if header == b"\x1f\x8b" or member.lower().endswith(".archive"):
                    with gzip.GzipFile(fileobj=raw_handle) as gz_handle:
                        for record in _iter_stream_bson(gz_handle, max_records=max_records, skip_records=skip_records):
                            yield record
                else:
                    try:
                        records = decode_file_iter(raw_handle)
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
