# Restore Drill Evidence — Sprint-09

| Field | Value |
|---|---|
| ID | OPS-RST-EVID-20260722 |
| Procedure | OPS-RST-001 |
| Date (UTC) | 2026-07-22 |
| Operator | Sprint-09 implementation (local DEV scratch) |
| Result | **PASS** |

## 1. Scope and honesty

This is a **DEV scratch restore drill** executed against disposable PostgreSQL 16 containers
(host ports `5433` / `5434`) because:

- Shared SIT/UAT is not provisioned (ADR-010 gated on ADR-007 target auth).
- Host port `5432` was already bound by an unrelated local container (`digitalagent-postgres`).
- OPS-BAK-001: DEV data is synthetic; the drill proves **procedure + tooling**, not PROD RPO/RTO.

A second drill on the shared environment remains **required** at ADR-010 activation
(OPS-DR-001 §7) before shared UAT entry.

## 2. Artifacts

| Artifact | Path / value |
|---|---|
| Logical dump (`pg_dump -Fc`) | `./ecmp_sprint09_drill.dump` |
| SHA-256 | `0BAFAD6D0D7380252E000054F7CC1E71F2F49E78D29C900ABC50450C7BF56AD5` |
| Source container | `ecmp-restore-drill-src` (postgres:16-alpine, DB `ecmp`) |
| Target container | `ecmp-restore-drill-dst` (postgres:16-alpine, DB `ecmp_restored`) |

## 3. Steps executed

1. Started scratch Postgres 16; waited for `pg_isready`.
2. Applied Alembic migrations to head (`0003`) via `ECMP_DATABASE_URL=...@localhost:5433/ecmp`.
3. Seeded synthetic row `CASE-DRILL09` + one `audit_log` (`case.create`, actor `ops.drill`).
4. Recorded pre-dump watermarks: `cases=1`, `audit_log=1`, `max(occurred_at)=2026-07-22T11:49:16.003323+00:00`.
5. `pg_dump -U ecmp -d ecmp -Fc` → artifact + SHA-256.
6. Provisioned empty target DB `ecmp_restored`; `pg_restore --clean --if-exists`.
7. Compared SRC vs DST counts, `max(occurred_at)`, Alembic `version_num`, and case row.

## 4. Verification results (OPS-RST-001 §3–§4)

| Check | Result |
|---|---|
| `audit_log` row count SRC = DST | PASS (`1` = `1`) |
| `max(occurred_at)` SRC = DST | PASS (`2026-07-22T11:49:16.003323+00:00`) |
| Append-only integrity | PASS — restore only; no UPDATE/DELETE tooling run against `audit_log` |
| Alembic revision | PASS (`0003` on SRC and DST) |
| Case smoke row present | PASS (`CASE-DRILL09`, `REGISTERED`) |
| Application HTTP probes | **Skipped** — no app writers attached to scratch DBs for this drill (documented); probes remain mandatory for shared-env drill |
| RTO wall-clock | Dump+restore+verify ≈ **6 s** on local Docker (not comparable to 4h shared-env RTO target) |

## 5. Sign-off

| Role | Status |
|---|---|
| Operations (drill executor) | Signed — PASS 2026-07-22 |
| Security Officer (`audit_log`) | Deferred to shared-env drill (synthetic DEV data only) |

## Related

- `../ECMP_Restore_Verification_Procedure_v0.1.md` (OPS-RST-001)
- `../ECMP_Backup_Strategy_v0.1.md` (OPS-BAK-001)
- `../ECMP_DR_BCP_Plan_v0.1.md` (OPS-DR-001)
