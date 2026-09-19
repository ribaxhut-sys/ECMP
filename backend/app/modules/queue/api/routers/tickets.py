"""QueueTicket FastAPI routes (TASK-064 / CAPABILITY-003 / API-365–369, 376–381)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.core.auth import Principal, require_permissions
from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import DataResponse, ErrorResponse
from app.modules.queue.api.controllers import TicketController
from app.modules.queue.api.dependencies import (
    get_queue_crud_service,
    get_queue_operations_service,
)
from app.modules.queue.api.requests import CreateTicketRequest, UpdateTicketRequest
from app.modules.queue.api.responses import QueueTicketResponse
from app.modules.queue.application.services import (
    QueueCrudApplicationService,
    QueueOperationsApplicationService,
)

nested_router = APIRouter(prefix="/api/v1/queues", tags=["Queue Tickets"])
tickets_router = APIRouter(prefix="/api/v1/tickets", tags=["Queue Tickets"])
ops_queue_router = APIRouter(prefix="/api/v1/queues", tags=["Queue Operations"])
ops_tickets_router = APIRouter(prefix="/api/v1/tickets", tags=["Queue Operations"])

_ERROR = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}


def get_ticket_controller(
    service: Annotated[QueueCrudApplicationService, Depends(get_queue_crud_service)],
    operations: Annotated[
        QueueOperationsApplicationService, Depends(get_queue_operations_service)
    ],
) -> TicketController:
    return TicketController(service, operations=operations)


@nested_router.post(
    "/{queue_id}/tickets",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Issue queue ticket",
    description=(
        "Issue a WAITING ticket for an OPEN queue. Ticket number is generated. "
        "Does not create Complaints (separate lifecycle)."
    ),
    responses=_ERROR,
)
async def create_ticket(
    queue_id: uuid.UUID,
    payload: CreateTicketRequest,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("queue:manage"))],
) -> DataResponse[QueueTicketResponse]:
    """API-365 — Issue Ticket (CRUD path)."""
    _ = principal
    return await controller.create(queue_id, payload, ctx)


@nested_router.get(
    "/{queue_id}/tickets",
    response_model=DataResponse[list[QueueTicketResponse]],
    status_code=status.HTTP_200_OK,
    summary="List tickets for queue",
    description="List all tickets for a queue ordered by createdAt ascending.",
    responses=_ERROR,
)
async def list_tickets(
    queue_id: uuid.UUID,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[list[QueueTicketResponse]]:
    """API-366 — List Tickets."""
    _ = principal
    return await controller.list(queue_id, ctx)


@tickets_router.get(
    "/{ticket_id}",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Get ticket by id",
    description="Return a QueueTicket response DTO by ticket_id.",
    responses=_ERROR,
)
async def get_ticket(
    ticket_id: uuid.UUID,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[QueueTicketResponse]:
    """API-367 — Get Ticket."""
    _ = principal
    return await controller.get(ticket_id, ctx)


@tickets_router.put(
    "/{ticket_id}",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Update ticket",
    description=(
        "Update ticket priority and/or status via domain transition rules. "
        "Prefer operational endpoints for lifecycle actions."
    ),
    responses=_ERROR,
)
async def update_ticket(
    ticket_id: uuid.UUID,
    payload: UpdateTicketRequest,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> DataResponse[QueueTicketResponse]:
    """API-368 — Update Ticket."""
    _ = principal
    return await controller.update(ticket_id, payload, ctx)


@tickets_router.delete(
    "/{ticket_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete ticket",
    description="Hard-delete a queue ticket. Does not affect Complaints.",
    response_class=Response,
    responses={
        204: {"description": "Deleted"},
        **_ERROR,
    },
)
async def delete_ticket(
    ticket_id: uuid.UUID,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> Response:
    """API-369 — Delete Ticket."""
    _ = principal
    return await controller.delete(ticket_id, ctx)


@ops_queue_router.post(
    "/{queue_id}/issue-ticket",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Issue ticket (operation)",
    description=(
        "Operational issue: Domain generates ticket number (default A001…) "
        "and sets status WAITING. Queue must be OPEN."
    ),
    responses=_ERROR,
)
async def issue_ticket_operation(
    queue_id: uuid.UUID,
    payload: CreateTicketRequest,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("queue:manage"))],
) -> DataResponse[QueueTicketResponse]:
    """API-376 — Issue Ticket (operation)."""
    _ = principal
    return await controller.issue_ticket(queue_id, payload, ctx)


@ops_queue_router.post(
    "/{queue_id}/call-next",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Call next ticket",
    description=(
        "Select next WAITING ticket by queue policy and transition to CALLED. "
        "Returns 204 when the waiting list is empty."
    ),
    responses={
        204: {"description": "No waiting tickets"},
        **_ERROR,
    },
)
async def call_next_ticket(
    queue_id: uuid.UUID,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> DataResponse[QueueTicketResponse] | Response:
    """API-377 — Call Next."""
    _ = principal
    return await controller.call_next(queue_id, ctx)


@ops_tickets_router.post(
    "/{ticket_id}/recall",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Recall ticket",
    description="Re-announce a CALLED or SERVING ticket. Status unchanged.",
    responses=_ERROR,
)
async def recall_ticket(
    ticket_id: uuid.UUID,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> DataResponse[QueueTicketResponse]:
    """API-378 — Recall Ticket."""
    _ = principal
    return await controller.recall(ticket_id, ctx)


@ops_tickets_router.post(
    "/{ticket_id}/complete",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Complete ticket",
    description="CALLED / SERVING → COMPLETED (domain-validated).",
    responses=_ERROR,
)
async def complete_ticket(
    ticket_id: uuid.UUID,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> DataResponse[QueueTicketResponse]:
    """API-379 — Complete Ticket."""
    _ = principal
    return await controller.complete(ticket_id, ctx)


@ops_tickets_router.post(
    "/{ticket_id}/skip",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Skip ticket",
    description="WAITING / CALLED → SKIPPED (domain-validated).",
    responses=_ERROR,
)
async def skip_ticket(
    ticket_id: uuid.UUID,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> DataResponse[QueueTicketResponse]:
    """API-380 — Skip Ticket."""
    _ = principal
    return await controller.skip(ticket_id, ctx)


@ops_tickets_router.post(
    "/{ticket_id}/cancel",
    response_model=DataResponse[QueueTicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Cancel ticket",
    description="WAITING / CALLED / SERVING → CANCELLED (domain-validated).",
    responses=_ERROR,
)
async def cancel_ticket(
    ticket_id: uuid.UUID,
    controller: Annotated[TicketController, Depends(get_ticket_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> DataResponse[QueueTicketResponse]:
    """API-381 — Cancel Ticket."""
    _ = principal
    return await controller.cancel(ticket_id, ctx)


__all__ = [
    "nested_router",
    "ops_queue_router",
    "ops_tickets_router",
    "tickets_router",
]
