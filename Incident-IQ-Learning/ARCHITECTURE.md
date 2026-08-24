# Architecture

Incident-IQ follows a modern client-server architecture with a heavy emphasis on AI capabilities using Retrieval-Augmented Generation (RAG).

## High-Level Components

1. **Frontend (Client)**
   - **Framework**: React (built with Vite for fast HMR and compilation).
   - **Language**: TypeScript.
   - **State Management**: Zustand for global state, TanStack React Query for server-state caching and async requests.
   - **Routing**: React Router DOM.

2. **Backend (Server)**
   - **Framework**: FastAPI (Python).
   - **AI Orchestration**: LangChain.
   - **Embeddings**: `sentence-transformers`.
   - **LLM**: Google Gemini (`google-genai`).

3. **Data Layer**
   - **Vector Database**: PostgreSQL with the `pgvector` extension (using psycopg for connection).
   - **Document Store**: MongoDB (via PyMongo) for unstructured data or chat history.
