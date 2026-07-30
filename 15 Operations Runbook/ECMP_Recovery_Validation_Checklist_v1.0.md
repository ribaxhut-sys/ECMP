# ECMP Recovery Validation Checklist

| Field | Value |
|---|---|
| ID | OPS-RCV-001 |
| Version | 1.0.1 |
| Date | 2026-07-30 |
| Owner | Operations Lead |
| Reviewer | DevOps Lead / Security Officer |
| Approver | Operations Lead |
| Status | 🟢 Active |
| Task | TASK-PLATFORM-SECMIG-P6-003 |
| Revision | P6-003 review: `audit_logs.created_at` / `audit_logs_legacy.occurred_at` |
| Stack | Foundation: root `backend/`, repo-root Compose |

Operational checklist for restore drills and live recovery validation.
Does **not** implement schedulers, WAL, PITR, Vault, KMS, HA, or replication.

Use with:

- [`./ECMP_Backup_Operations_Guide_v1.0.md`](./ECMP_Backup_Operations_Guide_v1.0.md) (OPS-BAK-001)
- [`./ECMP_Restore_Verification_Procedure_v0.1.md`](./ECMP_Restore_Verification_Procedure_v0.1.md) (OPS-RST-001)
- [`./ECMP_DR_BCP_Plan_v0.1.md`](./ECMP_DR_BCP_Plan_v0.1.md) (OPS-DR-001)

## 0. Drill identity

| Field | Value |
|---|---|
| Ticket / drill id | |
| Environment | DEV scratch / staging / production (circle) |
| Operator | |
| Approver | |
| Security Officer (shared env) | |
| UTC start | |
| UTC end | |

## 1. Pre-conditions

- [ ] Incident / maintenance declared (shared) **or** scratch scope documented (DEV)
- [ ] Writers stopped per OPS-SHDN-001 (if app attached)
- [ ] Dump artifact identified; format noted (`-Fc` binary-safe per OPS-BAK-001, or plain SQL)
- [ ] For `-Fc`: artifact produced via container file + `docker compose cp` (not PowerShell `>` on binary)
- [ ] SHA-256 verified against recorded value
- [ ] Sealed `.env` / secrets available for target release
- [ ] Target `IMAGE_TAG` / git tag pinned to dump compatibility
- [ ] Ops backup media meets encryption / access policy (OPS-BAK-001 §7)

## 2. Restore validation

- [ ] Postgres 16 target ready (`pg_isready` / Compose healthy)
- [ ] Restore completed without unreviewed errors
- [ ] `alembic current` matches expected app migration head
- [ ] `audit_logs` row count documented (vs backup note)
- [ ] `audit_logs` `max(created_at)` documented
- [ ] No UPDATE/DELETE tooling used against `audit_logs`
- [ ] If in scope: `audit_logs_legacy` row count + `max(occurred_at)` documented (explicit legacy table)
- [ ] No UPDATE/DELETE tooling used against `audit_logs_legacy` (when checked)
- [ ] Config restored + `python scripts/validate-production-config.py --env-file .env [--require-production]` **PASS**
- [ ] Secrets consistent (DB role ↔ `POSTGRES_PASSWORD` if applicable)

## 3. Smoke tests (foundation probes)

Staging/production (HTTPS):

- [ ] `GET https://<ECMP_DOMAIN>/live` → 200
- [ ] `GET https://<ECMP_DOMAIN>/ready` → 200 (startup + database ok)
- [ ] Backend log: expected `ENVIRONMENT` + `auth_mode` (jwt for staging/production)
- [ ] Login / refresh smoke (authorized test account)
- [ ] Critical path create/get (complaint/case) succeeds
- [ ] No secrets in logs / tickets

Local DEV alternative: `http://127.0.0.1:8000/live` and `/ready`.

**Do not** use legacy application probes `/health` or `/health/ready` for foundation ECMP API validation.

## 4. RPO verification

| Field | Value |
|---|---|
| Dump watermark (UTC) | |
| Incident / cutover time (UTC) | |
| **Measured RPO** (duration) | |
| DEC-005 target RPO | 15 minutes (**not** claimed until WAL/PITR exists) |
| Honest statement | Current capability = time since last logical dump (OPS-BAK-001) |

- [ ] Measured RPO recorded in evidence
- [ ] Data gap communicated to stakeholders / reconciliation owner if non-zero

## 5. RTO measurement

| Field | Value |
|---|---|
| T0 — writers stopped / decision to restore (UTC) | |
| T1 — service open / smoke PASS (UTC) | |
| **Measured RTO** | |
| DEC-005 target RTO | **4 hours** |
| Pass vs target? | Yes / No / N/A (DEV scratch not comparable) |

- [ ] Wall-clock measured
- [ ] Lessons logged if RTO > 4h on shared/prod drill

## 6. Evidence checklist

- [ ] Ticket id
- [ ] Timestamps (T0/T1) and measured RTO/RPO
- [ ] Dump path + SHA-256
- [ ] Alembic revision
- [ ] `audit_logs` metrics (`count`, `max(created_at)`) + SO sign-off (required on shared env)
- [ ] `audit_logs_legacy` metrics if in scope (`count`, `max(occurred_at)`)
- [ ] Validator output (redacted)
- [ ] `/live` + `/ready` results
- [ ] Auth + functional smoke results
- [ ] Operator + approver signatures
- [ ] Evidence stored in ops location (not git if sensitive)

Reference DEV evidence pack (historical PASS, HTTP skipped):
`./evidence/restore-drill-20260722/README.md`

## 7. Exit criteria

| Gate | Shared env / UAT entry | DEV scratch |
|---|---|---|
| Restore + audit checks | Required | Required for procedure proof |
| HTTP `/live` `/ready` + auth smoke | **Required** | Optional if documented skip |
| SO sign-off on `audit_logs` | **Required** | Deferred OK if synthetic |
| SO sign-off on `audit_logs_legacy` (if in scope) | Required when checked | Deferred OK if synthetic |
| RTO ≤ 4h | **Required** (or exception filed) | Not claimed against DEC-005 |
| RPO honesty statement | **Required** | Required |

Shared-env drill **PASS** is still a gate before shared UAT (OPS-DR-001 / DEP-CHK-001).

## Related

- `../docs/deployment/STARTUP_CHECKLIST.md`
- `../docs/deployment/PRODUCTION_DEPLOYMENT_GUIDE.md`
- `../docs/releases/ROLLBACK_v1.0.0.md`
- `./ECMP_Secret_Operations_Guide_v1.0.md`
