"""Authorization for CM Batch-1 (Aggregate) complaint attachments (CAPABILITY-011).

Used by the shared attachment router when a platform attachment is linked to a
Batch-1 complaint. Mirrors ``internal_complaint.attachment_authorization``: the
router asks one question ("may this principal touch this complaint's files?")
and the owning module answers with its own visibility rule.

Deliberately **mode-independent**. Cross-unit isolation is a domain rule, so it
must hold with ``ECMP_AUTH_MODE=dev`` too, where no orgUnitId claim is ever
issued and ``enforce_org_scope`` (SECMIG-P4) is a no-op. The actor's unit
therefore comes from ``OrgUnitResolver.resolve_principal`` (claim first, DB
membership fallback), not from the claim alone. The SECMIG-P4 guard machinery
itself is left untouched.
"""

from __future__ import annotations

import uuid
from dataclasses import replace

from sqlalchemy.orm import Session

from app.core.authorization.org_unit_guard import is_service_account_allowlisted
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.authorization.visibility import (
    VisibilityClass,
    is_pusat_unit,
    resolve_row_visibility,
)
from app.core.config import Settings
from app.core.errors import NotFoundError, OrgScopeDeniedError
from app.core.user_messages import m
from app.modules.cm_batch1.complaint_authorization import pusat_may_see_complaint
from app.modules.cm_batch1.repository import CmBatch1Repository


def assert_can_access_cm_complaint_attachment(
    *,
    principal: Principal,
    session: Session,
    complaint_id: str | uuid.UUID | None,
    settings: Settings,
) -> None:
    """Gate list / metadata / download of one Batch-1 complaint's files.

    Denial is ``OrgScopeDeniedError`` (403), not a no-leak 404: that is what
    ``download_attachment`` already returned for this exact case, and metadata
    and download must not disagree about the same file.

    Fail-open cases, both intentional: an ``aggregate_id`` with no Batch-1
    complaint row (CAP-011 is aggregate-agnostic — it holds no FK to Complaint)
    and a complaint with no recorded owning unit (staging / pre-column rows).
    Neither can be attributed to a unit, so there is nothing to compare.
    """
    if complaint_id is None or not str(complaint_id).strip():
        return
    resolver = OrgUnitResolver(session)
    try:
        resource_org = resolver.resolve_cm_complaint(complaint_id)
    except NotFoundError:
        return
    if resource_org is None:
        return

    actor_org = resolver.resolve_principal(principal)
    visibility = resolve_row_visibility(replace(principal, org_unit_id=actor_org))
    if visibility is VisibilityClass.ALL:
        return
    # Pusat handles escalated branch work — but only work that is actually
    # theirs (G3): the same DEC-024 predicate the Pusat list filters with, not
    # the blanket pass _enforce_cm_org_or_pusat_hq grants. A complaint row that
    # cannot be loaded keeps the fail-open above — there is nothing to judge.
    if visibility is VisibilityClass.PUSAT or is_pusat_unit(actor_org):
        row = CmBatch1Repository(session).get(str(complaint_id).strip())
        if row is None or pusat_may_see_complaint(session, row):
            return
    if actor_org is not None and actor_org == resource_org:
        return
    # Consulted only on the denial path — same machine-identity allowlist
    # OrgUnitGuard uses (default deny when unconfigured, SECMIG-P4-001R / M-2).
    if is_service_account_allowlisted(principal, settings):
        return
    raise OrgScopeDeniedError(
        m("common.org_scope_denied"),
        details={"reason": "org_unit_mismatch"},
    )
