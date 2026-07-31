# Path Overlap — VPS-only paths vs Batch-1 SoT (G5 / C-07)

| Field | Value |
|---|---|
| Date | 2026-07-31 |
| SoT tip checked | `2bf779d136a96c1c167abbacb51bf6e9a215791f` (`origin/feature/cm-batch1-s2-persistence`) |
| VPS path set | Phase 0 §3.2 (28 unique paths) |
| Method | Path existence on SoT tip (`git cat-file -e <tip>:<path>`) |
| Status | **Evidence recorded — content diff review still required before pick** |

## Summary

| Class | Count | Meaning |
|---|---|---|
| ABSENT on SoT | 15 | New path on VPS side — no pre-existing SoT file at that path |
| EXISTS on SoT | 13 | Same path exists on Batch-1 tip — **textual/content conflict risk** |

## EXISTS on SoT (conflict review required before cherry-pick)

| Path | Related VPS SHA(s) |
|---|---|
| `.gitignore` | `96f52eb` |
| `backend/app/core/errors.py` | `41a0f48` |
| `backend/app/modules/auth/router.py` | `41a0f48` |
| `backend/app/modules/users/repository.py` | `2f1348a` |
| `backend/app/modules/users/service.py` | `2f1348a` |
| `backend/tests/test_users.py` | `2f1348a` |
| `docker-compose.prod.yml` | `96f52eb` |
| `frontend/src/app/(app)/reports/page.tsx` | `a476ebf` |
| `frontend/src/app/(app)/users/page.tsx` | `a476ebf` |
| `frontend/src/features/reports/index.ts` | `a476ebf` |
| `frontend/src/features/users/index.ts` | `a476ebf` |
| `frontend/src/lib/api/index.ts` | `a476ebf` |
| `frontend/src/lib/api/users.ts` | `a476ebf` |

## ABSENT on SoT (new on VPS)

| Path | Related VPS SHA(s) |
|---|---|
| `.env.prod.example` | `96f52eb` |
| `27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md` | `96f52eb` |
| `backend/app/core/rate_limit.py` | `41a0f48` |
| `backend/tests/test_rate_limit.py` | `41a0f48` |
| `deploy/Caddyfile` | `96f52eb` |
| `deploy/README.md` | `96f52eb`, `2f1348a` |
| `deploy/SMOKE_UAT_2026-07-31.md` | `96f52eb`, `2f1348a` |
| `deploy/backup-postgres.sh` | `96f52eb` |
| `deploy/evidence/backup-verify-20260731.md` | `a476ebf` |
| `deploy/evidence/hardening-20260731.md` | `41a0f48` |
| `deploy/evidence/restore-drill-20260731.md` | `ad4a373` |
| `deploy/seed-lab-master-data.sql` | `2f1348a` |
| `frontend/src/features/reports/ReportsView.tsx` | `a476ebf` |
| `frontend/src/features/users/UsersManagement.tsx` | `a476ebf` |
| `frontend/src/lib/api/roles.ts` | `a476ebf` |

## Statement for A-03

**Not** “no path conflict.”  

**Recorded:** 13 paths exist on both trees; content-level merge risk remains Open until Tech Lead reviews diffs against SoT tip `2bf779d` and signs Approval Matrix row “Overlap VPS ↔ Batch-1”.

## Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Tech Lead | _pending_ | | Accept evidence / Request content diffs / Reject |
