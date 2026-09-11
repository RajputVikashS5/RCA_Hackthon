from fastapi import APIRouter, Depends
from app.api.auth import require_api_auth

from app.config import DEFAULT_TOP_K
from app.models.schemas import IncidentAnalysisRequest, SimilarIncidentResponse
from app.services.retriever import Retriever
from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Similarity"],
    dependencies=[Depends(require_api_auth)],
)

retriever = Retriever()


def _build_incident_query(request: IncidentAnalysisRequest) -> str:

    parts = [f"Description: {request.description.strip()}"]

    for field_name in ["component", "severity", "environment", "incident_type"]:

        value = getattr(request, field_name)

        if value:

            parts.append(f"{field_name.replace('_', ' ').title()}: {value}")

    return "\n".join(parts)


@router.post("/similar", response_model=SimilarIncidentResponse)
async def retrieve_similar_incidents(request: IncidentAnalysisRequest):

    if not request.description.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incident description cannot be empty.")

    incident_query = _build_incident_query(request)

    try:
        incidents = retriever.retrieve(incident_query, top_k=DEFAULT_TOP_K)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return SimilarIncidentResponse(incidents=incidents)
