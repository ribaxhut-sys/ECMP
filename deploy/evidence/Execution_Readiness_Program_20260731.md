# ECMP Execution Readiness Program
Version: 1.0  
Date: 2026-07-31  
Role: ECMP Release Manager  
Class: Project management plan only  

| Constraint | Value |
|---|---|
| Governance | Phases 0–4.5 CLOSED |
| Phase 5 Runbook | PRE-APPROVED — not for execution |
| RAB status | **NO-GO** |
| This document | Closes blockers before **next** RAB |
| Forbidden here | Git ops · implementation · deploy · merge · rebase · cherry-pick |

Immutable inputs: Reconciliation · Phase 0–4.5 · Phase 5 Runbook (PRE-APPROVED) · preparation drafts under `deploy/evidence/`.

---

# Executive Summary

Program ini mengubah daftar FAIL RAB (R1–R10) dan precondition Phase 2/3 menjadi **delapan work package** yang bisa dieksekusi tim proyek (review, tulis, tanda tangan) — **bukan** coding atau Git promote.

Hasil akhir yang diharapkan: semua Acceptance Criteria WP-01…WP-08 terpenuhi → Evidence Pack lengkap → **ajukan ulang Phase 4 RAB**. Hanya keputusan **GO** / **GO WITH WAIVERS** yang membuka eksekusi Phase 5 Runbook.

Draft artefak sudah ada di `deploy/evidence/` (split plans, overlap note, sign-off templates, base SHA draft). Program ini = **menyelesaikan & menandatangani**, bukan menulis ulang governance.

---

# Roadmap

| Wave | Fokus | WP | Keluaran |
|---|---|---|---|
| W0 | Kickoff & owner lock | — | RACI terisi; kalender review |
| W1 | Base + splits + compatibility | WP-01, WP-02, WP-03 | Base SHA signed; splits approved; content review EXISTS paths |
| W2 | Security + Deploy + Rollback | WP-04, WP-05, WP-06 | Sign-off PASS + rollback approved |
| W3 | Evidence + residual + PO | WP-07 (+ A-04/A-09 via WP-07/08) | Pack complete; risks accepted; PO scope |
| W4 | Pre-RAB dry-run | WP-08 | Readiness memo → re-RAB session |

Urutan ketat: **WP-01 ∥ early WP-02** → **WP-03 bergantung WP-02 path set** → **WP-04/05 setelah scope pick jelas** → **WP-06 paralel akhir W2** → **WP-07 aggregasi** → **WP-08**.

---

# Dependency Diagram

```text
                    ┌─────────┐
                    │  W0 RACI │
                    └────┬────┘
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
       ┌───────┐    ┌───────┐    ┌───────┐
       │ WP-01 │    │ WP-02 │───▶│ WP-03 │
       │ Base  │    │ Split │    │ Compat│
       └───┬───┘    └───┬───┘    └───┬───┘
           │            │            │
           └──────┬─────┴─────┬──────┘
                  ▼           ▼
            ┌────────┐  ┌────────┐
            │ WP-04  │  │ WP-05  │
            │ Sec    │  │ Deploy │
            └───┬────┘  └───┬────┘
                └─────┬─────┘
                      ▼
                 ┌────────┐
                 │ WP-06  │
                 │Rollback│
                 └───┬────┘
                     ▼
                 ┌────────┐
                 │ WP-07  │  ← juga A-04 residual, A-08 pack, A-09 PO
                 │Evidence│
                 └───┬────┘
                     ▼
                 ┌────────┐
                 │ WP-08  │
                 │Pre-RAB │
                 └───┬────┘
                     ▼
              Next Phase 4 RAB
```

---

# Work Package Table (summary)

| WP | Title | Owner (primary) | Depends on | Effort (est.) | Blocks RAB |
|---|---|---|---|---|---|
| WP-01 | Release Base Approval | Tech Lead + Release Manager | W0 | 0.5–1 d | R7, A-01, G2 |
| WP-02 | Mixed Commit Split Plans | Tech Lead (+ BE/FE) | W0; Phase 1 matrix | 1–2 d | R8, A-02, G4 |
| WP-03 | Batch-1 Compatibility Review | Tech Lead | WP-02; overlap note | 1–2 d | R3 partial, A-03, G5 |
| WP-04 | Security Review | Security Reviewer | WP-02 (scope); WP-03 flags | 1–2 d | R4, A-05, G7 |
| WP-05 | Deployment Review | Deploy Lead | WP-02; WP-01 | 1–2 d | R5, A-06, G8 |
| WP-06 | Rollback Pack | Deploy Lead + RM | WP-01; WP-02 | 0.5–1 d | R6, A-07, G9 |
| WP-07 | Evidence Pack | Release Manager | WP-01…06 + residual + PO | 0.5–1 d | R3, R9, R10, A-04, A-08, A-09, G10 |
| WP-08 | RAB Readiness Review | Release Manager | WP-07 | 0.5 d | R1, R2, A-10 prep |

**Critical path (nominal ~4–6 working days calendar if sequential reviews):**  
WP-01 → WP-02 → WP-03 → WP-04 → WP-07 → WP-08  
(with WP-05 ∥ WP-04 after WP-02; WP-06 ∥ late W2).

---

# Work Packages

## WP-01 — Release Base Approval

| Field | Content |
|---|---|
| **Objective** | Kunci base release branch = tip SoT Batch-1 yang disetujui (bukan VPS `main`). |
| **Inputs** | Reconciliation (SoT = `origin/feature/cm-batch1-s2-persistence`); draft `Base_SHA_Lock_DRAFT_20260731.md` (proposed `2bf779d`); Phase 2 G2 FAIL. |
| **Deliverables** | Base SHA Lock **signed** (Tech Lead + Release Manager); SHA full + short + date freeze. |
| **Owner** | Tech Lead (confirm tip) · Release Manager (record & publish). |
| **Dependencies** | W0 owners assigned. |
| **Acceptance Criteria** | Written Approve on Base SHA Lock; statement “not VPS `main@41a0f48`”; successor rule if tip moves before cut. |
| **Evidence Produced** | Updated/signed `Base_SHA_Lock_*.md` in `deploy/evidence/`. |
| **Estimated Effort** | 0.5–1 person-day. |
| **Risk if delayed** | R7/G2 remain FAIL; seluruh Phase 5 blocked; tip SoT bisa bergeser tanpa baseline. |

---

## WP-02 — Mixed Commit Split Plans

| Field | Content |
|---|---|
| **Objective** | Finalize & approve file-level SPLIT untuk empat Mixed + KEEP `ad4a373`. |
| **Inputs** | Phase 1 Decision Matrix; Phase 0 §3.1 paths; draft `Split_Plans_VPS_Mixed_20260731.md`. |
| **Deliverables** | Split Plans **approved** (C-01…C-05); unit list final; pick sequence confirmed. |
| **Owner** | Tech Lead · Backend Lead (C-02, C-04) · Frontend Lead (C-03). |
| **Dependencies** | W0; no dependency on WP-01 for drafting, **approval publish** after WP-01 preferred so base context clear. |
| **Acceptance Criteria** | Every Mixed has Unit A/B path tables; no path in two units; KEEP only `ad4a373`; Tech Lead (+ BE/FE as scoped) signed Approve. |
| **Evidence Produced** | Signed `Split_Plans_VPS_Mixed_*.md`. |
| **Estimated Effort** | 1–2 person-days (review meeting + edits). |
| **Risk if delayed** | R8/G4 FAIL; cherry-pick Mixed bulk risk; WP-03/04/05 scope unclear. |

---

## WP-03 — Batch-1 Compatibility Review

| Field | Content |
|---|---|
| **Objective** | Tutup celah overlap VPS ↔ Batch-1: dari path existence → **content review** pada path EXISTS + keputusan promote/defer per unit. |
| **Inputs** | `Path_Overlap_VPS_vs_Batch1_20260731.md` (13 EXISTS / 15 ABSENT); approved split units (WP-02); SoT tip = locked SHA (WP-01). |
| **Deliverables** | Compatibility memo: per EXISTS path → OK to pick / needs manual merge note / defer; signed A-03. |
| **Owner** | Tech Lead (overall) · BE/FE for owned paths. |
| **Dependencies** | WP-01 (SHA), WP-02 (units). |
| **Acceptance Criteria** | All 13 EXISTS paths dispositioned; no silent “no conflict” claim if content differs; Tech Lead signs Approval Matrix A-03. |
| **Evidence Produced** | `Compat_Review_Batch1_<date>.md` (+ optional annotated overlap file). |
| **Estimated Effort** | 1–2 person-days. |
| **Risk if delayed** | R3/G5/A-03 open; re-RAB cannot PASS residual RR-3. |

**Note:** Review = read/compare & write disposition. **Bukan** cherry-pick atau edit product code in this program.

---

## WP-04 — Security Review

| Field | Content |
|---|---|
| **Objective** | Complete S-01…S-09 against promotion candidates; written PASS/FAIL. |
| **Inputs** | Security template; Phase 0 §7 flags; split scope (WP-02); High items on `96f52eb` (env/JWT/docs exposure); rate-limit/XFF; IAM/Users UI. |
| **Deliverables** | Security Review Sign-off **PASS** (or FAIL with blocking findings list). |
| **Owner** | Security Reviewer · consult Backend/Frontend Leads. |
| **Dependencies** | WP-02 (what is in scope); WP-03 findings that affect auth/IAM surfaces. |
| **Acceptance Criteria** | Every S-01…S-09 filled; overall PASS signed; FAIL items either fixed-in-plan (out of this WP’s coding) or explicitly deferred with waiver path for later RAB — **no silent skip**. |
| **Evidence Produced** | Signed `Security_Review_Signoff_*.md`. |
| **Estimated Effort** | 1–2 person-days. |
| **Risk if delayed** | R4/G7 FAIL; High `96f52eb` / auth risks unaccepted. |

---

## WP-05 — Deployment Review

| Field | Content |
|---|---|
| **Objective** | Complete D-01…D-08 for compose/Caddy/backup/seed/runbook; written PASS. |
| **Inputs** | Deployment template; split infra units; Phase 1 High/Medium deploy flags; stance on `behind 14` (feeds A-04). |
| **Deliverables** | Deployment Review Sign-off **PASS**; note on D-07 divergence. |
| **Owner** | Deploy Lead · Tech Lead on D-07. |
| **Dependencies** | WP-01, WP-02. |
| **Acceptance Criteria** | D-01…D-08 filled; PASS signed; UFW out-of-git explicitly N/A for pick (D-06). |
| **Evidence Produced** | Signed `Deployment_Review_Signoff_*.md`. |
| **Estimated Effort** | 1–2 person-days. |
| **Risk if delayed** | R5/G8 FAIL; edge/compose promotion unsafe. |

---

## WP-06 — Rollback Pack

| Field | Content |
|---|---|
| **Objective** | Approve release-level rollback (not only Caddy lab). |
| **Inputs** | `Rollback_Pack_DRAFT_20260731.md`; Phase 5 Runbook §5 (reference only); pick sequence from WP-02. |
| **Deliverables** | Rollback Pack **approved** (R-01…R-06). |
| **Owner** | Deploy Lead + Release Manager. |
| **Dependencies** | WP-01 (base), WP-02 (reverse-order revert list). |
| **Acceptance Criteria** | Abort criteria clear; reverse revert order listed; no VPS `main` rewrite; seed backup rule if seed in scope; both owners signed. |
| **Evidence Produced** | Signed `Rollback_Pack_*.md`. |
| **Estimated Effort** | 0.5–1 person-day. |
| **Risk if delayed** | R6/G9 FAIL; cannot authorize cut safely. |

---

## WP-07 — Evidence Pack

| Field | Content |
|---|---|
| **Objective** | Aggregate & close evidence completeness + residual risk acceptance + Product Owner scope. |
| **Inputs** | All signed outputs WP-01…06; Phase 0–4.5 archives; `Residual_Risk_Acceptance_TEMPLATE_*`; Approval Matrix; Phase 3 E-01…E-06. |
| **Deliverables** | (1) Evidence pack index updated “COMPLETE for re-RAB”; (2) Residual risks **accepted in writing** (min RR-2, RR-3); (3) Product Owner A-09 signed; (4) Approval Matrix A-01…A-09 filled. |
| **Owner** | Release Manager · Governance Board (RR-2) · Product Owner (A-09) · Tech Lead (RR-3). |
| **Dependencies** | WP-01…WP-06 complete (PASS). |
| **Acceptance Criteria** | Checklist: Phase 0–4.5 present; Base/Split/Compat/Sec/Deploy/Rollback signed; Residual sheet signed; PO signed; A-01…A-09 = Go; **A-10 left for WP-08 / RAB**. |
| **Evidence Produced** | Updated `README_Release_Preparation_Pack_*.md`; signed residual + Approval Matrix; optional zip/index hash. |
| **Estimated Effort** | 0.5–1 person-day (+ meeting time for Board/PO). |
| **Risk if delayed** | R3/R9/R10/G10 FAIL; re-RAB premature. |

---

## WP-08 — RAB Readiness Review

| Field | Content |
|---|---|
| **Objective** | Dry-run DoR R1–R10; package re-RAB agenda; recommend GO / NO-GO / GO WITH WAIVERS **as recommendation only** (Board decides). |
| **Inputs** | Complete WP-07 pack; Phase 4 prior NO-GO; Phase 5 Runbook PRE-APPROVED. |
| **Deliverables** | `RAB_Readiness_Memo_<date>.md`: matrix R1–R10 proposed status; open waivers if any; meeting invite materials. |
| **Owner** | Release Manager (chair prep) · attendees per Approval Matrix. |
| **Dependencies** | WP-07. |
| **Acceptance Criteria** | Every R1–R10 has evidence pointer; no “PASS” claimed without signed artifact; A-10 **not** pre-signed as execution Go — A-10 / RAB GO is outcome of the **next RAB meeting**. |
| **Evidence Produced** | Readiness memo + agenda + evidence index link. |
| **Estimated Effort** | 0.5 person-day prep (+ meeting). |
| **Risk if delayed** | Team idles in NO-GO; Phase 5 remains frozen. |

---

# Milestones

| ID | Milestone | Definition of Done |
|---|---|---|
| M1 | Base locked | WP-01 AC met |
| M2 | Splits approved | WP-02 AC met |
| M3 | Compat closed | WP-03 AC met |
| M4 | Sec+Deploy PASS | WP-04 & WP-05 PASS |
| M5 | Rollback ready | WP-06 approved |
| M6 | Pack complete | WP-07 AC met (A-01…A-09) |
| M7 | Re-RAB ready | WP-08 memo issued |
| M8 | RAB decision | Next Phase 4 session records GO / NO-GO / GO WITH WAIVERS |

M8 is **outside** this program’s authority to grant — program only reaches M7.

---

# Critical Path

**Nominal sequence (blocking):**

1. WP-01 (base)  
2. WP-02 (splits)  
3. WP-03 (compat content)  
4. WP-04 (security) — longest review risk on critical path  
5. WP-07 (pack + residual + PO)  
6. WP-08 (readiness memo)

**Parallel off-path (must finish before WP-07):** WP-05, WP-06.

**Slack risk:** Security findings on `96f52eb` High items can extend WP-04 and slip M4→M7.

---

# Completion Criteria (program)

Program **COMPLETE** when:

1. WP-01…WP-08 Acceptance Criteria all met.  
2. Approval Matrix A-01…A-09 = Go (signed).  
3. Evidence pack indexed as ready for re-RAB.  
4. Readiness memo issued.  
5. **Explicitly still true:** Phase 5 Runbook **not executed**; no branch/cherry-pick/merge/deploy performed under this program.  
6. Next action handed to **Phase 4 RAB re-session** (M8).

Program **FAILED / STALLED** if any WP owner returns Reject/FAIL without remediation plan dated before re-RAB.

---

# RACI (executable)

| Activity | RM | Tech Lead | BE Lead | FE Lead | Sec | Deploy | PO | Gov Board |
|---|---|---|---|---|---|---|---|---|
| WP-01 Base | A/R | R | C | | | C | I | I |
| WP-02 Splits | A | R | R | R | C | C | I | I |
| WP-03 Compat | A | R | R | R | C | | I | I |
| WP-04 Security | A | C | C | C | R | C | I | I |
| WP-05 Deploy | A | C | C | | C | R | I | I |
| WP-06 Rollback | R | C | | | C | R | I | I |
| WP-07 Evidence | R | C | | | C | C | R (A-09) | R (RR-2) |
| WP-08 Pre-RAB | R | C | C | C | C | C | C | A (meeting) |

R=Responsible A=Accountable C=Consulted I=Informed · RM=Release Manager.

---

# Formal Close of this Plan

This is the **implementation work program** (project management) to exit RAB **NO-GO**.  
It does not authorize Phase 5 execution.  
Next authorized technical action after M7: **re-convene Phase 4 RAB** with the evidence pack.

—*End of Execution Readiness Program v1.0*
