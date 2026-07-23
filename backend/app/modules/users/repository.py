"""User persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models import Branch, Role, User


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = select(User).where(User.id == user_id, User.deleted_at.is_(None))
        return self._session.scalar(stmt)

    def username_exists(
        self, username: str, *, exclude_user_id: uuid.UUID | None = None
    ) -> bool:
        filters = [User.username == username, User.deleted_at.is_(None)]
        if exclude_user_id is not None:
            filters.append(User.id != exclude_user_id)
        stmt = select(User.id).where(*filters)
        return self._session.scalar(stmt) is not None

    def email_exists(
        self, email: str, *, exclude_user_id: uuid.UUID | None = None
    ) -> bool:
        filters = [User.email == email, User.deleted_at.is_(None)]
        if exclude_user_id is not None:
            filters.append(User.id != exclude_user_id)
        stmt = select(User.id).where(*filters)
        return self._session.scalar(stmt) is not None

    def role_exists(self, role_id: uuid.UUID) -> bool:
        stmt = select(Role.id).where(
            Role.id == role_id,
            Role.deleted_at.is_(None),
            Role.is_active.is_(True),
        )
        return self._session.scalar(stmt) is not None

    def branch_exists(self, branch_id: uuid.UUID) -> bool:
        stmt = select(Branch.id).where(
            Branch.id == branch_id,
            Branch.deleted_at.is_(None),
            Branch.is_active.is_(True),
        )
        return self._session.scalar(stmt) is not None

    def add(self, user: User) -> User:
        self._session.add(user)
        self._session.flush()
        return user

    def list_page(
        self,
        *,
        page: int,
        page_size: int,
        is_active: bool | None = None,
        role_id: uuid.UUID | None = None,
        branch_id: uuid.UUID | None = None,
    ) -> tuple[list[User], int]:
        filters = [User.deleted_at.is_(None)]
        if is_active is not None:
            filters.append(User.is_active.is_(is_active))
        if role_id is not None:
            filters.append(User.role_id == role_id)
        if branch_id is not None:
            filters.append(User.branch_id == branch_id)

        count_stmt = select(func.count()).select_from(User).where(*filters)
        total = int(self._session.scalar(count_stmt) or 0)

        stmt: Select[tuple[User]] = (
            select(User)
            .where(*filters)
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self._session.scalars(stmt).all()), total

    def commit(self) -> None:
        self._session.commit()

    def refresh(self, user: User) -> User:
        self._session.refresh(user)
        return user
