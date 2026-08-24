# API Flow

The API flow bridges the React frontend and the FastAPI backend.

## Sequence

1. **Frontend Request**: Triggered by user interaction (e.g., TanStack Query `useMutation` on a form submit).
2. **Network Layer**: Frontend `fetch` or Axios instance sends an HTTP request to `http://localhost:8000/api/...`.
3. **FastAPI Router**: The request hits `backend/app/main.py`, which delegates to the specific router in `backend/app/api/` (e.g., `chat.py`).
4. **Service Layer**: The router validates the Pydantic schema and calls the relevant service in `backend/app/services/` (e.g., `rag_pipeline.py`).
5. **Database/LLM Interaction**: The service retrieves data from Postgres/Mongo or calls the Gemini LLM.
6. **Response**: Data is serialized back into JSON via Pydantic and returned to the frontend.
