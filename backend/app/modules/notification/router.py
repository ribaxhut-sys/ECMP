"""Notification Foundation HTTP routes (API-327–335 / TASK-030)."""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import AuditAction
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.audit.hooks import write_audit
from app.modules.notification.permissions import (
    NOTIFICATION_CREATE,
    NOTIFICATION_DELETE,
    NOTIFICATION_READ,
    NOTIFICATION_UPDATE,
)
from app.modules.notification.repository import NotificationRepository
from app.modules.notification.schemas import (
    NotificationCreateRequest,
    NotificationQueueResponse,
    NotificationTemplateCreateRequest,
    NotificationTemplateResponse,
    NotificationTemplateUpdateRequest,
)
from app.modules.notification.service import NotificationService
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.service import SettingsService

templates_router = APIRouter(
    prefix="/api/v1/notification/templates", tags=["Notifications"]
)
queue_router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


def get_notification_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> NotificationService:
    settings = SettingsService(SettingsRepository(session))
    return NotificationService(
        repository=NotificationRepository(session),
        settings=settings,
    )


def _template_snapshot(row: NotificationTemplateResponse) -> dict:
    return {
        "id": str(row.id),
        "code": row.code,
        "name": row.name,
        "channel": row.channel,
        "subject": row.subject,
        "content": row.content,
        "isActive": row.is_active,
    }


# --- Template CRUD ---------------------------------------------------------


@templates_router.get(
    "",
    response_model=DataResponse[list[NotificationTemplateResponse]],
    status_code=status.HTTP_200_OK,
    summary="List notification templates",
)
def list_notification_templates(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[Principal, Depends(require_permissions(NOTIFICATION_READ))],
    active_only: Annotated[
        bool, Query(alias="activeOnly", description="Return active templates only")
    ] = False,
) -> DataResponse[list[NotificationTemplateResponse]]:
    """API-327 — list notification templates."""
    _ = principal
    return DataResponse(data=service.list_templates(active_only=active_only))


@templates_router.post(
    "",
    response_model=DataResponse[NotificationTemplateResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create notification template",
)
def create_notification_template(
    payload: NotificationTemplateCreateRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[
        Principal, Depends(require_permissions(NOTIFICATION_CREATE))
    ],
) -> DataResponse[NotificationTemplateResponse]:
    """API-328 — create a notification template."""
    result = service.create_template(payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="notification.template.created",
        entity_type="NotificationTemplate",
        action=AuditAction.CREATE,
        entity_id=result.id,
        new_values=_template_snapshot(result),
    )
    return DataResponse(data=result)


@templates_router.get(
    "/{template_id}",
    response_model=DataResponse[NotificationTemplateResponse],
    status_code=status.HTTP_200_OK,
    summary="Get notification template",
)
def get_notification_template(
    template_id: uuid.UUID,
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[Principal, Depends(require_permissions(NOTIFICATION_READ))],
) -> DataResponse[NotificationTemplateResponse]:
    """API-329 — get notification template by id."""
    _ = principal
    return DataResponse(data=service.get_template(template_id))


@templates_router.put(
    "/{template_id}",
    response_model=DataResponse[NotificationTemplateResponse],
    status_code=status.HTTP_200_OK,
    summary="Update notification template",
)
def update_notification_template(
    template_id: uuid.UUID,
    payload: NotificationTemplateUpdateRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[
        Principal, Depends(require_permissions(NOTIFICATION_UPDATE))
    ],
) -> DataResponse[NotificationTemplateResponse]:
    """API-330 — update notification template fields."""
    before = service.get_template(template_id)
    result = service.update_template(template_id, payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="notification.template.updated",
        entity_type="NotificationTemplate",
        action=AuditAction.UPDATE,
        entity_id=result.id,
        old_values=_template_snapshot(before),
        new_values=_template_snapshot(result),
    )
    return DataResponse(data=result)


@templates_router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft-delete notification template",
    response_class=Response,
)
def delete_notification_template(
    template_id: uuid.UUID,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[
        Principal, Depends(require_permissions(NOTIFICATION_DELETE))
    ],
) -> Response:
    """API-331 — soft-delete via is_active=False (no deleted_at on templates)."""
    before = service.get_template(template_id)
    service.delete_template(template_id)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="notification.template.deleted",
        entity_type="NotificationTemplate",
        action=AuditAction.DELETE,
        entity_id=template_id,
        old_values=_template_snapshot(before),
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --- Queue (no SEND endpoint) ----------------------------------------------


@queue_router.get(
    "",
    response_model=DataResponse[list[NotificationQueueResponse]],
    status_code=status.HTTP_200_OK,
    summary="List notification queue",
)
def list_notification_queue(
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[Principal, Depends(require_permissions(NOTIFICATION_READ))],
    status_filter: Annotated[
        Literal["PENDING", "PROCESSING", "SENT", "FAILED", "CANCELLED"] | None,
        Query(alias="status", description="Filter by queue status"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> DataResponse[list[NotificationQueueResponse]]:
    """API-333 — list notification queue rows (no send)."""
    _ = principal
    return DataResponse(data=service.list(status=status_filter, limit=limit))


@queue_router.post(
    "",
    response_model=DataResponse[NotificationQueueResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Enqueue notification",
)
def create_notification(
    payload: NotificationCreateRequest,
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[
        Principal, Depends(require_permissions(NOTIFICATION_CREATE))
    ],
) -> DataResponse[NotificationQueueResponse]:
    """API-332 — validate template, generate payload, insert PENDING queue row."""
    _ = principal
    return DataResponse(data=service.create(payload))


@queue_router.get(
    "/{queue_id}",
    response_model=DataResponse[NotificationQueueResponse],
    status_code=status.HTTP_200_OK,
    summary="Get notification queue item",
)
def get_notification_queue_item(
    queue_id: uuid.UUID,
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[Principal, Depends(require_permissions(NOTIFICATION_READ))],
) -> DataResponse[NotificationQueueResponse]:
    """API-334 — notification queue detail."""
    _ = principal
    return DataResponse(data=service.get(queue_id))


@queue_router.post(
    "/{queue_id}/cancel",
    response_model=DataResponse[NotificationQueueResponse],
    status_code=status.HTTP_200_OK,
    summary="Cancel pending notification",
)
def cancel_notification_queue_item(
    queue_id: uuid.UUID,
    service: Annotated[NotificationService, Depends(get_notification_service)],
    principal: Annotated[
        Principal, Depends(require_permissions(NOTIFICATION_UPDATE))
    ],
) -> DataResponse[NotificationQueueResponse]:
    """API-335 — cancel a PENDING queue item (no send endpoint exists)."""
    _ = principal
    return DataResponse(data=service.cancel(queue_id))
