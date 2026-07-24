"""Queue resource FastAPI routes (TASK-064 / CAPABILITY-003 / API-360–364, 374–375)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status

from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import DataResponse, ErrorResponse
from app.modules.queue.api.controllers import QueueController
from app.modules.queue.api.dependencies import (
    get_queue_crud_service,
    get_queue_operations_service,
)
from app.modules.queue.api.requests import CreateQueueRequest, UpdateQueueRequest
from app.modules.queue.api.responses import QueueResponse
from app.modules.queue.application.services import (
    QueueCrudApplicationService,
    QueueOperationsApplicationService,
)

router = APIRouter(prefix="/api/v1/queues", tags=["Queues"])

_ERROR = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}


def get_queue_controller(
    service: Annotated[QueueCrudApplicationService, Depends(get_queue_crud_service)],
    operations: Annotated[
        QueueOperationsApplicationService, Depends(get_queue_operations_service)
    ],
) -> QueueController:
    return QueueController(service, operations=operations)


@router.post(
    "",
    response_model=DataResponse[QueueResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create queue",
    description=(
        "Create a visit-context Queue under an organization. "
        "Default status is CLOSED. Does not create Complaints."
    ),
    responses=_ERROR,
)
async def create_queue(
    payload: CreateQueueRequest,
    controller: Annotated[QueueController, Depends(get_queue_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[QueueResponse]:
    """API-360 — Create Queue."""
    return await controller.create(payload, ctx)


@router.get(
    "",
    response_model=DataResponse[list[QueueResponse]],
    status_code=status.HTTP_200_OK,
    summary="List queues by organization",
    description="List queues owned by organizationId (required query parameter).",
    responses=_ERROR,
)
async def list_queues(
    organization_id: Annotated[uuid.UUID, Query(alias="organizationId")],
    controller: Annotated[QueueController, Depends(get_queue_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[list[QueueResponse]]:
    """API-361 — List Queues."""
    return await controller.list(organization_id, ctx)


@router.get(
    "/{queue_id}",
    response_model=DataResponse[QueueResponse],
    status_code=status.HTTP_200_OK,
    summary="Get queue by id",
    description="Return a single Queue response DTO by queue_id.",
    responses=_ERROR,
)
async def get_queue(
    queue_id: uuid.UUID,
    controller: Annotated[QueueController, Depends(get_queue_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[QueueResponse]:
    """API-362 — Get Queue."""
    return await controller.get(queue_id, ctx)


@router.put(
    "/{queue_id}",
    response_model=DataResponse[QueueResponse],
    status_code=status.HTTP_200_OK,
    summary="Update queue",
    description=(
        "Update mutable Queue fields (name, description, policy, status). "
        "organizationId is immutable."
    ),
    responses=_ERROR,
)
async def update_queue(
    queue_id: uuid.UUID,
    payload: UpdateQueueRequest,
    controller: Annotated[QueueController, Depends(get_queue_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[QueueResponse]:
    """API-363 — Update Queue."""
    return await controller.update(queue_id, payload, ctx)


@router.delete(
    "/{queue_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete queue",
    description="Hard-delete a Queue (cascades tickets/counters at persistence).",
    response_class=Response,
    responses={
        204: {"description": "Deleted"},
        **_ERROR,
    },
)
async def delete_queue(
    queue_id: uuid.UUID,
    controller: Annotated[QueueController, Depends(get_queue_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> Response:
    """API-364 — Delete Queue."""
    return await controller.delete(queue_id, ctx)


@router.post(
    "/{queue_id}/open",
    response_model=DataResponse[QueueResponse],
    status_code=status.HTTP_200_OK,
    summary="Open queue",
    description="Set queue operational status to OPEN (accepts tickets / call-next).",
    responses=_ERROR,
)
async def open_queue(
    queue_id: uuid.UUID,
    controller: Annotated[QueueController, Depends(get_queue_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[QueueResponse]:
    """API-374 — Open Queue."""
    return await controller.open(queue_id, ctx)


@router.post(
    "/{queue_id}/close",
    response_model=DataResponse[QueueResponse],
    status_code=status.HTTP_200_OK,
    summary="Close queue",
    description="Set queue operational status to CLOSED (rejects new tickets).",
    responses=_ERROR,
)
async def close_queue(
    queue_id: uuid.UUID,
    controller: Annotated[QueueController, Depends(get_queue_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> DataResponse[QueueResponse]:
    """API-375 — Close Queue."""
    return await controller.close(queue_id, ctx)


__all__ = ["router"]
