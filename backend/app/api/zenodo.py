from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query, status

from app.config import ZENODO_RECORD_ID, ZENODO_SAMPLE_SIZE
from app.database.connection import get_database_status
from app.services.zenodo_service import ZenodoService, ZenodoServiceError


router = APIRouter(prefix="/api/zenodo", tags=["Zenodo"])
service = ZenodoService()


def _zenodo_error(record_id: str, exc: ZenodoServiceError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "connected": False,
            "record_id": record_id,
            "metadata_access": "failed",
            "error": str(exc),
        },
    )


def _coalesce_request_values(
    payload: dict[str, Any] | None,
    *,
    record_id: str,
    sample_size: int,
) -> tuple[str, int]:
    data = payload or {}
    if not isinstance(data, dict):
        return record_id, sample_size
    requested_id = data.get("record_id") or data.get("recordId")
    requested_size = data.get("sample_size") or data.get("sampleSize")
    if requested_id:
        record_id = str(requested_id)
    if requested_size is not None:
        sample_size = max(1, min(int(requested_size), 20))
    return record_id, sample_size


@router.get("/status")
async def zenodo_status(record_id: str = Query(default=ZENODO_RECORD_ID)):
    try:
        return service.get_status(record_id)
    except ZenodoServiceError as exc:
        raise _zenodo_error(record_id, exc) from exc


@router.post("/inspect")
async def inspect_zenodo_dataset(
    payload: dict[str, Any] | None = Body(default=None),
    record_id: str = Query(default=ZENODO_RECORD_ID),
    sample_size: int = Query(default=5, ge=1, le=20),
):
    record_id, sample_size = _coalesce_request_values(payload, record_id=record_id, sample_size=sample_size)
    try:
        result = service.inspect_dataset(record_id, sample_size)
        result["archive_type"] = "mongodb"
        result["inspection"] = "complete"
        result["sample_count"] = int(result.get("sample_count") or 0)
        return result
    except ZenodoServiceError as exc:
        raise _zenodo_error(record_id, exc) from exc


@router.post("/ingest")
async def trigger_zenodo_ingest(
    payload: dict[str, Any] | None = Body(default=None),
):
    data = payload or {}
    limit = data.get("limit", 1000)
    try:
        limit_value = max(1, int(limit))
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": "limit must be a positive integer."},
        ) from None

    return {
        "status": "accepted",
        "mode": "offline-cli",
        "limit": limit_value,
        "message": "Zenodo ingestion is intentionally run outside the normal HTTP path. This endpoint only acknowledges the request and does not download or process the archive inline.",
        "record_id": ZENODO_RECORD_ID,
        "knowledge_base": get_database_status(),
    }


@router.get("/ingestion/status")
async def ingestion_status():
    database = get_database_status()
    return {
        "status": "idle",
        "discovered": 0,
        "processed": 0,
        "inserted": 0,
        "updated": 0,
        "skipped": 0,
        "failed": 0,
        "embeddings": 0,
        "knowledge_base": database,
        "message": "Ingestion runs explicitly through the offline CLI; normal API requests do not start archive jobs.",
    }


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


@router.get("/info")
async def get_zenodo_info(
    record_id: str = Query(default=ZENODO_RECORD_ID),
):
    try:
        return service.get_record_info(record_id)
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