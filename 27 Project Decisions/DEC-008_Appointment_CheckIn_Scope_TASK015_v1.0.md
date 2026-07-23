# Decision Record — Appointment Check-In Scope (TASK-015)

| Field | Value |
|---|---|
| ID | DEC-008 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-015) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-001, DEC-007, TASK-015

## Context

DEC-007 authorized Appointment **booking** only and left Customer Check-In out of scope. TASK-015 delivers check-in for `BOOKED` appointments (API-307).

## Decision

**Partial extension of DEC-007 for Customer Check-In only.**

In scope for TASK-015:

- Check in a `BOOKED` appointment once (`CHECKED_IN`)
- Store `checkedInAt` / `checkedInBy` / check-in notes
- Timeline event `complaint.appointment_checked_in`
- Escalation Detail UI: Check-In button, confirm dialog, display

Remains **out of scope**:

- Appointment Completion
- Customer No Show
- Notification / SLA / Auto Close
- Calendar / Slot Generator

## Rationale

TASK-015 is an approved delivery task with fixed API ID and UAT criteria. Narrowing scope avoids inventing completion/no-show workflows.

## Impact

- OpenAPI may add API-307 and `complaint.appointment_checked_in`
- Migration `0008_appointment_checkin` extends `appointments`
- Complaint stays `IN_PROGRESS`; escalation stays `APPROVED` on check-in

## Links

- Related: `DEC-007_Appointment_Booking_Scope_TASK014_v1.0.md`
- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml`
