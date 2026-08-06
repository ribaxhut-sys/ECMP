"""Escalation HTTP routes (API-207/208 + API-301..304 + API-313)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import (
    OrgUnitResolver,
    Principal,
    enforce_org_scope,
    require_escalation_close,
    require_escalation_review,
    require_permissions,
    require_supervisor_escalate,
)
from app.core.config import Settings, get_settings
from app.core.schemas import DataResponse
from app.db.session import get_db_session
from app.modules.escalations.repository import EscalationRepository
from app.modules.escalations.schemas import (
    CloseEscalationRequest,
    CloseEscalationResult,
    EscalateComplaintRequest,
    EscalateComplaintResult,
    EscalationRequestCreate,
    EscalationRequestResult,
    EscalationResponse,
    EscalationReviewRequest,
    EscalationReviewResult,
)
from app.modules.escalations.service import EscalationService

# Nested under /api/v1/complaints
complaints_router = APIRouter(prefix="/api/v1/complaints", tags=["Escalations"])

# Top-level /api/v1/escalations/{id} (API-302..304, API-313)
escalations_router = APIRouter(prefix="/api/v1/escalations", tags=["Escalations"])


def get_escalation_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> EscalationService:
    return EscalationService(EscalationRepository(session))


@complaints_router.post(
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
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[EscalateComplaintResult]:
    """SECMIG-P4 parity: org scope after permission check, before mutation."""
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
    result = service.escalate(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@complaints_router.post(
    "/{id}/escalations",
    response_model=DataResponse[EscalationRequestResult],
    status_code=status.HTTP_200_OK,
    summary="Request escalation (Branch → Head Office)",
)
def request_escalation(
    id: uuid.UUID,
    payload: EscalationRequestCreate,
    service: Annotated[EscalationService, Depends(get_escalation_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[EscalationRequestResult]:
    """API-301 — create Escalation Request (status REQUESTED).

    SECMIG-P4 parity: org scope after permission check, before mutation.
    """
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
    result = service.request_escalation(
        id, payload, actor_user_id=principal.user_id
    )
    return DataResponse(data=result)


@complaints_router.get(
    "/{id}/escalations",
    response_model=DataResponse[list[EscalationResponse]],
    status_code=status.HTTP_200_OK,
    summary="List escalation history",
)
def list_escalations(
    id: uuid.UUID,
    service: Annotated[EscalationService, Depends(get_escalation_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[list[EscalationResponse]]:
    """SECMIG-P4 parity: org scope on approved read (after permission)."""
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
    return DataResponse(data=service.list_escalations(id))


@escalations_router.get(
    "/{id}",
    response_model=DataResponse[EscalationResponse],
    status_code=status.HTTP_200_OK,
    summary="Get escalation by id",
)
def get_escalation(
    id: uuid.UUID,
    service: Annotated[EscalationService, Depends(get_escalation_service)],
    principal: Annotated[Principal, Depends(require_permissions("escalations:read"))],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[EscalationResponse]:
    """API-302 — get escalation detail by id.

    SECMIG-P4 parity: org scope on approved read (after permission), resolved
    via the escalation's parent complaint.
    """
    resource_org = OrgUnitResolver(session).resolve_escalation(id)
    enforce_org_scope(principal, resource_org, settings)
    return DataResponse(data=service.get_escalation(id))


@escalations_router.post(
    "/{id}/approve",
    response_model=DataResponse[EscalationReviewResult],
    status_code=status.HTTP_200_OK,
    summary="Approve escalation request",
)
def approve_escalation(
    id: uuid.UUID,
    payload: EscalationReviewRequest,
    service: Annotated[EscalationService, Depends(get_escalation_service)],
    principal: Annotated[Principal, Depends(require_escalation_review)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[EscalationReviewResult]:
    """API-303 — approve REQUESTED escalation (HO Scheduler / Admin).

    SECMIG-P4 parity: org scope after permission check, before mutation.
    """
    resource_org = OrgUnitResolver(session).resolve_escalation(id)
    enforce_org_scope(principal, resource_org, settings)
    result = service.approve(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@escalations_router.post(
    "/{id}/reject",
    response_model=DataResponse[EscalationReviewResult],
    status_code=status.HTTP_200_OK,
    summary="Reject escalation request",
)
def reject_escalation(
    id: uuid.UUID,
    payload: EscalationReviewRequest,
    service: Annotated[EscalationService, Depends(get_escalation_service)],
    principal: Annotated[Principal, Depends(require_escalation_review)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[EscalationReviewResult]:
    """API-304 — reject REQUESTED escalation (HO Scheduler / Admin).

    SECMIG-P4 parity: org scope after permission check, before mutation.
    """
    resource_org = OrgUnitResolver(session).resolve_escalation(id)
    enforce_org_scope(principal, resource_org, settings)
    result = service.reject(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


@escalations_router.post(
    "/{id}/close",
    response_model=DataResponse[CloseEscalationResult],
    status_code=status.HTTP_200_OK,
    summary="Close escalation",
)
def close_escalation(
    id: uuid.UUID,
    payload: CloseEscalationRequest,
    service: Annotated[EscalationService, Depends(get_escalation_service)],
    principal: Annotated[Principal, Depends(require_escalation_close)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[CloseEscalationResult]:
    """API-313 — explicit Escalation Closure after Complaint Closure (TASK-020).

    SECMIG-P4 parity: org scope after permission check, before mutation.
    """
    resource_org = OrgUnitResolver(session).resolve_escalation(id)
    enforce_org_scope(principal, resource_org, settings)
    result = service.close(id, payload, actor_user_id=principal.user_id)
    return DataResponse(data=result)


# Back-compat export used by api.router
router = complaints_router
