from __future__ import annotations

import pytest

from app.services.incident_ingestion import IncidentIngestionError, IncidentIngestionService


def test_valid_csv_ingestion_deduplicates_and_builds_search_text(tmp_path):
    dataset = tmp_path / "incidents.csv"
    dataset.write_text(
        """incident_id,title,description,root_cause,resolution,component,severity,environment
INC-1001,Payment service failure,HTTP 500 errors during checkout,Database connection pool exhaustion,Increase pool size,Payment Service,High,Production
INC-1001,Duplicate payment service failure,Duplicate row,Duplicate cause,Duplicate fix,Payment Service,High,Production
INC-1002,Cache outage,Users saw stale data,Cache invalidation failed,Restarted cache nodes,Cache,Medium,Production
""",
        encoding="utf-8",
    )

    service = IncidentIngestionService()
    records, stats, source_files = service.load_folder(str(tmp_path))

    assert len(records) == 2
    assert stats.indexed_rows == 2
    assert stats.duplicates_removed == 1
    assert stats.valid_rows == 3
    assert source_files == ["incidents.csv"]
    assert records[0].search_text is not None
    assert "Incident ID: INC-1001" in records[0].search_text


def test_missing_required_columns_are_rejected(tmp_path):
    dataset = tmp_path / "broken.csv"
    dataset.write_text(
        """incident_id,title,description
INC-2001,Missing fields,The record does not include root cause or resolution
""",
        encoding="utf-8",
    )

    service = IncidentIngestionService()

    with pytest.raises(IncidentIngestionError):
        service.load_folder(str(tmp_path))


def test_empty_dataset_is_rejected(tmp_path):
    dataset = tmp_path / "empty.csv"
    dataset.write_text("incident_id,title,description,root_cause,resolution\n", encoding="utf-8")

    service = IncidentIngestionService()

    with pytest.raises(IncidentIngestionError):
        service.load_folder(str(tmp_path))
