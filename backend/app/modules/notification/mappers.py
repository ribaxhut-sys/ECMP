"""Map between ORM NotificationQueue and domain NotificationRecord."""

from __future__ import annotations

from app.core.enums import NotificationChannel, NotificationQueueStatus
from app.modules.notification.domain.entity import NotificationRecord
from app.modules.notification.models import NotificationQueue


def to_record(row: NotificationQueue) -> NotificationRecord:
    channel = getattr(row, "channel", None) or NotificationChannel.EMAIL.value
    return NotificationRecord(
        id=row.id,
        notification_type=getattr(row, "notification_type", None),
        channel=channel,
        recipient=row.recipient or "",
        subject=getattr(row, "subject", None),
        message=getattr(row, "message", None),
        template=row.template_code,
        payload=dict(row.payload or {}),
        status=row.status,
        retry_count=row.retry_count,
        created_at=row.created_at,
        sent_at=row.sent_at,
        failed_at=getattr(row, "failed_at", None),
        last_error=row.last_error,
        scheduled_at=row.scheduled_at,
    )


def apply_record(row: NotificationQueue, record: NotificationRecord) -> None:
    if hasattr(row, "notification_type"):
        row.notification_type = record.notification_type
    if hasattr(row, "channel"):
        row.channel = record.channel
    row.recipient = record.recipient
    if hasattr(row, "subject"):
        row.subject = record.subject
    if hasattr(row, "message"):
        row.message = record.message
    row.template_code = record.template
    row.payload = dict(record.payload)
    row.status = record.status
    row.retry_count = record.retry_count
    row.sent_at = record.sent_at
    if hasattr(row, "failed_at"):
        row.failed_at = record.failed_at
    row.last_error = record.last_error
    row.scheduled_at = record.scheduled_at


def new_queue_row(record: NotificationRecord) -> NotificationQueue:
    return NotificationQueue(
        id=record.id,
        template_code=record.template,
        notification_type=record.notification_type,
        channel=record.channel,
        recipient=record.recipient,
        subject=record.subject,
        message=record.message,
        payload=dict(record.payload),
        status=record.status or NotificationQueueStatus.PENDING.value,
        retry_count=record.retry_count,
        scheduled_at=record.scheduled_at,
        sent_at=record.sent_at,
        failed_at=record.failed_at,
        last_error=record.last_error,
        created_at=record.created_at,
    )
