"""CAPABILITY-009 — NotificationRecord domain entity tests."""

from __future__ import annotations

import uuid

import pytest

from app.core.enums import NotificationChannel, NotificationQueueStatus
from app.core.errors import ValidationAppError
from app.modules.notification.domain.entity import NotificationRecord


def test_create_pending_notification() -> None:
    record = NotificationRecord.create(
        channel=NotificationChannel.EMAIL.value,
        recipient="user@example.com",
        notification_type="ComplaintCreated",
        subject="Hello",
        message="World",
        template="complaint.created",
    )
    assert record.status == NotificationQueueStatus.PENDING.value
    assert record.retry_count == 0
    assert record.sent_at is None
    assert record.failed_at is None


def test_create_rejects_unknown_channel() -> None:
    with pytest.raises(ValidationAppError):
        NotificationRecord.create(
            channel="CARRIER_PIGEON",
            recipient="x",
        )


def test_lifecycle_sending_sent() -> None:
    record = NotificationRecord.create(
        channel=NotificationChannel.SMS.value,
        recipient="+10000000000",
        message="ping",
    )
    record.mark_sending()
    assert record.status == NotificationQueueStatus.PROCESSING.value
    record.mark_sent()
    assert record.status == NotificationQueueStatus.SENT.value
    assert record.sent_at is not None


def test_lifecycle_failed_retry_cancel() -> None:
    record = NotificationRecord.create(
        channel=NotificationChannel.WEBHOOK.value,
        recipient="https://example.test/hook",
        notification_id=uuid.uuid4(),
    )
    record.mark_sending()
    record.mark_failed(error="stub boom")
    assert record.status == NotificationQueueStatus.FAILED.value
    assert record.failed_at is not None
    assert record.last_error == "stub boom"

    record.retry(max_retry=3)
    assert record.status == NotificationQueueStatus.PENDING.value
    assert record.retry_count == 1
    assert record.failed_at is None

    record.cancel()
    assert record.status == NotificationQueueStatus.CANCELLED.value


def test_retry_limit_exceeded() -> None:
    record = NotificationRecord.create(
        channel=NotificationChannel.PUSH.value,
        recipient="device-1",
    )
    record.retry_count = 3
    record.status = NotificationQueueStatus.FAILED.value
    with pytest.raises(ValidationAppError, match="[Bb]atas percobaan"):
        record.retry(max_retry=3)


def test_cancel_non_pending_rejected() -> None:
    record = NotificationRecord.create(
        channel=NotificationChannel.EMAIL.value,
        recipient="a@b.c",
    )
    record.mark_sent()
    with pytest.raises(ValidationAppError):
        record.cancel()
