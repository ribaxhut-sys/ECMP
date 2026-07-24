"""User-Role Assignment persistence repository (TASK-036)."""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, joinedload

from app.models import User
from app.modules.iam.role.models import Role
from app.modules.iam.user_role.models import UserRole


class UserRoleRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_user(self, user_id: uuid.UUID) -> User | None:
        return self._session.scalar(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )

    def get_role(self, role_id: uuid.UUID) -> Role | None:
        return self._session.scalar(
            select(Role).where(Role.id == role_id, Role.deleted_at.is_(None))
        )

    def get_roles_by_ids(self, role_ids: list[uuid.UUID]) -> list[Role]:
        if not role_ids:
            return []
        return list(
            self._session.scalars(
                select(Role).where(
                    Role.id.in_(role_ids),
                    Role.deleted_at.is_(None),
                )
            ).all()
        )

    def list_roles_for_user(self, user_id: uuid.UUID) -> list[Role]:
        stmt = (
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                Role.deleted_at.is_(None),
            )
            .order_by(Role.code.asc())
        )
        return list(self._session.scalars(stmt).all())

    def list_users_for_role(self, role_id: uuid.UUID) -> list[User]:
        stmt = (
            select(User)
            .options(joinedload(User.role))
            .join(UserRole, UserRole.user_id == User.id)
            .where(
                UserRole.role_id == role_id,
                User.deleted_at.is_(None),
            )
            .order_by(User.username.asc())
        )
        return list(self._session.scalars(stmt).unique().all())

    def get_link(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole | None:
        return self._session.scalar(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )

    def list_links_for_user(self, user_id: uuid.UUID) -> list[UserRole]:
        return list(
            self._session.scalars(
                select(UserRole).where(UserRole.user_id == user_id)
            ).all()
        )

    def add_link(self, row: UserRole) -> UserRole:
        self._session.add(row)
        self._session.flush()
        return row

    def delete_link(self, row: UserRole) -> None:
        self._session.delete(row)
        self._session.flush()

    def delete_links_for_user(
        self, user_id: uuid.UUID, role_ids: set[uuid.UUID]
    ) -> int:
        if not role_ids:
            return 0
        result = self._session.execute(
            delete(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id.in_(role_ids),
            )
        )
        self._session.flush()
        return int(result.rowcount or 0)

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
