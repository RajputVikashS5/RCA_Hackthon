from fastapi import APIRouter, HTTPException, status

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incident Ingestion"],
)


@router.post("/upload")
async def upload_incident_dataset():
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Dataset uploads are disabled. Run the offline ingestion pipeline to update the cloud knowledge base.",
    )