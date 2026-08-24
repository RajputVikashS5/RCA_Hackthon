# Error Handling

Incident-IQ implements standard error handling practices across the stack.

## Backend (FastAPI)
- Uses `HTTPException` to raise standard HTTP errors (e.g., 404 Not Found, 500 Internal Error).
- Pydantic automatically handles 422 Unprocessable Entity for bad validation.
- Custom exception handlers can be registered in `main.py` to catch specific service errors and format them consistently.

## Frontend (React)
- TanStack Query automatically catches API errors and exposes `isError` and `error` properties to components.
- Global error boundaries or toast notifications (e.g., via a UI library) are used to display user-friendly error messages when API calls fail.
