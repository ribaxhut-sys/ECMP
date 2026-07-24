# Queue ORM Guide (TASK-063)

| Field | Value |
|---|---|
| ID | GUIDE-QUEUE-ORM-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-063) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Models

| ORM | Table | Notes |
|---|---|---|
| `QueueORM` | `queues` | Aggregate root row |
| `QueueTicketORM` | `queue_tickets` | Unique `(queue_id, ticket_number)` |
| `QueueCounterORM` | `queue_counters` | `queue_id` FK (infra association) |

## Relationships

- Ticket / Counter → Queue: `ON DELETE CASCADE`
- Relationships are for ORM convenience only; repositories map to domain VOs.

## Isolation

- ORM classes live under `app.modules.queue.orm`.
- Not exported from `app.modules.queue` package `__all__`.
- Alembic registers metadata via `alembic/env.py` import of `app.modules.queue.orm`.

## Column types

- Identities: PostgreSQL `UUID`
- Status / policy / priority: `String(32)` storing enum values
- Timestamps: timezone-aware `DateTime`

## Forbidden

- Exposing ORM from Domain / Application
- Using ORM instances as DTOs
- Cross-domain FKs to Complaint / Workflow / KPI tables
