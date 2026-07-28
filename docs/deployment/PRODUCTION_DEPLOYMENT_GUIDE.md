# ECMP Production Deployment Guide (R6-03)

| Field | Value |
|---|---|
| ID | DEP-GUIDE-001 |
| Version | 1.0.0 |
| Date | 2026-07-28 |
| Branch | `release/v1.0.0` |
| Baseline tag | `v1.0.0-rc4` (pre-R6-03) → promote after R6-03 verification |
| Scope | Configuration, environment, startup validation, Compose readiness |
| Out of scope | SMTP, observability, K8s, load balancing, Identity/RBAC/Queue/Complaint feature changes |

## Architecture (deployable unit)

```text
Browser → Frontend (:3000) → Backend (:8000) → PostgreSQL (:5432 in-network)
                 ↑ CORS / cookies        ↑ Alembic on start
```

- TLS termination: **external reverse proxy** (not in Compose).
- Redis: **not used**.
- Object storage: local filesystem via System Settings (not Compose volume for blobs beyond DB).

## Prerequisites

1. Docker Engine + Compose v2+
2. Checkout release branch/tag
3. Secrets available (vault or secure `.env`, never committed)
4. Postgres backup taken before upgrade (see Upgrade / Rollback)
5. Config validation PASS:

```powershell
python scripts/validate-production-config.py --env-file .env --require-production
```

## Production `.env` checklist (minimum)

| Variable | Example shape |
|---|---|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `POSTGRES_PASSWORD` | strong unique secret |
| `JWT_SECRET_KEY` | `openssl rand -hex 32` |
| `ALLOWED_ORIGINS` | `https://ecmp.example.com` |
| `ALLOWED_HOSTS` | `ecmp-api.example.com,backend` |
| `PASSWORD_RESET_FRONTEND_BASE_URL` | `https://ecmp.example.com` |
| `EMAIL_PROVIDER` | `noop` |
| `NEXT_PUBLIC_API_BASE_URL` | `https://ecmp-api.example.com` |
| `IMAGE_TAG` | `v1.0.0` (or RC) |

Full matrix: [`ENVIRONMENT_VARIABLE_REFERENCE.md`](./ENVIRONMENT_VARIABLE_REFERENCE.md).

## Deploy procedure

```powershell
# 1. Checkout
git fetch --tags
git checkout release/v1.0.0   # or release tag

# 2. Prepare env (from vault)
copy .env.example .env
# edit .env — production values only

# 3. Validate
python scripts\validate-production-config.py --env-file .env --require-production

# 4. Build with pinned tag + provenance
$env:IMAGE_TAG = "v1.0.0"
$env:APP_VERSION = "1.0.0"
.\scripts\release\build-rc.ps1   # or: docker compose build

# 5. Start dependency order (Compose enforces health)
docker compose up -d postgres
docker compose up -d backend      # alembic upgrade head in entrypoint
docker compose up -d frontend

# 6. Health
curl.exe -fsS http://127.0.0.1:8000/health
curl.exe -fsS -o NUL -w "%{http_code}" http://127.0.0.1:3000/
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

## Post-deploy smoke

See [`STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md). Minimum:

- `GET /health` → `status=ok`, `database=up`
- Login / refresh / logout
- Frontend loads against `NEXT_PUBLIC_API_BASE_URL`

## Related procedures

- [`STARTUP_CHECKLIST.md`](./STARTUP_CHECKLIST.md)
- [`UPGRADE_PROCEDURE.md`](./UPGRADE_PROCEDURE.md)
- [`../releases/ROLLBACK_v1.0.0.md`](../releases/ROLLBACK_v1.0.0.md)
- [`../deployment-checklist.md`](../deployment-checklist.md)
