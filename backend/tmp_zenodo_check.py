from __future__ import annotations
import json
import sys
from ingestion.zenodo_client import ZenodoClient, ZenodoClientError
from app.config import ZENODO_RECORD_ID

client = ZenodoClient()
record_id = str(ZENODO_RECORD_ID)
try:
    record = client.get_record(record_id)
    files = client.list_files(record)
    bson_files = client.bson_files(files)
    out = {
        "record_id": str(record.get("id") or record_id),
        "title": (record.get("metadata") or {}).get("title"),
        "files_count": len(files),
        "bson_files_count": len(bson_files),
        "files": files[:10],
        "bson_files": bson_files,
    }
    print(json.dumps({"success": True, "data": out}, indent=2))
    sys.exit(0)
except ZenodoClientError as exc:
    print(json.dumps({"success": False, "error": str(exc)}))
    sys.exit(2)
except Exception as exc:
    print(json.dumps({"success": False, "error": repr(exc)}))
    sys.exit(3)
