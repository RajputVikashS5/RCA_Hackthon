from fastapi import APIRouter, HTTPException, status

from app.services.dataset_service import DatasetService
from app.services.r2_storage import R2StorageError


router = APIRouter(prefix="/api/dataset", tags=["Dataset"])
service = DatasetService()


def _storage_error(exc: R2StorageError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@router.get("")
async def dataset_metadata():
    try:
        return service.metadata()
    except R2StorageError as exc:
        raise _storage_error(exc) from exc


@router.get("/files")
async def dataset_files():
    try:
        return {"files": service.files()}
    except R2StorageError as exc:
        raise _storage_error(exc) from exc


@router.get("/status")
async def dataset_status():
    return service.status()
