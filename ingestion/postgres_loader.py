from __future__ import annotations

from pathlib import Path
import sys
from typing import Any, Iterable

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.repository import IncidentRepository


def upsert_batch(records: Iterable[dict[str, Any]], repository: IncidentRepository | None = None) -> int:
    repo = repository or IncidentRepository()
    return repo.upsert_batch(records)
