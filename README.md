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

Zenodo is an external source dataset, not the application's live database. Metadata is available through `GET /api/zenodo/status`; bounded inspection is available through `POST /api/zenodo/inspect` only after the archive has been explicitly downloaded locally. Normal RCA requests never access Zenodo.

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
ZENODO_RECORD_ID=15719919
ZENODO_API_URL=https://zenodo.org/api/records
ZENODO_CACHE_TTL=3600
ZENODO_REQUEST_TIMEOUT=30
ZENODO_SAMPLE_SIZE=5
INGEST_BATCH_SIZE=100
INGEST_MAX_RECORDS=1000
JIRA_DATA_DIR=C:/external/jira-data
```

The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`, which produces 384-dimensional normalized vectors. PostgreSQL must allow `CREATE EXTENSION vector`.

Initialize the schema and HNSW cosine index:

```bash
cd backend
python -m app.database.init_db
```

Download and inspect the dataset outside the repository. The current open anonymized release is Zenodo v7 at `https://zenodo.org/records/15719919`; it contains a roughly 5.8 GB MongoDB ZIP archive. Do not use restricted record `7182101`, and do not place the archive in Git.

```bash
python ingestion/download_zenodo.py --output-dir C:/external/jira-data
python ingestion/inspect_dataset.py C:/external/jira-data/2025-06-23\ ThePublicJiraDataset.zip --sample-size 5
python ingestion/pipeline.py C:/external/jira-data/2025-06-23\ ThePublicJiraDataset.zip --max-records 100 --batch-size 100
python ingestion/pipeline.py C:/external/jira-data/2025-06-23\ ThePublicJiraDataset.zip --max-records 1000 --batch-size 100
```

The pipeline locates the Jira issue BSON collection inside the ZIP, processes bounded streaming batches, deduplicates by `incident_id`, generates normalized 384-dimensional embeddings, and upserts through the existing PostgreSQL + pgvector repository. It does not fabricate missing root causes or resolutions. `INGEST_MAX_RECORDS` and `INGEST_BATCH_SIZE` control development scale.

Start the services:

```bash
cd backend
python -m uvicorn app.main:app --reload

cd frontend
npm run dev
```

## API

- `GET /api/health` reports database, pgvector, record-count, and vector-search status.
- `POST /api/incidents/similar` retrieves the top five historical matches.
- `POST /api/incidents/analyze` retrieves evidence and generates an RCA.
- `POST /api/incidents/upload` is disabled; dataset management belongs to the offline ingestion pipeline.
- `GET /api/zenodo/status` reports metadata access, archive availability, all files, sizes, and download URLs.
- `POST /api/zenodo/inspect` inspects a bounded sample of a locally downloaded ZIP/BSON archive.
- `GET /api/zenodo/ingestion/status` reports the database knowledge-base status and confirms that ingestion is an explicit offline operation.

## Data and security

Do not commit `.env`, database credentials, Zenodo archives, exported Jira records, generated embeddings, or local vector artifacts. See `.gitignore` and `.env.example`.