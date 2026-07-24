"""System Settings HTTP routes (API-320 / API-321 / API-322 / TASK-028)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import AuditAction
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.audit.hooks import write_audit
from app.modules.settings.repository import SettingsRepository
from app.modules.settings.schemas import SettingResponse, SettingUpdateRequest
from app.modules.settings.service import SettingsService

router = APIRouter(prefix="/api/v1/settings", tags=["Settings"])


def get_settings_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> SettingsService:
    return SettingsService(SettingsRepository(session))


@router.get(
    "/public",
    response_model=DataResponse[list[SettingResponse]],
    status_code=status.HTTP_200_OK,
    summary="List public settings",
)
def list_public_settings(
    service: Annotated[SettingsService, Depends(get_settings_service)],
) -> DataResponse[list[SettingResponse]]:
    """API-320 — PUBLIC visibility settings only (no authentication)."""
    return DataResponse(data=service.list_public())


@router.get(
    "",
    response_model=DataResponse[list[SettingResponse]],
    status_code=status.HTTP_200_OK,
    summary="List all settings",
)
def list_settings(
    service: Annotated[SettingsService, Depends(get_settings_service)],
    principal: Annotated[Principal, Depends(require_permissions("settings:read"))],
) -> DataResponse[list[SettingResponse]]:
    """API-321 — all settings (PUBLIC + PROTECTED). Requires settings:read."""
    _ = principal
    return DataResponse(data=service.list_all())


@router.put(
    "/{key}",
    response_model=DataResponse[SettingResponse],
    status_code=status.HTTP_200_OK,
    summary="Update setting value",
)
def update_setting(
    key: str,
    payload: SettingUpdateRequest,
    request: Request,
    session: Annotated[Session, Depends(get_db_session)],
    service: Annotated[SettingsService, Depends(get_settings_service)],
    principal: Annotated[
        Principal, Depends(require_permissions("settings:update"))
    ],
) -> DataResponse[SettingResponse]:
    """API-322 — update setting value with value_type validation."""
    before = service.get(key)
    result = service.update(key, payload)
    write_audit(
        session,
        request=request,
        principal=principal,
        event_type="setting.updated",
        entity_type="Setting",
        action=AuditAction.UPDATE,
        entity_id=result.id,
        old_values={
            "key": before.key,
            "value": before.value,
            "valueType": before.value_type,
        },
        new_values={
            "key": result.key,
            "value": result.value,
            "valueType": result.value_type,
        },
    )
    return DataResponse(data=result)
