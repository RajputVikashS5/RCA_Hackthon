"""Authentication boundary for protected API routes."""

from __future__ import annotations

from secrets import compare_digest

from fastapi import Header, HTTPException, status

from app.config import API_AUTH_REQUIRED, API_AUTH_TOKEN


def require_api_auth(authorization: str | None = Header(default=None)) -> None:
    """Require a server-side bearer token outside explicitly configured development."""
    if not API_AUTH_REQUIRED:
        return
    if not API_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="API authentication is enabled but API_AUTH_TOKEN is not configured.",
        )
    scheme, _, token = (authorization or "").partition(" ")
    if scheme.casefold() != "bearer" or not token or not compare_digest(token, API_AUTH_TOKEN):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
