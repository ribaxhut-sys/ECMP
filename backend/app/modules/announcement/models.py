"""SQLAlchemy ORM for Pengumuman (Complaint module operational announcements).

Flat module (mirrors app.modules.sla) — no separate DDD layering needed for
a single-aggregate content record. Reuses TimestampAuditSoftDeleteMixin for
created_at/updated_at/deleted_at/created_by/updated_by so audit columns match
the rest of ECMP v1.0 (no bespoke audit system).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import (
    AuditUserMixin,
    Base,
    TimestampAuditSoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

ANNOUNCEMENT_PRIORITIES = ("NORMAL", "IMPORTANT")
ANNOUNCEMENT_STATUSES = ("DRAFT", "PUBLISHED", "ARCHIVED")
# IMMEDIATE = visible as soon as the file exists, even while the announcement
# is still DRAFT. PUBLISHED (default — the safe choice) = follows the
# announcement's own status, only visible once PUBLISHED.
ANNOUNCEMENT_ATTACHMENT_VISIBILITIES = ("IMMEDIATE", "PUBLISHED")


class AnnouncementORM(TimestampAuditSoftDeleteMixin, Base):
    """Operational announcement shown on the Complaint module landing page.

    published_at / start_at / end_at intentionally stay simple timestamps —
    no scheduling engine. Publish sets published_at := now; start_at may be
    now (immediate) or a future visibility start; end_at is an optional plain
    expiry. Both start_at and end_at are evaluated at read/query time only.
    """

    __tablename__ = "announcements"
    __table_args__ = (
        Index("ix_announcements_status", "status"),
        Index("ix_announcements_published_at", "published_at"),
        Index("uq_announcements_reference_number", "reference_number", unique=True),
    )

    # Human reference — PGM-YYMM-NNNN; allocated at create, never rewritten.
    reference_number: Mapped[str] = mapped_column(String(32), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="NORMAL")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")

    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )


class AnnouncementNumberCounterORM(Base):
    """Portable counter — key ``an:YYYYMM`` for format ``PGM-YYMM-NNNN``."""

    __tablename__ = "announcement_number_counters"

    name: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class AnnouncementAttachmentORM(UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin, Base):
    """Join row: which platform Attachment belongs to which Announcement, and
    under which of the two visibility options (business decision, LOCKED).

    Pure relation + attribute — no soft-delete of its own. Removing an
    attachment from an announcement deletes this row; the underlying
    ``attachments`` row keeps its own existing soft-delete (status=DELETED)
    via the shared AttachmentService, unchanged.
    """

    __tablename__ = "announcement_attachments"
    __table_args__ = (
        UniqueConstraint(
            "announcement_id", "attachment_id", name="uq_announcement_attachments_pair"
        ),
        Index("ix_announcement_attachments_announcement_id", "announcement_id"),
        Index("ix_announcement_attachments_attachment_id", "attachment_id"),
    )

    announcement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("announcements.id", ondelete="CASCADE"),
        nullable=False,
    )
    attachment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attachments.id", ondelete="CASCADE"),
        nullable=False,
    )
    visibility: Mapped[str] = mapped_column(
        String(20), nullable=False, default="PUBLISHED"
    )


class AnnouncementReadORM(UUIDPrimaryKeyMixin, Base):
    """Per-user read receipt — minimal read-state, not a notification system
    (post-login unread-redirect milestone). One row per (announcement, user);
    ``read_at`` is set once, on first mark-read (idempotent — see
    AnnouncementRepository.mark_read's ON CONFLICT DO NOTHING).

    ``user_id`` intentionally has no FK — same convention as AuditUserMixin /
    ``announcements.published_by`` (actor reference, not a structural join):
    read history must survive user soft-delete, and a JWT principal is not
    guaranteed to have a backing ``users`` row (Mode A test tokens included).
    """

    __tablename__ = "announcement_reads"
    __table_args__ = (
        UniqueConstraint("announcement_id", "user_id", name="uq_announcement_reads_pair"),
        Index("ix_announcement_reads_announcement_id", "announcement_id"),
        Index("ix_announcement_reads_user_id", "user_id"),
    )

    announcement_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("announcements.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    read_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
