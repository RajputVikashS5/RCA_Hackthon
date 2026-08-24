# Security

Key security considerations for the Incident-IQ project:

1. **Environment Variables**: Sensitive keys (like API keys for Gemini, Database URIs) are stored in `.env` files and never committed to version control (`.gitignore`).
2. **CORS**: FastAPI is configured to only accept requests from the trusted React frontend origins, preventing cross-origin attacks.
3. **Input Validation**: FastAPI uses Pydantic to strictly validate all incoming data, preventing injection attacks or malformed data errors.
4. **Database Security**: Parameterized queries (via Psycopg or an ORM) are used to prevent SQL injection.
