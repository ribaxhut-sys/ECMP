# Mode A Batch-1 — RC Readiness Snapshot

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Tip | `1608245` on `feature/cm-batch1-s2-persistence` |
| Target | **Release Candidate** (internal/lab) — not Production |
| Status | **READY FOR RC** — frozen + tagged `v1.1.0-rc.1` |

## What is already closed

- G2 Mini Gate Mode A (EXITED)
- ADR-009 Addendum G2
- G1 exit verified
- Phase 4 RAB **GO WITH WAIVERS** (limited Phase 5 VPS ABSENT port — separate from RC tag)
- Phase 5 limited + post-P5 (W-S04 closed)
- SIT SoT choice recorded
- FR-030 / FR-040 = **DEFER** for Mode A DoD

## What still blocks declaring “Mode A Batch-1 RC”

| Gate | Status | Owner |
|---|---|---|
| U-5 human sign-off | **COMPLETE** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) | TL / SA / BO |
| DEC-020/021 ID collision remediation | **B-1 Option A recorded** (BA-03 renumber open) | Board / PMO |
| REL-RC-001 checklist filled for tip | **PASS (lab)** — §5 Go | Release Manager |
| Tag path vs REL-TAG-001 | **B-2 Option B** lab waiver recorded | Board + RM |
| SemVer + CHANGELOG RC section | **`v1.1.0-rc.1`** present | Release Manager / PMO |
| Annotated RC tag | **CUT** `v1.1.0-rc.1` |
| Clean freeze commit | **COMPLETE** |
| Second reviewer (optional lift W-SOD-1) | Not required for lab RC claim language if W-SOD-1 kept | Governance |

## Gate report

**Verdict:** see `RC_GATE_REPORT.md` (re-gated this pass)  
Assessment detail: `REL_RC_001_Mode_A_Batch1_Assessment_20260801.md`

## Explicitly not blockers for RC (lab)

- W-S03 OPEN (lab waiver; expires 2026-09-30 or Mode B contract)
- Mode B CLOSED
- FR-030 / FR-040 implementation
- IMS-001 / Security Baseline file restore from `main` (P1 doc port — confirm before ABSENT restore)

## Claim language allowed when gates above close

“Mode A Batch-1 Release Candidate at SHA … (lab / W-SOD-1).”  
**Not:** Production Enterprise Ready · Mode B complete.
