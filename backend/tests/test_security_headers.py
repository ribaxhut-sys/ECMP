"""RC1 security middleware smoke tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app

pytestmark = pytest.mark.security


def test_security_headers_present() -> None:
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        response = client.get("/live")
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("Referrer-Policy") == "no-referrer"
    assert "default-src 'none'" in (response.headers.get("Content-Security-Policy") or "")
    get_settings.cache_clear()


def test_root_exposes_version() -> None:
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert body["version"] == "1.0.0"
    assert body["live"] == "/live"
    assert body["ready"] == "/ready"
    get_settings.cache_clear()
