"""Role-Permission Matrix persistence repository (TASK-035)."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.iam.permission.models import Permission
from app.modules.iam.role.models import Role
from app.modules.iam.role_permission.models import RolePermission


class RolePermissionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_role(self, role_id: uuid.UUID) -> Role | None:
        return self._session.scalar(
            select(Role).where(Role.id == role_id, Role.deleted_at.is_(None))
        )

    def get_permission(self, permission_id: uuid.UUID) -> Permission | None:
        return self._session.scalar(
            select(Permission).where(
                Permission.id == permission_id,
                Permission.deleted_at.is_(None),
            )
        )

    def get_permissions_by_ids(
        self, permission_ids: list[uuid.UUID]
    ) -> list[Permission]:
        if not permission_ids:
            return []
        return list(
            self._session.scalars(
                select(Permission).where(
                    Permission.id.in_(permission_ids),
                    Permission.deleted_at.is_(None),
                )
            ).all()
        )

    def list_permissions_for_role(self, role_id: uuid.UUID) -> list[Permission]:
        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(
                RolePermission.role_id == role_id,
                Permission.deleted_at.is_(None),
            )
            .order_by(Permission.module.asc(), Permission.code.asc())
        )
        return list(self._session.scalars(stmt).all())

    def list_roles_for_permission(self, permission_id: uuid.UUID) -> list[Role]:
        stmt = (
            select(Role)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .where(
                RolePermission.permission_id == permission_id,
                Role.deleted_at.is_(None),
            )
            .order_by(Role.code.asc())
        )
        return list(self._session.scalars(stmt).all())

    def get_link(
        self, role_id: uuid.UUID, permission_id: uuid.UUID
    ) -> RolePermission | None:
        return self._session.scalar(
            select(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id,
            )
        )

    def list_links_for_role(self, role_id: uuid.UUID) -> list[RolePermission]:
        return list(
            self._session.scalars(
                select(RolePermission).where(RolePermission.role_id == role_id)
            ).all()
        )

    def add_link(self, row: RolePermission) -> RolePermission:
        self._session.add(row)
        self._session.flush()
        return row

    def delete_link(self, row: RolePermission) -> None:
        self._session.delete(row)
        self._session.flush()

    def delete_links_for_role(
        self, role_id: uuid.UUID, permission_ids: set[uuid.UUID]
    ) -> int:
        if not permission_ids:
            return 0
        result = self._session.execute(
            delete(RolePermission).where(
                RolePermission.role_id == role_id,
                RolePermission.permission_id.in_(permission_ids),
            )
        )
        self._session.flush()
        return int(result.rowcount or 0)

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
