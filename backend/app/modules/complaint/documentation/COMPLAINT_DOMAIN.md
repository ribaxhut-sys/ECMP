# Complaint Domain Model (CAPABILITY-004…007)

## Aggregate Root — Complaint

| Field | Type | Notes |
|---|---|---|
| complaint_id | UUID | Identity |
| organization_id | UUID | Tenant |
| branch_id | UUID | Branch |
| queue_ticket_id | UUID | Visit context reference only |
| category | string | Free-form (no master-data validation) |
| title | string | Required |
| description | string | Required |
| priority | ComplaintPriority | LOW / NORMAL / HIGH / URGENT |
| status | ComplaintStatus | See lifecycle |
| resolution | Resolution \| None | Set only on resolve; immutable after CLOSED |
| created_at | datetime (UTC) | |
| updated_at | datetime (UTC) | |

## Value Object — Resolution

| Field | Type | Notes |
|---|---|---|
| summary | string | Required |
| resolved_by | string | Required |
| resolved_at | datetime (UTC) | Set at resolve time |

Resolution may only be created when transitioning to `RESOLVED`.
After `CLOSED`, resolution must not change (`RESOLUTION_IMMUTABLE`).

## Child Entity — Assignment (CAPABILITY-006)

| Field | Type | Notes |
|---|---|---|
| assignment_id | UUID | Identity |
| complaint_id | UUID | Parent aggregate |
| assignee_type | AssigneeType | USER (TEAM/QUEUE/SYSTEM design-ready) |
| assignee_id | string | Assignee identity |
| assigned_at | datetime (UTC) | |
| assigned_by | string | Actor who assigned |
| released_at | datetime \| None | Set on release |
| release_reason | string \| None | Optional |
| is_active | bool | At most one `true` per complaint |

### Aggregate assignment operations

| Method | Effect on Assignment | Complaint status |
|---|---|---|
| `assign(...)` | Create active row (rejects if active exists) | Unchanged |
| `reassign(...)` | Release active + append new active | Unchanged |
| `unassign(...)` | Release active | Unchanged |

## Child Entity — Escalation (CAPABILITY-007)

| Field | Type | Notes |
|---|---|---|
| escalation_id | UUID | Identity |
| complaint_id | UUID | Parent aggregate |
| level | EscalationLevel | LEVEL_1…LEVEL_4 |
| reason | string | Required |
| escalated_by | string | Actor who escalated |
| escalated_at | datetime (UTC) | |
| released_at | datetime \| None | Set when superseded |
| is_current | bool | At most one `true` per complaint |

### Aggregate escalation operations

| Method | Effect on Escalation | Assignment | Complaint status |
|---|---|---|---|
| `escalate(...)` | Release prior current (if any) + append new current; level must increase | Unchanged | Unchanged |

## Aggregate operations (CAPABILITY-005)

| Method | Transition | Notes |
|---|---|---|
| `start_processing()` | OPEN → IN_PROGRESS | |
| `resolve(summary, resolved_by)` | IN_PROGRESS → RESOLVED | Creates Resolution |
| `close()` | RESOLVED → CLOSED | Locks resolution |
| `reopen(reason?)` | RESOLVED → IN_PROGRESS | Clears resolution; reason not persisted |

All invalid transitions raise `ComplaintDomainError`.

## Priority

`LOW` · `NORMAL` · `HIGH` · `URGENT`

Invalid priority → domain / application error `INVALID_PRIORITY`.

## Category

Examples only (not enforced): Billing, Internet, Sales, Activation, General.

## Boundaries

- Domain must not import SQLAlchemy, FastAPI, or Queue modules
- ORM stays under `infrastructure/orm`
- Controllers must not contain business rules
- Repository remains persistence-only
