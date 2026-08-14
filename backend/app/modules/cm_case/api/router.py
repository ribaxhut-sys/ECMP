"""REST controller for CAP-008 Mode A (Epic 5). No business logic here."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.core.auth import (
    OrgUnitResolver,
    Principal,
    enforce_org_scope,
    require_permissions,
)
from app.core.authorization.case_acceptance import (
    assert_case_acceptance_authorized,
    assert_case_resolve_accept_authorized,
)
from app.core.authorization.org_unit_guard import enforce_org_scope_any
from app.core.config import Settings, get_settings
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.api.schemas import (
    AddCaseRequest,
    CaseAcceptanceResponse,
    CaseResolutionResponse,
    CaseResponse,
    CaseSummaryResponse,
    CloseCaseRequest,
    CreateCaseRequest,
    RecordAcceptanceRequest,
    ResolveCaseRequest,
    UpdateCaseStatusRequest,
)
from app.modules.cm_case.application.dto import (
    AddCaseCommand,
    CaseDTO,
    CloseCaseCommand,
    CreateCaseCommand,
    RecordAcceptanceCommand,
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


def _actor_unit(principal: Principal, session: Session) -> str | None:
    """Acting unit for F4 history (\"unit mana yang melakukan\").

    Mirrors ``cm_batch1.router._effective_org_unit`` — claim first, ECMP
    membership fallback fail-open (Mode A / offline lab; dev-mode JWTs carry
    no orgUnitId claim at all).
    """
    resolver = OrgUnitResolver(session)
    claimed = resolver.normalize(principal.org_unit_id)
    if claimed:
        return claimed
    try:
        return resolver.resolve_principal_membership(principal.user_id)
    except Exception:
        return None


def _complaint_creator_id(session: Session, complaint_id: str | None) -> str | None:
    """F4 SoD — creator is the user who created the parent Complaint."""
    key = (complaint_id or "").strip()
    if not key:
        return None
    row: CmBatch1ComplaintORM | None = None
    try:
        row = session.get(CmBatch1ComplaintORM, uuid.UUID(key))
    except ValueError:
        row = None
    if row is None:
        return None
    return (row.created_by or "").strip() or None


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

    def acc(a):
        if a is None:
            return None
        return CaseAcceptanceResponse(
            acceptanceId=a.acceptance_id,
            party=a.party,
            decision=a.decision,
            actorId=a.actor_id,
            actorUnitId=a.actor_unit_id,
            decidedAt=a.decided_at,
            note=a.note,
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
        ownerUnitId=dto.owner_unit_id,
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
        handlingUnitAcceptance=acc(dto.handling_unit_acceptance),
        ownerAcceptance=acc(dto.owner_acceptance),
        acceptanceHistory=[acc(a) for a in dto.acceptance_history],
    )


@router.get("/api/v1/cm/cases")
def list_cases(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    complaint_id: Annotated[str | None, Query(alias="complaintId")] = None,
    status: Annotated[str | None, Query()] = None,
) -> ListResponse[CaseSummaryResponse]:
    """API-536 / DEC-024 — visibility-scoped Case list."""
    items, total = service.list_cases(
        principal,
        page=page,
        page_size=page_size,
        complaint_id=complaint_id,
        status=status,
    )
    return ListResponse(
        data=[
            CaseSummaryResponse(
                caseId=i.case_id,
                caseNumber=i.case_number,
                complaintId=i.complaint_id,
                status=i.status,
                caseType=i.case_type,
                category=i.category,
                priority=i.priority,
                subject=i.subject,
                owningUnitId=i.owning_unit_id,
                ownerUnitId=i.owner_unit_id,
                customerId=i.customer_id,
                createdAt=i.created_at,
                createdBy=i.created_by,
            )
            for i in items
        ],
        meta=PageMeta(page=page, pageSize=page_size, totalItems=total),
    )


@router.post("/api/v1/cm/cases", status_code=201)
def create_case(
    body: CreateCaseRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
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
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto))


@router.post("/api/v1/cm/complaints/{complaint_id}/cases", status_code=201)
def add_case(
    complaint_id: str,
    body: AddCaseRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
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
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto))


@router.get("/api/v1/cm/cases/{case_id}")
def get_case(
    case_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    complaint_id: Annotated[str | None, Query(alias="complaintId")] = None,
) -> DataResponse[CaseResponse]:
    """SECMIG-P4 parity: org scope on approved read (after permission).

    F4: Owner unit retains visibility after Handling Unit transfer.
    """
    units = OrgUnitResolver(session).resolve_case_units(case_id)
    enforce_org_scope_any(
        principal,
        (units.handling_unit_id, units.owner_unit_id),
        settings,
    )
    dto = service.get_case(case_id, complaint_id_context=complaint_id)
    return DataResponse(data=_to_response(dto))


@router.patch("/api/v1/cm/cases/{case_id}/status")
def update_case_status(
    case_id: str,
    body: UpdateCaseStatusRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    """SECMIG-P4 parity: org scope after permission check, before mutation."""
    _ = idempotency_key
    resource_org = OrgUnitResolver(session).resolve_case(case_id)
    enforce_org_scope(principal, resource_org, settings)
    dto = service.update_status(
        UpdateStatusCommand(
            case_id=case_id,
            to_status=body.to_status,
            actor_id=str(principal.user_id),
            destination_unit_id=body.destination_unit_id,
            cancel_reason=body.cancel_reason,
            reason=body.reason,
            assigned_user_id=body.assigned_user_id,
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto))


@router.post("/api/v1/cm/cases/{case_id}/resolve")
def resolve_case(
    case_id: str,
    body: ResolveCaseRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    """SECMIG-P4 parity: org scope after permission check, before mutation.

    F4: action=ACCEPT stamps Handling Unit acceptance. Mode A: Officer may ACCEPT
    on their own Handling Unit; cross-unit ACCEPT remains Supervisor/Manager/
    Admin (creator SoD for approver roles).
    """
    _ = idempotency_key
    units = OrgUnitResolver(session).resolve_case_units(case_id)
    enforce_org_scope(principal, units.handling_unit_id, settings)
    actor_unit = _actor_unit(principal, session)
    if (body.action or "").strip().upper() == "ACCEPT":
        assert_case_resolve_accept_authorized(
            principal,
            handling_unit_id=units.handling_unit_id,
            actor_unit_id=actor_unit,
            complaint_creator_id=_complaint_creator_id(session, units.complaint_id),
        )
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
            actor_unit_id=actor_unit,
        )
    )
    return DataResponse(data=_to_response(dto))


@router.post("/api/v1/cm/cases/{case_id}/acceptance")
def record_case_acceptance(
    case_id: str,
    body: RecordAcceptanceRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    """F4 closure rule — Handling Unit / Owner accept or reject a resolution.

    Authorization: ``complaints:update`` plus party / role / unit / creator SoD
    (not org-scope against Handling Unit alone).
    """
    _ = idempotency_key
    units = OrgUnitResolver(session).resolve_case_units(case_id)
    actor_unit = _actor_unit(principal, session)
    party = (body.party or "").strip().upper()
    # JWT org-scope against the party unit (Owner or current Handling Unit).
    party_org = (
        units.owner_unit_id if party == "OWNER" else units.handling_unit_id
    )
    enforce_org_scope(principal, party_org, settings)
    assert_case_acceptance_authorized(
        principal,
        party=party,
        owner_unit_id=units.owner_unit_id,
        handling_unit_id=units.handling_unit_id,
        actor_unit_id=actor_unit,
        complaint_creator_id=_complaint_creator_id(session, units.complaint_id),
    )
    dto = service.record_acceptance(
        RecordAcceptanceCommand(
            case_id=case_id,
            party=body.party,
            decision=body.decision,
            actor_id=str(principal.user_id),
            actor_unit_id=actor_unit,
            note=body.note,
        )
    )
    return DataResponse(data=_to_response(dto))


@router.post("/api/v1/cm/cases/{case_id}/close")
def close_case(
    case_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    body: CloseCaseRequest | None = None,
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    """SECMIG-P4 parity: org scope after permission check, before mutation.

    F4: Owner or Handling Unit may close once both acceptances are present.
    """
    _ = idempotency_key
    units = OrgUnitResolver(session).resolve_case_units(case_id)
    enforce_org_scope_any(
        principal,
        (units.handling_unit_id, units.owner_unit_id),
        settings,
    )
    note = body.note if body else None
    dto = service.close(
        CloseCaseCommand(
            case_id=case_id,
            actor_id=str(principal.user_id),
            note=note,
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto))
