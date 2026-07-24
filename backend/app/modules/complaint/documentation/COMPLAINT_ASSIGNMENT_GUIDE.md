# Complaint Assignment Guide (CAPABILITY-006)

| Field | Value |
|---|---|
| ID | DOM-COMPLAINT-ASSIGN-001 |
| Version | 1.0 |
| Owner | Backend Lead |
| Status | 🟢 Implemented |
| Last Review | 2026-07-24 |

## Objective

Assignment as a **child entity** of the Complaint aggregate root.
Determines **who is responsible** — does **not** change Complaint lifecycle status.

## Rules

| Rule | Behavior |
|---|---|
| 1 | At most one active Assignment per Complaint |
| 2 | First assign creates an active Assignment |
| 3 | Reassign releases the prior row and appends a new active row |
| 4 | History is append-only (prior assignee/assigned_at never rewritten) |
| 5 | Unassign releases the active row; no active assignee remains |
| 6 | Assignment never mutates Complaint status (`OPEN`…`CLOSED`) |

## AssigneeType

| Value | Status |
|---|---|
| `USER` | Implemented |
| `TEAM` | Design-ready (rejected until later capability) |
| `QUEUE` | Design-ready |
| `SYSTEM` | Design-ready |

## Layers

```text
HTTP → Controller → ComplaintAssignmentApplicationService
                 → Domain (Complaint.assign / reassign / unassign)
                 → AssignmentRepository port → SQLAlchemy → PostgreSQL
```

## Persistence

Table: `complaint_case_assignments` (FK → `complaint_cases.complaint_id`).

Partial unique index on `(complaint_id) WHERE is_active = true`.

Legacy ECMF `complaint_assignments` (FK → `complaints`) is unchanged.

## REST (API-401…405)

| API | Method | Path |
|---|---|---|
| API-401 | POST | `/api/v1/complaints/{id}/assign` |
| API-402 | POST | `/api/v1/complaints/{id}/reassign` |
| API-403 | POST | `/api/v1/complaints/{id}/unassign` |
| API-404 | GET | `/api/v1/complaints/{id}/assignment` |
| API-405 | GET | `/api/v1/complaints/{id}/assignments` |

OpenAPI: `07 API Catalog/openapi/complaint-domain-service.v1.yaml`

## Out of Scope

Escalation · SLA · Notification · Timeline · Dashboard · Audit · AI ·
Authentication · Workgroup · Rule Engine
