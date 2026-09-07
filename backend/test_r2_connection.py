"""Safe live R2 verification using bucket/object metadata only.

This script never calls download_file and never persists object bytes.
"""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.config import (
    R2_ACCESS_KEY_ID,
    R2_BUCKET_NAME,
    R2_DATASET_KEY,
    R2_ENDPOINT_URL,
    R2_REGION,
    R2_SECRET_ACCESS_KEY,
)
from app.services.r2_storage import R2Storage, R2StorageError


def main() -> int:
    required = {
        "R2_ENDPOINT_URL": R2_ENDPOINT_URL,
        "R2_ACCESS_KEY_ID": R2_ACCESS_KEY_ID,
        "R2_SECRET_ACCESS_KEY": R2_SECRET_ACCESS_KEY,
        "R2_BUCKET_NAME": R2_BUCKET_NAME,
        "R2_REGION": R2_REGION,
        "R2_DATASET_KEY": R2_DATASET_KEY,
    }
    missing = [name for name, value in required.items() if not value]
    if missing:
        print(f"R2 TEST STATUS: FAILED\nMissing configuration: {', '.join(missing)}")
        return 2

    storage = R2Storage()
    try:
        if not storage.bucket_accessible():
            print(f"R2 TEST STATUS: FAILED\nBucket access check failed for: {R2_BUCKET_NAME}")
            return 1
        metadata = storage.object_metadata(R2_DATASET_KEY)
        objects = storage.list_objects(prefix="jira/")
        listed = any(item.get("Key") == R2_DATASET_KEY for item in objects)
    except R2StorageError as exc:
        print(f"R2 TEST STATUS: FAILED\nR2 metadata check failed: {exc}")
        return 1

    size = int(metadata.get("ContentLength") or 0)
    print("R2 CONNECTION: SUCCESS")
    print(f"BUCKET: {R2_BUCKET_NAME}")
    print(f"OBJECT: {R2_DATASET_KEY}")
    print(f"CONTENT TYPE: {metadata.get('ContentType', 'unknown')}")
    print(f"OBJECT SIZE: {size} bytes")
    print(f"LAST MODIFIED: {metadata.get('LastModified', 'unknown')}")
    print(f"ETAG: {metadata.get('ETag', 'unknown')}")
    print("R2 OBJECT CHECK: SUCCESS")
    print(f"R2 LIST CHECK: {'SUCCESS' if listed else 'FAILED'}")
    if not listed:
        print("R2 TEST STATUS: FAILED\nExpected object was not returned by the jira/ listing.")
        return 1
    print("FULL DATASET DOWNLOADED: NO")
    print("R2 TEST STATUS: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
