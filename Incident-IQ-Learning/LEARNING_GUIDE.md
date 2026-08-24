# Learning Guide (Onboarding)

Welcome to Incident-IQ! If you are a new developer, follow this path to get up to speed:

1. **Read `PROJECT_MAP.md`**: Understand where things are located.
2. **Setup Local Environment**: 
   - Install Python dependencies (`pip install -r backend/requirements.txt`).
   - Install Node dependencies (`npm install` in `frontend/`).
   - Copy `.env.example` to `.env` and fill in your keys (Gemini API key, DB connections).
3. **Run the App**: Start Uvicorn for the backend and Vite for the frontend.
4. **Explore the Code**:
   - Trace the `backend/app/main.py` file to see how routes are registered.
   - Look at `frontend/src/App.tsx` (or main router) to see the entry points.
   - Deep dive into `backend/app/services/rag_pipeline.py` as it contains the core AI logic.
5. **Read Specifics**: Use the rest of the markdown files in this folder as a reference when you encounter a new concept (like `pgvector` or `TanStack`).
