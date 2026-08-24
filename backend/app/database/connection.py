from __future__ import annotations

from contextlib import contextmanager
from typing import Any, Iterator

from app.config import EMBEDDING_DIMENSION, get_database_url

try:
    from psycopg_pool import ConnectionPool
except ImportError:  # pragma: no cover - dependency is installed in deployment
    ConnectionPool = None


_pool = None


def _database_url() -> str | None:
    url = get_database_url()
    if url == "postgresql://username:password@hostname:5432/database":
        return None
    return url


def _get_pool():
    global _pool
    database_url = _database_url()

    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")
    if ConnectionPool is None:
        raise RuntimeError("The psycopg connection pool dependency is not installed.")
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=database_url,
            min_size=1,
            max_size=10,
            open=False,
            kwargs={"autocommit": False},
        )
        _pool.open(wait=True)
    return _pool


@contextmanager
def get_connection() -> Iterator[Any]:
    pool = _get_pool()
    with pool.connection() as connection:
        yield connection


def initialize_database() -> None:
    """Create the pgvector extension, schema, and vector index once per setup run."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS incidents (
                    id BIGSERIAL PRIMARY KEY,
                    incident_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    root_cause TEXT,
                    resolution TEXT,
                    comments TEXT,
                    project TEXT,
                    component TEXT,
                    service TEXT,
                    severity TEXT,
                    environment TEXT,
                    incident_type TEXT,
                    status TEXT,
                    created_at TIMESTAMPTZ,
                    updated_at TIMESTAMPTZ,
                    source TEXT,
                    source_url TEXT,
                    metadata JSONB NOT NULL DEFAULT '{{}}'::jsonb,
                    embedding VECTOR({EMBEDDING_DIMENSION}) NOT NULL
                )
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rca_analyses (
                    analysis_id UUID PRIMARY KEY,
                    description TEXT NOT NULL,
                    component TEXT,
                    severity TEXT,
                    environment TEXT,
                    incident_type TEXT,
                    result JSONB NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS rca_analyses_created_at_idx ON rca_analyses (created_at DESC)"
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS incidents_embedding_hnsw_idx
                ON incidents USING hnsw (embedding vector_cosine_ops)
                """
            )
        connection.commit()


def get_database_status() -> dict[str, Any]:
    status: dict[str, Any] = {
        "database": "Unavailable",
        "vector_extension": "Unavailable",
        "incident_records": 0,
        "embedding_dimension": EMBEDDING_DIMENSION,
        "vector_search": "Unavailable",
    }

    if not _database_url():
        status["detail"] = "Database connection is not configured."
        return status

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                status["database"] = "Connected"
                cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector')")
                if cursor.fetchone()[0]:
                    status["vector_extension"] = "Available"
                cursor.execute("SELECT COUNT(*) FROM incidents")
                status["incident_records"] = cursor.fetchone()[0]
                status["vector_search"] = "Available"
    except Exception:
        status["detail"] = "Database connection or schema is unavailable."

    return status


def close_database() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def run_connection_healthcheck() -> int:
    """Run a lightweight database connectivity check for local troubleshooting."""
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()[0]
        print(f"Database connectivity check passed (SELECT {result}).")
        return 0
    except Exception as exc:
        print(f"Database connectivity check failed: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(run_connection_healthcheck())
