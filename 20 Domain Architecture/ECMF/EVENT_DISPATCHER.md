# In-Process Event Dispatcher (TASK-046)

| Field | Value |
|---|---|
| ID | ARCH-ECMF-DISPATCH-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead / Integration Lead |
| Approver | Architecture Board (delegated via TASK-046) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Separate **Producer** from **Consumer** for Complaint lifecycle events inside
a single application process.

`ComplaintService` creates events via `ComplaintEventFactory` and delivers
them only through `EventDispatcher`. The service never imports, names, or
depends on concrete consumers.

## What this is

- In-process, synchronous event delivery
- Handler registration API
- Ordered invocation of registered handlers
- Isolated error collection via `DispatchResult`

## What this is NOT

- Not an Event Bus
- Not Kafka / RabbitMQ / Redis Streams / Pub-Sub
- Not an Event Store / outbox table / database persistence
- Not an async queue or background worker
- Not multi-process / multi-service messaging (ADR-009 still deferred)

## Principle

```text
Complaint Service (Producer)
      │
      ▼
ComplaintEventFactory.create_* (...)
      │
      ▼
immutable ComplaintEvent
      │
      ▼
EventDispatcher.dispatch(event)
      │
      ▼
EventHandler.handle(event)  × N  (registration order)
```

## Interface

### EventDispatcher

| Method | Behavior |
|---|---|
| `register(handler)` | Append handler (registration order) |
| `unregister(handler)` | Remove first matching instance |
| `dispatch(event)` | Sync invoke all handlers; return `DispatchResult` |
| `registered_handlers()` | Shallow copy of handlers in order |

### EventHandler

| Method | Behavior |
|---|---|
| `handle(event)` | Process one event; exceptions are isolated |

### DispatchResult

| Field | Description |
|---|---|
| `success_count` | Handlers that completed without exception |
| `failed_count` | Handlers that raised |
| `handler_results` | Ordered per-handler outcomes |
| `ok` | `True` when `failed_count == 0` |

## Error handling

- One handler failure **must not** stop remaining handlers.
- Exceptions are caught, logged, and collected into `DispatchResult`.
- Complaint business writes are **not** rolled back by handler failure.

## Ordering

Handlers execute strictly in **registration order**.

## Out of scope (STOP)

Do **not** implement these consumers in TASK-046 (Notification landed in TASK-047;
Dashboard projection landed in TASK-050; KPI projection landed in TASK-051;
Workflow foundation landed in TASK-052):

- AI Handler

Also out of scope: broker selection, event store, threads/async workers,
HTTP/API changes.

## Implementation

- Module: `backend/app/modules/event_dispatcher/`
- Types: `EventDispatcher`, `EventHandler`, `DispatchResult`, `HandlerResult`
- Producer wiring: `ComplaintService` injects/uses `EventDispatcher`
- Related: TASK-045 (`COMPLAINT_EVENTS.md`), ADR-001, ADR-009

## Related docs

- `COMPLAINT_EVENTS.md` — event contract / factory
- `../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`
- `../../backend/README.md` — Developer Guide
