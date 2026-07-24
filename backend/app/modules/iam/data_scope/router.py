"""Data Scope Foundation HTTP routes (API-354–355 / TASK-037)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import AuditAction
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.audit.hooks import write_audit
from app.modules.iam.data_scope.permissions import DATA_SCOPE_READ, DATA_SCOPE_UPDATE
from app.modules.iam.data_scope.repository import DataScopeRepository
from app.modules.iam.data_scope.schemas import (
    DataScopeReplaceRequest,
    DataScopeResponse,
)
from app.modules.iam.data_scope.service import DataScopeService

roles_data_scopes_router = APIRouter(prefix="/api/v1/roles", tags=["Data Scopes"])


def get_data_scope_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> DataScopeService:
    return DataScopeService(DataScopeRepository(session))


def _snapshot(scopes: list[DataScopeResponse]) -> dict:
    return {
        "scopes": [
            {
                "id": str(s.id),
                "scopeType": s.scope_type,
                "scopeValue": s.scope_value,
            }
            for s in scopes
        ]
    }


@roles_data_scopes_router.get(
    "/{role_id}/data-scopes",
    response_model=DataResponse[list[DataScopeResponse]],
    status_code=status.HTTP_200_OK,
    summary="List role data scopes",
)
def get_role_data_scopes(
    role_id: uuid.UUID,
    service: Annotated[DataScopeService, Depends(get_data_scope_service)],
    principal: Annotated[Principal, Depends(require_permissions(DATA_SCOPE_READ))],
) -> DataResponse[list[DataScopeResponse]]:
    """API-354 — list data scopes for a role."""
    _ = principal
    return DataResponse(data=service.get_role_scopes(role_id))


@roles_data_scopes_router.put(
    "/{role_id}/data-scopes",
    response_model=DataResponse[list[DataScopeResponse]],
    status_code=status.HTTP_200_OK,
    summary="Replace role data scopes",
)
def replace_role_data_scopes(
    role_id: uuid.UUID,
    payload: DataScopeReplaceRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[DataScopeService, Depends(get_data_scope_service)],
    principal: Annotated[Principal, Depends(require_permissions(DATA_SCOPE_UPDATE))],
) -> DataResponse[list[DataScopeResponse]]:
    """API-355 — replace full data-scope set for a role (empty clears)."""
    before = service.get_role_scopes(role_id)
    result = service.replace_role_scopes(role_id, payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="role.data_scopes.updated",
        entity_type="Role",
        action=AuditAction.UPDATE,
        entity_id=role_id,
        old_values=_snapshot(before),
        new_values=_snapshot(result),
        metadata={"scopeCount": len(result)},
    )
    return DataResponse(data=result)
