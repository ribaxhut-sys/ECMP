"""User persistence repository (SQLAlchemy 2.x)."""

from __future__ import annotations

import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session, joinedload

from app.models import Branch, Role, User, UserRole


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        stmt = (
            select(User)
            .options(joinedload(User.role))
            .where(User.id == user_id, User.deleted_at.is_(None))
        )
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

    def get_role_code(self, role_id: uuid.UUID) -> str | None:
        stmt = select(Role.code).where(
            Role.id == role_id,
            Role.deleted_at.is_(None),
            Role.is_active.is_(True),
        )
        code = self._session.scalar(stmt)
        return str(code) if code is not None else None

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

    def get_user_role_link(
        self, user_id: uuid.UUID, role_id: uuid.UUID
    ) -> UserRole | None:
        return self._session.scalar(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )

    def ensure_user_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Insert user_roles(user_id, role_id) if missing. Returns True if inserted."""
        if self.get_user_role_link(user_id, role_id) is not None:
            return False
        self._session.add(
            UserRole(id=uuid.uuid4(), user_id=user_id, role_id=role_id)
        )
        self._session.flush()
        return True

    def remove_user_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> bool:
        """Delete user_roles(user_id, role_id) if present. Returns True if deleted."""
        link = self.get_user_role_link(user_id, role_id)
        if link is None:
            return False
        self._session.delete(link)
        self._session.flush()
        return True

    def sync_primary_user_role(
        self,
        user_id: uuid.UUID,
        *,
        previous_role_id: uuid.UUID,
        new_role_id: uuid.UUID,
    ) -> None:
        """UAT-021: keep junction aligned when primary users.role_id changes.

        - Ensure ``new_role_id`` is present (idempotent).
        - Remove obsolete ``previous_role_id`` so demotion cannot leave
          elevated permissions via stale junction rows.
        - Preserve any other explicitly assigned secondary roles.
        """
        self.ensure_user_role(user_id, new_role_id)
        if previous_role_id != new_role_id:
            self.remove_user_role(user_id, previous_role_id)

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
            .options(joinedload(User.role))
            .where(*filters)
            .order_by(User.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self._session.scalars(stmt).unique().all()), total

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def refresh(self, user: User) -> User:
        self._session.refresh(user)
        # Load role for roleCode/roleName without relying on callers.
        if "role" not in user.__dict__ or user.__dict__.get("role") is None:
            role = self._session.get(Role, user.role_id)
            if role is not None:
                user.role = role
        return user
