# Compatibility Review — VPS paths vs Batch-1 SoT (WP-03)

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| SoT tip | `2bf779d136a96c1c167abbacb51bf6e9a215791f` |
| Compared to | VPS branch tip used for diff (`HEAD` at review = docs/governance tip on lab; path deltas vs SoT) |
| Method | Path existence (prior) + `git diff --stat SoT HEAD -- <path>` |
| Status | **COMPLETE — A-03 signed** |

## Summary

| Class | Count | Disposition policy |
|---|---|---|
| ABSENT on SoT | 15 | **OK to pick** after Security/Deploy (new files) |
| EXISTS on SoT | 13 | **Almost all DEFER** — SoT tip has *more* / divergent content; applying VPS tip would regress Batch-1 |

## EXISTS dispositions

| Path | Diff signal (SoT→VPS tip) | Disposition | Note |
|---|---|---|---|
| `.gitignore` | small (−19/+1 style) | **MERGE-NOTE** | Manual merge; prefer SoT ignore rules + keep VPS backup ignore if needed |
| `backend/app/core/errors.py` | VPS smaller | **DEFER** | Do not overwrite SoT; rate-limit error wiring only via careful patch if ever |
| `backend/app/modules/auth/router.py` | VPS much smaller (−109) | **DEFER** | Batch-1 ahead; VPS rate-limit lines only as surgical patch later |
| `backend/app/modules/users/repository.py` | VPS smaller | **DEFER** | IAM SoT richer |
| `backend/app/modules/users/service.py` | VPS much smaller (−232) | **DEFER** | High regression risk |
| `backend/tests/test_users.py` | VPS much smaller | **DEFER** | |
| `docker-compose.prod.yml` | VPS much smaller (−151) | **DEFER** overwrite | May **add** Caddy service via manual port of Unit A snippets — not blind file replace |
| `frontend/.../reports/page.tsx` | VPS additive | **MERGE-NOTE** | Review before pick |
| `frontend/.../users/page.tsx` | VPS additive | **MERGE-NOTE** | Review before pick |
| `frontend/.../reports/index.ts` | tiny | **MERGE-NOTE** | |
| `frontend/.../users/index.ts` | tiny | **MERGE-NOTE** | |
| `frontend/src/lib/api/index.ts` | VPS much smaller | **DEFER** | |
| `frontend/src/lib/api/users.ts` | divergent | **DEFER** | |

## ABSENT (OK candidates)

Includes: `.env.prod.example`, DEC-020 lab auth doc, `rate_limit.py`, `test_rate_limit.py`, `deploy/Caddyfile`, deploy README/SMOKE, backup script, evidence MDs, seed SQL, ReportsView, UsersManagement, `roles.ts` — subject to Security (env/docs exposure) and Deploy reviews.

## A-03 statement

**Not** “no path conflict.”  
**Recorded:** 13 EXISTS paths; **0** cleared as unconditional OK; **DEFER** dominates application surfaces.

## Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Tech Lead | Lab Operator | 2026-08-01 | **Accept evidence** — binding DEFER set |
