"""DEC-024 Case list visibility classes (Mode A lab).

Permission gate is separate (`complaints:read`). This module only decides
which rows a principal may see.
"""

from __future__ import annotations

from enum import StrEnum

from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal

# Lab / Mode A Pusat unit codes (owning_unit_id). Escalation path lands later (API-520).
DEFAULT_PUSAT_UNIT_CODES: frozenset[str] = frozenset(
    {"PUSAT", "HO", "HEAD_OFFICE", "HEAD-OFFICE"}
)

_ADMIN_ROLES: frozenset[str] = frozenset(
    {"ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"}
)
_UNIT_ROLES: frozenset[str] = frozenset(
    {"SUPERVISOR", "BRANCH_SUPERVISOR"}
)
_AGENT_ROLES: frozenset[str] = frozenset(
    {"AGENT", "CS_AGENT", "HANDLER", "BRANCH_OFFICER"}
)


class CaseVisibilityClass(StrEnum):
    SELF = "SELF"
    UNIT = "UNIT"
    PUSAT = "PUSAT"
    ALL = "ALL"


def is_pusat_unit(org_unit_id: str | None) -> bool:
    normalized = OrgUnitResolver.normalize(org_unit_id)
    if not normalized:
        return False
    return normalized.upper() in DEFAULT_PUSAT_UNIT_CODES


def resolve_case_visibility(principal: Principal) -> CaseVisibilityClass:
    """Map principal roles + org to DEC-024 visibility class."""
    if principal.has_any_role(*_ADMIN_ROLES):
        return CaseVisibilityClass.ALL

    if principal.has_any_role(*_UNIT_ROLES):
        if is_pusat_unit(principal.org_unit_id):
            return CaseVisibilityClass.PUSAT
        # Branch supervisor/manager without org → empty UNIT result (fail closed)
        return CaseVisibilityClass.UNIT

    if principal.has_any_role(*_AGENT_ROLES):
        return CaseVisibilityClass.SELF

    # Default deny-broad: treat as SELF (only own creates) rather than ALL
    return CaseVisibilityClass.SELF
