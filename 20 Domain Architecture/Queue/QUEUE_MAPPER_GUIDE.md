# Queue Mapper Guide (TASK-063)

| Field | Value |
|---|---|
| ID | GUIDE-QUEUE-MAPPER-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-063) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Bidirectional mapping between immutable domain models and SQLAlchemy ORM rows
without leaking ORM types to Application / Domain.

## Mappers

| Mapper | Domain → ORM | ORM → Domain |
|---|---|---|
| `QueueMapper` | `to_orm` / `apply_to_orm` | `to_domain` |
| `QueueTicketMapper` | `to_orm` / `apply_to_orm` | `to_domain` |
| `QueueCounterMapper` | `to_orm(queue_id, …)` / `apply_to_orm` | `to_domain` |

## Enum strategy

Domain enums (`QueueStatus`, `QueuePolicy`, …) map to/from `str` columns via
`.value` / enum constructors. Invalid DB values raise at map-to-domain time.

## QueueCounter association

Domain `QueueCounter` has no `queue_id`. Persistence association is supplied
explicitly to `QueueCounterMapper.to_orm(queue_id, domain)`.

## Rules

- Mappers contain no business logic.
- `apply_to_orm` never changes primary-key identity.
- Callers of repositories never see ORM objects.
