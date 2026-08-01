# B2-11 — CAP-007 Business Decision Closure

| Field | Value |
|---|---|
| Document ID | GOV-B2-11-BQ-001 |
| Decision ID | DEC-CAP007-BQ-001 |
| Sprint | B2-11 |
| Date | 2026-08-01 |
| Authority | ARB / Business Owner / Business Analyst / Repository Governance |
| Scope | Close B2-10 OPEN BQs for CAP-007 — **decision package only** |
| Non-goals | No Backend / Frontend / OpenAPI / BR / CAP-008 / Queue Service / API-390 / API-513 edits |
| Prerequisite | B2-10 CAP-007 NOT READY (DoR) |
| Verdict | **BUSINESS DECISION READY** |

## 1. Consolidated Business Decision Statement

**DEC-CAP007-BQ-001 (Proposed — repository-evidenced; apply to FRD/OpenAPI/SEC-RAM only after explicit approval):**

1. **Case SoT for API-040 / CAP-007 v0.1** = Sprint ECMF Case namespace (`/v1/cases`, DOM-ECMF-003 status set in draft OpenAPI). **Not** CAP-008 Aggregate Case statuses. **Not** API-513.
2. **Permission** for API-040 = existing code/catalog name **`dashboard:read`** (same family as CAPABILITY-013 / DEC-016). SEC-RAM-001 must add Planned Sprint-03 row **after approval** (document lag only).
3. **Drill-down v0.1** = read-only UX navigation to **existing** case retrieve/list contracts (API-002 / API-005). **No** new dashboard mutation API. **No** new OpenAPI operation invented for drill-down in v0.1.
4. **Actor scope v0.1** = **Supervisor unit-scoped** only (matches FRD-006 AC). Manager/Executive cross-unit aggregates = **Defer** to a later FRD revision.
5. **SLA columns (FR-030)** remain **Deferred** soft-dependency (FRD-006 §6 unchanged in meaning).

Visit Queue / API-390 / API-513 remain **OUT OF SCOPE** for CAP-007 (B2-09).

## 2. BQ dispositions

| BQ | Disposition | Recommendation |
|---|---|---|
| BQ-CAP007-01 | **CLOSED** | **Approve** Sprint ECMF Case SoT |
| BQ-CAP007-02 | **CLOSED** | **Approve** `dashboard:read` |
| BQ-CAP007-03 | **CLOSED** | **Approve** drill-down via API-002/005 only |
| BQ-CAP007-04 | **CLOSED** | **Approve** Supervisor-only v0.1; **Defer** Manager/Executive |
| BQ-CAP007-05 | **CLOSED** (was Deferred) | **Defer** FR-030 columns (confirm) |

## 3. Exit criteria (post-approval engineering prep)

- FRD-006 records DEC-CAP007-BQ-001 + remaining structural DoR gaps may still block LOCK
- OpenAPI draft permission text may cite `dashboard:read` (separate sprint — not this cut)
- This sprint does **not** claim CAP-007 READY FOR IMPLEMENTATION (B2-10 DoR structural gaps remain)

---

*End of GOV-B2-11-BQ-001.*
