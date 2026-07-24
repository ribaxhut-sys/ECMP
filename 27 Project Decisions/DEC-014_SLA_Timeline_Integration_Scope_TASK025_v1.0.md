# Decision Record — SLA Timeline Integration Scope (TASK-025)

| Field | Value |
|---|---|
| ID | DEC-014 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-025) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-013, TASK-024, TASK-025, API-209, API-314

## Context

TASK-024 evaluates SLA statuses from immutable due-at snapshots. Operators
need an audit trail of meaningful SLA transitions on the existing complaint
timeline (not a separate SLA timeline, and not notifications).

## Decision

**Reuse `complaint_timelines`.** Do not create a separate SLA timeline module
or table.

After each SLA evaluation, emit a timeline event **only when** a stage status
changes to `COMPLETED` or `BREACHED`. Identical re-evaluations produce no
duplicate events.

Event types:

- `sla.assignment.completed` / `sla.assignment.breached`
- `sla.appointment.completed` / `sla.appointment.breached`
- `sla.resolution.completed` / `sla.resolution.breached`
- `sla.escalation.completed` / `sla.escalation.breached`
- `sla.overall.completed` / `sla.overall.breached`

Actor is always **SYSTEM** (`actor_user_id` null; UI shows "System").

Payload metadata includes stage, old/new status, dueAt, and actor=`SYSTEM`.

Remains **out of scope**:

- Notifications / email / SMS / push / websocket
- Dashboard / reporting / KPI
- Scheduler / queue

## Rationale

Timeline is the established audit surface for complaint activity. Emitting
only on real status changes keeps the trail sparse and idempotent with
TASK-024's repeated evaluations.

## Impact

- `TimelineEvent` enum + OpenAPI TimelineEvent + API-209 description updated
- `SlaService.evaluate_for_complaint` writes timeline rows on transitions
- Complaint Timeline UI labels SLA events

## Links

- Related: `DEC-013_SLA_Breach_Detection_Scope_TASK024_v1.0.md`
- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml` (API-209)
