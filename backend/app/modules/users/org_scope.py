"""Cross-unit guard for single-user admin actions (UM-SEC-P0-1 / P0-2).

Lives outside the router so other modules that act on a *user* — the Users
directory work-stats panel, for one — compare units exactly the same way
instead of re-deriving the rule.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.errors import OrgScopeDeniedError
from app.core.user_messages import m
from app.models import Branch

HEAD_OFFICE_ADMIN_ROLES = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")


def org_scope_denied() -> OrgScopeDeniedError:
    """The one denial shape every user-scoped route returns (403)."""
    return OrgScopeDeniedError(
        m("common.org_scope_denied"),
        details={"reason": "org_unit_mismatch"},
    )


def assert_target_user_in_same_unit(
    principal: Principal,
    target_user_id: uuid.UUID,
    session: Session,
) -> None:
    """Single-target cross-unit write guard (UM-SEC-P0-1 / P0-2).

    Extracted verbatim from ``update_user_status`` (UM-BUG-007) so PUT /users/{id}
    and POST /users/{id}/reset-password compare the same way: Head Office
    Admin/Administrator/Super Admin stay unrestricted, every other role may only
    act on a member of its own unit.

    The actor's unit is resolved claim-first with a DB-membership fallback
    (``OrgUnitResolver.resolve_principal``), so the rule holds identically in
    Mode A — where no orgUnitId claim is ever issued — and in Mode B. Cross-unit
    isolation is a domain rule, which is why this deliberately does not go
    through ``org_scope_enforcement_enabled`` (jwt-only) like the read paths do.
    """
    if principal.has_any_role(*HEAD_OFFICE_ADMIN_ROLES):
        return
    resolver = OrgUnitResolver(session)
    actor_org = resolver.resolve_principal(principal)
    target_org = resolver.resolve_user(target_user_id)
    if actor_org is None or target_org is None or actor_org != target_org:
        raise org_scope_denied()


def assert_declared_branch_in_same_unit(
    principal: Principal,
    branch_id: uuid.UUID,
    session: Session,
) -> None:
    """A member may not be moved out of the administrator's own unit.

    Guarding only the target's *current* unit still lets a branch admin hand
    one of their members to another unit by writing ``branchId``. Same shape as
    the ``users:create`` declared-unit check, minus the jwt-only gate — this is
    the domain rule, so Mode A enforces it too.
    """
    if principal.has_any_role(*HEAD_OFFICE_ADMIN_ROLES):
        return
    resolver = OrgUnitResolver(session)
    actor_org = resolver.resolve_principal(principal)
    branch = session.get(Branch, branch_id)
    declared = OrgUnitResolver.normalize(branch.code if branch is not None else None)
    if actor_org is None or declared is None or actor_org != declared:
        raise org_scope_denied()
