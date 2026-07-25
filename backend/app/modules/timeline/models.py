"""CAPABILITY-010 Timeline ORM — append-only timeline_entries."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin


class TimelineEntryORM(UUIDPrimaryKeyMixin, Base):
    """Persisted activity history row. No update / delete columns by design."""

    __tablename__ = "timeline_entries"
    __table_args__ = (
        Index("ix_timeline_entries_aggregate_type", "aggregate_type"),
        Index("ix_timeline_entries_aggregate_id", "aggregate_id"),
        Index("ix_timeline_entries_event_type", "event_type"),
        Index("ix_timeline_entries_created_at", "created_at"),
        Index(
            "ix_timeline_entries_aggregate_created",
            "aggregate_type",
            "aggregate_id",
            "created_at",
        ),
    )

    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    actor_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
