"""F4 Case closure acceptance authorization (extends existing gates / org scope).

Does not invent a parallel permission system: callers still require
``complaints:update`` (or equivalent). This module adds party / role / unit /
creator (SoD) checks on top of that gate.

Mode A product policy (2026-08-12): Agent-family may complete Handling Unit /
Owner acceptance **on their own unit** (actor unit == party unit). Cross-unit
ACCEPT remains Supervisor/Manager/Admin.

Mode A product policy (2026-08-19): Creator SoD is only enforced when the
approver is acting on a unit other than their own. Agent-family (as before)
and Supervisor/Manager acting on their own unit may accept/close a case they
authored themselves — a second Supervisor/Manager is not required in that
case. Admin creators remain blocked unconditionally (Admin has no home-unit
scoping to anchor the exemption to).
"""

from __future__ import annotations

from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.errors import PermissionDeniedError
from app.core.user_messages import m

# Mirrors visibility.py role families — Supervisor/Manager (+ Admin) may give
# final Handling Unit / Owner acceptance on any matching unit. Agent-family may
# ACCEPT only when the party unit equals their acting unit (own-branch Mode A).
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
    """True when the principal's role may submit final F4 acceptance (any unit)."""
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
    - role is Agent (own-unit only) or Supervisor / Manager / Admin;
    - actor unit matches the party unit (Owner → owner_unit_id,
      HANDLING_UNIT → current handling / owning_unit_id), unless Admin;
    - creator SoD: complaint creator cannot be the sole approver, unless
      acting on their own unit (Agent Mode A Tutup, or Supervisor/Manager
      closing a case they authored within their own unit — 2026-08-19).
      Admin creators are always blocked (no home-unit anchor).
    """
    party_key = (party or "").strip().upper()
    if party_key not in {"OWNER", "HANDLING_UNIT"}:
        raise PermissionDeniedError(m("case.acceptance_party_invalid"))

    is_agent = principal_is_case_agent(principal)
    is_approver = principal_may_give_case_acceptance(principal)
    if not is_agent and not is_approver:
        raise PermissionDeniedError(m("case.acceptance_role_denied"))

    is_unit_approver = principal.has_any_role(*_UNIT_APPROVER_ROLES)
    is_creator = _ids_equal(str(principal.user_id), complaint_creator_id)

    actor_unit = OrgUnitResolver.normalize(actor_unit_id)
    if party_key == "OWNER":
        required = OrgUnitResolver.normalize(owner_unit_id)
        mismatch_message = "case.acceptance_owner_unit_mismatch"
    else:
        required = OrgUnitResolver.normalize(handling_unit_id)
        mismatch_message = "case.acceptance_handling_unit_mismatch"
    own_unit = bool(required) and actor_unit == required

    if is_creator and not (is_agent or (is_unit_approver and own_unit)):
        raise PermissionDeniedError(m("case.acceptance_creator_conflict"))

    if principal.has_any_role(*_ADMIN_ROLES):
        return

    if not own_unit:
        raise PermissionDeniedError(m(mismatch_message))


def assert_case_resolve_accept_authorized(
    principal: Principal,
    *,
    handling_unit_id: str | None,
    actor_unit_id: str | None,
    complaint_creator_id: str | None,
) -> None:
    """Authorize resolve action=ACCEPT (stamps Handling Unit acceptance).

    Agent may ACCEPT when acting on their own Handling Unit (Mode A). Cross-unit
    ACCEPT remains Supervisor/Manager/Admin via the same unit/SoD rules as
    party=HANDLING_UNIT acceptance.
    """
    assert_case_acceptance_authorized(
        principal,
        party="HANDLING_UNIT",
        owner_unit_id=None,
        handling_unit_id=handling_unit_id,
        actor_unit_id=actor_unit_id,
        complaint_creator_id=complaint_creator_id,
    )
