from __future__ import annotations
import json, sys, os
sys.path.insert(0, r'E:\Projects\RAG\backend')
sys.path.insert(0, r'E:\Projects\RAG')
from ingestion.zenodo_client import ZenodoClient, ZenodoClientError
from ingestion.prepare_manifest import prepare_manifest
import app.config as app_config

record_id = '7740379'
# Use a repo-local JIRA_DATA_DIR for safety
safe_dir = r'E:\Projects\RAG\tmp_jira_data'
app_config.JIRA_DATA_DIR = safe_dir
os.makedirs(safe_dir, exist_ok=True)

client = ZenodoClient()
try:
    record = client.get_record(record_id)
    files = client.list_files(record)
    bson_files = client.bson_files(files)
    probe = {
        'success': True,
        'record_id': str(record.get('id') or record_id),
        'title': (record.get('metadata') or {}).get('title'),
        'files_count': len(files),
        'bson_files_count': len(bson_files),
        'files': files,
        'bson_files': bson_files,
    }
    print(json.dumps({'probe': probe}, indent=2))
    # Create manifest (metadata-only)
    result = prepare_manifest(record_id, only_bson=False)
    manifest_path = result.get('manifest_path')
    print('\nManifest written to:', manifest_path)
    with open(manifest_path, 'r', encoding='utf-8') as fh:
        manifest = json.load(fh)
    print(json.dumps({'manifest': manifest}, indent=2))
except ZenodoClientError as exc:
    print(json.dumps({'success': False, 'error': str(exc)}))
    sys.exit(2)
except Exception as exc:
    print(json.dumps({'success': False, 'error': repr(exc)}))
    sys.exit(3)
