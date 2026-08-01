# Split Plans — VPS Mixed Commits — APPROVED (Lab Operator)

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Status | **APPROVED** (WP-02) with promote-scope constraint from WP-03 |
| Rule | Do not cherry-pick Mixed bulk; honor Unit A/B splits |

## Units (unchanged structure)

| SHA | Action | Unit A (candidate) | Unit B (separate/defer) |
|---|---|---|---|
| `96f52eb` | SPLIT | Caddy, compose.prod, backup script, `.env.prod.example`, `.gitignore` | DEC-020 lab doc, deploy README, SMOKE |
| `2f1348a` | SPLIT | users repo/service/test | seed SQL, deploy docs |
| `a476ebf` | SPLIT | Users/Reports UI+API paths | backup-verify evidence |
| `41a0f48` | SPLIT | rate_limit + auth/router + errors + test | hardening evidence |
| `ad4a373` | KEEP | restore-drill evidence whole | — |

## Promote-scope constraint (binding from WP-03)

Until content-merge plans exist for **DEFER** paths:

- **Authorized pick candidates (post-RAB):** ABSENT-on-SoT infra/evidence units primarily (`96f52eb` Unit A minus risky compose overwrite if WP-03 says DEFER compose; evidence KEEPs; rate_limit.py **new file** OK with care).
- **Deferred by default:** any Unit that touches EXISTS paths marked **DEFER** in `Compat_Review_Batch1_20260801.md` (users/*, auth/router bulk, api clients, docker-compose.prod.yml overwrite).

Pick order if authorized: infra ABSENT → evidence KEEP → new rate_limit files → **stop** before DEFER units.

## Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Tech Lead | Lab Operator | 2026-08-01 | **Approve** (with WP-03 constraint) |
| Backend Lead | Lab Operator (W-SOD-1) | 2026-08-01 | **Approve** |
| Frontend Lead | Lab Operator (W-SOD-1) | 2026-08-01 | **Approve** |

Supersedes draft: `Split_Plans_VPS_Mixed_20260731.md`
