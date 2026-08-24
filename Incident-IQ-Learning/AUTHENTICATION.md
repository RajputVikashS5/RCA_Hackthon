# Authentication

*(Note: If authentication is fully implemented, this serves as its documentation. If it is pending, this outlines the standard approach).*

Incident-IQ typically handles authentication using standard JWT (JSON Web Tokens).

## Flow
1. User logs in with credentials via the frontend.
2. Backend validates credentials against the PostgreSQL database.
3. Backend issues an `access_token` (JWT) to the frontend.
4. Frontend stores the token (usually in local storage or secure HTTP-only cookies).
5. Subsequent API requests include the token in the `Authorization: Bearer <token>` header.
6. FastAPI middleware validates the token before processing protected routes.
