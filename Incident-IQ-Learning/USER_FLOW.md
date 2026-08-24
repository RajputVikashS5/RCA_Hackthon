# User Flow

This document describes the typical user journeys within Incident-IQ.

## 1. Document Ingestion
1. User uploads a document (e.g., PDF) via the frontend UI.
2. Frontend sends a `multipart/form-data` request to the backend `/api/upload` endpoint.
3. Backend processes the file (`pdf_loader.py`), chunks it (`chunker.py`), generates embeddings (`embedding.py`), and stores it in the vector DB.

## 2. RAG Query (Chat)
1. User types a query into the chat interface.
2. Frontend sends a request to the backend `/api/chat` endpoint.
3. Backend takes the query, generates its embedding, retrieves similar documents from `pgvector`, and sends the context + query to Gemini via LangChain.
4. Gemini streams or returns the generated response back to the user interface.
