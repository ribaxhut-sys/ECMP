# ECMP Deployment Standards

| Field | Value |
|---|---|
| ID | DEP-001 |
| Version | 0.2 |
| Owner | DevOps Lead |
| Reviewer | Security / SRE |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |
| Task note | SECMIG-P6-005 — foundation SoT; slice paths Historical |

**Canonical deployment standards** for the **foundation stack**: root `backend/`,
`frontend/`, and Compose files at the repository root.

Executable deploy/startup procedures: [`../docs/deployment/`](../docs/deployment/)
(hub: [`../docs/deployment/README.md`](../docs/deployment/README.md)).
Release Go/No-Go: [`../16 Release Management/`](../16%20Release%20Management/).

## 0. Canonical vs Historical

| Path | Role |
|---|---|
| Root `backend/`, `frontend/`, `docker-compose*.yml`, `.env.example` | **Canonical** — production / SEC-MIG ops |
| `implementation/backend`, `implementation/infrastructure` | **Historical / optional packs** — Sprint-01 case-service slice; local IdP baseline (OPS-IDP-001). Do **not** use for foundation production cutover |

## 1. Environments (foundation)

### DEV (local)

- Database: PostgreSQL via root `docker-compose.yml` (service `postgres`) or equivalent local Postgres 16.
- Application: root `backend/` + `frontend/` (Compose or host uvicorn / Next.js per [`../docs/local-stack.md`](../docs/local-stack.md)).
- Schema: Alembic on foundation `backend/` (`alembic upgrade head`; Compose may run on start).
- Configuration: repo-root `.env` from `.env.example` / `.env.production.example` — **git-ignored**, never committed.
- Secure config matrix: [`../docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md`](../docs/deployment/ENVIRONMENT_VARIABLE_REFERENCE.md) (ENV-REF-001 / P6-001).

### CI

- Foundation and catalog gates per active workflows; OpenAPI catalog under `07 API Catalog/openapi/**` remains a contract SoT (DEC-002).
- Historical note: early Sprint-01 CI also gated `implementation/backend/**` — treat that path as legacy pack CI only.

### Staging / UAT / Production

- Auth: `ECMP_AUTH_MODE=jwt` with `OIDC_*` when `ENVIRONMENT=staging|production` (P6-001). Static `ECMP_DEV_*` tokens prohibited on shared/prod.
- Production TLS reference: `docker-compose.prod.yml` (Caddy) or `docker-compose.prod.nginx.yml` — see [`../docs/deployment/TLS_REVERSE_PROXY.md`](../docs/deployment/TLS_REVERSE_PROXY.md).
- Promotion Go/No-Go: **REL-SEC-001** + DEP-CHK-V1 + START-CHK-001 (see §3). Shared-env restore drill (OPS-RCV-001) required before first shared UAT.
- ADR-010 remains the platform baseline decision record; foundation Compose/docs are the **current operational reference** for the foundation release line. Remaining ADR-010 automation (registry promotion, WAL schedulers) stays Future until separately authorized.

## 2. Configuration & Secrets

| Environment | Mechanism | Rules |
|---|---|---|
| Local | Root `.env` (git-ignored) | Templates without secrets; validate with `scripts/validate-production-config.py` when targeting staging/production shapes |
| Shared / prod | Vault or sealed ops store + injected `.env` | No secrets in image, repo, or logs; rotate per OPS-SEC-SEC-001 |
| CI | Workflow secrets / ephemeral DB | CI credentials are not shared-env credentials |

One artifact, many configurations — behavior differs by env vars (`ENVIRONMENT`, `ECMP_AUTH_MODE`, `OIDC_*`, `ALLOWED_ORIGINS`, …), not by divergent code branches.

## 3. Promotion & gates

### Documentation precedence (foundation cutover)

```text
REL-SEC-001  →  DEP-CHK-V1  →  START-CHK-001
```

1. [`../16 Release Management/ECMP_Release_Security_Gate_v1.0.md`](../16%20Release%20Management/ECMP_Release_Security_Gate_v1.0.md) (REL-SEC-001)
2. [`../docs/deployment-checklist.md`](../docs/deployment-checklist.md) (DEP-CHK-V1)
3. [`../docs/deployment/STARTUP_CHECKLIST.md`](../docs/deployment/STARTUP_CHECKLIST.md) (START-CHK-001)

**DEP-CHK-001** ([`./ECMP_Production_Deployment_Checklist_v0.1.md`](./ECMP_Production_Deployment_Checklist_v0.1.md)) is **Historical** — Sprint-08 planning checklist. **Do not** use it for foundation production cutover.

Slice engineering Go/No-Go (catalog/CI/sign-off) remains REL-001 §3.1 when closing a delivery slice. Shared/prod always requires REL-SEC-001.

## 4. Rollback

- **Canonical mechanic (foundation production):** [`../docs/releases/ROLLBACK_v1.0.0.md`](../docs/releases/ROLLBACK_v1.0.0.md) using `docker-compose.prod.yml`.
- **DB restore:** OPS-RST-001; validation OPS-RCV-001. Prefer forward-fix over schema downgrade.
- **Schema:** Alembic revisions must keep working `downgrade()` where used; destructive downgrades need explicit Architecture / SO approval.
- **`audit_logs`** (platform) and **`audit_logs_legacy`** (domain writers) are append-only. Timestamps: `audit_logs.created_at`, `audit_logs_legacy.occurred_at`.

## 5. Observability

- **Foundation (canonical):** Liveness `GET /live`; Readiness `GET /ready`. Use for restore/DR (OPS-RST-001 / OPS-RCV-001).
- **Historical (slice pack `implementation/backend`):** `GET /health` / `GET /health/ready` — not for foundation production recovery.
- Structured logging + request/correlation ids — OPS-LOG-001 / TS-OBS-001.
- Metrics/tracing product stacks remain Future unless separately authorized.

## 6. Backup & recovery (policy pointer)

- Manual backup / restore / DR: OPS-BAK-001, OPS-RST-001, OPS-DR-001, OPS-RCV-001 under `15 Operations Runbook`.
- **Backup automation / WAL / PITR** = **Future** (not authorized by P6-003).

## Related

- [`../docs/deployment/README.md`](../docs/deployment/README.md) (DEP-HUB-001)
- [`./ECMP_Production_Deployment_Checklist_v0.1.md`](./ECMP_Production_Deployment_Checklist_v0.1.md) (DEP-CHK-001 — Historical)
- [`../docs/deployment-checklist.md`](../docs/deployment-checklist.md) (DEP-CHK-V1 — Active)
- [`../15 Operations Runbook/`](../15%20Operations%20Runbook/)
- [`../16 Release Management/ECMP_Release_Security_Gate_v1.0.md`](../16%20Release%20Management/ECMP_Release_Security_Gate_v1.0.md) (REL-SEC-001)
- [`../21 Technical Standards/ECMP_Technical_Standards_v0.1.md`](../21%20Technical%20Standards/ECMP_Technical_Standards_v0.1.md) (TS-001)
- ADR-004, ADR-007, ADR-010
