# Dashboard Projection Foundation (TASK-050)

| Field | Value |
|---|---|
| ID | ARCH-DASH-PROJECTION-001 |
| Version | 1.0 |
| Owner | Dashboard PO / Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-050) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Maintain a **live operational read model** (`DashboardProjection`) updated
only from Complaint lifecycle events via `EventDispatcher`.

The projection is **read-only** to consumers. It must **not** query Complaint
aggregates or call `ComplaintService` during updates.

## What this is

- Immutable `DashboardProjection` snapshot
- `DashboardProjectionStore` (in-memory, single projection)
- `DashboardProjectionHandler` implementing `EventHandler`
- Registration from composition root (not ComplaintService)

## What this is NOT

- Not an HTTP API / OpenAPI endpoint (no API changes)
- Not a database table, cache, or materialized view
- Not a change to Complaint aggregate, ComplaintEvent, EventDispatcher,
  Notification chain, Assignment, Resolution, Appointment, Escalation

## Principle

```text
ComplaintService (Producer)
      │
      ▼
ComplaintEventFactory
      │
      ▼
EventDispatcher.dispatch(event)
      │
      ▼
DashboardProjectionHandler.handle(event)
      │
      ▼
DashboardProjectionStore.apply(event)
      │
      ▼
immutable DashboardProjection snapshot
```

## Projection fields

| Field | Meaning |
|---|---|
| `total_complaints` | Complaints created |
| `open_complaints` | Not RESOLVED and not CLOSED |
| `assigned_complaints` | Current ASSIGNED count |
| `in_progress_complaints` | Current IN_PROGRESS count |
| `resolved_complaints` | Current RESOLVED count |
| `closed_complaints` | Current CLOSED count |
| `escalated_complaints` | Current ESCALATED count |
| `breached_sla` | Incremented only if event payload `slaBreached=true` (no dedicated breach event in this task) |
| `updated_at` | Last applied event timestamp |

## Projection rules

| Event | Rule |
|---|---|
| ComplaintCreated | `total++`, `open++` |
| ComplaintAssigned | Transition `fromStatus` → ASSIGNED |
| ComplaintAccepted | Marker only (no counter move) — avoids double-count with InProgress |
| ComplaintInProgress | Transition `fromStatus` → IN_PROGRESS |
| ComplaintResolved | Transition `fromStatus` → RESOLVED; open adjusts |
| ComplaintClosed | Transition `fromStatus` → CLOSED; open adjusts |
| ComplaintEscalated | Transition `fromStatus` → ESCALATED |

Transitions use `payload.fromStatus` when present. Status buckets never go
below zero.

## Implementation

- `backend/app/modules/dashboard/projection_models.py`
- `backend/app/modules/dashboard/projection_store.py`
- `backend/app/modules/dashboard/projection_handler.py`
- `backend/app/modules/dashboard/projection_registration.py`
- Composition: `backend/app/dependencies/events.py`

## Out of scope (STOP)

HTTP projection endpoint, persistence, SLA breach projector (beyond payload
flag), role/org filtered views (BR-DASH-01).
