from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.services.llm import GeminiLLM


class FakeModelRunner:
    def __init__(self, response_text: str):
        self.response_text = response_text

    def generate_content(self, *args, **kwargs):
        return SimpleNamespace(text=self.response_text)


class FakeGeminiClient:
    def __init__(self, response_text: str):
        self.models = FakeModelRunner(response_text)


class FailIfCalledClient:
    class _Models:
        def generate_content(self, *args, **kwargs):
            raise AssertionError("Gemini should not have been called for weak evidence.")

    def __init__(self):
        self.models = self._Models()


def test_successful_gemini_rca_response_is_parsed_and_grounded():
    llm = GeminiLLM()
    llm.client = FakeGeminiClient(
        json.dumps(
            {
                "root_cause": "Database connection pool exhaustion",
                "resolution": "Increase the database connection pool size and restart the affected service.",
                "evidence_strength": "High",
                "summary": "Historical payment incidents point to database saturation as the likely cause.",
                "supporting_incident_ids": ["INC-1001", "INC-1002"],
            }
        )
    )

    retrieved = [
        {
            "incident_id": "INC-1001",
            "title": "Payment service failure",
            "description": "HTTP 500 errors during checkout",
            "root_cause": "Database connection pool exhaustion",
            "resolution": "Increase pool size",
            "similarity_score": 0.94,
            "metadata": {},
        },
        {
            "incident_id": "INC-1002",
            "title": "Payment timeout",
            "description": "Checkout requests timed out",
            "root_cause": "Database connection pool exhaustion",
            "resolution": "Restart the payment service",
            "similarity_score": 0.89,
            "metadata": {},
        },
    ]

    result = llm.generate_rca({"description": "Checkout is failing with HTTP 500 errors."}, retrieved)

    assert result["root_cause"] == "Database connection pool exhaustion"
    assert result["resolution"].startswith("Increase the database connection pool size")
    assert result["evidence_strength"] == "High"
    assert result["evidence_incidents"][0]["incident_id"] == "INC-1001"


def test_invalid_gemini_response_is_sanitized_as_runtime_failure():
    llm = GeminiLLM()
    llm.client = FakeGeminiClient("not valid json")

    retrieved = [
        {
            "incident_id": "INC-1001",
            "title": "Payment service failure",
            "description": "HTTP 500 errors",
            "root_cause": "Database connection pool exhaustion",
            "resolution": "Increase pool size",
            "similarity_score": 0.9,
            "metadata": {},
        }
    ]

    with pytest.raises(RuntimeError, match="Gemini RCA generation failed"):
        llm.generate_rca({"description": "HTTP 500 errors"}, retrieved)


def test_weak_evidence_short_circuits_without_gemini_call():
    llm = GeminiLLM()
    llm.client = FailIfCalledClient()

    retrieved = [
        {
            "incident_id": "INC-9999",
            "title": "Weak match",
            "description": "Something unrelated",
            "root_cause": "Unknown",
            "resolution": "Unknown",
            "similarity_score": 0.1,
            "metadata": {},
        }
    ]

    result = llm.generate_rca({"description": "A very different incident"}, retrieved)

    assert result["evidence_strength"] == "Insufficient"
    assert result["root_cause"] is None


def test_evidence_gate_uses_strongest_match_not_first_hybrid_result():
    llm = GeminiLLM()
    llm.client = FakeGeminiClient(
        json.dumps(
            {
                "root_cause": "Parquet decoding failure",
                "resolution": "Repair the affected reader path.",
                "evidence_strength": "Medium",
                "summary": "A historical match supports the diagnosis.",
                "supporting_incident_ids": ["DRILL-816"],
            }
        )
    )
    retrieved = [
        {"incident_id": "DRILL-649", "similarity_score": 0.2},
        {"incident_id": "DRILL-816", "similarity_score": 0.7},
    ]

    result = llm.generate_rca({"description": "Parquet read failure"}, retrieved)

    assert result["evidence_strength"] == "Medium"


def test_null_like_model_root_cause_is_replaced_with_grounded_fallback():
    llm = GeminiLLM()
    llm.client = FakeGeminiClient(
        json.dumps(
            {
                "root_cause": "None",
                "resolution": "Fixed",
                "evidence_strength": "Medium",
                "summary": "Historical records document a fix but no root cause.",
                "supporting_incident_ids": ["DRILL-816"],
            }
        )
    )

    result = llm.generate_rca(
        {"description": "Parquet read failure"},
        [{"incident_id": "DRILL-816", "similarity_score": 0.7}],
    )

    assert result["root_cause"] is None
    assert result["resolution"] == "Fixed"
