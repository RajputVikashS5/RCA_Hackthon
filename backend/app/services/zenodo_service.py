from __future__ import annotations

from io import BytesIO, StringIO
import json
from pathlib import PurePosixPath
import threading
import time
from typing import Any, cast

import pandas as pd
import requests

from app.config import (
    JIRA_DATA_DIR,
    ZENODO_API_URL,
    ZENODO_CACHE_TTL,
    ZENODO_RECORD_ID,
    ZENODO_REQUEST_TIMEOUT,
    ZENODO_SAMPLE_SIZE,
)


SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".ndjson", ".xls", ".xlsx", ".gz", ".bz2", ".zip", ".bson"}


class ZenodoServiceError(RuntimeError):
    pass


class ZenodoService:
    _cache: dict[str, tuple[float, Any]] = {}
    _cache_lock = threading.Lock()

    def test_connection(self, record_id: str = ZENODO_RECORD_ID, sample_size: int = ZENODO_SAMPLE_SIZE) -> dict[str, Any]:
        record_id = str(record_id).strip()
        if not record_id.isdigit():
            return self._unavailable(record_id, "Invalid Zenodo record ID.")

        # Do not retry a known restricted file on every UI status refresh.
        restricted = self._get_cached(f"restricted:{record_id}")
        if restricted is not None:
            return restricted

        try:
            record = self._get_cached(f"record:{record_id}")
            if record is None:
                print(f"[Zenodo] Connecting to record {record_id}")
                record = self._fetch_record(record_id)
                self._set_cached(f"record:{record_id}", record)
                print("[Zenodo] Record found")
        except ZenodoServiceError as exc:
            # Zenodo is a supplemental source. A failed probe must never make the
            # primary PostgreSQL/pgvector knowledge base unavailable.
            return self._unavailable(record_id, str(exc))

        raw_files = record.get("files", [])
        files = self._available_files(record)
        print(f"[Zenodo] Files discovered: {len(files)}")
        data: dict[str, Any] = {
            "source": "zenodo",
            "recordId": record_id,
            "recordTitle": record.get("metadata", {}).get("title", "Untitled record"),
            "filesFound": len(files),
            "datasetFile": files[0]["key"] if files else None,
            "metadataAvailable": True,
            "filesAvailable": bool(files),
            "sampleRecords": [],
        }

        if not files:
            if raw_files:
                message = (
                    "Zenodo record metadata is accessible, but no supported dataset files are publicly downloadable."
                )
            else:
                message = "Zenodo record metadata is accessible, but dataset files are restricted."
            return self._cache_restricted(record_id, self._response(data, status="restricted", message=message))

        file_info = files[0]
        print(f"[Zenodo] Dataset file: {file_info['key']}")
        try:
            data["sampleRecords"] = self._get_sample(record_id, file_info, sample_size)
        except ZenodoServiceError as exc:
            # A file link can be listed in public metadata but still reject a
            # download. Treat that expected authorization failure as restricted.
            return self._cache_restricted(
                record_id,
                self._response(data, status="restricted", message=str(exc), files_available=False),
            )

        return self._response(data, status="available", message="Zenodo metadata and dataset files are accessible.")

    def _response(
        self,
        data: dict[str, Any],
        *,
        status: str,
        message: str,
        files_available: bool | None = None,
    ) -> dict[str, Any]:
        if files_available is not None:
            data["filesAvailable"] = files_available
        data["status"] = status
        data["message"] = message
        return {"success": True, "data": data}

    def _unavailable(self, record_id: str, message: str) -> dict[str, Any]:
        return self._response(
            {
                "source": "zenodo",
                "recordId": record_id,
                "metadataAvailable": False,
                "filesAvailable": False,
                "sampleRecords": [],
            },
            status="unavailable",
            message=message,
        )

    def _cache_restricted(self, record_id: str, response: dict[str, Any]) -> dict[str, Any]:
        self._set_cached(f"restricted:{record_id}", response)
        return response

    def get_record_info(self, record_id: str = ZENODO_RECORD_ID) -> dict[str, Any]:
        return self.get_status(record_id)

    def get_status(self, record_id: str = ZENODO_RECORD_ID) -> dict[str, Any]:
        record_id = str(record_id).strip()
        if not record_id.isdigit():
            raise ZenodoServiceError(f"Invalid Zenodo record ID: {record_id}")

        record = self._get_record(record_id)
        metadata = cast(dict[str, Any], record.get("metadata", {}) or {})
        files = self._record_files(record)
        archive = self._dataset_archive(files)
        title = str(metadata.get("title") or "Untitled record")
        description = str(metadata.get("description") or "")
        return {
            "connected": True,
            "metadata_access": "connected",
            "dataset_access": "available" if archive else "unavailable",
            "inspection": "not_started",
            "ingestion": "not_started",
            "record_id": record_id,
            "title": title,
            "version": metadata.get("version") or ("apache-jira" if record_id == "7740379" or "apache jira" in f"{title} {description}".lower() else None),
            "access_status": metadata.get("access_right") or record.get("access_right"),
            "anonymized": self._is_anonymized(title, description),
            "files": files,
            "dataset_archive": archive,
            "record_url": f"https://zenodo.org/records/{record_id}",
        }

    def inspect_dataset(self, record_id: str = ZENODO_RECORD_ID, sample_size: int = 5) -> dict[str, Any]:
        status = self.get_status(record_id)
        archive = cast(dict[str, Any], status.get("dataset_archive") or {})
        if not archive:
            raise ZenodoServiceError("The Zenodo record does not expose a MongoDB archive.")
        from pathlib import Path

        from ingestion.inspect_dataset import inspect_path

        local_archive = Path(JIRA_DATA_DIR) / archive["name"]
        if not local_archive.exists():
            raise ZenodoServiceError(
                f"Dataset archive is available at Zenodo but is not downloaded locally: {local_archive}. "
                "Run the explicit ingestion download command before inspection."
            )
        result = inspect_path(local_archive, sample_size=max(1, min(sample_size, 20)))
        result["archive_type"] = "mongodb"
        return result

    def _get_record(self, record_id: str) -> dict[str, Any]:
        cache_key = f"record:{record_id}"
        record = self._get_cached(cache_key)
        if record is None:
            record = self._fetch_record(record_id)
            self._set_cached(cache_key, record)
        return record

    def _record_files(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        raw_files = cast(list[dict[str, Any]], record.get("files", []) or [])
        for item in raw_files:
            key = str(item.get("key") or "")
            links = cast(dict[str, Any], item.get("links", {}) or {})
            if not key:
                continue
            # Normalize both 'download_url' and 'url' keys for downstream consumers
            download_url = links.get("self") or links.get("download")
            files.append(
                {
                    "name": key,
                    "key": key,
                    "size": item.get("size"),
                    "download_url": download_url,
                    "url": download_url,
                    "archive_type": self._archive_type(key),
                    "is_dataset_archive": False,
                }
            )
        archive = self._dataset_archive(files)
        if archive:
            for item in files:
                item["is_dataset_archive"] = item["name"] == archive["name"]
        return files

    def _dataset_archive(self, files: list[dict[str, Any]]) -> dict[str, Any] | None:
        candidates = [
            item for item in files
            if self._is_explicit_jira_archive(str(item.get("name", "")))
        ]
        if not candidates:
            return None
        candidates.sort(key=lambda item: (
            "publicjiradataset" not in item["name"].lower(),
            "jira" not in item["name"].lower(),
            -int(item.get("size") or 0),
        ))
        selected = candidates[0]
        return {
            "name": selected["name"],
            "size": selected.get("size"),
            "download_url": selected.get("download_url"),
            "available": bool(selected.get("download_url")),
            "archive_type": "mongodb",
        }

    @staticmethod
    def _is_explicit_jira_archive(name: str) -> bool:
        lower = name.lower()
        if lower.endswith((".bson", ".bson.gz", ".bson.tgz")):
            return "issue" in lower or "jira" in lower
        return lower.endswith(".zip") and any(
            marker in lower for marker in ("jira", "publicjira", "issue")
        )

    @staticmethod
    def _is_anonymized(title: str, description: str) -> bool | None:
        if "anonym" in f"{title} {description}".lower():
            return True
        return None

    def _fetch_record(self, record_id: str) -> dict[str, Any]:
        api_url = ZENODO_API_URL.rstrip("/")
        record_path = "" if api_url.endswith("/records") else "/records"
        url = f"{api_url}{record_path}/{record_id}"
        try:
            result = requests.get(url, timeout=ZENODO_REQUEST_TIMEOUT)
            result.raise_for_status()
            payload = result.json()
        except requests.HTTPError as exc:
            raise ZenodoServiceError(f"Zenodo returned HTTP {exc.response.status_code} for record {record_id}.") from exc
        except requests.RequestException as exc:
            raise ZenodoServiceError(f"Unable to reach Zenodo: {exc}") from exc
        except ValueError as exc:
            raise ZenodoServiceError("Zenodo returned an invalid JSON metadata response.") from exc

        if not isinstance(payload, dict):
            raise ZenodoServiceError("Zenodo metadata response was not a JSON object.")
        return cast(dict[str, Any], payload)

    def _available_files(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        files: list[dict[str, Any]] = []
        raw_files = cast(list[dict[str, Any]], record.get("files", []) or [])
        for item in raw_files:
            key = str(item.get("key", ""))
            extension = PurePosixPath(key).suffix.lower()
            links = cast(dict[str, Any], item.get("links", {}) or {})
            download_url = links.get("self") or links.get("download")
            if key and download_url and (extension in SUPPORTED_EXTENSIONS or self._archive_type(key) in {"zip", "gz", "bson"}):
                files.append({"key": key, "url": download_url, "size": item.get("size")})
        return files

    def _archive_type(self, filename: str) -> str | None:
        file_name = str(filename).lower()
        if file_name.endswith(".zip"):
            return "zip"
        if file_name.endswith(".gz"):
            return "gz"
        if file_name.endswith(".bson"):
            return "bson"
        if file_name.endswith(".json") or file_name.endswith(".jsonl") or file_name.endswith(".ndjson"):
            return "json"
        if file_name.endswith(".csv"):
            return "csv"
        if file_name.endswith(".xls") or file_name.endswith(".xlsx"):
            return "excel"
        return None

    def _get_sample(self, record_id: str, file_info: dict[str, Any], sample_size: int) -> list[dict[str, Any]]:
        cache_key = f"sample:{record_id}:{file_info['key']}:{sample_size}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        try:
            result = requests.get(file_info["url"], timeout=ZENODO_REQUEST_TIMEOUT)
            result.raise_for_status()
            content = result.content
        except requests.HTTPError as exc:
            raise ZenodoServiceError(f"Dataset download returned HTTP {exc.response.status_code}.") from exc
        except requests.RequestException as exc:
            raise ZenodoServiceError(f"Unable to download dataset file: {exc}") from exc

        try:
            records = self._parse_file(file_info["key"], content)
        except (ValueError, TypeError, OSError) as exc:
            raise ZenodoServiceError(f"Unable to parse dataset file '{file_info['key']}': {exc}") from exc

        sample = records[: max(0, sample_size)]
        self._set_cached(cache_key, sample)
        print("[Zenodo] Download successful")
        print("[Zenodo] Dataset parsed successfully")
        print("[Zenodo] Cache created")
        return sample

    def _parse_file(self, filename: str, content: bytes) -> list[dict[str, Any]]:
        extension = PurePosixPath(filename).suffix.lower()
        if extension == ".csv":
            frame: Any = getattr(pd, "read_csv")(StringIO(content.decode("utf-8-sig")))
            notna: Any = getattr(pd, "notna")(frame)
            return cast(list[dict[str, Any]], frame.where(notna, None).to_dict(orient="records"))
        if extension in {".xls", ".xlsx"}:
            frame: Any = getattr(pd, "read_excel")(BytesIO(content))
            notna: Any = getattr(pd, "notna")(frame)
            return cast(list[dict[str, Any]], frame.where(notna, None).to_dict(orient="records"))
        if extension in {".jsonl", ".ndjson"}:
            return [json.loads(line) for line in content.decode("utf-8-sig").splitlines() if line.strip()]
        if extension == ".json":
            payload: Any = json.loads(content.decode("utf-8-sig"))
            if isinstance(payload, list):
                return cast(list[dict[str, Any]], payload)
            if isinstance(payload, dict):
                payload_dict = cast(dict[str, Any], payload)
                for key in ("records", "data", "issues", "items"):
                    if isinstance(payload_dict.get(key), list):
                        return cast(list[dict[str, Any]], payload_dict[key])
                return [payload_dict]
            raise ValueError("JSON root must be an object or array")
        raise ValueError(f"unsupported file format: {extension or 'unknown'}")

    def _get_cached(self, key: str) -> Any | None:
        with self._cache_lock:
            cached = self._cache.get(key)
            if cached is None:
                return None
            created_at, value = cached
            if time.monotonic() - created_at >= ZENODO_CACHE_TTL:
                self._cache.pop(key, None)
                return None
            return value

    def _set_cached(self, key: str, value: Any) -> None:
        with self._cache_lock:
            self._cache[key] = (time.monotonic(), value)
