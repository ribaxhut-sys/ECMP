# Decision Record — SLA Breach Detection Scope (TASK-024)

| Field | Value |
|---|---|
| ID | DEC-013 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-024) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-012, TASK-023, TASK-024, API-314

## Context

TASK-023 stores immutable deadline snapshots on `sla_records` at complaint
create. TASK-024 evaluates status dimensions against those snapshots when
business events occur.

## Decision

**Extend `app/modules/sla`.** Do not create a new module. No migration.
Never re-read SLA Policy during evaluation. Never modify `*_due_at`.

Evaluation rule per stage (assignment / appointment / resolution /
escalation / overall):

- If completed and `completed_at <= due_at` → `COMPLETED`
- Else if `now <= due_at` → `PENDING`
- Else → `BREACHED`

Completion facts (not policy):

| Stage | Completed when |
|---|---|
| Assignment | First `assigned_at` exists |
| Appointment | Appointment `completed_at` exists |
| Resolution | `final_resolution_at` or resolution `resolved_at` |
| Escalation | Escalation `closed_at` exists |
| Overall | Complaint `closed_at` exists |

Trigger evaluation (no scheduler / cron / worker) on:

- Complaint created
- Assignment completed
- Appointment completed
- Resolution finalized (final resolution or resolve)
- Escalation closed
- Complaint closed
- API-314 read (re-evaluate from stored due_at only — display freshness
  without a background worker)

Evaluation is idempotent: repeated runs with unchanged business data yield
the same statuses.

Remains **out of scope**:

- Scheduler / cron / queue
- Notifications / email / SMS / push / websocket
- Dashboard / reporting / KPI
- Deadline recalculation
- EVT-004 emission (deferred)

## Rationale

Status evaluation must honor historical commitments captured as due-at
snapshots. Re-reading policy or rewriting deadlines would break auditability
(DEC-012). Event-driven evaluation avoids background jobs while keeping the
SLA card current after lifecycle actions.

## Impact

- Domain services call internal `SlaService.evaluate_for_complaint`
- API-314 returns updated status fields; no new public endpoints
- Frontend SLA Card displays PENDING / COMPLETED / BREACHED

## Links

- Related: `DEC-012_SLA_Deadline_Calculator_Scope_TASK023_v1.0.md`
- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml` (API-314)
