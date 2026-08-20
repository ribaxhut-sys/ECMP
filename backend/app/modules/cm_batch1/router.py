"""HTTP routes for CM Batch 1 — API-500…506 (FR-001 / FR-002 / FR-003)."""

from __future__ import annotations

from dataclasses import replace
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import (
    OrgUnitResolver,
    Principal,
    enforce_org_scope,
    require_any_permission,
    require_permissions,
)
from app.core.authorization.gates import (
    principal_may_auto_approve_intake_escalation,
    require_hq_intake_action,
)
from app.core.authorization.org_unit_guard import org_scope_enforcement_enabled
from app.core.authorization.visibility import is_pusat_unit
from app.core.config import Settings, get_settings
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.integrations.customer import build_customer_provider
from app.integrations.directory import LocalUserDirectory
from app.modules.attachment.permissions import ATTACHMENT_READ
from app.modules.attachment.registration import build_attachment_service
from app.modules.cm_batch1.attachment_repository import CmBatch1AttachmentRepository
from app.modules.cm_batch1.attachment_service import CmBatch1AttachmentService
from app.modules.cm_batch1.history import CmBatch1HistoryService
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.schemas import (
    Batch1AttachmentResponse,
    ComplaintBatch1Response,
    ConfirmCustomerRequest,
    ConfirmCustomerResponse,
    CreateComplaintBatch1Request,
    Customer360Batch1Response,
    CustomerSearchRequest,
    CustomerSearchResponse,
    DuplicateCheckRequest,
    DuplicateCheckResponse,
    DuplicateDecisionRequest,
    DuplicateDecisionResponse,
    HqAcceptAndScheduleRequest,
    HqAcceptRequest,
    HqCompleteRequest,
    HqReturnRequest,
    HqScheduleArrivalRequest,
    IntakeEscalationDecisionRequest,
    IntakeEscalationRequestBody,
    IntakeHistoryEntry,
    SupervisorQueueResponse,
    TransferAttachmentsRequest,
    TransferAttachmentsResponse,
    UserWorkStatsResponse,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_batch1.side_effects import CmBatch1SideEffectRecorder
from app.modules.timeline.repository import TimelineRepository

router = APIRouter(prefix="/api/v1/cm", tags=["CM-Batch1"])


def get_cm_batch1_service(
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CmBatch1Service:
    recorder = CmBatch1SideEffectRecorder(session)
    return CmBatch1Service(
        store=CmBatch1Repository(session),
        side_effects=recorder,
        customer_provider=build_customer_provider(
            settings.customer_provider,
            enterprise_base_url=settings.customer_provider_enterprise_base_url,
            session=session,
        ),
        user_directory=LocalUserDirectory(session),
    )


def get_cm_batch1_history_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> CmBatch1HistoryService:
    return CmBatch1HistoryService(
        TimelineRepository(session),
        user_directory=LocalUserDirectory(session),
    )


def get_cm_batch1_attachment_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> CmBatch1AttachmentService:
    recorder = CmBatch1SideEffectRecorder(session)
    return CmBatch1AttachmentService(
        attachment_service=build_attachment_service(session),
        repository=CmBatch1AttachmentRepository(session),
        complaints=CmBatch1Repository(session),
        side_effects=recorder,
    )

def _principal_key(principal: Principal) -> str:
    return str(principal.user_id)


@router.post(
    "/customers/search",
    response_model=DataResponse[CustomerSearchResponse],
    status_code=status.HTTP_200_OK,
    summary="Search Customer by exactly one key (API-502 / FR-002)",
)
def search_customer(
    body: CustomerSearchRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
) -> DataResponse[CustomerSearchResponse]:
    return DataResponse(
        data=service.search_customer(body, principal_key=_principal_key(principal))
    )


@router.post(
    "/customers/confirm",
    response_model=DataResponse[ConfirmCustomerResponse],
    status_code=status.HTTP_200_OK,
    summary="Confirm / lock CustomerId (API-503 / FR-002)",
)
def confirm_customer(
    body: ConfirmCustomerRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
) -> DataResponse[ConfirmCustomerResponse]:
    return DataResponse(
        data=service.confirm_customer(
            body.customer_id, principal_key=_principal_key(principal)
        )
    )


@router.get(
    "/customers/{customer_id}/batch1-360",
    response_model=DataResponse[Customer360Batch1Response],
    status_code=status.HTTP_200_OK,
    summary="Batch 1 Customer 360 minimum (API-504 / FR-002)",
)
def customer_360_minimum(
    customer_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
) -> DataResponse[Customer360Batch1Response]:
    _ = principal
    return DataResponse(data=service.customer_360_minimum(customer_id))


@router.post(
    "/customers/write-back",
    status_code=status.HTTP_400_BAD_REQUEST,
    summary="Forbidden Customer Master write-back (negative control)",
)
def forbid_write_back(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
) -> None:
    _ = principal
    service.reject_master_write_back()


@router.get(
    "/supervisor/queue",
    response_model=DataResponse[SupervisorQueueResponse],
    status_code=status.HTTP_200_OK,
    summary="Supervisor later-review / aging queue (API-513 / FR-001)",
)
def get_supervisor_queue(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    work_item_status: Annotated[
        str, Query(alias="workItemStatus")
    ] = "OPEN",
    aging_hours: Annotated[int, Query(alias="agingHours", ge=1, le=8760)] = 24,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> DataResponse[SupervisorQueueResponse]:
    _ = principal
    return DataResponse(
        data=service.get_supervisor_queue(
            work_item_status=work_item_status,
            aging_hours=aging_hours,
            limit=limit,
        )
    )


_ALLOWED_PRIORITIES = frozenset({"LOW", "MEDIUM", "HIGH", "CRITICAL"})
_ALLOWED_INTAKE_DISPOSITIONS = frozenset(
    {
        "BRANCH_CLOSED",
        "ESCALATE_PENDING_APPROVAL",
        "ESCALATE_APPROVED",
        "ESCALATE_REJECTED",
        "ESCALATE_CANCELLED",
        "RETURNED_TO_BRANCH",
        "HQ_SCHEDULED",
        "HQ_CLOSED",
        # Pseudo-value: any escalate-family state (Users directory drill-down).
        "ESCALATED",
        # Pseudo-value: not in the escalate family (dashboard waiting-assignment).
        "UNESCALATED",
    }
)


def _effective_org_unit(
    resolver: OrgUnitResolver, principal: Principal
) -> str | None:
    """Claim first; membership fallback fail-open (Mode A / offline lab)."""
    return resolver.resolve_principal(principal)


def _enforce_cm_org_or_pusat_hq(
    *,
    principal: Principal,
    resource_org: str | None,
    session: Session,
    settings: Settings,
) -> None:
    """Org-scope with Pusat HQ exception for escalated branch work."""
    if not org_scope_enforcement_enabled(settings):
        return
    effective = _effective_org_unit(OrgUnitResolver(session), principal)
    if is_pusat_unit(effective) or principal.has_any_role(
        "ADMIN", "ADMINISTRATOR", "SUPER_ADMIN", "HO_SCHEDULER",
        "HEAD_OFFICE_SCHEDULER", "SCHEDULER",
    ):
        return
    enforce_org_scope(principal, resource_org, settings)


@router.get(
    "/complaints",
    response_model=ListResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="List Aggregate Complaints (API-514 / FR-001) — coexistence read",
)
def list_complaints(
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    keyword: Annotated[str | None, Query(max_length=200)] = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    intake_disposition: Annotated[
        str | None, Query(alias="intakeDisposition")
    ] = None,
    priority: Annotated[str | None, Query()] = None,
    category: Annotated[str | None, Query(max_length=100)] = None,
    created_by: Annotated[str | None, Query(alias="createdBy")] = None,
    decided_by: Annotated[str | None, Query(alias="decidedBy")] = None,
) -> ListResponse[ComplaintBatch1Response]:
    pri = (priority or "").strip().upper() or None
    if pri is not None and pri not in _ALLOWED_PRIORITIES:
        pri = None
    st = (status_filter or "").strip().upper() or None
    if st is not None and st not in {
        "REGISTERED",
        "IN_PROGRESS",
        "CLOSED",
        "OPEN",
    }:
        st = None
    disp = (intake_disposition or "").strip().upper() or None
    if disp is not None and disp not in _ALLOWED_INTAKE_DISPOSITIONS:
        disp = None
    resolver = OrgUnitResolver(session)
    effective_org = _effective_org_unit(resolver, principal)
    vis_principal = replace(principal, org_unit_id=effective_org)
    items, total = service.list_complaints(
        page=page,
        page_size=page_size,
        keyword=keyword,
        status=st,
        intake_disposition=disp,
        priority=pri,
        category=category,
        created_by=(created_by or "").strip() or None,
        decided_by=(decided_by or "").strip() or None,
        principal=vis_principal,
        org_unit_id=effective_org,
    )
    return ListResponse(
        data=items,
        meta=PageMeta(page=page, pageSize=page_size, totalItems=total),
    )


@router.get(
    "/complaints/work-stats/{user_id}",
    response_model=DataResponse[UserWorkStatsResponse],
    status_code=status.HTTP_200_OK,
    summary="Per-user complaint work counters (Users directory panel, UM-BUG-006)",
)
def get_user_work_stats(
    user_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
) -> DataResponse[UserWorkStatsResponse]:
    _ = principal
    return DataResponse(data=service.work_stats_for_user(user_id))


@router.post(
    "/complaints",
    response_model=DataResponse[ComplaintBatch1Response],
    summary="Create Complaint Aggregate idempotent (API-500 / FR-001)",
)
def create_complaint(
    body: CreateComplaintBatch1Request,
    response: Response,
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    attachments: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    idempotency_key: Annotated[str | None, Header(alias="Idempotency-Key")] = None,
    channel_message_id: Annotated[
        str | None, Header(alias="X-Channel-Message-Id")
    ] = None,
) -> DataResponse[ComplaintBatch1Response]:
    # SECMIG-P4: pre-check declared unit before write (new create fail-closed).
    resolver = OrgUnitResolver(session)
    declared_org = resolver.resolve_declared(body.recording_unit_id)
    enforce_org_scope(principal, declared_org, settings)
    owning_unit_id = declared_org or _effective_org_unit(resolver, principal)
    # SECMIG-P4-001R2 FIX 2: authorize the *actual* replay target before any
    # create_replayed commit / outbox. Declared recordingUnitId alone is insufficient.
    def _authorize_replay(complaint_id: str) -> None:
        if not org_scope_enforcement_enabled(settings):
            return
        actual_org = resolver.resolve_cm_complaint(complaint_id)
        enforce_org_scope(principal, actual_org, settings)

    if org_scope_enforcement_enabled(settings):
        replay_complaint_id: str | None = None
        if idempotency_key and idempotency_key.strip():
            replay_complaint_id = service.peek_idempotent(idempotency_key.strip())
        if (
            replay_complaint_id is None
            and channel_message_id
            and channel_message_id.strip()
        ):
            replay_complaint_id = service.peek_by_channel_message(
                channel_message_id.strip()
            )
        if replay_complaint_id is not None:
            _authorize_replay(replay_complaint_id)
    result = service.create_complaint(
        body,
        request_id=idempotency_key or "",
        channel_message_id=channel_message_id,
        actor_id=_principal_key(principal),
        principal_key=_principal_key(principal),
        authorize_replay=_authorize_replay,
        owning_unit_id=owning_unit_id,
        auto_approve_escalation=principal_may_auto_approve_intake_escalation(
            principal
        ),
    )
    if (
        not result.replayed
        and body.staging_token
        and body.staging_token.strip()
    ):
        try:
            attachments.bind_staging_to_complaint(
                staging_token=body.staging_token.strip(),
                complaint_id=result.complaint_id,
                actor_id=_principal_key(principal),
            )
        except Exception:
            # E8 — Complaint remains; compensation via later-review work item.
            service.enqueue_later_review(
                customer_id=result.customer_id,
                reason="attachment_bind_failed",
                complaint_id=result.complaint_id,
            )
    response.status_code = (
        status.HTTP_200_OK if result.replayed else status.HTTP_201_CREATED
    )
    return DataResponse(data=result)


@router.get(
    "/complaints/{complaint_id}",
    response_model=DataResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="Get Complaint (API-501 / FR-001)",
)
def get_complaint(
    complaint_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintBatch1Response]:
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    _enforce_cm_org_or_pusat_hq(
        principal=principal,
        resource_org=resource_org,
        session=session,
        settings=settings,
    )
    return DataResponse(data=service.get_complaint(complaint_id))


@router.get(
    "/complaints/{complaint_id}/attachments",
    response_model=ListResponse[Batch1AttachmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List attachments for Aggregate complaint (API-509 / FR-004)",
)
def list_cm_complaint_attachments(
    complaint_id: str,
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_READ))],
    attachments: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 100,
) -> ListResponse[Batch1AttachmentResponse]:
    """Empty list is 200 — attachments are optional (FR-004)."""
    if org_scope_enforcement_enabled(settings):
        resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
        _enforce_cm_org_or_pusat_hq(
            principal=principal,
            resource_org=resource_org,
            session=session,
            settings=settings,
        )
    rows = attachments.list_for_complaint(complaint_id)
    start = (page - 1) * page_size
    return ListResponse(
        data=rows[start : start + page_size],
        meta=PageMeta(page=page, pageSize=page_size, totalItems=len(rows)),
    )


@router.get(
    "/complaints/{complaint_id}/history",
    response_model=ListResponse[IntakeHistoryEntry],
    status_code=status.HTTP_200_OK,
    summary="Chronological intake history (API-517 / FR-001)",
)
def get_complaint_history(
    complaint_id: str,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    history: Annotated[
        CmBatch1HistoryService, Depends(get_cm_batch1_history_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ListResponse[IntakeHistoryEntry]:
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    _enforce_cm_org_or_pusat_hq(
        principal=principal,
        resource_org=resource_org,
        session=session,
        settings=settings,
    )
    # 404 before reading the log — history is not an existence oracle.
    service.get_complaint(complaint_id)
    items = history.list_history(complaint_id)
    return ListResponse(
        data=items,
        meta=PageMeta(
            page=1, pageSize=max(1, len(items)), totalItems=len(items)
        ),
    )


@router.post(
    "/complaints/{complaint_id}/intake-escalation/decision",
    response_model=DataResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="Approve/reject intake escalation (API-515 / FR-001)",
)
def decide_intake_escalation(
    complaint_id: str,
    body: IntakeEscalationDecisionRequest,
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:escalate"))
    ],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintBatch1Response]:
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    enforce_org_scope(principal, resource_org, settings)
    return DataResponse(
        data=service.decide_intake_escalation(
            complaint_id,
            body,
            actor_id=_principal_key(principal),
        )
    )


@router.post(
    "/complaints/{complaint_id}/intake-escalation/request",
    response_model=DataResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="Re-request intake escalation after cancel/reject (API-518 lab / FR-001)",
)
def request_intake_escalation(
    complaint_id: str,
    body: IntakeEscalationRequestBody,
    principal: Annotated[
        Principal,
        Depends(require_any_permission("complaints:create", "complaints:escalate")),
    ],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintBatch1Response]:
    """From ESCALATE_CANCELLED / ESCALATE_REJECTED → ESCALATE_PENDING_APPROVAL.

    Prior Batalkan Eskalasi / Penolakan Eskalasi / Catatan Supervisor remain in
    description history (append-only). MUST NOT create Case.
    """
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    enforce_org_scope(principal, resource_org, settings)
    return DataResponse(
        data=service.request_intake_escalation(
            complaint_id,
            body,
            actor_id=_principal_key(principal),
            auto_approve_escalation=principal_may_auto_approve_intake_escalation(
                principal
            ),
        )
    )


@router.post(
    "/complaints/{complaint_id}/hq-accept",
    response_model=DataResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="HQ accept approved intake escalation (API-516 lab)",
)
def hq_accept_escalation(
    complaint_id: str,
    body: HqAcceptRequest,
    principal: Annotated[Principal, Depends(require_hq_intake_action)],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintBatch1Response]:
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    _enforce_cm_org_or_pusat_hq(
        principal=principal,
        resource_org=resource_org,
        session=session,
        settings=settings,
    )
    return DataResponse(
        data=service.accept_at_hq(
            complaint_id,
            body,
            actor_id=_principal_key(principal),
        )
    )


@router.post(
    "/complaints/{complaint_id}/hq-accept-and-schedule",
    response_model=DataResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="HQ accept and schedule arrival (lab) → HQ_SCHEDULED",
)
def hq_accept_and_schedule(
    complaint_id: str,
    body: HqAcceptAndScheduleRequest,
    principal: Annotated[Principal, Depends(require_hq_intake_action)],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintBatch1Response]:
    """Terima + jadwal sekaligus; cabang melihat sinyal untuk informasikan customer."""
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    _enforce_cm_org_or_pusat_hq(
        principal=principal,
        resource_org=resource_org,
        session=session,
        settings=settings,
    )
    return DataResponse(
        data=service.accept_and_schedule_at_hq(
            complaint_id,
            body,
            actor_id=_principal_key(principal),
        )
    )


@router.post(
    "/complaints/{complaint_id}/hq-return",
    response_model=DataResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="HQ return approved escalation to branch (API-519 lab / DEC-F4)",
)
def hq_return_escalation(
    complaint_id: str,
    body: HqReturnRequest,
    principal: Annotated[Principal, Depends(require_hq_intake_action)],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintBatch1Response]:
    """Tolak/kembalikan ke cabang dengan reason code + catatan (sebelum HQ accept)."""
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    _enforce_cm_org_or_pusat_hq(
        principal=principal,
        resource_org=resource_org,
        session=session,
        settings=settings,
    )
    return DataResponse(
        data=service.return_from_hq(
            complaint_id,
            body,
            actor_id=_principal_key(principal),
        )
    )


@router.post(
    "/complaints/{complaint_id}/hq-schedule-arrival",
    response_model=DataResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="Schedule customer arrival at HQ (API-517 lab)",
)
def hq_schedule_arrival(
    complaint_id: str,
    body: HqScheduleArrivalRequest,
    principal: Annotated[Principal, Depends(require_hq_intake_action)],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintBatch1Response]:
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    _enforce_cm_org_or_pusat_hq(
        principal=principal,
        resource_org=resource_org,
        session=session,
        settings=settings,
    )
    return DataResponse(
        data=service.schedule_hq_arrival(
            complaint_id,
            body,
            actor_id=_principal_key(principal),
        )
    )


@router.post(
    "/complaints/{complaint_id}/hq-complete",
    response_model=DataResponse[ComplaintBatch1Response],
    status_code=status.HTTP_200_OK,
    summary="HQ complete visit and close complaint (lab)",
)
def hq_complete_visit(
    complaint_id: str,
    body: HqCompleteRequest,
    principal: Annotated[Principal, Depends(require_hq_intake_action)],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintBatch1Response]:
    """Selesai di Pusat dengan catatan; status CLOSED. Kunjungan tetap di kalender hari itu."""
    resource_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
    _enforce_cm_org_or_pusat_hq(
        principal=principal,
        resource_org=resource_org,
        session=session,
        settings=settings,
    )
    return DataResponse(
        data=service.complete_at_hq(
            complaint_id,
            body,
            actor_id=_principal_key(principal),
        )
    )


@router.post(
    "/duplicates/check",
    response_model=DataResponse[DuplicateCheckResponse],
    status_code=status.HTTP_200_OK,
    summary="Check duplicate Complaint candidates (API-505 / FR-003)",
)
def check_duplicates(
    body: DuplicateCheckRequest,
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
) -> DataResponse[DuplicateCheckResponse]:
    return DataResponse(
        data=service.check_duplicates(body, actor_id=_principal_key(principal))
    )


@router.post(
    "/duplicates/decisions",
    response_model=DataResponse[DuplicateDecisionResponse],
    status_code=status.HTTP_200_OK,
    summary="Record duplicate decision / linkage (API-506 / FR-003)",
)
def record_duplicate_decision(
    body: DuplicateDecisionRequest,
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:create"))
    ],
    service: Annotated[CmBatch1Service, Depends(get_cm_batch1_service)],
    attachments: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[DuplicateDecisionResponse]:
    # SECMIG-P4-001R3 CR-1: any request that references survivingComplaintId
    # must pass OrgUnitGuard BEFORE service reads the surviving complaint,
    # copies customerId, persists the decision, writes outbox, or commits.
    # stagingToken is optional — do not gate authz on will_transfer / D-06.
    surviving = (body.surviving_complaint_id or "").strip()
    staging = (body.staging_token or "").strip()
    if surviving and org_scope_enforcement_enabled(settings):
        target_org = OrgUnitResolver(session).resolve_cm_complaint(surviving)
        enforce_org_scope(principal, target_org, settings)

    result = service.record_duplicate_decision(
        body, actor_id=_principal_key(principal)
    )
    # D-06 — link_existing with stagingToken transfers evidence (never discard).
    will_transfer = (
        body.decision == "link_existing" and bool(surviving) and bool(staging)
    )
    if will_transfer:
        attachments.transfer(
            TransferAttachmentsRequest(
                stagingToken=staging,
                survivingComplaintId=surviving,
            ),
            actor_id=_principal_key(principal),
        )
    return DataResponse(data=result)


@router.post(
    "/attachments/transfer",
    response_model=DataResponse[TransferAttachmentsResponse],
    status_code=status.HTTP_200_OK,
    summary="Transfer staged attachments to surviving Complaint (API-508 / FR-004 D-06)",
)
def transfer_staged_attachments(
    body: TransferAttachmentsRequest,
    principal: Annotated[
        Principal, Depends(require_permissions("complaints:create"))
    ],
    attachments: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[TransferAttachmentsResponse]:
    # SECMIG-P4-001R2 FIX 1: org-scope on surviving complaint before any rebind.
    if org_scope_enforcement_enabled(settings):
        target_org = OrgUnitResolver(session).resolve_cm_complaint(
            body.surviving_complaint_id
        )
        enforce_org_scope(principal, target_org, settings)
    return DataResponse(
        data=attachments.transfer(body, actor_id=_principal_key(principal))
    )
