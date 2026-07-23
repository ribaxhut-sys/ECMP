# Decision Record — Appointment Completion Scope (TASK-016)

| Field | Value |
|---|---|
| ID | DEC-009 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-016) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-001, DEC-007, DEC-008, TASK-016

## Context

DEC-008 authorized Customer Check-In and left Appointment Completion out of scope. TASK-016 delivers completion for `CHECKED_IN` appointments (API-308).

## Decision

**Partial extension of DEC-007/008 for Appointment Completion only.**

In scope for TASK-016:

- Complete a `CHECKED_IN` appointment once (`COMPLETED`)
- Persist `completionResult` (`COMPLETED` | `PARTIALLY_COMPLETED`), notes, actor, timestamp
- Timeline event `complaint.appointment_completed`
- Escalation Detail UI: Complete button, confirm dialog, display

Remains **out of scope**:

- Complaint Close / Escalation Close
- Customer No Show
- SLA / Notification / Survey / Rating
- Calendar / Auto Close

## Rationale

TASK-016 is an approved delivery task with fixed API ID and UAT criteria. Completion must not auto-close complaint or escalation.

## Impact

- OpenAPI may add API-308 and `complaint.appointment_completed`
- Migration `0009_appointment_completion` extends `appointments`
- Permission `appointments:complete` for Head Office Engineer / Admin
- Complaint stays `IN_PROGRESS`; escalation stays `APPROVED` on complete

## Links

- Related: `DEC-008_Appointment_CheckIn_Scope_TASK015_v1.0.md`
- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml`
