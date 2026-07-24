# Queue Persistence Architecture (TASK-063)

| Field | Value |
|---|---|
| ID | ARCH-QUEUE-PERSIST-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-063) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Establish the **ECMP Persistence Foundation**, with **Queue** as the reference
bounded context. Future domains (Complaint, Workflow, Dashboard, KPI) reuse
the same layering: interfaces → mappers → ORM → async repositories.

No REST API. No Controller. No Redis. No Kiosk. No Display. No UnitOfWork yet.

## Principles

1. Clean Architecture — Domain never imports SQLAlchemy / ORM.
2. DDD — repositories return immutable domain models only.
3. SOLID — repository ports (ABC) + SQLAlchemy adapters.
4. Dependency Injection — session-bound repository factories.
5. Async SQLAlchemy — `AsyncSession` controlled by the repository.
6. Extractable module — Queue persistence is self-contained under `queue/`.
7. Must not modify Complaint / Workflow / Execution* / Delivery* / Transport* /
   Provider* / Dashboard / Notification / KPI.

## Layers

```text
┌─────────────────────────────────────────────────────────────┐
│ Application (TASK-062) — still uses InMemoryQueueState      │
│  commands / queries / DTOs / QueueDomainService             │
└─────────────────────────────┬───────────────────────────────┘
                              │ depends on Domain
┌─────────────────────────────▼───────────────────────────────┐
│ Domain (TASK-061)                                           │
│  Queue · QueueTicket · QueueCounter · enums                 │
│  NO SQLAlchemy · NO ORM · NO repository implementations     │
└─────────────────────────────▲───────────────────────────────┘
                              │ returns Domain models
┌─────────────────────────────┴───────────────────────────────┐
│ Interfaces (TASK-063)                                       │
│  QueueRepository · QueueTicketRepository · QueueCounterRepo │
└─────────────────────────────▲───────────────────────────────┘
                              │ implements
┌─────────────────────────────┴───────────────────────────────┐
│ Infrastructure (TASK-063)                                   │
│  repositories/  — SqlAlchemy*Repository (AsyncSession)      │
│  mappers/       — Domain ↔ ORM                              │
│  orm/           — QueueORM · QueueTicketORM · QueueCounterORM│
│  infrastructure/ — DI factories                             │
└─────────────────────────────────────────────────────────────┘
```

## Package layout

| Path | Role |
|---|---|
| `interfaces/` | Repository ABCs (no SQLAlchemy) |
| `orm/` | SQLAlchemy models (never exported from package root) |
| `mappers/` | Bidirectional Domain ↔ ORM |
| `repositories/` | Async SQLAlchemy adapters |
| `infrastructure/` | DI wiring (`get_queue_repository`, …) |
| `app/db/async_session.py` | Shared async engine / session factory |

## Transaction scope

- Repositories accept `AsyncSession`.
- Writes `flush()` after mutations; callers own `commit` / `rollback`.
- No UnitOfWork in this milestone.

## Guarantees

- Domain models remain immutable / persistence-independent.
- Application never imports ORM.
- ORM never exposed outside infrastructure / mappers / repositories.
- Parameterized SQLAlchemy Core/ORM API only — no raw string SQL.
- Alembic migration `0027_queue_persistence` — schema only, no seed.

## Out of scope (STOP)

- Wiring application handlers to repositories (future task)
- REST / FastAPI routes / controllers
- Redis / cache
- Display / kiosk / notification
- UnitOfWork
- TASK-064+

## Related

- `QUEUE_REPOSITORY_PATTERN_GUIDE.md`
- `QUEUE_MAPPER_GUIDE.md`
- `QUEUE_ORM_GUIDE.md`
- `QUEUE_MIGRATION_GUIDE.md`
- `QUEUE_PERSISTENCE_DEVELOPER_GUIDE.md`
