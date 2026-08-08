"""Shared row-visibility classes (DEC-024 pattern) for Mode A lab lists.

Permission gate remains separate (e.g. ``complaints:read``). This module only
decides which rows a principal may see.

Used by CAP-008 Case list and CM Batch-1 Aggregate list. Pusat handler
predicate for complaints (escalated / HQ-accepted) is applied by the caller —
Case list still filters PUSAT by owning unit codes only until API-520.
"""

from __future__ import annotations

from enum import StrEnum

from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal

# Lab / Mode A Pusat unit codes (owning_unit_id). Canonical preference: "PUSAT".
DEFAULT_PUSAT_UNIT_CODES: frozenset[str] = frozenset(
    {"PUSAT", "HO", "HEAD_OFFICE", "HEAD-OFFICE"}
)

_ADMIN_ROLES: frozenset[str] = frozenset(
    {"ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"}
)
_UNIT_ROLES: frozenset[str] = frozenset(
    {"SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER"}
)
_AGENT_ROLES: frozenset[str] = frozenset(
    {"AGENT", "CS_AGENT", "HANDLER", "BRANCH_OFFICER"}
)
# Head-office operational roles (not admin). Visibility = PUSAT class
# (owning unit Pusat and/or escalated work — caller applies domain predicate).
_PUSAT_HANDLER_ROLES: frozenset[str] = frozenset(
    {
        "HO_SCHEDULER",
        "HEAD_OFFICE_SCHEDULER",
        "SCHEDULER",
        "HO_ENGINEER",
        "HEAD_OFFICE_ENGINEER",
    }
)


class VisibilityClass(StrEnum):
    SELF = "SELF"
    UNIT = "UNIT"
    PUSAT = "PUSAT"
    ALL = "ALL"


# Backward-compatible alias for Case module / existing tests.
CaseVisibilityClass = VisibilityClass


def is_pusat_unit(org_unit_id: str | None) -> bool:
    normalized = OrgUnitResolver.normalize(org_unit_id)
    if not normalized:
        return False
    return normalized.upper() in DEFAULT_PUSAT_UNIT_CODES


def resolve_row_visibility(principal: Principal) -> VisibilityClass:
    """Map principal roles + org to a visibility class (DEC-024 + HO handlers)."""
    if principal.has_any_role(*_ADMIN_ROLES):
        return VisibilityClass.ALL

    if principal.has_any_role(*_PUSAT_HANDLER_ROLES):
        return VisibilityClass.PUSAT

    if principal.has_any_role(*_UNIT_ROLES):
        if is_pusat_unit(principal.org_unit_id):
            return VisibilityClass.PUSAT
        return VisibilityClass.UNIT

    if principal.has_any_role(*_AGENT_ROLES):
        return VisibilityClass.SELF

    # Default deny-broad: treat as SELF (only own creates) rather than ALL
    return VisibilityClass.SELF


def resolve_case_visibility(principal: Principal) -> VisibilityClass:
    """Alias retained for CAP-008 / DEC-024 call sites."""
    return resolve_row_visibility(principal)


def complaint_visible_for_pusat(
    *,
    owning_unit_id: str | None,
    intake_disposition: str | None,
    hq_accepted_at: object | None,
    pusat_unit_codes: frozenset[str] = DEFAULT_PUSAT_UNIT_CODES,
) -> bool:
    """DEC-024 OQ-2 / workshop F4 handler queue for Aggregate complaints.

    Visible when owned by Pusat **or** escalation approved **or** HQ accepted.
    Pending branch-internal escalations are not visible to Pusat handlers.
    """
    unit = OrgUnitResolver.normalize(owning_unit_id)
    if unit and unit.upper() in {c.upper() for c in pusat_unit_codes}:
        return True
    disp = (intake_disposition or "").strip().upper()
    if disp == "ESCALATE_APPROVED":
        return True
    return hq_accepted_at is not None
