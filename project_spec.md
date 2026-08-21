# Enterprise Incident RCA Assistant — Project Specification

This repository is an existing FastAPI + Streamlit RAG application that has been transformed from generic PDF question answering into an **Enterprise Incident Root Cause Analysis (RCA) Assistant**.

The project goal is to help support engineers analyze a newly reported incident, retrieve the most similar historical incidents, and generate a concise RCA recommendation grounded in historical evidence.

## Current Product Shape

Primary workflow:

```text
Historical Incident Dataset
        ↓
Validation + Cleaning + Normalization
        ↓
Incident Records
        ↓
Search Text + Embeddings
        ↓
FAISS Vector Store
        ↓
New Incident Analysis
        ↓
Top 5 Similar Historical Incidents
        ↓
Gemini RCA Summary
```

The legacy PDF ingestion utilities are kept as reusable building blocks, but the RCA incident workflow is the primary product path.

## Architecture

Backend:

- FastAPI application in [backend/app/main.py](backend/app/main.py)
- Pydantic models in [backend/app/models/schemas.py](backend/app/models/schemas.py)
- Configuration in [backend/app/config.py](backend/app/config.py)
- Service layer in [backend/app/services/](backend/app/services)

Frontend:

- Streamlit app in [frontend/app.py](frontend/app.py)

Storage:

- Uploaded incident datasets are stored under [backend/app/data/](backend/app/data)
- FAISS index and metadata are stored under [backend/app/vector_db/](backend/app/vector_db)

## Data Model

Required incident fields:

- `incident_id`
- `title`
- `description`
- `root_cause`
- `resolution`

Optional fields supported by the ingestion pipeline:

- `component`
- `service`
- `severity`
- `environment`
- `incident_type`
- `date`
- `status`
- `tags`

An incident record is normalized into a searchable text representation and also preserved as structured metadata.

## Ingestion Workflow

Supported input formats:

- CSV as the primary format
- JSON and Excel when available through pandas readers

Ingestion behavior:

- Validate required columns
- Normalize column names and whitespace
- Drop empty or invalid rows
- Preserve incident IDs, root causes, and resolutions
- Deduplicate by `incident_id`
- Build a searchable incident text block
- Generate embeddings for the combined representation
- Persist FAISS index plus metadata

The incident text representation is derived from the full record, not arbitrary chunking.

## Embeddings

The project reuses the existing SentenceTransformer-based embedding model in [backend/app/services/embedding.py](backend/app/services/embedding.py).

Current implementation choice:

- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Embeddings are L2-normalized before indexing and querying
- FAISS uses `IndexFlatL2`
- Returned FAISS distances are converted to cosine similarity using:

```text
similarity = 1 - (squared_l2_distance / 2)
```

Because this is a normalized similarity score rather than a probability, the UI displays it as a similarity value instead of a percentage unless explicitly formatted for presentation.

## Retrieval

Retrieval returns the top 5 most similar historical incidents.

Each result includes:

- `incident_id`
- `title`
- `description`
- `root_cause`
- `resolution`
- `similarity_score`
- `metadata`

Only the retrieved incidents are passed into Gemini. The full dataset is never sent to the model.

## Gemini RCA Strategy

Gemini is used for evidence-grounded RCA synthesis, not free-form document Q&A.

Prompt behavior:

- Analyze the new incident description
- Review retrieved historical incidents
- Identify the most likely root cause
- Recommend a resolution
- Cite supporting incident IDs
- Distinguish evidence from inference
- Avoid inventing incidents, causes, or resolutions
- State when evidence is insufficient

The backend expects a structured RCA response and falls back to a safe no-evidence response if the model output is invalid or historical evidence is weak.

## API Contract

Primary endpoints:

- `POST /api/incidents/upload` uploads and indexes a historical incident dataset
- `POST /api/incidents/analyze` analyzes a new incident and returns RCA output
- `POST /api/incidents/similar` returns the top 5 similar incidents without Gemini
- `GET /api/health` reports service health

Legacy document-oriented routes are not the primary workflow anymore.

## Frontend

The Streamlit UI is an incident RCA dashboard:

- Dataset upload panel
- New incident analysis form
- Top 5 similar incidents view
- RCA result summary
- Evidence-oriented display of incident IDs, similarity, root causes, and resolutions

## Error Handling

The backend handles or should handle the following gracefully:

- Missing Gemini API key
- Invalid or empty dataset
- Missing required columns
- Duplicate incident IDs
- Empty incident description
- Uninitialized FAISS index
- Embedding failures
- Gemini API failures
- Invalid Gemini JSON responses
- No sufficiently relevant historical incidents

User-facing errors must not expose secrets, raw stack traces, or `.env` contents.

## Testing

The repository now needs a proper pytest suite covering:

- Ingestion validation and deduplication
- Retrieval ranking and similarity scoring
- RCA generation and fallback behavior
- API upload, analyze, similar, and health endpoints

Tests should avoid network access and mock Gemini plus embedding-heavy code where appropriate.

## Security

Secrets and generated artifacts must remain untracked.

Important exclusions:

- `.env`
- API keys
- credentials
- private datasets
- generated FAISS artifacts

## Files Reused From the Original Project

The following modules are intentionally reused and extended rather than replaced:

- [backend/app/services/embedding.py](backend/app/services/embedding.py)
- [backend/app/services/vector_store.py](backend/app/services/vector_store.py)
- [backend/app/services/retriever.py](backend/app/services/retriever.py)
- [backend/app/services/llm.py](backend/app/services/llm.py)
- [backend/app/services/rag_pipeline.py](backend/app/services/rag_pipeline.py)

## Major Design Decisions

- The system remains a single FastAPI backend plus one Streamlit frontend.
- FAISS stays the vector store.
- Google Gemini remains the LLM.
- The primary knowledge source is historical incidents, not generic PDFs.
- Similarity is reported as a normalized similarity score derived from normalized FAISS distances.
- The output is evidence-first RCA, not open-ended chat.

## Change Log

- Initial transform from PDF Q&A to incident RCA assistant
- Introduced incident ingestion and top-5 retrieval requirements
- Defined normalized FAISS similarity scoring
- Shifted Gemini usage to structured RCA generation
- Aligned backend, Streamlit UI, and pytest coverage with the incident RCA workflow
       ↓
15. Add tests
       ↓
16. Update README
       ↓
17. Update PROJECT_SPEC.md
       ↓
18. Run and verify complete application
```

---

# PHASE 21 — IMPORTANT DEVELOPMENT BEHAVIOR

Before editing a file, inspect its current contents.

Do not assume the repository matches the example architecture.

Use the actual existing code as the source for implementation.

If the existing architecture differs from this specification:

* Prefer the existing architecture when it is sound.
* Adapt the specification to the actual implementation.
* Document the final decision in `PROJECT_SPEC.md`.

Do not duplicate existing functionality.

Do not create files with overlapping responsibilities.

Keep functions small and understandable.

Use environment variables for secrets.

Keep the application runnable after each major phase.

---

# PHASE 22 — FINAL VALIDATION

After implementation, verify:

```text
[ ] Application starts successfully
[ ] FastAPI starts successfully
[ ] Swagger works
[ ] Streamlit starts successfully
[ ] Historical CSV uploads successfully
[ ] Dataset is validated
[ ] Embeddings are generated
[ ] FAISS index is created
[ ] New incident can be entered
[ ] Top 5 similar incidents appear
[ ] Similarity scores appear
[ ] Historical root causes appear
[ ] Historical resolutions appear
[ ] Gemini generates RCA
[ ] RCA contains likely root cause
[ ] RCA contains recommended resolution
[ ] RCA contains evidence
[ ] RCA contains concise summary
[ ] Error cases are handled
[ ] README is updated
[ ] PROJECT_SPEC.md is updated
[ ] No API keys are committed
```

If possible, perform a complete end-to-end test using a sample incident dataset.

---

# FINAL GOAL

The final application must no longer feel like a generic:

```text
"Chat with your PDFs"
```

It should clearly function as:

```text
        ENTERPRISE INCIDENT
                ↓
        SEMANTIC SEARCH
                ↓
     TOP 5 HISTORICAL INCIDENTS
                ↓
       ROOT CAUSE EVIDENCE
                ↓
        GEMINI RAG ANALYSIS
                ↓
        ┌─────────────────┐
        │ Likely Root     │
        │ Cause           │
        │                 │
        │ Resolution      │
        │                 │
        │ Evidence        │
        │                 │
        │ RCA Summary     │
        └─────────────────┘
```

The final product should directly satisfy the KIET Root Cause Analysis use case while preserving as much of the existing Enterprise RAG implementation as reasonably possible.
