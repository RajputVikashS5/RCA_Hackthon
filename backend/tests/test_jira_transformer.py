from ingestion.jira_transformer import transform_jira_issue


def test_low_quality_seo_titles_are_excluded():
    issue = {
        "key": "AAR-6170",
        "summary": "Buy Oxycontin No Prescription Needed Online",
        "description": "SEO content",
    }

    assert transform_jira_issue(issue) is None


def test_non_english_pharmaceutical_titles_are_excluded():
    issue = {
        "key": "AAR-5172",
        "summary": "Stanozolol Boldenona Enantato De Testosterona - Winstrol Injection",
        "description": "Promotional content",
    }

    assert transform_jira_issue(issue) is None


def test_streaming_titles_are_excluded():
    issue = {
        "key": "AAR-5184",
        "summary": "REGARDER Fast & Furious 9 streaming vf Film Complet",
        "description": "Promotional content",
    }

    assert transform_jira_issue(issue) is None


def test_operational_issue_is_preserved():
    issue = {
        "key": "OPS-42",
        "summary": "Checkout returns HTTP 500",
        "description": "Payment requests fail in production.",
    }

    record = transform_jira_issue(issue)

    assert record is not None
    assert record["incident_id"] == "OPS-42"