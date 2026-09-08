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

## Cloudflare R2 Dataset Storage

R2 stores the raw Jira archive while PostgreSQL + pgvector stores transformed incidents and embeddings.

1. Create a Cloudflare R2 bucket and a restricted S3 API token.
2. Add the server-side `R2_*` values from `.env.example` to `backend/.env`.
3. Test with a small file before uploading the full archive:

   ```bash
   python ingestion/upload_dataset.py --file test-r2.txt --key test/test-r2.txt
   ```

4. Upload the Jira archive with a predictable key:

   ```bash
   python ingestion/upload_dataset.py --file "E:\path\to\jira-dataset.zip" --key raw/jira-dataset.zip
   ```

5. Check `GET /api/dataset/status`, then ingest a bounded sample:

   ```bash
   python ingestion/pipeline.py --source r2 --max-records 1000
   ```

6. Verify the resulting records and embeddings in PostgreSQL before setting `INGEST_MAX_RECORDS=0` for a full batch ingestion.

## Setup

Install dependencies:

```bash
pip install -r backend/requirements.txt
```

Create `backend/.env` from `.env.example`:

```text
DATABASE_URL=postgresql://username:password@host:5432/database
GOOGLE_API_KEY=your_gemini_api_key
ZENODO_RECORD_ID=7740379
ZENODO_API_URL=https://zenodo.org/api/records
ZENODO_ACCESS_TOKEN=your_zenodo_access_token
ZENODO_CACHE_TTL=3600
ZENODO_REQUEST_TIMEOUT=30
ZENODO_SAMPLE_SIZE=5
INGEST_BATCH_SIZE=100
INGEST_MAX_RECORDS=1000
JIRA_DATA_DIR=C:/external/jira-data
```

Store the Zenodo access token in the backend environment file at `backend/.env` as `ZENODO_ACCESS_TOKEN=...`. Keep it server-side: the frontend must not receive or send this token. The backend uses it only for Zenodo metadata and explicit offline archive-download requests, and sends it as a Bearer header. Never commit `backend/.env`; rotate the token immediately if it has been exposed.

The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`, which produces 384-dimensional normalized vectors. PostgreSQL must allow `CREATE EXTENSION vector`.

Initialize the schema and HNSW cosine index:

```bash
cd backend
python -m app.database.init_db
```

Download and inspect the dataset outside the repository. The current open anonymized release is the Apache Jira dataset at `https://zenodo.org/records/7740379`; it contains a MongoDB archive and metadata files. Do not use restricted record `7182101`, and do not place the archive in Git.

```bash
python ingestion/download_zenodo.py --output-dir E:/external/jira-data
python ingestion/inspect_dataset.py E:/external/jira-data/issues.bson.gz --sample-size 5
python ingestion/pipeline.py E:/external/jira-data/issues.bson.gz --max-records 1000 --batch-size 10 --replace-source
```

The pipeline supports ZIP and gzipped BSON input, processes bounded streaming batches, deduplicates by `incident_id`, generates normalized 384-dimensional embeddings, and upserts through the existing PostgreSQL + pgvector repository. It does not fabricate missing root causes or resolutions. Low-quality SEO-like titles are excluded before embedding. `INGEST_MAX_RECORDS` and `INGEST_BATCH_SIZE` control development scale.

Runtime retrieval combines normalized cosine similarity with PostgreSQL full-text relevance. Semantic similarity remains the reported `similarity_score`; the combined `retrieval_score` is used only for ordering. RCA responses include retrieval diagnostics such as result count, highest/average similarity, and evidence-bearing records.

`--replace-source` deletes only the existing Apache Jira rows before rebuilding that source. For large archives, run bounded windows in separate processes. Use `--skip-records` to resume after a completed window without deleting existing rows:

```bash
python ingestion/pipeline.py E:/external/jira-data/issues.bson.gz --max-records 1000 --batch-size 10 --replace-source
python ingestion/pipeline.py E:/external/jira-data/issues.bson.gz --skip-records 1000 --max-records 1000 --batch-size 10
```

Keep the archive outside Git even though archive extensions are ignored by `.gitignore`.

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
- `GET /api/zenodo/status` reports metadata access, archive availability, all files, sizes, and download URLs.
- `POST /api/zenodo/inspect` inspects a bounded sample of a locally downloaded ZIP/BSON archive.
- `GET /api/zenodo/ingestion/status` reports the database knowledge-base status and confirms that ingestion is an explicit offline operation.
- `GET /api/dataset`, `GET /api/dataset/files`, and `GET /api/dataset/status` expose R2 metadata only; they never download the raw archive to a browser.

## Data and security

Do not commit `.env`, database credentials, Zenodo archives, exported Jira records, generated embeddings, or local vector artifacts. See `.gitignore` and `.env.example`.

## RCA validation

See [`docs/RCA_ARCHITECTURE.md`](docs/RCA_ARCHITECTURE.md) for runtime boundaries and [`docs/RCA_EVALUATION.md`](docs/RCA_EVALUATION.md) for the measured evaluation method. [`docs/FINAL_RCA_VALIDATION_REPORT.md`](docs/FINAL_RCA_VALIDATION_REPORT.md) records the current verified and unverified status. PostgreSQL remains the source of truth for incidents and analysis history; local browser state is not a second database.
