# ECMP Complaint Management Batch 1 — S2 Task 01 Implementation Report

| Field | Value |
|---|---|
| Document ID | GOV-S2-CM-B1-T01-001 |
| Date | 2026-07-29 |
| Status | 🟢 Complete |
| Scope | Complaint Aggregate Persistence Layer |
| Branch | `feature/cm-batch1-s2-persistence` |
| FRD / OpenAPI | Unchanged (per task constraints) |

## Objective

Replace in-memory `Batch1Store` production path with durable SQLAlchemy persistence + Alembic migration, retaining S1 API contracts (API-500…504) and S1 test behaviour.

## Delivered

| Deliverable | Location |
|---|---|
| Domain entities | `backend/app/modules/cm_batch1/entities.py` |
| SQLAlchemy ORM | `backend/app/modules/cm_batch1/models.py` |
| Repository | `backend/app/modules/cm_batch1/repository.py` |
| Alembic migration | `backend/alembic/versions/0040_cm_batch1_persistence.py` |
| Service / router refactor | `service.py`, `router.py` |
| In-memory store (unit tests) | `store.py` (protocol-compatible) |
| Tests | `backend/tests/test_cm_batch1.py` |

## Files created

- `backend/app/modules/cm_batch1/entities.py`
- `backend/app/modules/cm_batch1/models.py`
- `backend/app/modules/cm_batch1/repository.py`
- `backend/alembic/versions/0040_cm_batch1_persistence.py`
- `18 Architecture Governance/reviews/ECMP_CM_Batch1_S2_Task01_Persistence_v1.0.md`

## Files modified

- `backend/app/modules/cm_batch1/store.py` — domain import; `create` → `(entity, created)`; `commit` no-op
- `backend/app/modules/cm_batch1/service.py` — store protocol; commit on mutations
- `backend/app/modules/cm_batch1/router.py` — `get_db_session` + `CmBatch1Repository`
- `backend/app/modules/cm_batch1/__init__.py` — docstring
- `backend/app/models/__init__.py` — export Batch 1 ORM
- `backend/alembic/env.py` — register Batch 1 models
- `backend/tests/test_cm_batch1.py` — SQLite persistence fixtures + tests

## Migration summary (`0040_cm_batch1_persistence`)

| Table | Purpose |
|---|---|
| `cm_batch1_complaints` | Aggregate Root (`case_created` default false — D-02) |
| `cm_batch1_idempotency` | Request Id uniqueness (D-03) |
| `cm_batch1_channel_messages` | Channel Message Id uniqueness (D-03) |
| `cm_batch1_customer_locks` | FR-002 confirm lock |
| `cm_batch1_number_counters` | `CM-########` generator |

- Revises: `0039_admin_rbac_repair`
- **No** Case / Assignment / SLA / Escalation FK or Batch-2 columns
- Independent of legacy `complaints` / `complaint_cases`

## Test results

```text
python -m pytest backend/tests/test_cm_batch1.py -q
18 passed, 1 warning in ~3.1s
```

Includes original S1 suite + 3 S2 persistence tests (create/get/idempotent, 360+confirm+channel replay, migration revision chain).

## Non-goals (unchanged / not started)

- FR-003 / FR-004
- FRD / OpenAPI edits
- EVT-CM-* emission, audit trail, timeline, outbox
- Real Master Customer wiring
- Frontend

## Remaining issues

1. Apply migration on environments: `alembic upgrade head` (requires Postgres with `pgcrypto` / `gen_random_uuid()`).
2. Confirm lock still not enforced on create (known S1 gap; out of Task 01 scope).
3. SQLite used for unit persistence tests; production path is Postgres via Alembic.
4. Concurrent idempotency races rely on unique constraints + IntegrityError rewind — worth a dedicated multi-connection integration test against Postgres.

## Scope check

**PASS** — no Case / Assignment / SLA / Escalation / Resolution / Closure / Merge / Dashboard / Reporting / Batch 2 in this change.

---

*End of GOV-S2-CM-B1-T01-001.*
