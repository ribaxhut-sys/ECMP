# Phase 5 Execution Evidence — Limited Scope (GO WITH WAIVERS)

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| RAB | `Phase4_RAB_GO_WITH_WAIVERS_20260801.md` |
| Base SHA | `2bf779d136a96c1c167abbacb51bf6e9a215791f` |
| Release branch | `release/cm-batch1-vps-sync` |
| Method | Path checkout of **ABSENT** artefacts only (not Mixed cherry-pick bulk) |

## Included (ABSENT / evidence / infra lab)

- `.env.prod.example`
- `27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md`
- `backend/app/core/rate_limit.py` + `backend/tests/test_rate_limit.py` (**dormant** until DEFER `auth/router` surgical patch)
- `deploy/Caddyfile`, `deploy/README.md`, `deploy/SMOKE_UAT_2026-07-31.md`, `deploy/backup-postgres.sh`
- Lab + governance evidence under `deploy/evidence/` (Phase 0–5, APPROVED 20260801, RAB GO WITH WAIVERS)

## Explicitly excluded (DEFER / risk)

- `docker-compose.prod.yml` overwrite (SoT already has richer prod compose)
- `backend/app/modules/users/**`, `auth/router.py`, `errors.py` overwrite
- `frontend/src/lib/api/**` overwrite; Users/Reports UI that needs those APIs
- `deploy/seed-lab-master-data.sql` (data risk without mandatory restore window)

## CP checklist

| CP | Result |
|---|---|
| CP-1 Before branch | PASS — base locked, RAB GO WITH WAIVERS |
| CP-2 After port | PASS — DEFER paths untouched vs base |
| CP-3 Smoke | Partial — rate_limit unit not wired; no live deploy in this step |
| CP-4 Before PR | PASS — SHA register this file |
| CP-5 Before merge | Awaiting review — Board/maintainers |

## SHA register

| Item | Value |
|---|---|
| Base | `2bf779d136a96c1c167abbacb51bf6e9a215791f` |
| Release tip | bdf47aad440e633e85c8ba179c335b284d4f195e |
| PR URL | https://github.com/ribaxhut-sys/ECMP/pull/2 |
