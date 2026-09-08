from fastapi import APIRouter
from app.config import DEFAULT_TOP_K, MIN_SIMILARITY_SCORE
from app.models.schemas import IncidentAnalysisRequest, IncidentAnalysisResponse
from app.services.llm import GeminiLLM
from app.services.retriever import Retriever
from app.services.adaptive_evidence import AdaptiveEvidenceService
from app.services.r2_storage import R2StorageError
from app.database.analysis_repository import AnalysisRepository
from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Analysis"]
)

retriever = Retriever()
adaptive_evidence = AdaptiveEvidenceService(retriever)
llm = GeminiLLM()
analysis_repository = AnalysisRepository()


def _retrieval_diagnostics(incidents: list[dict]) -> dict[str, object]:
    scores = [float(item.get("similarity_score", 0.0)) for item in incidents]
    return {
        "retrieved_incidents": len(incidents),
        "highest_similarity": round(max(scores), 4) if scores else 0.0,
        "average_similarity": round(sum(scores) / len(scores), 4) if scores else 0.0,
        "evidence_bearing_incidents": sum(
            bool(item.get("root_cause") or item.get("resolution") or item.get("comments"))
            for item in incidents
        ),
        "incidents_with_resolution": sum(bool(item.get("resolution")) for item in incidents),
        "incidents_with_root_cause": sum(bool(item.get("root_cause")) for item in incidents),
        "evidence_threshold": MIN_SIMILARITY_SCORE,
    }


def _build_incident_query(request: IncidentAnalysisRequest) -> str:

    parts = [f"Description: {request.description.strip()}"]

    for field_name in ["component", "severity", "environment", "incident_type"]:

        value = getattr(request, field_name)

        if value:

            parts.append(f"{field_name.replace('_', ' ').title()}: {value}")

    return "\n".join(parts)


@router.post("/analyze", response_model=IncidentAnalysisResponse)
async def analyze_incident(request: IncidentAnalysisRequest):

    if not request.description.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incident description cannot be empty.")

    incident_query = _build_incident_query(request)

    try:
        adaptive_evidence.repository = retriever.repository
        evidence = adaptive_evidence.retrieve(
            incident_query,
            request.model_dump(),
            top_k=DEFAULT_TOP_K,
        )
        retrieved_incidents = evidence.incidents
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except R2StorageError:
        evidence = None
        retrieved_incidents = retriever.retrieve(incident_query, top_k=DEFAULT_TOP_K)

    try:
        analysis = llm.generate_rca(request.model_dump(), retrieved_incidents)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    response = IncidentAnalysisResponse(
        similar_incidents=retrieved_incidents,
        retrieval_diagnostics={
            **_retrieval_diagnostics(retrieved_incidents),
            "evidence_state": evidence.evaluation.state if evidence else "INITIAL_ONLY",
            "evidence_score": evidence.evaluation.score if evidence else 0.0,
            "initial_evidence_state": evidence.initial_evaluation.state if evidence else "INITIAL_ONLY",
            "evidence_expansion_used": evidence.expansion_used if evidence else False,
            "r2_candidates_found": evidence.r2_candidates_found if evidence else 0,
            "r2_incidents_ingested": evidence.r2_incidents_ingested if evidence else 0,
            "r2_incident_ids": evidence.r2_incident_ids if evidence else [],
            "provenance": (
                "PostgreSQL + R2 adaptive evidence expansion"
                if evidence and evidence.expansion_used
                else "PostgreSQL historical knowledge base"
            ),
        },
        evidence_expansion_used=evidence.expansion_used if evidence else False,
        r2_candidates_found=evidence.r2_candidates_found if evidence else 0,
        r2_incidents_ingested=evidence.r2_incidents_ingested if evidence else 0,
        provenance=(
            "PostgreSQL + R2 adaptive evidence expansion"
            if evidence and evidence.expansion_used
            else "PostgreSQL historical knowledge base"
        ),
        **analysis,
    )
    try:
        stored = analysis_repository.create(request.model_dump(), response.model_dump())
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="RCA analysis completed, but could not be saved to history.") from exc
    response.analysis_id = stored["id"]
    return response
