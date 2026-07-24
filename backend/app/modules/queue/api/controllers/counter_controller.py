"""QueueCounter HTTP controllers (TASK-064)."""

from __future__ import annotations

import uuid

from fastapi import Response, status

from app.core.request_context import RequestContext
from app.core.schemas import DataResponse
from app.modules.queue.api.exception_handlers import raise_as_api_error
from app.modules.queue.api.requests import CreateCounterRequest, UpdateCounterRequest
from app.modules.queue.api.responses import QueueCounterResponse
from app.modules.queue.application.services import (
    CreateCounterInput,
    QueueApplicationError,
    QueueCrudApplicationService,
    UpdateCounterInput,
)


class CounterController:
    """Thin HTTP adapter for QueueCounter resource."""

    def __init__(self, service: QueueCrudApplicationService) -> None:
        self._service = service

    async def create(
        self,
        queue_id: uuid.UUID,
        payload: CreateCounterRequest,
        ctx: RequestContext,
    ) -> DataResponse[QueueCounterResponse]:
        try:
            view = await self._service.create_counter(
                ctx,
                CreateCounterInput(
                    queue_id=queue_id,
                    name=payload.name,
                    status=payload.status,
                ),
            )
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueCounterResponse.from_view(view))

    async def list(
        self,
        queue_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[list[QueueCounterResponse]]:
        try:
            rows = await self._service.list_counters(ctx, queue_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=[QueueCounterResponse.from_view(r) for r in rows])

    async def update(
        self,
        counter_id: uuid.UUID,
        payload: UpdateCounterRequest,
        ctx: RequestContext,
    ) -> DataResponse[QueueCounterResponse]:
        try:
            view = await self._service.update_counter(
                ctx,
                counter_id,
                UpdateCounterInput(
                    name=payload.name,
                    status=payload.status,
                ),
            )
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueCounterResponse.from_view(view))

    async def delete(
        self,
        counter_id: uuid.UUID,
        ctx: RequestContext,
    ) -> Response:
        try:
            await self._service.delete_counter(ctx, counter_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = ["CounterController"]
