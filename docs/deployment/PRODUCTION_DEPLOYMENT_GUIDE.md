# ECMP Production Deployment Guide (R6-03 + B3)

| Field | Value |
|---|---|
| ID | DEP-GUIDE-001 |
| Version | 1.2.0 |
| Date | 2026-07-30 |
| Branch | `release/v1.0.0` |
| Scope | Configuration, environment, TLS reverse proxy, startup validation, Compose readiness, smoke/rollback verification |
| Out of scope | SMTP, observability product, K8s, load balancing, Identity/RBAC/Queue/Complaint feature changes |
| Related | SECMIG-P6-001, SECMIG-P6-002, SECMIG-P6-005 |
| Hub | [`./README.md`](./README.md) (DEP-HUB-001) |

**Cutover precedence:** REL-SEC-001 → DEP-CHK-V1 → START-CHK-001.
Do not use Historical DEP-CHK-001 for foundation production cutover.

## Architecture (deployable unit)

**Local / foundation Compose** (`docker-compose.yml`) — developer convenience; publishes app ports:

```text
Browser → Frontend (:3000) → Backend (:8000) → PostgreSQL
```

**Production reference** (`docker-compose.prod.yml`) — Release Blocker B3:

```text
Browser → Caddy (:443 TLS) → Frontend / Backend (internal) → PostgreSQL (internal)
```

- TLS termination: **Caddy** (recommended) or **Nginx** (alternative) — see [`TLS_REVERSE_PROXY.md`](./TLS_REVERSE_PROXY.md).
- Only the reverse proxy publishes host ports (80/443).
- Redis: **not used**.
- Object storage: local filesystem via System Settings (not Compose volume for blobs beyond DB).

## Prerequisites

1. Docker Engine + Compose v2+
2. Checkout release branch/tag
3. Secrets available (vault or secure `.env`, never committed)
4. DNS A/AAAA for `ECMP_DOMAIN` (production ACME)
5. Postgres backup taken before upgrade (see Upgrade / Rollback)
6. Config validation PASS:

```powershell
python scripts/validate-production-config.py --env-file .env --require-production
```

## Production `.env` checklist (minimum)

| Variable | Example shape |
|---|---|
| `ECMP_DOMAIN` | `ecmp.example.com` |
| `ACME_EMAIL` | `ops@example.com` |
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `ECMP_AUTH_MODE` | `jwt` (required; SECMIG-P6-001) |
| `ECMP_ENV` | `shared` |
| `OIDC_ISSUER` | IdP realm issuer URL |
| `OIDC_AUDIENCE` | `ecmp-api` |
| `OIDC_JWKS_URL` | IdP JWKS endpoint |
| `POSTGRES_PASSWORD` | strong unique secret |
| `JWT_SECRET_KEY` | `openssl rand -hex 32` |
| `ALLOWED_ORIGINS` | `https://ecmp.example.com` |
| `ALLOWED_HOSTS` | `ecmp.example.com,backend` |
| `PASSWORD_RESET_FRONTEND_BASE_URL` | `https://ecmp.example.com` |
| `EMAIL_PROVIDER` | `noop` |
| `NEXT_PUBLIC_API_BASE_URL` | `https://ecmp.example.com` |
| `FORWARDED_ALLOW_IPS` | `*` (prod compose; backend not published) |
| `IMAGE_TAG` | `v1.0.0` (or RC) |

Templates: `.env.production.example` (repo root), full matrix [`ENVIRONMENT_VARIABLE_REFERENCE.md`](./ENVIRONMENT_VARIABLE_REFERENCE.md).

## Deploy procedure (production + TLS)

```powershell
# 1. Checkout
git fetch --tags
git checkout release/v1.0.0   # or release tag

# 2. Prepare env
copy .env.production.example .env
# edit .env — production values + ECMP_DOMAIN + ACME_EMAIL

# 3. Validate
python scripts\validate-production-config.py --env-file .env --require-production
docker compose -f docker-compose.prod.yml config

# 4. Build / start (proxy is the only public entrypoint)
$env:IMAGE_TAG = "v1.0.0"
$env:APP_VERSION = "1.0.0"
docker compose -f docker-compose.prod.yml up -d --build

# 5. Health via HTTPS (not host :8000)
curl.exe -fsS https://$env:ECMP_DOMAIN/live
curl.exe -fsS https://$env:ECMP_DOMAIN/ready
curl.exe -sI http://$env:ECMP_DOMAIN/   # expect redirect to https
```

Local foundation stack (no TLS) remains:

```powershell
docker compose up -d postgres backend frontend
```

## Startup validation (fail-fast)

On backend boot (`lifespan`), `validate_runtime_config()` refuses to start when issues exist.
Each issue reports:

1. **Variable**
2. **Problem**
3. **Suggested fix**

Guards include: missing/weak DB password, invalid JWT, bad/localhost/HTTP origins (production), misaligned reset URL, `DEBUG=true`, `EMAIL_PROVIDER=logging`, unsupported `JWT_ALGORITHM`, and **SECMIG-P6-001** (`ENVIRONMENT=staging|production` ⇒ `ECMP_AUTH_MODE=jwt` + OIDC vars).

Pre-deploy:

```powershell
python scripts\validate-production-config.py --env-file .env --require-production
docker compose -f docker-compose.prod.yml config
```

Confirm validator prints `ECMP_AUTH_MODE=jwt` and OIDC fields `set`.

## CORS & cookies

| Setting | Production behavior |
|---|---|
| `ALLOWED_ORIGINS` | Explicit https origins; credentials allowed |
| Refresh cookie | `HttpOnly`; `Secure=true`; `SameSite=Lax`; path `/api/v1/auth` |
| Docs (`/docs`) | Disabled |
| Trusted hosts | Enforced via `ALLOWED_HOSTS` |
| Forwarded headers | Trusted from reverse proxy (`FORWARDED_ALLOW_IPS`) |

## Post-deploy smoke checklist

See [`STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md) and [`TLS_REVERSE_PROXY.md`](./TLS_REVERSE_PROXY.md).

| # | Check | Pass criteria |
|---|---|---|
| 1 | `GET https://<domain>/live` | 200 |
| 2 | `GET https://<domain>/ready` | 200; startup + database ok |
| 3 | HTTP → HTTPS | Redirect |
| 4 | HSTS / app security headers | Present on HTTPS |
| 5 | Backend log | `application started` with `ENVIRONMENT=production` and `auth_mode=jwt` |
| 6 | Login / refresh / logout | Succeed over HTTPS (IdP jwt) |
| 7 | Frontend | Loads via `NEXT_PUBLIC_API_BASE_URL` |
| 8 | `/docs` | 404 in production |

On failure: [`STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md) triage, security playbooks `15 Operations Runbook/ECMP_Security_Operations_Runbook_v1.0.md`, or rollback below.

## Rollback verification

After executing [`../releases/ROLLBACK_v1.0.0.md`](../releases/ROLLBACK_v1.0.0.md) (prefer `docker compose -f docker-compose.prod.yml`):

| # | Check | Pass criteria |
|---|---|---|
| 1 | Images / git tag | Match rollback target |
| 2 | Config validator | PASS for the restored `.env` |
| 3 | `/live` + `/ready` | 200 via HTTPS |
| 4 | Auth smoke | Login works; log `auth_mode` expected for that release |
| 5 | No secret leakage | Logs scrubbed; no plaintext secrets in tickets |

Secret-only rollback (wrong rotate): `Secret Operations Guide` (`15 Operations Runbook/ECMP_Secret_Operations_Guide_v1.0.md`).

Backup & recovery (P6-003): `Backup Operations Guide` (`15 Operations Runbook/ECMP_Backup_Operations_Guide_v1.0.md`), `Restore Verification` (`15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md`), `DR/BCP` (`15 Operations Runbook/ECMP_DR_BCP_Plan_v0.1.md`), `Recovery Validation Checklist` (`15 Operations Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md`).

## Related procedures

- [`./README.md`](./README.md) — **deployment documentation hub**
- [`TLS_REVERSE_PROXY.md`](./TLS_REVERSE_PROXY.md) — **B3 official reference**
- [`STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md) (START-CHK-001)
- [`UPGRADE_PROCEDURE.md`](./UPGRADE_PROCEDURE.md)
- [`OPERATIONAL_SECURITY.md`](./OPERATIONAL_SECURITY.md)
- [`ENVIRONMENT_VARIABLE_REFERENCE.md`](./ENVIRONMENT_VARIABLE_REFERENCE.md) (ENV-REF-001 / P6-001)
- [`../releases/ROLLBACK_v1.0.0.md`](../releases/ROLLBACK_v1.0.0.md)
- [`../deployment-checklist.md`](../deployment-checklist.md) (DEP-CHK-V1)
- `16 Release Management/ECMP_Release_Security_Gate_v1.0.md` (REL-SEC-001)
- Security Operations Runbook (`15 Operations Runbook/ECMP_Security_Operations_Runbook_v1.0.md`)
