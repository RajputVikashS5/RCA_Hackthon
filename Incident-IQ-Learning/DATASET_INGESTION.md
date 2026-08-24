# Dataset Ingestion

Before RAG can work, documents must be ingested and processed.

## Pipeline
1. **Loading**: Files are loaded (e.g., using `pdf_loader.py` for PDFs or `zenodo_service.py` to fetch datasets from Zenodo).
2. **Chunking**: `chunker.py` breaks large documents into smaller, manageable pieces (chunks). This is crucial because LLMs have token limits, and smaller chunks yield more precise vector search results.
3. **Embedding**: Each chunk is passed to the embedding service to create a vector.
4. **Storage**: The text chunk and its corresponding vector are saved to `pgvector`.
