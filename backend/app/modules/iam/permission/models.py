"""Permission ORM model (TASK-034).

Master catalog of application permissions. Role matrix binding remains
out of scope.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint, false, true
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampAuditSoftDeleteMixin


class Permission(TimestampAuditSoftDeleteMixin, Base):
    """Platform permission master (code = module:action)."""

    __tablename__ = "permissions"
    __table_args__ = (
        UniqueConstraint("code", name="uq_permissions_code"),
        Index("ix_permissions_module", "module"),
        Index("ix_permissions_is_active", "is_active"),
        Index("ix_permissions_is_system", "is_system"),
    )

    code: Mapped[str] = mapped_column(String(150), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    module: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
