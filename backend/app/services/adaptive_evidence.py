from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from typing import Any, Iterable

from app.config import (
    DEFAULT_TOP_K,
    R2_CATALOG_KEY,
    R2_CATALOG_MAX_BYTES,
    R2_EXPANSION_ENABLED,
    R2_MAX_CANDIDATES,
    RCA_MEDIUM_THRESHOLD,
    RCA_STRONG_THRESHOLD,
    RCA_WEAK_THRESHOLD,
)
from app.database.repository import IncidentRepository
from app.services.embedding import EmbeddingModel
from app.services.r2_storage import R2Storage, R2StorageError


@dataclass(frozen=True)
class EvidenceEvaluation:
    state: str
    score: float
    supporting_incidents: int
    incidents_with_root_cause: int
    incidents_with_resolution: int


@dataclass
class AdaptiveEvidenceResult:
    incidents: list[dict[str, Any]]
    evaluation: EvidenceEvaluation
    initial_evaluation: EvidenceEvaluation
    expansion_used: bool = False
    r2_candidates_found: int = 0
    r2_incidents_ingested: int = 0
    r2_incident_ids: list[str] = field(default_factory=list)
    ingestion: dict[str, int] = field(default_factory=dict)


def evaluate_evidence(incidents: Iterable[dict[str, Any]]) -> EvidenceEvaluation:
    rows = list(incidents)
    valid = [row for row in rows if float(row.get("similarity_score", 0.0)) >= RCA_WEAK_THRESHOLD]
    scores = [float(row.get("similarity_score", 0.0)) for row in valid]
    root_causes = [str(row.get("root_cause") or "").strip() for row in valid]
    resolutions = [str(row.get("resolution") or "").strip() for row in valid]
    documented = [row for row in valid if row.get("root_cause") and row.get("resolution")]
    best = max(scores, default=0.0)

    normalized_causes = [re.sub(r"\W+", " ", value.casefold()).strip() for value in root_causes if value]
    agreement = 1.0
    if normalized_causes:
        agreement = max(normalized_causes.count(value) for value in set(normalized_causes)) / len(normalized_causes)
    score = min(1.0, best * 0.7 + min(len(documented), 3) * 0.1 + agreement * 0.2)

    if not valid or not documented:
        state = "INSUFFICIENT"
    elif score >= RCA_STRONG_THRESHOLD:
        state = "STRONG"
    elif score >= RCA_MEDIUM_THRESHOLD:
        state = "MEDIUM"
    elif score >= RCA_WEAK_THRESHOLD:
        state = "WEAK"
    else:
        state = "INSUFFICIENT"

    return EvidenceEvaluation(
        state=state,
        score=round(score, 4),
        supporting_incidents=len(valid),
        incidents_with_root_cause=sum(bool(value) for value in root_causes),
        incidents_with_resolution=sum(bool(value) for value in resolutions),
    )


class R2CandidateDiscovery:
    """Searches a small, persisted R2 catalog; it never scans the raw archive."""

    def __init__(
        self,
        storage: R2Storage | None = None,
        catalog_key: str = R2_CATALOG_KEY,
        max_bytes: int = R2_CATALOG_MAX_BYTES,
        max_candidates: int = R2_MAX_CANDIDATES,
    ) -> None:
        self.storage = storage or R2Storage()
        self.catalog_key = catalog_key
        self.max_bytes = max_bytes
        self.max_candidates = max_candidates

    def search(self, incident: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            if not self.storage.object_exists(self.catalog_key):
                return []
            metadata = self.storage.object_metadata(self.catalog_key)
            size = int(metadata.get("ContentLength") or metadata.get("content_length") or 0)
            if size and size > self.max_bytes:
                raise R2StorageError("The R2 incident catalog exceeds the configured size limit.")
            body = self.storage.get_object(self.catalog_key).get("Body")
            if body is None:
                return []
            payload = json.loads(body.read(self.max_bytes + 1))
        except R2StorageError:
            raise
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            raise R2StorageError("The R2 incident catalog is not valid JSON.") from exc

        candidates = payload.get("incidents", []) if isinstance(payload, dict) else payload
        if not isinstance(candidates, list):
            raise R2StorageError("The R2 incident catalog must contain an incidents array.")

        query = " ".join(
            str(incident.get(field) or "")
            for field in ("description", "component", "severity", "environment", "incident_type")
        ).casefold()
        query_tokens = set(re.findall(r"[a-z0-9]{3,}", query))
        ranked: list[tuple[float, dict[str, Any]]] = []
        for raw in candidates:
            if not isinstance(raw, dict):
                continue
            candidate = self._normalize(raw)
            candidate_text = " ".join(
                str(candidate.get(field) or "")
                for field in ("incident_id", "title", "description", "root_cause", "resolution", "component", "service", "environment")
            ).casefold()
            candidate_tokens = set(re.findall(r"[a-z0-9]{3,}", candidate_text))
            overlap = len(query_tokens & candidate_tokens) / max(len(query_tokens), 1)
            if overlap <= 0:
                continue
            if incident.get("component") and str(incident["component"]).casefold() in candidate_text:
                overlap = min(1.0, overlap + 0.15)
            candidate["_catalog_score"] = round(overlap, 4)
            ranked.append((overlap, candidate))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [candidate for _, candidate in ranked[: self.max_candidates]]

    def search_r2_candidates(self, incident: dict[str, Any]) -> list[dict[str, Any]]:
        return self.search(incident)

    @staticmethod
    def _normalize(raw: dict[str, Any]) -> dict[str, Any]:
        candidate = dict(raw)
        candidate["incident_id"] = str(raw.get("incident_id") or raw.get("issue_key") or raw.get("key") or "").strip()
        candidate["title"] = str(raw.get("title") or raw.get("summary") or "").strip()
        candidate["description"] = str(raw.get("description") or raw.get("details") or "").strip()
        candidate["root_cause"] = str(raw.get("root_cause") or "").strip() or None
        candidate["resolution"] = str(raw.get("resolution") or "").strip() or None
        candidate["metadata"] = {
            **(raw.get("metadata") if isinstance(raw.get("metadata"), dict) else {}),
            "r2_object_key": raw.get("r2_object_key") or raw.get("object_key"),
            "dataset_version": raw.get("dataset_version"),
            "provenance": "r2-adaptive",
        }
        return candidate


class AdaptiveEvidenceService:
    def __init__(
        self,
        retriever: Any,
        repository: IncidentRepository | None = None,
        embedding_model: EmbeddingModel | None = None,
        discovery: R2CandidateDiscovery | None = None,
    ) -> None:
        self.retriever = retriever
        self.repository = repository or retriever.repository
        self.embedding_model = embedding_model or EmbeddingModel()
        self.discovery = discovery or R2CandidateDiscovery()

    def retrieve(
        self,
        query: str,
        incident: dict[str, Any],
        top_k: int = DEFAULT_TOP_K,
    ) -> AdaptiveEvidenceResult:
        initial = self.retriever.retrieve(query, top_k=top_k)
        initial_evaluation = evaluate_evidence(initial)
        if not R2_EXPANSION_ENABLED or initial_evaluation.state in {"STRONG", "MEDIUM"}:
            return AdaptiveEvidenceResult(initial, initial_evaluation, initial_evaluation)

        discover = getattr(self.discovery, "search_r2_candidates", None) or self.discovery.search
        candidates = discover(incident)
        relevant = [
            candidate for candidate in candidates
            if candidate.get("incident_id") and candidate.get("title") and candidate.get("description")
            and float(candidate.get("_catalog_score", 0.0)) >= RCA_WEAK_THRESHOLD
        ]
        ingestion = self.ingest_relevant_r2_candidates(relevant)
        expanded = self.retriever.retrieve(query, top_k=top_k) if ingestion["inserted"] else initial
        expanded_evaluation = evaluate_evidence(expanded)
        if expanded_evaluation.score < initial_evaluation.score:
            expanded = initial
            expanded_evaluation = initial_evaluation
        return AdaptiveEvidenceResult(
            incidents=expanded,
            evaluation=expanded_evaluation,
            initial_evaluation=initial_evaluation,
            expansion_used=bool(relevant),
            r2_candidates_found=len(candidates),
            r2_incidents_ingested=ingestion["inserted"],
            r2_incident_ids=[str(item["incident_id"]) for item in relevant],
            ingestion=ingestion,
        )

    def _ingest(self, candidates: list[dict[str, Any]]) -> dict[str, int]:
        if not candidates:
            return {"inserted": 0, "updated": 0, "skipped": 0, "failed": 0}
        existing_lookup = getattr(self.repository, "existing_incident_ids", None)
        existing = (
            existing_lookup([str(candidate["incident_id"]) for candidate in candidates])
            if existing_lookup
            else set()
        )
        new_candidates = [candidate for candidate in candidates if candidate["incident_id"] not in existing]
        if not new_candidates:
            return {"inserted": 0, "updated": 0, "skipped": len(candidates), "failed": 0}
        texts = [
            "\n".join(
                value for value in (
                    candidate.get("title"),
                    candidate.get("description"),
                    candidate.get("root_cause"),
                    candidate.get("resolution"),
                ) if value
            )
            for candidate in new_candidates
        ]
        embeddings = self.embedding_model.embed_documents(texts)
        records = []
        for candidate, embedding in zip(new_candidates, embeddings):
            record = {key: value for key, value in candidate.items() if not key.startswith("_")}
            record["source"] = "r2-adaptive"
            record["embedding"] = embedding.tolist()
            record["metadata"] = {
                **(record.get("metadata") or {}),
                "ingestion_timestamp": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            }
            records.append(record)
        self.repository.upsert_batch(records)
        return {"inserted": len(records), "updated": 0, "skipped": len(candidates) - len(records), "failed": 0}

    def ingest_relevant_r2_candidates(self, candidates: list[dict[str, Any]]) -> dict[str, int]:
        return self._ingest(candidates)
