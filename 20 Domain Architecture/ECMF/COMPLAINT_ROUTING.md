# Complaint Routing Architecture (TASK-043)

| Field | Value |
|---|---|
| ID | ARCH-ECMF-ROUTING-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-043) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Centralize **initial destination** decisions for multi-source / multi-target
complaints (DEC-018). Routing is **not** a workflow engine and does **not**
replace Assignment, Escalation, or Authorization.

## Principle

```text
Create Complaint
      │
      ▼
ComplaintRoutingService.resolve_route(source_*, target_*)
      │
      ▼
immutable ComplaintRoute
      │
      ├── Complaint Service applies assignment_context → branch_id (projection)
      ├── Audit / Timeline consume route metadata
      └── Assignment Engine assigns users later (unchanged; no routing rules)
```

**Rule:** Routing logic lives only in `app/modules/routing`.  
Complaint Service, Assignment Service, Notification, SLA, and KPI **must not**
embed route matrices — they consume `ComplaintRoute` only.

## ComplaintRoute (immutable)

| Field | Meaning |
|---|---|
| `receiver_type` | `BRANCH` or `HEAD_OFFICE` |
| `receiver_id` | UUID of the organizational receiver (`target_id`) |
| `assignment_context` | Opaque map for Assignment consumers (`branchId` / `headOfficeId`) |
| `routing_reason` | Human-readable explanation of the decision |

## Default routes

| Source | Target | Receiver |
|---|---|---|
| CUSTOMER | BRANCH | Branch |
| BRANCH | HEAD_OFFICE | Head Office |
| HEAD_OFFICE | BRANCH | Branch |
| SYSTEM | HEAD_OFFICE | Head Office |

Any other combination (e.g. CUSTOMER→HEAD_OFFICE, BRANCH→BRANCH,
HEAD_OFFICE→HEAD_OFFICE) is **rejected** unless explicitly added to the matrix.

## Backward compatibility

Legacy create (`customerId` ± `branchId`) still resolves as CUSTOMER→BRANCH.
Omitting `branchId` yields `receiver_id=null` with Branch receiver type
(same prior behavior).

## Out of scope

- Workflow engine / BPMN
- Auto-assigning a user on create
- Changing Assignment / Timeline / Resolution / Appointment / Escalation / AuthZ APIs
- Notification / SLA / KPI route rules

## Implementation

- Module: `backend/app/modules/routing/`
- Service: `ComplaintRoutingService.validate_route` / `resolve_route`
- Enum: `ComplaintReceiverType`
- Related: DEC-018, DOM-ECMF-002
