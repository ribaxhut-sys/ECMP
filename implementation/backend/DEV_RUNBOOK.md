# Dev Runbook — Case Service (Mode A / G2)

| Field | Value |
|---|---|
| Tree | `implementation/backend` |
| Related | DEC-021, ADR-009, REGRESSION_PACK_G2 |

## Path (happy)

```bash
# 0. Repo root
cd /path/to/ECMP

# 1. Postgres (if using compose under implementation)
docker compose -f implementation/infrastructure/docker-compose.yml up -d

# 2. Backend env
cd implementation/backend
cp -n .env.example .env   # never commit .env
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# 3. Migrate
alembic upgrade head

# 4. Run API
uvicorn app.main:app --reload --port 8001

# 5. Token (dev only — see README Auth)
# Authorization: Bearer $ECMP_DEV_TOKEN

# 6. Optional: enable drain inspector
# ECMP_ENABLE_DEV_ENDPOINTS=true → POST /_dev/outbox/drain

# 7. Regression
./scripts/run_g2_regression.sh
```

## Smoke vs VPS lab edge

Public edge uses **`backend/`** (DEC-020). For edge health:

```bash
./deploy/smoke-lab.sh https://pengaduan.layanankami.tech
```

Do not treat edge `/docs` 200 as success (W-S04 closed — expect 404).

## Failure hints

| Symptom | Check |
|---|---|
| 401 | Bearer token / `ECMP_DEV_TOKEN` |
| 403 | permission token variant |
| 409 INVALID_TRANSITION | workflow subset — reopen not in Mode A |
| migrate fail | Postgres up? `ECMP_DATABASE_URL` |
| contract fail | OpenAPI changed without DEC freeze |

## Mode B

Forbidden without Board C-7 lift + bilateral IdP — see `deploy/evidence/Mode_B_Blocked_Pending_IdP_Contract_20260801.md`.
