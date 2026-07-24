"""IssueTicket command (TASK-062)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.modules.queue.application.dto import QueueTicketDto
from app.modules.queue.application.services import (
    InMemoryQueueState,
    QueueApplicationError,
    QueueDomainService,
    get_queue_domain_service,
    get_queue_state,
)
from app.modules.queue.models import QueuePriority, QueueTicket, QueueTicketStatus


@dataclass(frozen=True, slots=True)
class IssueTicketCommand:
    queue_id: uuid.UUID
    priority: QueuePriority = QueuePriority.NORMAL
    ticket_id: uuid.UUID | None = None
    created_at: datetime | None = None


class IssueTicketHandler:
    def __init__(
        self,
        state: InMemoryQueueState | None = None,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._state = state if state is not None else get_queue_state()
        self._domain = domain if domain is not None else get_queue_domain_service()

    def handle(self, command: IssueTicketCommand) -> QueueTicketDto:
        queue = self._state.get_queue(command.queue_id)
        if queue is None:
            raise QueueApplicationError(
                "QUEUE_NOT_FOUND",
                f"queue not found: {command.queue_id}",
            )
        self._domain.validate_can_issue_ticket(queue)
        self._domain.validate_priority_rules(queue.policy, command.priority)

        sequence = self._state.next_sequence(queue.queue_id)
        ticket_number = self._domain.generate_ticket_number(sequence)
        self._domain.validate_no_duplicate_ticket_number(
            ticket_number,
            self._state.ticket_numbers(queue.queue_id),
        )

        ticket = QueueTicket(
            ticket_id=command.ticket_id or uuid.uuid4(),
            queue_id=queue.queue_id,
            ticket_number=ticket_number,
            priority=command.priority,
            status=QueueTicketStatus.WAITING,
            created_at=command.created_at or datetime.now(timezone.utc),
        )
        self._state.put_ticket(ticket)
        return QueueTicketDto.from_domain(ticket)


__all__ = ["IssueTicketCommand", "IssueTicketHandler"]
