from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterator

from transform_incidents import transform_issues


def read_issues(path: Path) -> Iterator[dict]:
    files = [path] if path.is_file() else sorted(path.rglob("*.json*"))
    for file_path in files:
        if file_path.suffix.lower() not in {".json", ".jsonl"}:
            continue
        with file_path.open(encoding="utf-8") as handle:
            if file_path.suffix.lower() == ".jsonl":
                for line in handle:
                    if line.strip():
                        yield json.loads(line)
                continue
            payload = json.load(handle)
            if isinstance(payload, list):
                yield from payload
            elif isinstance(payload, dict):
                yield payload


def process(path: Path, max_records: int = 50000, project: str | None = None) -> Iterator[dict]:
    count = 0
    seen: set[str] = set()
    for record in transform_issues(read_issues(path)):
        if project and record.get("project", "").lower() != project.lower():
            continue
        if record["incident_id"].lower() in seen:
            continue
        seen.add(record["incident_id"].lower())
        yield record
        count += 1
        if count >= max_records:
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transform local Jira exports into RCA records.")
    parser.add_argument("source", type=Path)
    parser.add_argument("--max-records", type=int, default=50000)
    parser.add_argument("--project")
    args = parser.parse_args()
    for record in process(args.source, args.max_records, args.project):
        print(json.dumps(record, ensure_ascii=False))
