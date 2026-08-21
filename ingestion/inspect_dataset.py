from __future__ import annotations

import argparse
import json
from pathlib import Path


def inspect_path(path: Path, sample_size: int = 3) -> dict:
    files = sorted(item for item in path.rglob("*") if item.is_file()) if path.is_dir() else [path]
    result = {"path": str(path), "files": [], "samples": []}
    for file_path in files:
        result["files"].append({"name": str(file_path), "bytes": file_path.stat().st_size})
        if len(result["samples"]) >= sample_size or file_path.suffix.lower() not in {".json", ".jsonl"}:
            continue
        try:
            with file_path.open(encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        result["samples"].append({"file": str(file_path), "keys": sorted(json.loads(line).keys())})
                        break
        except (OSError, json.JSONDecodeError, UnicodeDecodeError):
            continue
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inspect a local Zenodo export without loading it into memory.")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect_path(args.path), indent=2))
