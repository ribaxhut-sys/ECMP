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

```powershell
# 1. Backup
docker compose exec -T postgres pg_dump -U $env:POSTGRES_USER $env:POSTGRES_DB `
  > "backups/ecmp_pre_upgrade_$(Get-Date -Format yyyyMMdd_HHmmss).sql"

# 2. Fetch release
git fetch --tags
git checkout <target-tag>

# 3. Validate configuration
python scripts\validate-production-config.py --env-file .env --require-production

# 4. Build / pull images
$env:IMAGE_TAG = "<target-tag>"
$env:APP_VERSION = "<semver>"
docker compose build backend frontend

# 5. Rolling restart (migrations run in backend entrypoint)
docker compose up -d postgres
docker compose up -d --no-deps backend
# wait for healthy /health
docker compose up -d --no-deps frontend

# 6. Smoke
curl.exe -fsS http://127.0.0.1:8000/health
# login + critical path checks
```

## Alembic notes

- Backend entrypoint runs `alembic upgrade head` before uvicorn.
- If migration fails, container exits → investigate logs; restore from backup only if data corruption occurred (see Rollback).

## Rollback

Follow [`../releases/ROLLBACK_v1.0.0.md`](../releases/ROLLBACK_v1.0.0.md): stop app tiers, redeploy previous image tag, restore DB dump only when a migration must be reverted.
