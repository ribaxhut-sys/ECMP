# Complaint Escalation Guide (CAPABILITY-007)

| Field | Value |
|---|---|
| ID | DOM-COMPLAINT-ESC-001 |
| Version | 1.0 |
| Owner | Backend Lead |
| Status | 🟢 Implemented |
| Last Review | 2026-07-24 |

## Objective

Escalation as a **child entity** of the Complaint aggregate root.
Determines **handling level** — does **not** change Assignment or Complaint
lifecycle status.

## Rules

| Rule | Behavior |
|---|---|
| 1 | New Complaint has no escalation |
| 2 | Escalate makes the new row current |
| 3 | Prior current becomes historical (`is_current=false`, `released_at` set) |
| 4 | History is append-only (prior level/reason/escalated_* never rewritten) |
| 5 | Escalation never mutates Assignment |
| 6 | Escalation never mutates Complaint status (`OPEN`…`CLOSED`) |
| 7 | Level must strictly increase (e.g. `LEVEL_3` → `LEVEL_2` rejected) |

## EscalationLevel

`LEVEL_1` · `LEVEL_2` · `LEVEL_3` · `LEVEL_4`

## Layers

```text
HTTP → Controller → ComplaintEscalationApplicationService
                 → Domain (Complaint.escalate)
                 → EscalationRepository port → SQLAlchemy → PostgreSQL
```

## Persistence

Table: `complaint_case_escalations` (FK → `complaint_cases.complaint_id`).

Partial unique index on `(complaint_id) WHERE is_current = true`.

Legacy ECMF `complaint_escalations` (FK → `complaints`) is unchanged.

## REST (API-406…408)

| API | Method | Path |
|---|---|---|
| API-406 | POST | `/api/v1/complaints/{id}/escalate` |
| API-407 | GET | `/api/v1/complaints/{id}/escalation` |
| API-408 | GET | `/api/v1/complaints/{id}/escalations` |

OpenAPI: `07 API Catalog/openapi/complaint-domain-service.v1.yaml`

## Out of Scope

SLA · Scheduler · Notification · Timeline · Dashboard · Audit · AI ·
Authentication · Auto-escalation · Workflow
