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
