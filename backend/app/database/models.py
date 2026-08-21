from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class IncidentDatabaseRecord:
    incident_id: str
    title: str
    description: str
    embedding: list[float]
    root_cause: str | None = None
    resolution: str | None = None
    metadata: dict[str, Any] | None = None
