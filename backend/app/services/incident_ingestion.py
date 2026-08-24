from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List, Tuple

import pandas as pd

from app.models.schemas import IncidentRecord


SUPPORTED_EXTENSIONS = {".csv", ".json", ".xls", ".xlsx"}
REQUIRED_FIELDS = ["incident_id", "title", "description", "root_cause", "resolution"]

FIELD_ALIASES = {
    "incident_id": ["incident_id", "incident id", "incident-id", "id"],
    "title": ["title"],
    "description": ["description", "details"],
    "root_cause": ["root_cause", "root cause", "root-cause"],
    "resolution": ["resolution", "fix", "remediation"],
    "component": ["component"],
    "service": ["service"],
    "severity": ["severity"],
    "environment": ["environment"],
    "incident_type": ["incident_type", "incident type", "type"],
    "date": ["date", "incident_date", "incident date"],
    "status": ["status"],
    "tags": ["tags"],
}


@dataclass
class IngestionStats:
    source_files: int = 0
    total_rows: int = 0
    valid_rows: int = 0
    indexed_rows: int = 0
    duplicates_removed: int = 0
    skipped_rows: int = 0


class IncidentIngestionError(ValueError):
    pass


class IncidentIngestionService:
    def load_folder(self, folder_path: str) -> Tuple[List[IncidentRecord], IngestionStats, List[str]]:
        folder = Path(folder_path)

        if not folder.exists():
            raise IncidentIngestionError(f"Incident folder does not exist: {folder_path}")

        records: List[IncidentRecord] = []
        stats = IngestionStats()
        source_files: List[str] = []

        for file_path in sorted(folder.iterdir()):
            if not file_path.is_file() or file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            file_records, file_stats = self.load_file(file_path)
            records.extend(file_records)
            stats.source_files += 1
            stats.total_rows += file_stats.total_rows
            stats.valid_rows += file_stats.valid_rows
            stats.skipped_rows += file_stats.skipped_rows
            source_files.append(file_path.name)

        if not records:
            raise IncidentIngestionError("No valid incident records were found in the uploaded dataset.")

        deduped_records, duplicates_removed = self._deduplicate(records)
        stats.duplicates_removed = duplicates_removed
        stats.indexed_rows = len(deduped_records)

        return deduped_records, stats, source_files

    def load_file(self, file_path: Path) -> Tuple[List[IncidentRecord], IngestionStats]:
        dataframe = self._read_dataframe(file_path)
        normalized = self._normalize_columns(dataframe)

        missing_columns = [field for field in REQUIRED_FIELDS if field not in normalized.columns]
        if missing_columns:
            raise IncidentIngestionError(
                f"File '{file_path.name}' is missing required columns: {', '.join(missing_columns)}"
            )

        records: List[IncidentRecord] = []
        stats = IngestionStats(source_files=1, total_rows=len(normalized))

        for row_index, row in normalized.iterrows():
            cleaned = self._clean_row(row.to_dict())

            if not self._row_has_required_values(cleaned):
                stats.skipped_rows += 1
                continue

            cleaned["source_file"] = file_path.name
            cleaned["row_number"] = int(row_index) + 2
            cleaned["search_text"] = self.build_search_text(cleaned)

            records.append(IncidentRecord.model_validate(cleaned))
            stats.valid_rows += 1

        if not records:
            raise IncidentIngestionError(
                f"File '{file_path.name}' did not contain any valid incident rows after cleaning."
            )

        return records, stats

    def build_search_text(self, record: Dict[str, Any]) -> str:
        parts = [
            f"Incident ID: {record.get('incident_id', '').strip()}",
            f"Title: {record.get('title', '').strip()}",
            "Description:",
            record.get("description", "").strip(),
        ]

        for field in ["component", "service", "severity", "environment", "incident_type", "tags"]:
            if value := record.get(field):
                parts.append(f"{field.replace('_', ' ').title()}: {str(value).strip()}")

        return "\n".join(filter(None, parts))

    def _read_dataframe(self, file_path: Path) -> pd.DataFrame:
        suffix = file_path.suffix.lower()

        try:
            if suffix == ".csv":
                return pd.read_csv(file_path)
            if suffix == ".json":
                return pd.read_json(file_path)
            if suffix in {".xls", ".xlsx"}:
                return pd.read_excel(file_path)
        except Exception as exc:  # pragma: no cover - surfaced as friendly error
            raise IncidentIngestionError(f"Unable to read '{file_path.name}': {exc}") from exc

        raise IncidentIngestionError(f"Unsupported file format: {file_path.suffix}")

    def _normalize_columns(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        renamed = dataframe.copy()
        renamed.columns = [self._normalize_column_name(column) for column in renamed.columns]

        rename_map: Dict[str, str] = {}
        for canonical, aliases in FIELD_ALIASES.items():
            for alias in aliases:
                normalized_alias = self._normalize_column_name(alias)
                if normalized_alias in renamed.columns:
                    rename_map[normalized_alias] = canonical
                    break

        renamed = renamed.rename(columns=rename_map)
        renamed = renamed.loc[:, ~renamed.columns.duplicated()]
        return renamed

    def _normalize_column_name(self, column: Any) -> str:
        normalized = re.sub(r"[^a-z0-9]+", "_", str(column).strip().lower())
        return normalized.strip("_")

    def _clean_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        cleaned: Dict[str, Any] = {}

        for key, value in row.items():
            normalized_key = self._normalize_column_name(key)

            if isinstance(value, (list, tuple, set)):
                cleaned[normalized_key] = ", ".join(self._clean_scalar(item) for item in value if self._clean_scalar(item))
                continue

            if pd.isna(value):
                cleaned[normalized_key] = ""
                continue

            cleaned[normalized_key] = self._clean_scalar(value)

        if cleaned.get("date"):
            cleaned["date"] = self._normalize_date(cleaned["date"])

        return cleaned

    def _clean_scalar(self, value: Any) -> str:
        if value is None:
            return ""

        text = str(value).strip()
        return re.sub(r"\s+", " ", text)

    def _normalize_date(self, value: str) -> str:
        try:
            parsed = pd.to_datetime(value, errors="coerce")
            if pd.isna(parsed):
                return value
            return parsed.date().isoformat()
        except Exception:
            return value

    def _row_has_required_values(self, row: Dict[str, Any]) -> bool:
        for field in REQUIRED_FIELDS:
            if not row.get(field):
                return False
        return True

    def _deduplicate(self, records: List[IncidentRecord]) -> Tuple[List[IncidentRecord], int]:
        seen_ids = set()
        deduped: List[IncidentRecord] = []
        duplicates_removed = 0

        for record in records:
            normalized_id = record.incident_id.strip().lower()
            if normalized_id in seen_ids:
                duplicates_removed += 1
                continue

            seen_ids.add(normalized_id)
            deduped.append(record)

        return deduped, duplicates_removed