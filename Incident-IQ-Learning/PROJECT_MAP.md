# Project Map

This document outlines the high-level directory structure of the Incident-IQ codebase.

```text
RCA_Hackthon/
├── backend/                  # FastAPI Backend Application
│   ├── app/                  # Main application code
│   │   ├── api/              # FastAPI route endpoints
│   │   ├── database/         # Postgres and MongoDB connections/models
│   │   ├── models/           # Pydantic schemas
│   │   ├── services/         # Core business logic (RAG, Embeddings, Zenodo)
│   │   └── main.py           # Application entry point
│   ├── tests/                # Pytest suites
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React (Vite) Frontend Application
│   ├── src/                  
│   │   ├── components/       # Reusable UI components
│   │   ├── pages/            # View-level components
│   │   ├── services/         # API client configurations (TanStack)
│   │   └── store/            # Zustand state management
│   └── package.json          # Node dependencies
└── Incident-IQ-Learning/     # This learning guide
```
