from __future__ import annotations

import json
from typing import Any
from uuid import UUID, uuid4

from app.database.connection import get_connection


class AnalysisRepository:
    """Persistent RCA-result history stored beside the existing incident corpus."""

    def create(self, request: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
        analysis_id = uuid4()
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rca_analyses
                      (analysis_id, description, component, severity, environment, incident_type, result)
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb)
                    RETURNING analysis_id, description, component, severity, environment, incident_type, result, created_at
                    """,
                    (analysis_id, request["description"], request.get("component"), request.get("severity"), request.get("environment"), request.get("incident_type"), json.dumps(result)),
                )
                row = cursor.fetchone()
                columns = [item.name for item in cursor.description]
            connection.commit()
        return self._record(dict(zip(columns, row)))

    def list(self, limit: int = 50) -> list[dict[str, Any]]:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT analysis_id, description, component, severity, environment, incident_type, result, created_at FROM rca_analyses ORDER BY created_at DESC LIMIT %s",
                    (limit,),
                )
                rows = cursor.fetchall()
                columns = [item.name for item in cursor.description]
        return [self._record(dict(zip(columns, row))) for row in rows]

    def get(self, analysis_id: UUID) -> dict[str, Any] | None:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT analysis_id, description, component, severity, environment, incident_type, result, created_at FROM rca_analyses WHERE analysis_id = %s",
                    (analysis_id,),
                )
                row = cursor.fetchone()
                columns = [item.name for item in cursor.description] if row else []
        return self._record(dict(zip(columns, row))) if row else None

    def delete(self, analysis_id: UUID) -> bool:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM rca_analyses WHERE analysis_id = %s", (analysis_id,))
                deleted = cursor.rowcount > 0
            connection.commit()
        return deleted

    @staticmethod
    def _record(row: dict[str, Any]) -> dict[str, Any]:
        result = row.pop("result")
        if isinstance(result, str):
            result = json.loads(result)
        return {"id": str(row.pop("analysis_id")), "created_at": row.pop("created_at"), "input": row, "result": result}
