# Queue Persistence — Developer Guide (TASK-063)

| Field | Value |
|---|---|
| ID | DEV-QUEUE-PERSIST-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-063) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## When to use

Use Queue repositories when persisting Queue BC aggregates. Application
handlers still use `InMemoryQueueState` until a later wiring task.

## Imports

```text
# Ports
from app.modules.queue.interfaces import (
    QueueRepository,
    QueueTicketRepository,
    QueueCounterRepository,
)

# DI adapters
from app.modules.queue.infrastructure import (
    get_queue_repository,
    get_queue_ticket_repository,
    get_queue_counter_repository,
)

# Shared async session
from app.db.async_session import get_async_session_factory
```

Do **not** import `app.modules.queue.orm` from Application or Domain.

## Hard rules

- Domain never imports SQLAlchemy
- Application never imports ORM
- Repositories return domain models only
- Parameterized queries only
- No REST routes in this package
- Do not modify Complaint / Workflow / Execution* / Delivery* / Transport* /
  Provider* / Dashboard / Notification / KPI

## Tests

```bash
cd backend
pytest tests/test_queue_domain.py tests/test_queue_application.py tests/test_queue_persistence.py -q
```

Docker (when daemon available):

```bash
docker compose exec -T backend pytest tests/test_queue_persistence.py -q
```
