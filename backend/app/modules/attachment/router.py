"""Attachment Management HTTP routes (API-323–325 / TASK-029)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import AuditAction
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.attachment.permissions import (
    ATTACHMENT_CREATE,
    ATTACHMENT_DELETE,
    ATTACHMENT_READ,
)
from app.modules.attachment.repository import AttachmentRepository
from app.modules.attachment.schemas import AttachmentResponse
from app.modules.attachment.service import AttachmentService
from app.modules.audit.hooks import write_audit
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService

router = APIRouter(prefix="/api/v1/attachments", tags=["Attachments"])


def get_attachment_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AttachmentService:
    settings = SettingsService(SettingsRepository(session))
    return AttachmentService(
        repository=AttachmentRepository(session),
        settings=settings,
    )


@router.post(
    "",
    response_model=DataResponse[AttachmentResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload attachment",
)
async def upload_attachment(
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_CREATE))],
    object_type: Annotated[str, Form(alias="objectType")],
    object_id: Annotated[uuid.UUID, Form(alias="objectId")],
    file: Annotated[UploadFile, File()],
) -> DataResponse[AttachmentResponse]:
    """API-323 — multipart upload bound to any domain object."""
    data = await file.read()
    result = service.upload(
        object_type=object_type,
        object_id=object_id,
        filename=file.filename,
        content_type=file.content_type,
        data=data,
        uploaded_by=principal.user_id,
    )
    return DataResponse(data=result)


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
    row, data = service.download(attachment_id)
    headers = {
        "Content-Disposition": f'attachment; filename="{row.filename}"',
        "X-Checksum-SHA256": row.checksum,
    }
    return Response(
        content=data,
        media_type=row.mime_type,
        headers=headers,
    )


@router.delete(
    "/{attachment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete attachment",
    response_class=Response,
)
def delete_attachment(
    attachment_id: uuid.UUID,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[AttachmentService, Depends(get_attachment_service)],
    principal: Annotated[Principal, Depends(require_permissions(ATTACHMENT_DELETE))],
) -> Response:
    """API-326 — soft delete (DB row retained with deleted_at)."""
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
            "objectType": before.object_type,
            "objectId": str(before.object_id),
            "filename": before.filename,
            "mimeType": before.mime_type,
            "sizeBytes": before.size_bytes,
            "checksum": before.checksum,
        },
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
