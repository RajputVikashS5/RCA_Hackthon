from __future__ import annotations

from pathlib import Path

import pytest

from app.services.r2_storage import R2Storage, R2StorageError


class MissingObjectError(Exception):
    response = {"Error": {"Code": "404"}}


class FakeR2Client:
    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def upload_file(self, filename, bucket, key, **kwargs):
        self.objects[key] = Path(filename).read_bytes()

    def download_file(self, bucket, key, filename):
        if key not in self.objects:
            raise MissingObjectError()
        Path(filename).write_bytes(self.objects[key])

    def head_object(self, Bucket, Key):
        if Key not in self.objects:
            raise MissingObjectError()
        return {"ContentLength": len(self.objects[Key])}

    def get_object(self, Bucket, Key):
        import io
        if Key not in self.objects:
            raise MissingObjectError()
        return {"Body": io.BytesIO(self.objects[Key])}

    def head_bucket(self, Bucket):
        return {}

    def delete_object(self, Bucket, Key):
        self.objects.pop(Key, None)


def test_upload_download_and_missing_object(tmp_path):
    client = FakeR2Client()
    storage = R2Storage(client=client)
    source = tmp_path / "small.txt"
    destination = tmp_path / "downloaded.txt"
    source.write_text("r2 test", encoding="utf-8")

    storage.upload_file(source, "test/small.txt")

    assert storage.object_exists("test/small.txt")
    storage.download_file("test/small.txt", destination)
    assert destination.read_text(encoding="utf-8") == "r2 test"
    assert not storage.object_exists("missing.txt")


def test_unconfigured_storage_fails_without_exposing_credentials():
    storage = R2Storage()
    if storage.configured:
        pytest.skip("R2 credentials are configured in the test environment")
    with pytest.raises(R2StorageError, match="R2 is not configured"):
        storage.object_exists("raw/issues.bson.gz")
