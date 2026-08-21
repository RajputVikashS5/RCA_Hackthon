from fastapi import APIRouter, Query

from app.config import ZENODO_RECORD_ID, ZENODO_SAMPLE_SIZE
from app.services.zenodo_service import ZenodoService


router = APIRouter(prefix="/api/zenodo", tags=["Zenodo"])
service = ZenodoService()


@router.get("/test")
async def test_zenodo_connection(
    record_id: str = Query(default=ZENODO_RECORD_ID),
    sample_size: int = Query(default=ZENODO_SAMPLE_SIZE, ge=0, le=20),
):
    # This endpoint is a source probe, not a dependency of RCA. Expected source
    # states (restricted or unavailable) are returned as a successful check.
    return service.test_connection(record_id, sample_size)
