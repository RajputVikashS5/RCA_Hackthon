from fastapi import APIRouter

from app.config import DEFAULT_TOP_K
from app.models.schemas import IncidentAnalysisRequest, SimilarIncidentResponse
from app.services.retriever import Retriever
from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Similarity"]
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
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="FAISS index is not initialized. Upload a historical incident dataset first.") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SimilarIncidentResponse(incidents=incidents)