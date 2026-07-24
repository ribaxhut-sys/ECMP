# Complaint Event Architecture (TASK-045)

| Field | Value |
|---|---|
| ID | ARCH-ECMF-EVENTS-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead / Integration Lead |
| Approver | Architecture Board (delegated via TASK-045) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Standardize **immutable Complaint domain events** for significant lifecycle
transitions so future Dashboard, Notification, Workflow, KPI, and AI modules
can consume a single contract.

TASK-045 established **event creation**. TASK-046 adds in-process
**dispatch** via `EventDispatcher` (still not an event bus).

## Principle

```text
Significant Complaint state transition
      │
      ▼
ComplaintEventFactory.create_* (...)
      │
      ▼
immutable ComplaintEvent (in memory)
      │
      ▼
EventDispatcher.dispatch(event)   ← TASK-046
      │
      └── registered EventHandler.handle(event) × N
          (consumers deferred; registration order; failure-isolated)
```

**Rules**

- Events are **immutable** (`frozen` dataclass + frozen payload map).
- **No** Kafka / RabbitMQ / Redis Streams / Pub-Sub.
- **No** event store / database table / outbox write in TASK-045/046.
- Producer (`ComplaintService`) must not know concrete consumers.
- Does **not** mutate Complaint aggregate, Assignment, Timeline,
  Resolution, Appointment, Escalation, Authorization, or ComplaintContext.
- No HTTP API / OpenAPI changes (backward compatible).

## ComplaintEvent fields

| Field | Description |
|---|---|
| `event_id` | UUID of the event instance |
| `event_type` | One of the Complaint* types below |
| `occurred_at` | UTC timestamp |
| `complaint_id` | Complaint aggregate id |
| `complaint_number` | Human-readable number |
| `current_status` | Status after the transition |
| `priority` | Complaint priority |
| `source` | Polymorphic origin (`source_type` + `source_id`) |
| `target` | Polymorphic destination (`target_type` + `target_id`) |
| `routing` | Optional `ComplaintRoute` snapshot |
| `context_reference` | Stable key (`complaint:{id}`) for ComplaintContext |
| `payload` | Immutable transition-specific metadata |

## Event types

| Type | Typical trigger |
|---|---|
| `ComplaintCreated` | Complaint create |
| `ComplaintAssigned` | Status becomes ASSIGNED (factory ready; Assignment module unchanged) |
| `ComplaintAccepted` | ASSIGNED → IN_PROGRESS (assignee acceptance) |
| `ComplaintInProgress` | Status becomes IN_PROGRESS |
| `ComplaintResolved` | Status becomes RESOLVED (factory ready) |
| `ComplaintClosed` | Explicit close / CLOSED status |
| `ComplaintEscalated` | Status becomes ESCALATED (factory ready) |

## Factory

`ComplaintEventFactory` methods:

- `create_created`
- `create_assigned`
- `create_accepted`
- `create_in_progress`
- `create_resolved`
- `create_closed`
- `create_escalated`

## Out of scope (STOP)

- Event bus / broker selection (ADR-009 still applies for future bus)
- Event store / outbox table persistence
- Concrete consumers (Dashboard, Workflow, KPI, AI) — TASK-048+
- Notification consumer — implemented in TASK-047 (`EVENT_CONSUMER.md`)
- Changing Assignment / Escalation / Resolution / Timeline modules
- Threads / async queue / background workers

## Implementation

- Module: `backend/app/modules/complaint_events/`
- Types: `ComplaintEvent`, `ComplaintEventType`, `EventSourceRef`, `EventTargetRef`
- Factory: `ComplaintEventFactory`
- Producer: `ComplaintService` (create / status / close paths) → `EventDispatcher`
- Dispatcher: `backend/app/modules/event_dispatcher/` — see `EVENT_DISPATCHER.md`
- Catalog: `08 Event Catalog/events/events.yaml` (EVT-009 … EVT-015)
- Related: TASK-042, TASK-043, TASK-044, TASK-046, ADR-001, ADR-009
