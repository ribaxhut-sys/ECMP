"""Audit Log HTTP routes (API-336–337 / TASK-031)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.audit.permissions import AUDIT_READ
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditLogResponse
from app.modules.audit.service import AuditService

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])


def get_audit_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> AuditService:
    return AuditService(AuditRepository(session))


@router.get(
    "",
    response_model=DataResponse[list[AuditLogResponse]],
    status_code=status.HTTP_200_OK,
    summary="List audit logs",
)
def list_audit_logs(
    service: Annotated[AuditService, Depends(get_audit_service)],
    principal: Annotated[Principal, Depends(require_permissions(AUDIT_READ))],
    entity_type: Annotated[
        str | None, Query(alias="entityType", max_length=100)
    ] = None,
    entity_id: Annotated[uuid.UUID | None, Query(alias="entityId")] = None,
    actor_id: Annotated[uuid.UUID | None, Query(alias="actorId")] = None,
    action: Annotated[
        Literal["CREATE", "UPDATE", "DELETE", "LOGIN", "LOGOUT", "EXPORT", "IMPORT"]
        | None,
        Query(),
    ] = None,
    date_from: Annotated[datetime | None, Query(alias="dateFrom")] = None,
    date_to: Annotated[datetime | None, Query(alias="dateTo")] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> DataResponse[list[AuditLogResponse]]:
    """API-336 — filterable platform audit list (not Complaint Timeline)."""
    _ = principal
    return DataResponse(
        data=service.list(
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            action=action,
            date_from=date_from,
            date_to=date_to,
            limit=limit,
            offset=offset,
        )
    )


@router.get(
    "/{audit_id}",
    response_model=DataResponse[AuditLogResponse],
    status_code=status.HTTP_200_OK,
    summary="Get audit log",
)
def get_audit_log(
    audit_id: uuid.UUID,
    service: Annotated[AuditService, Depends(get_audit_service)],
    principal: Annotated[Principal, Depends(require_permissions(AUDIT_READ))],
) -> DataResponse[AuditLogResponse]:
    """API-337 — audit log detail."""
    _ = principal
    return DataResponse(data=service.get(audit_id))
