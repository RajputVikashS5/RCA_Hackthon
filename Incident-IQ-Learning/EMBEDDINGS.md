# Embeddings

Embeddings are numerical representations of text that capture semantic meaning.

## Implementation
Incident-IQ uses `sentence-transformers` to generate embeddings locally.
- **Service**: Located in `backend/app/services/embedding.py`.
- **Process**: When text (a document chunk or a user query) is processed, the sentence-transformer model converts the text into a dense vector (e.g., 384 or 768 dimensions).
- **Why local?**: Using `sentence-transformers` locally saves API costs compared to calling external embedding APIs like OpenAI's text-embedding-ada-002, while still providing high-quality semantic vectors.
