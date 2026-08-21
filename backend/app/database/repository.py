from __future__ import annotations

import json
from typing import Any, Iterable, Sequence

from app.database.connection import get_connection


_COLUMNS = (
    "incident_id, title, description, root_cause, resolution, comments, project, "
    "component, service, severity, environment, incident_type, status, created_at, "
    "updated_at, source, source_url, metadata, embedding"
)


def _register_vector(connection: Any) -> None:
    try:
        from pgvector.psycopg import register_vector
    except ImportError as exc:  # pragma: no cover - dependency is required in deployment
        raise RuntimeError("The pgvector Python dependency is not installed.") from exc
    register_vector(connection)


class IncidentRepository:
    def upsert_batch(self, records: Iterable[dict[str, Any]]) -> int:
        rows = list(records)
        if not rows:
            return 0

        with get_connection() as connection:
            _register_vector(connection)
            with connection.cursor() as cursor:
                for record in rows:
                    values = self._values(record)
                    cursor.execute(
                        f"""
                        INSERT INTO incidents ({_COLUMNS})
                        VALUES ({', '.join(['%s'] * len(values))})
                        ON CONFLICT (incident_id) DO UPDATE SET
                            title = EXCLUDED.title,
                            description = EXCLUDED.description,
                            root_cause = EXCLUDED.root_cause,
                            resolution = EXCLUDED.resolution,
                            comments = EXCLUDED.comments,
                            project = EXCLUDED.project,
                            component = EXCLUDED.component,
                            service = EXCLUDED.service,
                            severity = EXCLUDED.severity,
                            environment = EXCLUDED.environment,
                            incident_type = EXCLUDED.incident_type,
                            status = EXCLUDED.status,
                            created_at = EXCLUDED.created_at,
                            updated_at = EXCLUDED.updated_at,
                            source = EXCLUDED.source,
                            source_url = EXCLUDED.source_url,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding
                        """,
                        values,
                    )
            connection.commit()
        return len(rows)

    def search(self, embedding: Sequence[float], top_k: int = 5) -> list[dict[str, Any]]:
        with get_connection() as connection:
            _register_vector(connection)
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT {_COLUMNS}, 1 - (embedding <=> %s) AS similarity_score
                    FROM incidents
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (list(embedding), list(embedding), top_k),
                )
                rows = cursor.fetchall()
                columns = [item.name for item in cursor.description]

        results = []
        for row in rows:
            item = dict(zip(columns, row))
            metadata = item.pop("metadata", {}) or {}
            item.pop("embedding", None)
            item["similarity_score"] = round(float(item["similarity_score"]), 4)
            item["metadata"] = metadata
            results.append(item)
        return results

    def _values(self, record: dict[str, Any]) -> tuple[Any, ...]:
        metadata = record.get("metadata", {}) or {}
        if not isinstance(metadata, dict):
            metadata = {"value": str(metadata)}
        return (
            record.get("incident_id"),
            record.get("title", ""),
            record.get("description", ""),
            record.get("root_cause"),
            record.get("resolution"),
            record.get("comments"),
            record.get("project"),
            record.get("component"),
            record.get("service"),
            record.get("severity"),
            record.get("environment"),
            record.get("incident_type"),
            record.get("status"),
            record.get("created_at"),
            record.get("updated_at"),
            record.get("source"),
            record.get("source_url"),
            json.dumps(metadata),
            record.get("embedding"),
        )
