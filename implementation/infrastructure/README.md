# ECMP local infrastructure

| Field | Value |
|---|---|
| Path | `implementation/infrastructure/` |
| Compose | `docker-compose.yml` |
| Default | PostgreSQL 16 (`ecmp-postgres`) |
| Optional | Keycloak IdP via Compose profile **`auth`** (SEC-MIG Phase 1) |

## Commands

PostgreSQL only (unchanged default):

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml up -d
```

IdP baseline (opt-in):

```powershell
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth up -d
```

See:

- [`keycloak/README.md`](./keycloak/README.md) — realm import, clients, roles, validation
- [`../../15 Operations Runbook/ECMP_IdP_Administrator_Runbook_v1.0.md`](../../15%20Operations%20Runbook/ECMP_IdP_Administrator_Runbook_v1.0.md) — OPS-IDP-001

## Environment

Copy [`.env.example`](./.env.example) to `.env` to override Keycloak bootstrap admin (local only).

## Phase boundary

Profile `auth` provides infrastructure only. It does **not** change ECMP application authentication (Phase 2+).
