# Queue Application Architecture (TASK-062)

| Field | Value |
|---|---|
| ID | ARCH-QUEUE-APP-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-062) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Introduce the **Queue Application Foundation** — CQRS use cases, immutable
DTOs, and a pure `QueueDomainService` on top of the TASK-061 domain model.

No REST API. No database. No repository. No display / kiosk / notification.

## Principles

1. Clean Architecture — application depends on domain; no infrastructure.
2. DDD — `Queue` aggregate + `QueueDomainService` for cross-entity rules.
3. CQRS — commands mutate application state; queries read DTOs.
4. SOLID — handlers injected with state + domain service.
5. Bounded Context — Queue remains independent of Complaint / Delivery / etc.
6. Immutable DTOs / tickets — replace VOs; never mutate shared ticket fields.

## Layers

```text
┌─────────────────────────────────────────────────────────┐
│ Application (TASK-062)                                  │
│  commands/ · queries/ · dto/ · services/                │
│  QueueDomainService · InMemoryQueueState (foundation)   │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│ Domain (TASK-061)                                       │
│  Queue · QueueTicket · QueueCounter                     │
│  QueueStatus · QueueTicketStatus · QueuePolicy · …      │
└─────────────────────────────────────────────────────────┘

Infrastructure (REST / DB / Redis) — OUT OF SCOPE
```

## Components

| Component | Responsibility |
|---|---|
| `QueueDomainService` | Ticket numbers, status/policy validation, next-ticket selection, priority rules |
| `InMemoryQueueState` | Process-local foundation workspace (**not** a repository) |
| Command handlers | Create / Open / Pause / Close / Issue / CallNext / Complete / Cancel |
| Query handlers | GetQueue / GetQueueTickets / GetWaitingTickets |
| DTOs | Immutable `QueueDto` · `QueueTicketDto` · `QueueCounterDto` |

## Ticket vs Queue status

| Enum | Values | Applies to |
|---|---|---|
| `QueueStatus` | OPEN · PAUSED · CLOSED | `Queue`, `QueueCounter` |
| `QueueTicketStatus` | WAITING · CALLED · SERVING · COMPLETED · CANCELLED · SKIPPED | `QueueTicket` |

## Guarantees

- No DB / SQLAlchemy / Redis / repository
- No REST / FastAPI routers
- No display / kiosk / notification
- No cross-domain imports (Complaint, Workflow, Execution*, Delivery*, …)
- Domain service performs no I/O

## Implementation

- `backend/app/modules/queue/models.py`
- `backend/app/modules/queue/application/`

## Related

- `QUEUE_COMMAND_GUIDE.md`
- `QUEUE_QUERY_GUIDE.md`
- `QUEUE_TICKET_LIFECYCLE.md`
- `QUEUE_APPLICATION_DEVELOPER_GUIDE.md`
- `QUEUE_DOMAIN_ARCHITECTURE.md`
