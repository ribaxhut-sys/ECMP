"""Queue HTTP controllers (TASK-064 / CAPABILITY-003).

Translate HTTP ↔ Application only. No repository. No ORM. No business rules.
No header parsing — RequestContext comes from Core DI.
"""

from __future__ import annotations

import uuid

from fastapi import Response, status

from app.core.request_context import RequestContext
from app.core.schemas import DataResponse
from app.modules.queue.api.exception_handlers import raise_as_api_error
from app.modules.queue.api.requests import CreateQueueRequest, UpdateQueueRequest
from app.modules.queue.api.responses import QueueResponse
from app.modules.queue.application.services import (
    CreateQueueInput,
    QueueApplicationError,
    QueueCrudApplicationService,
    QueueOperationsApplicationService,
    UpdateQueueInput,
)


class QueueController:
    """Thin HTTP adapter for Queue resource + operational open/close."""

    def __init__(
        self,
        service: QueueCrudApplicationService,
        operations: QueueOperationsApplicationService | None = None,
    ) -> None:
        self._service = service
        self._operations = operations

    def _require_operations(self) -> QueueOperationsApplicationService:
        if self._operations is None:
            raise RuntimeError("QueueOperationsApplicationService is not configured")
        return self._operations

    async def create(
        self,
        payload: CreateQueueRequest,
        ctx: RequestContext,
    ) -> DataResponse[QueueResponse]:
        try:
            dto = await self._service.create_queue(
                ctx,
                CreateQueueInput(
                    organization_id=payload.organization_id,
                    name=payload.name,
                    description=payload.description,
                    policy=payload.policy,
                    status=payload.status,
                ),
            )
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueResponse.from_dto(dto))

    async def list(
        self,
        organization_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[list[QueueResponse]]:
        try:
            rows = await self._service.list_queues(ctx, organization_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=[QueueResponse.from_dto(r) for r in rows])

    async def get(
        self,
        queue_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueResponse]:
        try:
            dto = await self._service.get_queue(ctx, queue_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueResponse.from_dto(dto))

    async def update(
        self,
        queue_id: uuid.UUID,
        payload: UpdateQueueRequest,
        ctx: RequestContext,
    ) -> DataResponse[QueueResponse]:
        try:
            dto = await self._service.update_queue(
                ctx,
                queue_id,
                UpdateQueueInput(
                    name=payload.name,
                    description=payload.description,
                    policy=payload.policy,
                    status=payload.status,
                ),
            )
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueResponse.from_dto(dto))

    async def delete(
        self,
        queue_id: uuid.UUID,
        ctx: RequestContext,
    ) -> Response:
        try:
            await self._service.delete_queue(ctx, queue_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def open(
        self,
        queue_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueResponse]:
        try:
            dto = await self._require_operations().open_queue(ctx, queue_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueResponse.from_dto(dto))

    async def close(
        self,
        queue_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueResponse]:
        try:
            dto = await self._require_operations().close_queue(ctx, queue_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueResponse.from_dto(dto))


__all__ = ["QueueController"]
