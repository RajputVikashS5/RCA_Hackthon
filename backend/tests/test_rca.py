from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from app.services.llm import GeminiLLM


class FakeModelRunner:
    def __init__(self, response_text: str):
        self.response_text = response_text

    def send_message(self, *args, **kwargs):
        return SimpleNamespace(text=self.response_text)


class FakeGeminiClient:
    def __init__(self, response_text: str):
        self.chats = SimpleNamespace(create=lambda **kwargs: FakeModelRunner(response_text))


class FakeHealthClient:
    def __init__(self, error: Exception | None = None):
        self.models = self
        self.error = error

    def get(self, **kwargs):
        if self.error:
            raise self.error
        return {"name": kwargs["model"]}


class FailIfCalledClient:
    class _Chats:
        def create(self, **kwargs):
            return self

        def send_message(self, *args, **kwargs):
            raise AssertionError("Gemini should not have been called for weak evidence.")

    def __init__(self):
        self.chats = self._Chats()


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
    assert result["resolution"] == "Increase pool size"
    assert result["evidence_strength"] == "High"
    assert result["evidence_incidents"][0]["incident_id"] == "INC-1001"
    assert result["generation_mode"] == "gemini"


def test_current_incident_terms_do_not_bypass_historical_evidence():
    llm = GeminiLLM()
    llm.client = FakeGeminiClient(
        json.dumps(
            {
                "root_cause": "Payment gateway connection saturation.",
                "resolution": "Raise gateway connection limits.",
                "evidence_strength": "Medium",
                "summary": "The historical match is the only available evidence.",
                "supporting_incident_ids": ["PAY-1002"],
            }
        )
    )
    result = llm.generate_rca(
        {
            "description": (
                "Multiple production microservices have timeouts. DNS lookups fail, "
                "service discovery logs show resolution failures, and packet loss "
                "was observed between service discovery nodes."
            ),
            "component": "Service Discovery",
            "severity": "Critical",
            "environment": "Production",
            "incident_type": "Network Failure",
        },
        [
            {
                "incident_id": "PAY-1002",
                "root_cause": "Payment gateway connection saturation.",
                "resolution": "Raise gateway connection limits.",
                "similarity_score": 0.92,
            }
        ],
    )

    assert result["root_cause"] == "Payment gateway connection saturation."
    assert result["generation_mode"] == "gemini"


def test_invalid_gemini_response_uses_historical_fallback():
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

    result = llm.generate_rca({"description": "HTTP 500 errors"}, retrieved)
    assert result["generation_mode"] == "historical_fallback"
    assert result["root_cause"] == "Database connection pool exhaustion"


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
    assert "Insufficient historical evidence" in result["root_cause"]


def test_gemini_auth_failure_uses_strongest_documented_historical_evidence():
    class AuthFailureClient:
        class _Chats:
            def create(self, **kwargs):
                return self

            def send_message(self, *args, **kwargs):
                raise RuntimeError("401 UNAUTHENTICATED")

        def __init__(self):
            self.chats = self._Chats()

    llm = GeminiLLM()
    llm.client = AuthFailureClient()
    result = llm.generate_rca(
        {"description": "Checkout is failing"},
        [
            {
                "incident_id": "INC-1001",
                "similarity_score": 0.92,
                "root_cause": "Connection pool exhaustion",
                "resolution": "Increase pool size",
            }
        ],
    )

    assert result["generation_mode"] == "historical_fallback"
    assert result["root_cause"] == "Connection pool exhaustion"
    assert result["resolution"] == "Increase pool size"


def test_gemini_health_reports_available_model():
    llm = GeminiLLM()
    llm.client = FakeHealthClient()
    result = llm.healthcheck()
    assert result["status"] == "available"
    assert result["model"] == "gemini-3.6-flash"


def test_gemini_health_reports_missing_key(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    llm = GeminiLLM()
    llm.client = None
    result = llm.healthcheck()
    assert result == {
        "status": "not_configured",
        "reason": "api_key_missing",
        "detail": "GOOGLE_API_KEY is not configured.",
    }


def test_gemini_health_reports_unavailable_model():
    llm = GeminiLLM()
    llm.client = FakeHealthClient(RuntimeError("404 NOT_FOUND"))
    result = llm.healthcheck()
    assert result["status"] == "unavailable"
    assert result["reason"] == "model_unavailable"


def test_gemini_health_reports_network_failure():
    llm = GeminiLLM()
    llm.client = FakeHealthClient(TimeoutError())
    result = llm.healthcheck()
    assert result["status"] == "unavailable"
    assert result["reason"] == "api_or_network_failure"


def test_model_cannot_return_unsupported_root_cause_or_resolution():
    llm = GeminiLLM()
    llm.client = FakeGeminiClient(
        json.dumps(
            {
                "root_cause": "Invented cause",
                "resolution": "Invented fix",
                "evidence_strength": "High",
                "summary": "Unsupported.",
                "supporting_incident_ids": ["INC-1001"],
            }
        )
    )
    result = llm.generate_rca(
        {"description": "HTTP 500 errors"},
        [{
            "incident_id": "INC-1001",
            "root_cause": "Documented cause",
            "resolution": "Documented fix",
            "similarity_score": 0.9,
        }],
    )
    assert result["root_cause"] == "Documented cause"
    assert result["resolution"] == "Documented fix"


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


def test_unsupported_model_value_uses_strongest_documented_incident():
    llm = GeminiLLM()
    llm.client = FakeGeminiClient(
        json.dumps(
            {
                "root_cause": "Invented cause",
                "resolution": "Invented fix",
                "evidence_strength": "Medium",
                "summary": "The model selected the wrong historical record.",
                "supporting_incident_ids": [],
            }
        )
    )
    retrieved = [
        {
            "incident_id": "INC-weak",
            "root_cause": "Generic timeout",
            "resolution": "Restart service",
            "similarity_score": 0.61,
        },
        {
            "incident_id": "INC-strong",
            "root_cause": "Database connection pool exhaustion",
            "resolution": "Increase pool size",
            "similarity_score": 0.91,
        },
    ]

    result = llm.generate_rca({"description": "Checkout failure"}, retrieved)

    assert result["root_cause"] == "Database connection pool exhaustion"
    assert result["resolution"] == "Increase pool size"


def test_supporting_ids_limit_grounding_to_selected_database_evidence():
    llm = GeminiLLM()
    llm.client = FakeGeminiClient(
        json.dumps(
            {
                "root_cause": "Generic timeout",
                "resolution": "Restart service",
                "evidence_strength": "Medium",
                "summary": "The selected incident supports the answer.",
                "supporting_incident_ids": ["INC-weak"],
            }
        )
    )
    retrieved = [
        {
            "incident_id": "INC-weak",
            "root_cause": "Generic timeout",
            "resolution": "Restart service",
            "similarity_score": 0.61,
        },
        {
            "incident_id": "INC-strong",
            "root_cause": "Database connection pool exhaustion",
            "resolution": "Increase pool size",
            "similarity_score": 0.91,
        },
    ]

    result = llm.generate_rca({"description": "Checkout failure"}, retrieved)

    assert result["root_cause"] == "Generic timeout"
    assert result["resolution"] == "Restart service"


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

    assert result["root_cause"] == llm._fallback_root_cause()
    assert result["resolution"] == llm._fallback_resolution()
