"""Queue REST request DTOs (TASK-064)."""

from app.modules.queue.api.requests.counter import (
    CreateCounterRequest,
    UpdateCounterRequest,
)
from app.modules.queue.api.requests.queue import (
    CreateQueueRequest,
    UpdateQueueRequest,
)
from app.modules.queue.api.requests.ticket import (
    CreateTicketRequest,
    UpdateTicketRequest,
)

__all__ = [
    "CreateCounterRequest",
    "CreateQueueRequest",
    "CreateTicketRequest",
    "UpdateCounterRequest",
    "UpdateQueueRequest",
    "UpdateTicketRequest",
]
