"""Queue ORM models — separate from domain models (TASK-063).

Never expose outside infrastructure / repositories / mappers.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class QueueORM(Base):
    """Persistence row for Queue aggregate root."""

    __tablename__ = "queues"
    __table_args__ = (
        Index("ix_queues_organization_id", "organization_id"),
        Index("ix_queues_status", "status"),
        Index("ix_queues_organization_status", "organization_id", "status"),
    )

    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    policy: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    tickets: Mapped[list[QueueTicketORM]] = relationship(
        back_populates="queue",
        cascade="all, delete-orphan",
    )
    counters: Mapped[list[QueueCounterORM]] = relationship(
        back_populates="queue",
        cascade="all, delete-orphan",
    )


class QueueTicketORM(Base):
    """Persistence row for QueueTicket (immutable domain VO; row is replaceable)."""

    __tablename__ = "queue_tickets"
    __table_args__ = (
        UniqueConstraint(
            "queue_id",
            "ticket_number",
            name="uq_queue_tickets_queue_id_ticket_number",
        ),
        Index("ix_queue_tickets_queue_id", "queue_id"),
        Index("ix_queue_tickets_status", "status"),
        Index("ix_queue_tickets_queue_status", "queue_id", "status"),
        Index("ix_queue_tickets_created_at", "created_at"),
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("queues.queue_id", ondelete="CASCADE"),
        nullable=False,
    )
    ticket_number: Mapped[str] = mapped_column(String(64), nullable=False)
    priority: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    queue: Mapped[QueueORM] = relationship(back_populates="tickets")


class QueueCounterORM(Base):
    """Persistence row for QueueCounter (queue_id is infrastructure association)."""

    __tablename__ = "queue_counters"
    __table_args__ = (
        Index("ix_queue_counters_queue_id", "queue_id"),
        Index("ix_queue_counters_status", "status"),
    )

    counter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("queues.queue_id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    queue: Mapped[QueueORM] = relationship(back_populates="counters")


__all__ = [
    "QueueCounterORM",
    "QueueORM",
    "QueueTicketORM",
]
