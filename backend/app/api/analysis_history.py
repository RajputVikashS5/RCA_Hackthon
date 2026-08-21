from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.database.analysis_repository import AnalysisRepository
from app.models.schemas import StoredAnalysisResponse

router = APIRouter(prefix="/api/analyses", tags=["RCA Analysis History"])
repository = AnalysisRepository()


@router.get("", response_model=list[StoredAnalysisResponse])
async def list_analyses(limit: int = Query(default=50, ge=1, le=100)):
    try:
        return repository.list(limit)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Analysis history is unavailable.") from exc


@router.get("/{analysis_id}", response_model=StoredAnalysisResponse)
async def get_analysis(analysis_id: UUID):
    try:
        record = repository.get(analysis_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Analysis history is unavailable.") from exc
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
    return record


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_analysis(analysis_id: UUID):
    try:
        deleted = repository.delete(analysis_id)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Analysis history is unavailable.") from exc
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")
