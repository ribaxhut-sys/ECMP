# ECMP Test Case Catalog — Complaint Management Batch 1

| Field | Value |
|---|---|
| ID | TC-CAT-CM-B1-001 |
| Version | 1.0 |
| Owner | QA Lead |
| Reviewer | BA / Solution Architect |
| Approver | Architecture Board / CTO |
| Status | 🟡 Planned (authored; not executed) |
| Date | 2026-07-29 |
| FRD | FRD-CM-001 v1.1 LOCKED |
| RTM | RTM-CM-B1-001 LOCKED |
| Namespace | TC-CM-* (not Sprint TC-001…) |

## Purpose

Formal Planned Test Cases for Batch 1 (FR-001…FR-004). Mapped 1:1 from RTM Acceptance Criteria. **Do not** create Case in any positive path (CTO D-02).

## Summary

| FR | AC count | TC IDs | Status |
|---|---|---|---|
| FR-001 | 12 | TC-CM-FR001-01…12 | 🟡 Partial — 01,02,04,10,11,12 covered in `test_cm_batch1.py` (S1) |
| FR-002 | 9 | TC-CM-FR002-01…09 | 🟡 Partial — 01,02,03,04,05,07,08,09 covered (S1); 06 contract later |
| FR-003 | 8 | TC-CM-FR003-01…08 | 🕓 Planned |
| FR-004 | 9 | TC-CM-FR004-01…09 | 🕓 Planned |
| **Total** | **38** | | **~14 executed unit/API (S1)** |

---

## FR-001 — Complaint Registration

| TC | Title | AC | API | EVT | Priority |
|---|---|---|---|---|---|
| TC-CM-FR001-01 | Authorized create → REGISTERED, unique number, **no Case** | AC-CM-FR001-01 | API-500 | EVT-CM-001 | Must |
| TC-CM-FR001-02 | Stores CustomerId only (not Master SoR attributes) | AC-CM-FR001-02 | API-500 | EVT-CM-001 | Must |
| TC-CM-FR001-03 | Immutable audit + Timeline “Complaint Created” | AC-CM-FR001-03 | API-500 | EVT-CM-001 | Must |
| TC-CM-FR001-04 | Missing mandatory attributes → field validation reject | AC-CM-FR001-04 | API-500 | — | Must |
| TC-CM-FR001-05 | Unauthorized → reject + security audit | AC-CM-FR001-05 | API-500 | — | Must |
| TC-CM-FR001-06 | Duplicate override with/without justification | AC-CM-FR001-06 | API-500 / API-506 | EVT-CM-021 | Must |
| TC-CM-FR001-07 | Redirect transfers staged evidence (no discard) | AC-CM-FR001-07 | API-500 / API-508 | EVT-CM-003, EVT-CM-033 | Must |
| TC-CM-FR001-08 | Strict mode + Master Customer down → reject | AC-CM-FR001-08 | API-500 | — | Must |
| TC-CM-FR001-09 | Notification down → Complaint remains; outbox records failure | AC-CM-FR001-09 | API-500 | EVT-CM-005 | Must |
| TC-CM-FR001-10 | Repeated Request Id → no new Aggregate | AC-CM-FR001-10 | API-500 | EVT-CM-002 | Must |
| TC-CM-FR001-11 | Repeated Channel Message Id → no new Aggregate | AC-CM-FR001-11 | API-500 | EVT-CM-002 | Must |
| TC-CM-FR001-12 | Confirm presents Batch 1 Customer 360 minimum | AC-CM-FR001-12 | API-504 | — | Must |

**Shared asserts (all FR-001 positives):** `caseCreated == false` OR no Case resource created.

---

## FR-002 — Customer Search

| TC | Title | AC | API | EVT | Priority |
|---|---|---|---|---|---|
| TC-CM-FR002-01 | Unique Customer Number → lock CustomerId + 360 minimum | AC-CM-FR002-01 | API-502 / API-504 | EVT-CM-010 | Must |
| TC-CM-FR002-02 | Multiple matches → no lock until selection | AC-CM-FR002-02 | API-502 | — | Must |
| TC-CM-FR002-03 | No match → normal create rejected (unless UNVERIFIED policy) | AC-CM-FR002-03 | API-502 / API-500 | EVT-CM-011 | Must |
| TC-CM-FR002-04 | Master Customer write-back rejected | AC-CM-FR002-04 | — | — | Must |
| TC-CM-FR002-05 | Strict unavailable → degraded; no invented customer | AC-CM-FR002-05 | API-502 | EVT-CM-011 | Must |
| TC-CM-FR002-06 | Frontend calls Backend only (integration/contract) | AC-CM-FR002-06 | API-502 | — | Must |
| TC-CM-FR002-07 | Two key types in one request → reject | AC-CM-FR002-07 | API-502 | — | Must |
| TC-CM-FR002-08 | Enumeration threshold → delay/block + audit + alert | AC-CM-FR002-08 | API-502 | EVT-CM-011 | Must |
| TC-CM-FR002-09 | Profile `asOf` freshness shown | AC-CM-FR002-09 | API-504 | — | Must |

---

## FR-003 — Duplicate Detection

| TC | Title | AC | API | EVT | Priority |
|---|---|---|---|---|---|
| TC-CM-FR003-01 | Open candidate in window → warning | AC-CM-FR003-01 | API-505 | EVT-CM-020 | Must |
| TC-CM-FR003-02 | Open/link existing → no new Aggregate, **no Case** | AC-CM-FR003-02 | API-506 | EVT-CM-022 / 023 | Must |
| TC-CM-FR003-03 | Continue without required justification → reject | AC-CM-FR003-03 | API-506 | — | Must |
| TC-CM-FR003-04 | Override with justification → create + linkage + audit | AC-CM-FR003-04 | API-506 / API-500 | EVT-CM-021 | Must |
| TC-CM-FR003-05 | Hard-block category → reject create | AC-CM-FR003-05 | API-505 / API-500 | — | Must |
| TC-CM-FR003-06 | Index unavailable → degraded + later-review work item | AC-CM-FR003-06 | API-505 | EVT-CM-025 / 026 | Must |
| TC-CM-FR003-07 | Out-of-scope candidates → uniform empty | AC-CM-FR003-07 | API-505 | — | Must |
| TC-CM-FR003-08 | Any Batch 1 duplicate flow → **no Case created** | AC-CM-FR003-08 | API-505 / API-506 | EVT-CM-024 | Must |

---

## FR-004 — Attachment Upload

| TC | Title | AC | API | EVT | Priority |
|---|---|---|---|---|---|
| TC-CM-FR004-01 | Allowlisted upload → ACTIVE + hash + history/audit | AC-CM-FR004-01 | API-507 | EVT-CM-030 | Must |
| TC-CM-FR004-02 | Illegal type/size → reject; no ACTIVE | AC-CM-FR004-02 | API-507 | — | Must |
| TC-CM-FR004-03 | Malware failure → reject + security audit | AC-CM-FR004-03 | API-507 | — | Must |
| TC-CM-FR004-04 | Physical delete rejected; void-with-reason only | AC-CM-FR004-04 | API-512 | EVT-CM-032 | Must |
| TC-CM-FR004-05 | Supersede → prior SUPERSEDED and retrievable | AC-CM-FR004-05 | API-507 | EVT-CM-031 | Must |
| TC-CM-FR004-06 | Later escalation visibility (No Information Lost) | AC-CM-FR004-06 | API-509 | — | Must |
| TC-CM-FR004-07 | Frontend uses Backend attachment APIs only | AC-CM-FR004-07 | API-507…512 | — | Must |
| TC-CM-FR004-08 | Duplicate redirect transfer → survivor + audit; no discard | AC-CM-FR004-08 | API-508 | EVT-CM-033 | Must |
| TC-CM-FR004-09 | CaseId not belonging to Complaint → reject | AC-CM-FR004-09 | API-507 | — | Must |

---

## Authoring notes (for pytest later)

- Prefix paths under `/api/v1/cm/...` for Aggregate Batch 1 (see OpenAPI).
- Synthetic customers only; never real PII.
- Security suite must include enumeration, idempotency replay, authz deny.
- Exit Batch 1 only when executed coverage of Must TCs = 100%.

## Document History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-07-29 | Initial 38 Planned TCs from RTM-CM-B1-001 (S0) |

---

*End of TC-CAT-CM-B1-001.*
