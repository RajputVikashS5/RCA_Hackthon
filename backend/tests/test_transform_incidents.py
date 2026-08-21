from ingestion.transform_incidents import transform_issue


def test_jira_issue_preserves_evidence_and_leaves_root_cause_unknown():
    record = transform_issue(
        {
            "id": "42",
            "key": "PAY-42",
            "fields": {
                "summary": "Checkout returns HTTP 500",
                "description": "Payment requests fail in production.",
                "comment": {"comments": [{"body": "Investigating database saturation."}]},
                "resolution": {"name": "Fixed"},
                "project": {"key": "PAY"},
                "components": [{"name": "Checkout"}],
                "status": {"name": "Resolved"},
            },
        },
        source_url="https://zenodo.org/records/15719919",
    )

    assert record["incident_id"] == "PAY-42"
    assert record["resolution"] == "Fixed"
    assert record["root_cause"] is None
    assert "Investigating database saturation" in record["search_text"]
    assert record["source_url"].endswith("15719919")


def test_explicit_root_cause_is_extracted_without_model_inference():
    record = transform_issue(
        {
            "key": "OPS-7",
            "fields": {
                "summary": "Service outage",
                "description": "The service is unavailable.",
                "customfield_root_cause": "Connection pool exhaustion",
            },
        }
    )

    assert record["root_cause"] == "Connection pool exhaustion"
