"""Complaint HTTP routes."""

from __future__ import annotations

import uuid
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import Principal, require_permissions
from app.core.enums import ComplaintStatus
from app.core.schemas import DataResponse, ListResponse, PageMeta
from app.db.session import get_db_session
from app.modules.complaints.repository import ComplaintRepository
from app.modules.complaints.schemas import (
    ComplaintCreateRequest,
    ComplaintResponse,
    ComplaintUpdateRequest,
)
from app.modules.complaints.service import ComplaintService

router = APIRouter(prefix="/api/v1/complaints", tags=["Complaints"])

PriorityFilter = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def get_complaint_service(
    session: Annotated[Session, Depends(get_db_session)],
) -> ComplaintService:
    return ComplaintService(ComplaintRepository(session))


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
) -> DataResponse[ComplaintResponse]:
    _ = principal
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
) -> DataResponse[ComplaintResponse]:
    updated = service.update(
        id,
        payload,
        actor_user_id=principal.user_id,
    )
    return DataResponse(data=updated)
