"""Queue REST request / response schemas (TASK-064).

HTTP contracts only — never Domain Entity, never ORM.
"""

from app.modules.queue.api.requests import (
    CreateCounterRequest,
    CreateQueueRequest,
    CreateTicketRequest,
    UpdateCounterRequest,
    UpdateQueueRequest,
    UpdateTicketRequest,
)
from app.modules.queue.api.responses import (
    QueueCounterResponse,
    QueueResponse,
    QueueTicketResponse,
)

__all__ = [
    "CreateCounterRequest",
    "CreateQueueRequest",
    "CreateTicketRequest",
    "QueueCounterResponse",
    "QueueResponse",
    "QueueTicketResponse",
    "UpdateCounterRequest",
    "UpdateQueueRequest",
    "UpdateTicketRequest",
]
