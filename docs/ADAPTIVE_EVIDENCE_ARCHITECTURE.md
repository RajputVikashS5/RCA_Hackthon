# Adaptive Historical Evidence Retrieval

## Current and target architecture

The existing runtime path is a FastAPI request, query embedding, PostgreSQL
`pgvector` hybrid retrieval, and Gemini synthesis with a documented historical
fallback. Cloudflare R2 remains the raw Jira archive and is not queried during
normal requests.

The adaptive path keeps that default. It evaluates the first PostgreSQL result
set using semantic similarity, documented root cause and resolution fields,
result count, and agreement between root causes. Strong or medium evidence goes
directly to RCA. Weak or insufficient evidence consults a bounded, persisted
R2 incident catalog, selects only relevant candidates, ingests them into
PostgreSQL, and runs retrieval again.

## R2 and PostgreSQL responsibilities

- **R2:** raw archive plus a small `R2_CATALOG_KEY` JSON catalog. The catalog
  contains searchable incident summaries and provenance such as `r2_object_key`
  and `dataset_version`.
- **PostgreSQL + pgvector:** the persistent runtime knowledge base and the only
  semantic retrieval layer. Adaptive records use `source=r2-adaptive`.
- **Embedding service:** the existing 384-dimensional SentenceTransformer
  service is reused for newly ingested candidates only.

R2 object storage has no semantic search capability. The application therefore
does not pretend that the 2.8GB archive can be searched directly. A catalog must
be prepared once or refreshed as a background/offline operation. If it is
missing, adaptive expansion safely returns no candidates rather than scanning
or downloading the archive.

## Retrieval, expansion, and validation

1. Build the incident query and run the existing PostgreSQL hybrid retrieval.
2. Evaluate evidence as `STRONG`, `MEDIUM`, `WEAK`, or `INSUFFICIENT`.
3. For weak/insufficient results, read only the bounded catalog (default 16 MiB)
   and return at most `R2_MAX_CANDIDATES` candidates.
4. Require an incident ID, title, and description before ingestion. Deduplicate
   against PostgreSQL incident IDs; existing records are not re-embedded.
5. Store provenance in `source` and `metadata`, upsert new records, and rerun
   PostgreSQL retrieval.
6. Use the improved evidence set for the existing Gemini grounding and
   historical fallback. Gemini output still sanitizes supporting IDs and
   documented root-cause/resolution values.

The API exposes retrieval diagnostics including evidence state and score,
whether expansion ran, candidate and ingestion counts, candidate IDs, and
provenance. The frontend renders these without exposing credentials.

## Safety and performance

Historical Jira text is untrusted evidence and remains enclosed as data in the
Gemini prompt. No R2, database, or API credentials are returned to clients.
Normal strong-evidence requests perform no R2 operation. Catalog size,
candidate count, top-K, and thresholds are configurable through environment
variables. Incremental ingestion is idempotent by the unique Jira incident ID.

The deliberate limitation is that adaptive expansion cannot discover records
from an archive without a catalog or another prebuilt index. Returning
insufficient evidence is safer than implementing a fake semantic R2 search or
scanning the archive on every request.
