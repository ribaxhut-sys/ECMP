# MISSING_APPROVALS.md — Mode A Batch-1 RC

| Field | Value |
|---|---|
| Document ID | REL-MISS-MA-B1-001 |
| Date | 2026-08-01 |
| SHA | `1608245` |
| Sync | External decisions `EXT-HD-RC-MA-B1-20260801` synchronized into SoT |
| Fake signatures | **Forbidden** — rows below record external decisions only |

---

## Closed this sync (external decisions)

| Approval | Owner | Status |
|---|---|---|
| U-5 — Tech Lead / SA / BO | TL / SA / BO | **COMPLETE** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) |
| Board B-1 DEC collision | Architecture Board / PMO | **APPROVED Option A** |
| Board B-2 REL-TAG path | Architecture Board + RM | **APPROVED Option B** |
| SemVer identity | Release Manager / PMO | **`v1.1.0-rc.1`** |
| REL-RC-001 §5 TL / QA / RM | TL · QA · RM | **Go** (`EXT-HD-RC-MA-B1-20260801` / W-SOD-1) |

---

## Still open (cut mechanics — not reopened human gates)

**NONE** — freeze commit + annotated tag `v1.1.0-rc.1` complete.

---

## Optional / conditional (unchanged)

| Approval | Owner | Blocking Level | Required Before RC |
|---|---|---|---|
| Security delta note (S-03/S-04 vs post-P5) | Security Reviewer | **P1** | Recommended |
| ABSENT port IMS-001 / SEC Baseline | Release Manager (+ Sec) | **P1** | No if deferred in RC notes |
| Second reviewer to lift W-SOD-1 | Governance | **P1** | No for lab claim if W-SOD-1 kept |
| R6-01 build/verify artifact run | Release Manager / Eng | **P1** | Lab N/A noted in assessment |
| CI green attestation bound to `1608245` | Tech Lead / QA | **P1** | Recommended |

---

## Explicitly NOT missing (already recorded)

| Item | Status |
|---|---|
| Phase 4 RAB GO WITH WAIVERS (limited Phase 5) | Present |
| Approval Matrix A-01…A-10 (lab) | Present |
| Security CONDITIONAL PASS (lab) | Present |
| Deployment PASS (lab) | Present |
| Residual risk acceptance (lab) | Present |
| Rollback pack APPROVED | Present |
| G2 Mode A EXITED | Present |
| Mode B CLOSED / BLOCKED | Present |
