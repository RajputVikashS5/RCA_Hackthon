from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.test_retriever import router as retriever_router
from app.api.upload import router as upload_router
from app.api.zenodo import router as zenodo_router
from app.api.analysis_history import router as analysis_history_router
from app.api.dataset import router as dataset_router
from app.services.dataset_service import DatasetService
from app.database.connection import get_database_status, verify_database_schema
from app.config import CORS_ALLOWED_ORIGINS
from app.services.embedding import EmbeddingModel
from app.services.llm import GeminiLLM

health_embedding_model = EmbeddingModel()
health_llm = GeminiLLM()

app = FastAPI(
    title="Enterprise Incident RCA Assistant",
    description="Backend API for incident ingestion, similar-incident retrieval, and Gemini-powered RCA generation.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    verify_database_schema()
    health_embedding_model._ensure_model()

app.include_router(chat_router)
app.include_router(retriever_router)
app.include_router(upload_router)
app.include_router(zenodo_router)
app.include_router(analysis_history_router)
app.include_router(dataset_router)


@app.get("/")
async def home():
    return {
        "message": "Enterprise Incident RCA Backend Running"
    }


@app.get("/api/health")
async def api_health():
    database = get_database_status()
    database_available = database["database"] == "Connected"
    vector_available = database_available and database["vector_extension"] == "Available"
    embedding = health_embedding_model.healthcheck()
    gemini = health_llm.healthcheck()
    dataset_status = DatasetService().status()
    dependencies = {
        "api": {"status": "available"},
        "database": {"status": "available" if database_available else "unavailable"},
        "pgvector": {"status": "available" if vector_available else "unavailable"},
        "embedding_model": embedding,
        "gemini": gemini,
    }
    all_required_available = all(
        item["status"] == "available" for item in dependencies.values()
    )
    return {
        "status": "Healthy" if all_required_available else "Degraded",
        "readiness": "ready" if all_required_available else "degraded",
        **database,
        "dependencies": dependencies,
        "services": {
            "database": "available" if database_available else "unavailable",
            "rag": "available" if vector_available and embedding["status"] == "available" else "unavailable",
            "gemini": gemini["status"],
            "existing_dataset": "available" if database["incident_records"] else "no indexed records",
            # Zenodo is intentionally not contacted by health checks or RCA.
            "zenodo": "optional",
            "r2_configured": dataset_status["configured"],
            "r2_bucket_accessible": dataset_status["bucket_accessible"],
        },
    }


@app.get("/health")
async def health():
    return await api_health()
