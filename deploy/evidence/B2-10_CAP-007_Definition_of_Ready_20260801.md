# B2-10 — CAP-007 Definition of Ready

| Field | Value |
|---|---|
| Document ID | GOV-B2-10-DOR-001 |
| Sprint | B2-10 |
| Date | 2026-08-01 |
| Authority | ARB / BA / Chief Solution Architect / Repository Governance |
| Scope | DoR assessment for CAP-007 **only** — no BE/FE/OpenAPI/BR/FRD content edits |
| Prerequisite | B2-09 QUEUE ARCHITECTURE RATIONALIZATION COMPLETE |
| Verdict | **CAP-007 NOT READY** |

## 1. Recommendation (exactly one)

**Continue Draft** — FRD-006 remains 🟡 Draft; API-040 remains non-normative draft.

Not LOCK FRD · Not return-to-architecture (B2-09 SoT stands) · Business Decisions needed before LOCK (see §3) but answers **not invented** in this sprint.

## 2. DoR checklist (evidence)

| Item | Result | Evidence |
|---|---|---|
| Business approved | **FAIL** | FRD Status Draft; explicit “belum DoR” |
| Governance approved | **PARTIAL** | B2-09 SoT = API-040; no Board LOCK of FRD-006 |
| Repository aligned | **PASS** | Register/B2-09 align API-040 ≠ API-390/513 |
| FRD complete | **FAIL** | Missing flows, definitions, drill-down FR, dual-SoT case namespace, validation rules |
| OpenAPI ready (normative) | **FAIL** | `x-status: draft`; “Do NOT implement”; permission name TBD |
| Dependencies understood | **PASS** | Documented; soft-deps clear |
| No unresolved blocker | **FAIL** | Permission TBD; case status namespace; drill-down; SEC-RAM revision; BO DoR sign-off |
| Traceability complete | **PARTIAL** | TRC-L-008 exists Planned; Decision link for FRD LOCK absent; TC-040 Planned |
| Architecture approved | **PASS** | B2-09 multi-lane KEEP + API-040 target |

## 3. Open Business Questions (repository-implied — NOT answered here)

| ID (working) | Question | Class |
|---|---|---|
| BQ-CAP007-01 | Which Case SoT feeds API-040 aggregates — Sprint `/v1/cases` statuses vs Aggregate CAP-008 statuses? | **OPEN** (blocks schema freeze) |
| BQ-CAP007-02 | Exact dashboard read permission name / SEC-RAM-001 revision for Sprint-03? | **OPEN** (draft OpenAPI TBD) |
| BQ-CAP007-03 | Is “drill-down ke case” in-scope FR for v0.1 or deferred to list API-005 only? | **OPEN** (overview claims; no FR row) |
| BQ-CAP007-04 | Are Manager/Executive cross-unit aggregates in v0.1 or Supervisor-unit-only? | **OPEN** (actors listed; AC only Supervisor) |
| BQ-CAP007-05 | Is FR-030 SLA column required for CAP-007 v1 or optional soft-dep? | **DEFERRED** (FRD §6: optional via FR-030) |
| Visit Queue / API-390 / API-513 as CAP-007 | — | **OUT OF SCOPE** (B2-09 LOCKED disposition) |

No BQ answers invented. No FRD sections invented.

## 4. OpenAPI readiness

**API-040 = NOT READY to become normative.**

## 5. Related

- FRD: `03 Functional Requirements/ECMP_FRD_Dashboard_Queue_v0.1.md`
- Draft: `07 API Catalog/openapi/drafts/dashboard-queues.v1.draft.yaml`
- Architecture: `deploy/evidence/B2-09_Queue_Architecture_Rationalization_20260801.md`

---

*End of GOV-B2-10-DOR-001.*
