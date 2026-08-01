"""RecallTicket command (CAPABILITY-003)."""

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


@dataclass(frozen=True, slots=True)
class RecallTicketCommand:
    ticket_id: uuid.UUID


class RecallTicketHandler:
    def __init__(
        self,
        state: InMemoryQueueState | None = None,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._state = state if state is not None else get_queue_state()
        self._domain = domain if domain is not None else get_queue_domain_service()

    def handle(self, command: RecallTicketCommand) -> QueueTicketDto:
        ticket = self._state.get_ticket(command.ticket_id)
        if ticket is None:
            raise QueueApplicationError(
                "TICKET_NOT_FOUND",
                f"tiket tidak ditemukan: {command.ticket_id}",
            )
        recalled = self._domain.recall_ticket(ticket)
        return QueueTicketDto.from_domain(recalled)


__all__ = ["RecallTicketCommand", "RecallTicketHandler"]
