from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", "5"))
MIN_SIMILARITY_SCORE = float(os.getenv("MIN_SIMILARITY_SCORE", "0.35"))

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