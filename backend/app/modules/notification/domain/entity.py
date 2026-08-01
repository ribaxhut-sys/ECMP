"""Notification domain entity + lifecycle (CAPABILITY-009).

Channel-independent: Complaint never chooses EMAIL/WhatsApp/SMS.
Transport is decided by Notification + stub providers only.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Mapping

from app.core.enums import NotificationChannel, NotificationQueueStatus
from app.core.errors import ValidationAppError
from app.core.user_messages import m


@dataclass
class NotificationRecord:
    """Mutable domain record for a persisted notification request.

    Maps to ``notification_queue`` (foundation table). Status *Sending*
    is stored as ``PROCESSING``.
    """

    id: uuid.UUID
    notification_type: str | None
    channel: str
    recipient: str
    subject: str | None
    message: str | None
    template: str | None
    payload: dict[str, Any]
    status: str
    retry_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    sent_at: datetime | None = None
    failed_at: datetime | None = None
    last_error: str | None = None
    scheduled_at: datetime | None = None

    @classmethod
    def create(
        cls,
        *,
        channel: str,
        recipient: str,
        notification_type: str | None = None,
        subject: str | None = None,
        message: str | None = None,
        template: str | None = None,
        payload: Mapping[str, Any] | None = None,
        notification_id: uuid.UUID | None = None,
        scheduled_at: datetime | None = None,
    ) -> NotificationRecord:
        try:
            NotificationChannel(channel)
        except ValueError as exc:
            raise ValidationAppError(
                f"kanal notifikasi tidak didukung: {channel}",
                details={
                    "channel": channel,
                    "allowed": [c.value for c in NotificationChannel],
                },
            ) from exc
        now = datetime.now(UTC)
        return cls(
            id=notification_id or uuid.uuid4(),
            notification_type=notification_type,
            channel=channel,
            recipient=recipient,
            subject=subject,
            message=message,
            template=template,
            payload=dict(payload or {}),
            status=NotificationQueueStatus.PENDING.value,
            retry_count=0,
            created_at=now,
            sent_at=None,
            failed_at=None,
            last_error=None,
            scheduled_at=scheduled_at,
        )

    def mark_sending(self) -> None:
        if self.status not in (
            NotificationQueueStatus.PENDING.value,
            NotificationQueueStatus.FAILED.value,
        ):
            raise ValidationAppError(
                m("notification.only_pending_failed_enter_sending"),
                details={"id": str(self.id), "status": self.status},
            )
        self.status = NotificationQueueStatus.PROCESSING.value

    def mark_sent(self, *, now: datetime | None = None) -> None:
        if self.status not in (
            NotificationQueueStatus.PENDING.value,
            NotificationQueueStatus.PROCESSING.value,
        ):
            raise ValidationAppError(
                m("notification.only_pending_processing_sent"),
                details={"id": str(self.id), "status": self.status},
            )
        ts = now or datetime.now(UTC)
        self.status = NotificationQueueStatus.SENT.value
        self.sent_at = ts
        self.failed_at = None
        self.last_error = None

    def mark_failed(
        self,
        *,
        error: str,
        now: datetime | None = None,
    ) -> None:
        if self.status not in (
            NotificationQueueStatus.PENDING.value,
            NotificationQueueStatus.PROCESSING.value,
        ):
            raise ValidationAppError(
                m("notification.only_pending_processing_failed"),
                details={"id": str(self.id), "status": self.status},
            )
        ts = now or datetime.now(UTC)
        self.status = NotificationQueueStatus.FAILED.value
        self.failed_at = ts
        self.last_error = error

    def cancel(self) -> None:
        if self.status == NotificationQueueStatus.CANCELLED.value:
            return
        if self.status != NotificationQueueStatus.PENDING.value:
            raise ValidationAppError(
                m("notification.only_pending_cancel"),
                details={"id": str(self.id), "status": self.status},
            )
        self.status = NotificationQueueStatus.CANCELLED.value

    def retry(self, *, max_retry: int) -> None:
        if self.status not in (
            NotificationQueueStatus.FAILED.value,
            NotificationQueueStatus.PENDING.value,
        ):
            raise ValidationAppError(
                m("notification.only_failed_pending_retry"),
                details={"id": str(self.id), "status": self.status},
            )
        if self.retry_count >= max_retry:
            raise ValidationAppError(
                m("notification.retry_limit_exceeded"),
                details={
                    "id": str(self.id),
                    "retryCount": self.retry_count,
                    "maxRetry": max_retry,
                },
            )
        self.retry_count += 1
        self.status = NotificationQueueStatus.PENDING.value
        self.failed_at = None
        self.last_error = None
        self.sent_at = None
