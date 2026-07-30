# ECMP Implementation (Historical / parallel packs)

| Field | Value |
|---|---|
| ID | IMP-000 |
| Version | 0.3 |
| Owner | Engineering Manager / Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | ⚫ **Historical** (packs) — foundation SoT is repo root |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |
| Task note | SECMIG-P6-005 |

## Foundation first (canonical)

**Production / SEC-MIG / shared-env operations use the repository root stack:**

| Component | Path |
|---|---|
| Backend | `../backend/` |
| Frontend | `../frontend/` |
| Compose | `../docker-compose.yml`, `../docker-compose.prod.yml` |
| Deploy hub | [`../docs/deployment/README.md`](../docs/deployment/README.md) |
| Ops / security / backup | [`../15 Operations Runbook/`](../15%20Operations%20Runbook/) |
| Release gate | [`../16 Release Management/`](../16%20Release%20Management/) |

Do **not** treat `implementation/backend` as the production application SoT.

## What this folder is

Optional / historical packs retained for:

- Sprint-01 **case-service** slice (`backend/` here) — early create/get case path
- Local **Keycloak IdP baseline** (`infrastructure/` + profile `auth`) — OPS-IDP-001
- Developer Portal (`portal/`) — EKR tooling, not product UI
- Historical sprint implementation plans under subfolders (often marked Historical inline)

## Structure

```text
implementation/
├── backend/          ← Historical Sprint-01 case-service pack (not foundation SoT)
├── infrastructure/   ← Historical/optional: Postgres DEV pack + Keycloak auth profile
├── portal/           ← Developer Portal (EKR tooling)
├── frontend/         ← Historical / deferred pack notes (product UI = root frontend/)
├── tests/            ← e2e across packs (limited use)
└── deployment/       ← Historical placeholder; use docs/deployment + 14 Deployment Standards
```

## Optional: local IdP pack (SEC-MIG Phase 1 — no foundation wiring required)

```bash
docker compose -f implementation/infrastructure/docker-compose.yml --profile auth up -d
```

See `infrastructure/keycloak/README.md` and
[`../15 Operations Runbook/ECMP_IdP_Administrator_Runbook_v1.0.md`](../15%20Operations%20Runbook/ECMP_IdP_Administrator_Runbook_v1.0.md).
Does **not** replace foundation `ECMP_AUTH_MODE=jwt` production procedures (P6-001).

## Historical: Sprint-01 case-service local run

Only when deliberately exercising the legacy pack:

```bash
docker compose -f implementation/infrastructure/docker-compose.yml up -d
cd implementation/backend
python -m venv .venv
# activate venv, pip install, .env, alembic, uvicorn — pack-local only
```

## GO status (archived context)

Sprint-01 GO = slice create/get + G0 platform floor (DEC-002). That authorization
applied to the early slice track. Current foundation releases follow
`16 Release Management` (REL-SEC-001 for shared/prod).
