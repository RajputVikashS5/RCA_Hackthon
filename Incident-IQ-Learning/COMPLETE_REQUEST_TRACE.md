# Complete Request Trace (RAG Query)

Here is a step-by-step trace of a user asking a question.

1. **User Action**: Types "What is the RCA procedure?" and clicks Send.
2. **Frontend UI**: React state updates. `useMutation` triggers an API call to `/api/chat`.
3. **FastAPI Route**: `app/api/chat.py` receives the JSON payload. Pydantic validates the request.
4. **LangChain Pipeline**: The route calls the RAG service.
5. **Embedding**: The query is converted to a vector via `sentence-transformers`.
6. **Vector Search**: `pgvector` searches for the top 5 chunks closest to the query vector.
7. **Prompt Construction**: LangChain injects the 5 chunks and the query into a prompt template.
8. **LLM Generation**: The prompt is sent to Gemini via `google-genai`.
9. **Response**: Gemini's answer is returned to FastAPI.
10. **Frontend Render**: FastAPI sends the JSON response to React, which updates the UI.
