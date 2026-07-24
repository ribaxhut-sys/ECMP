"""Data Scope persistence repository (TASK-037)."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.iam.data_scope.models import DataScope
from app.modules.iam.role.models import Role


class DataScopeRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_role(self, role_id: uuid.UUID) -> Role | None:
        return self._session.scalar(
            select(Role).where(Role.id == role_id, Role.deleted_at.is_(None))
        )

    def get_by_id(self, scope_id: uuid.UUID) -> DataScope | None:
        return self._session.scalar(
            select(DataScope).where(DataScope.id == scope_id)
        )

    def get_by_key(
        self,
        role_id: uuid.UUID,
        scope_type: str,
        scope_value: str | None,
    ) -> DataScope | None:
        stmt = select(DataScope).where(
            DataScope.role_id == role_id,
            DataScope.scope_type == scope_type,
        )
        if scope_value is None:
            stmt = stmt.where(DataScope.scope_value.is_(None))
        else:
            stmt = stmt.where(DataScope.scope_value == scope_value)
        return self._session.scalar(stmt)

    def list(
        self,
        *,
        role_id: uuid.UUID | None = None,
        scope_type: str | None = None,
    ) -> list[DataScope]:
        stmt = select(DataScope).order_by(
            DataScope.role_id.asc(),
            DataScope.scope_type.asc(),
            DataScope.scope_value.asc().nullsfirst(),
        )
        if role_id is not None:
            stmt = stmt.where(DataScope.role_id == role_id)
        if scope_type is not None:
            stmt = stmt.where(DataScope.scope_type == scope_type)
        return list(self._session.scalars(stmt).all())

    def list_for_role(self, role_id: uuid.UUID) -> list[DataScope]:
        return self.list(role_id=role_id)

    def add(self, row: DataScope) -> DataScope:
        self._session.add(row)
        self._session.flush()
        return row

    def delete(self, row: DataScope) -> None:
        self._session.delete(row)
        self._session.flush()

    def delete_all_for_role(self, role_id: uuid.UUID) -> int:
        result = self._session.execute(
            delete(DataScope).where(DataScope.role_id == role_id)
        )
        self._session.flush()
        return int(result.rowcount or 0)

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
