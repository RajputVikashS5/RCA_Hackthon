from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
import tempfile
from typing import Iterator

from app.config import R2_OBJECT_KEY
from app.services.r2_storage import R2Storage


@contextmanager
def dataset_file(
    object_key: str = R2_OBJECT_KEY,
    storage: R2Storage | None = None,
) -> Iterator[Path]:
    """Download one R2 object to a seekable temporary file and always remove it."""
    r2 = storage or R2Storage()
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(prefix="rca-r2-", suffix=Path(object_key).suffix, delete=False) as handle:
            temporary_path = Path(handle.name)
        yield r2.download_file(object_key, temporary_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
