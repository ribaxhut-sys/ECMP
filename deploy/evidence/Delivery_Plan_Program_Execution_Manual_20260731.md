# ECMP Delivery Plan
## Program Execution Manual
Version: 1.0  
Date: 2026-07-31  
Role: ECMP Program Manager  

| Field | Value |
|---|---|
| Governance | CLOSED (Phase 0–4.5) |
| Git / Phase 5 execution | **NOT AUTHORIZED** (RAB = NO-GO) |
| Parent plan | `Execution_Readiness_Program_20260731.md` — approved |
| This document | Operational delivery manual for WP-01…WP-08 |
| Forbidden | Git · implementation · deployment · merge · rebase · cherry-pick · governance redesign |

---

# Executive Summary

Manual ini mengubah Execution Readiness Program menjadi **cara kerja harian/mingguan** tim: status WP, syarat mulai/selesai, DoD, RACI, risiko, isu, keputusan, dan template laporan.

**Sasaran program:** menandatangani semua artefak blocking agar sidang ulang Phase 4 RAB bisa digelar.  
**Bukan sasaran:** membuat release branch, cherry-pick, merge, atau deploy.

**Status awal (2026-07-31):** draft evidence pack ada; **0/8 WP Done**; semua sign-off **UNSIGNED**; RAB tetap **NO-GO**.

---

# Delivery Timeline

| Day (nominal) | Focus | WP | Exit |
|---|---|---|---|
| D0 | Kickoff: nama owner, kalender, channel status | W0 | RACI names filled |
| D1 | Base SHA + start splits | WP-01, WP-02 | M1 in progress / M1 done |
| D2 | Finish splits; start compat | WP-02 → WP-03 | M2 done |
| D3 | Compat dispositions | WP-03 | M3 done |
| D4–D5 | Security + Deploy (+ Rollback draft sign) | WP-04, WP-05, WP-06 | M4, M5 |
| D6 | Evidence pack + residual + PO | WP-07 | M6 |
| D7 | Pre-RAB memo + schedule session | WP-08 | M7 → handoff re-RAB |

Calendar stretch if reviewers part-time: **+3–5 days**. Critical path still WP-01→02→03→04→07→08.

---

# Roadmap

```text
W0 Kickoff ──► W1 Base/Split/Compat ──► W2 Sec/Deploy/Rollback ──► W3 Evidence ──► W4 Pre-RAB ──► [Re-RAB]
     │              WP-01 WP-02 WP-03           WP-04 WP-05 WP-06         WP-07           WP-08        M8*
```

\*M8 = RAB decision — **outside** this delivery program’s authority.

---

# 1. Program Overview

| Item | Description |
|---|---|
| Program name | ECMP Execution Readiness Delivery |
| Goal | Satisfy RAB R1–R10 blockers via signed reviews |
| In scope | WP-01…WP-08: approve base, splits, compat, sec, deploy, rollback, evidence, pre-RAB |
| Out of scope | Phase 5 Git execution; feature coding; architecture change; production Aggregate cutover |
| Success | M7 complete → re-RAB scheduled with complete pack |
| Failure mode | Any WP Reject/FAIL without dated remediation before re-RAB |

---

# 2. Work Breakdown Structure

```text
ECMP Execution Readiness Delivery
├── W0 Program Setup
│   ├── W0.1 Assign named owners (RACI)
│   ├── W0.2 Status cadence (daily/weekly)
│   └── W0.3 Evidence folder conventions
├── W1 Foundation Approvals
│   ├── WP-01 Release Base Approval
│   ├── WP-02 Mixed Commit Split Plans
│   └── WP-03 Batch-1 Compatibility Review
├── W2 Control Reviews
│   ├── WP-04 Security Review
│   ├── WP-05 Deployment Review
│   └── WP-06 Rollback Pack
├── W3 Pack Closure
│   └── WP-07 Evidence Pack (+ residual + PO)
└── W4 Gate Prep
    └── WP-08 RAB Readiness Review
```

---

# 3. Milestone Plan

| ID | Milestone | Target (nominal) | Definition of Done |
|---|---|---|---|
| M0 | Kickoff complete | D0 | Named owners in RACI |
| M1 | Base locked | D1 | WP-01 Done |
| M2 | Splits approved | D2 | WP-02 Done |
| M3 | Compat closed | D3 | WP-03 Done |
| M4 | Sec+Deploy PASS | D5 | WP-04 & WP-05 Done |
| M5 | Rollback ready | D5 | WP-06 Done |
| M6 | Pack complete | D6 | WP-07 Done (A-01…A-09 Go) |
| M7 | Re-RAB ready | D7 | WP-08 Done; session booked |
| M8 | RAB decision | TBD | GO / NO-GO / GO WITH WAIVERS — **Board** |

---

# Critical Path

1. **WP-01** Base SHA  
2. **WP-02** Split plans  
3. **WP-03** Compat (13 EXISTS paths)  
4. **WP-04** Security (highest slip risk — High flags `96f52eb`)  
5. **WP-07** Evidence + residual + PO  
6. **WP-08** Pre-RAB memo  

**Parallel (must finish before WP-07):** WP-05, WP-06.

---

# 4. Dependency Matrix

| WP | Depends on | Blocks |
|---|---|---|
| WP-01 | W0 | WP-03 (SHA), WP-05, WP-06, WP-07 |
| WP-02 | W0 | WP-03, WP-04, WP-05, WP-06, WP-07 |
| WP-03 | WP-01, WP-02 | WP-04 (auth/IAM flags), WP-07 |
| WP-04 | WP-02, WP-03 | WP-07 |
| WP-05 | WP-01, WP-02 | WP-07 |
| WP-06 | WP-01, WP-02 | WP-07 |
| WP-07 | WP-01…WP-06 | WP-08 |
| WP-08 | WP-07 | Re-RAB (M8) |

| From \ To | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 |
|---|---|---|---|---|---|---|---|---|
| 01 | — | | X | | X | X | X | |
| 02 | | — | X | X | X | X | X | |
| 03 | | | — | X | | | X | |
| 04 | | | | — | | | X | |
| 05 | | | | | — | | X | |
| 06 | | | | | | — | X | |
| 07 | | | | | | | — | X |
| 08 | | | | | | | | — |

X = hard dependency.

---

# 5. Responsibility Matrix (RACI)

| WP / Activity | Program Mgr | Release Mgr | Tech Lead | BE Lead | FE Lead | Sec Reviewer | Deploy Lead | Product Owner | Gov Board |
|---|---|---|---|---|---|---|---|---|---|
| W0 Kickoff | A/R | R | C | I | I | I | I | I | I |
| WP-01 Base | A | R | R | C | | | C | I | I |
| WP-02 Splits | A | C | R | R | R | C | C | I | I |
| WP-03 Compat | A | C | R | R | R | C | | I | I |
| WP-04 Security | A | C | C | C | C | R | C | I | I |
| WP-05 Deploy | A | C | C | C | | C | R | I | I |
| WP-06 Rollback | A | R | C | | | C | R | I | I |
| WP-07 Evidence | A | R | C | | | C | C | R (A-09) | R (RR-2) |
| WP-08 Pre-RAB | A | R | C | C | C | C | C | C | C* |
| Weekly status | R | C | C | C | C | C | C | I | I |

\*Board chairs/decides at M8; consulted at WP-08 prep.  
R=Responsible A=Accountable C=Consulted I=Informed.

---

# RACI (named — fill at W0)

| Role | Person (name) | Backup |
|---|---|---|
| Program Manager | _TBD_ | |
| Release Manager | _TBD_ | |
| Tech Lead | _TBD_ | |
| Backend Lead | _TBD_ | |
| Frontend Lead | _TBD_ | |
| Security Reviewer | _TBD_ | |
| Deploy Lead | _TBD_ | |
| Product Owner | _TBD_ | |
| Governance Board chair | _TBD_ | |

---

# 6. Risk Tracking Matrix / Risk Dashboard

| ID | Risk | Prob | Impact | Score | Owner | Mitigation | Status |
|---|---|---|---|---|---|---|---|
| RK-01 | Reviewer names not assigned (W0 slip) | H | H | Crit | Program Mgr | Fill RACI Day 0 | Open |
| RK-02 | Base tip moves before lock | M | H | High | Tech Lead | Freeze SHA in WP-01; re-verify at WP-08 | Open |
| RK-03 | Split disagreement BE/FE | M | H | High | Tech Lead | Decision workshop ≤2h; escalate PO if scope | Open |
| RK-04 | EXISTS path content conflicts hard | H | H | Crit | Tech Lead | Disposition defer unit; do not invent redesign | Open |
| RK-05 | Security FAIL on `96f52eb` High items | H | H | Crit | Sec Reviewer | Document FAIL findings; remediation plan dated — no silent PASS | Open |
| RK-06 | Deploy FAIL on compose/Caddy/seed | M | H | High | Deploy Lead | Defer Unit B seed; keep edge Unit A gated | Open |
| RK-07 | Residual RR-2 (`behind 14`) rejected | M | H | High | Gov Board | Keep no bulk merge; written accept or forensics defer | Open |
| RK-08 | PO rejects scope / platform sprawl | L | H | Med | PO | Confirm Complaint Module / lab sync only | Open |
| RK-09 | Team starts Phase 5 Git early | M | Crit | Crit | Program Mgr | Daily reminder: Execution NOT authorized | Open |
| RK-10 | Re-RAB scheduled with incomplete pack | M | H | High | Release Mgr | WP-08 checklist gate | Open |

**Dashboard rollup:** Critical open = RK-01, RK-04, RK-05, RK-09.

---

# 7. Issue Register / Issue Dashboard

| ID | Issue | WP | Severity | Owner | Raised | Due | Status | Resolution |
|---|---|---|---|---|---|---|---|---|
| IS-01 | All Approval Matrix rows unsigned | WP-07 | High | Release Mgr | 2026-07-31 | M6 | Open | Collect signatures |
| IS-02 | Base SHA Lock still DRAFT | WP-01 | High | Tech Lead | 2026-07-31 | M1 | Open | Sign `Base_SHA_Lock_*` |
| IS-03 | Split Plans still DRAFT | WP-02 | High | Tech Lead | 2026-07-31 | M2 | Open | Sign split doc |
| IS-04 | Overlap = path-only; content review pending | WP-03 | High | Tech Lead | 2026-07-31 | M3 | Open | Compat memo |
| IS-05 | Security sheet UNSIGNED | WP-04 | High | Sec | 2026-07-31 | M4 | Open | Complete S-01…S-09 |
| IS-06 | Deployment sheet UNSIGNED | WP-05 | High | Deploy | 2026-07-31 | M4 | Open | Complete D-01…D-08 |
| IS-07 | Rollback Pack DRAFT unsigned | WP-06 | Med | Deploy+RM | 2026-07-31 | M5 | Open | Sign R-01…R-06 |
| IS-08 | Residual risks not accepted | WP-07 | High | Board/TL | 2026-07-31 | M6 | Open | Sign residual sheet |
| IS-09 | Product Owner A-09 missing | WP-07 | High | PO | 2026-07-31 | M6 | Open | Scope sign-off |
| IS-10 | RAB = NO-GO (expected until M8) | — | Info | Board | 2026-07-31 | M8 | Open | Re-session after M7 |

**Dashboard:** 9 actionable Open · 1 informational (IS-10).

---

# 8. Decision Register

| ID | Decision | Date | Status | Source |
|---|---|---|---|---|
| DEC-G-01 | SoT Batch-1 = `origin/feature/cm-batch1-s2-persistence` | 2026-07-31 | Approved | Reconciliation |
| DEC-G-02 | VPS = lab deploy target; not Batch-1 code SoT | 2026-07-31 | Approved | Reconciliation |
| DEC-G-03 | Git strategy = Release Branch + selective cherry-pick; no merge/rebase VPS `main` | 2026-07-31 | Approved | Phase 1/2 |
| DEC-G-04 | Mixed ×4 = SPLIT; `ad4a373` = KEEP | 2026-07-31 | Approved | Phase 1 |
| DEC-G-05 | Pick order after SPLIT: `96f52eb`→`2f1348a`→`a476ebf`→`ad4a373`→`41a0f48` | 2026-07-31 | Approved | Phase 1/3 |
| DEC-G-06 | Preparation YES WITH CONDITIONS; Execution NO-GO | 2026-07-31 | Approved | Phase 2/4 |
| DEC-G-07 | Phase 5 Runbook PRE-APPROVED only | 2026-07-31 | Approved | Phase 5 |
| DEC-G-08 | Execution Readiness Program = path to next RAB | 2026-07-31 | Approved | Readiness Program |
| DEC-D-01 | Proposed base tip `2bf779d` | 2026-07-31 | **Pending sign** | Base SHA draft |
| DEC-D-02 | Draft branch name `release/cm-batch1-vps-sync` | 2026-07-31 | Informative | Phase 3 |

No new governance decisions in this manual.

---

# Work Package Execution Cards

Status legend: **Not Started** · **In Progress** · **Blocked** · **Done** · **Rejected**

---

## WP-01 — Release Base Approval

| Field | Content |
|---|---|
| **Current Status** | Not Started (draft artifact exists; unsigned) |
| **Owner** | Tech Lead + Release Manager |
| **Start Condition** | W0 RACI names filled |
| **Finish Condition** | Base SHA Lock signed Approve by Tech Lead + RM |
| **Deliverables** | Signed Base SHA Lock (full SHA, short, freeze date, not-VPS-main statement) |
| **Evidence Required** | `Base_SHA_Lock_*.md` with signatures |
| **Blocking Items** | IS-02; unnamed Tech Lead/RM |
| **Success Criteria** | A-01 / R7 / G2 closable at pack time |
| **DoD** | See §11 WP-01 |

---

## WP-02 — Mixed Commit Split Plans

| Field | Content |
|---|---|
| **Current Status** | Not Started (draft exists; unsigned) |
| **Owner** | Tech Lead (+ BE/FE Leads) |
| **Start Condition** | W0 done; Phase 1 matrix + Phase 0 paths available |
| **Finish Condition** | Split Plans signed Approve (TL + scoped BE/FE) |
| **Deliverables** | Approved C-01…C-05 unit tables + sequence |
| **Evidence Required** | Signed `Split_Plans_VPS_Mixed_*.md` |
| **Blocking Items** | IS-03; RK-03 |
| **Success Criteria** | A-02 / R8 / G4 closable |
| **DoD** | See §11 WP-02 |

---

## WP-03 — Batch-1 Compatibility Review

| Field | Content |
|---|---|
| **Current Status** | Not Started (path overlap note exists; content review pending) |
| **Owner** | Tech Lead |
| **Start Condition** | WP-01 Done; WP-02 Done |
| **Finish Condition** | Compat memo signed; all 13 EXISTS paths dispositioned |
| **Deliverables** | `Compat_Review_Batch1_<date>.md`; A-03 signed |
| **Evidence Required** | Compat memo + signed Approval Matrix A-03 |
| **Blocking Items** | IS-04; RK-04 |
| **Success Criteria** | Not claiming “no path conflict”; RR-3 addressable |
| **DoD** | See §11 WP-03 |

---

## WP-04 — Security Review

| Field | Content |
|---|---|
| **Current Status** | Not Started (template unsigned) |
| **Owner** | Security Reviewer |
| **Start Condition** | WP-02 Done; WP-03 findings available for auth/IAM |
| **Finish Condition** | S-01…S-09 complete; overall PASS **or** FAIL with dated remediation (no silent skip) |
| **Deliverables** | Signed Security Sign-off |
| **Evidence Required** | `Security_Review_Signoff_*.md` |
| **Blocking Items** | IS-05; RK-05 |
| **Success Criteria** | A-05 / R4 / G7 closable only on PASS (or Board waiver path documented for later RAB — not invented here) |
| **DoD** | See §11 WP-04 |

---

## WP-05 — Deployment Review

| Field | Content |
|---|---|
| **Current Status** | Not Started (template unsigned) |
| **Owner** | Deploy Lead |
| **Start Condition** | WP-01 Done; WP-02 Done |
| **Finish Condition** | D-01…D-08 complete; PASS signed |
| **Deliverables** | Signed Deployment Sign-off (+ D-07 note) |
| **Evidence Required** | `Deployment_Review_Signoff_*.md` |
| **Blocking Items** | IS-06; RK-06 |
| **Success Criteria** | A-06 / R5 / G8 closable |
| **DoD** | See §11 WP-05 |

---

## WP-06 — Rollback Pack

| Field | Content |
|---|---|
| **Current Status** | Not Started (draft unsigned) |
| **Owner** | Deploy Lead + Release Manager |
| **Start Condition** | WP-01 Done; WP-02 Done |
| **Finish Condition** | R-01…R-06 approved by both owners |
| **Deliverables** | Signed Rollback Pack |
| **Evidence Required** | `Rollback_Pack_*.md` signed |
| **Blocking Items** | IS-07 |
| **Success Criteria** | A-07 / R6 / G9 closable |
| **DoD** | See §11 WP-06 |

---

## WP-07 — Evidence Pack

| Field | Content |
|---|---|
| **Current Status** | Not Started (pack index partial; signatures missing) |
| **Owner** | Release Manager (+ Board RR-2, PO A-09) |
| **Start Condition** | WP-01…WP-06 Done (PASS) |
| **Finish Condition** | Pack COMPLETE; residual signed; PO signed; A-01…A-09 Go |
| **Deliverables** | Updated pack README; signed Residual; signed Approval Matrix A-01…A-09 |
| **Evidence Required** | All WP evidence + `Residual_Risk_Acceptance_*.md` + Approval Matrix |
| **Blocking Items** | IS-01, IS-08, IS-09 |
| **Success Criteria** | R3/R9/R10/G10 closable for re-RAB |
| **DoD** | See §11 WP-07 |

---

## WP-08 — RAB Readiness Review

| Field | Content |
|---|---|
| **Current Status** | Not Started |
| **Owner** | Release Manager (Program Mgr accountable) |
| **Start Condition** | WP-07 Done |
| **Finish Condition** | Readiness memo issued; re-RAB meeting scheduled; R1–R10 evidence pointers listed |
| **Deliverables** | `RAB_Readiness_Memo_<date>.md` + agenda |
| **Evidence Required** | Memo + calendar invite + pack index link |
| **Blocking Items** | Incomplete WP-07 |
| **Success Criteria** | M7 met; **A-10 / RAB GO not pre-signed** — reserved for M8 |
| **DoD** | See §11 WP-08 |

---

# Completion Dashboard

| WP | Status | % | Milestone |
|---|---|---|---|
| WP-01 | Not Started | 0 | M1 |
| WP-02 | Not Started | 0 | M2 |
| WP-03 | Not Started | 0 | M3 |
| WP-04 | Not Started | 0 | M4 |
| WP-05 | Not Started | 0 | M4 |
| WP-06 | Not Started | 0 | M5 |
| WP-07 | Not Started | 0 | M6 |
| WP-08 | Not Started | 0 | M7 |
| **Program** | **Not Started** | **0%** | → M7 |

Draft artifacts present ≠ Done. Done = **signed** per DoD.

---

# 11. Definition of Done (every WP)

### WP-01 DoD
- [ ] Full base SHA written  
- [ ] Short SHA written  
- [ ] Freeze date written  
- [ ] Explicit “not VPS main”  
- [ ] Tech Lead signature  
- [ ] Release Manager signature  
- [ ] File stored under `deploy/evidence/`  

### WP-02 DoD
- [ ] C-01…C-04 Unit A/B path tables final  
- [ ] C-05 KEEP confirmed  
- [ ] Pick sequence confirmed  
- [ ] No path double-assigned  
- [ ] Tech Lead Approve  
- [ ] BE Lead Approve (C-02/C-04)  
- [ ] FE Lead Approve (C-03)  

### WP-03 DoD
- [ ] All 13 EXISTS paths listed with disposition (OK / merge-note / defer)  
- [ ] ABSENT paths acknowledged  
- [ ] Compat memo filed  
- [ ] Tech Lead signs A-03  
- [ ] No false “no conflict” claim  

### WP-04 DoD
- [ ] S-01…S-09 each PASS/FAIL/N/A + notes  
- [ ] High items (`96f52eb` env/JWT/docs, XFF, IAM, Users UI) addressed  
- [ ] Overall PASS signed **or** FAIL with remediation date  
- [ ] Security Reviewer name + date  

### WP-05 DoD
- [ ] D-01…D-08 each result + notes  
- [ ] D-06 UFW out-of-git explicit  
- [ ] D-07 behind-14 stance recorded  
- [ ] Deploy Lead PASS signature  

### WP-06 DoD
- [ ] Lab edge rollback documented  
- [ ] Release-branch reverse-revert order listed  
- [ ] Abort criteria listed  
- [ ] Seed backup rule if seed in scope  
- [ ] Deploy Lead + RM signatures  

### WP-07 DoD
- [ ] Pack index lists all required artifacts Present/Signed  
- [ ] Residual RR-1…RR-7 dispositioned; RR-2 & RR-3 accepted or blocking noted  
- [ ] Governance Board acceptance block for RR-2  
- [ ] Product Owner A-09  
- [ ] Approval Matrix A-01…A-09 = Go  
- [ ] A-10 left blank pending RAB  

### WP-08 DoD
- [ ] Readiness memo maps R1–R10 → evidence paths  
- [ ] No PASS claimed without signed file  
- [ ] Re-RAB date/time proposed or booked  
- [ ] Phase 5 still marked NOT AUTHORIZED until GO  
- [ ] Program Mgr / RM sign memo  

---

# 12. Program Completion Criteria

Program delivery is **COMPLETE** when:

1. All WP-01…WP-08 = **Done** per DoD.  
2. Completion Dashboard = 100% to M7.  
3. Issue Register actionable items IS-01…IS-09 = Closed.  
4. Critical risks RK-01/04/05/09 mitigated or accepted in residual sheet.  
5. Re-RAB session scheduled.  
6. **Still true:** no Git branch/cherry-pick/merge/deploy performed.  
7. Handoff package pointed to Board for **M8**.

Program is **NOT complete** if only drafts exist without signatures.

---

# 9. Weekly Status Report Template

```text
ECMP Execution Readiness — Weekly Status
Week of: ____    Author: ____ (Program Manager)

1. Headline (1–2 sentences)
2. RAB status: NO-GO (unchanged) / re-RAB scheduled: ____
3. Milestone progress: M0–M7 (Done / In Progress / Not Started)
4. WP status table: ID | Status | % | Owner | Blocker
5. Issues opened/closed this week
6. Risks changed this week
7. Decisions needed from Board/PO this week
8. Next week plan (max 5 bullets)
9. Explicit reminder: Phase 5 Git execution NOT authorized
```

---

# 10. Daily Progress Report Template

```text
ECMP Execution Readiness — Daily Progress
Date: ____    Author: ____

1. Yesterday: done
2. Today: plan
3. Blockers (ID from Issue Register)
4. WP touched today + new status
5. Signatures collected today (who/what)
6. Ask / help needed
7. Confirmation: no Git promote actions taken
```

---

# Formal Conclusion

This **Program Execution Manual** is the operational layer over the approved Execution Readiness Program.  
It is executable by a project team through reviews and sign-offs only.  
**Execution of Phase 5 remains NOT AUTHORIZED** until Phase 4 RAB issues GO or GO WITH WAIVERS.

—*End of Delivery Plan / Program Execution Manual v1.0*
