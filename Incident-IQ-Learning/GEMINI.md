# Google Gemini

Incident-IQ uses Google's Gemini as its primary Large Language Model (LLM).

## Integration
- **SDK**: `google-genai`
- **Service**: `backend/app/services/llm.py`
- **Usage**: Gemini is responsible for the "Generation" part of the RAG pipeline. It receives the augmented prompts and generates human-like text responses. It can also be used for summarization, entity extraction, or formatting tasks during the ingestion pipeline.
