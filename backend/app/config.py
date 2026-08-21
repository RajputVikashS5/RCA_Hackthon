from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
MIN_SIMILARITY_SCORE = float(os.getenv("MIN_SIMILARITY_SCORE", "0.35"))
EMBEDDING_MODEL_NAME = os.getenv(
	"EMBEDDING_MODEL_NAME",
	"sentence-transformers/all-MiniLM-L6-v2",
)
EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", "384"))
INGEST_BATCH_SIZE = int(os.getenv("INGEST_BATCH_SIZE", "100"))
INGEST_MAX_RECORDS = int(os.getenv("INGEST_MAX_RECORDS", "50000"))
ZENODO_RECORD_URL = os.getenv(
	"ZENODO_RECORD_URL",
	"https://zenodo.org/api/records/7182101",
)
ZENODO_RECORD_ID = os.getenv("ZENODO_RECORD_ID", "7182101")
ZENODO_API_URL = os.getenv("ZENODO_API_URL", "https://zenodo.org/api/records")
ZENODO_CACHE_TTL = int(os.getenv("ZENODO_CACHE_TTL", "3600"))
ZENODO_REQUEST_TIMEOUT = float(os.getenv("ZENODO_REQUEST_TIMEOUT", "30"))
ZENODO_SAMPLE_SIZE = int(os.getenv("ZENODO_SAMPLE_SIZE", "5"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DOCUMENTS_DIR = os.path.join(BASE_DIR, "data", "documents")
INCIDENTS_DIR = os.path.join(BASE_DIR, "data", "incidents")
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
INCIDENT_VECTOR_DB_DIR = os.path.join(VECTOR_DB_DIR, "incidents")

# Create folders if they don't exist
os.makedirs(DOCUMENTS_DIR, exist_ok=True)
os.makedirs(INCIDENTS_DIR, exist_ok=True)
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(INCIDENT_VECTOR_DB_DIR, exist_ok=True)