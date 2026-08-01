"""Small platform coverage boosts (TASK-PLATFORM-CI-COV-001)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from sqlalchemy.exc import SQLAlchemyError

from app.api import health as health_mod
from app.modules.queue.api import schemas as queue_schemas


def test_queue_api_schemas_exports() -> None:
    assert queue_schemas.CreateQueueRequest is not None
    assert "CreateTicketRequest" in queue_schemas.__all__


def test_legacy_health_db_exception_paths() -> None:
    settings = MagicMock()
    settings.app_name = "ECMP"
    settings.app_version = "1.0.0"
    settings.environment = "test"

    with (
        patch.object(health_mod, "get_settings", return_value=settings),
        patch.object(health_mod, "ping_database", side_effect=SQLAlchemyError("x")),
    ):
        resp = health_mod.health()
    assert resp.status == "degraded"
    assert resp.database == "down"

    with (
        patch.object(health_mod, "get_settings", return_value=settings),
        patch.object(health_mod, "ping_database", side_effect=RuntimeError("boom")),
    ):
        resp2 = health_mod.health()
    assert resp2.status == "degraded"
    assert resp2.database == "down"
