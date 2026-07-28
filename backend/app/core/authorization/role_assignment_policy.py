"""Role assignment policy (UAT-020) — privilege escalation guard.

Centralized allow-list of which role *families* a caller may assign.
Aliases (e.g. AGENT ↔ OFFICER, BRANCH_SUPERVISOR ↔ SUPERVISOR) map to
families so business rules are not scattered as raw code strings.

Server-side only — never trust the frontend.
"""

from __future__ import annotations

from collections.abc import Iterable

from app.core.errors import ForbiddenError

# Canonical family ← concrete role codes (seed / legacy aliases).
_ROLE_FAMILY_BY_CODE: dict[str, str] = {
    "ADMIN": "ADMIN",
    "ADMINISTRATOR": "ADMIN",
    "SUPER_ADMIN": "ADMIN",
    "SUPERVISOR": "SUPERVISOR",
    "BRANCH_SUPERVISOR": "SUPERVISOR",
    "AGENT": "OFFICER",
    "CS_AGENT": "OFFICER",
    "HANDLER": "OFFICER",
    "BRANCH_OFFICER": "OFFICER",
    "VIEWER": "VIEWER",
    "HO_SCHEDULER": "HO_SCHEDULER",
    "HEAD_OFFICE_SCHEDULER": "HO_SCHEDULER",
    "SCHEDULER": "HO_SCHEDULER",
    "HO_ENGINEER": "HO_ENGINEER",
    "HEAD_OFFICE_ENGINEER": "HO_ENGINEER",
}

# Caller family → families they may assign (explicit allow-list).
# SUPERVISOR may assign OFFICER only — not ADMIN and not peer SUPERVISOR.
_ASSIGNABLE_FAMILIES: dict[str, frozenset[str]] = {
    "ADMIN": frozenset(
        {
            "ADMIN",
            "SUPERVISOR",
            "OFFICER",
            "VIEWER",
            "HO_SCHEDULER",
            "HO_ENGINEER",
        }
    ),
    "SUPERVISOR": frozenset({"OFFICER"}),
    "OFFICER": frozenset(),
    "VIEWER": frozenset(),
    "HO_SCHEDULER": frozenset(),
    "HO_ENGINEER": frozenset(),
}


def role_family(role_code: str | None) -> str | None:
    """Map a concrete role code to its policy family, or None if unknown."""
    if not role_code:
        return None
    return _ROLE_FAMILY_BY_CODE.get(role_code.strip().upper())


def assignable_role_families(actor_role_codes: Iterable[str]) -> frozenset[str]:
    """Union of families the actor may assign, based on their own roles."""
    allowed: set[str] = set()
    for code in actor_role_codes:
        family = role_family(code)
        if family is None:
            continue
        allowed |= _ASSIGNABLE_FAMILIES.get(family, frozenset())
    return frozenset(allowed)


def can_assign_role(
    actor_role_codes: Iterable[str],
    target_role_code: str | None,
) -> bool:
    """True iff the actor may assign ``target_role_code`` under policy."""
    target_family = role_family(target_role_code)
    if target_family is None:
        return False
    return target_family in assignable_role_families(actor_role_codes)


def assert_can_assign_role(
    actor_role_codes: Iterable[str],
    target_role_code: str | None,
    *,
    target_role_id: str | None = None,
) -> None:
    """Raise 403 Forbidden when the assignment would escalate privilege."""
    if can_assign_role(actor_role_codes, target_role_code):
        return
    details: dict[str, object] = {
        "targetRoleCode": target_role_code,
        "actorRoles": sorted({c.upper() for c in actor_role_codes}),
    }
    if target_role_id is not None:
        details["targetRoleId"] = target_role_id
    raise ForbiddenError(
        "Not allowed to assign this role",
        details=details,
    )
