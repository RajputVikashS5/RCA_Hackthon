from pathlib import Path
from zipfile import ZipFile

from bson import BSON

from ingestion.inspect_dataset import inspect_path
from ingestion.jira_reader import iter_batches
from ingestion.jira_transformer import transform_jira_issue


def _archive(path: Path) -> Path:
    payload = b"".join(
        BSON.encode(item)
        for item in (
            {
                "key": "PAY-1",
                "fields": {
                    "summary": "Checkout returns HTTP 500",
                    "description": "Payment requests fail during checkout.",
                    "project": {"key": "PAY"},
                    "components": [{"name": "Checkout"}],
                    "status": {"name": "Resolved"},
                },
            },
            {
                "key": "PAY-2",
                "fields": {"summary": "Connection timeout", "description": "Database pool is exhausted."},
            },
        )
    )
    archive = path / "jira.zip"
    with ZipFile(archive, "w") as output:
        output.writestr("dump/issues.bson", payload)
    return archive


def test_inspector_reports_collection_and_bounded_sample(tmp_path):
    result = inspect_path(_archive(tmp_path), sample_size=1)

    assert result["archive_type"] == "mongodb"
    assert result["collections"] == ["issues"]
    assert result["sample_count"] == 1
    assert result["sample_records"][0]["key"] == "PAY-1"


def test_reader_streams_batches_and_honors_limit(tmp_path):
    batches = list(iter_batches(_archive(tmp_path), batch_size=1, max_records=2))

    assert [len(batch) for batch in batches] == [1, 1]
    assert batches[1][0]["key"] == "PAY-2"


def test_reader_skips_records_before_streaming_batches(tmp_path):
    batches = list(iter_batches(_archive(tmp_path), batch_size=1, max_records=1, skip_records=1))

    assert len(batches) == 1
    assert batches[0][0]["key"] == "PAY-2"


def test_transformer_keeps_root_cause_nullable_and_builds_search_text():
    result = transform_jira_issue(
        {
            "key": "PAY-1",
            "fields": {
                "summary": "Checkout returns HTTP 500",
                "description": "Payment requests fail during checkout.",
                "resolution": {"name": "Fixed"},
                "project": {"key": "PAY"},
                "components": [{"name": "Checkout"}],
            },
        }
    )

    assert result is not None
    assert result["root_cause"] is None
    assert result["resolution"] == "Fixed"
    assert "Project: PAY" in result["search_text"]
    assert "Component: Checkout" in result["search_text"]


def test_download_latest_uses_bearer_token_when_configured(monkeypatch, tmp_path):
    import ingestion.download_zenodo as download_module

    seen = {}

    class DummyResponse:
        def __init__(self, payload):
            self._payload = payload
            self.status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

        def iter_content(self, chunk_size=1024 * 1024):
            yield b"zip-bytes"

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_get(url, timeout, headers=None, stream=False):
        seen.setdefault("calls", []).append({"url": url, "timeout": timeout, "headers": headers, "stream": stream})
        if stream:
            return DummyResponse({})
        return DummyResponse({
            "id": 7740379,
            "files": [{
                "key": "models1.zip",
                "size": 123,
                "links": {"self": "https://example.test/files/models1.zip/content"},
            }],
        })

    monkeypatch.setattr(download_module.requests, "get", fake_get)
    monkeypatch.setattr(download_module, "ZENODO_ACCESS_TOKEN", "secret-token")

    path = download_module.download_latest(tmp_path)

    assert path.name == "models1.zip"
    assert path.read_bytes() == b"zip-bytes"
    assert seen["calls"][0]["headers"]["Authorization"] == "Bearer secret-token"
    assert seen["calls"][1]["headers"]["Authorization"] == "Bearer secret-token"


def test_inspector_handles_gzipped_bson_collections(tmp_path):
    import gzip

    payload = b"".join(
        BSON.encode(item)
        for item in (
            {"key": "PAY-1", "fields": {"summary": "Alpha"}},
            {"key": "PAY-2", "fields": {"summary": "Beta"}},
        )
    )
    archive = tmp_path / "issues.bson.gz"
    with gzip.open(archive, "wb") as handle:
        handle.write(payload)

    result = inspect_path(archive, sample_size=2)

    assert result["archive_type"] == "mongodb"
    assert result["collections"] == ["issues"]
    assert result["sample_count"] == 2
    assert result["sample_records"][0]["key"] == "PAY-1"
