# Enterprise RCA frontend

This Vite + React application is the web interface for the FastAPI RCA backend.

## Run locally

Start the backend from the repository root:

```bash
cd backend
python -m uvicorn app.main:app --reload
```

Then start this application:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

The Vite `/api` proxy sends requests to `http://127.0.0.1:8000` by default. For a deployed API, set `VITE_API_BASE_URL` in `.env`; the backend origin is not embedded in UI components.

## Connected API contracts

- `POST /api/incidents/analyze` — retrieve historical evidence and generate a Gemini RCA
- `POST /api/incidents/similar` — PostgreSQL/pgvector similarity search
- `GET /api/health` — database and vector-search health
- `GET /api/zenodo/test` — read-only Zenodo connectivity probe

FastAPI currently exposes no authentication, so analysis history is application-wide rather than user-specific. Completed RCA analyses are stored in the existing PostgreSQL database and available through `/api/analyses`.
