from fastapi import APIRouter
from app.config import DEFAULT_TOP_K
from app.models.schemas import IncidentAnalysisRequest, IncidentAnalysisResponse
from app.services.llm import GeminiLLM
from app.services.retriever import Retriever
from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Analysis"]
)

retriever = Retriever()
llm = GeminiLLM()


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
        retrieved_incidents = retriever.retrieve(incident_query, top_k=DEFAULT_TOP_K)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="FAISS index is not initialized. Upload a historical incident dataset first.") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    try:
        analysis = llm.generate_rca(request.model_dump(), retrieved_incidents)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return IncidentAnalysisResponse(
        similar_incidents=retrieved_incidents,
        **analysis,
    )
