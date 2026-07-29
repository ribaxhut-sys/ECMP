"""Dynamic Permission Resolver (TASK-038).

Resolution path:

    User → UserRole → Role → RolePermission → Permission → Set[str]

Authorization Engine reads permission codes from the database (with cache).
Data Scope filtering is out of scope.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.iam.permission.models import Permission
from app.modules.iam.permission_cache import (
    PermissionCache,
    get_permission_cache,
)
from app.modules.iam.role.models import Role
from app.modules.iam.role_permission.models import RolePermission
from app.modules.iam.user_role.models import UserRole


class PermissionResolver:
    """Resolve effective permission codes for a user from IAM junction tables."""

    def __init__(
        self,
        session: Session,
        cache: PermissionCache | None = None,
    ) -> None:
        self._session = session
        self._cache = cache if cache is not None else get_permission_cache()

    def resolve(self, user_id: uuid.UUID) -> frozenset[str]:
        cached = self._cache.get(user_id)
        if cached is not None:
            return cached

        permissions = self._load_from_db(user_id)
        self._cache.set(user_id, permissions)
        return permissions

    def resolve_for_role_codes(
        self,
        role_codes: list[str] | tuple[str, ...] | set[str],
    ) -> frozenset[str]:
        """Resolve permissions for internal role codes (jwt mode / ADR-008).

        Does not read permissions from the JWT. Unknown / empty codes yield
        an empty permission set (fail-closed).
        """
        codes = sorted(
            {
                str(code).strip().upper()
                for code in role_codes
                if code is not None and str(code).strip()
            }
        )
        if not codes:
            return frozenset()

        stmt = (
            select(Permission.code)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(Role, Role.id == RolePermission.role_id)
            .where(
                Role.code.in_(codes),
                Role.deleted_at.is_(None),
                Role.is_active.is_(True),
                Permission.deleted_at.is_(None),
                Permission.is_active.is_(True),
            )
            .distinct()
        )
        returned = self._session.scalars(stmt).all()
        return frozenset(str(code) for code in returned)

    def resolve_sorted(self, user_id: uuid.UUID) -> list[str]:
        return sorted(self.resolve(user_id))

    def invalidate(self, user_id: uuid.UUID) -> None:
        self._cache.invalidate(user_id)

    def invalidate_all(self) -> None:
        self._cache.invalidate_all()

    def _load_from_db(self, user_id: uuid.UUID) -> frozenset[str]:
        stmt = (
            select(Permission.code)
            .join(
                RolePermission,
                RolePermission.permission_id == Permission.id,
            )
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                Role.deleted_at.is_(None),
                Role.is_active.is_(True),
                Permission.deleted_at.is_(None),
                Permission.is_active.is_(True),
            )
            .distinct()
        )
        codes = self._session.scalars(stmt).all()
        return frozenset(str(code) for code in codes)
