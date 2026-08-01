# NEXT_HUMAN_ACTIONS.md — Mode A Batch-1 RC

| Field | Value |
|---|---|
| Document ID | REL-NEXT-MA-B1-001 |
| Date | 2026-08-01 |
| SHA | `1608245` |
| Automation | May prepare docs only — **must not** sign or invent Go |
| Related | `MISSING_APPROVALS.md`, `RC_GATE_REPORT.md`, `DEC_ID_Collision_Register_20260801.md` |

---

## Sync note (2026-08-01)

External decisions `EXT-HD-RC-MA-B1-20260801` recorded in SoT: B-1=A, B-2=B, SemVer=`v1.1.0-rc.1`, U-5 COMPLETE, QA/TL COMPLETE, REL-RC-001 §5 Go.

**Remaining cut actions (not reopening human gates):**

1. Freeze clean commit on `feature/cm-batch1-s2-persistence`  
2. Create annotated tag `v1.1.0-rc.1` when explicitly permitted  
3. Re-affirm `RC_GATE_REPORT.md` after freeze+tag  

## Priority order

### 1. Architecture Board / PMO

| # | Action | Input artefacts | Output needed |
|---|---|---|---|
| B-1 | Resolve DEC-020 / DEC-021 **ID collision** (option A / B / C) | `DEC_ID_Collision_Register_20260801.md` | Written Board choice; authorize renumber **without** changing Approved decision substance improperly |
| B-2 | Decide **tag path**: merge `feature/cm-batch1-s2-persistence` → `main` then tag, **or** time-boxed waiver to tag feature tip for lab RC | REL-TAG-001; `RC_GATE_REPORT.md` | Written decision |
| B-3 | Confirm Mode B remains CLOSED for this RC | `Mode_B_Blocked_*` | No unlock |

**STOP:** Do not renumber DEC files until B-1 is recorded.

### 2. Release Manager

| # | Action | Notes |
|---|---|---|
| RM-1 | Propose SemVer `vX.Y.Z-rc.N` (do not invent in automation) | Align REL-VER-001; avoid colliding with foundation `v1.0.0` meaning |
| RM-2 | After Board B-2: prepare CHANGELOG section + release notes stub | Empty approval lines OK |
| RM-3 | Ensure working tree clean freeze commit of doc pack | REL-RC-001 / REL-TAG-001 |
| RM-4 | Complete REL-RC-001 assessment to PASS then **sign §5** | Use `REL_RC_001_*Assessment*` |
| RM-5 | Optional: authorize ABSENT port IMS-001 / SEC Baseline or defer in RC notes | Gap on tip |
| RM-6 | After all Go: create **annotated** tag on authorized ref only | Never move tags |

### 3. Tech Lead

| # | Action |
|---|---|
| TL-1 | Sign U-5 G0 exit (or W-SOD-1 conditional lab mark) |
| TL-2 | Confirm G2 / dual-tree claims still accurate at tip |
| TL-3 | Sign REL-RC-001 §5 Go/No-Go after checklist green |
| TL-4 | Optional: attach CI attestation for tip SHA |

### 4. Solution Architect

| # | Action |
|---|---|
| SA-1 | Sign U-5 G0 exit |
| SA-2 | Support Board on DEC collision (recommend Option A: O-06 keeps DEC-021; G2 → next ID) — **recommendation only** |
| SA-3 | Affirm FR-030/040 DEFER remains Mode A DoD |

### 5. Security Reviewer

| # | Action |
|---|---|
| SEC-1 | Optional delta note: S-03/S-04 vs post-P5 (`ECMP_AUTH_MODE` present; W-S04 closed) — **do not rewrite** original sign-off body |
| SEC-2 | Affirm W-S03 remains OPEN lab waiver; no Mode B fabrication |
| SEC-3 | If IMS/SEC Baseline ported: review status lines (RAB no longer NO-GO for limited scope) |

### 6. Business Owner / Product Owner

| # | Action |
|---|---|
| BO-1 | Sign U-5 DoR FRD-002 v0.2 |
| BO-2 | Optional countersign Sprint-03 residual DEFER (FR-030/040) |
| BO-3 | Affirm RC scope = Mode A Batch-1 lab RC — not Enterprise Platform |

### 7. QA Lead

| # | Action |
|---|---|
| QA-1 | Re-run or attest G2 pack at freeze SHA if required |
| QA-2 | Disclose Batch-1 RTM executed-TC gap vs G2 103 in RC notes |
| QA-3 | Sign REL-RC-001 §5 Go/No-Go |

---

## What automation / doc managers must NOT do

- Fill signature or Go/No-Go cells  
- Cut annotated RC tags  
- Renumber Approved DEC/ADR bodies without Board record  
- Enable Mode B / invent OIDC  
- Claim READY FOR RC before humans complete P0 list  

---

## Suggested sequence (after this pack)

```text
Board B-1 + B-2
  → RM-1 SemVer
  → U-5 (TL, SA, BO)
  → Freeze clean commit
  → QA/TL attest tests
  → REL-RC-001 §5 (TL, QA, RM)
  → Tag on authorized ref
  → Re-run RC_GATE_REPORT → aim READY FOR RC
```

Current: **documentation pack ready for Board review of open decisions**; RC cut **not** authorized by this file.
