from __future__ import annotations

import argparse
import json
from pathlib import Path

import requests

DEFAULT_RECORD = "https://zenodo.org/api/records/15719919"


def select_dataset_archive(files: list[dict]) -> dict:
    candidates = [item for item in files if str(item.get("key", "")).lower().endswith(".zip")]
    if not candidates:
        raise RuntimeError("Zenodo record has no MongoDB ZIP archive.")
    candidates.sort(key=lambda item: (
        "publicjiradataset" not in str(item.get("key", "")).lower(),
        -int(item.get("size") or 0),
    ))
    return candidates[0]


def download_latest(output_dir: Path, record_url: str = DEFAULT_RECORD) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    metadata = requests.get(record_url, timeout=60)
    metadata.raise_for_status()
    record = metadata.json()
    files = record.get("files", [])
    file_info = select_dataset_archive(files)
    target = output_dir / file_info["key"]
    if not target.exists():
        with requests.get(file_info["links"]["self"], stream=True, timeout=120) as response:
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
