from __future__ import annotations

import io
import json

from app.services.dataset_service import DatasetService
from app.services.r2_storage import R2Storage
from ingestion.dataset_manifest import build_manifest, calculate_sha256, validate_manifest


class FakeClient:
    def __init__(self):
        self.objects = {
            "jira/2025-06-23 ThePublicJiraDataset.zip": b"dataset",
            "dataset-manifest.json": json.dumps({
                "dataset_name": "Apache Jira",
                "dataset_version": "1.0",
                "source": "Zenodo",
                "storage": "cloudflare-r2",
                "files": [{
                    "name": "2025-06-23 ThePublicJiraDataset.zip",
                    "object_key": "jira/2025-06-23 ThePublicJiraDataset.zip",
                    "size_bytes": 7,
                }],
            }).encode(),
        }

    def head_bucket(self, Bucket):
        return {}

    def head_object(self, Bucket, Key):
        if Key not in self.objects:
            error = RuntimeError()
            error.response = {"Error": {"Code": "404"}}
            raise error
        return {}

    def get_paginator(self, name):
        class Paginator:
            def __init__(self, objects):
                self.objects = objects

            def paginate(self, Bucket, Prefix):
                yield {"Contents": [{"Key": key, "Size": len(value)} for key, value in self.objects.items() if key.startswith(Prefix)]}
        return Paginator(self.objects)

    def get_object(self, Bucket, Key):
        return {"Body": io.BytesIO(self.objects[Key])}


def test_dataset_status_reads_manifest_and_object_metadata():
    service = DatasetService(R2Storage(client=FakeClient()))

    status = service.status()
    metadata = service.metadata()

    assert status["dataset_available"] is True
    assert metadata["dataset_name"] == "Apache Jira"
    assert metadata["files"][0]["object_key"] == "jira/2025-06-23 ThePublicJiraDataset.zip"


def test_manifest_validation_and_streaming_checksum(tmp_path):
    path = tmp_path / "dataset.bin"
    path.write_bytes(b"abc")
    manifest = build_manifest(path, object_key="raw/dataset.bin")

    assert manifest["files"][0]["sha256"] == calculate_sha256(path)
    assert validate_manifest(manifest) is manifest
