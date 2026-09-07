from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "backend"
for path in (PROJECT_ROOT, BACKEND_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from app.services.r2_storage import R2Storage, R2StorageError
from ingestion.dataset_manifest import build_manifest, write_manifest
from app.config import R2_MANIFEST_KEY


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upload a local Jira dataset to Cloudflare R2.")
    parser.add_argument("--file", required=True, type=Path)
    parser.add_argument("--key", required=True, help="R2 object key, for example raw/jira-dataset.zip")
    parser.add_argument("--skip-sha256", action="store_true")
    args = parser.parse_args(argv)

    if not args.file.is_file():
        parser.error(f"local dataset file does not exist: {args.file}")
    try:
        checksum = "" if args.skip_sha256 else None
        manifest = build_manifest(args.file, object_key=args.key, source="Zenodo", checksum=checksum)
        storage = R2Storage()
        storage.upload_file(args.file, args.key)
        if not storage.object_exists(args.key):
            raise R2StorageError(f"R2 object '{args.key}' was not found after upload.")
        manifest_path = args.file.with_name(f"{args.file.name}.manifest.json")
        write_manifest(manifest, manifest_path)
        storage.upload_file(manifest_path, R2_MANIFEST_KEY)
        print(f"Uploaded: {args.key}")
        print(f"Size: {args.file.stat().st_size} bytes")
        if not args.skip_sha256:
            print(f"SHA256: {manifest['files'][0]['sha256']}")
        print(f"Manifest: {R2_MANIFEST_KEY}")
        return 0
    except R2StorageError as exc:
        print(f"R2 upload failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
