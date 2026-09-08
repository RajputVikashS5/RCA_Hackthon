from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Callable, Iterable


@dataclass(frozen=True)
class EvaluationCase:
    case_id: str
    description: str
    relevant_incident_ids: tuple[str, ...]
    expected_root_cause: str | None
    expected_resolution: str | None
    expected_behavior: str


@dataclass
class EvaluationReport:
    total_cases: int
    retrieval: dict[str, float]
    rca: dict[str, float]
    cases: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for position, incident_id in enumerate(retrieved, start=1):
        if incident_id in relevant:
            return 1.0 / position
    return 0.0


def evaluate_cases(
    cases: Iterable[EvaluationCase],
    retrieve: Callable[[str], list[dict[str, Any]]],
    analyze: Callable[[EvaluationCase, list[dict[str, Any]]], dict[str, Any]],
) -> EvaluationReport:
    """Run cases against injected production-compatible functions.

    No score is inferred for missing values: unavailable expected labels are
    excluded from the corresponding RCA metric and remain visible per case.
    """
    case_results: list[dict[str, Any]] = []
    recall_at_1: list[float] = []
    recall_at_5: list[float] = []
    mrr: list[float] = []
    root_cause_scores: list[float] = []
    resolution_scores: list[float] = []
    evidence_scores: list[float] = []
    unsupported_claim_scores: list[float] = []

    for case in cases:
        retrieved = retrieve(case.description)
        retrieved_ids = [str(item.get("incident_id", "")) for item in retrieved]
        relevant = set(case.relevant_incident_ids)
        recall_at_1.append(float(bool(set(retrieved_ids[:1]) & relevant)))
        recall_at_5.append(float(bool(set(retrieved_ids[:5]) & relevant)))
        mrr.append(_reciprocal_rank(retrieved_ids, relevant))
        result = analyze(case, retrieved)

        expected_root = case.expected_root_cause
        expected_resolution = case.expected_resolution
        if expected_root is not None:
            root_cause_scores.append(float(result.get("root_cause") == expected_root))
        if expected_resolution is not None:
            resolution_scores.append(float(result.get("resolution") == expected_resolution))
        evidence_scores.append(
            float(set(result.get("supporting_incident_ids", [])) <= set(retrieved_ids))
        )
        unsupported_claims = result.get("unsupported_claims")
        if isinstance(unsupported_claims, bool):
            unsupported_claim_scores.append(float(not unsupported_claims))

        case_results.append(
            {
                "case_id": case.case_id,
                "expected_behavior": case.expected_behavior,
                "retrieved_incident_ids": retrieved_ids,
                "result": result,
            }
        )

    def average(values: list[float]) -> float | None:
        return round(sum(values) / len(values), 4) if values else None

    return EvaluationReport(
        total_cases=len(case_results),
        retrieval={
            "recall_at_1": average(recall_at_1),
            "recall_at_5": average(recall_at_5),
            "mrr": average(mrr),
        },
        rca={
            "root_cause_accuracy": average(root_cause_scores),
            "resolution_accuracy": average(resolution_scores),
            "evidence_accuracy": average(evidence_scores),
            "unsupported_claim_rate": (
                round(1 - average(unsupported_claim_scores), 4)
                if unsupported_claim_scores
                else None
            ),
        },
        cases=case_results,
    )
