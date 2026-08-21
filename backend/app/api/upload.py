from pathlib import Path
import os
import shutil

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.config import INCIDENTS_DIR
from app.models.schemas import IncidentUploadResponse
from app.services.incident_ingestion import IncidentIngestionError, SUPPORTED_EXTENSIONS
from app.services.rag_pipeline import RAGPipeline

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Upload"]
)

pipeline = RAGPipeline()

def _clear_incident_folder() -> None:

    folder = Path(INCIDENTS_DIR)

    for existing_file in folder.iterdir():

        if existing_file.is_file():

            existing_file.unlink()


@router.post("/upload", response_model=IncidentUploadResponse)
async def upload_incident_dataset(file: UploadFile = File(...)):

    suffix = Path(file.filename).suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV, JSON, XLS, and XLSX files are supported for incident uploads.",
        )

    _clear_incident_folder()

    save_path = os.path.join(INCIDENTS_DIR, file.filename)

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        stats = pipeline.build_vector_database()
    except IncidentIngestionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - surfaced as a friendly API error
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to index the incident dataset.") from exc

    return IncidentUploadResponse(
        success=True,
        message="Historical incident dataset uploaded and indexed successfully.",
        source_files=[file.filename],
        total_incidents=stats.total_rows,
        indexed_incidents=stats.indexed_rows,
        duplicates_removed=stats.duplicates_removed,
        skipped_rows=stats.skipped_rows,
    )