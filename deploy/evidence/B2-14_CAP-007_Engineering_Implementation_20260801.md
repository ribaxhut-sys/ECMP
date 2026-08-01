# B2-14 — CAP-007 Engineering Implementation

| Field | Value |
|---|---|
| Document ID | ENG-B2-14-CAP007-001 |
| Sprint | B2-14 |
| Date | 2026-08-01 |
| Authority | ARB / Principal Engineer / QA Lead / Repository Governance |
| Scope | Implement CAP-007 against normative API-040 only |
| Non-goals | No BR / FRD / OpenAPI invent; no CAP-008; no Queue Service; no API-390; no API-513; no Mode B |
| Prerequisite | B2-13 API-040 NORMATIVE (`dashboard-queues.v1.yaml` 1.0.0) |
| Verdict | **CAP-007 ENGINEERING COMPLETE** |

## 1. Contract implemented

| Item | Result |
|---|---|
| Spec | `07 API Catalog/openapi/dashboard-queues.v1.yaml` **1.0.0** (unchanged) |
| Endpoint | `GET /v1/dashboard/queues` |
| Permission | `dashboard:read` (existing auth framework) |
| Response | Unwrapped `{ asOf, queues[] }` — QueueEntry per DOM-ECMF-003 |
| Case SoT | Sprint ECMF `cases` (`implementation/backend`) |
| Drill-down | FE filters Case list via API-005 only (DEC-CAP007-BQ-001 §3) |

## 2. Code locations

| Layer | Path |
|---|---|
| Route | `implementation/backend/app/main.py` |
| Application service | `implementation/backend/app/service.py` (`get_dashboard_queues`) |
| DTO | `implementation/backend/app/schemas.py` (`QueueEntry`, `DashboardQueuesResponse`) |
| Auth fixture | `implementation/backend/app/auth.py` (`dashboard:read` on supervisors) |
| API client | `implementation/frontend/src/api/dashboard.ts` |
| UI | `implementation/frontend/src/features/case-queue/components/DashboardQueuesPanel.tsx` |
| Workspace | `implementation/frontend/src/features/case-queue/CaseQueueWorkspace.tsx` |

Domain layering follows ADR-005 minimal split (Service + schemas DTO). No invented Aggregate/Repository packages.

## 3. Tests (TC-040)

| Level | Evidence | Result |
|---|---|---|
| API / Integration | `implementation/backend/tests/test_dashboard_queues_api040.py` (7) | PASS |
| Frontend unit | `DashboardQueuesPanel.test.tsx` (2) | PASS |
| Browser E2E | No harness in Sprint ECMF tree | N/A (not invented) |

TC-040 steps 1–4 covered by API suite (unit scope, foreign supervisor, reconcile API-005, 401/403, GET-only).

## 4. Traceability / register

| Artifact | Change |
|---|---|
| TRC-L-008 | Planned → **Approved** |
| CAP-007 register | → Implemented (B2-14) |
| API Catalog README | API-040 → Implemented (schema file untouched) |
| TC-040 catalog | → Implemented (B2-14 API suite) |

## 5. Explicit non-touch

- OpenAPI YAML body / FRD / Business Rules — **not modified**
- Mode A `backend/` API-390 / CAP-008 Aggregate / API-513 — **not modified**
- Enterprise Platform / Mode B — **not modified**

---

*End of ENG-B2-14-CAP007-001.*
