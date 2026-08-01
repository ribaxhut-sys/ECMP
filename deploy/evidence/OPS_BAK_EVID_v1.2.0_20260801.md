# OPS-BAK-001 Evidence — ECMP v1.2.0-rc.1 pre-release dump

| Field | Value |
|---|---|
| ID | OPS-BAK-EVID-v1.2.0-rc.1-20260801 |
| Procedure | OPS-BAK-001 |
| Date (UTC) | 2026-08-01T08:32:02Z |
| Candidate | `v1.2.0-rc.1` @ `6890f50d8243ba30589a3d88f0c0efcef791ce01` |
| Operator | Production Readiness Team (lab) |
| Result | **PASS** (lab dump sealed) |

## Artifact

| Item | Value |
|---|---|
| Path (ops-managed, git-ignored) | `backups/ecmp_20260801T083202Z_v1.2.0-rc.1.dump` |
| Format | PostgreSQL custom `-Fc` (binary-safe; container write + `docker cp`) |
| SHA-256 | `31a4fa582f99d0e851fe4ae689dd36bae81fd43f39cfded65e714f1bb0457b6a` |
| Checksum file | `backups/ecmp_20260801T083202Z_v1.2.0-rc.1.dump.sha256` |
| Alembic at dump | `0046_cm_case_management` |
| Alembic note | `backups/ecmp_20260801T083202Z_v1.2.0-rc.1.alembic.txt` |

## Honesty

- This dump satisfies REL-SEC-001 §3.5 **lab / pre-decision backup evidence** for candidate `v1.2.0-rc.1`.
- It does **not** authorize production cutover while AuthN/OIDC gates FAIL.
- RPO remains time-since-last-dump (WAL/PITR out of scope).
- Secrets / sealed config backup: host `.env.prod` remains operator-managed (git-ignored); not duplicated into git.

## Related

- `15 Operations Runbook/ECMP_Backup_Operations_Guide_v1.0.md`
- `deploy/evidence/OPS_RCV_EVID_v1.2.0_20260801.md`
