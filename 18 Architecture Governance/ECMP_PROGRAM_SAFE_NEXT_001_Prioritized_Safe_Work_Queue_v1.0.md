# PROGRAM-SAFE-NEXT-001 — Prioritized Safe Work Queue (Post BOARD-006 / Profiles Draft)

| Field | Value |
|---|---|
| Document ID | GOV-SAFE-NEXT-001 |
| Program | PROGRAM-SAFE-NEXT-001 |
| Version | 1.0 |
| Date | 2026-07-31 |
| Prepared by | Architecture Board Secretary / Documentation Administrator |
| Authority | Project Owner instruction — lanjutkan semua yang aman; tentukan prioritas |
| Status | 🟢 **Recorded** |
| Mode B | **CLOSED** (C-B6-1 / C-7) — this queue does not unlock |

---

## 1. Priority order (binding for this queue)

| Prio | Workstream | Why first | Artifact(s) |
|---:|---|---|---|
| **P1** | Org-gap **delivery plan** | Hard Mode B unlock prerequisite (C-B6-3 / K-7); plans gap without coding Mode B | `ECMP_PROGRAM_ORG_GAP_DELIVERY_PLAN_v0.1.md` |
| **P2** | Enterprise Platform **bilateral review pack** | Unblocks provisional wire names on Draft profiles; bilateral (C-3) | `ECMP_PROGRAM_EP_BILATERAL_PROFILE_REVIEW_PACK_v0.1.md` |
| **P3** | **O-06 / O-07** policy drafts | Prevent unsafe AuthZ expansion / orphan handling before delivery | `DEC-021` / `DEC-022` (**Proposed**) |
| **P4** | **Mode A** next-work priority note | Delivery continues under AUTHORIZED WITH CONDITIONS without enterprise unlock | `ECMP_PROGRAM_MODE_A_NEXT_WORK_PRIORITY_v0.1.md` |
| **P5** | BOARD-008 EA draft pack + DTM-001 | Board intake only; HOST Gate; **not** coding | `ECMP_PROGRAM_BOARD_008_EA_TARGET_PLATFORM_Draft_Pack_v0.1.md` · DTM-001 · `04 …/board-drafts/` |

**Explicitly deferred (not safe as “done” without external/Board action):**

| Item | Why deferred |
|---|---|
| Mode B unlock / Identity Adapter coding / OpenAPI enterprise `securitySchemes` | C-B6-1 CLOSED |
| EA-TARGET Sprint 2–6 / EA-PLATFORM v0.5+ coding | BOARD-008: drafts ≠ tickets; needs G-HOST ∩ C-7 |
| Schema migration for organizations/departments | Needs delivery authorization after plan; still ≠ Mode B unlock |
| EP wet-ink countersign | Requires Enterprise Platform party |
| ADR-007 / ADR-012 Board disposition (D-08) | Separate Board session — do not invent |
| Batch-2 / enterprise customer | CLOSED |

---

## 2. Anti-skip reminder

Governance path remains: profiles Draft → EP bilateral → org-gap **delivery** (schema when authorized) → evidence bar → **then** explicit Board unlock of Mode B. Do not treat P1–P5 as Mode B authorization. EA-TARGET/PLATFORM drafts require **HOST Gate** (BOARD-008 §4) before contract-dependent coding.

---

## 3. Execution status (this delivery)

| Prio | Status 2026-07-31 |
|---|---|
| P1 | **DONE (Draft plan published)** |
| P2 | **DONE (Review pack published — awaiting EP)** |
| P3 | **DONE (DEC-021 / DEC-022 Proposed)** |
| P4 | **DONE (Mode A priority note published)** |
| P5 | **DONE (BOARD-008 draft pack + DTM-001 published — Board REVIEW pending; HOST items Open)** |

---

*End of GOV-SAFE-NEXT-001.*
