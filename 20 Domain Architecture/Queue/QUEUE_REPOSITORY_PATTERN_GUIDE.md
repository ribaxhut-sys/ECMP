# Queue Repository Pattern Guide (TASK-063)

| Field | Value |
|---|---|
| ID | GUIDE-QUEUE-REPO-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-063) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Ports (interfaces)

| Interface | Responsibility |
|---|---|
| `QueueRepository` | CRUD + list-by-organization for Queue aggregate |
| `QueueTicketRepository` | CRUD + list-by-queue / status for tickets |
| `QueueCounterRepository` | CRUD + list-by-queue (queue_id passed on write) |

Interfaces live in `app.modules.queue.interfaces` and import **domain only**.

## Adapters

| Adapter | Session |
|---|---|
| `SqlAlchemyQueueRepository` | `AsyncSession` |
| `SqlAlchemyQueueTicketRepository` | `AsyncSession` |
| `SqlAlchemyQueueCounterRepository` | `AsyncSession` |

## Rules

1. Return domain models only — never ORM instances.
2. No business rules inside repositories.
3. Use SQLAlchemy expression API (`select`, `delete`, bound parameters).
4. `flush()` after writes; do not invent a UnitOfWork here.
5. Inject via `infrastructure.get_queue_*_repository(session)`.

## Example (conceptual)

```text
session: AsyncSession
repo = get_queue_repository(session)
queue = await repo.add(domain_queue)
await session.commit()
```

## Anti-patterns

- Importing ORM in Application / Domain
- Returning `QueueORM` from a repository method
- Embedding status-transition rules in repositories
- Raw f-string SQL
