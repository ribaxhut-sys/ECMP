"""Data Scope Resolver (TASK-039).

Resolution path:

    User → UserRole → Role → DataScope → EffectiveScope

Provides Authorization Layer helpers for endpoints to call.
Does not auto-filter complaint/domain queries.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.iam.data_scope.models import DataScope, ScopeType
from app.modules.iam.permission_cache import (
    UserScopedTtlCache,
    get_data_scope_cache,
)
from app.modules.iam.role.models import Role
from app.modules.iam.user_role.models import UserRole


@dataclass(frozen=True, slots=True)
class EffectiveScope:
    """Union of data scopes across all active roles for a user."""

    entries: frozenset[tuple[str, str | None]]

    @property
    def scope_types(self) -> frozenset[str]:
        return frozenset(scope_type for scope_type, _ in self.entries)

    def has_global(self) -> bool:
        return ScopeType.GLOBAL.value in self.scope_types

    def get_branches(self) -> frozenset[str]:
        return frozenset(
            value
            for scope_type, value in self.entries
            if scope_type == ScopeType.BRANCH.value and value
        )

    def get_organizations(self) -> frozenset[str]:
        return frozenset(
            value
            for scope_type, value in self.entries
            if scope_type == ScopeType.ORGANIZATION.value and value
        )

    def get_custom_values(self) -> frozenset[str]:
        return frozenset(
            value
            for scope_type, value in self.entries
            if scope_type == ScopeType.CUSTOM.value and value
        )

    def is_self_only(self) -> bool:
        """True when access is SELF-restricted (no GLOBAL / BRANCH / ORG / CUSTOM)."""
        if ScopeType.SELF.value not in self.scope_types:
            return False
        expanding = {
            ScopeType.GLOBAL.value,
            ScopeType.BRANCH.value,
            ScopeType.ORGANIZATION.value,
            ScopeType.CUSTOM.value,
        }
        return not (self.scope_types & expanding)

    def has_type(self, scope_type: ScopeType | str) -> bool:
        return ScopeType(scope_type).value in self.scope_types


class DataScopeResolver:
    """Resolve effective data scopes for a user from IAM junction tables."""

    def __init__(
        self,
        session: Session,
        cache: UserScopedTtlCache[object] | None = None,
    ) -> None:
        self._session = session
        self._cache = cache if cache is not None else get_data_scope_cache()

    def resolve_scopes(self, user_id: uuid.UUID) -> EffectiveScope:
        cached = self._cache.get(user_id)
        if isinstance(cached, EffectiveScope):
            return cached

        scope = self._load_from_db(user_id)
        self._cache.set(user_id, scope)
        return scope

    def has_global_scope(self, user_id: uuid.UUID) -> bool:
        return self.resolve_scopes(user_id).has_global()

    def get_branches(self, user_id: uuid.UUID) -> frozenset[str]:
        return self.resolve_scopes(user_id).get_branches()

    def get_organizations(self, user_id: uuid.UUID) -> frozenset[str]:
        return self.resolve_scopes(user_id).get_organizations()

    def is_self_only(self, user_id: uuid.UUID) -> bool:
        return self.resolve_scopes(user_id).is_self_only()

    def invalidate(self, user_id: uuid.UUID) -> None:
        self._cache.invalidate(user_id)

    def invalidate_all(self) -> None:
        self._cache.invalidate_all()

    def _load_from_db(self, user_id: uuid.UUID) -> EffectiveScope:
        stmt = (
            select(DataScope.scope_type, DataScope.scope_value)
            .join(Role, Role.id == DataScope.role_id)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == user_id,
                Role.deleted_at.is_(None),
                Role.is_active.is_(True),
            )
            .distinct()
        )
        rows = self._session.execute(stmt).all()
        entries = frozenset(
            (str(scope_type), scope_value if scope_value is None else str(scope_value))
            for scope_type, scope_value in rows
        )
        return EffectiveScope(entries=entries)
