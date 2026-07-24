"""SLA HTTP routes (API-314 complaint SLA; API-315–317 policies)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.sla.repository import SlaRepository
from app.modules.sla.schemas import (
    SlaPolicyCreateRequest,
    SlaPolicyResponse,
    SlaRecordResponse,
)
from app.modules.sla.service import SlaService

router = APIRouter(prefix="/api/v1/complaints", tags=["SLA"])
policies_router = APIRouter(prefix="/api/v1/sla/policies", tags=["SLA"])


def get_sla_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> SlaService:
    return SlaService(SlaRepository(session))


@router.get(
    "/{id}/sla",
    response_model=DataResponse[SlaRecordResponse],
    status_code=status.HTTP_200_OK,
    summary="Get complaint SLA",
)
def get_complaint_sla(
    id: uuid.UUID,
    service: Annotated[SlaService, Depends(get_sla_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[SlaRecordResponse]:
    """API-314 — read-only SLA foundation for Complaint Detail."""
    _ = principal
    return DataResponse(data=service.get_for_complaint(id))


@policies_router.get(
    "",
    response_model=DataResponse[list[SlaPolicyResponse]],
    status_code=status.HTTP_200_OK,
    summary="List SLA policies",
)
def list_sla_policies(
    service: Annotated[SlaService, Depends(get_sla_service)],
    principal: Annotated[Principal, Depends(require_permissions("sla:read"))],
) -> DataResponse[list[SlaPolicyResponse]]:
    """API-315 — list configurable SLA policies."""
    _ = principal
    return DataResponse(data=service.list_policies())


@policies_router.post(
    "",
    response_model=DataResponse[SlaPolicyResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create SLA policy",
)
def create_sla_policy(
    payload: SlaPolicyCreateRequest,
    service: Annotated[SlaService, Depends(get_sla_service)],
    principal: Annotated[Principal, Depends(require_permissions("sla:manage"))],
) -> DataResponse[SlaPolicyResponse]:
    """API-316 — create an inactive SLA policy (activate via API-317)."""
    _ = principal
    return DataResponse(data=service.create_policy(payload))


@policies_router.put(
    "/{id}/activate",
    response_model=DataResponse[SlaPolicyResponse],
    status_code=status.HTTP_200_OK,
    summary="Activate SLA policy",
)
def activate_sla_policy(
    id: uuid.UUID,
    service: Annotated[SlaService, Depends(get_sla_service)],
    principal: Annotated[Principal, Depends(require_permissions("sla:manage"))],
) -> DataResponse[SlaPolicyResponse]:
    """API-317 — make this the sole active policy (future complaints only)."""
    _ = principal
    return DataResponse(data=service.activate_policy(id))
