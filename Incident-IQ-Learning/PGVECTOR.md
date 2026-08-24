# PGVector

`pgvector` is an open-source vector similarity search extension for PostgreSQL.

## How it works in Incident-IQ
Instead of using a dedicated vector database (like Pinecone or Milvus), Incident-IQ leverages `pgvector` to store embeddings directly alongside relational data in Postgres.

1. Documents are chunked and converted into vector embeddings (arrays of floats).
2. These arrays are stored in a specialized `VECTOR` column type provided by `pgvector`.
3. When a user queries the system, the query is converted to an embedding.
4. The backend uses `pgvector` operations (like Cosine Distance `<=>` or Euclidean Distance `<->`) to find the most similar document chunks in the database efficiently using HNSW or IVFFlat indexes.
