# ECMP Production Deployment Guide (R6-03 + B3)

| Field | Value |
|---|---|
| ID | DEP-GUIDE-001 |
| Version | 1.1.0 |
| Date | 2026-07-28 |
| Branch | `release/v1.0.0` |
| Scope | Configuration, environment, TLS reverse proxy, startup validation, Compose readiness |
| Out of scope | SMTP, observability, K8s, load balancing, Identity/RBAC/Queue/Complaint feature changes |

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

Guards include: missing/weak DB password, invalid JWT, bad/localhost/HTTP origins (production), misaligned reset URL, `DEBUG=true`, `EMAIL_PROVIDER=logging`, unsupported `JWT_ALGORITHM`.

## CORS & cookies

| Setting | Production behavior |
|---|---|
| `ALLOWED_ORIGINS` | Explicit https origins; credentials allowed |
| Refresh cookie | `HttpOnly`; `Secure=true`; `SameSite=Lax`; path `/api/v1/auth` |
| Docs (`/docs`) | Disabled |
| Trusted hosts | Enforced via `ALLOWED_HOSTS` |
| Forwarded headers | Trusted from reverse proxy (`FORWARDED_ALLOW_IPS`) |

## Post-deploy smoke

See [`STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md) and [`TLS_REVERSE_PROXY.md`](./TLS_REVERSE_PROXY.md). Minimum:

- `GET https://<domain>/ready` → startup + database ok
- HTTP→HTTPS redirect
- Login / refresh / logout over HTTPS
- Frontend loads against `NEXT_PUBLIC_API_BASE_URL`

## Related procedures

- [`TLS_REVERSE_PROXY.md`](./TLS_REVERSE_PROXY.md) — **B3 official reference**
- [`STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md)
- [`UPGRADE_PROCEDURE.md`](./UPGRADE_PROCEDURE.md)
- [`../releases/ROLLBACK_v1.0.0.md`](../releases/ROLLBACK_v1.0.0.md)
- [`../deployment-checklist.md`](../deployment-checklist.md)
