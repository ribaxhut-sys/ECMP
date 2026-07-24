# Complaint Context Architecture (TASK-044)

| Field | Value |
|---|---|
| ID | ARCH-ECMF-CONTEXT-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-044) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Provide **one immutable object** representing the operational state of a
Complaint for future consumers (Dashboard, KPI, Notification, Workflow, AI).

Complaint Context is a **read model**, not a new aggregate and not a new table.

## Principle

```text
Complaint + Assignment + SLA + Routing (resolve from source/target)
      │
      ▼
ComplaintContextService.build_context(complaintId)
      │
      ▼
immutable ComplaintContext
      │
      ├── ComplaintService.get_context / refresh_context (optional)
      └── Future: Dashboard / KPI / Notification / Workflow / AI
```

**Rules**

- Assembled from existing data only — **no persistence**, **no cache**.
- Does **not** mutate Complaint, Assignment, Timeline, Resolution,
  Appointment, Escalation, Authorization, or Routing Service.
- No new API endpoints in TASK-044 (backward compatible).

## ComplaintContext fields

| Field | Source |
|---|---|
| `complaint` | Complaint header snapshot |
| `current_assignment` | Current `ComplaintAssignment` (`is_current=true`) or null |
| `current_status` | `complaint.status` |
| `current_sla` | `SlaRecord` for the complaint or null |
| `priority` | `complaint.priority` |
| `source` | `source_type` + `source_id` (DEC-018) |
| `target` | `target_type` + `target_id` (DEC-018) |
| `routing` | `ComplaintRoute` via `ComplaintRoutingService.resolve_route` |
| `current_assignee` | Projected from current assignment or null |
| `created_at` / `updated_at` | Complaint timestamps |

## Service

| Method | Behavior |
|---|---|
| `build_context(complaintId)` | Load live data → assemble frozen `ComplaintContext` |
| `refresh_context(complaintId)` | Re-assemble from live data (no cache; same as build) |

## Out of scope

- New database table / materialized view / Redis cache
- Public HTTP API for context
- Changing Assignment / Timeline / Resolution / Appointment / Escalation / AuthZ
- Changing Routing matrix

## Implementation

- Module: `backend/app/modules/complaint_context/`
- Types: `ComplaintContext`, nested snapshots (`ComplaintSnapshot`,
  `AssignmentSnapshot`, `SlaSnapshot`, `SourceRef`, `TargetRef`, `AssigneeRef`)
- Service: `ComplaintContextService`
- Optional consumer: `ComplaintService.get_context` / `refresh_context`
- Related: DEC-018, TASK-042, TASK-043
