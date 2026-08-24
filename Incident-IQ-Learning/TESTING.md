# Testing

## Backend
- **Framework**: `pytest`.
- **Location**: `backend/tests/`.
- **Approach**: FastAPI provides a `TestClient` (based on `httpx`) that allows for simulating HTTP requests against the API endpoints without running a live server. Tests mock external dependencies like the Gemini API or the database to ensure unit tests are fast and reliable.

## Frontend
- **Linting**: `oxlint` is used for extremely fast static code analysis and identifying logical errors or anti-patterns in the TypeScript code.
- **TypeScript**: `tsc` provides strict type-checking during the build process.
