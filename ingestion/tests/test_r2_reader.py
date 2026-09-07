from __future__ import annotations

from pathlib import Path

from ingestion.r2_reader import dataset_file


class FakeStorage:
    def download_file(self, key, destination):
        Path(destination).write_bytes(b"temporary dataset")
        return Path(destination)


def test_r2_reader_cleans_up_temporary_file():
    with dataset_file("raw/test.zip", storage=FakeStorage()) as path:
        assert path.read_bytes() == b"temporary dataset"
        temporary_path = path
    assert not temporary_path.exists()
