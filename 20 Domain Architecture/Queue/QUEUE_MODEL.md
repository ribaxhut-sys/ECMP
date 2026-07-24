# Queue Model (TASK-061 / TASK-062)

| Field | Value |
|---|---|
| ID | DOM-QUEUE-MODEL-001 |
| Version | 1.1 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-061…062) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Queue (Aggregate Root)

| Field | Type | Notes |
|---|---|---|
| `queue_id` | UUID | Identity |
| `organization_id` | UUID | Owning org |
| `name` | str | Required, non-empty |
| `description` | str | May be empty |
| `status` | `QueueStatus` | OPEN / PAUSED / CLOSED |
| `policy` | `QueuePolicy` | FIFO / PRIORITY_QUEUE |

## QueueTicket (Immutable)

| Field | Type | Notes |
|---|---|---|
| `ticket_id` | UUID | Identity |
| `queue_id` | UUID | Parent queue |
| `ticket_number` | str | Required; unique within queue |
| `priority` | `QueuePriority` | NORMAL / PRIORITY / VIP |
| `status` | `QueueTicketStatus` | Dedicated ticket lifecycle enum |
| `created_at` | datetime | UTC-normalized |

## QueueCounter

| Field | Type | Notes |
|---|---|---|
| `counter_id` | UUID | Identity |
| `name` | str | Required |
| `status` | `QueueStatus` | OPEN / PAUSED / CLOSED |

## Enums

### QueueStatus

OPEN · PAUSED · CLOSED

### QueueTicketStatus (TASK-062)

WAITING · CALLED · SERVING · COMPLETED · CANCELLED · SKIPPED

### QueuePriority

NORMAL · PRIORITY · VIP

### QueuePolicy

| Policy | Meaning |
|---|---|
| `FIFO` | First-in, first-out |
| `PRIORITY_QUEUE` | Priority-aware ordering |

## Out of scope

REST, Redis, display, kiosk, notification, UnitOfWork, TASK-064+.
Persistence foundation (TASK-063) is in scope under `interfaces/` / `orm/` /
`mappers/` / `repositories/` / `infrastructure/`.
