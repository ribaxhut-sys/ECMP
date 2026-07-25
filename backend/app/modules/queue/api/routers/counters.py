"""QueueCounter FastAPI routes (TASK-064 / API-370–373)."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.core.auth import Principal, require_permissions
from app.core.request_context import RequestContext, get_request_context
from app.core.schemas import DataResponse, ErrorResponse
from app.modules.queue.api.controllers import CounterController
from app.modules.queue.api.dependencies import get_queue_crud_service
from app.modules.queue.api.requests import CreateCounterRequest, UpdateCounterRequest
from app.modules.queue.api.responses import QueueCounterResponse
from app.modules.queue.application.services import QueueCrudApplicationService

nested_router = APIRouter(prefix="/api/v1/queues", tags=["Queue Counters"])
counters_router = APIRouter(prefix="/api/v1/counters", tags=["Queue Counters"])

_ERROR = {
    400: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    409: {"model": ErrorResponse},
    422: {"model": ErrorResponse},
    500: {"model": ErrorResponse},
}


def get_counter_controller(
    service: Annotated[QueueCrudApplicationService, Depends(get_queue_crud_service)],
) -> CounterController:
    return CounterController(service)


@nested_router.post(
    "/{queue_id}/counters",
    response_model=DataResponse[QueueCounterResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create queue counter",
    description="Create a service counter bound to a queue. No kiosk / display.",
    responses=_ERROR,
)
async def create_counter(
    queue_id: uuid.UUID,
    payload: CreateCounterRequest,
    controller: Annotated[CounterController, Depends(get_counter_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:create"))],
) -> DataResponse[QueueCounterResponse]:
    """API-370 — Create Counter."""
    _ = principal
    return await controller.create(queue_id, payload, ctx)


@nested_router.get(
    "/{queue_id}/counters",
    response_model=DataResponse[list[QueueCounterResponse]],
    status_code=status.HTTP_200_OK,
    summary="List counters for queue",
    description="List counters for a queue ordered by name ascending.",
    responses=_ERROR,
)
async def list_counters(
    queue_id: uuid.UUID,
    controller: Annotated[CounterController, Depends(get_counter_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:read"))],
) -> DataResponse[list[QueueCounterResponse]]:
    """API-371 — List Counters."""
    _ = principal
    return await controller.list(queue_id, ctx)


@counters_router.put(
    "/{counter_id}",
    response_model=DataResponse[QueueCounterResponse],
    status_code=status.HTTP_200_OK,
    summary="Update counter",
    description="Update counter name and/or status.",
    responses=_ERROR,
)
async def update_counter(
    counter_id: uuid.UUID,
    payload: UpdateCounterRequest,
    controller: Annotated[CounterController, Depends(get_counter_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> DataResponse[QueueCounterResponse]:
    """API-372 — Update Counter."""
    _ = principal
    return await controller.update(counter_id, payload, ctx)


@counters_router.delete(
    "/{counter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete counter",
    description="Hard-delete a queue counter.",
    response_class=Response,
    responses={
        204: {"description": "Deleted"},
        **_ERROR,
    },
)
async def delete_counter(
    counter_id: uuid.UUID,
    controller: Annotated[CounterController, Depends(get_counter_controller)],
    ctx: Annotated[RequestContext, Depends(get_request_context)],
    principal: Annotated[Principal, Depends(require_permissions("complaints:update"))],
) -> Response:
    """API-373 — Delete Counter."""
    _ = principal
    return await controller.delete(counter_id, ctx)


__all__ = ["counters_router", "nested_router"]
