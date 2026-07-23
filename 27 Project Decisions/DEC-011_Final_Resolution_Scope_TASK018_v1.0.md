# Decision Record — Final Resolution Scope (TASK-018)

| Field | Value |
|---|---|
| ID | DEC-011 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-018) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-001, DEC-007, DEC-008, DEC-009, DEC-010, TASK-018

## Context

DEC-009 delivered appointment completion and left complaint/escalation open.
TASK-018 captures Final Resolution after a `COMPLETED` appointment (API-310)
without closing the complaint or escalation.

## Decision

**Extend the existing resolutions module and `complaint_resolutions` entity.**
Do not create a new module.

In scope for TASK-018:

- Submit Final Resolution once per complaint after appointment `COMPLETED`
- Persist summary, notes, follow-up flag, actor, timestamp on resolution entity
- Timeline event `complaint.final_resolution_submitted`
- Complaint Detail UI: Final Resolution section (submit + read-only after)

Remains **out of scope**:

- Complaint Closure / Escalation Closure
- Approval workflow
- SLA / Notification / Survey
- Auto Close

## Business Rules

- Complaint must exist and be `IN_PROGRESS`
- Appointment must be `COMPLETED` (reject `NO_SHOW` and non-completed)
- Only one Final Resolution per complaint
- Complaint remains `IN_PROGRESS`; escalation remains `APPROVED`
- Do **not** close complaint or escalation

## Rationale

Final Resolution is an intermediate HO Engineer step after field work.
Closure and approval are separate later tasks; completing an appointment must
not imply case closure.

## Impact

- OpenAPI adds API-310 (`POST .../final-resolution`) and companion GET
- Migration `0011_final_resolution` extends `complaint_resolutions`
- Write gate: Head Office Engineer / Admin (`appointments:complete`)
- Read: `complaints:read` (Branch Officer, Branch Supervisor, HO Scheduler, HO Engineer)

## Links

- Related: `DEC-010_Appointment_NoShow_Scope_TASK017_v1.0.md`
- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml`
