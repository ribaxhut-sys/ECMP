# Queue Domain — Developer Guide (TASK-061)

| Field | Value |
|---|---|
| ID | DOM-QUEUE-DEV-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-061) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Package

| Module | Role |
|---|---|
| `models.py` | `Queue`, `QueueTicket`, `QueueCounter`, enums |

Do **not** modify Complaint, Workflow, Execution*, Delivery*, Transport*,
Provider*, Notification, Dashboard, or KPI.

## Import

```text
from app.modules.queue import (
    Queue,
    QueueTicket,
    QueueCounter,
    QueueStatus,
    QueueTicketStatus,
    QueuePriority,
    QueuePolicy,
)
```

## Hard rules

- Immutable `QueueTicket` — never mutate fields in place
- Ticket lifecycle uses `QueueTicketStatus` (not `QueueStatus`)
- No REST router / repository / SQLAlchemy models in this package
- No display / kiosk / notification logic
- No DB / scheduler / queue infrastructure
- Policy is enum-only (FIFO / PRIORITY_QUEUE) — no scheduling engine
- Application layer: see `QUEUE_APPLICATION_DEVELOPER_GUIDE.md` (TASK-062)

## Tests

```bash
cd backend
pytest tests/test_queue_domain.py tests/test_queue_application.py -q
```

Docker:

```bash
docker compose exec -T backend pytest tests/test_queue_domain.py tests/test_queue_application.py -q
```
