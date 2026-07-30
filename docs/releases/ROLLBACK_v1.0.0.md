# ECMP v1.0.0 — Rollback Package

| Field | Value |
|---|---|
| ID | RBK-V1-001 |
| Version | 1.1.0 |
| Date | 2026-07-30 |
| Task | Release Blocker B4; SECMIG-P6-005 compose alignment |
| Status | 🟢 Active |

## Purpose

Rollback Production to the previous known-good release if go-live validation fails
or a critical post-deploy incident occurs.

**Canonical production Compose:** `docker-compose.prod.yml` (or Nginx variant).
Operator flow: Release → Deployment → Startup → Ops → Backup/Restore → **Rollback**.
Hub: [`../deployment/README.md`](../deployment/README.md).

## Preconditions

1. Pre-deploy Postgres backup available (timestamped dump) per OPS-BAK-001.
2. Previous Docker images retained (or rebuildable from prior tag `v1.0.0-rc4`).
3. Ops approval to execute rollback (REL-APR-001 when under release governance).

## Artifacts

| Artifact | Location / Identifier |
|---|---|
| Previous application tag | `v1.0.0-rc4` |
| Previous images | `ecmp-backend` / `ecmp-frontend` built from `v1.0.0-rc4` commit (`bd0072c`) |
| Database backup | `backups/ecmp_pre_v1.0.0_<timestamp>.sql` (ops-managed path) |
| This procedure | `docs/releases/ROLLBACK_v1.0.0.md` |

## Rollback procedure

Use production compose throughout:

```text
COMPOSE=docker compose -f docker-compose.prod.yml
```

### A. Application-only rollback (preferred when schema is compatible)

`v1.0.0-rc4` → `v1.0.0` shares the same additive Alembic lineage on `release/v1.0.0`.
Prefer **forward-fix** over schema downgrade.

```bash
# 1. Stop app tiers (keep edge/proxy as needed for controlled drain)
docker compose -f docker-compose.prod.yml stop frontend backend

# 2. Checkout previous tag (or redeploy previous image digests)
git fetch --tags
git checkout v1.0.0-rc4

# 3. Restore prior image tags / rebuild
export IMAGE_TAG=v1.0.0-rc4
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d postgres
# wait healthy
docker compose -f docker-compose.prod.yml up -d backend
# wait /ready via https://$ECMP_DOMAIN/ready
docker compose -f docker-compose.prod.yml up -d frontend
docker compose -f docker-compose.prod.yml up -d caddy

# 4. Do NOT restore DB dump unless a migration must be reverted
```

### B. Full rollback including database (only if migration corruption)

```bash
docker compose -f docker-compose.prod.yml stop frontend backend

docker compose -f docker-compose.prod.yml up -d postgres
# wait healthy
# Restore pre-deploy dump (follow OPS-RST-001; binary-safe for -Fc)
docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < backups/ecmp_pre_v1.0.0_<timestamp>.sql

git checkout v1.0.0-rc4
export IMAGE_TAG=v1.0.0-rc4
docker compose -f docker-compose.prod.yml build backend frontend
docker compose -f docker-compose.prod.yml up -d backend frontend caddy
```

> Warning: DB restore is destructive to post-deploy data. Use only with incident commander approval. Prefer OPS-RST-001 for restore detail.

Local/dev foundation (`docker-compose.yml` without `.prod`) is **not** the production rollback path.

## Validation after rollback

Probes via `https://$ECMP_DOMAIN` (host `:8000` not published on prod compose).

| Check | Expected |
|---|---|
| Config validator | `python scripts/validate-production-config.py --env-file .env --require-production` → PASS |
| `GET /live` | HTTP 200 (liveness) via HTTPS |
| `GET /ready` | HTTP 200 when DB/startup ready; **503** when not |
| Version field | Matches rolled-back release (`1.0.0-rc4` if reverting to RC4) |
| Startup log | `ENVIRONMENT` + `auth_mode` consistent with target release / `.env` |
| Login | 200 + refresh cookie (jwt mode when staging/production) |
| Refresh | 200 with rotation |
| Dashboard | Loads summary panels |
| Smoke: create complaint | Succeeds for authorized role |
| Logs | No auth/token leakage |

Full smoke table: [`../deployment/PRODUCTION_DEPLOYMENT_GUIDE.md`](../deployment/PRODUCTION_DEPLOYMENT_GUIDE.md). Secret rollback only: `15 Operations Runbook/ECMP_Secret_Operations_Guide_v1.0.md`. DB/config restore procedure: `15 Operations Runbook/ECMP_Restore_Verification_Procedure_v0.1.md`. Drill evidence checklist: `15 Operations Runbook/ECMP_Recovery_Validation_Checklist_v1.0.md`.

## Communication

1. Record incident ID, trigger, and decision in ops log.
2. Notify stakeholders of temporary service impact.
3. Open hotfix / post-mortem if Production remains on prior tag.
