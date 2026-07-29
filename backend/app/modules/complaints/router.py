"""Complaint HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import (
    OrgUnitResolver,
    Principal,
    enforce_org_scope,
    require_complaint_close,
    require_permissions,
)
from app.core.config import Settings, get_settings
from app.core.enums import ComplaintStatus
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.dependencies.events import get_event_dispatcher
from app.modules.complaints.repository import ComplaintRepository
from app.modules.complaints.schemas import (
    CloseComplaintRequest,
    CloseComplaintResult,
    ComplaintCreateRequest,
    ComplaintResponse,
    ComplaintStatusChangeRequest,
    ComplaintUpdateRequest,
)
from app.modules.complaints.service import ComplaintService
from app.modules.sla.repository import SlaRepository
from app.modules.sla.service import SlaService

router = APIRouter(prefix="/api/v1/complaints", tags=["Complaints"])

PriorityFilter = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def get_complaint_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ComplaintService:
    # Dispatcher comes from composition root; Notification registers there —
    # ComplaintService never imports Notification.
    return ComplaintService(
        ComplaintRepository(session),
        SlaService(SlaRepository(session)),
        event_dispatcher=get_event_dispatcher(),
    )


@router.post(
    "",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create complaint",
)
def create_complaint(
    payload: ComplaintCreateRequest,
    service: Annotated[ComplaintService, Depends(get_complaint_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
) -> DataResponse[ComplaintResponse]:
    created = service.create(payload, actor_user_id=principal.user_id)
    return DataResponse(data=created)


@router.get(
    "",
    response_model=ListResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="List complaints",
)
def list_complaints(
    service: Annotated[ComplaintService, Depends(get_complaint_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="pageSize", ge=1, le=100)] = 20,
    status_filter: Annotated[
        ComplaintStatus | None, Query(alias="status")
    ] = None,
    priority: Annotated[PriorityFilter | None, Query()] = None,
    customer_id: Annotated[uuid.UUID | None, Query(alias="customerId")] = None,
    branch_id: Annotated[uuid.UUID | None, Query(alias="branchId")] = None,
) -> ListResponse[ComplaintResponse]:
    _ = principal
    items, total = service.list(
        page=page,
        page_size=page_size,
        status=status_filter,
        priority=priority,
        customer_id=customer_id,
        branch_id=branch_id,
    )
    return ListResponse(
        data=items,
        meta=PageMeta(page=page, pageSize=page_size, totalItems=total),
    )


@router.get(
    "/{id}",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Get complaint by id",
)
def get_complaint(
    id: uuid.UUID,
    service: Annotated[ComplaintService, Depends(get_complaint_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintResponse]:
    """SECMIG-P4 / P4-001R: org scope on approved G1 read (after permission)."""
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
    return DataResponse(data=service.get(id))


@router.put(
    "/{id}",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Update complaint",
)
def update_complaint(
    id: uuid.UUID,
    payload: ComplaintUpdateRequest,
    service: Annotated[ComplaintService, Depends(get_complaint_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintResponse]:
    """SECMIG-P4-001R C-2: org scope after permission check."""
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
    updated = service.update(
        id,
        payload,
        actor_user_id=principal.user_id,
    )
    return DataResponse(data=updated)


@router.patch(
    "/{id}/status",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_200_OK,
    summary="Change complaint status",
)
def change_complaint_status(
    id: uuid.UUID,
    payload: ComplaintStatusChangeRequest,
    service: Annotated[ComplaintService, Depends(get_complaint_service)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[ComplaintResponse]:
    """Validated status transition (TASK-009). Invalid transitions → 400.

    SECMIG-P4: org scope enforced after permission check (Gate G1).
    """
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
    updated = service.change_status(
        id,
        payload,
        actor_user_id=principal.user_id,
    )
    return DataResponse(data=updated)


@router.post(
    "/{id}/close",
    response_model=DataResponse[CloseComplaintResult],
    status_code=status.HTTP_200_OK,
    summary="Close complaint",
)
def close_complaint(
    id: uuid.UUID,
    payload: CloseComplaintRequest,
    service: Annotated[ComplaintService, Depends(get_complaint_service)],
    principal: Annotated[Principal, Depends(require_complaint_close)],
    session: Annotated[Session, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> DataResponse[CloseComplaintResult]:
    """Explicit Complaint Closure after Final Resolution (API-312 / TASK-019).

    Does not close the escalation. Final Resolution must already exist.
    SECMIG-P4-001R C-1: org scope after permission check.
    """
    resource_org = OrgUnitResolver(session).resolve_complaint(id)
    enforce_org_scope(principal, resource_org, settings)
    closed = service.close(
        id,
        payload,
        actor_user_id=principal.user_id,
    )
    return DataResponse(data=closed)
