"""CreateQueue command (TASK-062)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.modules.queue.application.dto import QueueDto
from app.modules.queue.application.services import (
    InMemoryQueueState,
    QueueDomainService,
    get_queue_domain_service,
    get_queue_state,
)
from app.modules.queue.models import Queue, QueuePolicy, QueueStatus


@dataclass(frozen=True, slots=True)
class CreateQueueCommand:
    organization_id: uuid.UUID
    name: str
    description: str = ""
    policy: QueuePolicy = QueuePolicy.FIFO
    queue_id: uuid.UUID | None = None


class CreateQueueHandler:
    """Create a Queue aggregate in CLOSED status (open via OpenQueue)."""

    def __init__(
        self,
        state: InMemoryQueueState | None = None,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._state = state if state is not None else get_queue_state()
        self._domain = domain if domain is not None else get_queue_domain_service()

    def handle(self, command: CreateQueueCommand) -> QueueDto:
        self._domain.validate_queue_policy(command.policy)
        queue = Queue(
            queue_id=command.queue_id or uuid.uuid4(),
            organization_id=command.organization_id,
            name=command.name,
            description=command.description,
            status=QueueStatus.CLOSED,
            policy=command.policy,
        )
        self._state.put_queue(queue)
        return QueueDto.from_domain(queue)


__all__ = ["CreateQueueCommand", "CreateQueueHandler"]
