# Domain Architecture — Queue

| Field | Value |
|---|---|
| ID | DOM-QUEUE-001 |
| Version | 1.4 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-061…064 / CAPABILITY-003) |
| Status | 🟢 Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Objective

First-class **Queue** bounded context: domain model, application CQRS,
persistence foundation, REST CRUD, and **operational lifecycle**
(CAPABILITY-003).

No Redis. No display / kiosk / voice / notification. No Complaint coupling.

## In Scope

### TASK-061 — Domain

- `Queue` aggregate root
- `QueueTicket` (immutable) + `QueueTicketStatus`
- `QueueCounter`
- `QueuePolicy`, `QueueStatus`, `QueuePriority`

### TASK-062 — Application

- `QueueDomainService`
- Commands: Create / Open / Pause / Close / Issue / CallNext / Complete / Cancel / Skip / Recall
- Queries: GetQueue / GetQueueTickets / GetWaitingTickets
- DTOs: `QueueDto` · `QueueTicketDto` · `QueueCounterDto`
- In-memory application state (foundation workspace — not a repository)

### TASK-063 — Persistence Foundation

- Repository interfaces: `QueueRepository` · `QueueTicketRepository` · `QueueCounterRepository`
- Async SQLAlchemy repositories + DI wiring
- ORM: `QueueORM` · `QueueTicketORM` · `QueueCounterORM` (infrastructure only)
- Bidirectional mappers (Domain ↔ ORM)
- Alembic `0027_queue_persistence` (schema only, no seed)
- Shared `app/db/async_session.py` for future domains

### TASK-064 — REST API Foundation

- `queue/api/` — controllers, routers, requests, responses, validators,
  exception_handlers, dependencies
- Persistence-backed `QueueCrudApplicationService`
- Endpoints API-360…373 (Queues / Tickets / Counters)
- OpenAPI: `07 API Catalog/openapi/queue-service.v1.yaml`
- Request Context via Core (`app.core.request_context`, CAPABILITY-002)

### CAPABILITY-003 — Queue Operations

- Pluggable `TicketNumberGenerator` (default `A001`, `A002`, …)
- `QueueOperationsApplicationService` (async orchestration)
- Domain lifecycle: issue / call_next / recall / complete / skip / cancel
- Queue open / close operations
- REST endpoints API-374…381
- Controllers remain thin; repositories remain persistence-only

## Out of Scope (STOP)

- Display / Kiosk / Voice
- Redis / WebSocket / Background Worker
- Complaint / Workflow / Notification / Dashboard APIs
- Authentication / Authorization / Audit enforcement
- TASK-065+ beyond Operations

## Related

- `QUEUE_DOMAIN_ARCHITECTURE.md`
- `QUEUE_APPLICATION_ARCHITECTURE.md`
- `QUEUE_PERSISTENCE_ARCHITECTURE.md`
- `QUEUE_REST_API.md`
- `QUEUE_MODEL.md`
- `QUEUE_COMMAND_GUIDE.md`
- `QUEUE_QUERY_GUIDE.md`
- `QUEUE_TICKET_LIFECYCLE.md`
- `QUEUE_REPOSITORY_PATTERN_GUIDE.md`
- `QUEUE_MAPPER_GUIDE.md`
- `QUEUE_ORM_GUIDE.md`
- `QUEUE_MIGRATION_GUIDE.md`
- `QUEUE_DEVELOPER_GUIDE.md`
- `QUEUE_APPLICATION_DEVELOPER_GUIDE.md`
- `QUEUE_PERSISTENCE_DEVELOPER_GUIDE.md`
