# Restore Drill Evidence — Sprint-09

| Field | Value |
|---|---|
| ID | OPS-RST-EVID-20260722 |
| Procedure | OPS-RST-001 |
| Date (UTC) | 2026-07-22 |
| Operator | Sprint-09 implementation (local DEV scratch) |
| Result | **PASS** (historical procedure proof) |
| Naming note | **Historical** — dual-table model (`audit_logs` / `audit_logs_legacy`) post-dates this drill |

## 1. Scope and honesty

This is a **DEV scratch restore drill** executed against disposable PostgreSQL 16 containers
(host ports `5433` / `5434`) because:

- Shared SIT/UAT is not provisioned (ADR-010 gated on ADR-007 target auth).
- Host port `5432` was already bound by an unrelated local container (`digitalagent-postgres`).
- OPS-BAK-001: DEV data is synthetic; the drill proves **procedure + tooling**, not PROD RPO/RTO.

A second drill on the shared environment remains **required** at ADR-010 activation
(OPS-DR-001) before shared UAT entry — use OPS-RCV-001 with foundation probes `/live` `/ready`,
platform table **`audit_logs`** (`created_at`), and explicit **`audit_logs_legacy`**
(`occurred_at`) when in scope.

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
3. Seeded synthetic row `CASE-DRILL09` + one audit row (`case.create`, actor `ops.drill`).
4. Recorded pre-dump watermarks: `cases=1`, audit rows `=1`, `max(occurred_at)=2026-07-22T11:49:16.003323+00:00`.
5. `pg_dump -U ecmp -d ecmp -Fc` → artifact + SHA-256 (scratch containers; binary path used in drill).
6. Provisioned empty target DB `ecmp_restored`; `pg_restore --clean --if-exists`.
7. Compared SRC vs DST counts, max timestamp, Alembic `version_num`, and case row.

## 4. Verification results (historical mapping)

> **Historical probe note:** Foundation ECMP API probes are now `GET /live` and `GET /ready`
> (P6-003). This DEV scratch drill skipped HTTP entirely; the next shared-env drill must use
> `/live` and `/ready` per OPS-RCV-001 — not legacy `/health` paths.

> **Historical audit naming:** Checks below used the singular label `audit_log` / column
> `occurred_at` in contemporaneous notes. Under the current schema (TASK-031 / `0019_audit`),
> that verification maps to **`audit_logs_legacy.occurred_at`**. Do **not** treat it as
> platform **`audit_logs.created_at`**. Future drills must verify both tables explicitly when
> both exist in the dump.

| Check | Result |
|---|---|
| Audit row count SRC = DST (**now: `audit_logs_legacy`**) | PASS (`1` = `1`) |
| `max(occurred_at)` SRC = DST (**legacy column**) | PASS (`2026-07-22T11:49:16.003323+00:00`) |
| Append-only integrity | PASS — restore only; no UPDATE/DELETE tooling on audit rows |
| Alembic revision | PASS (`0003` on SRC and DST) |
| Case smoke row present | PASS (`CASE-DRILL09`, `REGISTERED`) |
| Application HTTP probes | **Skipped** — documented; mandatory for shared-env drill via `/live` `/ready` |
| RTO wall-clock | Dump+restore+verify ≈ **6 s** on local Docker (not comparable to 4h shared-env RTO target) |

## 5. Sign-off

| Role | Status |
|---|---|
| Operations (drill executor) | Signed — PASS 2026-07-22 |
| Security Officer (audit tables) | Deferred to shared-env drill (synthetic DEV data only) |

## Related

- `../ECMP_Restore_Verification_Procedure_v0.1.md` (OPS-RST-001)
- `../ECMP_Backup_Operations_Guide_v1.0.md` (OPS-BAK-001)
- `../ECMP_Recovery_Validation_Checklist_v1.0.md` (OPS-RCV-001)
- `../ECMP_DR_BCP_Plan_v0.1.md` (OPS-DR-001)
