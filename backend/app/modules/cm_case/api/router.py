"""REST controller for CAP-008 Mode A (Epic 5). No business logic here."""

from __future__ import annotations

import logging
import uuid
from dataclasses import replace
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.core.auth import (
    OrgUnitResolver,
    Principal,
    enforce_org_scope,
    require_any_permission,
    require_permissions,
)
from app.core.authorization.case_acceptance import (
    assert_case_acceptance_authorized,
    assert_case_resolve_accept_authorized,
)
from app.core.authorization.org_unit_guard import enforce_org_scope_any
from app.core.authorization.visibility import VisibilityClass, resolve_case_visibility
from app.core.config import Settings, get_settings
from app.core.errors import PermissionDeniedError
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.integrations.directory.local_adapter import LocalUserDirectory
from app.modules.cm_batch1.models import CmBatch1ComplaintORM
from app.modules.cm_case.api.schemas import (
    AddCaseRequest,
    CancelEscalationToPusatRequest,
    CaseAcceptanceResponse,
    CaseHistoryEntry,
    CaseResolutionResponse,
    CaseResponse,
    CaseSummaryResponse,
    WorkBadgeCountsResponse,
    CloseCaseRequest,
    CreateCaseRequest,
    EscalateToPusatRequest,
    RecordAcceptanceRequest,
    ResolveCaseRequest,
    ReturnEscalationRequest,
    UpdateCaseStatusRequest,
)
from app.modules.cm_case.application.dto import (
    AddCaseCommand,
    CancelEscalationToPusatCommand,
    CaseDTO,
    CloseCaseCommand,
    CreateCaseCommand,
    EscalateToPusatCommand,
    RecordAcceptanceCommand,
    ResolveCaseCommand,
    ReturnEscalationCommand,
    UpdateStatusCommand,
)
from app.modules.cm_case.application.history import CaseHistoryService
from app.modules.cm_case.application.services import (
    AuditTimelineSideEffects,
    CaseApplicationService,
)
from app.modules.cm_case.infrastructure.inbox_repository import (
    safe_mark_read,
    safe_work_badge_counts,
)
from app.modules.cm_case.infrastructure.repository import SqlAlchemyCaseRepository
from app.modules.timeline.repository import TimelineRepository

logger = logging.getLogger(__name__)

router = APIRouter(tags=["CM-Case-ModeA"])


def get_case_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> CaseApplicationService:
    return CaseApplicationService(
        SqlAlchemyCaseRepository(session),
        side_effects=AuditTimelineSideEffects(session),
    )


def get_case_history_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> CaseHistoryService:
    return CaseHistoryService(
        TimelineRepository(session),
        user_directory=LocalUserDirectory(session),
    )


def _history_list_response(
    items: list[CaseHistoryEntry],
) -> ListResponse[CaseHistoryEntry]:
    """API-537 envelope: one page, ``pageSize`` capped at PageMeta maximum 100."""
    total = len(items)
    page_items = items[:100]
    return ListResponse(
        data=page_items,
        meta=PageMeta(
            page=1,
            pageSize=max(1, len(page_items)),
            totalItems=total,
        ),
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


def _officer_labels(session: Session, *raw_ids: str | None) -> dict[str, str]:
    wanted = {str(i).strip() for i in raw_ids if i and str(i).strip()}
    if not wanted:
        return {}
    try:
        return LocalUserDirectory(session).display_names(wanted)
    except Exception:
        return {}


def _to_response(dto: CaseDTO, *, session: Session | None = None) -> CaseResponse:
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
        handlingClaimedBy=dto.handling_claimed_by,
        handlingClaimedByName=(
            _officer_labels(session, dto.handling_claimed_by).get(
                (dto.handling_claimed_by or "").strip()
            )
            if session and dto.handling_claimed_by
            else None
        ),
        updatedAt=dto.updated_at,
        complaintStatusAfterCreate=dto.complaint_status_after_create,
        handlingUnitAcceptance=acc(dto.handling_unit_acceptance),
        ownerAcceptance=acc(dto.owner_acceptance),
        acceptanceHistory=[acc(a) for a in dto.acceptance_history],
        escalatedToPusat=dto.escalated_to_pusat,
        owningUnit=dto.owning_unit,
        escalationReason=dto.escalation_reason,
        escalatedAt=dto.escalated_at,
    )


@router.get("/api/v1/cm/cases")
def list_cases(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    complaint_id: Annotated[str | None, Query(alias="complaintId")] = None,
    status: Annotated[str | None, Query()] = None,
) -> ListResponse[CaseSummaryResponse]:
    """API-536 / DEC-024 — visibility-scoped Case list.

    Mode A JWTs have no ``orgUnitId`` claim. Patch the principal with the
    same membership fallback as Aggregate ``list_complaints`` so SUPERVISOR
    UNIT visibility is not empty (UM-BUG-005).
    """
    vis_principal = replace(principal, org_unit_id=_actor_unit(principal, session))
    items, total = service.list_cases(
        vis_principal,
        page=page,
        page_size=page_size,
        complaint_id=complaint_id,
        status=status,
    )
    names = _officer_labels(
        session,
        *[i.handling_claimed_by for i in items],
    )
    return ListResponse(
        data=[
            CaseSummaryResponse(
                caseId=i.case_id,
                caseNumber=i.case_number,
                complaintId=i.complaint_id,
                complaintNumber=i.complaint_number,
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
                handlingClaimedBy=i.handling_claimed_by,
                handlingClaimedByName=(
                    names.get(i.handling_claimed_by)
                    if i.handling_claimed_by
                    else None
                ),
                escalatedToPusat=i.escalated_to_pusat,
                owningUnit=i.owning_unit,
                escalationReason=i.escalation_reason,
                isRead=i.is_read,
                unreadReason=i.unread_reason,
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
            note=body.note,
            intake_action=body.intake_action,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


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
    return DataResponse(data=_to_response(dto, session=session))


def _pusat_may_read_escalated(principal: Principal, escalated: bool) -> bool:
    """DEC-029: Pusat handlers read Cases flagged to Pusat without rewriting unit."""
    if not escalated:
        return False
    vis = resolve_case_visibility(principal)
    return vis in (VisibilityClass.PUSAT, VisibilityClass.ALL)


def _actor_is_pusat(principal: Principal, session: Session) -> bool:
    vis_principal = replace(principal, org_unit_id=_actor_unit(principal, session))
    vis = resolve_case_visibility(vis_principal)
    return vis in (VisibilityClass.PUSAT, VisibilityClass.ALL)


def _enforce_case_mutation_scope(
    *,
    principal: Principal,
    session: Session,
    settings: Settings,
    service: CaseApplicationService,
    case_id: str,
    branch_org: str | None,
    branch_orgs: tuple[str | None, ...] | None = None,
) -> CaseDTO:
    """Pusat may mutate an escalated Case; otherwise enforce branch org-scope."""
    dto = service.get_case(case_id)
    vis_principal = replace(principal, org_unit_id=_actor_unit(principal, session))
    if dto.escalated_to_pusat and _pusat_may_read_escalated(
        vis_principal, True
    ):
        return dto
    if branch_orgs is not None:
        enforce_org_scope_any(principal, branch_orgs, settings)
    else:
        enforce_org_scope(principal, branch_org, settings)
    return dto


@router.get("/api/v1/cm/work-badges")
def get_work_badges(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[WorkBadgeCountsResponse]:
    """Mode A sidebar counts: Cabang unread Cases + Pusat unclaimed queue.

    Fail-open: repository errors return zeros so navigation stays up.
    Not CAP-005 email/SMS. Not a Mode B unlock.
    """
    unread, queue = safe_work_badge_counts(
        session,
        actor_id=str(principal.user_id),
        actor_is_pusat=_actor_is_pusat(principal, session),
    )
    return DataResponse(
        data=WorkBadgeCountsResponse(unreadCases=unread, pusatQueue=queue)
    )


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
    DEC-029: Pusat may read a Case flagged ``escalatedToPusat`` even though
    originating ``owningUnitId`` stays the branch (DEC-028).
    """
    units = OrgUnitResolver(session).resolve_case_units(case_id)
    vis_principal = replace(principal, org_unit_id=_actor_unit(principal, session))
    dto = service.get_case(case_id, complaint_id_context=complaint_id)
    if not _pusat_may_read_escalated(vis_principal, dto.escalated_to_pusat):
        enforce_org_scope_any(
            principal,
            (units.handling_unit_id, units.owner_unit_id),
            settings,
        )
    body = _to_response(dto, session=session)
    # get_db_session does not auto-commit; persist mark-read before close.
    safe_mark_read(session, case_id=case_id, user_id=str(principal.user_id))
    try:
        session.commit()
    except Exception:
        logger.exception("case inbox mark-read commit failed")
        try:
            session.rollback()
        except Exception:
            pass
    return DataResponse(data=body)


@router.get("/api/v1/cm/cases/{case_id}/history")
def get_case_history(
    case_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    history: Annotated[CaseHistoryService, Depends(get_case_history_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    complaint_id: Annotated[str | None, Query(alias="complaintId")] = None,
) -> ListResponse[CaseHistoryEntry]:
    """API-537 / UC-CAP02-07 — this Case, plus parent HQ-path events."""
    units = OrgUnitResolver(session).resolve_case_units(case_id)
    vis_principal = replace(principal, org_unit_id=_actor_unit(principal, session))
    dto = service.get_case(case_id, complaint_id_context=complaint_id)
    if not _pusat_may_read_escalated(vis_principal, dto.escalated_to_pusat):
        enforce_org_scope_any(
            principal,
            (units.handling_unit_id, units.owner_unit_id),
            settings,
        )
    items = history.list_for_case(dto)
    return _history_list_response(items)


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
    actor_unit = _actor_unit(principal, session)
    actor_is_pusat = _actor_is_pusat(principal, session)
    resource_org = OrgUnitResolver(session).resolve_case(case_id)
    _enforce_case_mutation_scope(
        principal=principal,
        session=session,
        settings=settings,
        service=service,
        case_id=case_id,
        branch_org=resource_org,
    )
    dto = service.update_status(
        UpdateStatusCommand(
            case_id=case_id,
            to_status=body.to_status,
            actor_id=str(principal.user_id),
            destination_unit_id=body.destination_unit_id,
            cancel_reason=body.cancel_reason,
            reason=body.reason,
            assigned_user_id=body.assigned_user_id,
            actor_unit_id=actor_unit,
            handling_claimed_by=body.handling_claimed_by,
            actor_can_reassign=principal.has_any_role(
                "SUPERVISOR", "BRANCH_SUPERVISOR", "MANAGER"
            ),
            actor_is_pusat=actor_is_pusat,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


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
    actor_unit = _actor_unit(principal, session)
    actor_is_pusat = _actor_is_pusat(principal, session)
    dto = _enforce_case_mutation_scope(
        principal=principal,
        session=session,
        settings=settings,
        service=service,
        case_id=case_id,
        branch_org=units.handling_unit_id,
    )
    handling_for_accept = (
        actor_unit
        if dto.escalated_to_pusat and actor_is_pusat
        else units.handling_unit_id
    )
    if (body.action or "").strip().upper() == "ACCEPT":
        assert_case_resolve_accept_authorized(
            principal,
            handling_unit_id=handling_for_accept,
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
            actor_is_pusat=actor_is_pusat,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/cm/cases/{case_id}/escalate-to-pusat")
def escalate_case_to_pusat(
    case_id: str,
    body: EscalateToPusatRequest,
    principal: Annotated[
        Principal,
        Depends(require_any_permission("complaints:create", "complaints:escalate")),
    ],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    """DEC-029 / API-520 lab — escalate this Case to Pusat (BQ-009: no ESCALATED)."""
    _ = idempotency_key
    units = OrgUnitResolver(session).resolve_case_units(case_id)
    enforce_org_scope_any(
        principal,
        (units.handling_unit_id, units.owner_unit_id),
        settings,
    )
    dto = service.escalate_to_pusat(
        EscalateToPusatCommand(
            case_id=case_id,
            reason=body.reason,
            actor_id=str(principal.user_id),
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/cm/cases/{case_id}/cancel-escalation-to-pusat")
def cancel_escalation_to_pusat(
    case_id: str,
    body: CancelEscalationToPusatRequest,
    principal: Annotated[
        Principal,
        Depends(require_any_permission("complaints:create", "complaints:escalate")),
    ],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    """Mode A lab — branch cancels DEC-029 escalate before Pusat claims handling."""
    _ = idempotency_key
    units = OrgUnitResolver(session).resolve_case_units(case_id)
    enforce_org_scope_any(
        principal,
        (units.handling_unit_id, units.owner_unit_id),
        settings,
    )
    dto = service.cancel_escalation_to_pusat(
        CancelEscalationToPusatCommand(
            case_id=case_id,
            reason=body.reason,
            actor_id=str(principal.user_id),
            actor_unit_id=_actor_unit(principal, session),
            actor_is_pusat=_actor_is_pusat(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/cm/cases/{case_id}/return-escalation")
def return_case_escalation(
    case_id: str,
    body: ReturnEscalationRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[CaseApplicationService, Depends(get_case_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
) -> DataResponse[CaseResponse]:
    """API-521 lab — Pusat returns this Case to the originating branch."""
    _ = idempotency_key
    _ = settings
    if not _actor_is_pusat(principal, session):
        raise PermissionDeniedError(
            "Only Pusat may return an escalated Case to the branch."
        )
    dto = service.return_escalation(
        ReturnEscalationCommand(
            case_id=case_id,
            return_note=body.return_note,
            actor_id=str(principal.user_id),
            actor_unit_id=_actor_unit(principal, session),
            actor_is_pusat=True,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


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
    actor_is_pusat = _actor_is_pusat(principal, session)
    party = (body.party or "").strip().upper()
    party_org = (
        units.owner_unit_id if party == "OWNER" else units.handling_unit_id
    )
    dto_case = _enforce_case_mutation_scope(
        principal=principal,
        session=session,
        settings=settings,
        service=service,
        case_id=case_id,
        branch_org=party_org,
    )
    handling_for_assert = (
        actor_unit
        if dto_case.escalated_to_pusat and actor_is_pusat and party == "HANDLING_UNIT"
        else units.handling_unit_id
    )
    assert_case_acceptance_authorized(
        principal,
        party=party,
        owner_unit_id=units.owner_unit_id,
        handling_unit_id=handling_for_assert,
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
            actor_is_pusat=actor_is_pusat,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


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
    _enforce_case_mutation_scope(
        principal=principal,
        session=session,
        settings=settings,
        service=service,
        case_id=case_id,
        branch_org=None,
        branch_orgs=(units.handling_unit_id, units.owner_unit_id),
    )
    note = body.note if body else None
    dto = service.close(
        CloseCaseCommand(
            case_id=case_id,
            actor_id=str(principal.user_id),
            note=note,
            actor_unit_id=_actor_unit(principal, session),
            actor_is_pusat=_actor_is_pusat(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))
