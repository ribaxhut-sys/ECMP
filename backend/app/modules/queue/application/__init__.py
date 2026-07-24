"""Queue Application layer (TASK-062).

CQRS commands / queries + domain service. No REST. No DB. No repository.
"""

from app.modules.queue.application.commands import (
    CallNextTicketCommand,
    CallNextTicketHandler,
    CancelTicketCommand,
    CancelTicketHandler,
    CloseQueueCommand,
    CloseQueueHandler,
    CompleteTicketCommand,
    CompleteTicketHandler,
    CreateQueueCommand,
    CreateQueueHandler,
    IssueTicketCommand,
    IssueTicketHandler,
    OpenQueueCommand,
    OpenQueueHandler,
    PauseQueueCommand,
    PauseQueueHandler,
)
from app.modules.queue.application.dto import (
    QueueCounterDto,
    QueueDto,
    QueueTicketDto,
)
from app.modules.queue.application.queries import (
    GetQueueHandler,
    GetQueueQuery,
    GetQueueTicketsHandler,
    GetQueueTicketsQuery,
    GetWaitingTicketsHandler,
    GetWaitingTicketsQuery,
)
from app.modules.queue.application.services import (
    InMemoryQueueState,
    QueueApplicationError,
    QueueDomainService,
    get_queue_domain_service,
    get_queue_state,
)

__all__ = [
    "CallNextTicketCommand",
    "CallNextTicketHandler",
    "CancelTicketCommand",
    "CancelTicketHandler",
    "CloseQueueCommand",
    "CloseQueueHandler",
    "CompleteTicketCommand",
    "CompleteTicketHandler",
    "CreateQueueCommand",
    "CreateQueueHandler",
    "GetQueueHandler",
    "GetQueueQuery",
    "GetQueueTicketsHandler",
    "GetQueueTicketsQuery",
    "GetWaitingTicketsHandler",
    "GetWaitingTicketsQuery",
    "InMemoryQueueState",
    "IssueTicketCommand",
    "IssueTicketHandler",
    "OpenQueueCommand",
    "OpenQueueHandler",
    "PauseQueueCommand",
    "PauseQueueHandler",
    "QueueApplicationError",
    "QueueCounterDto",
    "QueueDomainService",
    "QueueDto",
    "QueueTicketDto",
    "get_queue_domain_service",
    "get_queue_state",
]
