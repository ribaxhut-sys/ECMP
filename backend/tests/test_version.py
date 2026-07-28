"""R6-01: GET /version returns build provenance from settings/env (not hardcoded)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app


def test_version_endpoint_reads_settings(monkeypatch) -> None:
    monkeypatch.setenv("GIT_COMMIT", "abc123deadbeef")
    monkeypatch.setenv("GIT_BRANCH", "release/v1.0.0")
    monkeypatch.setenv("BUILD_TIME", "2026-07-28T03:00:00Z")
    monkeypatch.setenv("GIT_TREE_STATE", "clean")
    monkeypatch.setenv("APP_VERSION", "1.0.0-rc2")
    monkeypatch.setenv("ENVIRONMENT", "development")
    get_settings.cache_clear()

    client = TestClient(create_app())
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "version": "1.0.0-rc2",
        "git_commit": "abc123deadbeef",
        "branch": "release/v1.0.0",
        "build_time": "2026-07-28T03:00:00Z",
        "environment": "development",
        "git_tree_state": "clean",
    }
    get_settings.cache_clear()
