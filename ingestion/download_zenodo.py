from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import requests

BACKEND_ROOT = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config import ZENODO_ACCESS_TOKEN, ZENODO_API_URL, ZENODO_RECORD_ID

DEFAULT_RECORD = f"{ZENODO_API_URL.rstrip('/')}/records/{ZENODO_RECORD_ID}"


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    token = (ZENODO_ACCESS_TOKEN or "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _request_get(url: str, *, timeout: float, stream: bool = False):
    kwargs = {"timeout": timeout, "stream": stream}
    headers = _headers()
    if headers:
        kwargs["headers"] = headers
    try:
        return requests.get(url, **kwargs)
    except TypeError:
        kwargs.pop("headers", None)
        return requests.get(url, timeout=timeout, stream=stream)


def _is_bson_archive(name: str) -> bool:
    lower = name.lower()
    return lower.endswith(".bson") or lower.endswith(".bson.gz") or lower.endswith(".bson.tgz")


def _archive_priority(name: str) -> tuple[int, int]:
    lower = name.lower()
    if "issues" in lower and _is_bson_archive(lower):
        return (0, 0)
    if _is_bson_archive(lower) and ("jira" in lower or "issue" in lower):
        return (1, 0)
    if lower.endswith(".zip") and any(marker in lower for marker in ("jira", "publicjira", "issue")):
        return (2, 0)
    return (3, 0)


def select_dataset_archive(files: list[dict]) -> dict:
    candidates = [
        item for item in files
        if (
            _is_bson_archive(str(item.get("key", "")))
            and any(marker in str(item.get("key", "")).lower() for marker in ("jira", "issue"))
        )
        or (
            str(item.get("key", "")).lower().endswith(".zip")
            and any(marker in str(item.get("key", "")).lower() for marker in ("jira", "publicjira", "issue"))
        )
    ]
    if not candidates:
        legacy_archives = [
            item for item in files
            if str(item.get("key", "")).lower().endswith((".zip", ".bson", ".bson.gz", ".bson.tgz"))
        ]
        if len(legacy_archives) == 1:
            # Preserve the historical single-archive workflow. When multiple archives
            # exist, only an explicitly Jira-named archive is accepted.
            candidates = legacy_archives
        else:
            raise RuntimeError("Zenodo record has no explicit Jira MongoDB archive.")
    candidates.sort(key=lambda item: (
        _archive_priority(str(item.get("key", ""))),
        -int(item.get("size") or 0),
    ))
    return candidates[0]


def download_latest(output_dir: Path, record_url: str = DEFAULT_RECORD) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = _request_get(record_url, timeout=60)
    metadata.raise_for_status()
    record = metadata.json()
    files = record.get("files", [])
    file_info = select_dataset_archive(files)
    target = output_dir / file_info["key"]
    if not target.exists():
        with _request_get(file_info["links"]["self"], timeout=120, stream=True) as response:
            response.raise_for_status()
            with target.open("wb") as handle:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        handle.write(chunk)
    (output_dir / "zenodo_record.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    return target


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--record-url", default=DEFAULT_RECORD)
    args = parser.parse_args()
    print(download_latest(args.output_dir, args.record_url))
