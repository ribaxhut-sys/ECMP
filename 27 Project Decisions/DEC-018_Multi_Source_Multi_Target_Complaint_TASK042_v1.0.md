# Decision Record — Multi-Source & Multi-Target Complaint (TASK-042)

| Field | Value |
|---|---|
| ID | DEC-018 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-042) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-24
- Related: TASK-042, DOM-ECMF-002, API create complaint

## Context

Complaints were modeled as customer-originated and branch-targeted only
(`customer_id` required, optional `branch_id`). Operational reality requires
complaints originated by Branch, Head Office, or System, and targeted at
Branch or Head Office — without splitting the Complaint aggregate or changing
lifecycle / Assignment / Timeline / Resolution / Appointment / Escalation /
Authorization.

## Decision

**Keep a single Complaint aggregate and table.** Add polymorphic fields:

| Field | Purpose |
|---|---|
| `source_type` | `ComplaintSourceType`: CUSTOMER, BRANCH, HEAD_OFFICE, SYSTEM |
| `source_id` | UUID of the originator (entity depends on `source_type`) |
| `target_type` | `ComplaintTargetType`: BRANCH, HEAD_OFFICE |
| `target_id` | UUID of the destination (entity depends on `target_type`) |

Enums are stored as `VARCHAR` so future values (VENDOR, REGIONAL, …) can be
added in application code **without schema changes**.

Legacy columns remain:

- `customer_id` — populated when `source_type=CUSTOMER`; nullable otherwise
- `branch_id` — populated when `target_type=BRANCH` (initial assignment
  context); cleared when `target_type=HEAD_OFFICE`

### Lifecycle

Unchanged: OPEN/NEW → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED
(existing status machine and related workflows untouched).

### Assignment

Assignment engine/API is **not** modified. Initial operational branch context
is derived only from `target_type` / `target_id` → `branch_id` when target is
BRANCH.

### API backward compatibility

Legacy create payload (`customerId` + optional `branchId`) continues to work
and implies:

- `source_type = CUSTOMER`
- `source_id = customerId`
- `target_type = BRANCH`
- `target_id = branchId` (may be null if branch omitted)

Generalized create requires `sourceType`, `sourceId`, `targetType`, and
`targetId` together.

## Anti-patterns (rejected)

- Separate `BranchComplaint` / `CustomerComplaint` / `HeadOfficeComplaint` tables
- Duplicating complaint tables or aggregates
- Changing Assignment, Timeline, Resolution, Appointment, Escalation, or AuthZ

## Impact

- Migration `0026_complaint_source_target` + backfill
- OpenAPI Complaint create/response schemas
- Domain / ERD / Architecture docs

## Links

- Contract: `07 API Catalog/openapi/complaint-service.v1.yaml`
- Migration: `backend/alembic/versions/0026_complaint_source_target.py`
- Domain: `20 Domain Architecture/ECMF/`
