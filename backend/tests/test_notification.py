"""Notification Foundation unit/service tests (TASK-030)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.errors import ConflictError, NotFoundError, ValidationAppError
from app.modules.notification.schemas import (
    NotificationCreateRequest,
    NotificationTemplateCreateRequest,
    NotificationTemplateUpdateRequest,
)
from app.modules.notification.service import (
    SETTING_DEFAULT_CHANNEL,
    SETTING_ENABLED,
    SETTING_MAX_RETRY,
    NotificationService,
    _render_text,
)


def _settings(
    *,
    enabled: bool = True,
    channel: str = "EMAIL",
    max_retry: int = 3,
) -> MagicMock:
    settings = MagicMock()
    settings.get_bool.side_effect = lambda key, default=None: (
        enabled if key == SETTING_ENABLED else (default if default is not None else True)
    )
    settings.get_string.side_effect = lambda key, default=None: (
        channel
        if key == SETTING_DEFAULT_CHANNEL
        else (default if default is not None else "")
    )
    settings.get_int.side_effect = lambda key, default=None: (
        max_retry
        if key == SETTING_MAX_RETRY
        else (default if default is not None else 0)
    )
    return settings


def _template(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "code": "COMPLAINT_ASSIGNED",
        "name": "Complaint Assigned",
        "channel": "EMAIL",
        "subject": "Assigned: {{complaintNumber}}",
        "content": "Hello {{assigneeName}}, case {{complaintNumber}}.",
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def _queue(**overrides: object) -> SimpleNamespace:
    now = datetime.now(UTC)
    base = {
        "id": uuid.uuid4(),
        "template_code": "COMPLAINT_ASSIGNED",
        "recipient": "agent@example.com",
        "payload": {"channel": "EMAIL"},
        "status": "PENDING",
        "retry_count": 0,
        "scheduled_at": None,
        "sent_at": None,
        "last_error": None,
        "created_at": now,
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_render_text_replaces_placeholders() -> None:
    assert (
        _render_text("Hi {{name}} — {{ticket}}", {"name": "Ada", "ticket": "T-1"})
        == "Hi Ada — T-1"
    )
    assert _render_text("Keep {{unknown}}", {}) == "Keep {{unknown}}"


def test_create_template_rejects_duplicate_code() -> None:
    repo = MagicMock()
    repo.get_template_by_code.return_value = _template()
    service = NotificationService(repository=repo, settings=_settings())

    with pytest.raises(ConflictError):
        service.create_template(
            NotificationTemplateCreateRequest(
                code="COMPLAINT_ASSIGNED",
                name="Dup",
                channel="EMAIL",
                content="x",
            )
        )


def test_create_enqueues_pending_with_rendered_payload() -> None:
    template = _template()
    repo = MagicMock()
    repo.get_template_by_code.return_value = template

    def add_queue(row: object) -> object:
        return row

    repo.add_queue.side_effect = add_queue
    service = NotificationService(repository=repo, settings=_settings())

    result = service.create(
        NotificationCreateRequest(
            templateCode="COMPLAINT_ASSIGNED",
            recipient="agent@example.com",
            variables={"complaintNumber": "CMP-1", "assigneeName": "Ada"},
        )
    )

    assert result.status == "PENDING"
    assert result.recipient == "agent@example.com"
    assert result.payload is not None
    assert result.payload["subject"] == "Assigned: CMP-1"
    assert result.payload["content"] == "Hello Ada, case CMP-1."
    assert result.payload["maxRetry"] == 3
    assert result.payload["channel"] == "EMAIL"
    repo.commit.assert_called()


def test_create_rejects_when_notifications_disabled() -> None:
    service = NotificationService(
        repository=MagicMock(), settings=_settings(enabled=False)
    )
    with pytest.raises(ValidationAppError, match="dinonaktifkan"):
        service.create(
            NotificationCreateRequest(
                templateCode="COMPLAINT_ASSIGNED",
                recipient="a@b.com",
            )
        )


def test_create_rejects_inactive_template() -> None:
    repo = MagicMock()
    repo.get_template_by_code.return_value = _template(is_active=False)
    service = NotificationService(repository=repo, settings=_settings())
    with pytest.raises(NotFoundError):
        service.create(
            NotificationCreateRequest(
                templateCode="COMPLAINT_ASSIGNED",
                recipient="a@b.com",
            )
        )


def test_cancel_pending_sets_cancelled() -> None:
    row = _queue(status="PENDING")
    repo = MagicMock()
    repo.get_queue_by_id.return_value = row
    service = NotificationService(repository=repo, settings=_settings())

    result = service.cancel(row.id)
    assert result.status == "CANCELLED"
    assert row.status == "CANCELLED"
    repo.commit.assert_called()


def test_cancel_non_pending_rejected() -> None:
    row = _queue(status="SENT")
    repo = MagicMock()
    repo.get_queue_by_id.return_value = row
    service = NotificationService(repository=repo, settings=_settings())
    with pytest.raises(ValidationAppError, match="PENDING"):
        service.cancel(row.id)


def test_delete_template_soft_deactivates() -> None:
    row = _template(is_active=True)
    repo = MagicMock()
    repo.get_template_by_id.return_value = row
    service = NotificationService(repository=repo, settings=_settings())

    service.delete_template(row.id)
    repo.soft_delete_template.assert_called_once_with(row)
    repo.commit.assert_called()


def test_update_template_requires_fields() -> None:
    row = _template()
    repo = MagicMock()
    repo.get_template_by_id.return_value = row
    service = NotificationService(repository=repo, settings=_settings())
    with pytest.raises(ValidationAppError):
        service.update_template(row.id, NotificationTemplateUpdateRequest())
