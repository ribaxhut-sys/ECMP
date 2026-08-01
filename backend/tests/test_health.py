"""B2 liveness / readiness probe tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.runtime_state import mark_startup_incomplete
from app.main import create_app


def test_live_returns_200_without_database_check() -> None:
    get_settings.cache_clear()
    with (
        patch(
            "app.api.health.ping_database_async",
            new_callable=AsyncMock,
        ) as ping,
        TestClient(create_app()) as client,
    ):
        response = client.get("/live")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "service" in body
    ping.assert_not_called()
    get_settings.cache_clear()


def test_ready_returns_200_when_dependencies_ok() -> None:
    get_settings.cache_clear()
    with (
        patch(
            "app.api.health.ping_database_async",
            new_callable=AsyncMock,
            return_value=True,
        ),
        TestClient(create_app()) as client,
    ):
        response = client.get("/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ready"
    assert body["checks"]["startup"] == "ok"
    assert body["checks"]["database"] == "ok"
    get_settings.cache_clear()


def test_ready_returns_503_when_database_unavailable() -> None:
    get_settings.cache_clear()
    with (
        patch(
            "app.api.health.ping_database_async",
            new_callable=AsyncMock,
            return_value=False,
        ),
        TestClient(create_app()) as client,
    ):
        live = client.get("/live")
        ready = client.get("/ready")
    assert live.status_code == 200
    assert ready.status_code == 503
    body = ready.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["startup"] == "ok"
    assert body["checks"]["database"] == "fail"
    get_settings.cache_clear()


def test_ready_returns_503_when_startup_incomplete() -> None:
    get_settings.cache_clear()
    with (
        patch(
            "app.api.health.ping_database_async",
            new_callable=AsyncMock,
            return_value=True,
        ) as ping,
        TestClient(create_app()) as client,
    ):
        mark_startup_incomplete()
        response = client.get("/ready")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "not_ready"
    assert body["checks"]["startup"] == "fail"
    assert body["checks"]["database"] == "fail"
    ping.assert_not_called()
    get_settings.cache_clear()


def test_security_headers_present_on_live() -> None:
    get_settings.cache_clear()
    with TestClient(create_app()) as client:
        response = client.get("/live")
    assert response.status_code == 200
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
    assert response.headers.get("X-Frame-Options") == "DENY"
    get_settings.cache_clear()
