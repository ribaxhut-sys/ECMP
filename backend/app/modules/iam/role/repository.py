"""Role Management persistence repository (TASK-033)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.iam.role.models import Role


class RoleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, role_id: uuid.UUID) -> Role | None:
        return self._session.scalar(
            select(Role).where(Role.id == role_id, Role.deleted_at.is_(None))
        )

    def get_by_code(self, code: str) -> Role | None:
        return self._session.scalar(
            select(Role).where(Role.code == code, Role.deleted_at.is_(None))
        )

    def list(
        self,
        *,
        active_only: bool = False,
        include_system: bool = True,
    ) -> list[Role]:
        stmt = select(Role).where(Role.deleted_at.is_(None)).order_by(Role.code.asc())
        if active_only:
            stmt = stmt.where(Role.is_active.is_(True))
        if not include_system:
            stmt = stmt.where(Role.is_system.is_(False))
        return list(self._session.scalars(stmt).all())

    def add(self, row: Role) -> Role:
        self._session.add(row)
        self._session.flush()
        return row

    def soft_delete(self, row: Role) -> Role:
        """Soft-delete via deleted_at (+ deactivate). System roles rejected in service."""
        now = datetime.now(UTC)
        row.deleted_at = now
        row.is_active = False
        row.updated_at = now
        self._session.flush()
        return row

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
