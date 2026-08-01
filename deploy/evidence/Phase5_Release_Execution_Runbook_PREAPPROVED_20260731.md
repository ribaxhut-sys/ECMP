# ECMP Phase 5 — Release Execution Runbook (PRE-APPROVED)

| Field | Value |
|---|---|
| Version | 1.0 |
| Date | 2026-07-31 |
| Role | ECMP Release Manager |
| Governance status | Phase 4 RAB = **NO-GO** (Phase 4.5 Closure) |
| Execution status | **NOT AUTHORIZED** |
| Document class | Operational runbook only — does not change governance |

> **HARD STOP:** Do not create a release branch, cherry-pick, merge, rebase, deploy, or rewrite history until Phase 4 RAB issues **GO** or **GO WITH WAIVERS**. This document is PRE-APPROVED content for use **after** that decision.

Immutable inputs: Repository Reconciliation · Phase 0 · Phase 1 · Phase 2 · Phase 3 · Phase 4 · Phase 4.5.

---

# Executive Summary

This runbook operationalizes the **already approved** Git strategy: **Release Branch + selective cherry-pick** from VPS-only commits after SPLIT, base = Batch-1 SoT, **no** merge/rebase of VPS `main`.

Because RAB is **NO-GO**, the sequence below is **frozen for reference**. Release Manager must verify RAB status at Step 0; on NO-GO, stop immediately.

Approved pick order (after SPLIT): `96f52eb` → `2f1348a` → `a476ebf` → `ad4a373` → `41a0f48`.  
KEEP: `ad4a373`. SPLIT required: four Mixed commits per `Split_Plans_VPS_Mixed_20260731.md`.

---

# Execution Timeline (authorized only after RAB GO)

| Step | Name | Checkpoint | Gate |
|---|---|---|---|
| 0 | Verify RAB status | — | STOP if not GO / GO WITH WAIVERS |
| 1 | Verify DoR A-01…A-10 + evidence pack | CP-1 | STOP on FAIL |
| 2 | Create release branch from locked base SHA | CP-1 → after create | |
| 3 | Execute approved cherry-picks (split units) in order | CP-2 after each | STOP on FAIL |
| 4 | Resolve textual conflicts (approved paths only) | CP-2 | |
| 5 | Run approved smoke tests | CP-3 | STOP on FAIL |
| 6 | Record resulting SHAs + evidence | CP-4 | |
| 7 | Open Pull Request to SoT | CP-4 | Await approval |
| 8 | Pre-merge validation | CP-5 | STOP on FAIL |
| 9 | Merge only after explicit promote Go (DoRR) | — | Out of auto-runbook if not signed |
| 10 | Post-execution validation + archive | — | |

---

# 1. Execution Preconditions

All must be true **before** Step 2:

| ID | Precondition | Source |
|---|---|---|
| X-00 | Phase 4 RAB = GO or GO WITH WAIVERS | Phase 4 / re-RAB |
| X-01 | DoR A-01…A-10 = Go (signed) | Phase 3 / Approval Matrix |
| X-02 | Base SHA locked in writing | `Base_SHA_Lock_*` (proposed `2bf779d` until signed) |
| X-03 | Split plans approved | `Split_Plans_VPS_Mixed_20260731.md` |
| X-04 | Path overlap note accepted; content review for EXISTS paths done | `Path_Overlap_VPS_vs_Batch1_20260731.md` |
| X-05 | Security + Deployment sign-off PASS | S-*/D-* sheets |
| X-06 | Rollback pack approved | `Rollback_Pack_DRAFT_*` signed |
| X-07 | Residual risks accepted in writing (min RR-2, RR-3) | Residual risk sheet |
| X-08 | Product Owner A-09 signed | Approval Matrix |
| X-09 | Strategy unchanged: Release Branch + selective cherry-pick; **no** merge/rebase VPS `main` | Phase 1/2/3 |

If any precondition false → **Execution is not authorized.**

---

# 2. Execution Sequence

## Step 0 — Verify RAB status

| Field | Content |
|---|---|
| Purpose | Enforce governance freeze |
| Owner | Release Manager |
| Input | Latest Phase 4 RAB / re-RAB decision |
| Output | GO / GO WITH WAIVERS / NO-GO |
| Success Criteria | Decision is GO or GO WITH WAIVERS |
| Failure Criteria | NO-GO, missing, or expired without re-RAB |
| Evidence Produced | Screenshot/copy of RAB decision archived |
| Rollback Action | N/A — do not start |

**Current recorded decision: NO-GO → STOP. Execution is not authorized.**

---

## Step 1 — Verify DoR and evidence pack (CP-1)

| Field | Content |
|---|---|
| Purpose | Confirm preparation complete |
| Owner | Release Manager |
| Input | Approval Matrix A-01…A-10; evidence pack index |
| Output | CP-1 PASS/FAIL |
| Success Criteria | All A-01…A-10 signed Go; evidence pack complete |
| Failure Criteria | Any unsigned blocking row |
| Evidence Produced | `CP1_Pre_Branch_Checklist_<date>.md` |
| Rollback Action | Remain on SoT tip; no branch |

---

## Step 2 — Create Release Branch

| Field | Content |
|---|---|
| Purpose | Hold selective picks off locked SoT base |
| Owner | Release Manager + Tech Lead |
| Input | Locked base SHA; draft name `release/cm-batch1-vps-sync` (or agreed) |
| Output | Release branch at base SHA |
| Success Criteria | Branch exists; tip == locked base; not created from VPS `main` |
| Failure Criteria | Wrong base, created from VPS `main`, or RAB not GO |
| Evidence Produced | Branch name + base SHA in evidence |
| Rollback Action | Delete local unused branch / close remote branch without merge (no history rewrite on `main`/SoT) |

**Authorized only if Step 0–1 PASS.**

---

## Step 3 — Execute approved cherry-picks (after SPLIT)

| Field | Content |
|---|---|
| Purpose | Promote only approved split units |
| Owner | Tech Lead (exec) / Release Manager (sequence) |
| Input | Approved split units; order below |
| Output | New commit SHA(s) on release branch per unit |
| Success Criteria | Only approved paths; order respected; CP-2 PASS each time |
| Failure Criteria | Picking Mixed bulk; wrong order; unapproved paths; unresolved conflict |
| Evidence Produced | Per-pick SHA log |
| Rollback Action | See §5 — abort/revert reverse order on **release branch only** |

### Approved order (Phase 1/3 + Split Plans)

1. `96f52eb` Unit A (infra/edge) — then optional Unit B (docs)  
2. `2f1348a` Unit A (IAM app) — then optional Unit B (seed/docs)  
3. `a476ebf` Unit A (Users/Reports UI+API) — then Unit B (evidence)  
4. `ad4a373` KEEP whole (restore-drill evidence)  
5. `41a0f48` Unit B (hardening evidence) then Unit A (rate-limit app) — or evidence chain as in split plan; **rate-limit app after edge infra**

Do **not** introduce alternate strategies (no rebase onto `origin/main`, no merge VPS `main`).

After **every** unit: run **CP-2**.

---

## Step 4 — Resolve textual conflicts

| Field | Content |
|---|---|
| Purpose | Resolve known overlaps without strategy change |
| Owner | Tech Lead |
| Input | Conflict on EXISTS paths / `deploy/README.md` & `SMOKE_UAT_*` (A→M) |
| Output | Conflict resolution notes |
| Success Criteria | Resolution recorded; no silent drop of SoT Batch-1 behavior |
| Failure Criteria | Unresolvable without new design; scope creep |
| Evidence Produced | `Conflict_Resolution_<pick>_<date>.md` |
| Rollback Action | Abort pick; reset release branch to prior CP-2 good SHA |

---

## Step 5 — Run approved smoke tests (CP-3)

| Field | Content |
|---|---|
| Purpose | Minimal verification of picked surfaces (Phase 3 C-09 / DoRR) |
| Owner | QA Lead |
| Input | Release branch tip; scope of units actually picked |
| Output | Smoke result PASS/FAIL |
| Success Criteria | Health/edge as scoped; login+rate-limit if picked; users IAM/UI if picked |
| Failure Criteria | Any scoped smoke FAIL |
| Evidence Produced | `Smoke_Results_<date>.md` |
| Rollback Action | Do not open PR; revert to last good tip or abort |

---

## Step 6 — Record resulting SHAs

| Field | Content |
|---|---|
| Purpose | Traceability |
| Owner | Release Manager |
| Input | Branch tip + each pick SHA |
| Output | SHA register |
| Success Criteria | Base + every pick + tip recorded |
| Failure Criteria | Missing SHA |
| Evidence Produced | `Release_SHA_Register_<date>.md` |
| Rollback Action | N/A (documentation) |

---

## Step 7 — Open Pull Request (CP-4)

| Field | Content |
|---|---|
| Purpose | Promote via PR to SoT — not merge from VPS `main` |
| Owner | Release Manager |
| Input | Release branch; SHA register; smoke PASS |
| Output | PR URL |
| Success Criteria | PR targets Batch-1 SoT (or Board-named successor); description lists picks |
| Failure Criteria | PR from VPS `main`; missing evidence |
| Evidence Produced | PR URL archived |
| Rollback Action | Close PR without merge |

---

## Step 8 — Await approval / Before Merge (CP-5)

| Field | Content |
|---|---|
| Purpose | Enforce DoRR + human promote Go |
| Owner | Release Manager + reviewers |
| Input | PR checks; Security/Deploy not withdrawn; Product/Governance promote Go |
| Output | CP-5 PASS → merge allowed |
| Success Criteria | Reviews PASS; DoRR items true; no RAB revocation |
| Failure Criteria | Failed checks; withdrawn sign-off; unresolved EXISTS conflict |
| Evidence Produced | Review approvals log |
| Rollback Action | Do not merge; close or update PR |

---

## Step 9 — Merge (only if CP-5 PASS)

| Field | Content |
|---|---|
| Purpose | Land release branch on SoT via approved PR |
| Owner | Release Manager / repo admin per protection rules |
| Input | CP-5 PASS |
| Output | Merge commit SHA |
| Success Criteria | Merge commit on SoT; no force-push |
| Failure Criteria | Force-push, merge of VPS `main`, or CP-5 FAIL |
| Evidence Produced | Merge commit SHA (+ optional release tag if Board-approved) |
| Rollback Action | Revert merge commit on SoT via new PR (preferred); do not rewrite SoT history |

**Note:** Live Aggregate cutover to production lab URL is **out of scope** of this runbook unless a separate cutover DEC is approved (Reconciliation).

---

# 3. Checkpoint Verification

| CP | When | PASS | FAIL | STOP |
|---|---|---|---|---|
| CP-1 | Before Release Branch | RAB GO/GO WITH WAIVERS + DoR A-01…A-10 signed + base SHA locked | Any precondition missing | Do not create branch |
| CP-2 | After every cherry-pick unit | Clean pick or documented conflict resolution; only approved paths | Wrong paths, Mixed bulk, unresolved conflict | Abort further picks; rollback release branch tip |
| CP-3 | After smoke | Scoped smoke PASS | Any scoped FAIL | No PR; rollback or fix-forward only with re-approval |
| CP-4 | Before PR | SHA register complete; smoke PASS; evidence attached | Missing SHA/evidence | Do not open PR |
| CP-5 | Before merge | Reviews + DoRR + promote Go | Failed review / sign-off withdrawn | Do not merge |

---

# Checkpoint Matrix

| CP | Owner | Evidence | On FAIL |
|---|---|---|---|
| CP-1 | Release Manager | Pre-branch checklist | STOP |
| CP-2 | Tech Lead | Per-pick SHA + conflict note | STOP picks |
| CP-3 | QA Lead | Smoke results | STOP PR |
| CP-4 | Release Manager | SHA register + PR draft | STOP open PR |
| CP-5 | Release Manager | Review + promote Go | STOP merge |

---

# 4. Failure Handling

| Condition | Immediate Action | Escalation | Evidence | Rollback |
|---|---|---|---|---|
| RAB still NO-GO / revoked | STOP all Git | Governance Board | RAB record | None — never started / freeze |
| DoR incomplete | STOP before branch | Release Manager → owners of unsigned rows | Approval Matrix | None |
| Wrong base / branch from VPS `main` | Do not pick; delete/close bad branch | Tech Lead | Branch SHA log | Remove bad branch |
| Cherry-pick conflict unresolvable | Abort current pick | Tech Lead → Governance | Conflict note | Reset release tip to last CP-2 PASS |
| Mixed commit picked without SPLIT | STOP; do not continue | Release Manager | Pick log | Revert that pick on release branch |
| Smoke FAIL | Block PR | QA + owning Lead | Smoke log | Revert failing unit(s) |
| Security/Deploy sign-off withdrawn | Freeze PR/merge | Security/Deploy Lead | Written withdrawal | No merge; consider revert |
| Push/PR blocked | Stop; do not force-push | Tech Lead | Error log | Keep local evidence; no rewrite |
| Scope creep / redesign requested | Reject; stay on runbook | Product Owner | Decision note | N/A |

---

# Failure Matrix (summary)

| ID | Severity | STOP? |
|---|---|---|
| F-RAB | Critical | Yes |
| F-DoR | Critical | Yes |
| F-BASE | Critical | Yes |
| F-PICK | High | Yes (further picks) |
| F-SMOKE | High | Yes (PR) |
| F-SIGNOFF | High | Yes (merge) |
| F-SCOPE | Medium | Yes (until PO) |

---

# 5. Rollback Procedure

Aligned with approved Rollback Pack (release-level):

1. **Prefer:** revert commits on release branch in **reverse pick order**.  
2. **Abort mid-sequence:** stop picks; tip = last good SHA; record abort.  
3. **PR open:** close without merge.  
4. **Already merged:** revert merge via new PR on SoT — **no** force-push to SoT/`main`.  
5. **Never:** merge VPS `main` to “undo”; never rewrite VPS `main` history as rollback.  
6. **Edge lab only:** Caddy/compose lab rollback per deploy runbook — separate from Git promote rollback.  
7. **Seed applied:** restore from pre-seed backup (R-04) before retry.

---

# 6. Evidence Collection

| Artifact | When | Owner |
|---|---|---|
| RAB GO decision copy | Step 0 | Release Manager |
| CP-1 checklist | Before branch | Release Manager |
| Release branch name + base SHA | Step 2 | Release Manager |
| Per cherry-pick SHA (+ unit id) | Each Step 3 | Tech Lead |
| Conflict resolution notes | Step 4 | Tech Lead |
| Smoke test results | Step 5 | QA Lead |
| Release SHA register | Step 6 | Release Manager |
| PR URL | Step 7 | Release Manager |
| Review / promote approvals | Step 8 | Release Manager |
| Merge commit SHA | Step 9 | Release Manager |
| Release tag (if Board-approved) | Optional post-merge | Release Manager |
| Rollback logs (if any) | On failure | Release Manager |
| Final evidence pack index update | End | Release Manager |

Archive under `deploy/evidence/` with dated filenames.

---

# Evidence Register (template)

| Item | Value |
|---|---|
| RAB decision | _pending GO_ |
| Base SHA | _locked SHA_ |
| Release branch | `release/cm-batch1-vps-sync` (or agreed) |
| Pick SHAs | _list_ |
| Tip SHA | |
| Smoke | |
| PR URL | |
| Merge SHA | |
| Tag | |

---

# 7. Post Execution Validation

| Check | PASS criteria |
|---|---|
| Repository Integrity | No force-push to SoT/`main`; remotes consistent |
| Branch Integrity | Release branch tip matches SHA register; not VPS `main` |
| Commit Traceability | Every pick maps to approved split unit + source VPS SHA |
| Evidence Completeness | All §6 artifacts present |
| Rollback Availability | Rollback pack still valid against tip/merge |
| Deployment Readiness | **Lab/SoT promote ready ≠ production Aggregate cutover** unless separate DEC |

---

# Post Execution Checklist

- [ ] RAB GO recorded  
- [ ] Base SHA == locked  
- [ ] Only approved units picked  
- [ ] Order respected  
- [ ] CP-1…CP-5 archived  
- [ ] Smoke PASS archived  
- [ ] PR URL archived  
- [ ] Merge SHA archived (if merged)  
- [ ] No merge/rebase of VPS `main` occurred  
- [ ] Rollback path verified  

---

# Formal Conclusion

1. **Execution is not authorized** under current Phase 4 RAB **NO-GO**.  
2. This Phase 5 runbook is **PRE-APPROVED** as operational content only.  
3. It **must not be executed** until Phase 4 RAB issues **GO** or **GO WITH WAIVERS** and DoR A-01…A-10 remain satisfied.  
4. Git strategy remains immutable: **Release Branch + selective cherry-pick**; no redesign.

—*End of Phase 5 Release Execution Runbook v1.0 (PRE-APPROVED / NOT FOR EXECUTION)*
