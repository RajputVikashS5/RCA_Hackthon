# Adaptive Evidence Implementation Report

## Implementation

The project now retains PostgreSQL + pgvector as the primary runtime retrieval
layer and Cloudflare R2 as the raw historical source. Weak or insufficient
first-pass evidence can use a bounded persisted R2 incident catalog, incrementally
ingest relevant records with the existing embedding service, and run a second
PostgreSQL retrieval. Existing IDs are skipped and provenance is stored in the
incident `source` and `metadata` fields.

The API and RCA result UI report evidence state, provenance, expansion usage,
R2 candidate count, and newly ingested count. Gemini grounding and the existing
historical fallback remain in place.

## Validation

- Focused adaptive-evidence tests cover evidence scoring, catalog discovery,
  bounded candidate selection, deduplication seams, and second-pass retrieval.
- Backend: `55 passed, 1 skipped` with `python -m pytest`.
- Frontend: `npm run build` passed (`tsc -b` and Vite production build).
- The R2/Gemini live end-to-end path was not executed because this workspace
  does not provide a verified live database/catalog/API test fixture.

## Limitations

R2 requires a small `R2_CATALOG_KEY` JSON catalog for request-time candidate
discovery. The raw archive is intentionally never downloaded or scanned during
RCA. Without that catalog, the safe result is insufficient evidence and no
adaptive ingestion.

## Verdict

**YES WITH LIMITATIONS** — the implemented runtime can dynamically expand
historical evidence from a prepared R2 catalog and produce evidence-grounded
RCA while preserving the safe fallback. It does not claim semantic search over
the raw archive itself.
