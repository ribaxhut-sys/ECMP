"""Authenticated caller identity (Authorization Middleware — TASK-040)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Principal:
    """Authenticated caller identity (JWT claims + resolved permissions)."""

    user_id: uuid.UUID
    roles: tuple[str, ...] = ()
    permissions: frozenset[str] = field(default_factory=frozenset)
    force_password_change: bool = False
    sid: str | None = None
    org_unit_id: str | None = None

    def has_permission(self, permission: str) -> bool:
        return "*" in self.permissions or permission in self.permissions

    def has_any_role(self, *roles: str) -> bool:
        mine = {role.upper() for role in self.roles}
        return bool(mine & {role.upper() for role in roles})
