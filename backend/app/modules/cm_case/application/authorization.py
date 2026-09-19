"""Single-resource visibility for CAP-008 Cases — P0-3 (domain layer).

Twin of ``cm_batch1.complaint_authorization``: the rule the Case list already
filters with (``resolve_case_visibility`` + the ``list_summaries`` clauses),
expressed once more in Python so a Case that a principal cannot see in the
list cannot be opened — or mutated — by id either.

Mode-independent on purpose. ``enforce_org_scope`` / ``enforce_org_scope_any``
(SECMIG-P4) stay where they are and keep their jwt-only contract; this runs
underneath them so ``ECMP_AUTH_MODE=dev`` is covered too.
"""

from __future__ import annotations

from dataclasses import replace

from app.core.authorization.org_unit_guard import is_service_account_allowlisted
from app.core.authorization.principal import Principal
from app.core.authorization.visibility import (
    VisibilityClass,
    is_pusat_unit,
    resolve_case_visibility,
)
from app.core.config import Settings
from app.core.errors import NotFoundError
from app.modules.cm_case.application.dto import CaseDTO

CASE_NOT_FOUND = "Case does not exist."


def cm_case_visible(
    principal: Principal,
    dto: CaseDTO,
    *,
    actor_unit_id: str | None,
    complaint_creator_id: str | None = None,
) -> bool:
    """Row-level predicate, class by class — same rules as ``list_summaries``.

    ``PUSAT`` is the escalated/HQ-owned scope, never "Pusat sees every branch":
    an ordinary branch Case that was never escalated stays invisible.
    """
    unit = (actor_unit_id or "").strip()
    visibility = resolve_case_visibility(
        replace(principal, org_unit_id=actor_unit_id)
    )
    if visibility is VisibilityClass.ALL:
        return True
    # Own unit — F4 keeps the Owner unit's access after the Handling Unit moves.
    # Same by-id grant as the Complaint twin: wider than the SELF *list* rule
    # on purpose, so a colleague's Case in the same branch stays openable.
    if unit and unit in {
        (dto.owning_unit_id or "").strip(),
        (dto.owner_unit_id or "").strip(),
    }:
        return True
    if visibility is VisibilityClass.PUSAT and (
        # DEC-029: escalated / HQ-owned work only, not every branch Case.
        bool(dto.escalated_to_pusat)
        or is_pusat_unit(dto.owning_unit_id)
        or is_pusat_unit(dto.owner_unit_id)
    ):
        return True
    actor = str(principal.user_id)
    # Mode A interim (BQ-006): inbox is Case.created_by, plus Cases under a
    # Complaint the actor created — another officer may have opened the Case
    # (same allowance the list makes for parent-scoped reads).
    return (dto.created_by or "").strip() == actor or (
        (complaint_creator_id or "").strip() == actor
    )


def assert_cm_case_visible(
    principal: Principal,
    dto: CaseDTO,
    *,
    settings: Settings,
    actor_unit_id: str | None,
    complaint_creator_id: str | None = None,
) -> None:
    """Raise 404 unless this principal may see the Case (no-leak by-id probe)."""
    if cm_case_visible(
        principal,
        dto,
        actor_unit_id=actor_unit_id,
        complaint_creator_id=complaint_creator_id,
    ):
        return
    if is_service_account_allowlisted(principal, settings):
        return
    raise NotFoundError(CASE_NOT_FOUND)
