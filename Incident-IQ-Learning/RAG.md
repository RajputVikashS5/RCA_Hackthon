# RAG (Retrieval-Augmented Generation)

RAG is the core AI pattern used in Incident-IQ to provide accurate answers based on custom documents.

## The Pipeline (`rag_pipeline.py`)
1. **Retrieve**: When a user asks a question, the system queries the `pgvector` database to find the top-K most relevant document chunks based on vector similarity.
2. **Augment**: The system constructs a prompt that includes the original user question AND the text from the retrieved chunks as "context".
3. **Generate**: This augmented prompt is sent to the Gemini LLM. Gemini uses the provided context to generate a factual answer, reducing hallucinations and grounding the response in your specific data.
