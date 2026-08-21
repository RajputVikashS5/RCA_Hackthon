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

The source is the open anonymized v7 Public Jira Dataset, currently published at `https://zenodo.org/records/15719919` and referenced by the project configuration. The older record `https://zenodo.org/records/7182101` is restricted; it is retained only as the requested record history.

The v7 download is a large ZIP containing a MongoDB archive. The offline scripts therefore download only when explicitly invoked and expect a local export or JSON/JSONL representation for transformation. Raw archives and exports are ignored and should preferably live outside the repository entirely.

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

- `download_zenodo.py`: explicit, cached download of the latest open release
- `inspect_dataset.py`: local file inventory and lightweight JSON samples
- `process_jira.py`: streaming JSON/JSONL transformation, configurable project and record limit
- `transform_incidents.py`: conservative extraction from fields, comments, status, resolution, components, project, and metadata
- `generate_embeddings.py` and `load_postgres.py`: batch embedding and database upsert path

The default development limit is 50,000 records and the default batch size is 100. `incident_id` deduplication happens before upsert; reruns are resumable through database conflict updates. Missing root-cause evidence remains `NULL`; ingestion never asks Gemini to invent historical facts.

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

## Validation plan

Tests must cover transformation with missing fields, filtering, deduplication, batch behavior, repository upsert/search with a mocked connection, health behavior without credentials, Top-5 ordering, no-result behavior, Gemini failure/fallback, and API contracts. Cloud-specific extension and retrieval tests must run against a PostgreSQL instance with pgvector configured.