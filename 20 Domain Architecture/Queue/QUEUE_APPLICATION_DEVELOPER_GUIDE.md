# Queue Application — Developer Guide (TASK-062)

| Field | Value |
|---|---|
| ID | DOM-QUEUE-APP-DEV-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-062) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Package layout

```text
backend/app/modules/queue/
  models.py                 # Domain VOs + enums (TASK-061/062)
  application/
    commands/               # CQRS write use cases
    queries/                # CQRS read use cases
    dto/                    # Immutable DTOs
    services/
      domain_service.py     # QueueDomainService (no DB)
      state.py              # InMemoryQueueState (not a repository)
      errors.py
      wiring.py             # DI factories
```

## Import

```text
from app.modules.queue.application import (
    CreateQueueCommand,
    CreateQueueHandler,
    QueueDomainService,
    InMemoryQueueState,
)
from app.modules.queue import QueueTicketStatus, QueueStatus
```

## DI

| Factory | Returns |
|---|---|
| `get_queue_domain_service()` | Shared `QueueDomainService` |
| `get_queue_state()` | Process-local `InMemoryQueueState` |

Handlers accept optional `state` / `domain` for tests.

## Hard rules

- Do **not** add REST routers / SQLAlchemy / Redis in this package
- Do **not** mutate `QueueTicket` / DTO fields in place — replace VOs
- Do **not** import Complaint / Workflow / Execution* / Delivery* /
  Transport* / Provider* / Notification / Dashboard / KPI
- `InMemoryQueueState` is foundation workspace only — not persistence

## Tests

```bash
cd backend
pytest tests/test_queue_domain.py tests/test_queue_application.py -q
```

Docker:

```bash
docker compose exec -T backend pytest tests/test_queue_domain.py tests/test_queue_application.py -q
```

## Related

- `QUEUE_APPLICATION_ARCHITECTURE.md`
- `QUEUE_COMMAND_GUIDE.md`
- `QUEUE_QUERY_GUIDE.md`
- `QUEUE_TICKET_LIFECYCLE.md`
- `QUEUE_DEVELOPER_GUIDE.md` (domain)
