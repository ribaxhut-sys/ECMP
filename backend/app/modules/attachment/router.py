"""CAPABILITY-011 Attachment Management HTTP routes (API-323–326, 386–387)."""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import AuditAction
from app.core.schemas import DataResponse, ListResponse
from app.db.session import get_db_session
from app.modules.attachment.permissions import (
    ATTACHMENT_CREATE,
    ATTACHMENT_DELETE,
    ATTACHMENT_READ,
)
from app.modules.attachment.registration import build_attachment_service
from app.modules.attachment.schemas import AttachmentResponse
from app.modules.attachment.service import AttachmentService
from app.modules.audit.hooks import write_audit

router = APIRouter(prefix="/api/v1/attachments", tags=["Attachments"])
complaint_attachments_router = APIRouter(
    prefix="/api/v1/complaints", tags=["Attachments"]
)


def get_attachment_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AttachmentService:
    return build_attachment_service(session)


@router.post(
    "",
    response_model=DataResponse[AttachmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload attachment",
)
async def upload_attachment(
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_CREATE))],
    aggregate_type: Annotated[
        Literal["Complaint", "Queue", "Notification"],
        Form(alias="aggregateType"),
    ],
    aggregate_id: Annotated[uuid.UUID, Form(alias="aggregateId")],
    file: Annotated[UploadFile, File()],
) -> DataResponse[AttachmentResponse]:
    """API-323 — multipart upload bound to any aggregate."""
    data = await file.read()
    result = service.upload(
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        filename=file.filename,
        content_type=file.content_type,
        data=data,
        uploaded_by=principal.user_id,
    )
    return DataResponse(data=result)


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
    response_model=DataResponse[AttachmentResponse],
    status_code=status.HTTP_200_OK,
    summary="Get attachment metadata",
)
def get_attachment(
    attachment_id: uuid.UUID,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_READ))],
) -> DataResponse[AttachmentResponse]:
    """API-324 — attachment metadata only (no file bytes)."""
    _ = principal
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
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_READ))],
) -> Response:
    """API-325 — stream file bytes with original filename."""
    _ = principal
    entity, data = service.download(attachment_id)
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
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logically delete attachment",
    response_class=Response,
)
def delete_attachment(
    attachment_id: uuid.UUID,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_DELETE))],
) -> Response:
    """API-326 — logical delete (status=DELETED). Physical blob retained."""
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
    response_model=ListResponse[AttachmentResponse],
    status_code=status.HTTP_200_OK,
    summary="List attachments for a complaint",
)
def list_complaint_attachments(
    id: uuid.UUID,
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_READ))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 100,
) -> ListResponse[AttachmentResponse]:
    """API-387 — attachments bound to aggregate Complaint."""
    _ = principal
    data, meta = service.list_for_complaint(id, page=page, page_size=page_size)
    return ListResponse(data=data, meta=meta)
