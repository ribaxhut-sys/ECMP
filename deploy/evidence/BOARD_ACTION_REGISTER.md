# BOARD ACTION REGISTER — Mode A Batch-1

| Field | Value |
|---|---|
| Document ID | BOARD-AR-MA-B1-001 |
| Date | 2026-08-01 |
| SHA / Branch | `1608245` / `feature/cm-batch1-s2-persistence` |
| Rule | Status values below are repository-backed prep states only — not forged completions |
| Related | `NEXT_HUMAN_ACTIONS.md`, `MISSING_APPROVALS.md`, `BOARD_DECISION_MATRIX.md` |

| ID | Action | Owner | Due Date | Status | Dependencies |
|---|---|---|---|---|---|
| BA-01 | Schedule Board Meeting; circulate pre-read pack | PMO / Board chair | **PENDING HUMAN DECISION** | Open | `BOARD_DECISION_PACKAGE.md`, agenda |
| BA-02 | Vote B-1 DEC ID collision (A/B/C); record written choice | Architecture Board / PMO | 2026-08-01 | **Done — Option A** (`EXT-HD-RC-MA-B1-20260801`) | `DEC_ID_Collision_Register_20260801.md` |
| BA-03 | After BA-02: execute authorized renumber/citation updates only (no substance rewrite of Approved decisions) | PMO + Solution Architect (executor) | 2026-08-01 | Open — authorized by B-1 A; execution separate | BA-02 recorded choice |
| BA-04 | Vote B-2 tag path (merge→tag vs lab waiver→tag); record written choice | Architecture Board + Release Manager | 2026-08-01 | **Done — Option B** (`EXT-HD-RC-MA-B1-20260801`) | REL-TAG-001; `RC_GATE_REPORT.md` |
| BA-05 | Affirm Mode B remains CLOSED for this RC path | Board / SA / Security | **PENDING HUMAN DECISION** | Open — **PENDING HUMAN DECISION** | `Mode_B_Blocked_Pending_IdP_Contract_20260801.md` |
| BA-06 | Choose SemVer `vX.Y.Z-rc.N` for Mode A Batch-1 (or formal Board→RM delegation) | Release Manager / PMO | 2026-08-01 | **Done — v1.1.0-rc.1** (`EXT-HD-RC-MA-B1-20260801`) | BA-04 preferred first |
| BA-07 | Sign U-5 — Tech Lead (G0 exit) | Tech Lead | 2026-08-01 | **Done — PASS** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) | `U5_Signoff_Checklist_20260801.md` |
| BA-08 | Sign U-5 — Solution Architect (G0 exit) | Solution Architect | 2026-08-01 | **Done — PASS** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) | U5 checklist |
| BA-09 | Sign U-5 — Business Owner (FRD-002 DoR) | Business Owner | 2026-08-01 | **Done — PASS** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) | U5 checklist |
| BA-10 | Freeze clean commit of governance/release doc pack at authorized tip | Release Manager | 2026-08-01 | **Open — PREPARE** (tree dirty; freeze required before tag) | BA-02…BA-06 direction; REL-RC-001 clean-tree rule |
| BA-11 | Add CHANGELOG RC section + Batch-1 release notes stub for chosen SemVer | Release Manager | 2026-08-01 | **Done — CHANGELOG [1.1.0-rc.1]** | BA-06, BA-10 |
| BA-12 | Attest / re-run G2 pack at freeze SHA; disclose RTM executed-TC gap vs G2 103 | QA Lead (+ Tech Lead) | 2026-08-01 | **Done — COMPLETE** (`EXT-HD-RC-MA-B1-20260801`) | BA-10 |
| BA-13 | Complete REL-RC-001 assessment to PASS criteria; sign §5 Go/No-Go | Tech Lead · QA Lead · Release Manager | 2026-08-01 | **Done — Go** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) | BA-07…BA-12; Board B-1/B-2 |
| BA-14 | Create annotated RC tag on **authorized** ref only (never move tags) | Release Manager | 2026-08-01 | **Prepared — NOT CUT** (`v1.1.0-rc.1` on `1608245`) | BA-04 Option B, BA-06, BA-10, BA-13 Go |
| BA-15 | Re-run `RC_GATE_REPORT.md`; flip verdict only if evidence supports READY FOR RC | Release Manager / Governance | 2026-08-01 | **In progress** (this pass) | BA-14 sequence |
| BA-16 | Optional: Security delta note S-03/S-04 vs post-P5 (do not rewrite original sheet) | Security Reviewer | **PENDING HUMAN DECISION** | Open (P1) | `Security_Review_Signoff_20260801.md` |
| BA-17 | Optional: confirm ABSENT port of IMS-001 / SEC Baseline or defer in RC notes | Release Manager (+ Security) | **PENDING HUMAN DECISION** | Open (P1) | Gap on tip vs `main` @ `57dfae8` |

---

## Status legend

| Status | Meaning |
|---|---|
| Open | Identified; not done |
| Open — **PENDING HUMAN DECISION** | Requires human/Board; automation STOP |
| Blocked | Waiting on dependency |
| Done | Human/external decision recorded in SoT |

---

## Explicit non-actions (do not assign as automation)

- Fill signature cells  
- Invent Board vote results  
- Enable Mode B / invent OIDC  
- Claim READY FOR RC before BA-15 evidence  

---

*Register synchronized to external decisions `EXT-HD-RC-MA-B1-20260801` on 2026-08-01.*
