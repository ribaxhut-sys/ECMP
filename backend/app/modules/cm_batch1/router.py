"""HTTP routes for CM Batch 1 — API-500…506 (FR-001 / FR-002 / FR-003)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session

from app.core.auth import OrgUnitResolver, Principal, enforce_org_scope, require_permissions
from app.core.authorization.org_unit_guard import org_scope_enforcement_enabled
from app.core.config import Settings, get_settings
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.integrations.customer import build_customer_provider
from app.modules.attachment.registration import build_attachment_service
from app.modules.cm_batch1.attachment_repository import CmBatch1AttachmentRepository
from app.modules.cm_batch1.attachment_service import CmBatch1AttachmentService
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.schemas import (
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
    SupervisorQueueResponse,
    TransferAttachmentsRequest,
    TransferAttachmentsResponse,
)
from app.modules.cm_batch1.service import CmBatch1Service
from app.modules.cm_batch1.side_effects import CmBatch1SideEffectRecorder

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
        ),
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


@router.post(
    "/complaints",
    response_model=DataResponse[ComplaintBatch1Response],
    summary="Create Complaint Aggregate idempotent (API-500 / FR-001) — no Case",
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
    declared_org = OrgUnitResolver(session).resolve_declared(body.recording_unit_id)
    enforce_org_scope(principal, declared_org, settings)
    # SECMIG-P4-001R2 FIX 2: authorize the *actual* replay target before any
    # create_replayed commit / outbox. Declared recordingUnitId alone is insufficient.
    def _authorize_replay(complaint_id: str) -> None:
        if not org_scope_enforcement_enabled(settings):
            return
        actual_org = OrgUnitResolver(session).resolve_cm_complaint(complaint_id)
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
    enforce_org_scope(principal, resource_org, settings)
    return DataResponse(data=service.get_complaint(complaint_id))


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
