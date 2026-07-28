# ECMP Upgrade Procedure (R6-03)

| Field | Value |
|---|---|
| ID | UPG-001 |
| Version | 1.0.0 |
| Date | 2026-07-28 |

## Principles

1. Prefer **forward fixes** over schema downgrade.
2. Always take a Postgres dump before applying new Alembic revisions.
3. Pin `IMAGE_TAG` / git tag; do not upgrade production on floating `latest`.
4. Re-run config validation after any `.env` change.

## Upgrade steps

Production TLS stack uses `docker-compose.prod.yml` (see [`TLS_REVERSE_PROXY.md`](./TLS_REVERSE_PROXY.md)).
Substitute `docker compose` below with `docker compose -f docker-compose.prod.yml` in production.

```powershell
# 1. Backup Postgres (+ optionally Caddy data volume ecmp_prod_caddy_data)
docker compose -f docker-compose.prod.yml exec -T postgres pg_dump -U $env:POSTGRES_USER $env:POSTGRES_DB `
  > "backups/ecmp_pre_upgrade_$(Get-Date -Format yyyyMMdd_HHmmss).sql"

# 2. Fetch release
git fetch --tags
git checkout <target-tag>

# 3. Validate configuration
python scripts\validate-production-config.py --env-file .env --require-production
docker compose -f docker-compose.prod.yml config

# 4. Build / pull images
$env:IMAGE_TAG = "<target-tag>"
$env:APP_VERSION = "<semver>"
docker compose -f docker-compose.prod.yml build backend frontend

# 5. Rolling restart (migrations run in backend entrypoint; proxy stays up)
docker compose -f docker-compose.prod.yml up -d postgres
docker compose -f docker-compose.prod.yml up -d --no-deps backend
# wait for healthy /ready (via proxy once backend is up)
docker compose -f docker-compose.prod.yml up -d --no-deps frontend
docker compose -f docker-compose.prod.yml up -d caddy

# 6. Smoke via HTTPS (do not rely on host :8000 — not published in prod)
curl.exe -fsS https://$env:ECMP_DOMAIN/live
curl.exe -fsS https://$env:ECMP_DOMAIN/ready
# login + critical path checks
```

### Certificate renewal

- **Caddy:** automatic; no upgrade step. Persist `ecmp_prod_caddy_data`.
- **Nginx alternative:** renew PEMs under `deploy/proxy/certs/`, then `nginx -s reload`.

## Alembic notes

- Backend entrypoint runs `alembic upgrade head` before uvicorn.
- If migration fails, container exits → investigate logs; restore from backup only if data corruption occurred (see Rollback).

## Rollback

Follow [`../releases/ROLLBACK_v1.0.0.md`](../releases/ROLLBACK_v1.0.0.md): stop app tiers, redeploy previous image tag, restore DB dump only when a migration must be reverted.
