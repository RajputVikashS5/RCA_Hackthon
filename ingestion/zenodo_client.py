from __future__ import annotations

from typing import Any, Dict, List
import requests

from app.config import ZENODO_ACCESS_TOKEN, ZENODO_API_URL, ZENODO_REQUEST_TIMEOUT


class ZenodoClientError(RuntimeError):
    pass


class ZenodoClient:
    """Lightweight Zenodo metadata client.

    - Fetches record metadata and lists files.
    - Uses the bearer token only if configured.
    - Does NOT download the full archive unless explicitly invoked elsewhere.
    """

    def __init__(self, api_url: str = ZENODO_API_URL, timeout: float = ZENODO_REQUEST_TIMEOUT, access_token: str | None = None) -> None:
        self.api_url = api_url.rstrip("/")
        self.timeout = timeout
        self.access_token = (access_token if access_token is not None else ZENODO_ACCESS_TOKEN) or ""

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return headers

    def _raise_for_status(self, response: requests.Response, record_id: str) -> None:
        status_code = getattr(response, "status_code", 200)
        if status_code == 401:
            raise ZenodoClientError(f"Zenodo authentication failed for record {record_id}. Check ZENODO_ACCESS_TOKEN.")
        if status_code == 403:
            raise ZenodoClientError(f"Zenodo access is forbidden for record {record_id}.")
        if status_code == 404:
            raise ZenodoClientError(f"Zenodo record {record_id} was not found.")
        if status_code == 429:
            raise ZenodoClientError(f"Zenodo rate limit exceeded for record {record_id}.")
        if hasattr(response, "raise_for_status"):
            response.raise_for_status()

    def get_record(self, record_id: str) -> Dict[str, Any]:
        record_path = "" if self.api_url.endswith("/records") else "/records"
        url = f"{self.api_url}{record_path}/{record_id}"
        request_kwargs: Dict[str, Any] = {"timeout": self.timeout}
        if self.access_token:
            request_kwargs["headers"] = self._headers()
        try:
            try:
                resp = requests.get(url, **request_kwargs)
            except TypeError:
                # Support older or mocked request stubs that do not accept keyword headers.
                resp = requests.get(url, timeout=self.timeout)
            self._raise_for_status(resp, record_id)
            payload = resp.json()
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

    def supports_record_level_issue_access(self, files: List[Dict[str, Any]]) -> bool:
        """Return True only when a real issue feed exists as structured JSON/text, not metadata or BSON archives."""
        for f in files:
            name = (f.get("name") or f.get("key") or "").lower()
            if "issues" not in name:
                continue
            if "metadata" in name:
                continue
            if name.endswith(".bson") or name.endswith(".bson.gz") or name.endswith(".bson.tgz"):
                continue
            if name.endswith(".json") or name.endswith(".jsonl") or name.endswith(".json.gz") or name.endswith(".jsonl.gz"):
                return True
        return False

