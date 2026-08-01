"""OpenQueue command (TASK-062)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.modules.queue.application.dto import QueueDto
from app.modules.queue.application.services import (
    InMemoryQueueState,
    QueueApplicationError,
    QueueDomainService,
    get_queue_domain_service,
    get_queue_state,
)
from app.modules.queue.models import QueueStatus


@dataclass(frozen=True, slots=True)
class OpenQueueCommand:
    queue_id: uuid.UUID


class OpenQueueHandler:
    def __init__(
        self,
        state: InMemoryQueueState | None = None,
        domain: QueueDomainService | None = None,
    ) -> None:
        self._state = state if state is not None else get_queue_state()
        self._domain = domain if domain is not None else get_queue_domain_service()

    def handle(self, command: OpenQueueCommand) -> QueueDto:
        queue = self._state.get_queue(command.queue_id)
        if queue is None:
            raise QueueApplicationError(
                "QUEUE_NOT_FOUND",
                f"antrian tidak ditemukan: {command.queue_id}",
            )
        updated = self._domain.with_queue_status(queue, QueueStatus.OPEN)
        self._state.replace_queue(updated)
        return QueueDto.from_domain(updated)


__all__ = ["OpenQueueCommand", "OpenQueueHandler"]
