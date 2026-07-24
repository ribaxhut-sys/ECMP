"""Generic Attachment ORM model (TASK-029).

Polymorphic association via object_type + object_id.
Not owned by Complaint or any single domain.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, SoftDeleteMixin, UUIDPrimaryKeyMixin


class Attachment(UUIDPrimaryKeyMixin, SoftDeleteMixin, Base):
    """Platform attachment metadata; bytes live behind StorageProvider."""

    __tablename__ = "attachments"
    __table_args__ = (
        Index("ix_attachments_object", "object_type", "object_id"),
        Index("ix_attachments_uploaded_by", "uploaded_by"),
        Index("ix_attachments_checksum", "checksum"),
        Index("ix_attachments_stored_filename", "stored_filename"),
    )

    object_type: Mapped[str] = mapped_column(String(50), nullable=False)
    object_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    extension: Mapped[str | None] = mapped_column(String(20), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_provider: Mapped[str] = mapped_column(String(50), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
