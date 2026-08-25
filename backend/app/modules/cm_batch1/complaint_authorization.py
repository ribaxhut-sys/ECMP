"""Single-resource visibility for CM Batch-1 (Aggregate) Complaints — P0-3.

Same shape as ``cm_batch1.attachment_authorization`` (G2): the router asks the
owning module whether this principal may touch this complaint, and the module
answers with the **domain** rule — the one that must hold in Mode A (``dev``)
as well, where ``enforce_org_scope`` is a no-op by design (SECMIG-P4). That
guard is left exactly as it is; this is a separate layer underneath it.

The predicate is the Python twin of what ``list_complaints`` already filters
with (``resolve_row_visibility`` + ``pusat_row_scope_clause``), so a row a
principal cannot see in the list cannot be opened by id either.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
from typing import Protocol

from sqlalchemy import exists, or_, select
from sqlalchemy.orm import Session

from app.core.authorization.org_unit_guard import is_service_account_allowlisted
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.authorization.visibility import (
    DEFAULT_PUSAT_UNIT_CODES,
    VisibilityClass,
    complaint_visible_for_pusat,
    pusat_unit_clause,
    resolve_row_visibility,
)
from app.core.config import Settings
from app.core.errors import NotFoundError
from app.core.user_messages import m
from app.modules.cm_case.infrastructure.orm import CmCaseORM


class ComplaintRow(Protocol):
    """The four facts the rule reads — satisfied by both the Aggregate entity
    and ``ComplaintBatch1Response``, so callers pass whichever they already
    hold instead of the module re-loading the row from a second source."""

    complaint_id: str
    owning_unit_id: str | None
    intake_disposition: str | None
    hq_accepted_at: datetime | None
    created_by: str | None


def _pusat_case_flags(session: Session, complaint_id: str) -> tuple[bool, bool]:
    """(has any Case, has a Pusat Case) for the parent — twin of the list SQL."""
    key = (complaint_id or "").strip()
    if not key:
        return False, False
    has_any = bool(
        session.scalar(
            select(exists().where(CmCaseORM.complaint_id == key))
        )
    )
    if not has_any:
        return False, False
    has_pusat = bool(
        session.scalar(
            select(
                exists().where(
                    CmCaseORM.complaint_id == key,
                    or_(
                        CmCaseORM.escalated_to_pusat.is_(True),
                        pusat_unit_clause(
                            CmCaseORM.owning_unit_id,
                            pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
                        ),
                        pusat_unit_clause(
                            CmCaseORM.owner_unit_id,
                            pusat_unit_codes=DEFAULT_PUSAT_UNIT_CODES,
                        ),
                    ),
                )
            )
        )
    )
    return True, has_pusat


def pusat_may_see_complaint(session: Session, row: ComplaintRow) -> bool:
    """DEC-024 ``PUSAT`` row scope for one complaint (never "Pusat sees all").

    Mirrors ``pusat_row_scope_clause``:
    ``(owned/escalated/HQ-accepted OR a Pusat Case) AND (no Case OR a Pusat
    Case)`` — a parent whose only Cases are branch-closed is branch work, and
    a Case escalated straight to Pusat (DEC-029) is HQ work even when the
    parent never took the intake escalate path.
    """
    has_any_case, has_pusat_case = _pusat_case_flags(session, row.complaint_id)
    if has_pusat_case:
        return True
    if has_any_case:
        return False
    return complaint_visible_for_pusat(
        owning_unit_id=row.owning_unit_id,
        intake_disposition=row.intake_disposition,
        hq_accepted_at=row.hq_accepted_at,
    )


def cm_complaint_visible(
    principal: Principal,
    row: ComplaintRow,
    *,
    session: Session,
    actor_unit_id: str | None,
) -> bool:
    """May this principal open this complaint by id?

    Three grants, in order of how the repository already thinks about rows:

    1. ``ALL`` visibility (admin / viewer) — every row, unchanged.
    2. **Own unit.** The mode-independent twin of what ``enforce_org_scope``
       enforces in Mode B: the owning unit equals the actor's. This is a
       by-id grant, deliberately wider than the ``SELF`` *list* rule — an
       officer opening a colleague's complaint in their own branch is normal
       work, and narrowing detail to "rows my inbox lists" is a product
       decision, not an org-scope fix.
    3. ``PUSAT`` — only through the escalation predicate below, never
       "Pusat sees every branch".

    What no grant covers is the thing P0-3 is about: another unit's row.
    """
    unit = (actor_unit_id or "").strip()
    visibility = resolve_row_visibility(
        replace(principal, org_unit_id=actor_unit_id)
    )
    if visibility is VisibilityClass.ALL:
        return True
    if unit and (row.owning_unit_id or "").strip() == unit:
        return True
    if visibility is VisibilityClass.PUSAT and pusat_may_see_complaint(session, row):
        return True
    # Own intake stays readable even after the row moved units (SELF list rule).
    return (row.created_by or "").strip() == str(principal.user_id)


def assert_cm_complaint_visible(
    principal: Principal,
    row: ComplaintRow,
    *,
    session: Session,
    settings: Settings,
    actor_unit_id: str | None = None,
) -> None:
    """Raise 404 unless this principal may see the complaint.

    ``NotFoundError`` (not 403) deliberately: a by-id probe must not confirm
    that a complaint exists in another unit — the same no-leak shape
    ``assert_internal_complaint_visible`` already uses for ticket reads.
    """
    unit = (
        actor_unit_id
        if actor_unit_id is not None
        else OrgUnitResolver(session).resolve_principal(principal)
    )
    if cm_complaint_visible(principal, row, session=session, actor_unit_id=unit):
        return
    # Denial path only — same machine-identity allowlist OrgUnitGuard uses.
    if is_service_account_allowlisted(principal, settings):
        return
    raise NotFoundError(m("complaint.not_found"))
