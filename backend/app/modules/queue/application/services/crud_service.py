"""Persistence-backed Queue CRUD application service (TASK-064).

Controllers call this layer. Repositories are injected via interfaces.
No FastAPI. No ORM imports. No Call Next / display / kiosk.

CAPABILITY-002: public use cases accept RequestContext as execution context.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, replace
from datetime import datetime, timezone

from app.core.request_context import RequestContext
from app.modules.queue.application.dto import (
    QueueCounterDto,
    QueueDto,
    QueueTicketDto,
)
from app.modules.queue.application.services.domain_service import QueueDomainService
from app.modules.queue.application.services.errors import QueueApplicationError
from app.modules.queue.interfaces.repositories import (
    QueueCounterRepository,
    QueueRepository,
    QueueTicketRepository,
)
from app.modules.queue.models import (
    Queue,
    QueueCounter,
    QueuePolicy,
    QueuePriority,
    QueueStatus,
    QueueTicket,
    QueueTicketStatus,
)


@dataclass(frozen=True, slots=True)
class CreateQueueInput:
    organization_id: uuid.UUID
    name: str
    description: str = ""
    policy: QueuePolicy = QueuePolicy.FIFO
    status: QueueStatus = QueueStatus.CLOSED
    queue_id: uuid.UUID | None = None


@dataclass(frozen=True, slots=True)
class UpdateQueueInput:
    name: str | None = None
    description: str | None = None
    policy: QueuePolicy | None = None
    status: QueueStatus | None = None


@dataclass(frozen=True, slots=True)
class IssueTicketInput:
    queue_id: uuid.UUID
    priority: QueuePriority = QueuePriority.NORMAL
    ticket_id: uuid.UUID | None = None
    created_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class UpdateTicketInput:
    priority: QueuePriority | None = None
    status: QueueTicketStatus | None = None


@dataclass(frozen=True, slots=True)
class CreateCounterInput:
    queue_id: uuid.UUID
    name: str
    status: QueueStatus = QueueStatus.CLOSED
    counter_id: uuid.UUID | None = None


@dataclass(frozen=True, slots=True)
class UpdateCounterInput:
    name: str | None = None
    status: QueueStatus | None = None


@dataclass(frozen=True, slots=True)
class QueueCounterView:
    """Application read model including persistence association queue_id."""

    counter_id: uuid.UUID
    queue_id: uuid.UUID
    name: str
    status: QueueStatus

    @classmethod
    def from_parts(cls, queue_id: uuid.UUID, counter: QueueCounter) -> QueueCounterView:
        return cls(
            counter_id=counter.counter_id,
            queue_id=queue_id,
            name=counter.name,
            status=counter.status,
        )

    def to_dto(self) -> QueueCounterDto:
        return QueueCounterDto(
            counter_id=self.counter_id,
            name=self.name,
            status=self.status,
        )


class QueueCrudApplicationService:
    """CRUD use cases over repository ports + domain rules."""

    def __init__(
        self,
        queues: QueueRepository,
        tickets: QueueTicketRepository,
        counters: QueueCounterRepository,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._queues = queues
        self._tickets = tickets
        self._counters = counters
        self._domain = domain if domain is not None else QueueDomainService()

    # ------------------------------------------------------------------ Queue

    async def create_queue(
        self, context: RequestContext, data: CreateQueueInput
    ) -> QueueDto:
        _ = context
        self._domain.validate_queue_policy(data.policy)
        if not isinstance(data.status, QueueStatus):
            raise QueueApplicationError(
                "INVALID_QUEUE_STATUS",
                f"status antrian tidak valid: {data.status!r}",
            )
        queue = Queue(
            queue_id=data.queue_id or uuid.uuid4(),
            organization_id=data.organization_id,
            name=data.name,
            description=data.description,
            status=data.status,
            policy=data.policy,
        )
        saved = await self._queues.add(queue)
        return QueueDto.from_domain(saved)

    async def list_queues(
        self, context: RequestContext, organization_id: uuid.UUID
    ) -> tuple[QueueDto, ...]:
        _ = context
        rows = await self._queues.list_by_organization(organization_id)
        return tuple(QueueDto.from_domain(q) for q in rows)

    async def get_queue(
        self, context: RequestContext, queue_id: uuid.UUID
    ) -> QueueDto:
        _ = context
        queue = await self._require_queue(queue_id)
        return QueueDto.from_domain(queue)

    async def update_queue(
        self,
        context: RequestContext,
        queue_id: uuid.UUID,
        data: UpdateQueueInput,
    ) -> QueueDto:
        _ = context
        queue = await self._require_queue(queue_id)
        name = data.name if data.name is not None else queue.name
        description = (
            data.description if data.description is not None else queue.description
        )
        policy = data.policy if data.policy is not None else queue.policy
        status = data.status if data.status is not None else queue.status
        self._domain.validate_queue_policy(policy)
        updated = Queue(
            queue_id=queue.queue_id,
            organization_id=queue.organization_id,
            name=name,
            description=description,
            status=status,
            policy=policy,
        )
        saved = await self._queues.update(updated)
        return QueueDto.from_domain(saved)

    async def delete_queue(
        self, context: RequestContext, queue_id: uuid.UUID
    ) -> None:
        _ = context
        deleted = await self._queues.delete(queue_id)
        if not deleted:
            raise QueueApplicationError(
                "QUEUE_NOT_FOUND",
                f"antrian tidak ditemukan: {queue_id}",
            )

    # ----------------------------------------------------------------- Ticket

    async def issue_ticket(
        self, context: RequestContext, data: IssueTicketInput
    ) -> QueueTicketDto:
        _ = context
        queue = await self._require_queue(data.queue_id)
        self._domain.validate_can_issue_ticket(queue)
        self._domain.validate_priority_rules(queue.policy, data.priority)

        existing = await self._tickets.list_by_queue(queue.queue_id)
        sequence = len(existing) + 1
        ticket_number = self._domain.generate_ticket_number(sequence)
        numbers = frozenset(t.ticket_number for t in existing)
        # If collision (gaps from deletes), advance until free.
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

    async def list_tickets(
        self, context: RequestContext, queue_id: uuid.UUID
    ) -> tuple[QueueTicketDto, ...]:
        _ = context
        await self._require_queue(queue_id)
        rows = await self._tickets.list_by_queue(queue_id)
        return tuple(QueueTicketDto.from_domain(t) for t in rows)

    async def get_ticket(
        self, context: RequestContext, ticket_id: uuid.UUID
    ) -> QueueTicketDto:
        _ = context
        ticket = await self._require_ticket(ticket_id)
        return QueueTicketDto.from_domain(ticket)

    async def update_ticket(
        self,
        context: RequestContext,
        ticket_id: uuid.UUID,
        data: UpdateTicketInput,
    ) -> QueueTicketDto:
        _ = context
        ticket = await self._require_ticket(ticket_id)
        priority = data.priority if data.priority is not None else ticket.priority
        if data.priority is not None:
            queue = await self._require_queue(ticket.queue_id)
            self._domain.validate_priority_rules(queue.policy, priority)

        updated = replace(ticket, priority=priority)
        if data.status is not None and data.status is not ticket.status:
            updated = self._domain.transition_ticket(updated, data.status)
        saved = await self._tickets.update(updated)
        return QueueTicketDto.from_domain(saved)

    async def delete_ticket(
        self, context: RequestContext, ticket_id: uuid.UUID
    ) -> None:
        _ = context
        deleted = await self._tickets.delete(ticket_id)
        if not deleted:
            raise QueueApplicationError(
                "TICKET_NOT_FOUND",
                f"tiket tidak ditemukan: {ticket_id}",
            )

    # ---------------------------------------------------------------- Counter

    async def create_counter(
        self, context: RequestContext, data: CreateCounterInput
    ) -> QueueCounterView:
        _ = context
        await self._require_queue(data.queue_id)
        if not isinstance(data.status, QueueStatus):
            raise QueueApplicationError(
                "INVALID_QUEUE_STATUS",
                f"status counter tidak valid: {data.status!r}",
            )
        counter = QueueCounter(
            counter_id=data.counter_id or uuid.uuid4(),
            name=data.name,
            status=data.status,
        )
        saved = await self._counters.add(data.queue_id, counter)
        return QueueCounterView.from_parts(data.queue_id, saved)

    async def list_counters(
        self, context: RequestContext, queue_id: uuid.UUID
    ) -> tuple[QueueCounterView, ...]:
        _ = context
        await self._require_queue(queue_id)
        rows = await self._counters.list_by_queue(queue_id)
        return tuple(QueueCounterView.from_parts(queue_id, c) for c in rows)

    async def update_counter(
        self,
        context: RequestContext,
        counter_id: uuid.UUID,
        data: UpdateCounterInput,
    ) -> QueueCounterView:
        _ = context
        counter = await self._require_counter(counter_id)
        queue_id = await self._counters.get_queue_id(counter_id)
        if queue_id is None:
            raise QueueApplicationError(
                "COUNTER_NOT_FOUND",
                f"counter tidak ditemukan: {counter_id}",
            )
        name = data.name if data.name is not None else counter.name
        status = data.status if data.status is not None else counter.status
        updated = QueueCounter(
            counter_id=counter.counter_id,
            name=name,
            status=status,
        )
        saved = await self._counters.update(queue_id, updated)
        return QueueCounterView.from_parts(queue_id, saved)

    async def delete_counter(
        self, context: RequestContext, counter_id: uuid.UUID
    ) -> None:
        _ = context
        deleted = await self._counters.delete(counter_id)
        if not deleted:
            raise QueueApplicationError(
                "COUNTER_NOT_FOUND",
                f"counter tidak ditemukan: {counter_id}",
            )

    # ---------------------------------------------------------------- helpers

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

    async def _require_counter(self, counter_id: uuid.UUID) -> QueueCounter:
        counter = await self._counters.get_by_id(counter_id)
        if counter is None:
            raise QueueApplicationError(
                "COUNTER_NOT_FOUND",
                f"counter tidak ditemukan: {counter_id}",
            )
        return counter


__all__ = [
    "CreateCounterInput",
    "CreateQueueInput",
    "IssueTicketInput",
    "QueueCounterView",
    "QueueCrudApplicationService",
    "UpdateCounterInput",
    "UpdateQueueInput",
    "UpdateTicketInput",
]
