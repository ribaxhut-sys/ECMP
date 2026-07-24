"""Ticket-nested Complaint FastAPI routes (CAPABILITY-004 / API-395–396)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import DataResponse, ErrorResponse
from app.modules.complaint.api.controllers import ComplaintController
from app.modules.complaint.api.requests import CreateComplaintRequest
from app.modules.complaint.api.responses import ComplaintResponse
from app.modules.complaint.api.routers.complaints import get_complaint_controller

router = APIRouter(prefix="/api/v1/tickets", tags=["Complaint Domain"])

_ERROR = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}


@router.get(
    "/{ticket_id}/complaints",
    response_model=DataResponse[list[ComplaintResponse]],
    status_code=status.HTTP_200_OK,
    summary="List complaints by queue ticket",
    operation_id="listComplaintsByTicket",
    description=(
        "List Complaints linked to a visit-context queue ticket id. "
        "Does not load Queue entities."
    ),
    responses=_ERROR,
)
async def list_complaints_by_ticket(
    ticket_id: uuid.UUID,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[list[ComplaintResponse]]:
    """API-395 — List Complaints by Ticket."""
    return await controller.list_by_ticket(ticket_id, ctx)


@router.post(
    "/{ticket_id}/complaints",
    response_model=DataResponse[ComplaintResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create complaint for queue ticket",
    operation_id="createComplaintForTicket",
    description=(
        "Create a Complaint bound to the path ticket id (visit context). "
        "Body queueTicketId is optional and overridden by the path."
    ),
    responses=_ERROR,
)
async def create_complaint_for_ticket(
    ticket_id: uuid.UUID,
    payload: CreateComplaintRequest,
    controller: Annotated[ComplaintController, Depends(get_complaint_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[ComplaintResponse]:
    """API-396 — Create Complaint for Ticket."""
    return await controller.create(payload, ctx, queue_ticket_id=ticket_id)


__all__ = ["router"]
