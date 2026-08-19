"""SQLAlchemy ORM for Pengaduan Internal."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    false,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class InternalComplaintORM(Base):
    __tablename__ = "internal_complaints"
    __table_args__ = (
        UniqueConstraint("complaint_number", name="uq_internal_complaints_number"),
        Index("ix_internal_complaints_status", "status"),
        Index("ix_internal_complaints_owner_unit", "owner_unit_id"),
        Index("ix_internal_complaints_handling_unit", "handling_unit_id"),
        Index("ix_internal_complaints_created_at", "created_at"),
        Index(
            "ix_internal_complaints_transfer_request_status",
            "transfer_request_status",
        ),
        Index(
            "ix_internal_complaints_withdraw_request_status",
            "withdraw_request_status",
        ),
        Index(
            "ix_internal_complaints_completion_request_status",
            "completion_request_status",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    complaint_number: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    subcategory: Mapped[str | None] = mapped_column(String(200), nullable=True)
    priority: Mapped[str] = mapped_column(String(32), nullable=False)
    chronology: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Optional reference to Batch-1 Aggregate (snapshot number for display).
    related_complaint_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    related_complaint_number: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    owner_unit_id: Mapped[str] = mapped_column(String(128), nullable=False)
    handling_unit_id: Mapped[str] = mapped_column(String(128), nullable=False)
    supervisor_approved_after_resolved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    # Agent-family transfer request gate — PENDING/APPROVED/REJECTED, null
    # when no request has ever been made (Supervisor/Manager direct create).
    transfer_request_status: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )
    transfer_request_destination_unit_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    transfer_request_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    transfer_requested_by: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    transfer_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    transfer_decided_by: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    transfer_decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    transfer_decision_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    withdraw_request_status: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )
    withdraw_request_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    withdraw_requested_by: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    withdraw_requested_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    withdraw_decided_by: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    withdraw_decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    withdraw_decision_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    withdrawn_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    withdraw_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    completion_request_status: Mapped[str | None] = mapped_column(
        String(16), nullable=True
    )
    completion_return_reason: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    completion_returned_by: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    completion_returned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    pusat_handled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    closed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
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


class InternalComplaintResolutionORM(Base):
    __tablename__ = "internal_complaint_resolutions"
    __table_args__ = (Index("ix_ic_resolutions_complaint_id", "complaint_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("internal_complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    resolution_code: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    summary: Mapped[str] = mapped_column(String(1000), nullable=False, default="")
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    proposed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    decided_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class InternalComplaintAcceptanceORM(Base):
    """Append-only dual-acceptance history."""

    __tablename__ = "internal_complaint_acceptances"
    __table_args__ = (Index("ix_ic_acceptances_complaint_id", "complaint_id"),)

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("internal_complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    party: Mapped[str] = mapped_column(String(32), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_unit_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    decided_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class InternalComplaintEventORM(Base):
    """Append-only timeline / history for Pengaduan Internal."""

    __tablename__ = "internal_complaint_events"
    __table_args__ = (
        Index("ix_ic_events_complaint_id", "complaint_id"),
        Index("ix_ic_events_occurred_at", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("internal_complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_unit_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    source_unit_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    target_unit_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class InternalComplaintNumberCounterORM(Base):
    """Legacy per-year global counter — kept read-only for rows already on disk.

    Superseded by ``InternalComplaintUnitCounterORM`` (per-unit-per-month);
    not written by ``create()`` anymore. Not dropped: old ``PI-YYYY-NNNNNN``
    lab rows must stay resolvable and are never remapped.
    """

    __tablename__ = "internal_complaint_number_counters"

    year: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_seq: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class InternalComplaintUnitCounterORM(Base):
    """Per-unit-per-month sequence for ``PI-{UNIT}-{YYMM}-{NNN}`` (current format)."""

    __tablename__ = "internal_complaint_unit_counters"

    unit_code: Mapped[str] = mapped_column(String(8), primary_key=True)
    # YYYYMM, e.g. 202608 — integer sort order matches chronological order.
    period: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_seq: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
