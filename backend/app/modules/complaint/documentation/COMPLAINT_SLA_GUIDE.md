# Complaint SLA Guide (CAPABILITY-008)

| Field | Value |
|---|---|
| ID | DOM-COMPLAINT-SLA-001 |
| Version | 1.0 |
| Owner | Backend Lead |
| Status | 🟢 Implemented |
| Last Review | 2026-07-24 |

## Objective

SLA as a **child entity** of the Complaint aggregate root.
Calculates **due time / remaining / breach** only — does **not** change
Complaint status, create Escalation, send Notification, or run a scheduler.

## Rules

| Rule | Behavior |
|---|---|
| 1 | At most one active ComplaintSLA per Complaint |
| 2 | SLA starts from an SLAPolicy |
| 3 | `due_at = started_at + target_minutes` |
| 4 | Closing Complaint completes active SLA (`completed_at`, `is_active=false`) |
| 5 | If `current_time > due_at` → `is_breached=true`, `breached_at` set once |
| 6 | SLA never mutates Complaint status |
| 7 | SLA never creates Escalation |
| 8 | SLA never sends Notification |

## Entities

### SLAPolicy

`policy_id` · `name` · `target_minutes` · `is_default` · `description?`

Shared by many Complaints. One default policy is seeded.

### ComplaintSLA

`sla_id` · `complaint_id` · `policy_id` · `started_at` · `due_at` ·
`completed_at?` · `breached_at?` · `is_active` · `is_breached`

## Layers

```text
HTTP → Controller → ComplaintSLAApplicationService
                 → Domain (Complaint.start_sla / complete_sla / detect_breach)
                 → ComplaintSlaRepository + SLAPolicyRepository
                 → SQLAlchemy → PostgreSQL
```

## Persistence

| Table | Role |
|---|---|
| `complaint_sla_policies` | CA BC SLAPolicy (legacy ECMF `sla_policies` unchanged) |
| `complaint_case_slas` | ComplaintSLA child of `complaint_cases` |

Partial unique index on `(complaint_id) WHERE is_active = true`.

Migration: `0032_complaint_sla`.

## REST (API-409…412)

| API | Method | Path |
|---|---|---|
| API-409 | POST | `/api/v1/complaints/{id}/sla/start` |
| API-410 | POST | `/api/v1/complaints/{id}/sla/complete` |
| API-411 | POST | `/api/v1/complaints/{id}/sla/recalculate` |
| API-412 | GET | `/api/v1/complaints/{id}/sla` |

OpenAPI: `07 API Catalog/openapi/complaint-domain-service.v1.yaml`

## Out of Scope

Scheduler · Notification · Escalation Trigger · Timeline · Dashboard · Audit ·
AI · Authentication · Rule Engine · Workflow
