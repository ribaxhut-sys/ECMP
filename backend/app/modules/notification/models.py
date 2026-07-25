"""Notification Foundation ORM models (TASK-030).

Platform service tables — not owned by Complaint or any domain module.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    DateTime,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
    true,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class NotificationTemplate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Reusable notification template (channel + subject/content).

    Soft-delete uses ``is_active=False`` (schema has no ``deleted_at``).
    Queue rows reference ``code`` by value, not FK.
    """

    __tablename__ = "notification_templates"
    __table_args__ = (
        UniqueConstraint("code", name="uq_notification_templates_code"),
        Index("ix_notification_templates_channel", "channel"),
        Index("ix_notification_templates_is_active", "is_active"),
    )

    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    channel: Mapped[str] = mapped_column(String(30), nullable=False)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )


class NotificationQueue(UUIDPrimaryKeyMixin, Base):
    """Persisted Notification request (CAPABILITY-009 / TASK-030 table).

    Channel-independent queue row. Transport adapters are stubbed —
    no SMTP / WhatsApp / SMS / Push / webhook network calls here.
    """

    __tablename__ = "notification_queue"
    __table_args__ = (
        Index("ix_notification_queue_template_code", "template_code"),
        Index("ix_notification_queue_status", "status"),
        Index("ix_notification_queue_scheduled_at", "scheduled_at"),
        Index("ix_notification_queue_created_at", "created_at"),
        Index("ix_notification_queue_channel", "channel"),
        Index("ix_notification_queue_recipient", "recipient"),
    )

    template_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notification_type: Mapped[str | None] = mapped_column(String(80), nullable=True)
    channel: Mapped[str | None] = mapped_column(String(30), nullable=True)
    recipient: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    failed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
