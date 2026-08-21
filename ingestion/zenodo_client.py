from __future__ import annotations

from pathlib import Path
from typing import Any

import requests

from ingestion.download_zenodo import download_latest, select_dataset_archive


class ZenodoClient:
    def __init__(self, record_url: str = "https://zenodo.org/api/records/15719919", timeout: float = 60):
        self.record_url = record_url
        self.timeout = timeout

    def metadata(self) -> dict[str, Any]:
        response = requests.get(self.record_url, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise RuntimeError("Zenodo metadata response was not an object.")
        return payload

    def dataset_archive(self) -> dict[str, Any]:
        return select_dataset_archive(self.metadata().get("files", []))

    def download(self, output_dir: Path) -> Path:
        return download_latest(output_dir, self.record_url)
