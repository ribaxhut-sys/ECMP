"""SQLAlchemy ORM for CM Batch 1 Aggregate persistence (S2 Task 01).

Separate from legacy ``complaints`` / ``complaint_cases`` tables.
Optional ``case_id`` pin (FR-004) references ``cm_cases`` when a Case exists.
No Batch-2 columns on the Complaint aggregate itself.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
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
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class CmBatch1ComplaintORM(Base):
    """Complaint Aggregate Root for Batch 1 (DM-CM-001 / DB-CM-001)."""

    __tablename__ = "cm_batch1_complaints"
    __table_args__ = (
        UniqueConstraint("complaint_number", name="uq_cm_batch1_complaints_number"),
        Index("ix_cm_batch1_complaints_customer_id", "customer_id"),
        Index("ix_cm_batch1_complaints_status", "status"),
        Index("ix_cm_batch1_complaints_created_at", "created_at"),
        Index("ix_cm_batch1_complaints_intake_disposition", "intake_disposition"),
        Index("ix_cm_batch1_complaints_hq_accepted_at", "hq_accepted_at"),
        Index("ix_cm_batch1_complaints_decided_by", "decided_by"),
        Index("ix_cm_batch1_complaints_owning_unit_id", "owning_unit_id"),
        Index(
            "ix_cm_batch1_complaints_hq_destination_unit_id",
            "hq_destination_unit_id",
        ),
        # SLA feed only scans still-open complaints (DEC-031).
        Index(
            "ix_cm_batch1_complaints_open_created_at",
            "created_at",
            postgresql_where=text("closed_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    complaint_number: Mapped[str] = mapped_column(String(32), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(128), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    channel: Mapped[str] = mapped_column(String(64), nullable=False)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(32), nullable=False, default="MEDIUM")
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="REGISTERED"
    )
    # When the Aggregate reached CLOSED (DEC-031). Kept in lockstep with
    # ``status`` by ``apply_complaint_status`` — cleared again on reopen, so it
    # always describes the *current* closure, never a stale earlier one.
    # ``updated_at`` cannot serve this purpose: any edit moves it.
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Intake path label (not Aggregate lifecycle). e.g. ESCALATE_PENDING_APPROVAL.
    intake_disposition: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    # When set, HQ has accepted/claimed — Batalkan Eskalasi blocked.
    hq_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Org unit key (Branch.code / "PUSAT") — list visibility SoT (DEC-024 pattern).
    owning_unit_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Customer visit schedule at HQ (Batch-1 lab; not foundation Appointment).
    hq_arrival_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    hq_arrival_time: Mapped[str | None] = mapped_column(String(5), nullable=True)
    # Which Pusat unit the taxpayer reports to (PUSAT-CRO / PUSAT-SEKRE /
    # PUSAT-SUBAN-…). Set by Pusat together with the final arrival time — never
    # by the branch, and never written into owning_unit_id (that column is the
    # visibility SoT and holds the originating branch).
    hq_destination_unit_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    hq_destination_set_by: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    hq_destination_set_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Branch-proposed slot at escalation time — advisory only, cleared once
    # Pusat decides (accept/return). Not a reservation.
    proposed_arrival_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    proposed_arrival_time: Mapped[str | None] = mapped_column(
        String(5), nullable=True
    )
    proposed_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    proposed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # True after the first Case exists (mark_complaint_in_progress /
    # sync_complaint_status_from_cases). Default false at intake.
    case_created: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    created_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    # Who resolved the intake-escalation decision (APPROVE/REJECT/CANCEL) and
    # when — UM-BUG-006, see decide_intake_escalation in service.py.
    decided_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
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


class CmBatch1IdempotencyORM(Base):
    """Request Id (Idempotency-Key) → Aggregate (D-03 / DM-CM-010)."""

    __tablename__ = "cm_batch1_idempotency"
    __table_args__ = (
        UniqueConstraint("request_id", name="uq_cm_batch1_idempotency_request_id"),
        Index("ix_cm_batch1_idempotency_complaint_id", "complaint_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    request_id: Mapped[str] = mapped_column(String(256), nullable=False)
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_batch1_complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class CmBatch1ChannelMessageORM(Base):
    """Channel Message Id → Aggregate (D-03)."""

    __tablename__ = "cm_batch1_channel_messages"
    __table_args__ = (
        UniqueConstraint(
            "channel_message_id", name="uq_cm_batch1_channel_message_id"
        ),
        Index("ix_cm_batch1_channel_messages_complaint_id", "complaint_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    channel_message_id: Mapped[str] = mapped_column(String(256), nullable=False)
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_batch1_complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class CmBatch1CustomerLockORM(Base):
    """Per-principal confirmed CustomerId lock (FR-002 confirm)."""

    __tablename__ = "cm_batch1_customer_locks"
    __table_args__ = (
        UniqueConstraint("principal_key", name="uq_cm_batch1_customer_locks_principal"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    principal_key: Mapped[str] = mapped_column(String(128), nullable=False)
    customer_id: Mapped[str] = mapped_column(String(128), nullable=False)
    locked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class CmBatch1NumberCounterORM(Base):
    """Portable counter — key ``cn:UNIT:YYYYMM`` for ``CM{UNIT}-YYMM-NNNN``."""

    __tablename__ = "cm_batch1_number_counters"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class CmBatch1DuplicateDecisionORM(Base):
    """FR-003 duplicate decision / linkage history (BR-014 / BR-018)."""

    __tablename__ = "cm_batch1_duplicate_decisions"
    __table_args__ = (
        Index("ix_cm_batch1_dup_decisions_customer_id", "customer_id"),
        Index("ix_cm_batch1_dup_decisions_surviving", "surviving_complaint_id"),
        Index("ix_cm_batch1_dup_decisions_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    customer_id: Mapped[str] = mapped_column(String(128), nullable=False)
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    surviving_complaint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_batch1_complaints.id", ondelete="SET NULL"),
        nullable=True,
    )
    source_complaint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_batch1_complaints.id", ondelete="SET NULL"),
        nullable=True,
    )
    justification: Mapped[str | None] = mapped_column(Text, nullable=True)
    staging_token: Mapped[str | None] = mapped_column(String(256), nullable=True)
    warning: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    hard_block: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    policy_version: Mapped[str] = mapped_column(String(64), nullable=False)
    candidate_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    later_review_work_item_id: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    case_created: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class CmBatch1LaterReviewItemORM(Base):
    """Supervisor later-review work item when duplicate check is degraded (FR-003 E1)."""

    __tablename__ = "cm_batch1_later_review_items"
    __table_args__ = (
        Index("ix_cm_batch1_later_review_customer_id", "customer_id"),
        Index("ix_cm_batch1_later_review_status", "status"),
        Index("ix_cm_batch1_later_review_complaint_id", "complaint_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    work_item_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    customer_id: Mapped[str] = mapped_column(String(128), nullable=False)
    complaint_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    reason: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class CmBatch1AttachmentStagingORM(Base):
    """Create-session staging token (FR-004 A4 / D-06)."""

    __tablename__ = "cm_batch1_attachment_staging"
    __table_args__ = (
        UniqueConstraint("staging_token", name="uq_cm_batch1_staging_token"),
        Index("ix_cm_batch1_staging_status", "status"),
        Index("ix_cm_batch1_staging_expires_at", "expires_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    staging_token: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="OPEN")
    created_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class CmBatch1AttachmentORM(Base):
    """Batch 1 attachment business metadata linked to CAP-011 attachment row."""

    __tablename__ = "cm_batch1_attachments"
    __table_args__ = (
        Index("ix_cm_batch1_attachments_complaint_id", "complaint_id"),
        Index("ix_cm_batch1_attachments_staging_token", "staging_token"),
        Index("ix_cm_batch1_attachments_status", "status"),
        Index("ix_cm_batch1_attachments_platform_id", "platform_attachment_id"),
        Index("ix_cm_batch1_attachments_checksum", "checksum_sha256"),
        Index("ix_cm_batch1_attachments_customer_id", "customer_id"),
        Index("ix_cm_batch1_attachments_case_id", "case_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    platform_attachment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attachments.id", ondelete="RESTRICT"),
        nullable=False,
    )
    staging_token: Mapped[str | None] = mapped_column(String(128), nullable=True)
    complaint_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_batch1_complaints.id", ondelete="SET NULL"),
        nullable=True,
    )
    customer_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    case_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_cases.id", ondelete="SET NULL"),
        nullable=True,
    )
    classification: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_batch1_attachments.id", ondelete="SET NULL"),
        nullable=True,
    )
    void_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
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


class CmBatch1AttachmentHistoryORM(Base):
    """Append-only attachment history (FR-004 / BR-012)."""

    __tablename__ = "cm_batch1_attachment_history"
    __table_args__ = (
        Index("ix_cm_batch1_att_history_attachment_id", "attachment_id"),
        Index("ix_cm_batch1_att_history_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    attachment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_batch1_attachments.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


class CmBatch1OutboxORM(Base):
    """Persist-only EVT-CM-* outbox (S2 Task 04). No publisher."""

    __tablename__ = "cm_batch1_outbox"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_cm_batch1_outbox_idempotency_key"),
        Index("ix_cm_batch1_outbox_event_id", "event_id"),
        Index("ix_cm_batch1_outbox_status", "status"),
        Index("ix_cm_batch1_outbox_aggregate", "aggregate_type", "aggregate_id"),
        Index("ix_cm_batch1_outbox_occurred_at", "occurred_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    event_id: Mapped[str] = mapped_column(String(32), nullable=False)
    event_name: Mapped[str] = mapped_column(String(128), nullable=False)
    aggregate_type: Mapped[str] = mapped_column(String(64), nullable=False)
    aggregate_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    idempotency_key: Mapped[str] = mapped_column(String(256), nullable=False)
    payload_json: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="UNPUBLISHED")
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
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class CmBatch1PusatQueueSeenORM(Base):
    """Per-user Pusat read receipt for the HQ queue row (one row per parent).

    Derived-unread model: no fan-out at escalation time, so a Pusat user who
    joins later still sees the backlog and no user directory is needed (the
    directory belongs to the Enterprise Platform, ADR-015). A row is written
    only when someone opens the complaint (or one of its Cases); the badge
    treats the row as read while ``seen_at`` is newer than the last branch
    movement on that complaint.
    """

    __tablename__ = "cm_pusat_queue_seen"
    __table_args__ = (
        UniqueConstraint(
            "complaint_id", "user_id", name="uq_cm_pusat_queue_seen_pair"
        ),
        Index("ix_cm_pusat_queue_seen_user_id", "user_id"),
        Index("ix_cm_pusat_queue_seen_complaint_id", "complaint_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    complaint_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("cm_batch1_complaints.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[str] = mapped_column(String(128), nullable=False)
    seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
