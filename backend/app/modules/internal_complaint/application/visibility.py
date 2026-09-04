"""List/GET visibility for Pengaduan Internal (Mode A).

WITHDRAWN tickets are owner-visible. Pusat sees them only after Pusat has
handled (receive, return-for-completion, or approved withdraw request).
"""

from __future__ import annotations

from datetime import datetime

from app.core.authorization.org_unit_guard import (
    is_service_account_allowlisted,
    org_scope_enforcement_enabled,
)
from app.core.authorization.principal import Principal
from app.core.authorization.visibility import VisibilityClass, is_pusat_unit
from app.core.config import Settings
from app.core.errors import NotFoundError
from app.core.user_messages import m
from app.modules.internal_complaint.application.dto import InternalComplaintDTO

_ADMIN_ROLES = frozenset({"ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"})
_VIEWER_ROLES = frozenset({"VIEWER"})
_UNIT_ROLES = frozenset(
    {
        "SUPERVISOR",
        "BRANCH_SUPERVISOR",
        "MANAGER",
        "AGENT",
        "CS_AGENT",
        "HANDLER",
        "BRANCH_OFFICER",
    }
)


def resolve_internal_visibility(
    principal: Principal, *, org_unit_id: str | None = None
) -> VisibilityClass:
    """Pengaduan Internal: Owner/Handling unit visibility for Agent too.

    F4 Case uses SELF for branch Agents; Internal Complaints require unit
    members (including Agent) to see complaints owned or handled by their unit.

    ``org_unit_id`` is the resolved membership (``_actor_unit``). Lab JWTs
    often omit ``orgUnitId``; class must follow membership, not the claim.
    """
    if principal.has_any_role(*_ADMIN_ROLES) or principal.has_any_role(
        *_VIEWER_ROLES
    ):
        return VisibilityClass.ALL
    if principal.has_any_role(*_UNIT_ROLES):
        unit = org_unit_id or principal.org_unit_id
        if is_pusat_unit(unit):
            return VisibilityClass.PUSAT
        return VisibilityClass.UNIT
    return VisibilityClass.SELF


def pusat_sees_withdrawn(*, owner_unit_id: str, pusat_handled_at: datetime | None) -> bool:
    """True when a WITHDRAWN ticket belongs in the Pusat inbox."""
    return is_pusat_unit(owner_unit_id) or pusat_handled_at is not None


def is_internal_complaint_visible(
    principal: Principal,
    dto: InternalComplaintDTO,
    *,
    actor_unit_id: str | None,
) -> bool:
    vis = resolve_internal_visibility(principal, org_unit_id=actor_unit_id)
    if vis is VisibilityClass.ALL:
        return True
    if vis is VisibilityClass.SELF:
        return str(principal.user_id) == dto.created_by
    if vis is VisibilityClass.UNIT and is_pusat_unit(actor_unit_id):
        vis = VisibilityClass.PUSAT
    if vis is VisibilityClass.UNIT:
        unit = (actor_unit_id or "").strip()
        if not unit:
            return False
        return unit == dto.owner_unit_id or unit == dto.handling_unit_id
    if vis is VisibilityClass.PUSAT:
        if dto.status == "WITHDRAWN":
            return pusat_sees_withdrawn(
                owner_unit_id=dto.owner_unit_id,
                pusat_handled_at=dto.pusat_handled_at,
            )
        return is_pusat_unit(dto.owner_unit_id) or is_pusat_unit(dto.handling_unit_id)
    return False


def assert_internal_complaint_visible(
    principal: Principal,
    dto: InternalComplaintDTO,
    *,
    actor_unit_id: str | None,
    settings: Settings,
) -> None:
    """404 when the ticket is outside the caller's list visibility (no leak)."""
    if org_scope_enforcement_enabled(settings) and is_service_account_allowlisted(
        principal, settings
    ):
        return
    if not is_internal_complaint_visible(
        principal, dto, actor_unit_id=actor_unit_id
    ):
        raise NotFoundError(m("complaint.not_found"))
