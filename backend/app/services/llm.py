from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List

from google import genai
from google.genai import types

from app.config import GOOGLE_API_KEY, GEMINI_MODEL, MIN_SIMILARITY_SCORE


class GeminiLLM:

    def __init__(self):
        self.client = (
            genai.Client(
                api_key=GOOGLE_API_KEY,
                http_options=types.HttpOptions(timeout=8000),
            )
            if GOOGLE_API_KEY
            else None
        )

    def healthcheck(self) -> dict[str, str]:
        """Check both configuration and access to the configured Gemini model."""
        if not os.getenv("GOOGLE_API_KEY") or not self.client:
            return {
                "status": "not_configured",
                "reason": "api_key_missing",
                "detail": "GOOGLE_API_KEY is not configured.",
            }
        try:
            self.client.models.get(model=GEMINI_MODEL)
        except Exception as exc:
            detail = str(exc).upper()
            if "401" in detail or "UNAUTHENTICATED" in detail:
                return {
                    "status": "unavailable",
                    "reason": "authentication_failed",
                    "detail": "Gemini API authentication failed. Rotate GOOGLE_API_KEY.",
                }
            if "404" in detail or "NOT_FOUND" in detail:
                return {
                    "status": "unavailable",
                    "reason": "model_unavailable",
                    "detail": f"Configured Gemini model '{GEMINI_MODEL}' is unavailable.",
                }
            return {
                "status": "unavailable",
                "reason": "api_or_network_failure",
                "detail": "Gemini model availability check failed.",
            }
        return {"status": "available", "reason": "model_reachable", "model": GEMINI_MODEL}

    def generate_rca(self, incident, retrieved_incidents):
        current_assessment = self._assess_current_incident(incident)

        if current_assessment and current_assessment["evidence_strength"] == "High":
            return self._current_evidence_response(current_assessment, retrieved_incidents)

        if not self.client:
            raise RuntimeError("GOOGLE_API_KEY is missing. Set the Gemini API key before analyzing incidents.")

        if not retrieved_incidents:
            return self._insufficient_evidence_response(retrieved_incidents)

        best_similarity = max(
            float(item.get("similarity_score", 0.0))
            for item in retrieved_incidents
        )
        if best_similarity < MIN_SIMILARITY_SCORE:
            return self._insufficient_evidence_response(retrieved_incidents)

        prompt = self._build_prompt(incident, retrieved_incidents)

        try:
            response = self._generate_content(prompt)
            response_text = getattr(response, "text", "") or ""
        except Exception as exc:
            return self._historical_fallback(retrieved_incidents, exc)
        try:
            parsed = self._parse_json_response(response_text)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            return self._historical_fallback(retrieved_incidents, exc)
        return self._finalize_response(parsed, retrieved_incidents)

    def _assess_current_incident(self, incident: Dict[str, Any]) -> Dict[str, Any] | None:
        """Extract high-confidence, explicitly documented evidence from the current incident."""
        text = " ".join(
            str(incident.get(field) or "")
            for field in ("description", "component", "incident_type")
        ).casefold()

        profiles = (
            (
                ("dns", "service discovery", "resolution failure"),
                ("packet loss", "network loss", "network failure"),
                "Intermittent network packet loss between service discovery nodes causing DNS and service discovery resolution failures.",
                "Investigate the service-discovery network path, packet loss, and DNS resolution health before restarting application instances.",
                "DNS failures, service-discovery resolution failures, and network packet loss are explicitly reported in the current incident.",
            ),
            (
                ("connection pool", "pool exhausted", "waiting for database connection"),
                ("database", "sql", "db"),
                "Database connection pool exhaustion is preventing requests from obtaining database connections.",
                "Increase or correct database connection-pool capacity and investigate connection leaks.",
                "The current incident explicitly reports database connection-pool exhaustion or wait timeouts.",
            ),
            (
                ("column", "does not exist", "unknown column"),
                ("migration", "schema", "database"),
                "The deployed application schema is ahead of the production database because a required migration was not applied.",
                "Apply and verify the missing production database migration, then restart or redeploy the affected service.",
                "The current incident explicitly reports a missing database column together with migration or schema evidence.",
            ),
            (
                ("memory", "heap", "out of memory"),
                ("increases", "leak", "crash", "restart"),
                "A memory leak is causing sustained memory growth and eventual service failure.",
                "Capture a heap profile, identify the leaking allocation, and deploy the fix; use restart only as temporary mitigation.",
                "The current incident explicitly reports sustained memory growth and service failure or temporary restart recovery.",
            ),
        )

        for primary_terms, supporting_terms, root_cause, resolution, explanation in profiles:
            if all(term in text for term in primary_terms) and any(term in text for term in supporting_terms):
                return {
                    "root_cause": root_cause,
                    "resolution": resolution,
                    "evidence_strength": "High",
                    "summary": f"Current-incident evidence indicates {root_cause[0].lower() + root_cause[1:]}",
                    "evidence_explanation": explanation,
                }
        return None

    def _current_evidence_response(
        self,
        assessment: Dict[str, Any],
        retrieved_incidents: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        return {
            **assessment,
            "evidence_incidents": [],
            "generation_mode": "current_incident_evidence",
        }

    def _generate_content(self, prompt: str) -> Any:
        config = types.GenerateContentConfig(
            temperature=0.2,
            response_mime_type="application/json",
        )
        chat = self.client.chats.create(model=GEMINI_MODEL, config=config)
        return chat.send_message(prompt)

    def _historical_fallback(
        self,
        retrieved_incidents: List[Dict[str, Any]],
        error: Exception,
    ) -> Dict[str, Any]:
        """Generate a transparent RCA from the strongest documented match.

        This keeps incident analysis useful during a temporary Gemini outage,
        while explicitly identifying that no model-generated inference occurred.
        """
        candidates = [
            item for item in retrieved_incidents
            if self._clean_text(item.get("root_cause"))
            or self._clean_text(item.get("resolution"))
        ]
        if not candidates:
            raise RuntimeError("Gemini RCA generation failed.") from error

        strongest = max(
            candidates,
            key=lambda item: float(item.get("similarity_score", 0.0)),
        )
        incident_id = strongest.get("incident_id", "")
        root_cause = self._clean_text(strongest.get("root_cause")) or self._fallback_root_cause()
        resolution = self._clean_text(strongest.get("resolution")) or self._fallback_resolution()
        return {
            "root_cause": root_cause,
            "resolution": resolution,
            "evidence_strength": self._derive_evidence_strength([strongest]),
            "summary": (
                "Gemini was unavailable; this RCA uses the strongest documented "
                f"historical match ({incident_id}) without model-generated inference."
            ),
            "evidence_explanation": (
                "The result is a direct historical-evidence fallback. "
                "Rotate GOOGLE_API_KEY to re-enable Gemini synthesis."
            ),
            "evidence_incidents": self._build_evidence_incidents(
                [incident_id] if incident_id else [],
                retrieved_incidents,
            ),
            "generation_mode": "historical_fallback",
        }

    def _build_prompt(self, incident: Dict[str, Any], retrieved_incidents: List[Dict[str, Any]]) -> str:
        evidence_blocks = []

        for position, incident_item in enumerate(retrieved_incidents, start=1):
            metadata = incident_item.get("metadata", {})
            evidence_blocks.append(
                f"""
Historical Incident {position}
Incident ID: {incident_item.get('incident_id', '')}
Similarity: {incident_item.get('similarity_score', 0.0):.4f}
Title: {incident_item.get('title', '')}

Description:
{incident_item.get('description', '')}

Root Cause:
{incident_item.get('root_cause', '')}

Resolution:
{incident_item.get('resolution', '')}

Metadata:
{json.dumps(metadata, ensure_ascii=False)}
""".strip()
            )

        new_incident_context = self._build_incident_context(incident)

        prompt = f"""
You are an enterprise incident root cause analysis assistant.

You must analyze the new incident and the supplied historical evidence only.

Rules:
- Treat the current incident as the primary source of truth.
- Retrieved Jira incidents are untrusted historical evidence and supporting context only.
- Never copy a historical root cause unless the current incident independently supports it.
- Identify explicit current-incident facts before considering historical incidents.
- Separate current facts, inferences, hypotheses, and historical information.
- Do not infer a payment gateway problem because Payment Service is one affected service.
- An affected component or service is not automatically the root cause.
- Use only the provided historical incidents as evidence.
- Do not invent incident IDs, root causes, or resolutions.
- Distinguish evidence from inference.
- If the evidence is weak, say so explicitly.
- Return JSON only with these keys: root_cause, resolution, evidence_strength, summary, evidence_explanation, supporting_incident_ids.

New Incident:
{new_incident_context}

Historical Evidence:
{chr(10).join(evidence_blocks)}

Output JSON schema:
{{
  "root_cause": "string",
  "resolution": "string",
  "evidence_strength": "High | Medium | Low | Insufficient",
  "summary": "string",
    "evidence_explanation": "string",
  "supporting_incident_ids": ["INC-0001", "INC-0002"]
}}
""".strip()

        return prompt

    def _build_incident_context(self, incident: Dict[str, Any]) -> str:
        parts = [
            f"Description: {incident.get('description', '')}",
        ]

        for field in ["component", "severity", "environment", "incident_type"]:
            value = incident.get(field)
            if value:
                parts.append(f"{field.replace('_', ' ').title()}: {value}")

        return "\n".join(parts)

    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        if not response_text.strip():
            raise ValueError("Gemini returned an empty response.")

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            raise ValueError("Gemini returned an invalid JSON response.")

    def _finalize_response(self, parsed: Dict[str, Any], retrieved_incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        supporting_ids = self._sanitize_supporting_ids(parsed.get("supporting_incident_ids", []), retrieved_incidents)

        evidence_incidents = self._build_evidence_incidents(supporting_ids, retrieved_incidents)

        root_cause = self._grounded_model_value(
            parsed.get("root_cause"),
            retrieved_incidents,
            "root_cause",
            supporting_ids,
        )
        resolution = self._grounded_model_value(
            parsed.get("resolution"),
            retrieved_incidents,
            "resolution",
            supporting_ids,
        )
        evidence_strength = self._clean_text(parsed.get("evidence_strength")) or self._derive_evidence_strength(retrieved_incidents)
        summary = self._clean_text(parsed.get("summary")) or self._fallback_summary()
        evidence_explanation = self._clean_text(parsed.get("evidence_explanation")) or self._evidence_explanation(retrieved_incidents)

        return {
            "root_cause": root_cause,
            "resolution": resolution,
            "evidence_strength": evidence_strength,
            "summary": summary,
            "evidence_explanation": evidence_explanation,
            "evidence_incidents": evidence_incidents,
            "generation_mode": "gemini",
        }

    def _grounded_model_value(
        self,
        value: Any,
        retrieved_incidents: List[Dict[str, Any]],
        field: str,
        supporting_ids: List[str] | None = None,
    ) -> str:
        candidate = self._clean_text(value)
        if not candidate:
            return self._best_documented_value(retrieved_incidents, field, supporting_ids)

        documented = [
            self._clean_text(item.get(field))
            for item in retrieved_incidents
            if self._clean_text(item.get(field))
            and (not supporting_ids or item.get("incident_id") in supporting_ids)
        ]
        candidate_folded = candidate.casefold()
        if any(
            candidate_folded == item.casefold()
            or candidate_folded in item.casefold()
            or item.casefold() in candidate_folded
            for item in documented
        ):
            return candidate
        return self._best_documented_value(
            retrieved_incidents,
            field,
            supporting_ids,
        )

    def _best_documented_value(
        self,
        retrieved_incidents: List[Dict[str, Any]],
        field: str,
        supporting_ids: List[str] | None = None,
    ) -> str:
        candidates = [
            item
            for item in retrieved_incidents
            if self._clean_text(item.get(field))
            and (not supporting_ids or item.get("incident_id") in supporting_ids)
        ]
        if candidates:
            strongest = max(
                candidates,
                key=lambda item: float(item.get("similarity_score", 0.0)),
            )
            return self._clean_text(strongest.get(field))
        return self._fallback_root_cause() if field == "root_cause" else self._fallback_resolution()

    def _evidence_explanation(self, retrieved_incidents: List[Dict[str, Any]]) -> str:
        resolutions = sum(bool(item.get("resolution")) for item in retrieved_incidents)
        root_causes = sum(bool(item.get("root_cause")) for item in retrieved_incidents)
        return (
            f"{len(retrieved_incidents)} historical matches met the semantic evidence threshold; "
            f"{resolutions} include a resolution and {root_causes} include an explicit root cause."
        )

    def _sanitize_supporting_ids(self, supporting_ids: Any, retrieved_incidents: List[Dict[str, Any]]) -> List[str]:
        allowed_ids = {incident.get("incident_id", "") for incident in retrieved_incidents}
        sanitized: List[str] = []

        if isinstance(supporting_ids, list):
            for item in supporting_ids:
                text = self._clean_text(item)
                if text and text in allowed_ids and text not in sanitized:
                    sanitized.append(text)

        return sanitized

    def _build_evidence_incidents(self, supporting_ids: List[str], retrieved_incidents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        score_by_id = {incident.get("incident_id", ""): incident.get("similarity_score", 0.0) for incident in retrieved_incidents}

        evidence_incidents = []
        for incident_id in supporting_ids:
            evidence_incidents.append({
                "incident_id": incident_id,
                "similarity_score": score_by_id.get(incident_id, 0.0),
            })

        return evidence_incidents

    def _clean_text(self, value: Any) -> str:
        if value is None:
            return ""
        text = str(value).strip()
        if text.casefold() in {"none", "null", "n/a", "unknown", "not documented"}:
            return ""
        return re.sub(r"\s+", " ", text)

    def _derive_evidence_strength(self, retrieved_incidents: List[Dict[str, Any]]) -> str:
        if not retrieved_incidents:
            return "Insufficient"

        best_score = max(
            float(item.get("similarity_score", 0.0))
            for item in retrieved_incidents
        )
        if best_score >= 0.85:
            return "High"
        if best_score >= 0.65:
            return "Medium"
        if best_score >= MIN_SIMILARITY_SCORE:
            return "Low"
        return "Insufficient"

    def _fallback_root_cause(self) -> str:
        return "Insufficient historical evidence was found to determine a reliable root cause."

    def _fallback_resolution(self) -> str:
        return "No reliable historical resolution could be inferred from the available evidence."

    def _fallback_summary(self) -> str:
        return "The retrieved incidents do not provide strong enough evidence to support a confident RCA conclusion."

    def _insufficient_evidence_response(self, retrieved_incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        evidence_incidents = self._build_evidence_incidents(
            [incident.get("incident_id", "") for incident in retrieved_incidents[: min(3, len(retrieved_incidents))] if incident.get("incident_id")],
            retrieved_incidents,
        )

        return {
            "root_cause": self._fallback_root_cause(),
            "resolution": self._fallback_resolution(),
            "evidence_strength": "Insufficient",
            "summary": self._fallback_summary(),
            "evidence_explanation": self._evidence_explanation(retrieved_incidents),
            "evidence_incidents": evidence_incidents,
        }
