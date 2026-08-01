"""Mapper between ORM rows and CaseAggregate."""

from __future__ import annotations

from uuid import UUID

from app.modules.cm_case.domain.aggregate import CaseAggregate, ResolutionRecord
from app.modules.cm_case.domain.value_objects import (
    CancelReason,
    CaseNumber,
    CaseStatus,
    ResolutionProposalStatus,
)
from app.modules.cm_case.infrastructure.orm import CmCaseORM, CmCaseResolutionORM


def resolution_from_orm(row: CmCaseResolutionORM) -> ResolutionRecord:
    return ResolutionRecord(
        resolution_id=str(row.id),
        resolution_code=row.resolution_code,
        summary=row.summary,
        status=ResolutionProposalStatus(row.status),
        comment=row.comment,
        detail=row.detail,
        customer_impact=row.customer_impact,
        attachment_ids=list(row.attachment_ids or []),
        proposed_by=row.proposed_by,
        proposed_at=row.proposed_at,
        decided_by=row.decided_by,
        decided_at=row.decided_at,
        rejection_reason=row.rejection_reason,
    )


def case_from_orm(
    row: CmCaseORM, resolutions: list[CmCaseResolutionORM]
) -> CaseAggregate:
    history = [resolution_from_orm(r) for r in resolutions]
    current = history[-1] if history else None
    cancel = CancelReason(row.cancel_reason) if row.cancel_reason else None
    return CaseAggregate(
        case_id=row.id,
        case_number=CaseNumber(row.case_number),
        complaint_id=row.complaint_id,
        customer_id=row.customer_id,
        status=CaseStatus(row.status),
        case_type=row.case_type,
        subject=row.subject,
        description=row.description,
        priority=row.priority,
        created_by=row.created_by,
        created_at=row.created_at,
        category=row.category,
        owning_unit_id=row.owning_unit_id,
        sla_policy_version_id=row.sla_policy_version_id,
        sla_countdown_active=False,
        cancel_reason=cancel,
        closed_by=row.closed_by,
        closed_at=row.closed_at,
        updated_at=row.updated_at,
        resolution=current,
        resolution_history=history,
        supervisor_approved_after_resolved=row.supervisor_approved_after_resolved,
    )


def apply_case_to_orm(case: CaseAggregate, row: CmCaseORM) -> None:
    row.case_number = case.case_number.value
    row.complaint_id = case.complaint_id
    row.customer_id = case.customer_id
    row.status = case.status.value
    row.case_type = case.case_type
    row.category = case.category
    row.subject = case.subject
    row.description = case.description
    row.priority = case.priority
    row.owning_unit_id = case.owning_unit_id
    row.sla_policy_version_id = case.sla_policy_version_id
    row.sla_countdown_active = False
    row.cancel_reason = case.cancel_reason.value if case.cancel_reason else None
    row.closed_by = case.closed_by
    row.closed_at = case.closed_at
    row.supervisor_approved_after_resolved = case.supervisor_approved_after_resolved
    row.created_by = case.created_by
    row.created_at = case.created_at
    if case.updated_at is not None:
        row.updated_at = case.updated_at


def resolution_to_orm(case_id: UUID, record: ResolutionRecord) -> CmCaseResolutionORM:
    return CmCaseResolutionORM(
        id=UUID(record.resolution_id),
        case_id=case_id,
        resolution_code=record.resolution_code,
        summary=record.summary,
        detail=record.detail,
        customer_impact=record.customer_impact,
        status=record.status.value,
        comment=record.comment,
        attachment_ids=list(record.attachment_ids),
        proposed_by=record.proposed_by,
        proposed_at=record.proposed_at,
        decided_by=record.decided_by,
        decided_at=record.decided_at,
        rejection_reason=record.rejection_reason,
    )
