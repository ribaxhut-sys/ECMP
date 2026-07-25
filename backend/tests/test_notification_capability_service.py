"""CAPABILITY-009 — NotificationService lifecycle + stub provider tests."""

from __future__ import annotations

import uuid
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from app.core.enums import NotificationQueueStatus
from app.core.errors import ValidationAppError
from app.modules.notification.infrastructure.providers import StubNotificationProvider
from app.modules.notification.service import NotificationService


def _settings(*, max_retry: int = 3, enabled: bool = True) -> MagicMock:
    settings = MagicMock()
    settings.get_bool.return_value = enabled
    settings.get_string.return_value = "EMAIL"
    settings.get_int.return_value = max_retry
    return settings


def _queue_row(**overrides):
    base = {
        "id": uuid.uuid4(),
        "template_code": "TPL_A",
        "notification_type": "TemplateEnqueue",
        "channel": "EMAIL",
        "recipient": "a@b.c",
        "subject": "Hi",
        "message": "Body",
        "payload": {"channel": "EMAIL", "content": "Body"},
        "status": NotificationQueueStatus.PENDING.value,
        "retry_count": 0,
        "scheduled_at": None,
        "sent_at": None,
        "failed_at": None,
        "last_error": None,
        "created_at": __import__("datetime").datetime.now(
            __import__("datetime").UTC
        ),
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def test_process_marks_sent_via_stub() -> None:
    row = _queue_row()
    repo = MagicMock()
    repo.get_queue_by_id.return_value = row
    service = NotificationService(
        repository=repo,
        settings=_settings(),
        provider=StubNotificationProvider(),
    )
    result = service.process(row.id)
    assert result.status == NotificationQueueStatus.SENT.value
    assert row.status == NotificationQueueStatus.SENT.value
    assert row.sent_at is not None
    repo.commit.assert_called()


def test_process_marks_failed_via_stub() -> None:
    row = _queue_row()
    repo = MagicMock()
    repo.get_queue_by_id.return_value = row
    service = NotificationService(
        repository=repo,
        settings=_settings(),
        provider=StubNotificationProvider(succeed=False, detail="nope"),
    )
    result = service.process(row.id)
    assert result.status == NotificationQueueStatus.FAILED.value
    assert row.last_error == "nope"
    assert row.failed_at is not None


def test_retry_increments_and_returns_pending() -> None:
    row = _queue_row(
        status=NotificationQueueStatus.FAILED.value,
        retry_count=1,
        last_error="x",
    )
    repo = MagicMock()
    repo.get_queue_by_id.return_value = row
    service = NotificationService(repository=repo, settings=_settings(max_retry=3))
    result = service.retry(row.id)
    assert result.status == NotificationQueueStatus.PENDING.value
    assert result.retry_count == 2
    assert row.last_error is None


def test_retry_rejects_when_limit_reached() -> None:
    row = _queue_row(
        status=NotificationQueueStatus.FAILED.value,
        retry_count=3,
    )
    repo = MagicMock()
    repo.get_queue_by_id.return_value = row
    service = NotificationService(repository=repo, settings=_settings(max_retry=3))
    with pytest.raises(ValidationAppError, match="retry limit"):
        service.retry(row.id)


def test_mark_sent_and_failed_helpers() -> None:
    row = _queue_row()
    repo = MagicMock()
    repo.get_queue_by_id.return_value = row
    service = NotificationService(repository=repo, settings=_settings())
    service.mark_sent(row.id)
    assert row.status == NotificationQueueStatus.SENT.value

    row2 = _queue_row()
    repo.get_queue_by_id.return_value = row2
    service.mark_failed(row2.id, error="boom")
    assert row2.status == NotificationQueueStatus.FAILED.value
    assert row2.last_error == "boom"
