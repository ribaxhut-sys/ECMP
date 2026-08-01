"""Persistence-backed Queue Operations application service (CAPABILITY-003).

Orchestrates repository ports + domain rules. No FastAPI. No ORM. No business
rules beyond calling Domain. Controllers remain thin. Not a repository.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.request_context import RequestContext
from app.modules.queue.application.dto import QueueDto, QueueTicketDto
from app.modules.queue.application.services.domain_service import QueueDomainService
from app.modules.queue.application.services.errors import QueueApplicationError
from app.modules.queue.interfaces.repositories import (
    QueueRepository,
    QueueTicketRepository,
)
from app.modules.queue.models import (
    Queue,
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)


@dataclass(frozen=True, slots=True)
class IssueTicketOperationInput:
    queue_id: uuid.UUID
    priority: QueuePriority = QueuePriority.NORMAL
    ticket_id: uuid.UUID | None = None
    created_at: datetime | None = None


class QueueOperationsApplicationService:
    """Operational queue use cases (lifecycle — not CRUD)."""

    def __init__(
        self,
        queues: QueueRepository,
        tickets: QueueTicketRepository,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._queues = queues
        self._tickets = tickets
        self._domain = domain if domain is not None else QueueDomainService()

    async def open_queue(
        self, context: RequestContext, queue_id: uuid.UUID
    ) -> QueueDto:
        _ = context
        queue = await self._require_queue(queue_id)
        updated = self._domain.with_queue_status(queue, QueueStatus.OPEN)
        saved = await self._queues.update(updated)
        return QueueDto.from_domain(saved)

    async def close_queue(
        self, context: RequestContext, queue_id: uuid.UUID
    ) -> QueueDto:
        _ = context
        queue = await self._require_queue(queue_id)
        updated = self._domain.with_queue_status(queue, QueueStatus.CLOSED)
        saved = await self._queues.update(updated)
        return QueueDto.from_domain(saved)

    async def issue_ticket(
        self, context: RequestContext, data: IssueTicketOperationInput
    ) -> QueueTicketDto:
        _ = context
        queue = await self._require_queue(data.queue_id)
        self._domain.validate_can_issue_ticket(queue)
        self._domain.validate_priority_rules(queue.policy, data.priority)

        existing = await self._tickets.list_by_queue(queue.queue_id)
        sequence = len(existing) + 1
        ticket_number = self._domain.generate_ticket_number(sequence)
        numbers = frozenset(t.ticket_number for t in existing)
        while ticket_number in numbers:
            sequence += 1
            ticket_number = self._domain.generate_ticket_number(sequence)
        self._domain.validate_no_duplicate_ticket_number(ticket_number, numbers)

        ticket = QueueTicket(
            ticket_id=data.ticket_id or uuid.uuid4(),
            queue_id=queue.queue_id,
            ticket_number=ticket_number,
            priority=data.priority,
            status=QueueTicketStatus.WAITING,
            created_at=data.created_at or datetime.now(timezone.utc),
        )
        saved = await self._tickets.add(ticket)
        return QueueTicketDto.from_domain(saved)

    async def call_next(
        self, context: RequestContext, queue_id: uuid.UUID
    ) -> QueueTicketDto | None:
        _ = context
        queue = await self._require_queue(queue_id)
        self._domain.validate_can_call(queue)
        tickets = await self._tickets.list_by_queue(queue.queue_id)
        selected = self._domain.select_next_ticket(queue, tickets)
        if selected is None:
            return None
        updated = self._domain.transition_ticket(selected, QueueTicketStatus.CALLED)
        saved = await self._tickets.update(updated)
        return QueueTicketDto.from_domain(saved)

    async def recall_ticket(
        self, context: RequestContext, ticket_id: uuid.UUID
    ) -> QueueTicketDto:
        _ = context
        ticket = await self._require_ticket(ticket_id)
        recalled = self._domain.recall_ticket(ticket)
        return QueueTicketDto.from_domain(recalled)

    async def complete_ticket(
        self, context: RequestContext, ticket_id: uuid.UUID
    ) -> QueueTicketDto:
        _ = context
        ticket = await self._require_ticket(ticket_id)
        updated = self._domain.transition_ticket(ticket, QueueTicketStatus.COMPLETED)
        saved = await self._tickets.update(updated)
        return QueueTicketDto.from_domain(saved)

    async def skip_ticket(
        self, context: RequestContext, ticket_id: uuid.UUID
    ) -> QueueTicketDto:
        _ = context
        ticket = await self._require_ticket(ticket_id)
        updated = self._domain.transition_ticket(ticket, QueueTicketStatus.SKIPPED)
        saved = await self._tickets.update(updated)
        return QueueTicketDto.from_domain(saved)

    async def cancel_ticket(
        self, context: RequestContext, ticket_id: uuid.UUID
    ) -> QueueTicketDto:
        _ = context
        ticket = await self._require_ticket(ticket_id)
        updated = self._domain.transition_ticket(ticket, QueueTicketStatus.CANCELLED)
        saved = await self._tickets.update(updated)
        return QueueTicketDto.from_domain(saved)

    async def _require_queue(self, queue_id: uuid.UUID) -> Queue:
        queue = await self._queues.get_by_id(queue_id)
        if queue is None:
            raise QueueApplicationError(
                "QUEUE_NOT_FOUND",
                f"antrian tidak ditemukan: {queue_id}",
            )
        return queue

    async def _require_ticket(self, ticket_id: uuid.UUID) -> QueueTicket:
        ticket = await self._tickets.get_by_id(ticket_id)
        if ticket is None:
            raise QueueApplicationError(
                "TICKET_NOT_FOUND",
                f"tiket tidak ditemukan: {ticket_id}",
            )
        return ticket


__all__ = [
    "IssueTicketOperationInput",
    "QueueOperationsApplicationService",
]
