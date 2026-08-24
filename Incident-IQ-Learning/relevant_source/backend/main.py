import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.test_retriever import router as retriever_router
from app.api.upload import router as upload_router
from app.api.zenodo import router as zenodo_router
from app.api.analysis_history import router as analysis_history_router
from app.config import GOOGLE_API_KEY
from app.database.connection import get_database_status, initialize_database


cors_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

app = FastAPI(
    title="Enterprise Incident RCA Assistant",
    description="Backend API for incident ingestion, similar-incident retrieval, and Gemini-powered RCA generation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    import logging
    try:
        initialize_database()
    except Exception as e:
        logging.warning(f"Database initialization failed: {e}. The app will start but database-dependent features will be unavailable.")

app.include_router(chat_router)
app.include_router(retriever_router)
app.include_router(upload_router)
app.include_router(zenodo_router)
app.include_router(analysis_history_router)


@app.get("/")
async def home():
    return {
        "message": "Enterprise Incident RCA Backend Running"
    }


@app.get("/api/health")
async def api_health():
    database = get_database_status()
    database_available = database["database"] == "Connected"
    gemini_configured = GOOGLE_API_KEY and GOOGLE_API_KEY != "your-google-api-key"
        
    system_status = "Healthy"
    if not database_available:
        system_status = "Unavailable"
    elif not gemini_configured:
        system_status = "Degraded"

    return {
        "status": system_status,
        **database,
        "services": {
            "database": "available" if database_available else "unavailable",
            "rag": "available" if database_available and database.get("vector_search") == "Available" else "unavailable",
            "gemini": "healthy" if gemini_configured else "unhealthy",
            "existing_dataset": "available" if database.get("incident_records") else "no indexed records",
            "zenodo": "optional",
    },
    }


@app.get("/health")
async def health():
    return await api_health()
