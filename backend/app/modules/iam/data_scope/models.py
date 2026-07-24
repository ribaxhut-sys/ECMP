"""DataScope ORM model and scope type enum (TASK-037)."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ScopeType(StrEnum):
    """Supported data scope types (foundation set)."""

    GLOBAL = "GLOBAL"
    ORGANIZATION = "ORGANIZATION"
    BRANCH = "BRANCH"
    SELF = "SELF"
    CUSTOM = "CUSTOM"


_SCOPES_WITHOUT_VALUE = frozenset({ScopeType.GLOBAL, ScopeType.SELF})
_SCOPES_WITH_VALUE = frozenset(
    {ScopeType.ORGANIZATION, ScopeType.BRANCH, ScopeType.CUSTOM}
)


def scope_requires_value(scope_type: ScopeType | str) -> bool:
    return ScopeType(scope_type) in _SCOPES_WITH_VALUE


def scope_forbids_value(scope_type: ScopeType | str) -> bool:
    return ScopeType(scope_type) in _SCOPES_WITHOUT_VALUE


class DataScope(Base):
    """Data access scope bound to a role."""

    __tablename__ = "data_scopes"
    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "scope_type",
            "scope_value",
            name="uq_data_scopes_role_id_scope_type_scope_value",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    scope_type: Mapped[str] = mapped_column(String(50), nullable=False)
    scope_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
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
