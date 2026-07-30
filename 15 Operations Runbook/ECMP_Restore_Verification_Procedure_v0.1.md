# ECMP Restore Verification Procedure

| Field | Value |
|---|---|
| ID | OPS-RST-001 |
| Version | 1.0.1 |
| Date | 2026-07-30 |
| Owner | Operations Lead |
| Reviewer | DevOps Lead / Security Officer |
| Approver | Operations Lead |
| Status | 🟢 Active (procedure) — shared-env drill still **Planned** |
| Task | TASK-PLATFORM-SECMIG-P6-003 |
| Revision | P6-003 review: `audit_logs` / `created_at`; binary-safe restore |
| Stack | Foundation: root `backend/`, repo-root Compose |
| Related | OPS-BAK-001, OPS-DR-001, OPS-RCV-001, OPS-SHDN-001, OPS-SEC-SEC-001 |

Documentation + drill evidence. First **shared-environment** restore drill remains
**required at least once before shared UAT** (OPS-DR-001) after ADR-010 baseline
activation. Sprint-09 executed a **DEV scratch** drill (see §9) — it does **not**
replace the shared-env drill.

**Probes (foundation):** use `GET /live` and `GET /ready` (not legacy `/health` paths).

## 1. Prerequisites

- Known-good logical dump + SHA-256 per OPS-BAK-001 (or disposable scratch Postgres 16 for DEV drills)
- Sealed config (`.env`) and secrets recoverable per OPS-SEC-SEC-001
- Application image/tag pinned and compatible with restored Alembic head (`backend/` entrypoint)
- Incident / maintenance window declared (shared env); stop writers per OPS-SHDN-001
- Access for SQL verification and HTTPS (or local) smoke tests — HTTP smoke **mandatory** on shared env

## 2. Database restore

1. Declare incident; **stop application writers** (OPS-SHDN-001) — prevent writes to an inconsistent DB.
2. Provision or verify target PostgreSQL 16 (foundation Compose service `postgres`).
3. Verify dump checksum: compare `(Get-FileHash $dump -Algorithm SHA256).Hash` to the contents of `$dump.sha256` (or recorded ticket value).
4. Restore (**binary-safe for `-Fc`** — do not PowerShell-redirect binary into `pg_restore`):
   - Custom format: copy dump into the container, then `pg_restore` from a container path.
   - Plain SQL: `psql` from a container path (or text redirect into `psql` is acceptable for `.sql` only).
5. If WAL/PITR were active (**not** current capability — Future only): replay to recovery target. **Skip** until implemented.
6. Run `alembic current` against the restored DB — revision must match the application tag to start.
7. **Verify `audit_logs`** (and optionally `audit_logs_legacy`) before opening traffic (§5).
8. Continue with config/secret alignment (§3–§4), then start app and validate (§6).

Example (production Compose; destructive — incident commander approval):

```powershell
docker compose -f docker-compose.prod.yml stop frontend backend
# ensure postgres healthy

$dump = "backups\ecmp_<ts>.dump"
$expected = (Get-Content -Path "$dump.sha256" -Raw).Trim()
$actual = (Get-FileHash -Path $dump -Algorithm SHA256).Hash
if ($actual -ne $expected) { throw "Checksum mismatch" }

# Binary-safe: copy into container, restore from path (no `<` redirect of -Fc)
docker compose -f docker-compose.prod.yml cp $dump postgres:/tmp/ecmp_restore.dump
docker compose -f docker-compose.prod.yml exec -T postgres `
  pg_restore --clean --if-exists -U $env:POSTGRES_USER -d $env:POSTGRES_DB /tmp/ecmp_restore.dump
docker compose -f docker-compose.prod.yml exec -T postgres rm -f /tmp/ecmp_restore.dump
```

Plain SQL alternative (text OK):

```powershell
docker compose -f docker-compose.prod.yml cp backups\ecmp_<ts>.sql postgres:/tmp/ecmp_restore.sql
docker compose -f docker-compose.prod.yml exec -T postgres `
  psql -U $env:POSTGRES_USER -d $env:POSTGRES_DB -f /tmp/ecmp_restore.sql
```

## 3. Configuration restore

1. Retrieve sealed `.env` for the **target** release from the approved store (not from git history).
2. Align Compose checkout / `IMAGE_TAG` with the dump’s recorded app version.
3. Validate:

```powershell
python scripts\validate-production-config.py --env-file .env --require-production
docker compose -f docker-compose.prod.yml config
```

4. Confirm `ENVIRONMENT` / `ECMP_AUTH_MODE=jwt` for staging/production (P6-001).
5. Do **not** “fix” AuthN by setting `ECMP_AUTH_MODE=dev` on shared/prod hosts.

## 4. Secret restore

Follow [`./ECMP_Secret_Operations_Guide_v1.0.md`](./ECMP_Secret_Operations_Guide_v1.0.md) §5:

1. Restore previous secret values from the sealed store if a bad rotation caused the outage.
2. Keep `POSTGRES_PASSWORD` consistent with the Postgres role if DB credentials are involved.
3. Restart backend (and postgres path only if DB secret changed).
4. Re-run validator + smoke (§6).

## 5. Audit table verification (mandatory)

### 5.1 Platform `audit_logs` (canonical gate)

| Check | Pass criteria |
|---|---|
| Row count vs last backup note | Explain any delta; do not silently drop newer rows |
| `max(created_at)` | ≥ last known backup watermark (or documented gap) |
| Append-only integrity | No UPDATE/DELETE tooling run against `audit_logs` during restore |

Example:

```sql
SELECT COUNT(*) AS n, MAX(created_at) AS max_created_at FROM audit_logs;
```

### 5.2 Legacy `audit_logs_legacy` (explicit — not interchangeable)

Legacy Complaint/Auth/Resolution writers use **`audit_logs_legacy`** with timestamp
**`occurred_at`**. Verify when the dump / domain requires it; **never** call this table
`audit_log` or treat it as the platform security audit SoT.

| Check | Pass criteria |
|---|---|
| Row count vs last backup note | Explain deltas |
| `max(occurred_at)` | ≥ watermark or documented gap |
| Append-only integrity | No UPDATE/DELETE tooling against `audit_logs_legacy` |

```sql
SELECT COUNT(*) AS n, MAX(occurred_at) AS max_occurred_at FROM audit_logs_legacy;
```

If a newer fragment of either table can be salvaged (future WAL/replica), **reconcile/attach** —
do not discard (OPS-DR-001). Report gaps to Security Officer.

## 6. Validation (application)

Foundation probes and smoke (staging/production via HTTPS):

| # | Check | Pass |
|---|---|---|
| 1 | `GET /live` → 200 | Liveness |
| 2 | `GET /ready` → 200 (`checks.startup` / `checks.database` ok) | Readiness + DB |
| 3 | Config validator PASS | Secure config baseline |
| 4 | Auth smoke (login / refresh) with `auth_mode=jwt` where required | AuthN |
| 5 | Authenticated create/get on critical complaint/case path | Functional smoke |
| 6 | Logs: no secret leakage; request ids present | OPS-LOG-001 |

Local DEV may use `http://127.0.0.1:8000/live` and `/ready`. Production: host `:8000` is
**not** published — use `https://$ECMP_DOMAIN/...`.

Full smoke tables: `../docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md`,
`../docs/deployment/STARTUP_CHECKLIST.md`.

Operational drill checklist (RPO/RTO/evidence): [`./ECMP_Recovery_Validation_Checklist_v1.0.md`](./ECMP_Recovery_Validation_Checklist_v1.0.md).

## 7. Rollback

| Situation | Action |
|---|---|
| Bad app deploy; schema still compatible | App-only rollback — [`../docs/releases/ROLLBACK_v1.0.0.md`](../docs/releases/ROLLBACK_v1.0.0.md) §A; **do not** restore DB |
| Migration / data corruption | Full rollback including DB dump — ROLLBACK §B; incident commander approval |
| Bad secret rotation only | OPS-SEC-SEC-001 §5 — restore sealed secrets; no DB restore |
| Restore itself fails validation | Keep writers stopped; escalate L3; preserve failed target for forensics |

Prefer **forward fix** over schema downgrade when possible (UPG-001).

## 8. Evidence collection

Minimum evidence pack (store outside git if sensitive):

- [ ] Incident / change ticket id
- [ ] UTC timestamps: stop writers / restore start / restore end / traffic open
- [ ] Dump path + SHA-256 + format (`-Fc` or plain)
- [ ] Recorded RPO gap (incident time − dump watermark)
- [ ] Measured RTO wall-clock vs 4h target
- [ ] `audit_logs`: count + `max(created_at)` before/after
- [ ] `audit_logs_legacy` (if in scope): count + `max(occurred_at)` before/after
- [ ] Alembic revision on restored DB
- [ ] Validator stdout (redacted)
- [ ] `/live` + `/ready` results
- [ ] Auth + functional smoke results
- [ ] Operator + approver (+ Security Officer for audit tables on shared env)

## 9. Sprint-09 DEV scratch drill result (2026-07-22)

| Field | Value |
|---|---|
| Evidence pack | `./evidence/restore-drill-20260722/README.md` |
| Dump SHA-256 | `0BAFAD6D0D7380252E000054F7CC1E71F2F49E78D29C900ABC50450C7BF56AD5` |
| Result | **PASS** — SRC/DST row checks + Alembic; HTTP smoke skipped |
| Security Officer sign-off | Deferred to shared-env drill |
| Follow-up | Complete OPS-RCV-001 on shared Postgres before UAT entry |

**Historical naming:** that drill pre-dates / does not reflect the current dual-table model.
Its recorded checks map to what is now **`audit_logs_legacy`** (`occurred_at`). Current
gates must use platform **`audit_logs`** (`created_at`) plus explicit legacy checks when needed.
Re-pin Alembic head to current `backend/` on the next shared drill.

## 10. Related

- `./ECMP_Backup_Operations_Guide_v1.0.md` (OPS-BAK-001)
- `./ECMP_DR_BCP_Plan_v0.1.md` (OPS-DR-001)
- `./ECMP_Recovery_Validation_Checklist_v1.0.md` (OPS-RCV-001)
- `./ECMP_Shutdown_Procedure_v0.1.md` (OPS-SHDN-001)
- `./ECMP_Secret_Operations_Guide_v1.0.md` (OPS-SEC-SEC-001)
- `./evidence/restore-drill-20260722/README.md`
- `../docs/deployment/UPGRADE_PROCEDURE.md`
- `../docs/releases/ROLLBACK_v1.0.0.md`
