# ECMP Complaint Management Batch 1 — S1 Implementation Note

| Field | Value |
|---|---|
| Document ID | GOV-S1-CM-B1-001 |
| Date | 2026-07-29 |
| Status | 🟢 Complete (slice) |
| Scope | FR-002 + FR-001 (no Case) |

## Delivered

| Item | Location |
|---|---|
| Module | `backend/app/modules/cm_batch1/` |
| Routes | `/api/v1/cm/customers/*`, `/api/v1/cm/complaints*` |
| Tests | `backend/tests/test_cm_batch1.py` — **15 passed** |
| APIs live (S1) | API-500…504 |

## Behaviour locked in code

- Exactly one customer key type
- Enumeration rate-limit / progressive delay / block (D-04)
- Master Customer stub read-only; write-back rejected (ADR-002)
- Batch 1 360 minimum: profile + active + count + `asOf` (D-05)
- Create → `REGISTERED`, `caseCreated=false` (D-02)
- Request Id + Channel Message Id idempotent replay (D-03)

## Explicit follow-ons (S2)

- Persist Aggregate + idempotency tables (Alembic)
- Wire real Master Customer API
- FR-003 Duplicate APIs (API-505/506)
- FR-004 Attachment transfer (API-508) + D-06
- Execute remaining TC-CM-* against persistence

## Non-changes

- FRD / BR / ADR / Batch 1 scope unchanged
- Legacy `/api/v1/complaints` stack untouched

---

*End of GOV-S1-CM-B1-001.*
