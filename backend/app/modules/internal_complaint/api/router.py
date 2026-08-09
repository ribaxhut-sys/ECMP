"""REST API for Pengaduan Internal — domain terpisah dari F4 / Batch-1."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.auth import OrgUnitResolver, Principal, require_permissions
from app.core.authorization.case_acceptance import (
    assert_case_acceptance_authorized,
    assert_case_resolve_accept_authorized,
    principal_is_case_agent,
)
from app.core.authorization.org_unit_guard import enforce_org_scope, enforce_org_scope_any
from app.core.config import Settings, get_settings
from app.core.errors import PermissionDeniedError
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.core.user_messages import m
from app.db.session import get_db_session
from app.integrations.directory import LocalUserDirectory
from app.modules.internal_complaint.api.schemas import (
    AcceptanceResponse,
    CloseRequest,
    CreateInternalComplaintRequest,
    HistoryEventResponse,
    InternalComplaintResponse,
    InternalComplaintSummaryResponse,
    RecordAcceptanceRequest,
    ResolutionResponse,
    ResolveRequest,
    StartHandlingRequest,
    TransferRequest,
    UpdateStatusRequest,
)
from app.modules.internal_complaint.application.dto import (
    CloseCommand,
    CreateInternalComplaintCommand,
    InternalComplaintDTO,
    RecordAcceptanceCommand,
    ResolveCommand,
    StartHandlingCommand,
    TransferCommand,
    UpdateStatusCommand,
)
from app.modules.internal_complaint.application.related_aggregate import (
    resolve_related_aggregate,
)
from app.modules.internal_complaint.application.services import (
    InternalComplaintApplicationService,
)
from app.modules.internal_complaint.infrastructure.repository import (
    SqlAlchemyInternalComplaintRepository,
)

router = APIRouter(tags=["Internal-Complaints"])


def get_internal_complaint_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> InternalComplaintApplicationService:
    return InternalComplaintApplicationService(
        SqlAlchemyInternalComplaintRepository(session)
    )


def _actor_unit(principal: Principal, session: Session) -> str | None:
    resolver = OrgUnitResolver(session)
    claimed = resolver.normalize(principal.org_unit_id)
    if claimed:
        return claimed
    try:
        return resolver.resolve_principal_membership(principal.user_id)
    except Exception:
        return None


def _require_actor_unit(principal: Principal, session: Session) -> str:
    unit = _actor_unit(principal, session)
    if not unit:
        raise PermissionDeniedError(m("common.org_scope_denied"))
    return unit


def _display_names_for_dto(
    session: Session, dto: InternalComplaintDTO
) -> dict[str, str]:
    ids = {
        dto.created_by,
        dto.closed_by,
        *(e.actor_id for e in dto.history),
        *(a.actor_id for a in dto.acceptance_history),
    }
    wanted = {i for i in ids if i}
    if not wanted:
        return {}
    try:
        return LocalUserDirectory(session).display_names(wanted)
    except Exception:
        return {}


def _to_response(
    dto: InternalComplaintDTO,
    *,
    session: Session | None = None,
) -> InternalComplaintResponse:
    names: dict[str, str] = {}
    if session is not None:
        names = _display_names_for_dto(session, dto)

    def res(r):
        if r is None:
            return None
        return ResolutionResponse(
            resolutionId=r.resolution_id,
            resolutionCode=r.resolution_code,
            summary=r.summary,
            status=r.status,
            comment=r.comment,
            detail=r.detail,
            proposedBy=r.proposed_by,
            proposedAt=r.proposed_at,
            decidedBy=r.decided_by,
            decidedAt=r.decided_at,
            rejectionReason=r.rejection_reason,
        )

    def acc(a):
        if a is None:
            return None
        return AcceptanceResponse(
            acceptanceId=a.acceptance_id,
            party=a.party,
            decision=a.decision,
            actorId=a.actor_id,
            actorUnitId=a.actor_unit_id,
            decidedAt=a.decided_at,
            note=a.note,
        )

    def hist(e):
        return HistoryEventResponse(
            eventId=e.event_id,
            eventType=e.event_type,
            actorId=e.actor_id,
            actorName=names.get(e.actor_id),
            actorUnitId=e.actor_unit_id,
            occurredAt=e.occurred_at,
            note=e.note,
            sourceUnitId=e.source_unit_id,
            targetUnitId=e.target_unit_id,
        )

    return InternalComplaintResponse(
        complaintId=dto.complaint_id,
        complaintNumber=dto.complaint_number,
        status=dto.status,
        subject=dto.subject,
        description=dto.description,
        category=dto.category,
        subcategory=dto.subcategory,
        priority=dto.priority,
        chronology=dto.chronology,
        impact=dto.impact,
        relatedComplaintId=dto.related_complaint_id,
        relatedComplaintNumber=dto.related_complaint_number,
        ownerUnitId=dto.owner_unit_id,
        handlingUnitId=dto.handling_unit_id,
        resolution=res(dto.resolution),
        resolutionHistory=[res(r) for r in dto.resolution_history],
        handlingUnitAcceptance=acc(dto.handling_unit_acceptance),
        ownerAcceptance=acc(dto.owner_acceptance),
        acceptanceHistory=[acc(a) for a in dto.acceptance_history],
        history=[hist(e) for e in dto.history],
        closedBy=dto.closed_by,
        closedAt=dto.closed_at,
        createdAt=dto.created_at,
        createdBy=dto.created_by,
        createdByName=names.get(dto.created_by),
        updatedAt=dto.updated_at,
    )


@router.get("/api/v1/internal/complaints")
def list_internal_complaints(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    status: Annotated[str | None, Query()] = None,
) -> ListResponse[InternalComplaintSummaryResponse]:
    items, total = service.list_complaints(
        principal,
        page=page,
        page_size=page_size,
        status=status,
        org_unit_id=_actor_unit(principal, session),
    )
    creator_ids = {i.created_by for i in items if i.created_by}
    names = (
        LocalUserDirectory(session).display_names(creator_ids)
        if creator_ids
        else {}
    )
    return ListResponse(
        data=[
            InternalComplaintSummaryResponse(
                complaintId=i.complaint_id,
                complaintNumber=i.complaint_number,
                status=i.status,
                subject=i.subject,
                category=i.category,
                priority=i.priority,
                ownerUnitId=i.owner_unit_id,
                handlingUnitId=i.handling_unit_id,
                createdAt=i.created_at,
                createdBy=i.created_by,
                createdByName=names.get(i.created_by),
                relatedComplaintId=i.related_complaint_id,
                relatedComplaintNumber=i.related_complaint_number,
            )
            for i in items
        ],
        meta=PageMeta(page=page, pageSize=page_size, totalItems=total),
    )


@router.post("/api/v1/internal/complaints", status_code=201)
def create_internal_complaint(
    body: CreateInternalComplaintRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[InternalComplaintResponse]:
    # Owner = creator unit (server-side). Client ownerUnitId ignored.
    # relatedComplaintNumber from client is ignored — snapshot from Aggregate DB.
    # Optional handlingUnitId = initial Handling transfer (Cabang ↔ Pusat),
    # allowed under create so Agent can escalate without complaints:assign.
    owner_unit = _require_actor_unit(principal, session)
    related = resolve_related_aggregate(
        session,
        related_complaint_id=body.related_complaint_id,
        principal=principal,
        actor_unit_id=owner_unit,
    )
    dto = service.create(
        CreateInternalComplaintCommand(
            subject=body.subject,
            description=body.description,
            category=body.category,
            priority=body.priority,
            subcategory=None,
            chronology=body.chronology,
            impact=body.impact,
            actor_id=str(principal.user_id),
            owner_unit_id=owner_unit,
            actor_unit_id=owner_unit,
            related_complaint_id=(related.complaint_id if related else None),
            related_complaint_number=(
                related.complaint_number if related else None
            ),
        )
    )
    dest = OrgUnitResolver.normalize(body.handling_unit_id)
    if dest and dest != OrgUnitResolver.normalize(dto.handling_unit_id):
        dto = service.transfer(
            TransferCommand(
                complaint_id=dto.complaint_id,
                destination_unit_id=dest,
                actor_id=str(principal.user_id),
                reason="Initial transfer on create",
                actor_unit_id=owner_unit,
            )
        )
    return DataResponse(data=_to_response(dto, session=session))


@router.get("/api/v1/internal/complaints/{complaint_id}")
def get_internal_complaint(
    complaint_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    dto = service.get(complaint_id)
    enforce_org_scope_any(
        principal,
        (dto.handling_unit_id, dto.owner_unit_id),
        settings,
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/transfer")
def transfer_internal_complaint(
    complaint_id: str,
    body: TransferRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:assign"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    current = service.get(complaint_id)
    enforce_org_scope_any(
        principal,
        (current.handling_unit_id, current.owner_unit_id),
        settings,
    )
    dto = service.transfer(
        TransferCommand(
            complaint_id=complaint_id,
            destination_unit_id=body.destination_unit_id,
            actor_id=str(principal.user_id),
            reason=body.reason,
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/receive")
def receive_internal_complaint(
    complaint_id: str,
    body: StartHandlingRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    current = service.get(complaint_id)
    actor_unit = _actor_unit(principal, session)
    enforce_org_scope(principal, current.handling_unit_id, settings)
    dto = service.start_handling(
        StartHandlingCommand(
            complaint_id=complaint_id,
            actor_id=str(principal.user_id),
            note=body.note,
            actor_unit_id=actor_unit,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.patch("/api/v1/internal/complaints/{complaint_id}/status")
def update_internal_complaint_status(
    complaint_id: str,
    body: UpdateStatusRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    current = service.get(complaint_id)
    enforce_org_scope_any(
        principal,
        (current.handling_unit_id, current.owner_unit_id),
        settings,
    )
    dto = service.update_status(
        UpdateStatusCommand(
            complaint_id=complaint_id,
            to_status=body.to_status,
            actor_id=str(principal.user_id),
            destination_unit_id=body.destination_unit_id,
            reason=body.reason,
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/resolve")
def resolve_internal_complaint(
    complaint_id: str,
    body: ResolveRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    current = service.get(complaint_id)
    actor_unit = _actor_unit(principal, session)
    enforce_org_scope(principal, current.handling_unit_id, settings)
    action = (body.action or "").strip().upper()
    if action == "ACCEPT":
        assert_case_resolve_accept_authorized(
            principal,
            handling_unit_id=current.handling_unit_id,
            actor_unit_id=actor_unit,
            complaint_creator_id=current.created_by,
        )
    elif action == "PROPOSE" and not (
        principal_is_case_agent(principal)
        or principal.has_any_role(
            "SUPERVISOR",
            "BRANCH_SUPERVISOR",
            "MANAGER",
            "ADMIN",
            "ADMINISTRATOR",
        )
    ):
        raise PermissionDeniedError(m("case.resolve_accept_role_denied"))

    dto = service.resolve(
        ResolveCommand(
            complaint_id=complaint_id,
            action=body.action,
            comment=body.comment,
            resolution_code=body.resolution_code,
            summary=body.summary,
            detail=body.detail,
            rejection_reason=body.rejection_reason,
            actor_id=str(principal.user_id),
            actor_unit_id=actor_unit,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/acceptance")
def record_internal_acceptance(
    complaint_id: str,
    body: RecordAcceptanceRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[InternalComplaintResponse]:
    current = service.get(complaint_id)
    actor_unit = _actor_unit(principal, session)
    assert_case_acceptance_authorized(
        principal,
        party=body.party,
        owner_unit_id=current.owner_unit_id,
        handling_unit_id=current.handling_unit_id,
        actor_unit_id=actor_unit,
        complaint_creator_id=current.created_by,
    )
    dto = service.record_acceptance(
        RecordAcceptanceCommand(
            complaint_id=complaint_id,
            party=body.party,
            decision=body.decision,
            note=body.note,
            actor_id=str(principal.user_id),
            actor_unit_id=actor_unit,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/close")
def close_internal_complaint(
    complaint_id: str,
    body: CloseRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:close"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    current = service.get(complaint_id)
    enforce_org_scope_any(
        principal,
        (current.handling_unit_id, current.owner_unit_id),
        settings,
    )
    dto = service.close(
        CloseCommand(
            complaint_id=complaint_id,
            actor_id=str(principal.user_id),
            note=body.note,
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))
