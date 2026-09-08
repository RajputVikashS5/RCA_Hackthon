from __future__ import annotations

from pathlib import PurePosixPath
from typing import Any

from app.config import R2_MANIFEST_KEY, R2_OBJECT_KEY
from app.services.r2_storage import R2Storage, R2StorageError


class DatasetService:
    def __init__(self, storage: R2Storage | None = None) -> None:
        self.storage = storage or R2Storage()

    def files(self) -> list[dict[str, Any]]:
        prefix = str(PurePosixPath(R2_OBJECT_KEY).parent)
        return self.storage.list_objects(prefix=f"{prefix}/" if prefix != "." else "")

    def metadata(self) -> dict[str, Any]:
        manifest: dict[str, Any] | None = None
        if self.storage.object_exists(R2_MANIFEST_KEY):
            body = self.storage.get_object(R2_MANIFEST_KEY).get("Body")
            if body is not None:
                import json
                manifest = json.loads(body.read())
        objects = self.files()
        total_size = sum(int(item.get("Size") or 0) for item in objects)
        return {
            **(manifest or {"dataset_name": "Apache Jira", "dataset_version": None, "source": "unknown"}),
            "storage": "cloudflare-r2",
            "status": "available" if objects else "empty",
            "object_key": R2_OBJECT_KEY,
            "files": manifest.get("files", objects) if manifest else objects,
            "total_size_bytes": total_size,
        }

    def status(self) -> dict[str, Any]:
        try:
            accessible = self.storage.bucket_accessible()
            exists = self.storage.object_exists(R2_OBJECT_KEY) if accessible else False
            return {
                "configured": self.storage.configured,
                "bucket_accessible": accessible,
                "dataset_available": exists,
                "status": "available" if exists else "not_available",
            }
        except R2StorageError as exc:
            return {"configured": self.storage.configured, "bucket_accessible": False, "dataset_available": False, "status": "unavailable", "message": str(exc)}
