# Decision Record — Appointment Booking Scope (TASK-014)

| Field | Value |
|---|---|
| ID | DEC-007 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-014) |
| Status | Approved |
| Last Review | 2026-07-23 |
| Next Review | 2026-10-23 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-23
- Related: DEC-001, TASK-014

## Context

DEC-001 placed Branch/HO **Appointment** (along with Schedule Slot and Work Order) outside product scope until a Blueprint revision. TASK-014 explicitly delivers Head Office Appointment **booking** for approved escalations (API-305 / API-306).

## Decision

**Partial supersession of DEC-001 for Appointment booking only.**

In scope for TASK-014:

- Book one active (`BOOKED`) appointment against an `APPROVED` escalation
- Read appointment by id
- Timeline event `complaint.appointment_booked`
- Escalation Detail UI: booking form + detail card

Remains **out of scope** (DEC-001 still binds):

- Calendar View
- Slot Generator
- Customer Check-In
- Appointment Completion / Cancel workflow
- Notification
- SLA
- Auto Close
- Work Order

## Rationale

TASK-014 is an approved delivery task with fixed API IDs and UAT criteria. Narrowing the supersession to booking avoids inventing the full scheduling product while unblocking the approved escalation → appointment path.

## Impact

- OpenAPI may add API-305 / API-306 and `complaint.appointment_booked`
- Foundation `backend/` may add `appointments` table (migration `0007`) and module
- Complaint stays `IN_PROGRESS`; escalation stays `APPROVED` on book

## Links

- Related: `DEC-001_Business_Baseline_SoT_v1.0.md`
- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml`
