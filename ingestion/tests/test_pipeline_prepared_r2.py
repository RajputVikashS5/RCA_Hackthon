from __future__ import annotations

import io
import json

from ingestion import pipeline


class FakeStorage:
    def __init__(self) -> None:
        self.download_called = False
        self.objects = {
            "incidents/catalog.json": json.dumps(
                {
                    "version": 1,
                    "batches": [
                        {"object_key": "incidents/batch-000001.jsonl", "record_count": 3}
                    ],
                }
            ).encode(),
            "incidents/batch-000001.jsonl": b"".join(
                (
                    json.dumps(
                        {
                            "key": f"INC-{index}",
                            "fields": {
                                "summary": f"Incident {index}",
                                "description": "database connection failure",
                            },
                        }
                    ).encode()
                    + b"\n"
                )
                for index in range(3)
            ),
        }

    def object_metadata(self, key):
        return {"ContentLength": len(self.objects[key])}

    def get_object(self, key):
        return {"Body": io.BytesIO(self.objects[key])}

    def download_file(self, key, destination):
        self.download_called = True
        raise AssertionError("normal prepared ingestion must not download the raw ZIP")


class FakeRepository:
    def __init__(self):
        self.ids = {"INC-0"}

    def existing_incident_ids(self, ids):
        return self.ids.intersection(ids)


def test_prepared_r2_ingestion_is_incremental_and_deduplicated(monkeypatch):
    repository = FakeRepository()
    storage = FakeStorage()
    inserted = []

    monkeypatch.setattr(pipeline, "initialize_database", lambda: None)
    monkeypatch.setattr(pipeline, "IncidentRepository", lambda: repository)
    monkeypatch.setattr(pipeline, "R2Storage", lambda: storage)
    monkeypatch.setattr(pipeline, "EmbeddingModel", lambda: object())
    monkeypatch.setattr(
        pipeline,
        "embed_batch",
        lambda records, embedder: ([{**record, "embedding": [0.0] * 384} for record in records], []),
    )
    def fake_upsert(records, repository):
        inserted.extend(records)
        repository.ids.update(record["incident_id"] for record in records)
        return len(records)

    monkeypatch.setattr(pipeline, "upsert_batch", fake_upsert)

    first = pipeline.ingest_prepared_r2(batch_size=2, max_records=2)
    second = pipeline.ingest_prepared_r2(batch_size=2, max_records=2)

    assert first["processed"] == 2
    assert second["processed"] == 0
    assert [record["incident_id"] for record in inserted] == ["INC-1", "INC-2"]
    assert not storage.download_called
