"""SQLAlchemy ORM for Pengetahuan (Knowledge Module).

Flat module (mirrors app.modules.announcement) — no separate DDD layering
needed for a single-aggregate content record. Reuses TimestampAuditSoftDeleteMixin
for created_at/updated_at/deleted_at/created_by/updated_by so audit columns
match the rest of ECMP v1.0 (no bespoke audit system).

Business decision (LOCKED, ECMP — Business & Domain Design: Modul Pengetahuan):
  - Versioning: a new version is a new Knowledge record (``supersedes_knowledge_id``
    points to the prior record) — no ``knowledge_versions`` table.
  - Lifecycle: DRAFT -> ACTIVE -> ARCHIVED. No EXPIRED status column — expiry is
    derived at read time from effective_from/effective_to (mirrors how
    announcements derive SCHEDULED/EXPIRED — see catalog reasoning in
    app.modules.announcement.repository.is_scheduled_announcement).
  - Files: 0..N source files via the ``knowledge_files`` join table onto the
    existing generic ``attachments`` table (CAPABILITY-011) — same relation
    shape as ``announcement_attachments``. Exactly one file may hold role
    PRIMARY (enforced by a partial unique index).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import (
    AuditUserMixin,
    Base,
    TimestampAuditSoftDeleteMixin,
    TimestampMixin,
    UUIDPrimaryKeyMixin,
)

# Business decision (LOCKED) — five values, no "LAINNYA"/"OTHER" fallback.
KNOWLEDGE_TYPES = ("SOP", "PERATURAN", "SURAT_EDARAN", "KEPUTUSAN", "PANDUAN")
KNOWLEDGE_STATUSES = ("DRAFT", "ACTIVE", "ARCHIVED")
KNOWLEDGE_FILE_ROLES = ("PRIMARY", "SUPPORTING")


class KnowledgeORM(TimestampAuditSoftDeleteMixin, Base):
    """A controlled record of one organizational rule/procedure.

    ``owner_org_unit_id`` is provenance only (Pengetahuan v1 is global-read,
    Pusat-curated — see gates.principal_may_manage_knowledge); it does not
    narrow who may read an ACTIVE record.
    """

    __tablename__ = "knowledge"
    __table_args__ = (
        Index("ix_knowledge_status", "status"),
        Index("ix_knowledge_knowledge_type", "knowledge_type"),
        Index("ix_knowledge_published_at", "published_at"),
        Index("ix_knowledge_supersedes_knowledge_id", "supersedes_knowledge_id"),
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    knowledge_type: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="DRAFT")

    document_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    version_label: Mapped[str | None] = mapped_column(String(32), nullable=True)

    effective_from: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    effective_to: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    owner_org_unit_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    supersedes_knowledge_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.id", ondelete="SET NULL"),
        nullable=True,
    )


class KnowledgeFileORM(UUIDPrimaryKeyMixin, TimestampMixin, AuditUserMixin, Base):
    """Join row: which platform Attachment belongs to which Knowledge, and in
    which role (PRIMARY — exactly one required for ACTIVE — or SUPPORTING).

    Pure relation + attribute — no soft-delete of its own. Removing a file
    from a Knowledge deletes this row; the underlying ``attachments`` row
    keeps its own existing soft-delete (status=DELETED) via the shared
    AttachmentService, unchanged.
    """

    __tablename__ = "knowledge_files"
    __table_args__ = (
        UniqueConstraint(
            "knowledge_id", "attachment_id", name="uq_knowledge_files_pair"
        ),
        Index("ix_knowledge_files_knowledge_id", "knowledge_id"),
        Index("ix_knowledge_files_attachment_id", "attachment_id"),
        # At most one PRIMARY file per Knowledge — DB-level guarantee.
        Index(
            "uq_knowledge_files_one_primary",
            "knowledge_id",
            unique=True,
            postgresql_where=text("role = 'PRIMARY'"),
        ),
    )

    knowledge_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("knowledge.id", ondelete="CASCADE"),
        nullable=False,
    )
    attachment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("attachments.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, default="SUPPORTING"
    )
