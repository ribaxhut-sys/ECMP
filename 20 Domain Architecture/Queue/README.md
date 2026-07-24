# Domain Architecture — Queue

| Field | Value |
|---|---|
| ID | DOM-QUEUE-001 |
| Version | 1.1 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-061…062) |
| Status | 🟢 Approved (TASK-061 Domain + TASK-062 Application Foundation) |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Objective

First-class **Queue** bounded context: domain model + application CQRS
foundation (commands, queries, domain service, immutable DTOs).

No infrastructure. No persistence. No REST. No display / kiosk / notification.

## In Scope

### TASK-061 — Domain

- `Queue` aggregate root
- `QueueTicket` (immutable) + `QueueTicketStatus`
- `QueueCounter`
- `QueuePolicy`, `QueueStatus`, `QueuePriority`

### TASK-062 — Application

- `QueueDomainService`
- Commands: Create / Open / Pause / Close / Issue / CallNext / Complete / Cancel
- Queries: GetQueue / GetQueueTickets / GetWaitingTickets
- DTOs: `QueueDto` · `QueueTicketDto` · `QueueCounterDto`
- In-memory application state (foundation only — not a repository)

## Out of Scope (STOP)

- REST API / repository / database / Redis / SQLAlchemy
- Display / kiosk / notification
- Changes to Complaint / Workflow / Execution* / Delivery* / Transport* /
  Provider* / Notification / Dashboard / KPI
- TASK-063+

## Related

- `QUEUE_DOMAIN_ARCHITECTURE.md`
- `QUEUE_APPLICATION_ARCHITECTURE.md`
- `QUEUE_MODEL.md`
- `QUEUE_COMMAND_GUIDE.md`
- `QUEUE_QUERY_GUIDE.md`
- `QUEUE_TICKET_LIFECYCLE.md`
- `QUEUE_DEVELOPER_GUIDE.md`
- `QUEUE_APPLICATION_DEVELOPER_GUIDE.md`
