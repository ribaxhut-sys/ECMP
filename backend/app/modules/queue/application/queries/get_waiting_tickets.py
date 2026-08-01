"""GetWaitingTickets query (TASK-062)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.modules.queue.application.dto import QueueTicketDto
from app.modules.queue.application.services import (
    InMemoryQueueState,
    QueueApplicationError,
    QueueDomainService,
    get_queue_domain_service,
    get_queue_state,
)
from app.modules.queue.models import QueueTicketStatus


@dataclass(frozen=True, slots=True)
class GetWaitingTicketsQuery:
    queue_id: uuid.UUID


class GetWaitingTicketsHandler:
    def __init__(
        self,
        state: InMemoryQueueState | None = None,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._state = state if state is not None else get_queue_state()
        self._domain = domain if domain is not None else get_queue_domain_service()

    def handle(self, query: GetWaitingTicketsQuery) -> tuple[QueueTicketDto, ...]:
        queue = self._state.get_queue(query.queue_id)
        if queue is None:
            raise QueueApplicationError(
                "QUEUE_NOT_FOUND",
                f"antrian tidak ditemukan: {query.queue_id}",
            )
        self._domain.validate_queue_policy(queue.policy)
        tickets = [
            t
            for t in self._state.list_tickets(query.queue_id)
            if t.status is QueueTicketStatus.WAITING
        ]
        return tuple(QueueTicketDto.from_domain(t) for t in tickets)


__all__ = ["GetWaitingTicketsQuery", "GetWaitingTicketsHandler"]
