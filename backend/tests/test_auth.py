from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.api import auth


def test_api_auth_accepts_only_the_configured_bearer_token(monkeypatch):
    monkeypatch.setattr(auth, "API_AUTH_REQUIRED", True)
    monkeypatch.setattr(auth, "API_AUTH_TOKEN", "test-token")
    auth.require_api_auth("Bearer test-token")
    with pytest.raises(HTTPException) as error:
        auth.require_api_auth("Bearer wrong-token")
    assert error.value.status_code == 401
