from __future__ import annotations

import io
import json
from pathlib import Path

from ingestion import r2_batches
from ingestion.jira_reader import R2RangeReader


class FakeStorage:
    def __init__(self) -> None:
        self.objects: dict[str, bytes] = {}

    def upload_file(self, path: Path, key: str) -> None:
        self.objects[key] = path.read_bytes()

    def object_metadata(self, key: str) -> dict[str, int]:
        return {"ContentLength": len(self.objects[key])}

    def get_object(self, key: str) -> dict[str, io.BytesIO]:
        return {"Body": io.BytesIO(self.objects[key])}


def test_prepare_writes_jsonl_batches_and_catalog(monkeypatch, tmp_path):
    records = [{"key": f"INC-{index}", "fields": {"summary": f"Title {index}"}} for index in range(3)]
    monkeypatch.setattr(r2_batches, "R2_BATCH_PREFIX", "incidents")
    monkeypatch.setattr(
        "ingestion.jira_reader.iter_issue_documents",
        lambda source, collection=None: iter(records),
    )
    storage = FakeStorage()
    source = tmp_path / "source.zip"
    source.write_bytes(b"source")

    result = r2_batches.prepare_r2_dataset(
        source,
        storage,
        batch_size=2,
        prefix="incidents",
        catalog_key="catalog.json",
    )

    assert result["records_processed"] == 3
    assert result["records_uploaded"] == 3
    assert result["batches_uploaded"] == 2
    assert result["source_fully_downloaded"] is True
    catalog = json.loads(storage.objects["catalog.json"])
    assert [batch["record_count"] for batch in catalog["batches"]] == [2, 1]
    assert json.loads(storage.objects["incidents/batch-000001.jsonl"].splitlines()[0])["key"] == "INC-0"


def test_prepared_batches_stream_jsonl_objects():
    storage = FakeStorage()
    storage.objects["catalog.json"] = json.dumps(
        {"version": 1, "batches": [{"object_key": "batch.jsonl", "record_count": 2}]}
    ).encode()
    storage.objects["batch.jsonl"] = b'{"key":"INC-1"}\n{"key":"INC-2"}\n'

    batches = list(r2_batches.iter_prepared_batches(storage, catalog_key="catalog.json"))

    assert list(batches[0][1]) == [{"key": "INC-1"}, {"key": "INC-2"}]


def test_r2_range_reader_reads_only_requested_ranges():
    class RangeStorage:
        def __init__(self):
            self.data = b"0123456789" * 10
            self.ranges = []

        def read_range(self, key, start, end):
            self.ranges.append((start, end))
            return self.data[start:end + 1]

    storage = RangeStorage()
    reader = R2RangeReader(storage, "source.zip", len(storage.data), chunk_size=10)

    assert reader.read(5) == b"01234"
    assert reader.bytes_read == 10
    assert reader.read(5) == b"56789"
    assert len(storage.ranges) == 1
