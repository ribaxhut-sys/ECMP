"""CAPABILITY-011 Attachment Management HTTP routes (API-323–326, 386–387).

Batch 1 (API-507…512) reuses these routes as the single attachment engine —
optional Batch 1 form fields dispatch to CmBatch1AttachmentService orchestration.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import OrgUnitResolver, Principal, enforce_org_scope, require_permissions
from app.core.config import Settings, get_settings
from app.core.enums import AuditAction
from app.core.errors import NotFoundError, ValidationAppError
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.core.user_messages import m
from app.db.session import get_db_session
from app.modules.attachment.domain.enums import AggregateType
from app.modules.attachment.permissions import (
    ATTACHMENT_CREATE,
    ATTACHMENT_DELETE,
    ATTACHMENT_READ,
)
from app.modules.attachment.registration import build_attachment_service
from app.modules.attachment.schemas import AttachmentResponse
from app.modules.attachment.service import AttachmentService
from app.modules.audit.hooks import write_audit
from app.modules.cm_batch1.attachment_repository import CmBatch1AttachmentRepository
from app.modules.cm_batch1.attachment_service import CmBatch1AttachmentService
from app.modules.cm_batch1.repository import CmBatch1Repository
from app.modules.cm_batch1.schemas import Batch1AttachmentResponse

router = APIRouter(prefix="/api/v1/attachments", tags=["Attachments"])
complaint_attachments_router = APIRouter(
    prefix="/api/v1/complaints", tags=["Attachments"]
)


def get_attachment_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AttachmentService:
    return build_attachment_service(session)


def get_cm_batch1_attachment_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> CmBatch1AttachmentService:
    return CmBatch1AttachmentService(
        attachment_service=build_attachment_service(session),
        repository=CmBatch1AttachmentRepository(session),
        complaints=CmBatch1Repository(session),
    )


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Upload attachment",
)
async def upload_attachment(
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    batch1: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_CREATE))],
    file: Annotated[UploadFile, File()],
    aggregate_type: Annotated[
        Literal["Complaint", "Queue", "Notification"] | None,
        Form(alias="aggregateType"),
    ] = None,
    aggregate_id: Annotated[uuid.UUID | None, Form(alias="aggregateId")] = None,
    staging_token: Annotated[str | None, Form(alias="stagingToken")] = None,
    complaint_id: Annotated[str | None, Form(alias="complaintId")] = None,
    customer_id: Annotated[str | None, Form(alias="customerId")] = None,
    classification: Annotated[str | None, Form()] = None,
    case_id: Annotated[str | None, Form(alias="caseId")] = None,
    supersedes_attachment_id: Annotated[
        str | None, Form(alias="supersedesAttachmentId")
    ] = None,
) -> DataResponse[Any]:
    """API-323 / API-507 — multipart upload (platform or Batch 1 orchestration)."""
    data = await file.read()
    batch1_requested = bool(
        staging_token
        or complaint_id
        or classification
        or case_id
        or supersedes_attachment_id
        or customer_id
    )
    if batch1_requested:
        result = batch1.upload(
            data=data,
            filename=file.filename,
            content_type=file.content_type,
            classification=classification or "customer_evidence",
            actor_id=str(principal.user_id),
            staging_token=staging_token,
            complaint_id=complaint_id,
            customer_id=customer_id,
            case_id=case_id,
            supersedes_attachment_id=supersedes_attachment_id,
            uploaded_by=principal.user_id,
        )
        return DataResponse(data=result)

    if aggregate_type is None or aggregate_id is None:
        raise ValidationAppError(
            m("storage.aggregate_type_id_required"),
            details={},
        )
    result_platform = service.upload(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        filename=file.filename,
        content_type=file.content_type,
        data=data,
        uploaded_by=principal.user_id,
    )
    return DataResponse(data=result_platform)


@router.get(
    "",
    response_model=ListResponse[AttachmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List attachments",
)
def list_attachments(
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_READ))],
    aggregate_type: Annotated[
        Literal["Complaint", "Queue", "Notification"] | None,
        Query(alias="aggregateType"),
    ] = None,
    aggregate_id: Annotated[
        uuid.UUID | None, Query(alias="aggregateId")
    ] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 50,
) -> ListResponse[AttachmentResponse]:
    """API-386 — paginated attachment metadata list."""
    _ = principal
    data, meta = service.list(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        page=page,
        page_size=page_size,
    )
    return ListResponse(data=data, meta=meta)


@router.get(
    "/{attachment_id}",
    status_code=status.HTTP_200_OK,
    summary="Get attachment metadata",
)
def get_attachment(
    attachment_id: uuid.UUID,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    batch1: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_READ))],
) -> DataResponse[Any]:
    """API-324 / API-510 — metadata including integrity hash."""
    _ = principal
    linked = batch1.try_get_by_platform_id(attachment_id)
    if linked is not None:
        return DataResponse(data=linked)
    linked = batch1.try_get(str(attachment_id))
    if linked is not None:
        return DataResponse(data=linked)
    return DataResponse(data=service.get(attachment_id))


@router.get(
    "/{attachment_id}/download",
    status_code=status.HTTP_200_OK,
    summary="Download attachment file",
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "Raw file bytes",
        }
    },
)
def download_attachment(
    attachment_id: uuid.UUID,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    batch1: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_READ))],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    """API-325 / API-511 — stream file bytes with original filename.

    SECMIG-P4 parity: org scope on approved read (after permission), resolved
    via the attachment's owning complaint (Foundation or Batch 1 Aggregate).
    Queue / Notification aggregate types are out of this fix's scope.
    """
    linked = batch1.try_get_by_platform_id(attachment_id) or batch1.try_get(
        str(attachment_id)
    )
    platform_id = batch1.resolve_platform_attachment_id(attachment_id)
    entity, data = service.download(platform_id)

    # CAPABILITY-011 is deliberately aggregate-agnostic (no FK to Complaint) —
    # only enforce when the attachment is actually bound to a resolvable
    # complaint; nothing to scope against otherwise.
    if linked is not None:
        if linked.complaint_id:
            try:
                resource_org = OrgUnitResolver(session).resolve_cm_complaint(
                    linked.complaint_id
                )
            except NotFoundError:
                pass
            else:
                enforce_org_scope(principal, resource_org, settings)
    elif entity.aggregate_type == AggregateType.COMPLAINT.value:
        try:
            resource_org = OrgUnitResolver(session).resolve_complaint(entity.aggregate_id)
        except NotFoundError:
            pass
        else:
            enforce_org_scope(principal, resource_org, settings)

    headers = {
        "Content-Disposition": f'attachment; filename="{entity.original_name}"',
        "X-Checksum-SHA256": entity.checksum_sha256,
    }
    return Response(
        content=data,
        media_type=entity.mime_type,
        headers=headers,
    )


@router.delete(
    "/{attachment_id}",
    summary="Logically delete / void attachment",
    response_model=None,
)
def delete_attachment(
    attachment_id: uuid.UUID,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    batch1: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_DELETE))],
    reason: Annotated[str | None, Query()] = None,
) -> Response | DataResponse[Batch1AttachmentResponse]:
    """API-326 / API-512 — platform soft-delete or Batch 1 void-with-reason."""
    linked = batch1.try_get_by_platform_id(attachment_id) or batch1.try_get(
        str(attachment_id)
    )
    if linked is not None:
        voided = batch1.void(
            linked.attachment_id,
            reason=reason or "void_via_api",
            actor_id=str(principal.user_id),
        )
        return DataResponse(data=voided)

    before = service.get(attachment_id)
    service.soft_delete(attachment_id)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="attachment.deleted",
        entity_type="Attachment",
        action=AuditAction.DELETE,
        entity_id=attachment_id,
        old_values={
            "id": str(before.id),
            "aggregateType": before.aggregate_type,
            "aggregateId": str(before.aggregate_id),
            "originalName": before.original_name,
            "mimeType": before.mime_type,
            "sizeBytes": before.size_bytes,
            "checksumSha256": before.checksum_sha256,
            "status": before.status,
        },
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@complaint_attachments_router.get(
    "/{id}/attachments",
    status_code=status.HTTP_200_OK,
    summary="List attachments for a complaint",
)
def list_complaint_attachments(
    id: uuid.UUID,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    batch1: Annotated[
        CmBatch1AttachmentService, Depends(get_cm_batch1_attachment_service)
    ],
    session: Annotated[Session, Depends(get_db_session)],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_READ))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 100,
) -> ListResponse[Any]:
    """API-387 / API-509 — Batch 1 Aggregate uses orchestration list."""
    _ = principal
    repo = CmBatch1Repository(session)
    if repo.get(str(id)) is not None:
        rows = batch1.list_for_complaint(str(id))
        return ListResponse(
            data=rows,
            meta=PageMeta(
                page=1,
                pageSize=max(len(rows), 1),
                totalItems=len(rows),
            ),
        )
    data, meta = service.list_for_complaint(id, page=page, page_size=page_size)
    return ListResponse(data=data, meta=meta)
