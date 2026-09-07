from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from app.config import (
    R2_ACCESS_KEY_ID,
    R2_BUCKET_NAME,
    R2_ENDPOINT_URL,
    R2_MULTIPART_CHUNKSIZE_MB,
    R2_MULTIPART_THRESHOLD_MB,
    R2_REGION,
    R2_SECRET_ACCESS_KEY,
)


class R2StorageError(RuntimeError):
    """A safe, application-level error for Cloudflare R2 operations."""


class R2Storage:
    def __init__(self, client: Any | None = None) -> None:
        self.bucket = R2_BUCKET_NAME
        self._client = client
        if client is None and self.is_configured():
            try:
                import boto3
                from boto3.s3.transfer import TransferConfig
            except ImportError as exc:  # pragma: no cover - dependency is deployment-provided
                raise R2StorageError("The boto3 dependency is not installed.") from exc
            self._client = boto3.client(
                "s3",
                endpoint_url=R2_ENDPOINT_URL,
                aws_access_key_id=R2_ACCESS_KEY_ID,
                aws_secret_access_key=R2_SECRET_ACCESS_KEY,
                region_name=R2_REGION,
            )
            self.transfer_config = TransferConfig(
                multipart_threshold=R2_MULTIPART_THRESHOLD_MB * 1024 * 1024,
                multipart_chunksize=R2_MULTIPART_CHUNKSIZE_MB * 1024 * 1024,
            )
        else:
            self.transfer_config = None

    @staticmethod
    def is_configured() -> bool:
        return bool(R2_ENDPOINT_URL and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY and R2_BUCKET_NAME)

    @property
    def configured(self) -> bool:
        return self._client is not None and bool(self.bucket)

    def _require_client(self) -> Any:
        if self._client is None:
            raise R2StorageError(
                "Cloudflare R2 is not configured. Set R2_ENDPOINT_URL, R2_ACCESS_KEY_ID, "
                "R2_SECRET_ACCESS_KEY, and R2_BUCKET_NAME."
            )
        return self._client

    def upload_file(self, file_path: str | Path, object_key: str, callback: Callable[[int], None] | None = None) -> None:
        client = self._require_client()
        path = Path(file_path)
        if not path.is_file():
            raise R2StorageError(f"Dataset file does not exist: {path}")
        try:
            kwargs: dict[str, Any] = {"Config": self.transfer_config} if self.transfer_config else {}
            if callback:
                kwargs["Callback"] = callback
            client.upload_file(str(path), self.bucket, object_key, **kwargs)
        except Exception as exc:
            raise R2StorageError(f"Unable to upload R2 object '{object_key}': {type(exc).__name__}.") from exc

    def download_file(self, object_key: str, destination: str | Path) -> Path:
        client = self._require_client()
        path = Path(destination)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            client.download_file(self.bucket, object_key, str(path))
        except Exception as exc:
            raise R2StorageError(f"Unable to download R2 object '{object_key}': {type(exc).__name__}.") from exc
        return path

    def object_exists(self, object_key: str) -> bool:
        client = self._require_client()
        try:
            client.head_object(Bucket=self.bucket, Key=object_key)
            return True
        except Exception as exc:
            response = getattr(exc, "response", {}) or {}
            code = str(response.get("Error", {}).get("Code", ""))
            if code in {"404", "NoSuchKey", "NotFound"}:
                return False
            raise R2StorageError(f"Unable to check R2 object '{object_key}': {type(exc).__name__}.") from exc

    def object_metadata(self, object_key: str) -> dict[str, Any]:
        try:
            return self._require_client().head_object(Bucket=self.bucket, Key=object_key)
        except Exception as exc:
            raise R2StorageError(
                f"Unable to read metadata for R2 object '{object_key}': {type(exc).__name__}."
            ) from exc

    def get_object(self, object_key: str) -> dict[str, Any]:
        try:
            return self._require_client().get_object(Bucket=self.bucket, Key=object_key)
        except Exception as exc:
            raise R2StorageError(f"Unable to read R2 object '{object_key}': {type(exc).__name__}.") from exc

    def list_objects(self, prefix: str = "") -> list[dict[str, Any]]:
        client = self._require_client()
        objects: list[dict[str, Any]] = []
        try:
            paginator = client.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
                objects.extend(page.get("Contents", []))
        except Exception as exc:
            raise R2StorageError(f"Unable to list R2 objects: {type(exc).__name__}.") from exc
        return objects

    def delete_object(self, object_key: str) -> None:
        try:
            self._require_client().delete_object(Bucket=self.bucket, Key=object_key)
        except Exception as exc:
            raise R2StorageError(f"Unable to delete R2 object '{object_key}': {type(exc).__name__}.") from exc

    def bucket_accessible(self) -> bool:
        try:
            self._require_client().head_bucket(Bucket=self.bucket)
            return True
        except Exception:
            return False
