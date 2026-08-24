from fastapi import APIRouter
from app.config import DEFAULT_TOP_K, MIN_SIMILARITY_SCORE
from app.models.schemas import IncidentAnalysisRequest, IncidentAnalysisResponse
from app.services.llm import GeminiLLM
from app.services.retriever import Retriever
from app.database.analysis_repository import AnalysisRepository
from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Analysis"]
)

retriever = Retriever()
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


import logging

@router.post("/analyze", response_model=IncidentAnalysisResponse)
async def analyze_incident(request: IncidentAnalysisRequest):
    logging.info("[ANALYSIS] Request received")
    
    if not request.description.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incident description cannot be empty.")
    
    logging.info("[ANALYSIS] Input validation passed")

    incident_query = _build_incident_query(request)
    
    logging.info("[EMBEDDING] Starting query embedding")
    try:
        logging.info("[DATABASE] Connecting to PostgreSQL")
        logging.info("[PGVECTOR] Searching historical incidents")
        retrieved_incidents = retriever.retrieve(incident_query, top_k=DEFAULT_TOP_K)
        logging.info(f"[RETRIEVAL] Final evidence count={len(retrieved_incidents)}")
    except RuntimeError as exc:
        logging.error(f"[VECTOR_SEARCH] Failed: {exc}")
        # Use 500 so the frontend extracts the specific structured error message, unlike 503 which is hardcoded.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "The vector database search failed.", "code": "VECTOR_SEARCH_FAILED"}
        ) from exc

    logging.info("[RCA] Calling LLM")
    try:
        analysis = llm.generate_rca(request.model_dump(), retrieved_incidents)
        logging.info("[RCA] LLM response received")
        logging.info("[RCA] Response validation successful")
    except RuntimeError as exc:
        logging.error(f"[RCA] LLM service unavailable: {exc}")
        # Gracefully degrade: return 200 OK with available historical evidence.
        evidence_incidents = []
        if retrieved_incidents:
            score_by_id = {inc.get("incident_id", ""): inc.get("similarity_score", 0.0) for inc in retrieved_incidents}
            evidence_incidents = [
                {"incident_id": inc_id, "similarity_score": score_by_id.get(inc_id, 0.0)}
                for inc_id in [inc.get("incident_id", "") for inc in retrieved_incidents[:3] if inc.get("incident_id")]
            ]
        
        analysis = {
            "evidence_status": "AVAILABLE",
            "confidence": "UNAVAILABLE",
            "message": "Historical evidence available but RCA generation unavailable.",
            "root_cause": None,
            "resolution": None,
            "evidence_strength": "Unavailable",
            "summary": "RCA generation failed. Showing historical evidence only.",
            "evidence_explanation": f"{len(retrieved_incidents)} historical incidents were retrieved successfully.",
            "evidence_incidents": evidence_incidents,
        }
    except ValueError as exc:
        logging.error(f"[RCA] Generation failed: {exc}")
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    response = IncidentAnalysisResponse(
        similar_incidents=retrieved_incidents,
        retrieval_diagnostics=_retrieval_diagnostics(retrieved_incidents),
        **analysis,
    )
    
    try:
        logging.info("[HISTORY] Saving analysis")
        stored = analysis_repository.create(request.model_dump(), response.model_dump())
        response.analysis_id = stored["id"]
    except RuntimeError as exc:
        logging.warning(f"[HISTORY] History storage failed: {exc}")
        # Don't fail the entire request just because history failed.

    logging.info("[ANALYSIS] Returning successful response")
    return response
