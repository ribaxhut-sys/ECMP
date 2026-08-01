"""GetQueue query (TASK-062)."""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.modules.queue.application.dto import QueueDto
from app.modules.queue.application.services import (
    InMemoryQueueState,
    QueueApplicationError,
    get_queue_state,
)


@dataclass(frozen=True, slots=True)
class GetQueueQuery:
    queue_id: uuid.UUID


class GetQueueHandler:
    def __init__(self, state: InMemoryQueueState | None = None) -> None:
        self._state = state if state is not None else get_queue_state()

    def handle(self, query: GetQueueQuery) -> QueueDto:
        queue = self._state.get_queue(query.queue_id)
        if queue is None:
            raise QueueApplicationError(
                "QUEUE_NOT_FOUND",
                f"antrian tidak ditemukan: {query.queue_id}",
            )
        return QueueDto.from_domain(queue)


__all__ = ["GetQueueQuery", "GetQueueHandler"]
