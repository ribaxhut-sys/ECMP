"""REST controller for CAP-008 Mode A (Epic 5). No business logic here."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.cm_case.api.schemas import (
    AddCaseRequest,
    CaseResolutionResponse,
    CaseResponse,
    CloseCaseRequest,
    CreateCaseRequest,
    ResolveCaseRequest,
    UpdateCaseStatusRequest,
)
from app.modules.cm_case.application.dto import (
    AddCaseCommand,
    CaseDTO,
    CloseCaseCommand,
    CreateCaseCommand,
    ResolveCaseCommand,
    UpdateStatusCommand,
)
from app.modules.cm_case.application.services import (
    AuditTimelineSideEffects,
    CaseApplicationService,
)
from app.modules.cm_case.infrastructure.repository import SqlAlchemyCaseRepository

router = APIRouter(tags=["CM-Case-ModeA"])


def get_case_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> CaseApplicationService:
    return CaseApplicationService(
        SqlAlchemyCaseRepository(session),
        side_effects=AuditTimelineSideEffects(session),
    )


def _to_response(dto: CaseDTO) -> CaseResponse:
    def res(r):
        if r is None:
            return None
        return CaseResolutionResponse(
            resolutionId=r.resolution_id,
            resolutionCode=r.resolution_code,
            summary=r.summary,
            status=r.status,
            comment=r.comment,
            detail=r.detail,
            customerImpact=r.customer_impact,
            attachmentIds=r.attachment_ids,
            proposedBy=r.proposed_by,
            proposedAt=r.proposed_at,
            decidedBy=r.decided_by,
            decidedAt=r.decided_at,
            rejectionReason=r.rejection_reason,
        )

    return CaseResponse(
        caseId=dto.case_id,
        caseNumber=dto.case_number,
        complaintId=dto.complaint_id,
        customerId=dto.customer_id,
        status=dto.status,
        caseType=dto.case_type,
        category=dto.category,
        subject=dto.subject,
        description=dto.description,
        priority=dto.priority,
        owningUnitId=dto.owning_unit_id,
        assignedUserId=None,
        slaPolicyVersionId=dto.sla_policy_version_id,
        slaCountdownActive=False,
        resolution=res(dto.resolution),
        resolutionHistory=[res(r) for r in dto.resolution_history],
        cancelReason=dto.cancel_reason,
        closedBy=dto.closed_by,
        closedAt=dto.closed_at,
        createdAt=dto.created_at,
        createdBy=dto.created_by,
        updatedAt=dto.updated_at,
        complaintStatusAfterCreate=dto.complaint_status_after_create,
    )


@router.post("/api/v1/cm/cases", status_code=201)
def create_case(
    body: CreateCaseRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    _ = idempotency_key  # optional — FRD NOT SPECIFIED as mandatory for Mode A
    dto = service.create_case(
        CreateCaseCommand(
            complaint_id=body.complaint_id,
            case_type=body.case_type,
            subject=body.subject,
            description=body.description,
            priority=body.priority,
            category=body.category,
            destination_unit_id=body.destination_unit_id,
            assigned_user_id=body.assigned_user_id,
            sla_policy_version_id=body.sla_policy_version_id,
            actor_id=str(principal.user_id),
        )
    )
    return DataResponse(data=_to_response(dto))


@router.post("/api/v1/cm/complaints/{complaint_id}/cases", status_code=201)
def add_case(
    complaint_id: str,
    body: AddCaseRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    _ = idempotency_key
    dto = service.add_case(
        AddCaseCommand(
            complaint_id=complaint_id,
            case_type=body.case_type,
            subject=body.subject,
            description=body.description,
            priority=body.priority,
            category=body.category,
            destination_unit_id=body.destination_unit_id,
            assigned_user_id=body.assigned_user_id,
            sla_policy_version_id=body.sla_policy_version_id,
            actor_id=str(principal.user_id),
        )
    )
    return DataResponse(data=_to_response(dto))


@router.get("/api/v1/cm/cases/{case_id}")
def get_case(
    case_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    complaint_id: Annotated[str | None, Query(alias="complaintId")] = None,
) -> DataResponse[CaseResponse]:
    _ = principal
    dto = service.get_case(case_id, complaint_id_context=complaint_id)
    return DataResponse(data=_to_response(dto))


@router.patch("/api/v1/cm/cases/{case_id}/status")
def update_case_status(
    case_id: str,
    body: UpdateCaseStatusRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    _ = idempotency_key
    dto = service.update_status(
        UpdateStatusCommand(
            case_id=case_id,
            to_status=body.to_status,
            actor_id=str(principal.user_id),
            destination_unit_id=body.destination_unit_id,
            cancel_reason=body.cancel_reason,
            reason=body.reason,
            assigned_user_id=body.assigned_user_id,
        )
    )
    return DataResponse(data=_to_response(dto))


@router.post("/api/v1/cm/cases/{case_id}/resolve")
def resolve_case(
    case_id: str,
    body: ResolveCaseRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    _ = idempotency_key
    dto = service.resolve(
        ResolveCaseCommand(
            case_id=case_id,
            action=body.action,
            comment=body.comment,
            actor_id=str(principal.user_id),
            resolution_code=body.resolution_code,
            summary=body.summary,
            detail=body.detail,
            customer_impact=body.customer_impact,
            attachment_ids=list(body.attachment_ids or []),
            rejection_reason=body.rejection_reason,
        )
    )
    return DataResponse(data=_to_response(dto))


@router.post("/api/v1/cm/cases/{case_id}/close")
def close_case(
    case_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    body: CloseCaseRequest | None = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    _ = idempotency_key
    note = body.note if body else None
    dto = service.close(
        CloseCaseCommand(
            case_id=case_id, actor_id=str(principal.user_id), note=note
        )
    )
    return DataResponse(data=_to_response(dto))
