"""F4 Case closure acceptance authorization (extends existing gates / org scope).

Does not invent a parallel permission system: callers still require
``complaints:update`` (or equivalent). This module adds party / role / unit /
creator (SoD) checks on top of that gate.
"""

from __future__ import annotations

from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.errors import PermissionDeniedError
from app.core.user_messages import m

# Mirrors visibility.py role families — Supervisor/Manager (+ Admin) may give
# final Handling Unit / Owner acceptance. Agent-family may handle and propose
# resolution only (no parallel permission catalog).
_ADMIN_ROLES: frozenset[str] = frozenset(
    {"ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"}
)
_UNIT_APPROVER_ROLES: frozenset[str] = frozenset(
    {"SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER"}
)
_AGENT_ROLES: frozenset[str] = frozenset(
    {"AGENT", "CS_AGENT", "HANDLER", "BRANCH_OFFICER"}
)
_ACCEPTANCE_APPROVER_ROLES: frozenset[str] = frozenset(
    {*_UNIT_APPROVER_ROLES, *_ADMIN_ROLES}
)


def principal_may_give_case_acceptance(principal: Principal) -> bool:
    """True when the principal's role may submit final F4 acceptance."""
    return principal.has_any_role(*_ACCEPTANCE_APPROVER_ROLES)


def principal_is_case_agent(principal: Principal) -> bool:
    """Agent-family without an overlapping approver role."""
    if principal_may_give_case_acceptance(principal):
        return False
    return principal.has_any_role(*_AGENT_ROLES)


def _ids_equal(left: str | None, right: str | None) -> bool:
    a = (left or "").strip().lower()
    b = (right or "").strip().lower()
    return bool(a) and bool(b) and a == b


def assert_case_acceptance_authorized(
    principal: Principal,
    *,
    party: str,
    owner_unit_id: str | None,
    handling_unit_id: str | None,
    actor_unit_id: str | None,
    complaint_creator_id: str | None,
) -> None:
    """Authorize F4 Handling Unit / Owner acceptance for the acting principal.

    Checks (all required):
    - role is Supervisor / Manager / Admin (not Agent);
    - actor unit matches the party unit (Owner → owner_unit_id,
      HANDLING_UNIT → current handling / owning_unit_id), unless Admin;
    - creator SoD: complaint creator cannot be the sole approver for either
      party (single acceptance pointer per party ⇒ creator cannot approve).
    """
    party_key = (party or "").strip().upper()
    if party_key not in {"OWNER", "HANDLING_UNIT"}:
        raise PermissionDeniedError(m("case.acceptance_party_invalid"))

    if not principal_may_give_case_acceptance(principal):
        raise PermissionDeniedError(m("case.acceptance_role_denied"))

    if _ids_equal(str(principal.user_id), complaint_creator_id):
        raise PermissionDeniedError(m("case.acceptance_creator_conflict"))

    if principal.has_any_role(*_ADMIN_ROLES):
        return

    actor_unit = OrgUnitResolver.normalize(actor_unit_id)
    if party_key == "OWNER":
        required = OrgUnitResolver.normalize(owner_unit_id)
        if not required or actor_unit != required:
            raise PermissionDeniedError(m("case.acceptance_owner_unit_mismatch"))
        return

    required = OrgUnitResolver.normalize(handling_unit_id)
    if not required or actor_unit != required:
        raise PermissionDeniedError(m("case.acceptance_handling_unit_mismatch"))


def assert_case_resolve_accept_authorized(
    principal: Principal,
    *,
    handling_unit_id: str | None,
    actor_unit_id: str | None,
    complaint_creator_id: str | None,
) -> None:
    """Authorize resolve action=ACCEPT (stamps Handling Unit acceptance).

    Agent may PROPOSE only. ACCEPT is final HU agreement and follows the same
    role / unit / SoD rules as party=HANDLING_UNIT acceptance.
    """
    if principal_is_case_agent(principal):
        raise PermissionDeniedError(m("case.resolve_accept_role_denied"))
    assert_case_acceptance_authorized(
        principal,
        party="HANDLING_UNIT",
        owner_unit_id=None,
        handling_unit_id=handling_unit_id,
        actor_unit_id=actor_unit_id,
        complaint_creator_id=complaint_creator_id,
    )
