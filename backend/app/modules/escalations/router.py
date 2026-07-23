"""Escalation HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions, require_supervisor_escalate
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.escalations.repository import EscalationRepository
from app.modules.escalations.schemas import (
    EscalateComplaintRequest,
    EscalateComplaintResult,
    EscalationResponse,
)
from app.modules.escalations.service import EscalationService

router = APIRouter(prefix="/api/v1/complaints", tags=["Escalations"])


def get_escalation_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> EscalationService:
    return EscalationService(EscalationRepository(session))


@router.post(
    "/{id}/escalate",
    response_model=DataResponse[EscalateComplaintResult],
    status_code=status.HTTP_200_OK,
    summary="Escalate complaint",
)
def escalate_complaint(
    id: uuid.UUID,
    payload: EscalateComplaintRequest,
    service: Annotated[EscalationService, Depends(get_escalation_service)],
    principal: Annotated[Principal, Depends(require_supervisor_escalate)],
) -> DataResponse[EscalateComplaintResult]:
    result = service.escalate(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@router.get(
    "/{id}/escalations",
    response_model=DataResponse[list[EscalationResponse]],
    status_code=status.HTTP_200_OK,
    summary="List escalation history",
)
def list_escalations(
    id: uuid.UUID,
    service: Annotated[EscalationService, Depends(get_escalation_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[list[EscalationResponse]]:
    _ = principal
    return DataResponse(data=service.list_escalations(id))
