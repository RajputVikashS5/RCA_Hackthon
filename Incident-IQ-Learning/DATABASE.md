# Database Strategy

Incident-IQ utilizes a polyglot persistence strategy, employing both Relational and NoSQL databases.

## 1. PostgreSQL
Used as the primary relational database and vector store.
- **Library**: `psycopg` (with connection pooling).
- **Models**: Handled in `backend/app/database/models.py`.
- **Primary Use**: Storing structured user data, metadata, and document embeddings via the `pgvector` extension.

## 2. MongoDB
Used as a flexible document store.
- **Library**: `pymongo`.
- **Primary Use**: Storing unstructured or highly dynamic data, such as complete chat histories or raw ingestion logs that don't fit neatly into a rigid schema.
