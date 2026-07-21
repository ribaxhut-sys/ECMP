"""Persistence models — snake_case columns per naming standard (21 Technical Standards).

Tables match Alembic revision 0001: cases, audit_log, outbox.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Index, String, Text, false
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class CaseModel(Base):
    __tablename__ = "cases"
    __table_args__ = (Index("ix_cases_customer_id", "customer_id"),)

    case_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(64), nullable=False)
    case_type: Mapped[str] = mapped_column(String(32), nullable=False)
    priority: Mapped[str] = mapped_column(String(16), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    channel: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # server_default matches Alembic revision 0001 (schema parity checked in tests).
    customer_verified: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(String(64), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_by: Mapped[str] = mapped_column(String(64), nullable=False)


class AuditLogModel(Base):
    """Append-only audit trail (BR-008). No update/delete path exists in the application."""

    __tablename__ = "audit_log"
    __table_args__ = (Index("ix_audit_log_entity", "entity_type", "entity_id"),)

    log_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    actor_user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(64), nullable=False)
    new_value: Mapped[dict] = mapped_column(JSON, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class OutboxModel(Base):
    """Transactional outbox (ADR-009): events persisted with the business write."""

    __tablename__ = "outbox"
    __table_args__ = (Index("ix_outbox_unpublished", "published_at", "created_at"),)

    outbox_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_id: Mapped[str] = mapped_column(String(16), nullable=False)
    event_name: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
