from __future__ import annotations

from io import BytesIO, StringIO
import json
from pathlib import PurePosixPath
import threading
import time
from typing import Any

import pandas as pd
import requests

from app.config import (
    ZENODO_API_URL,
    ZENODO_CACHE_TTL,
    ZENODO_RECORD_ID,
    ZENODO_REQUEST_TIMEOUT,
    ZENODO_SAMPLE_SIZE,
)


SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".ndjson", ".xls", ".xlsx"}


class ZenodoServiceError(RuntimeError):
    pass


class ZenodoService:
    _cache: dict[str, tuple[float, Any]] = {}
    _cache_lock = threading.Lock()

    def test_connection(self, record_id: str = ZENODO_RECORD_ID, sample_size: int = ZENODO_SAMPLE_SIZE) -> dict[str, Any]:
        record_id = str(record_id).strip()
        if not record_id.isdigit():
            raise ZenodoServiceError(f"Invalid Zenodo record ID: {record_id}")

        record = self._get_cached(f"record:{record_id}")
        if record is None:
            print(f"[Zenodo] Connecting to record {record_id}")
            record = self._fetch_record(record_id)
            self._set_cached(f"record:{record_id}", record)
            print("[Zenodo] Record found")

        raw_files = record.get("files", [])
        files = self._available_files(record)
        print(f"[Zenodo] Files discovered: {len(files)}")
        response: dict[str, Any] = {
            "success": True,
            "source": "Zenodo",
            "recordId": record_id,
            "recordTitle": record.get("metadata", {}).get("title", "Untitled record"),
            "filesFound": len(files),
            "datasetFile": files[0]["key"] if files else None,
            "connection": "successful",
            "sampleRecords": [],
        }

        if not files:
            if raw_files:
                raise ZenodoServiceError(
                    f"Zenodo record {record_id} has downloadable files, but none use a supported format: "
                    f"{', '.join(str(item.get('key', 'unknown')) for item in raw_files)}"
                )
            raise ZenodoServiceError(
                f"Zenodo record {record_id} is reachable, but it has no publicly downloadable files."
            )

        file_info = files[0]
        print(f"[Zenodo] Dataset file: {file_info['key']}")
        response["sampleRecords"] = self._get_sample(record_id, file_info, sample_size)
        return response

    def _fetch_record(self, record_id: str) -> dict[str, Any]:
        url = f"{ZENODO_API_URL.rstrip('/')}/{record_id}"
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
        return payload

    def _available_files(self, record: dict[str, Any]) -> list[dict[str, Any]]:
        files = []
        for item in record.get("files", []):
            key = str(item.get("key", ""))
            extension = PurePosixPath(key).suffix.lower()
            download_url = item.get("links", {}).get("self") or item.get("links", {}).get("download")
            if key and download_url and extension in SUPPORTED_EXTENSIONS:
                files.append({"key": key, "url": download_url, "size": item.get("size")})
        return files

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
            frame = pd.read_csv(StringIO(content.decode("utf-8-sig")))
            return frame.where(pd.notna(frame), None).to_dict(orient="records")
        if extension in {".xls", ".xlsx"}:
            frame = pd.read_excel(BytesIO(content))
            return frame.where(pd.notna(frame), None).to_dict(orient="records")
        if extension in {".jsonl", ".ndjson"}:
            return [json.loads(line) for line in content.decode("utf-8-sig").splitlines() if line.strip()]
        if extension == ".json":
            payload = json.loads(content.decode("utf-8-sig"))
            if isinstance(payload, list):
                return payload
            if isinstance(payload, dict):
                for key in ("records", "data", "issues", "items"):
                    if isinstance(payload.get(key), list):
                        return payload[key]
                return [payload]
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