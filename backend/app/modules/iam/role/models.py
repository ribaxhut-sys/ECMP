"""Role ORM model (TASK-033).

Extends the existing ``roles`` foundation table with ``is_system``.
User assignment / permission matrix remain out of scope.
"""

from __future__ import annotations

from sqlalchemy import Boolean, Index, String, Text, UniqueConstraint, false, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampAuditSoftDeleteMixin


class Role(TimestampAuditSoftDeleteMixin, Base):
    """Platform role master (code + display metadata)."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("code", name="uq_roles_code"),
        Index("ix_roles_is_active", "is_active"),
        Index("ix_roles_is_system", "is_system"),
    )

    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    users: Mapped[list["User"]] = relationship(back_populates="role")
