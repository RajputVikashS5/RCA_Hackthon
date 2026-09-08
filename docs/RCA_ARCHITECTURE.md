# RCA Architecture

## Runtime flow

1. FastAPI validates an incident request.
2. `EmbeddingModel` lazily loads `sentence-transformers/all-MiniLM-L6-v2` and produces normalized 384-dimensional vectors.
3. PostgreSQL with pgvector performs semantic and full-text hybrid retrieval.
4. Gemini receives only the new incident and retrieved historical evidence.
5. The response is sanitized, evidence IDs are restricted to retrieved IDs, and the complete result is persisted in `rca_analyses`.
6. The frontend reads analysis history and dependency status from the API; browser state is only a cache.

## Health semantics

`GET /api/health` always reports API reachability in `dependencies.api`. Database, pgvector, embedding, and Gemini statuses are checked independently. The `readiness` field is `ready` only when every required dependency is available. A HTTP 200 response does not imply that every dependency is healthy.

## Data ownership

PostgreSQL is the source of truth for incidents and RCA history. Dataset archives are external ingestion inputs and are never queried during normal RCA requests.

## Security boundaries

Secrets remain server-side. Historical incident text is untrusted evidence and is delimited in the Gemini prompt. Model output is parsed as JSON and supporting incident IDs are allow-listed against retrieved records.
