# Decision Record — Customer No Show Scope (TASK-017)

| Field | Value |
|---|---|
| ID | DEC-010 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-017) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-001, DEC-007, DEC-008, DEC-009, TASK-017

## Context

DEC-008/009 delivered check-in and completion and left Customer No Show out of scope. TASK-017 marks `BOOKED` appointments as `NO_SHOW` when the customer does not arrive (API-309).

## Decision

**Partial extension of DEC-007 for Customer No Show only.**

In scope for TASK-017:

- Mark a `BOOKED` appointment once as `NO_SHOW`
- Persist reason, actor, timestamp
- Timeline event `complaint.appointment_no_show`
- Escalation Detail UI: Mark No Show button, confirm dialog, display

Remains **out of scope**:

- Complaint Close / Escalation Close
- Reschedule / Automatic rebooking
- SLA / Notification / Survey
- Calendar / Auto Close

## Rationale

TASK-017 is an approved delivery task with fixed API ID and UAT criteria. No-show must not auto-close complaint or escalation, and cannot apply after check-in or completion.

## Impact

- OpenAPI may add API-309 and `complaint.appointment_no_show`
- Migration `0010_appointment_no_show` extends `appointments`
- Write gate: Head Office Scheduler / Admin (`escalations:review`)
- Complaint stays `IN_PROGRESS`; escalation stays `APPROVED` on no-show

## Links

- Related: `DEC-009_Appointment_Completion_Scope_TASK016_v1.0.md`
- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml`
