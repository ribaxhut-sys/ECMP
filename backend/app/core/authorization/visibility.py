"""Shared row-visibility classes (DEC-024 pattern) for Mode A lab lists.

Permission gate remains separate (e.g. ``complaints:read``). This module only
decides which rows a principal may see.

Used by CAP-008 Case list and CM Batch-1 Aggregate list. Pusat handler
predicate for complaints (escalated / HQ-accepted) is applied by the caller —
Case list still filters PUSAT by owning unit codes only until API-520.
"""

from __future__ import annotations

from enum import StrEnum

from sqlalchemy import ColumnElement, func, or_

from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal

# Lab / Mode A Pusat **root** unit codes (owning_unit_id). Preference: "PUSAT".
DEFAULT_PUSAT_UNIT_CODES: frozenset[str] = frozenset(
    {"PUSAT", "HO", "HEAD_OFFICE", "HEAD-OFFICE"}
)

# Pusat is not one door: a taxpayer escalated to Pusat may arrive at CRO, at
# Sekretariat, or at a Suban. Those sub-units are coded as a root code plus a
# separator plus their own suffix — "PUSAT-CRO", "PUSAT-SUBAN-1" — so every
# read path recognizes them as Pusat without a database round-trip and pure
# domain code keeps working unchanged. The write boundary (picking a
# destination unit) additionally verifies the Branch row exists and is active.
#
# "_" is deliberately not a separator: it is a LIKE wildcard, so the SQL twin
# below would silently match unrelated codes.
_PUSAT_SUBUNIT_SEPARATORS: tuple[str, ...] = ("-", ".", "/")

_ADMIN_ROLES: frozenset[str] = frozenset(
    {"ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"}
)
_UNIT_ROLES: frozenset[str] = frozenset(
    {"SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER"}
)
_AGENT_ROLES: frozenset[str] = frozenset(
    {"AGENT", "CS_AGENT", "HANDLER", "BRANCH_OFFICER"}
)
# DEC-027: Viewer is read-only across units (no mutations — permission gate).
_VIEWER_ROLES: frozenset[str] = frozenset({"VIEWER"})
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


def is_pusat_unit(
    org_unit_id: str | None,
    *,
    pusat_unit_codes: frozenset[str] = DEFAULT_PUSAT_UNIT_CODES,
) -> bool:
    """True for a Pusat root code **or** any of its sub-units (PUSAT-CRO, …)."""
    normalized = OrgUnitResolver.normalize(org_unit_id)
    if not normalized:
        return False
    upper = normalized.upper()
    for root in (code.upper() for code in pusat_unit_codes):
        if upper == root:
            return True
        if any(
            upper.startswith(f"{root}{sep}") for sep in _PUSAT_SUBUNIT_SEPARATORS
        ):
            return True
    return False


def pusat_unit_clause(
    column: ColumnElement[str | None],
    *,
    pusat_unit_codes: frozenset[str] = DEFAULT_PUSAT_UNIT_CODES,
) -> ColumnElement[bool]:
    """SQL twin of :func:`is_pusat_unit` — keep both sides of the rule here.

    List queries cannot call the Python predicate row by row, so the same
    root-or-sub-unit rule is expressed once as a clause instead of being
    re-derived (differently) in every repository.
    """
    upper = func.upper(column)
    roots = sorted({code.upper() for code in pusat_unit_codes})
    clauses: list[ColumnElement[bool]] = [upper.in_(roots)]
    clauses.extend(
        upper.like(f"{root}{sep}%")
        for root in roots
        for sep in _PUSAT_SUBUNIT_SEPARATORS
    )
    return or_(*clauses)


def resolve_row_visibility(principal: Principal) -> VisibilityClass:
    """Map principal roles + org to a visibility class (DEC-024 + HO handlers)."""
    if principal.has_any_role(*_ADMIN_ROLES):
        return VisibilityClass.ALL

    if principal.has_any_role(*_VIEWER_ROLES):
        return VisibilityClass.ALL

    if principal.has_any_role(*_PUSAT_HANDLER_ROLES):
        return VisibilityClass.PUSAT

    if principal.has_any_role(*_UNIT_ROLES):
        if is_pusat_unit(principal.org_unit_id):
            return VisibilityClass.PUSAT
        return VisibilityClass.UNIT

    if principal.has_any_role(*_AGENT_ROLES):
        # Lab "Agent Pusat" = AGENT (branch-scoped) on unit PUSAT — same inbox
        # as HO handlers: Pusat-owned + escalations approved to Pusat (OQ-2 / BR-2).
        if is_pusat_unit(principal.org_unit_id):
            return VisibilityClass.PUSAT
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
    if is_pusat_unit(owning_unit_id, pusat_unit_codes=pusat_unit_codes):
        return True
    disp = (intake_disposition or "").strip().upper()
    if disp in {"ESCALATE_APPROVED", "HQ_SCHEDULED"}:
        return True
    return hq_accepted_at is not None
