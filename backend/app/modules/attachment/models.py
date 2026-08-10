"""CAPABILITY-011 Attachment ORM — generic aggregate-bound metadata."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDPrimaryKeyMixin


class AttachmentORM(UUIDPrimaryKeyMixin, Base):
    """Persisted attachment metadata; bytes live behind StorageProvider."""

    __tablename__ = "attachments"
    __table_args__ = (
        Index("ix_attachments_aggregate_type", "aggregate_type"),
        Index("ix_attachments_aggregate_id", "aggregate_id"),
        Index("ix_attachments_uploaded_at", "uploaded_at"),
        Index("ix_attachments_checksum_sha256", "checksum_sha256"),
        Index(
            "ix_attachments_aggregate",
            "aggregate_type",
            "aggregate_id",
        ),
        Index("ix_attachments_uploaded_by", "uploaded_by"),
        Index("ix_attachments_status", "status"),
        Index("ix_attachments_file_name", "file_name"),
    )

    aggregate_type: Mapped[str] = mapped_column(String(50), nullable=False)
    aggregate_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    extension: Mapped[str | None] = mapped_column(String(20), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    checksum_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    # Announcement catalog only (NULL for Complaint/Queue/Notification).
    # Orthogonal to announcement_attachments.visibility (IMMEDIATE/PUBLISHED).
    access_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    uploaded_org_unit_id: Mapped[str | None] = mapped_column(String(64), nullable=True)


# Backward-compatible alias used by ``app.models`` and existing imports.
Attachment = AttachmentORM
