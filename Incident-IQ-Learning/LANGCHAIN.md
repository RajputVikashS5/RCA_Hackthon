# LangChain

LangChain acts as the orchestration framework tying the AI components together.

## Role in Incident-IQ
While you could write raw API calls to Gemini and raw SQL to PGVector, LangChain provides abstractions that make this easier:
- **Chains**: Linking the retrieval step and the generation step together into a cohesive pipeline.
- **Memory**: Managing conversation history (storing past messages so the LLM remembers context).
- **Prompts**: Using prompt templates to consistently format the context and query for the LLM.
