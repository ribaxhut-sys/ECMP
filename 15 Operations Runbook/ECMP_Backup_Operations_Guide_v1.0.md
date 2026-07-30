# ECMP Backup Operations Guide

| Field | Value |
|---|---|
| ID | OPS-BAK-001 |
| Version | 1.0.1 |
| Date | 2026-07-30 |
| Revision | P6-003 Claude Independent Review fixes (audit table names; binary-safe `-Fc`) |
| Owner | Operations Lead |
| Reviewer | DevOps Lead / Security Architect |
| Approver | Operations Lead |
| Status | 🟢 Active (documentation / operational readiness) |
| Task | TASK-PLATFORM-SECMIG-P6-003 |
| Stack | Foundation: root `backend/`, `frontend/`, repo-root Compose |
| Related | OPS-DR-001, OPS-RST-001, OPS-RCV-001, OPS-SEC-SEC-001, DEC-005, ADR-010 |

Supersedes the Draft content previously titled *ECMP Backup Strategy v0.1* (same ID).
This guide is **documentation and operator procedure only**. It does **not** authorize
backup schedulers, WAL shipping, PITR, Vault, KMS, HA, or replication in this task.

## 1. Scope

| Environment | Backup required? | Rationale |
|---|---|---|
| DEV (local) | **No** | Synthetic/disposable; recreate via Compose + Alembic |
| CI | **No** | Ephemeral service containers |
| Staging / Production (foundation Compose) | **Yes (manual)** | Pre-upgrade / pre-risk-change dumps; see §3 |
| Shared SIT/UAT (ADR-010 full baseline) | **Yes** | Same manual baseline until automation is separately authorized |

**Canonical paths:** dumps and operator notes live under ops-managed `backups/` (git-ignored).
Application code: root `backend/`. Do not use `implementation/backend` as the production SoT.

## 2. Recovery objectives (honest)

| Objective | Target (DEC-005) | **Current capability** (P6-003) |
|---|---|---|
| **RTO** | **4 hours** | Achievable with manual restore + foundation Compose redeploy **if** a known-good dump and sealed config/secrets exist. Must be **measured** on each drill (OPS-RCV-001). |
| **RPO** | **15 minutes** (requires WAL/PITR — **out of scope / not implemented**) | **Current RPO = time since last successful logical dump** (typically pre-upgrade / ad-hoc). Operators **must not** claim DEC-005 RPO until WAL/PITR is authorized and verified. |

Record the dump watermark (`UTC timestamp` + SHA-256) on every backup so the actual RPO for an incident is computable.

## 3. Database backup

### 3.1 What to protect

Priority (aligned with OPS-DR-001):

1. PostgreSQL data (complaint/case domain, platform **`audit_logs`**, legacy **`audit_logs_legacy`**, outbox, notes, notification log, etc.)
2. Alembic revision identity of the dump (must match app tag used on restore)
3. Dump integrity (checksum)

Both audit tables are append-only (**BR-CP-03** / BR-008). Backups must not truncate history.

| Table | Role | Timestamp column for verification |
|---|---|---|
| **`audit_logs`** | Platform AuditService (canonical for restore gates / security taxonomy) | **`created_at`** |
| **`audit_logs_legacy`** | Legacy Complaint/Auth/Resolution writers only | **`occurred_at`** |

Do **not** write `audit_log` (singular) — that name is obsolete and ambiguous.

### 3.2 Standard format (custom `-Fc`, binary-safe)

Prefer **custom format** for drills and shared-env recoveries.

**Do not** pipe `-Fc` output through PowerShell `>` / `Out-File` / text redirection — that re-encodes bytes and **corrupts** the dump. Write the file **inside** the Postgres container, then `docker compose cp` to the host.

```powershell
$ts = Get-Date -Format yyyyMMdd_HHmmss
New-Item -ItemType Directory -Force -Path backups | Out-Null
$out = "backups/ecmp_${ts}.dump"

# 1) Binary dump written inside the container (uses container env POSTGRES_*)
docker compose -f docker-compose.prod.yml exec -T postgres `
  sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/ecmp_backup.dump'

# 2) Copy binary artifact to host (no text encoding)
docker compose -f docker-compose.prod.yml cp postgres:/tmp/ecmp_backup.dump $out

# 3) Checksum — store hash string only (ASCII)
(Get-FileHash -Path $out -Algorithm SHA256).Hash |
  Set-Content -Path "$out.sha256" -Encoding ascii

# Optional cleanup inside container
docker compose -f docker-compose.prod.yml exec -T postgres rm -f /tmp/ecmp_backup.dump
```

Plain SQL dumps (default `pg_dump` text format, as in `docs/deployment/UPGRADE_PROCEDURE.md`) remain
acceptable for **pre-upgrade** operational backups — text redirection is valid **only** for plain SQL,
not for `-Fc`. Record format in the evidence note.

| Field | Record |
|---|---|
| Path | ops-managed `backups/...` |
| Format | `-Fc` (preferred) or plain `.sql` |
| SHA-256 | Adjacent `.sha256` or ticket attachment |
| `IMAGE_TAG` / git tag | App version dump is compatible with |
| Alembic head (optional note) | From running env before dump |
| UTC time | Watermark for RPO calculation |

### 3.3 When to take a dump (minimum)

- Before every production/staging upgrade that may run Alembic
- Before destructive maintenance (role password change affecting volume, volume migrate)
- Before shared-env restore drills
- After Security Officer request following a compromise assessment (forensic preserve — do not overwrite)

### 3.4 Explicit non-goals (this task)

- No cron / GitHub Actions backup jobs
- No WAL archiving / PITR
- No cloud bucket provisioning scripts in-repo

## 4. Configuration backup

| Artifact | Policy |
|---|---|
| Host `.env` (runtime) | **Never commit**. Keep a **sealed copy** outside the git tree (org secret store / encrypted offline media). Copy only after `validate-production-config.py` PASS. |
| `.env.example` / `.env.production.example` | Templates only — **not** a backup of production values. |
| Compose files | Versioned in git (root `docker-compose.prod.yml`, etc.). Pin checkout tag with the dump. |
| TLS / Caddy data volume | Optional: back up `ecmp_prod_caddy_data` when host rebuild must preserve ACME state (`docs/deployment/TLS_REVERSE_PROXY.md`). |
| IdP production config | **IdP-operated** — not ECMP repo backup. Local DEV Keycloak pack under `implementation/infrastructure` is **Historical / DEV-only**. |

**Config backup checklist (operator):**

1. Export variable **names** + non-secret structure to the change ticket (never paste secret values).
2. Store full `.env` only in the approved sealed store.
3. Note `IMAGE_TAG`, `APP_VERSION`, `ECMP_DOMAIN`, `ENVIRONMENT`, `ECMP_AUTH_MODE`.
4. Re-validate after any restore: `python scripts/validate-production-config.py --env-file .env --require-production`.

## 5. Secret backup policy

Source of truth for inventory: `backend/app/core/secrets.py` / OPS-SEC-SEC-001.

| Rule | Requirement |
|---|---|
| Storage | Secrets live in process env / git-ignored `.env` or org secret injection — **not** in git, tickets, or chat. |
| Sealed backup | Before rotation or emergency replace, ensure the **previous** values are recoverable from the approved sealed store (OPS-SEC-SEC-001 §5). |
| Database dumps | Treat dumps as **sensitive** (may contain PII / business data). Do **not** embed `JWT_SECRET_KEY` or plaintext passwords into dump filenames or companion plaintext notes. |
| Evidence | Record secret **names** changed and fingerprints per OPS-SEC-SEC-001 — never full values. |
| Out of scope | Vault / KMS product implementation (future). |

If `POSTGRES_PASSWORD` must change: take a DB dump first; keep env and Postgres role password in sync (OPS-SEC-SEC-001 §2).

## 6. Retention

| Class | Minimum retention (interim) | Notes |
|---|---|---|
| Pre-upgrade / pre-change logical dumps | **30 days** or until next **two** successful upgrades, whichever is longer | Ops-managed storage |
| Restore-drill artifacts | **90 days** (or until next shared drill supersedes) | May be synthetic; still checksum |
| Sealed `.env` / secret store versions | Per org secret-store policy; **≥ last two** known-good sets | Required for secret rollback |
| Incident / forensic dumps | Hold until Security Officer release | Do not auto-delete |

Compliance may extend these later; until then these minima apply for staging/production foundation deployments. DEV/CI: no retention obligation.

## 7. Encryption requirements

| Layer | Requirement |
|---|---|
| At rest (backup media) | Encrypt ops backup volume / sealed store (OS disk encryption, encrypted archive, or org equivalent). Plain dumps on unencrypted shared disks are **not** acceptable for staging/production. |
| In transit | Prefer dump capture on the host via local Compose exec; if copied off-box, use TLS or encrypted channel only. |
| Access control | Limit read access to Operations Lead / DevOps on-call / Security Officer as needed. |
| Git | Backup artifacts and `.env` **must not** be committed. |

Encryption product choice (BitLocker, LUKS, org CASB, etc.) is an ops environment decision — not implemented in this repository.

## 8. Relationship to future targets

| Item | Status |
|---|---|
| Daily automated `pg_dump` | **Future** (not this task) |
| WAL + PITR for DEC-005 RPO 15m | **Future** (not this task) |
| Off-box object storage automation | **Future** |

Until those land, operators communicate **current RPO capability** (§2) in incident reports.

## 9. Related

- `./ECMP_DR_BCP_Plan_v0.1.md` (OPS-DR-001)
- `./ECMP_Restore_Verification_Procedure_v0.1.md` (OPS-RST-001)
- `./ECMP_Recovery_Validation_Checklist_v1.0.md` (OPS-RCV-001)
- `./ECMP_Secret_Operations_Guide_v1.0.md` (OPS-SEC-SEC-001)
- `../docs/deployment/UPGRADE_PROCEDURE.md`
- `../docs/releases/ROLLBACK_v1.0.0.md`
- `../docs/deployment/STARTUP_CHECKLIST.md`
