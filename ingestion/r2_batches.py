from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import tempfile
from typing import Any, Iterator

from app.config import R2_BATCH_CATALOG_KEY, R2_BATCH_PREFIX, R2_CATALOG_MAX_BYTES
from app.services.r2_storage import R2Storage


def _record_id(record: dict[str, Any]) -> str:
    fields = record.get("fields") if isinstance(record.get("fields"), dict) else record
    return str(record.get("key") or record.get("issue_key") or fields.get("key") or record.get("id") or "").strip()


def read_jsonl(handle: Any) -> Iterator[dict[str, Any]]:
    for line in handle:
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            yield value


def load_batch_catalog(storage: R2Storage, key: str = R2_BATCH_CATALOG_KEY) -> dict[str, Any]:
    metadata = storage.object_metadata(key)
    size = int(metadata.get("ContentLength") or metadata.get("content_length") or 0)
    if size > R2_CATALOG_MAX_BYTES:
        raise RuntimeError(f"Prepared R2 catalog exceeds {R2_CATALOG_MAX_BYTES} bytes.")
    body = storage.get_object(key).get("Body")
    if body is None:
        raise RuntimeError("Prepared R2 catalog has no response body.")
    try:
        payload = json.loads(body.read(R2_CATALOG_MAX_BYTES + 1))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Prepared R2 catalog is not valid JSON.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("batches"), list):
        raise RuntimeError("Prepared R2 catalog must contain a batches array.")
    return payload


def iter_prepared_batches(
    storage: R2Storage,
    *,
    catalog_key: str = R2_BATCH_CATALOG_KEY,
) -> Iterator[tuple[dict[str, Any], Iterator[dict[str, Any]]]]:
    catalog = load_batch_catalog(storage, catalog_key)
    for batch in catalog["batches"]:
        if not isinstance(batch, dict) or not batch.get("object_key"):
            continue
        body = storage.get_object(str(batch["object_key"])).get("Body")
        if body is None:
            raise RuntimeError(f"Prepared R2 batch has no body: {batch['object_key']}")
        yield batch, read_jsonl(body)


@contextmanager
def _jsonl_file(records: list[dict[str, Any]]) -> Iterator[Path]:
    with tempfile.NamedTemporaryFile(prefix="r2-batch-", suffix=".jsonl", delete=False, mode="w", encoding="utf-8") as handle:
        path = Path(handle.name)
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True, default=str) + "\n")
    try:
        yield path
    finally:
        path.unlink(missing_ok=True)


def prepare_r2_dataset(
    source: Path | None,
    storage: R2Storage,
    *,
    batch_size: int = 1000,
    prefix: str = R2_BATCH_PREFIX,
    catalog_key: str = R2_BATCH_CATALOG_KEY,
    collection: str | None = None,
    max_records: int | None = None,
    r2_object_key: str | None = None,
) -> dict[str, int]:
    if batch_size <= 0:
        raise ValueError("batch_size must be positive")
    from ingestion.jira_reader import iter_issue_documents, iter_r2_issue_documents

    if max_records is not None and max_records < 0:
        raise ValueError("max_records must be non-negative.")
    source_size = source.stat().st_size if source and source.is_file() else (
        storage.object_size(r2_object_key) if r2_object_key else 0
    )
    catalog: dict[str, Any] = {
        "version": 1,
        "source": str(source),
        "source_size": source_size,
        "batches": [],
    }
    records_processed = 0
    records_uploaded = 0
    batch_number = 0
    batch: list[dict[str, Any]] = []
    bytes_read = 0

    def progress(value: int) -> None:
        nonlocal bytes_read
        bytes_read = max(bytes_read, value)

    def upload(records: list[dict[str, Any]]) -> None:
        nonlocal batch_number, records_uploaded
        batch_number += 1
        object_key = f"{prefix.rstrip('/')}/batch-{batch_number:06d}.jsonl"
        ids = [_record_id(record) for record in records]
        with _jsonl_file(records) as path:
            storage.upload_file(path, object_key)
            size = path.stat().st_size
        catalog["batches"].append(
            {
                "object_key": object_key,
                "record_count": len(records),
                "file_size": size,
                "first_incident_id": ids[0] if ids else "",
                "last_incident_id": ids[-1] if ids else "",
                "incident_ids": ids,
            }
        )
        records_uploaded += len(records)
        estimated = f"{records_processed / max(records_processed, 1) * 100:.1f}% of discovered records"
        print(
            f"R2 preparation: records processed={records_processed}, records uploaded={records_uploaded}, "
            f"current batch={batch_number}, bytes processed={size}, estimated progress={estimated}, errors=0",
            flush=True,
        )

    if r2_object_key:
        records = iter_r2_issue_documents(
            storage,
            r2_object_key,
            collection=collection,
            max_records=max_records,
            progress=progress,
        )
    else:
        reader_kwargs = {"collection": collection}
        if max_records is not None:
            reader_kwargs["max_records"] = max_records
        records = iter_issue_documents(source, **reader_kwargs)
    for record in records:
        batch.append(record)
        records_processed += 1
        if len(batch) >= batch_size:
            upload(batch)
            batch = []
    if batch:
        upload(batch)

    with _jsonl_file([catalog]) as path:
        path.write_text(json.dumps(catalog, ensure_ascii=True, default=str), encoding="utf-8")
        storage.upload_file(path, catalog_key)
    return {
        "records_processed": records_processed,
        "records_uploaded": records_uploaded,
        "batches_uploaded": batch_number,
        "bytes_read": bytes_read if r2_object_key else source_size,
        "source_fully_downloaded": bool(not r2_object_key),
    }
