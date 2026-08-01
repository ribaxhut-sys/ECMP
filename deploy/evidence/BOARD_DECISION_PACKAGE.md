# BOARD DECISION PACKAGE — Mode A Batch-1

| Field | Value |
|---|---|
| Document ID | BOARD-PKG-MA-B1-001 |
| Date | 2026-08-01 |
| Prepared by | Release Governance Coordinator (lab) |
| Audience | Board · Release Manager · Tech Lead · Solution Architect · QA Lead · Business Owner |
| SoT tip | `16082454659d7f511e5296d0bd9531185766e6db` (`1608245`) |
| Branch | `feature/cm-batch1-s2-persistence` |
| Purpose | Prepare repository for **Board Meeting** — not RC cut, not Production |
| Approvals in this file | **None** |
| Fabrication | Forbidden — no invented Board / RM / Security / QA decisions |

---

## 1. Executive Summary

ECMP Mode A Batch-1 berada pada fase **Release Governance**. Engineering gate G2 Mode A **EXITED**; regression pack **PASS** (103 recorded). Phase 4 RAB = **GO WITH WAIVERS** (limited Phase 5 only). Mode B = **CLOSED**.

**RC status:** see `RC_GATE_REPORT.md` (re-gated this pass).  
External decisions recorded: B-1 Option A; B-2 Option B; SemVer `v1.1.0-rc.1`; U-5 COMPLETE; REL-RC-001 §5 Go (`EXT-HD-RC-MA-B1-20260801`). Remaining cut: freeze commit + annotated tag.

Paket ini **hanya** mempersiapkan Board Meeting. Tidak ada eksekusi renumber DEC, tidak ada tag RC, tidak ada perubahan arsitektur/API/DB/ADR/DEC body.

---

## 2. Current Repository Status

| Item | Status (repository evidence) |
|---|---|
| SHA / Branch | `1608245` / `feature/cm-batch1-s2-persistence` |
| Engineering (G2 Mode A) | COMPLETE / EXITED — `G2_Mini_Gate_Mode_A_20260801.md` |
| Regression | PASSED (103) — `REGRESSION_PACK_G2.md` + G2 evidence |
| Mode A Batch-1 scope | COMPLETE for lab engineering path; FR-030/040 **DEFER** |
| Release documentation pack | COMPLETE — `PACK_STATUS_20260801.md`, `RELEASE_MANIFEST.md` |
| Phase 4 RAB (limited P5) | GO WITH WAIVERS |
| Approval Matrix A-01…A-10 (lab) | Complete (lab / W-SOD-1) — not enterprise SoD |
| U-5 sign-off | **COMPLETE** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) |
| REL-RC-001 §5 | **COMPLETE — Go** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) |
| Annotated RC tag | **Prepared — NOT CUT** (`v1.1.0-rc.1`) |
| Mode B | CLOSED / BLOCKED |
| RC gate verdict | See `RC_GATE_REPORT.md` (re-gated; freeze+tag open) |

Working tree note (REL-RC-001): evidence/governance delta may remain uncommitted — freeze commit **required before tag** (Release Manager).

---

## 3. Open Decisions

### B-1 — DEC ID Collision

| Field | Value |
|---|---|
| Reference | `DEC_ID_Collision_Register_20260801.md` |
| Severity | P0 governance |
| Status | **APPROVED — Option A** (`EXT-HD-RC-MA-B1-20260801`) |
| Execution in this pack | Decision recorded; renumber = BA-03 separate |

Collisions (file path is disambiguator until Board chooses):

| ID | File A | File B |
|---|---|---|
| DEC-020 | Complaint Implementation SoT Namespace Remapping (Accepted) | Lab Auth Local Then SSO Target (Accepted ops) |
| DEC-021 | Organization Hierarchy Descendant Scope O-06 (Proposed) | G2 Mini-Gate Mode A (Accepted Mode A lab) |

| Option | Meaning |
|---|---|
| A | Keep O-06 as DEC-021; rename/renumber G2 → DEC-023 (+ update citations) |
| B | Keep G2 as DEC-021; renumber O-06 → next free ID (+ update OQ/ADR-018 citations) |
| C | Keep both; introduce explicit suffixes via new numbering policy |

**Prepared recommendation (not a Board vote):** Option A — aligns with collision register and SA recommendation in `NEXT_HUMAN_ACTIONS.md` (SA-2). Board must still vote.

### B-2 — Release Tag Strategy

| Field | Value |
|---|---|
| Policy | REL-TAG-001 (`16 Release Management/ECMP_Git_Tag_Convention_v0.1.md`) |
| Conflict | Tip is on **feature branch**; policy tags only default-branch commits (or requires waiver) |
| Status | **APPROVED — Option B** (`EXT-HD-RC-MA-B1-20260801`) |
| Choice in this pack | Lab waiver → tag on `feature/cm-batch1-s2-persistence` |

| Option | Path | Pros | Cons |
|---|---|---|---|
| **A** | Merge feature → `main` → create annotated RC tag | Compliant with REL-TAG-001; cleaner SoT for consumers | Merge risk; behind-14 / W-D07 discipline; may pull scope beyond lab tip intent |
| **B** | Temporary Lab Waiver → annotated RC tag on feature branch | Faster lab RC identity; no immediate merge | Requires explicit Board/RM waiver; policy exception; consumers must understand lab-only tag |

SemVer identity recorded: **`v1.1.0-rc.1`** (`EXT-HD-RC-MA-B1-20260801`).

### B-3 — Mode B (confirm closed)

| Field | Value |
|---|---|
| Required outcome for this RC path | Mode B remains **CLOSED** |
| Evidence | `Mode_B_Blocked_Pending_IdP_Contract_20260801.md` |
| Status | Affirmation expected; unlock = out of scope |

---

## 4. Open Risks

| ID | Risk | Severity | Notes |
|---|---|---|---|
| DEC-ID | Ambiguous DEC-020 / DEC-021 citations | Medium | B-1 Option A recorded; BA-03 renumber open |
| REL-TAG | Feature-tip tag vs REL-TAG-001 | Medium | B-2 Option B waiver recorded; tag not cut |
| W-SOD-1 | Single lab operator multi-role | High (governance) | Disclosed; not enterprise SoD |
| W-S03 | `ENVIRONMENT=production` + Mode A JWT | High (claim) | OPEN to 2026-09-30 / Mode B contract |
| W-D07 | behind-14 unforensicked | High | No bulk merge/rebase |
| U-5 / REL-RC-001 | Signed (`EXT-HD-RC-MA-B1-20260801`) | Closed (lab) | Synced |
| Dual-tree | `backend/` vs `implementation/backend` SIT confusion | Medium | SIT SoT memo binding |
| RTM-exec | Batch-1 RTM executed TC historically 0% | Medium | Do not equate to G2 103 |
| IMS-gap | IMS-001 / SEC Baseline absent on tip (on `main`) | Medium | ABSENT port = RM decision |
| Sec-drift | Security sheet vs post-P5 truth | Medium | Delta review optional; do not rewrite signed sheet |
| Dirty tree | Uncommitted governance artefacts | Medium | Freeze commit before tag |

---

## 5. Board Recommendations

| # | Recommendation | Type |
|---|---|---|
| 1 | Convene Board Meeting using `BOARD_MEETING_AGENDA.md` | Process |
| 2 | Vote **B-1** — **APPROVED Option A** | `EXT-HD-RC-MA-B1-20260801` |
| 3 | Vote **B-2** — **APPROVED Option B** | `EXT-HD-RC-MA-B1-20260801` |
| 4 | Affirm Mode B remains CLOSED for Mode A Batch-1 RC path | Scope control |
| 5 | After Board votes: hand off to Action Register owners (U-5, SemVer, REL-RC-001, freeze, tag) | Post-meeting |
| 6 | Do **not** claim READY FOR RC, Production Ready, or Enterprise Platform from this meeting alone | Claim control |

**Meeting readiness (this coordinator):** documentation package supports Board review of open decisions.  
**RC readiness:** human/Board P0 for listed external decisions closed; freeze + tag remain for cut — see `RC_GATE_REPORT.md`.

---

## Companion artefacts

| Doc | Path |
|---|---|
| Decision matrix | `BOARD_DECISION_MATRIX.md` |
| Agenda | `BOARD_MEETING_AGENDA.md` |
| Action register | `BOARD_ACTION_REGISTER.md` |
| RC final checklist (blank approvals) | `RC_FINAL_CHECKLIST.md` |
| One-page dashboard | `EXECUTIVE_STATUS.md` |
| Gate report | `RC_GATE_REPORT.md` |
| Collision register | `DEC_ID_Collision_Register_20260801.md` |
| Missing approvals | `MISSING_APPROVALS.md` |
| Next human actions | `NEXT_HUMAN_ACTIONS.md` |

---

*End of BOARD_DECISION_PACKAGE — target state: READY FOR BOARD MEETING (not READY FOR RC)*
