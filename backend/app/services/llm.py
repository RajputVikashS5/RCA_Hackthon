from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from google import genai
from google.genai import types

from app.config import GOOGLE_API_KEY, GEMINI_MODEL, MIN_SIMILARITY_SCORE


class GeminiLLM:

    def __init__(self):

        self.client = genai.Client(api_key=GOOGLE_API_KEY) if GOOGLE_API_KEY else None

    def generate_rca(self, incident, retrieved_incidents):

        if not self.client:
            raise RuntimeError("GOOGLE_API_KEY is missing. Set the Gemini API key before analyzing incidents.")

        if not retrieved_incidents:
            return self._insufficient_evidence_response(retrieved_incidents)

        if retrieved_incidents[0].get("similarity_score", 0.0) < MIN_SIMILARITY_SCORE:
            return self._insufficient_evidence_response(retrieved_incidents)

        prompt = self._build_prompt(incident, retrieved_incidents)

        try:
            response = self.client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )
            response_text = getattr(response, "text", "") or ""
            parsed = self._parse_json_response(response_text)
        except Exception as exc:
            raise RuntimeError("Gemini RCA generation failed.") from exc
        return self._finalize_response(parsed, retrieved_incidents)

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
- Use only the provided historical incidents as evidence.
- Do not invent incident IDs, root causes, or resolutions.
- Distinguish evidence from inference.
- If the evidence is weak, say so explicitly.
- Return JSON only with these keys: root_cause, resolution, evidence_strength, summary, supporting_incident_ids.

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

        root_cause = self._clean_text(parsed.get("root_cause")) or self._fallback_root_cause()
        resolution = self._clean_text(parsed.get("resolution")) or self._fallback_resolution()
        evidence_strength = self._clean_text(parsed.get("evidence_strength")) or self._derive_evidence_strength(retrieved_incidents)
        summary = self._clean_text(parsed.get("summary")) or self._fallback_summary()

        return {
            "root_cause": root_cause,
            "resolution": resolution,
            "evidence_strength": evidence_strength,
            "summary": summary,
            "evidence_incidents": evidence_incidents,
        }

    def _sanitize_supporting_ids(self, supporting_ids: Any, retrieved_incidents: List[Dict[str, Any]]) -> List[str]:
        allowed_ids = {incident.get("incident_id", "") for incident in retrieved_incidents}
        sanitized: List[str] = []

        if isinstance(supporting_ids, list):
            for item in supporting_ids:
                text = self._clean_text(item)
                if text and text in allowed_ids and text not in sanitized:
                    sanitized.append(text)

        if not sanitized:
            sanitized = [incident.get("incident_id", "") for incident in retrieved_incidents[: min(3, len(retrieved_incidents))] if incident.get("incident_id")]

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
        return re.sub(r"\s+", " ", text)

    def _derive_evidence_strength(self, retrieved_incidents: List[Dict[str, Any]]) -> str:
        if not retrieved_incidents:
            return "Insufficient"

        best_score = float(retrieved_incidents[0].get("similarity_score", 0.0))
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
            "evidence_incidents": evidence_incidents,
        }
