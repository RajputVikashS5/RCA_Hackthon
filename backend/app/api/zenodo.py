from fastapi import APIRouter, HTTPException, Query, status

from app.config import ZENODO_RECORD_ID, ZENODO_SAMPLE_SIZE
from app.services.zenodo_service import ZenodoService, ZenodoServiceError


router = APIRouter(prefix="/api/zenodo", tags=["Zenodo"])
service = ZenodoService()


@router.get("/test")
async def test_zenodo_connection(
    record_id: str = Query(default=ZENODO_RECORD_ID),
    sample_size: int = Query(default=ZENODO_SAMPLE_SIZE, ge=0, le=20),
):
    try:
        return service.test_connection(record_id, sample_size)
    except ZenodoServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "success": False,
                "source": "Zenodo",
                "recordId": record_id,
                "connection": "failed",
                "error": str(exc),
            },
        ) from exc