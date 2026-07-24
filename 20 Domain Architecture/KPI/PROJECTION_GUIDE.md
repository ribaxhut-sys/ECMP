# KPI Projection Foundation (TASK-051)

| Field | Value |
|---|---|
| ID | ARCH-KPI-PROJECTION-001 |
| Version | 1.0 |
| Owner | KPI PO / Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-051) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Maintain a **live operational KPI read model** (`KpiProjection`) updated
only from Complaint lifecycle events via `EventDispatcher`.

The projection is **read-only** to consumers. It must **not** query Complaint
aggregates or call `ComplaintService` during updates.

## What this is

- Immutable `KpiProjection` snapshot
- `KpiProjectionStore` (in-memory, single projection)
- `KpiProjectionHandler` implementing `EventHandler`
- Registration from composition root (not ComplaintService)

## What this is NOT

- Not an HTTP API / OpenAPI endpoint (no API changes)
- Not a database table, cache, or materialized view
- Not a change to Complaint aggregate, ComplaintContext, ComplaintEvent,
  EventDispatcher, Notification, Dashboard Projection, Assignment,
  Resolution, Appointment, or Escalation
- Not a replacement for the existing KPI summary API (`KpiService` /
  TASK-026) — that remains a separate read path over operational tables

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
KpiProjectionHandler.handle(event)
      │
      ▼
KpiProjectionStore.apply(event)
      │
      ▼
immutable KpiProjection snapshot
```

## Projection fields

| Field | Meaning |
|---|---|
| `total_received` | Cumulative ComplaintCreated count |
| `total_closed` | Cumulative ComplaintClosed count |
| `total_resolved` | Cumulative ComplaintResolved count |
| `total_escalated` | Cumulative ComplaintEscalated count |
| `current_open` | Not RESOLVED and not CLOSED |
| `current_in_progress` | Current IN_PROGRESS count |
| `sla_breached` | Incremented only if event payload `slaBreached=true` |
| `closure_rate` | `total_closed / total_received` (0 when received = 0) |
| `resolution_rate` | `total_resolved / total_received` (0 when received = 0) |
| `updated_at` | Last applied event timestamp |

## Projection rules

| Event | Rule |
|---|---|
| ComplaintCreated | `total_received++`, `current_open++` |
| ComplaintAssigned | Transition `fromStatus` → ASSIGNED (open/in_progress adjust) |
| ComplaintAccepted | Marker only (no counter move) — avoids double-count with InProgress |
| ComplaintInProgress | Transition `fromStatus` → IN_PROGRESS (`current_in_progress++`) |
| ComplaintResolved | `total_resolved++`; transition → RESOLVED; open/in_progress adjust |
| ComplaintClosed | `total_closed++`; transition → CLOSED; open/in_progress adjust |
| ComplaintEscalated | `total_escalated++`; transition → ESCALATED |

Transitions use `payload.fromStatus` when present. Current counters never go
below zero. Rates are derived on snapshot only.

## Calculation rules

```text
closure_rate     = closed / received   (0.0 if received == 0)
resolution_rate  = resolved / received (0.0 if received == 0)
```

## Implementation

- `backend/app/modules/kpi/projection_models.py`
- `backend/app/modules/kpi/projection_store.py`
- `backend/app/modules/kpi/projection_handler.py`
- `backend/app/modules/kpi/projection_registration.py`
- Composition: `backend/app/dependencies/events.py`

## Out of scope (STOP)

HTTP projection endpoint, persistence, SLA breach projector (beyond payload
flag), role/org filtered KPI views, workflow execution (TASK-053+).
