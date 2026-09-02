"""REST API for Pengaduan Internal — domain terpisah dari F4 / Batch-1."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import OrgUnitResolver, Principal, require_permissions
from app.core.authorization.case_acceptance import (
    assert_case_acceptance_authorized,
    principal_is_case_agent,
)
from app.core.authorization.org_unit_guard import (
    enforce_org_scope,
    enforce_org_scope_any,
    org_scope_enforcement_enabled,
)
from app.core.authorization.visibility import is_pusat_unit
from app.core.config import Settings, get_settings
from app.core.enums import AuditAction
from app.core.errors import PermissionDeniedError, ValidationAppError
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.core.user_messages import m
from app.db.session import get_db_session
from app.integrations.directory import LocalUserDirectory
from app.modules.attachment.domain.enums import AggregateType
from app.modules.attachment.repository import AttachmentRepository
from app.modules.audit.hooks import resolve_actor_name, write_audit
from app.modules.internal_complaint.api.schemas import (
    AcceptanceResponse,
    CloseRequest,
    CreateInternalComplaintRequest,
    DecideTransferRequestRequest,
    DecideWithdrawRequestRequest,
    HistoryEventResponse,
    InternalComplaintResponse,
    InternalComplaintSummaryResponse,
    RecordAcceptanceRequest,
    RequestTransferRequest,
    ResendToPusatRequest,
    ResolutionResponse,
    ResolveRequest,
    ReturnForCompletionRequest,
    StartHandlingRequest,
    TransferRequest,
    UpdateStatusRequest,
    WithdrawRequest,
)
from app.modules.internal_complaint.application.dto import (
    CloseCommand,
    CreateInternalComplaintCommand,
    DecideTransferRequestCommand,
    DecideWithdrawRequestCommand,
    InternalComplaintDTO,
    RecordAcceptanceCommand,
    RequestTransferCommand,
    RequestWithdrawCommand,
    ResendToPusatCommand,
    ResolveCommand,
    ReturnForCompletionCommand,
    StartHandlingCommand,
    TransferCommand,
    UpdateStatusCommand,
    WithdrawCommand,
)
from app.modules.internal_complaint.application.pdf import (
    InternalPdfAttachment,
    InternalPdfSnapshot,
    internal_pdf_filename,
    render_internal_snapshot_pdf,
)
from app.modules.internal_complaint.application.related_aggregate import (
    resolve_related_aggregate,
)
from app.modules.internal_complaint.application.services import (
    InternalComplaintApplicationService,
)
from app.modules.internal_complaint.application.visibility import (
    assert_internal_complaint_visible,
)
from app.modules.internal_complaint.infrastructure.repository import (
    SqlAlchemyInternalComplaintRepository,
)

router = APIRouter(tags=["Internal-Complaints"])
logger = logging.getLogger(__name__)


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


_ADMIN_FAMILY_ROLES = ("ADMIN", "ADMINISTRATOR", "SUPER_ADMIN")


def _actor_is_admin(principal: Principal) -> bool:
    return principal.has_any_role(*_ADMIN_FAMILY_ROLES)


def _units_match(left: str | None, right: str | None) -> bool:
    a = OrgUnitResolver.normalize(left)
    b = OrgUnitResolver.normalize(right)
    return bool(a) and bool(b) and a == b


def _may_owner_withdraw(
    principal: Principal, dto: InternalComplaintDTO, session: Session
) -> bool:
    if str(principal.user_id) == dto.created_by:
        return True
    if _actor_is_admin(principal):
        return True
    unit = _actor_unit(principal, session)
    return bool(
        principal.has_permission("complaints:assign")
        and _units_match(unit, dto.owner_unit_id)
    )


def _enforce_internal_org_scope(
    principal: Principal, resource_org_unit_id: str | None, settings: Settings
) -> None:
    """Org-scope for deciding a transfer request — Admin family decides any unit.

    Mirrors cm_batch1's Pusat-HQ-exception pattern: Supervisor/Manager must
    still match the requester's own unit; Admin (holder of
    ``internal:escalate-decide`` regardless of unit membership) bypasses.
    """
    if not org_scope_enforcement_enabled(settings):
        return
    if principal.has_any_role(*_ADMIN_FAMILY_ROLES):
        return
    enforce_org_scope(principal, resource_org_unit_id, settings)


def _require_visible_internal_complaint(
    *,
    complaint_id: str,
    principal: Principal,
    service: InternalComplaintApplicationService,
    session: Session,
    settings: Settings,
) -> InternalComplaintDTO:
    """Load by id and apply the domain visibility floor (404, no leak).

    ``enforce_org_scope*`` is a no-op in Mode A (``ECMP_AUTH_MODE=dev``).
    This assert is mode-independent so a branch cannot mutate another
    unit's ticket by id — same contract as GET.
    """
    dto = service.get(complaint_id)
    assert_internal_complaint_visible(
        principal,
        dto,
        actor_unit_id=_actor_unit(principal, session),
        settings=settings,
    )
    return dto


def _display_names_for_dto(
    session: Session, dto: InternalComplaintDTO
) -> dict[str, str]:
    ids = {
        dto.created_by,
        dto.closed_by,
        dto.transfer_requested_by,
        dto.transfer_decided_by,
        dto.withdraw_requested_by,
        dto.withdraw_decided_by,
        dto.withdrawn_by,
        dto.completion_returned_by,
        dto.resolution.proposed_by if dto.resolution else None,
        *(e.actor_id for e in dto.history),
        *(a.actor_id for a in dto.acceptance_history),
        *(r.proposed_by for r in dto.resolution_history),
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
            proposedByName=names.get(r.proposed_by) if r.proposed_by else None,
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
        closedByName=names.get(dto.closed_by) if dto.closed_by else None,
        closedAt=dto.closed_at,
        createdAt=dto.created_at,
        createdBy=dto.created_by,
        createdByName=names.get(dto.created_by),
        updatedAt=dto.updated_at,
        transferRequestStatus=dto.transfer_request_status,
        transferRequestDestinationUnitId=dto.transfer_request_destination_unit_id,
        transferRequestReason=dto.transfer_request_reason,
        transferRequestedBy=dto.transfer_requested_by,
        transferRequestedByName=(
            names.get(dto.transfer_requested_by) if dto.transfer_requested_by else None
        ),
        transferRequestedAt=dto.transfer_requested_at,
        transferDecidedBy=dto.transfer_decided_by,
        transferDecidedByName=(
            names.get(dto.transfer_decided_by) if dto.transfer_decided_by else None
        ),
        transferDecidedAt=dto.transfer_decided_at,
        transferDecisionReason=dto.transfer_decision_reason,
        withdrawRequestStatus=dto.withdraw_request_status,
        withdrawRequestReason=dto.withdraw_request_reason,
        withdrawRequestedBy=dto.withdraw_requested_by,
        withdrawRequestedByName=(
            names.get(dto.withdraw_requested_by) if dto.withdraw_requested_by else None
        ),
        withdrawRequestedAt=dto.withdraw_requested_at,
        withdrawDecidedBy=dto.withdraw_decided_by,
        withdrawDecidedByName=(
            names.get(dto.withdraw_decided_by) if dto.withdraw_decided_by else None
        ),
        withdrawDecidedAt=dto.withdraw_decided_at,
        withdrawDecisionReason=dto.withdraw_decision_reason,
        withdrawnBy=dto.withdrawn_by,
        withdrawnByName=names.get(dto.withdrawn_by) if dto.withdrawn_by else None,
        withdrawnAt=dto.withdrawn_at,
        withdrawReason=dto.withdraw_reason,
        completionRequestStatus=dto.completion_request_status,
        completionReturnReason=dto.completion_return_reason,
        completionReturnedBy=dto.completion_returned_by,
        completionReturnedByName=(
            names.get(dto.completion_returned_by)
            if dto.completion_returned_by
            else None
        ),
        completionReturnedAt=dto.completion_returned_at,
    )


def _internal_attachment_manifest(
    session: Session, complaint_id: str
) -> list[InternalPdfAttachment]:
    try:
        aggregate_id = uuid.UUID(complaint_id)
    except ValueError:
        return []
    try:
        rows, _ = AttachmentRepository(session).list_by_aggregate(
            aggregate_type=AggregateType.INTERNAL_COMPLAINT.value,
            aggregate_id=aggregate_id,
            page=1,
            page_size=100,
        )
    except Exception:
        logger.exception("internal complaint pdf attachment list failed")
        return []
    return [
        InternalPdfAttachment(
            original_name=row.original_name or row.file_name or "",
            mime_type=row.mime_type or "",
            size_bytes=int(row.size_bytes or 0),
            checksum_sha256=row.checksum_sha256 or "",
            status=row.status or "",
        )
        for row in rows
    ]


def _audit_internal_export(
    session: Session,
    *,
    request: Request,
    principal: Principal,
    complaint_id: str,
    complaint_number: str,
    filename: str,
) -> None:
    try:
        try:
            entity_uuid = uuid.UUID(complaint_id)
        except ValueError:
            entity_uuid = None
        write_audit(
            session,
            request=request,
            principal=principal,
            event_type="internal_complaint.exported",
            entity_type="InternalComplaint",
            action=AuditAction.EXPORT,
            entity_id=entity_uuid,
            metadata={"complaintNumber": complaint_number, "filename": filename},
        )
    except Exception:
        logger.exception("internal complaint pdf export audit failed")


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
    pending_transfer_request: Annotated[
        bool | None, Query(alias="pendingTransferRequest")
    ] = None,
    pending_withdraw_request: Annotated[
        bool | None, Query(alias="pendingWithdrawRequest")
    ] = None,
    needs_receive: Annotated[bool | None, Query(alias="needsReceive")] = None,
) -> ListResponse[InternalComplaintSummaryResponse]:
    items, total = service.list_complaints(
        principal,
        page=page,
        page_size=page_size,
        status=status,
        org_unit_id=_actor_unit(principal, session),
        pending_transfer_request=pending_transfer_request,
        pending_withdraw_request=pending_withdraw_request,
        needs_receive=needs_receive,
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
                transferRequestStatus=i.transfer_request_status,
                withdrawRequestStatus=i.withdraw_request_status,
                completionRequestStatus=i.completion_request_status,
            )
            for i in items
        ],
        meta=PageMeta(page=page, pageSize=page_size, totalItems=total),
    )


@router.get("/api/v1/internal/complaints/inbox/pending-count")
def get_pending_inbox_count(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[int]:
    """Sidebar badge — incoming tickets awaiting receive at the caller's unit.

    Cabang: CREATED/ASSIGNED whose handling unit is the branch.
    Pusat: CREATED/ASSIGNED whose handling unit is a Pusat unit.
    Tickets the caller sent away (handling elsewhere) do not count.
    """
    count = service.count_pending_inbox(
        principal, org_unit_id=_actor_unit(principal, session)
    )
    return DataResponse(data=count)


@router.get("/api/v1/internal/complaints/transfer-requests/pending-count")
def get_pending_transfer_request_count(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[int]:
    """Sidebar badge — same UNIT/PUSAT/ALL visibility as the list (DEC-024)."""
    count = service.count_pending_transfer_requests(
        principal, org_unit_id=_actor_unit(principal, session)
    )
    return DataResponse(data=count)


@router.get("/api/v1/internal/complaints/withdraw-requests/pending-count")
def get_pending_withdraw_request_count(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
) -> DataResponse[int]:
    """Sidebar badge — pending branch withdraw requests visible to the caller."""
    count = service.count_pending_withdraw_requests(
        principal, org_unit_id=_actor_unit(principal, session)
    )
    return DataResponse(data=count)


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
    # Cabang create always sends Handling to Pusat (ASSIGNED) — no Agent
    # transfer-request hop. Pusat create keeps the assign vs request gate.
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
    if not is_pusat_unit(owner_unit):
        dest = dest if dest and is_pusat_unit(dest) else "PUSAT"
        if dest != OrgUnitResolver.normalize(dto.handling_unit_id):
            dto = service.transfer(
                TransferCommand(
                    complaint_id=dto.complaint_id,
                    destination_unit_id=dest,
                    actor_id=str(principal.user_id),
                    reason="Kirim ke Pusat saat dibuat",
                    actor_unit_id=owner_unit,
                    actor_is_admin=_actor_is_admin(principal),
                )
            )
    elif dest and dest != OrgUnitResolver.normalize(dto.handling_unit_id):
        if principal.has_permission("complaints:assign"):
            dto = service.transfer(
                TransferCommand(
                    complaint_id=dto.complaint_id,
                    destination_unit_id=dest,
                    actor_id=str(principal.user_id),
                    reason="Initial transfer on create",
                    actor_unit_id=owner_unit,
                    actor_is_admin=_actor_is_admin(principal),
                )
            )
        else:
            reason = (body.request_reason or "").strip()
            if not reason:
                raise ValidationAppError(
                    m("internal.transfer_request_reason_required"),
                    details={"field": "requestReason"},
                )
            dto = service.request_transfer(
                RequestTransferCommand(
                    complaint_id=dto.complaint_id,
                    destination_unit_id=dest,
                    reason=reason,
                    actor_id=str(principal.user_id),
                    actor_unit_id=owner_unit,
                    actor_is_admin=_actor_is_admin(principal),
                )
            )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/transfer-request")
def request_internal_transfer(
    complaint_id: str,
    body: RequestTransferRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    """(Re-)submit an Agent transfer request after REJECTED — 'boleh ajukan ulang'.

    Same permission as create (Agent-family) — Supervisor/Manager/Admin use
    /transfer directly and never need this endpoint.
    """
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    enforce_org_scope(principal, current.owner_unit_id, settings)
    dto = service.request_transfer(
        RequestTransferCommand(
            complaint_id=complaint_id,
            destination_unit_id=body.destination_unit_id,
            reason=body.reason,
            actor_id=str(principal.user_id),
            actor_unit_id=_actor_unit(principal, session),
            actor_is_admin=_actor_is_admin(principal),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/transfer-request/decision")
def decide_internal_transfer_request(
    complaint_id: str,
    body: DecideTransferRequestRequest,
    principal: Annotated[
        Principal, Depends(require_permissions("internal:escalate-decide"))
    ],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    """Supervisor / Manager / Admin decides a pending Agent transfer request."""
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    _enforce_internal_org_scope(principal, current.owner_unit_id, settings)
    dto = service.decide_transfer_request(
        DecideTransferRequestCommand(
            complaint_id=complaint_id,
            decision=body.decision,
            reason=body.reason,
            actor_id=str(principal.user_id),
            actor_unit_id=_actor_unit(principal, session),
            actor_is_admin=_actor_is_admin(principal),
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
    dto = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.get("/api/v1/internal/complaints/{complaint_id}/export")
def export_internal_complaint_pdf(
    complaint_id: str,
    request: Request,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    """API-550 — snapshot PDF of this Pengaduan Internal ticket.

    Same visibility as GET. Does not mutate status. Attachment bytes are not
    embedded. Cabang and Pusat who may view the ticket may download.
    """
    dto = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    names = _display_names_for_dto(session, dto)
    exported_at = datetime.now(UTC)
    actor_name = names.get(str(principal.user_id))
    if not actor_name:
        try:
            actor_name = resolve_actor_name(session, principal.user_id)
        except Exception:
            actor_name = None
    exporter = actor_name or str(principal.user_id)
    snapshot = InternalPdfSnapshot(
        complaint=dto,
        created_by_name=names.get(dto.created_by) if dto.created_by else None,
        closed_by_name=names.get(dto.closed_by) if dto.closed_by else None,
        withdrawn_by_name=names.get(dto.withdrawn_by) if dto.withdrawn_by else None,
        actor_names=names,
        attachments=_internal_attachment_manifest(session, dto.complaint_id),
        exported_by=exporter,
        exported_at=exported_at,
    )
    payload = render_internal_snapshot_pdf(snapshot)
    filename = internal_pdf_filename(dto.complaint_number, exported_at)
    _audit_internal_export(
        session,
        request=request,
        principal=principal,
        complaint_id=dto.complaint_id,
        complaint_number=dto.complaint_number,
        filename=filename,
    )
    return Response(
        content=payload,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


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
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
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
            actor_is_admin=_actor_is_admin(principal),
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
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
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


@router.post("/api/v1/internal/complaints/{complaint_id}/return-for-completion")
def return_internal_complaint_for_completion(
    complaint_id: str,
    body: ReturnForCompletionRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    """Pusat handling unit returns the ticket to the owner branch."""
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    actor_unit = _actor_unit(principal, session)
    enforce_org_scope(principal, current.handling_unit_id, settings)
    if not _units_match(actor_unit, current.handling_unit_id):
        raise PermissionDeniedError(m("internal.return_not_allowed"))
    dto = service.return_for_completion(
        ReturnForCompletionCommand(
            complaint_id=complaint_id,
            actor_id=str(principal.user_id),
            reason=body.reason,
            actor_unit_id=actor_unit,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/resend-to-pusat")
def resend_internal_complaint_to_pusat(
    complaint_id: str,
    body: ResendToPusatRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    """Owner unit resends to Pusat after completing documents."""
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    actor_unit = _actor_unit(principal, session)
    enforce_org_scope(principal, current.owner_unit_id, settings)
    if not _units_match(actor_unit, current.owner_unit_id):
        raise PermissionDeniedError(m("internal.resend_not_allowed"))
    dto = service.resend_to_pusat(
        ResendToPusatCommand(
            complaint_id=complaint_id,
            actor_id=str(principal.user_id),
            actor_unit_id=actor_unit,
            note=body.note,
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/withdraw")
def withdraw_internal_complaint(
    complaint_id: str,
    body: WithdrawRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    """Owner-unit cancel before Pusat receives — no Pusat notification."""
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    enforce_org_scope(principal, current.owner_unit_id, settings)
    if not _may_owner_withdraw(principal, current, session):
        raise PermissionDeniedError(m("internal.withdraw_not_allowed"))
    dto = service.withdraw(
        WithdrawCommand(
            complaint_id=complaint_id,
            actor_id=str(principal.user_id),
            reason=body.reason,
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/withdraw-request")
def request_internal_withdraw(
    complaint_id: str,
    body: WithdrawRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    enforce_org_scope(principal, current.owner_unit_id, settings)
    if not _may_owner_withdraw(principal, current, session):
        raise PermissionDeniedError(m("internal.withdraw_not_allowed"))
    dto = service.request_withdraw(
        RequestWithdrawCommand(
            complaint_id=complaint_id,
            actor_id=str(principal.user_id),
            reason=body.reason,
            actor_unit_id=_actor_unit(principal, session),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


@router.post("/api/v1/internal/complaints/{complaint_id}/withdraw-request/decision")
def decide_internal_withdraw_request(
    complaint_id: str,
    body: DecideWithdrawRequestRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    service: Annotated[
        InternalComplaintApplicationService, Depends(get_internal_complaint_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    can_decide = (
        _actor_is_admin(principal)
        or principal.has_permission("complaints:assign")
        or principal.has_permission("internal:escalate-decide")
    )
    if not can_decide:
        raise PermissionDeniedError(m("internal.withdraw_decide_denied"))
    _enforce_internal_org_scope(principal, current.handling_unit_id, settings)
    dto = service.decide_withdraw_request(
        DecideWithdrawRequestCommand(
            complaint_id=complaint_id,
            decision=body.decision,
            actor_id=str(principal.user_id),
            reason=body.reason,
            actor_unit_id=_actor_unit(principal, session),
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
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
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
            actor_is_admin=_actor_is_admin(principal),
        )
    )
    return DataResponse(data=_to_response(dto, session=session))


def _may_resolve_action(principal: Principal) -> bool:
    return principal_is_case_agent(principal) or principal.has_any_role(
        "SUPERVISOR",
        "BRANCH_SUPERVISOR",
        "MANAGER",
        "ADMIN",
        "ADMINISTRATOR",
        "SUPER_ADMIN",
    )


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
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
    actor_unit = _actor_unit(principal, session)
    action = (body.action or "").strip().upper()
    if action == "PROPOSE":
        _enforce_internal_org_scope(principal, current.handling_unit_id, settings)
    elif action in {"ACCEPT", "REJECT"}:
        _enforce_internal_org_scope(principal, current.owner_unit_id, settings)
    else:
        _enforce_internal_org_scope(principal, current.handling_unit_id, settings)
    if not _may_resolve_action(principal):
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
            actor_is_admin=_actor_is_admin(principal),
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
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[InternalComplaintResponse]:
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
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
    current = _require_visible_internal_complaint(
        complaint_id=complaint_id,
        principal=principal,
        service=service,
        session=session,
        settings=settings,
    )
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
