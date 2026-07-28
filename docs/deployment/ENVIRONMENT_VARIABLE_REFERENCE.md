# ECMP Environment Variable Reference (R6-03)

| Field | Value |
|---|---|
| ID | ENV-REF-001 |
| Version | 1.0.0 |
| Date | 2026-07-28 |
| Scope | Foundation stack (`backend/`, `frontend/`, root Compose) |
| Related | R6-03, `.env.example`, `backend/app/core/config.py` |

## Classification

| Class | Meaning |
|---|---|
| **Required** | Must be present for the process/compose service to start safely |
| **Optional** | Safe default exists; override per environment |
| **Development Only** | Allowed in `development` / `test`; rejected outside |
| **Production Only** | Stricter or mandatory when `ENVIRONMENT=production` |
| **Deprecated** | Present historically or in examples; do not use |

`ENVIRONMENT` values: `development` | `test` | `staging` | `production`.  
`test` follows development guard rules (docs on, Secure cookies off, localhost allowed).

## Matrix

| Variable | Class | Dev default | Staging | Production | Notes |
|---|---|---|---|---|---|
| `ENVIRONMENT` | Required | `development` | `staging` | `production` | Drives fail-fast gates |
| `APP_VERSION` | Optional | `1.0.0` | set to release | set to release | Also bake via build ARG |
| `LOG_LEVEL` | Optional | `INFO` | `INFO` | `INFO` | |
| `DEBUG` | Development Only | `false` | **must false** | **must false** | Fail-fast if true outside dev/test |
| `POSTGRES_USER` | Required | `ecmp` | strong role | strong role | |
| `POSTGRES_PASSWORD` | Required | weak OK | **strong** | **strong** | Compose `${:?}` required |
| `POSTGRES_DB` | Required | `ecmp` | set | set | |
| `POSTGRES_HOST` | Required | `localhost` | service DNS | service DNS | Compose injects `postgres` |
| `POSTGRES_PORT` | Optional | `5433` (host) | `5432` in-net | `5432` in-net | |
| `DATABASE_URL` | Optional | unset | optional override | optional override | Must be PostgreSQL if set |
| `BACKEND_PORT` | Optional | `8000` | map as needed | **not published** (prod compose) | Local compose host port only |
| `ECMP_DOMAIN` | Production Only | — | public hostname | public hostname | Caddy/Nginx server name (B3) |
| `ACME_EMAIL` | Production Only (Caddy) | — | ops email | ops email | ACME registration contact |
| `HTTP_PORT` / `HTTPS_PORT` | Optional | — | `80` / `443` | `80` / `443` | Proxy published ports |
| `FORWARDED_ALLOW_IPS` | Production (behind proxy) | `127.0.0.1` | proxy CIDRs or `*` | `*` in prod compose | Uvicorn trusted proxies; see TLS guide |
| `ALLOWED_ORIGINS` | Required | `http://localhost:3000` | real origin(s) | **https** origin(s) | No `*`; no localhost outside dev |
| `ALLOWED_HOSTS` | Required (non-dev) | localhost list | public hosts | `ECMP_DOMAIN,backend` | TrustedHostMiddleware |
| `JWT_SECRET_KEY` | Required | placeholder OK | **≥32 chars** | **≥32 chars** | Compose `${:?}` required |
| `JWT_ALGORITHM` | Required | `HS256` | `HS256` | `HS256` | Only supported algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Optional | `15` | `15` | `15` | |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Optional | `7` | `7` | `7` | |
| `LOGIN_RATE_LIMIT_ENABLED` | Optional | `true` | `true` | `true` | In-memory; not Redis |
| `LOGIN_MAX_FAILED_ATTEMPTS` | Optional | `5` | `5` | `5` | |
| `LOGIN_LOCKOUT_SECONDS` | Optional | `300` | `300` | `300` | |
| `FRONTEND_PORT` | Optional | `3000` | map | **not published** (prod compose) | Local compose host port only |
| `NEXT_PUBLIC_API_BASE_URL` | Required (build) | `http://localhost:8000` | public API URL | **https://ECMP_DOMAIN** | Docker build fails if unset; single-host topology |
| `PASSWORD_MIN_LENGTH` | Optional | `8` | ≥8 | ≥8 | |
| `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` | Optional | `15` | set | set | |
| `PASSWORD_RESET_FRONTEND_BASE_URL` | Required | localhost OK | public FE | **https** FE | Must align with `ALLOWED_ORIGINS` |
| `EMAIL_PROVIDER` | Dev: `logging` / Prod: `noop` | `logging` | `noop` | `noop` | SMTP out of R6-03 scope |
| `PGADMIN_*` | Optional (tools) | weak OK | strong if used | strong if used | Profile `tools` only |
| `IMAGE_TAG` | Optional | `latest` | pin tag | **pin release tag** | Avoid floating `latest` in prod |
| `GIT_COMMIT` / `GIT_BRANCH` / `BUILD_TIME` / `GIT_TREE_STATE` | Optional | `unknown` | bake at build | bake at build | R6-01 provenance |
| `REDIS_URL` / `REDIS_*` | **Deprecated / unused** | — | — | — | Not read by foundation stack |
| `ECMP_*` (implementation backend) | Legacy pack | — | — | — | Not used by root foundation app |

## Unused / duplicate / conflict findings

| Finding | Detail | Action |
|---|---|---|
| Unused Redis vars | No Redis client; login lockout is in-memory (R2-03) | Do not invent `REDIS_*`; document as N/A |
| Duplicate stacks | Root `backend/` vs `implementation/backend/` (`ECMP_*`) | Production uses **root** stack only |
| Duplicate CORS names | Root `ALLOWED_ORIGINS` vs legacy `ECMP_ALLOWED_ORIGINS` | Use `ALLOWED_ORIGINS` for foundation |
| Conflict risk | `PASSWORD_RESET_FRONTEND_BASE_URL` ≠ any `ALLOWED_ORIGINS` | Fail-fast outside development |
| Conflict risk | Compose default localhost origins + `ENVIRONMENT=production` | App refuses to start |
| Storage env | No `STORAGE_*` env | Configure via System Settings keys `storage.provider` / `storage.root.path` |

## Validation

```bash
python scripts/validate-production-config.py --env-file .env
python scripts/validate-production-config.py --env-file .env --require-production
docker compose -f docker-compose.prod.yml config
```

TLS / proxy: [`TLS_REVERSE_PROXY.md`](./TLS_REVERSE_PROXY.md), template [`.env.production.example`](../../.env.production.example).

Unit coverage: `backend/tests/test_settings_guard.py`.
