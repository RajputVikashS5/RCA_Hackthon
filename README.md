# Enterprise Incident RCA Assistant

An evidence-grounded incident analysis assistant for support teams. The runtime path is:

```text
Zenodo Public Jira Dataset
        -> offline ingestion and transformation
        -> batch embeddings
        -> cloud PostgreSQL + pgvector
        -> top 5 cosine-similar incidents
        -> Google Gemini RAG
        -> RCA result in Streamlit
```

The raw Jira dataset and generated embeddings remain outside this Git repository. FastAPI never downloads Zenodo during normal RCA queries.

The read-only Zenodo probe is available at `GET /api/zenodo/test`. It fetches record metadata and, when the record exposes a supported public file, downloads and parses a small cached sample. It never writes Zenodo data to PostgreSQL.

## Features

- Open anonymized v7 Public Jira Dataset ingestion from Zenodo
- Configurable filtering, limits, batching, and resumable upserts
- Conservative Jira-to-incident transformation with nullable root causes
- SentenceTransformer embeddings in PostgreSQL using pgvector
- Top-5 cosine similarity retrieval
- Gemini RCA synthesis grounded only in retrieved evidence
- FastAPI API and Streamlit interface

## Setup

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create `backend/.env` from `.env.example`:

```text
DATABASE_URL=postgresql://username:password@host:5432/database
GOOGLE_API_KEY=your_gemini_api_key
ZENODO_RECORD_ID=7182101
ZENODO_API_URL=https://zenodo.org/api/records
ZENODO_CACHE_TTL=3600
ZENODO_REQUEST_TIMEOUT=30
ZENODO_SAMPLE_SIZE=5
```

The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`, which produces 384-dimensional normalized vectors. PostgreSQL must allow `CREATE EXTENSION vector`.

Initialize the schema and HNSW cosine index:

```bash
cd backend
python -m app.database.init_db
```

Download and inspect the dataset outside the repository. The current open anonymized release is Zenodo v7 at `https://zenodo.org/records/15719919`; it contains a roughly 5.8 GB MongoDB archive.

```bash
python ingestion/download_zenodo.py --output-dir C:/data/public-jira
python ingestion/inspect_dataset.py C:/data/public-jira
python ingestion/load_postgres.py C:/data/public-jira/export --max-records 50000 --batch-size 100
```

The loader processes batches, deduplicates by `incident_id`, and updates existing database rows on reruns. It does not fabricate missing root causes or resolutions. `INGEST_MAX_RECORDS` and `INGEST_BATCH_SIZE` control development scale.

Start the services:

```bash
cd backend
python -m uvicorn app.main:app --reload

cd frontend
npm install
npm run dev
```

## API

- `GET /api/health` reports database, pgvector, record-count, and vector-search status.
- `POST /api/incidents/similar` retrieves the top five historical matches.
- `POST /api/incidents/analyze` retrieves evidence and generates an RCA.
- `POST /api/incidents/upload` is disabled; dataset management belongs to the offline ingestion pipeline.
- `GET /api/zenodo/test` checks the public Zenodo record and returns metadata plus sample records when a supported downloadable file is available.

## Data and security

Do not commit `.env`, database credentials, Zenodo archives, exported Jira records, generated embeddings, or local vector artifacts. See `.gitignore` and `.env.example`.
