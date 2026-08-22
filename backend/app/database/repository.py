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
        raise RuntimeError(
            "The pgvector Python dependency is not installed."
        ) from exc

    register_vector(connection)


def _vector_type():
    try:
        from pgvector import Vector
        return Vector
    except ImportError:
        from pgvector.psycopg import Vector
        return Vector


class IncidentRepository:

    def delete_source(self, source: str) -> int:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM incidents WHERE source = %s", (source,))
                deleted = cursor.rowcount
            connection.commit()
        return deleted

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

    def search(
        self,
        embedding: Sequence[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:

        with get_connection() as connection:
            _register_vector(connection)

            with connection.cursor() as cursor:

                # Convert the Python embedding list into a pgvector Vector.
                # This prevents PostgreSQL from treating it as real[].
                query_vector = _vector_type()(list(embedding))

                cursor.execute(
                    f"""
                    SELECT
                        {_COLUMNS},
                        1 - (embedding <=> %s) AS similarity_score

                    FROM incidents

                    WHERE embedding IS NOT NULL

                    ORDER BY embedding <=> %s

                    LIMIT %s
                    """,
                    (
                        query_vector,
                        query_vector,
                        top_k,
                    ),
                )

                rows = cursor.fetchall()

                columns = [
                    item.name
                    for item in cursor.description
                ]

        results = []

        for row in rows:
            item = dict(zip(columns, row))

            metadata = item.pop("metadata", {}) or {}

            item.pop("embedding", None)

            item["similarity_score"] = round(
                float(item["similarity_score"]),
                4,
            )

            item["metadata"] = metadata

            results.append(item)

        return results

    def search_hybrid(
        self,
        embedding: Sequence[float],
        query_text: str,
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        with get_connection() as connection:
            _register_vector(connection)
            with connection.cursor() as cursor:
                query_vector = _vector_type()(list(embedding))
                cursor.execute(
                    f"""
                    WITH candidates AS (
                        SELECT
                            {_COLUMNS},
                            1 - (embedding <=> %s) AS semantic_score,
                            ts_rank_cd(
                                to_tsvector('simple', concat_ws(' ', title, description, comments, resolution, project, component, incident_type, severity, environment, status)),
                                websearch_to_tsquery('simple', replace(%s, ' ', ' OR '))
                            ) AS keyword_score
                        FROM incidents
                        WHERE embedding IS NOT NULL
                    )
                    SELECT *,
                        semantic_score * 0.8 +
                        LEAST(keyword_score, 1.0) * 0.2 AS retrieval_score
                    FROM candidates
                    ORDER BY retrieval_score DESC, semantic_score DESC
                    LIMIT %s
                    """,
                    (query_vector, query_text, top_k),
                )
                rows = cursor.fetchall()
                columns = [item.name for item in cursor.description]

        results = []
        for row in rows:
            item = dict(zip(columns, row))
            item.pop("embedding", None)
            item["metadata"] = item.pop("metadata", {}) or {}
            item["similarity_score"] = round(float(item.pop("semantic_score")), 4)
            item["keyword_score"] = round(float(item.pop("keyword_score")), 4)
            item["retrieval_score"] = round(float(item.pop("retrieval_score")), 4)
            results.append(item)
        return results

    def _values(
        self,
        record: dict[str, Any],
    ) -> tuple[Any, ...]:

        metadata = record.get("metadata", {}) or {}

        if not isinstance(metadata, dict):
            metadata = {
                "value": str(metadata)
            }

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