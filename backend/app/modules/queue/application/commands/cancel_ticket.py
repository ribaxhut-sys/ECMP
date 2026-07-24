"""CancelTicket command (TASK-062)."""

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
class CancelTicketCommand:
    ticket_id: uuid.UUID


class CancelTicketHandler:
    def __init__(
        self,
        state: InMemoryQueueState | None = None,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._state = state if state is not None else get_queue_state()
        self._domain = domain if domain is not None else get_queue_domain_service()

    def handle(self, command: CancelTicketCommand) -> QueueTicketDto:
        ticket = self._state.get_ticket(command.ticket_id)
        if ticket is None:
            raise QueueApplicationError(
                "TICKET_NOT_FOUND",
                f"ticket not found: {command.ticket_id}",
            )
        updated = self._domain.transition_ticket(
            ticket, QueueTicketStatus.CANCELLED
        )
        self._state.replace_ticket(updated)
        return QueueTicketDto.from_domain(updated)


__all__ = ["CancelTicketCommand", "CancelTicketHandler"]
