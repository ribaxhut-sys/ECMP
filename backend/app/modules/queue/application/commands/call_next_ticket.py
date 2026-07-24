"""CallNextTicket command (TASK-062)."""

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
class CallNextTicketCommand:
    queue_id: uuid.UUID


class CallNextTicketHandler:
    def __init__(
        self,
        state: InMemoryQueueState | None = None,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._state = state if state is not None else get_queue_state()
        self._domain = domain if domain is not None else get_queue_domain_service()

    def handle(self, command: CallNextTicketCommand) -> QueueTicketDto | None:
        queue = self._state.get_queue(command.queue_id)
        if queue is None:
            raise QueueApplicationError(
                "QUEUE_NOT_FOUND",
                f"queue not found: {command.queue_id}",
            )
        self._domain.validate_can_call(queue)
        tickets = self._state.list_tickets(queue.queue_id)
        selected = self._domain.select_next_ticket(queue, tickets)
        if selected is None:
            return None
        updated = self._domain.transition_ticket(
            selected, QueueTicketStatus.CALLED
        )
        self._state.replace_ticket(updated)
        return QueueTicketDto.from_domain(updated)


__all__ = ["CallNextTicketCommand", "CallNextTicketHandler"]
