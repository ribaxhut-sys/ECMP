"""Permission Management persistence repository (TASK-034)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.iam.permission.models import Permission


class PermissionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, permission_id: uuid.UUID) -> Permission | None:
        return self._session.scalar(
            select(Permission).where(
                Permission.id == permission_id,
                Permission.deleted_at.is_(None),
            )
        )

    def get_by_code(self, code: str) -> Permission | None:
        return self._session.scalar(
            select(Permission).where(
                Permission.code == code,
                Permission.deleted_at.is_(None),
            )
        )

    def list(
        self,
        *,
        active_only: bool = False,
        include_system: bool = True,
        module: str | None = None,
    ) -> list[Permission]:
        stmt = (
            select(Permission)
            .where(Permission.deleted_at.is_(None))
            .order_by(Permission.module.asc(), Permission.code.asc())
        )
        if active_only:
            stmt = stmt.where(Permission.is_active.is_(True))
        if not include_system:
            stmt = stmt.where(Permission.is_system.is_(False))
        if module:
            stmt = stmt.where(Permission.module == module)
        return list(self._session.scalars(stmt).all())

    def add(self, row: Permission) -> Permission:
        self._session.add(row)
        self._session.flush()
        return row

    def soft_delete(self, row: Permission) -> Permission:
        """Soft-delete via deleted_at (+ deactivate). System rows rejected in service."""
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
