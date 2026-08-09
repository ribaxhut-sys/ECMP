"""Resolve optional related Batch-1 Aggregate for Pengaduan Internal create."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.authorization.case_acceptance import (
    principal_is_case_agent,
    principal_may_give_case_acceptance,
)
from app.core.authorization.org_unit_resolver import OrgUnitResolver
from app.core.authorization.principal import Principal
from app.core.authorization.visibility import resolve_row_visibility
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.internal_complaint.domain import errors as err


@dataclass(frozen=True, slots=True)
class RelatedAggregateRef:
    complaint_id: str
    complaint_number: str


def _ids_equal(left: str | None, right: str | None) -> bool:
    a = (left or "").strip().lower()
    b = (right or "").strip().lower()
    return bool(a) and bool(b) and a == b


def _units_equal(left: str | None, right: str | None) -> bool:
    a = OrgUnitResolver.normalize(left)
    b = OrgUnitResolver.normalize(right)
    return bool(a) and bool(b) and a == b


def resolve_related_aggregate(
    session: Session,
    *,
    related_complaint_id: str | None,
    principal: Principal,
    actor_unit_id: str | None,
) -> RelatedAggregateRef | None:
    """Validate optional Aggregate link; return DB snapshot or None.

    - empty → None
    - must exist and status != CLOSED
    - Agent-family: created_by == actor (SELF)
    - Supervisor/Manager: owning_unit_id == actor unit (UNIT)
    - Admin (ALL): allowed when not CLOSED
    """
    key = (related_complaint_id or "").strip()
    if not key:
        return None

    row: CmBatch1ComplaintORM | None = None
    try:
        row = session.get(CmBatch1ComplaintORM, UUID(key))
    except ValueError:
        row = None
    if row is None:
        row = session.scalar(
            select(CmBatch1ComplaintORM).where(
                CmBatch1ComplaintORM.complaint_number == key
            )
        )
    if row is None:
        raise err.not_found("Related Aggregate complaint does not exist.")

    status = (row.status or "").strip().upper()
    if status == "CLOSED":
        raise err.conflict(
            "RELATED_COMPLAINT_CLOSED",
            "Related Aggregate must not be CLOSED.",
            details={"relatedComplaintId": str(row.id), "status": status},
        )

    vis = resolve_row_visibility(principal).value
    if vis == "ALL" or principal.has_any_role(
        "ADMIN", "ADMINISTRATOR", "SUPER_ADMIN"
    ):
        return RelatedAggregateRef(
            complaint_id=str(row.id),
            complaint_number=row.complaint_number,
        )

    if principal_is_case_agent(principal):
        if not _ids_equal(str(principal.user_id), row.created_by):
            raise err.conflict(
                "RELATED_COMPLAINT_NOT_VISIBLE",
                "Agent may only link Aggregate complaints they created.",
                details={"relatedComplaintId": str(row.id)},
            )
        return RelatedAggregateRef(
            complaint_id=str(row.id),
            complaint_number=row.complaint_number,
        )

    if principal_may_give_case_acceptance(principal):
        if not _units_equal(actor_unit_id, row.owning_unit_id):
            raise err.conflict(
                "RELATED_COMPLAINT_NOT_VISIBLE",
                "Related Aggregate is outside actor unit scope.",
                details={
                    "relatedComplaintId": str(row.id),
                    "owningUnitId": row.owning_unit_id,
                },
            )
        return RelatedAggregateRef(
            complaint_id=str(row.id),
            complaint_number=row.complaint_number,
        )

    if not _ids_equal(str(principal.user_id), row.created_by):
        raise err.conflict(
            "RELATED_COMPLAINT_NOT_VISIBLE",
            "Related Aggregate is not visible to the actor.",
            details={"relatedComplaintId": str(row.id)},
        )
    return RelatedAggregateRef(
        complaint_id=str(row.id),
        complaint_number=row.complaint_number,
    )
