from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_FIELDS = {"dataset_name", "dataset_version", "source", "storage", "files"}


def calculate_sha256(path: str | Path, chunk_size: int = 8 * 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest(
    path: str | Path,
    *,
    object_key: str,
    dataset_name: str = "Apache Jira",
    dataset_version: str = "1.0",
    source: str = "local",
    checksum: str | None = None,
) -> dict[str, Any]:
    file_path = Path(path)
    return {
        "dataset_name": dataset_name,
        "dataset_version": dataset_version,
        "source": source,
        "storage": "cloudflare-r2",
        "files": [{
            "name": file_path.name,
            "object_key": object_key,
            "file_name": file_path.name,
            "file_size": file_path.stat().st_size,
            "size_bytes": file_path.stat().st_size,
            "sha256": calculate_sha256(file_path) if checksum is None else checksum,
            "uploaded_at": datetime.now(timezone.utc).isoformat(),
        }],
    }


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    missing = REQUIRED_FIELDS - set(manifest)
    if missing:
        raise ValueError(f"Dataset manifest is missing fields: {', '.join(sorted(missing))}")
    if not isinstance(manifest["files"], list):
        raise ValueError("Dataset manifest files must be a list.")
    return manifest


def write_manifest(manifest: dict[str, Any], path: str | Path) -> Path:
    validate_manifest(manifest)
    output = Path(path)
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return output
