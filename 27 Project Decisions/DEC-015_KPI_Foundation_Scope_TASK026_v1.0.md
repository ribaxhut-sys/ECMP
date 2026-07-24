# Decision Record — KPI Foundation Scope (TASK-026)

| Field | Value |
|---|---|
| ID | DEC-015 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-026) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-013, DEC-014, TASK-026, API-318

## Context

Operational domains (Complaint, SLA, Timeline, Appointment, Resolution,
Escalation) already persist facts. TASK-026 adds a read-only KPI Foundation
that aggregates those facts for dashboard/analytics consumers.

## Decision

**Create `app/modules/kpi`.** No database migration. No KPI tables.
No materialized views. No scheduler. No writes to operational entities.

API-318 `GET /api/v1/kpi/summary` returns live aggregates:

- Complaint totals (total / open / closed)
- SLA stage completed / breached counts (assignment, appointment,
  resolution, escalation, overall)

Filters (optional): date range (`reportedAt`), branch, category, priority.

Permission: `kpi:read`.

Remains **out of scope**:

- Dashboard charts / realtime / caching / Redis
- Materialized views / scheduler
- Notifications / reporting exports (Excel/PDF)

## Rationale

KPI must never become a second source of truth. Computing aggregates from
operational tables keeps metrics consistent with SLA evaluation (DEC-013)
without duplicating state.

## Impact

- New module + OpenAPI API-318 + API Catalog
- Dashboard KPI Summary Card (simple cards only)
- RBAC adds `kpi:read`

## Links

- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml` (API-318)
