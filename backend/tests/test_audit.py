"""Audit Log unit/service tests (TASK-031)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import NotFoundError, ValidationAppError
from app.modules.audit.service import AuditService, redact_sensitive


def test_redact_sensitive_masks_secrets() -> None:
    payload = {
        "username": "admin",
        "password": "secret123",
        "nested": {"api_key": "abc", "ok": True},
        "token": "jwt-value",
        "authorization": "Bearer x",
        "refresh_token": "r",
        "cookie": "sid=1",
    }
    cleaned = redact_sensitive(payload)
    assert cleaned["username"] == "admin"
    assert cleaned["password"] == "***REDACTED***"
    assert cleaned["nested"]["api_key"] == "***REDACTED***"
    assert cleaned["nested"]["ok"] is True
    assert cleaned["token"] == "***REDACTED***"
    assert cleaned["authorization"] == "***REDACTED***"
    assert cleaned["refresh_token"] == "***REDACTED***"
    assert cleaned["cookie"] == "***REDACTED***"


def test_log_persists_pending_row() -> None:
    repo = MagicMock()

    def add(row: object) -> object:
        return row

    repo.add.side_effect = add
    service = AuditService(repo)

    result = service.log(
        event_type="setting.updated",
        entity_type="Setting",
        action="UPDATE",
        entity_id=uuid.uuid4(),
        actor_id=uuid.uuid4(),
        actor_name="golive_admin",
        old_values={"value": "old", "password": "x"},
        new_values={"value": "new"},
    )

    assert result.event_type == "setting.updated"
    assert result.action == "UPDATE"
    assert result.old_values is not None
    assert result.old_values["password"] == "***REDACTED***"
    assert result.old_values["value"] == "old"
    repo.commit.assert_called_once()


def test_log_rejects_invalid_action() -> None:
    service = AuditService(MagicMock())
    with pytest.raises(ValidationAppError):
        service.log(
            event_type="x",
            entity_type="Y",
            action="HACK",
        )


def test_get_not_found() -> None:
    repo = MagicMock()
    repo.get_by_id.return_value = None
    service = AuditService(repo)
    with pytest.raises(NotFoundError):
        service.get(uuid.uuid4())


def test_list_validates_date_range() -> None:
    service = AuditService(MagicMock())
    start = datetime(2026, 7, 24, tzinfo=UTC)
    end = datetime(2026, 7, 23, tzinfo=UTC)
    with pytest.raises(ValidationAppError):
        service.list(date_from=start, date_to=end)


def test_list_returns_mapped_rows() -> None:
    now = datetime.now(UTC)
    row = SimpleNamespace(
        id=uuid.uuid4(),
        event_type="attachment.deleted",
        entity_type="Attachment",
        entity_id=uuid.uuid4(),
        action="DELETE",
        actor_id=uuid.uuid4(),
        actor_name="admin",
        ip_address="127.0.0.1",
        user_agent="pytest",
        old_values={"filename": "a.pdf"},
        new_values=None,
        metadata_json=None,
        created_at=now,
    )
    repo = MagicMock()
    repo.list.return_value = [row]
    service = AuditService(repo)
    items = service.list(action="DELETE", limit=10)
    assert len(items) == 1
    assert items[0].action == "DELETE"
    assert items[0].event_type == "attachment.deleted"
