from __future__ import annotations

from typing import Any, Dict, List
import requests

from app.config import ZENODO_API_URL, ZENODO_REQUEST_TIMEOUT


class ZenodoClientError(RuntimeError):
    pass


class ZenodoClient:
    """Lightweight Zenodo metadata client.

    - Only fetches record metadata and lists files.
    - Does NOT download dataset contents.
    """

    def __init__(self, api_url: str = ZENODO_API_URL, timeout: float = ZENODO_REQUEST_TIMEOUT) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout

    def get_record(self, record_id: str) -> Dict[str, Any]:
        url = f"{self.api_url}/{record_id}"
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            payload = resp.json()
        except requests.HTTPError as exc:
            raise ZenodoClientError(f"Zenodo returned HTTP {exc.response.status_code} for record {record_id}.") from exc
        except requests.RequestException as exc:
            raise ZenodoClientError(f"Unable to reach Zenodo: {exc}") from exc
        except ValueError as exc:
            raise ZenodoClientError("Zenodo returned an invalid JSON metadata response.") from exc

        if not isinstance(payload, dict):
            raise ZenodoClientError("Zenodo metadata response was not a JSON object.")
        return payload

    def list_files(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw_files = record.get("files") or []
        files: List[Dict[str, Any]] = []
        SUPPORTED_EXTENSIONS = {".csv", ".json", ".jsonl", ".ndjson", ".xls", ".xlsx", ".gz", ".bz2", ".zip", ".bson"}
        for item in raw_files:
            key = item.get("key")
            if not key:
                continue
            links = item.get("links") or {}
            download_url = links.get("self") or links.get("download")
            # normalize suffix
            name_lower = str(key).lower()
            ext = None
            for candidate in SUPPORTED_EXTENSIONS:
                if name_lower.endswith(candidate):
                    ext = candidate
                    break
            if not download_url or ext is None:
                # skip unsupported or non-downloadable files
                continue
            files.append({
                "name": key,
                "key": key,
                "size": item.get("size"),
                "download_url": download_url,
                "available": True,
            })
        return files

    def bson_files(self, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return files that look like BSON dumps (.bson or .bson.gz).
        """
        candidates: List[Dict[str, Any]] = []
        for f in files:
            name = (f.get("name") or "").lower()
            if name.endswith(".bson") or name.endswith(".bson.gz") or name.endswith(".bson.tgz"):
                candidates.append(f)
        return candidates

