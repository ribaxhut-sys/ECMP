"""QueueTicket HTTP controllers (TASK-064 / CAPABILITY-003)."""

from __future__ import annotations

import uuid

from fastapi import Response, status

from app.core.request_context import RequestContext
from app.core.schemas import DataResponse
from app.modules.queue.api.exception_handlers import raise_as_api_error
from app.modules.queue.api.requests import CreateTicketRequest, UpdateTicketRequest
from app.modules.queue.api.responses import QueueTicketResponse
from app.modules.queue.application.services import (
    IssueTicketInput,
    IssueTicketOperationInput,
    QueueApplicationError,
    QueueCrudApplicationService,
    QueueOperationsApplicationService,
    UpdateTicketInput,
)


class TicketController:
    """Thin HTTP adapter for QueueTicket CRUD + operational lifecycle."""

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
        queue_id: uuid.UUID,
        payload: CreateTicketRequest,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse]:
        try:
            dto = await self._service.issue_ticket(
                ctx,
                IssueTicketInput(
                    queue_id=queue_id,
                    priority=payload.priority,
                ),
            )
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))

    async def list(
        self,
        queue_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[list[QueueTicketResponse]]:
        try:
            rows = await self._service.list_tickets(ctx, queue_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=[QueueTicketResponse.from_dto(r) for r in rows])

    async def get(
        self,
        ticket_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse]:
        try:
            dto = await self._service.get_ticket(ctx, ticket_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))

    async def update(
        self,
        ticket_id: uuid.UUID,
        payload: UpdateTicketRequest,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse]:
        try:
            dto = await self._service.update_ticket(
                ctx,
                ticket_id,
                UpdateTicketInput(
                    priority=payload.priority,
                    status=payload.status,
                ),
            )
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))

    async def delete(
        self,
        ticket_id: uuid.UUID,
        ctx: RequestContext,
    ) -> Response:
        try:
            await self._service.delete_ticket(ctx, ticket_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    async def issue_ticket(
        self,
        queue_id: uuid.UUID,
        payload: CreateTicketRequest,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse]:
        try:
            dto = await self._require_operations().issue_ticket(
                ctx,
                IssueTicketOperationInput(
                    queue_id=queue_id,
                    priority=payload.priority,
                ),
            )
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))

    async def call_next(
        self,
        queue_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse] | Response:
        try:
            dto = await self._require_operations().call_next(ctx, queue_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        if dto is None:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))

    async def recall(
        self,
        ticket_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse]:
        try:
            dto = await self._require_operations().recall_ticket(ctx, ticket_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))

    async def complete(
        self,
        ticket_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse]:
        try:
            dto = await self._require_operations().complete_ticket(ctx, ticket_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))

    async def skip(
        self,
        ticket_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse]:
        try:
            dto = await self._require_operations().skip_ticket(ctx, ticket_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))

    async def cancel(
        self,
        ticket_id: uuid.UUID,
        ctx: RequestContext,
    ) -> DataResponse[QueueTicketResponse]:
        try:
            dto = await self._require_operations().cancel_ticket(ctx, ticket_id)
        except QueueApplicationError as exc:
            raise_as_api_error(exc)
        return DataResponse(data=QueueTicketResponse.from_dto(dto))


__all__ = ["TicketController"]
