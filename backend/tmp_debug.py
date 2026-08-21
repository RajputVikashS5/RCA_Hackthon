from fastapi.testclient import TestClient
from app.main import app
from app.api import zenodo as zenodo_module
from app.services import zenodo_service as service_module
from types import SimpleNamespace

def _record_response():
    return SimpleNamespace(
        raise_for_status=lambda: None,
        json=lambda: {
            "id": 15719919,
            "metadata": {
                "title": "The Public Jira Dataset",
                "description": "An anonymized public Jira dataset v7.",
                "access_right": "open",
            },
            "files": [
                {"key": "events.metadata.json.gz", "size": 10, "links": {"self": "https://metadata"}},
                {"key": "2025-06-23 ThePublicJiraDataset.zip", "size": 5813135238, "links": {"self": "https://archive"}},
            ],
        },
    )

service_module.JIRA_DATA_DIR = 'C:/temp/does_not_exist'
service_module.requests.get = lambda url, timeout: _record_response()
zenodo_module.service._cache.clear()
client = TestClient(app)
resp = client.post('/api/zenodo/inspect')
print(resp.status_code)
print(resp.json())
