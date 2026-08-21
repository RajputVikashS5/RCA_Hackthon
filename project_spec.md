# Enterprise Incident RCA Assistant - Project Specification

## Product goal

The application analyzes a newly reported incident, retrieves the five most similar historical Jira incidents, and produces an evidence-grounded RCA with Google Gemini.

## Architecture

```text
Zenodo Public Jira Dataset
        -> offline inspection and ingestion
        -> Jira-to-incident transformation
        -> batch embedding generation
        -> cloud PostgreSQL + pgvector
        -> cosine Top-5 retrieval
        -> Gemini evidence-grounded RCA
        -> FastAPI
        -> Streamlit
```

The raw Zenodo dataset is external and must remain outside the repository. Normal FastAPI startup and RCA requests never download Zenodo or read local Jira files.

## Dataset

The source is the open anonymized Public Jira Dataset v7 at `https://zenodo.org/records/15719919`. The restricted record `https://zenodo.org/records/7182101` is not used.

The v7 release is a roughly 5.8 GB ZIP containing MongoDB BSON collections. Zenodo metadata access does not mean Jira records are available to runtime requests. The offline ingestion scripts explicitly download the archive outside the repository, inspect only bounded samples, stream the Jira issue collection, and write transformed records to PostgreSQL. Raw archives and exports are ignored and must remain outside Git.

## Database

Configuration uses the provider-neutral `DATABASE_URL` PostgreSQL connection string. `backend/app/database/connection.py` lazily creates a psycopg connection pool. `backend/app/database/init_db.py` is the reproducible initialization command.

Initialization creates `vector` once, creates the `incidents` table, and creates an HNSW index using `vector_cosine_ops`. The selected `sentence-transformers/all-MiniLM-L6-v2` model is normalized and produces 384 dimensions, so the embedding column is `VECTOR(384)`. The dimension is configured and validated rather than assumed by retrieval.

The schema contains:

- `id BIGSERIAL PRIMARY KEY`
- unique, required `incident_id`
- title, description, nullable root_cause and resolution
- comments, project, component, service, severity, environment, incident_type, status
- created_at, updated_at, source, source_url
- JSONB metadata
- 384-dimensional embedding

`IncidentRepository.upsert_batch` updates rows on `incident_id` conflicts. `search` orders by pgvector cosine distance and returns `1 - distance` as a cosine similarity score, without percentage conversion.

## Ingestion

The independent `ingestion/` package contains:

- `download_zenodo.py`: explicit, cached download of the v7 MongoDB ZIP
- `inspect_dataset.py`: bounded ZIP/BSON collection and schema inspection
- `jira_reader.py`: streaming Jira BSON batches with configurable limits
- `jira_transformer.py`: conservative Jira-to-incident transformation
- `embedding_pipeline.py`: normalized 384-dimensional batch embeddings
- `postgres_loader.py`: repository-backed PostgreSQL + pgvector upserts
- `pipeline.py`: offline orchestration and progress statistics

The default development limit is `INGEST_MAX_RECORDS=1000` and the default batch size is `INGEST_BATCH_SIZE=100`. The first validation runs use limits of 100 and 1000 records. `incident_id` deduplication happens before upsert; reruns update existing rows through the unique key. Missing root-cause evidence remains `NULL`; ingestion never asks Gemini to invent historical facts.

The searchable text includes incident ID, title, description, comments, any explicit root cause, resolution, and relevant metadata. The same embedding model and normalization are used for indexing and querying.

## Runtime API

- `GET /api/health`: API health plus database connection, vector extension, incident count, dimension, and vector-search status.
- `POST /api/incidents/similar`: embed the submitted incident and return up to five PostgreSQL matches.
- `POST /api/incidents/analyze`: retrieve matches, pass only those matches to Gemini, and return root cause, resolution, evidence strength, supporting IDs, similar incidents, and summary.
- `POST /api/incidents/upload`: disabled for normal runtime use; the offline ingestion command owns dataset management.

The Streamlit UI contains only the incident form, RCA results, and a knowledge-base status panel. It does not upload Zenodo data.

## Gemini behavior

Gemini receives the new incident and only the retrieved historical evidence. The prompt requires evidence/inference distinction, valid supporting IDs, and an insufficient-evidence response. It must not invent incident IDs, historical causes, or resolutions.

## Migration status and compatibility

The old FAISS modules remain in the repository temporarily as migration-era code and as historical test references, but they are no longer imported by the production retrieval path. Once PostgreSQL/pgvector has been validated in the configured cloud environment, `vector_store.py`, `rag_pipeline.py`, `faiss-cpu`, and stale FAISS tests can be removed in a separate cleanup pass.

## Security

Secrets are loaded from environment variables and are never returned by health endpoints. `.env`, raw data, archives, exports, processed files, and generated vector artifacts are ignored. Database errors return generic status details rather than connection strings.

## Runtime debugging notes and final architecture

The production runtime path is intentionally separated from the offline ingestion workflow:

```text
Offline / Admin workflow
Zenodo
  -> download & inspect dataset
  -> transform Jira records
  -> generate embeddings
  -> insert into PostgreSQL + pgvector

Runtime workflow
React
  -> FastAPI
  -> generate embedding for the new incident
  -> query PostgreSQL + pgvector for Top 5
  -> pass retrieved evidence to Gemini
  -> return structured RCA
```

The initial production issue was caused by a real backend dependency problem rather than a frontend bug: the PostgreSQL connection was available, but the `vector` extension and `incidents` schema were not initialized at app startup. Retrieval therefore failed during the first similarity query and surfaced as a generic 500 response. The fix is to initialize the database vector extension early during FastAPI startup and to validate the database health endpoint without exposing credentials.

The second issue was a local development CORS misconfiguration. The Vite React app runs on `http://localhost:5173` and `http://127.0.0.1:5173`, so the backend must explicitly allow these origins while avoiding `allow_credentials=True` with wildcard origins. The runtime configuration uses explicit allowed origins and the standard `*` methods/headers policy for the browser request.

The Zenodo API is intentionally separate from runtime RCA. `/api/zenodo/status` verifies metadata and identifies the actual MongoDB ZIP without downloading it. `/api/zenodo/inspect` reads only a bounded sample from an archive already downloaded to `JIRA_DATA_DIR`. Ingestion runs explicitly through the CLI; no normal HTTP request starts a multi-gigabyte job.

The user-facing analysis flow must never depend on downloading Zenodo data. Normal RCA requests operate only against the cloud PostgreSQL + pgvector knowledge base and the Gemini model.

## Validation plan

Tests cover transformation with missing fields, filtering, deduplication, batch behavior, repository upsert/search with a mocked connection, health behavior without credentials, Top-5 ordering, no-result behavior, Gemini failure/fallback, API contracts, CORS origin validation, and lightweight Zenodo connectivity checks. Cloud-specific extension and retrieval tests must run against a PostgreSQL instance with pgvector configured.