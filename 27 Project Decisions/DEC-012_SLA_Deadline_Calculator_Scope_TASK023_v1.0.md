# Decision Record — SLA Deadline Calculator Scope (TASK-023)

| Field | Value |
|---|---|
| ID | DEC-012 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-023) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-001, TASK-021, TASK-022, TASK-023, API-314

## Context

TASK-021 delivered the `sla_records` foundation (statuses `PENDING`, deadlines
NULL). TASK-022 delivered configurable SLA policies (API-315–317) with at most
one active policy. TASK-023 computes immutable deadline snapshots when a
complaint is created.

## Decision

**Extend the existing `app/modules/sla` module.** Do not create a new module.
No database migration — reuse `sla_records` deadline columns.

In scope for TASK-023:

- On complaint create: require an active SLA policy
- Evaluate the active policy **once** at create time
- Persist immutable due-at snapshots on `sla_records`:
  - `assignment_due_at` = `created_at` + `assignment_target_minutes`
  - `appointment_due_at` = `created_at` + `appointment_target_minutes`
  - `resolution_due_at` = `created_at` + `resolution_target_minutes`
  - `escalation_due_at` = `created_at` + `escalation_target_minutes`
  - `overall_due_at` = `created_at` + `overall_target_minutes`
- All SLA dimension statuses remain `PENDING`
- Existing complaint SLA rows are never recalculated when policy changes
- Complaint Detail SLA card displays due dates via API-314

Remains **out of scope**:

- Breach detection
- Countdown timers
- Scheduler / background jobs
- Notifications
- Dashboard / Reporting / KPI
- Auto updates of existing SLA records

## Business Rules

- Active SLA policy is mandatory for complaint creation (reject if none)
- Deadlines are calculated only once at create
- Snapshots are immutable; future policy activation does not alter them
- SLA status remains `PENDING` (no breach / ON_TIME logic)

## Rationale

Policy evaluation at create-time produces a stable audit snapshot. Recalculating
existing complaints when policies change would rewrite historical commitments
and break operational accountability.

## Impact

- Complaint create path rejects when no active SLA policy exists
- API-314 response schema documents populated due dates for new complaints
- No new public endpoints; no schema migration

## Links

- Related: TASK-021, TASK-022
- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml` (API-314)
