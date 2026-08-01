# ECMP Secret Operations Guide

| Field | Value |
|---|---|
| ID | OPS-SEC-SEC-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Owner | DevOps Lead / Security Architect |
| Status | 🟢 Active (foundation stack) |
| Task | TASK-PLATFORM-SECMIG-P6-002 |
| Scope | Environment-sourced secrets for root `backend/` (DEP-001 §2) |
| Out of scope | Vault, KMS, automated schedulers (explicit non-goals) |

## 1. Inventory (foundation)

Source of truth: `backend/app/core/secrets.py` → `SECRET_INVENTORY`.

| Env var | Required | Notes |
|---|---|---|
| `JWT_SECRET_KEY` | Yes | HS256 lab/dual-mode tooling; ≥32 chars outside development |
| `POSTGRES_PASSWORD` | Yes* | Unless password embedded in `DATABASE_URL` |
| `DATABASE_URL` | Optional | Treat full DSN as secret if set |
| `PGADMIN_DEFAULT_PASSWORD` | Optional | Tools profile only; validated when set |

AuthN for staging/production is **`ECMP_AUTH_MODE=jwt`** (P6-001). OIDC client secrets at the IdP are **IdP-operated** (not in this inventory). Still rotate `JWT_SECRET_KEY` if leaked.

Never commit `.env`. Approved source: process environment / git-ignored `.env`.

## 2. Rotation (planned)

Use for routine credential change (no active breach).

1. **Announce** maintenance window if login disruption expected (HS256 invalidation for any remaining `dev`-mode tokens; jwt mode users depend on IdP).
2. **Generate**
   ```powershell
   # Example JWT secret
   openssl rand -hex 32
   # DB password: use org password manager / generator (≥8 chars, not denylist)
   ```
3. **Update** host `.env` (or secret injection used by Compose). Do not log plaintext.
4. **Validate before restart**
   ```powershell
   python scripts/validate-production-config.py --env-file .env --require-production
   docker compose -f docker-compose.prod.yml config
   ```
5. **Roll** backend (and postgres only if DB password changes — update Postgres role password in sync with env).
   ```powershell
   docker compose -f docker-compose.prod.yml up -d --no-deps backend
   # If POSTGRES_PASSWORD changed: follow DBA procedure to ALTER ROLE, then recreate/restart postgres consistently with volume — prefer planned change with dump first.
   ```
6. **Smoke:** `/live`, `/ready`, login (jwt), refresh/logout over HTTPS.
7. **Evidence:** ticket id, timestamp, validator PASS snippet (no secret values), image tag, operator id.

## 3. Emergency replacement (compromise)

Trigger: SEC-P3 in [`ECMP_Security_Operations_Runbook_v1.0.md`](./ECMP_Security_Operations_Runbook_v1.0.md).

1. Escalate **L2-SEC**; declare incident commander.
2. Generate **new** secrets (do not reuse).
3. Replace in the live secret source **immediately**; remove leaked copies (chat, tickets, old `.env` backups) under chain-of-custody.
4. Restart backend (and DB credentials path if DB secret leaked).
5. Run validator + smoke (section 2 steps 4–6). Prefer brief authenticated outage over continuing with leaked material.
6. If `POSTGRES_PASSWORD` leaked: assume data exposure risk; preserve audit/logs; Security Officer decides further forensics (no silent DB wipe).
7. IdP: if OIDC client secret / realm admin leaked, use IdP admin procedures (OPS-IDP-001 is **local DEV only** — production IdP follows org IdP runbook).
8. Evidence pack: old secret **fingerprints** only (e.g. length + last-4 if policy allows), never full values; list of systems that had the secret.

## 4. Validation

| Gate | Command / check |
|---|---|
| CLI | `python scripts/validate-production-config.py --env-file .env [--require-production]` |
| Startup | Backend lifespan `validate_runtime_config` — weak/missing secrets fail-fast outside development |
| Compose | `${JWT_SECRET_KEY:?}` / `${POSTGRES_PASSWORD:?}` / AuthN `${:?}` (P6) |
| Redaction | Logs/errors must not print secrets (`SecretRedactingFilter`); spot-check after rotate |

Staging/production also require `ECMP_AUTH_MODE=jwt` + OIDC URLs (not secrets, but deploy blockers).

## 5. Rollback

If new secret breaks the service (typo, postgres mismatch):

1. Restore **previous** secret values from the approved secret store / sealed backup (not from git).
2. `docker compose -f docker-compose.prod.yml up -d --no-deps backend` (and postgres if applicable).
3. Re-run validator + smoke.
4. If application image rollback is also required, follow [`../docs/releases/ROLLBACK_v1.0.0.md`](../docs/releases/ROLLBACK_v1.0.0.md) **after** secrets are consistent with the target release.

Do not “fix” production by setting `ECMP_AUTH_MODE=dev`.

## 6. Evidence collection (checklist)

- [ ] Incident / change ticket id
- [ ] UTC timestamps (start rotate / restart / smoke PASS)
- [ ] Which env vars changed (names only)
- [ ] Validator stdout (redacted)
- [ ] Compose project / `IMAGE_TAG` / `APP_VERSION`
- [ ] `GET /ready` result
- [ ] Auth smoke result (`auth_mode=jwt` in startup log for staging/production)
- [ ] Operator + approver

Store evidence outside the git repo if it may contain sensitive paths.

## 7. Key registry note

`backend/app/core/keys/` in-memory registry is **bookkeeping** for HS256 metadata. Effective HS256 material remains `JWT_SECRET_KEY` via Settings until a future wiring task. Manual `registry.rotate()` alone does **not** rotate production signing. Do not treat registry APIs as the secret-ops path.

## 8. Related

- [`../docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md`](../docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md)
- [`../docs/deployment/STARTUP_CHECKLIST.md`](../docs/deployment/STARTUP_CHECKLIST.md)
- [`./ECMP_Security_Operations_Runbook_v1.0.md`](./ECMP_Security_Operations_Runbook_v1.0.md)
- [`./ECMP_Backup_Operations_Guide_v1.0.md`](./ECMP_Backup_Operations_Guide_v1.0.md) — sealed config/secret backup policy (P6-003)
- [`./ECMP_Restore_Verification_Procedure_v0.1.md`](./ECMP_Restore_Verification_Procedure_v0.1.md) — secret restore during recovery
- [`./ECMP_Recovery_Validation_Checklist_v1.0.md`](./ECMP_Recovery_Validation_Checklist_v1.0.md)
