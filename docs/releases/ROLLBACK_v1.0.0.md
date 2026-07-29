# ECMP v1.0.0 — Rollback Package

| Field | Value |
|---|---|
| ID | RBK-V1-001 |
| Version | 1.0.0 |
| Date | 2026-07-29 |
| Task | Release Blocker B4 (rollback target corrected to `v1.0.0-rc4`) |

## Purpose

Rollback Production to the previous known-good release if go-live validation fails
or a critical post-deploy incident occurs.

## Preconditions

1. Pre-deploy Postgres backup available (timestamped dump).
2. Previous Docker images retained (or rebuildable from prior tag `v1.0.0-rc4`).
3. Ops approval to execute rollback.

## Artifacts

| Artifact | Location / Identifier |
|---|---|
| Previous application tag | `v1.0.0-rc4` |
| Previous images | `ecmp-backend` / `ecmp-frontend` built from `v1.0.0-rc4` commit (`bd0072c`) |
| Database backup | `backups/ecmp_pre_v1.0.0_<timestamp>.sql` (ops-managed path) |
| This procedure | `docs/releases/ROLLBACK_v1.0.0.md` |

## Rollback procedure

### A. Application-only rollback (preferred when schema is compatible)

`v1.0.0-rc4` → `v1.0.0` shares the same additive Alembic lineage on `release/v1.0.0`.
Prefer **forward-fix** over schema downgrade.

```bash
# 1. Stop app tiers
docker compose stop frontend backend

# 2. Checkout previous tag (or redeploy previous image digests)
git fetch --tags
git checkout v1.0.0-rc4

# 3. Restore prior image tags / rebuild
docker compose build backend frontend
docker compose up -d postgres
# wait healthy
docker compose up -d backend
# wait healthy (/ready)
docker compose up -d frontend

# 4. Do NOT restore DB dump unless a migration must be reverted
```

### B. Full rollback including database (only if migration corruption)

```bash
docker compose stop frontend backend

# Restore pre-deploy dump into Postgres (example)
docker compose up -d postgres
# wait healthy
docker exec -i ecmp-postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" < backups/ecmp_pre_v1.0.0_<timestamp>.sql

git checkout v1.0.0-rc4
docker compose build backend frontend
docker compose up -d backend frontend
```

> Warning: DB restore is destructive to post-deploy data. Use only with incident commander approval.

## Validation after rollback

| Check | Expected |
|---|---|
| `GET /live` | HTTP 200 (liveness) |
| `GET /ready` | HTTP 200 when DB/startup ready; **503** when not |
| Version field | Matches rolled-back release (`1.0.0-rc4` if reverting to RC4) |
| Login | 200 + refresh cookie |
| Refresh | 200 with rotation |
| Dashboard | Loads summary panels |
| Smoke: create complaint | Succeeds for authorized role |
| Logs | No auth/token leakage |

## Communication

1. Record incident ID, trigger, and decision in ops log.
2. Notify stakeholders of temporary service impact.
3. Open hotfix / post-mortem if Production remains on prior tag.
