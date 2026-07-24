"""Queue application services (TASK-062 / TASK-064 / CAPABILITY-003)."""

from app.modules.queue.application.services.crud_service import (
    CreateCounterInput,
    CreateQueueInput,
    IssueTicketInput,
    QueueCounterView,
    QueueCrudApplicationService,
    UpdateCounterInput,
    UpdateQueueInput,
    UpdateTicketInput,
)
from app.modules.queue.application.services.domain_service import QueueDomainService
from app.modules.queue.application.services.errors import QueueApplicationError
from app.modules.queue.application.services.operations_service import (
    IssueTicketOperationInput,
    QueueOperationsApplicationService,
)
from app.modules.queue.application.services.state import InMemoryQueueState
from app.modules.queue.application.services.wiring import (
    get_queue_domain_service,
    get_queue_state,
)

__all__ = [
    "CreateCounterInput",
    "CreateQueueInput",
    "InMemoryQueueState",
    "IssueTicketInput",
    "IssueTicketOperationInput",
    "QueueApplicationError",
    "QueueCounterView",
    "QueueCrudApplicationService",
    "QueueDomainService",
    "QueueOperationsApplicationService",
    "UpdateCounterInput",
    "UpdateQueueInput",
    "UpdateTicketInput",
    "get_queue_domain_service",
    "get_queue_state",
]
