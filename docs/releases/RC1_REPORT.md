# ECMP Release Candidate Report — v1.0.0

| Field | Value |
|---|---|
| ID | RC-RPT-001 |
| Version | **1.0.0** (originally prepared as **1.0.0-rc1**) |
| Date | 2026-07-25 |
| Task | Sprint R1 / R1-01–R1-03 (re-validation); originally PHASE-12 / TASK-014 |
| Scope | Foundation stack (`backend/`, `frontend/`, Compose) — **no new features in Sprint R1** |

## Gate Summary

| Area | Result |
|---|---|
| Business Modules | **PASS** |
| Authentication | **PASS** |
| Security | **PASS** |
| Deployment | **PASS** |
| Documentation | **PASS** |
| Testing | **PASS** (full suite vs Compose PostgreSQL — Sprint R1) |
| OpenAPI | **PASS** |
| Docker | **PASS** |
| Root Frontend CI | **PASS** (npm ci · typecheck · build — Sprint R1-02) |

## Release Recommendation

### **GO**

ECMP **v1.0.0** remains **GO** for Production after Sprint R1 re-validation.

Code freeze remains in effect: critical/high fixes and documentation only.

---

## Business Modules

| Module | Status | Notes |
|---|---|---|
| Complaints | PASS | CRUD + domain processing + search |
| Assignment | PASS | Supervisor + history |
| Escalation | PASS | Supervisor + history + review/closure |
| Resolutions / Appointments | PASS | Resolution + appointment lifecycle |
| Timeline | PASS | Complaint + activity timeline |
| Queue | PASS | Queues / tickets / counters |
| SLA | PASS | Complaint SLA + policies |
| Attachments | PASS | Aggregate-bound attachments |
| Notifications | PASS | Templates + queue |
| Reporting / KPI / Dashboard | PASS | Aggregates + panels |
| User Management / IAM | PASS | Users + roles/permissions/scopes |
| Settings / Audit / Branches | PASS | Platform support APIs |

No schema/API additions in Sprint R1 tasks.

## Authentication

| Check | Status |
|---|---|
| Login (bcrypt) | PASS |
| JWT access 15m | PASS |
| Refresh 7d + rotate | PASS |
| Logout revoke | PASS |
| `/auth/me` | PASS |
| Dashboard without `NEXT_PUBLIC_ACCESS_TOKEN` | PASS |

## Security

| Check | Status |
|---|---|
| JWT + refresh rotation | PASS |
| Security headers | PASS |
| Trusted Host (non-dev) | PASS |
| Secret guard | PASS |
| Hardened CORS | PASS |
| No sensitive logs | PASS |
| Docs disabled in production | PASS |

## Deployment

| Check | Status |
|---|---|
| Checklist published | PASS — `docs/deployment-checklist.md` |
| Env validation / secret guard | PASS |
| Alembic on container start | PASS |
| Health verification steps | PASS |
| Alembic head (Sprint R1 host) | PASS — **0036_search_indexes** |

## Documentation

| Artifact | Status |
|---|---|
| `docs/releases/v1.0.0.md` | PASS (Sprint R1 refresh) |
| `CHANGELOG.md` | PASS (Sprint R1 refresh) |
| `README.md` / `docs/local-stack.md` | PASS |
| API Catalog + OpenAPI `1.0.0` | PASS |
| Known limitations | PASS (aligned to current scope) |

## Testing

### Sprint R1 re-validation (2026-07-25)

Compose PostgreSQL service (`ecmp-postgres`, port **5433**); `alembic upgrade head`; full backend suite:

| Metric | Result |
|---|---|
| Passed | **910** |
| Failed | **0** |
| Skipped | **0** |
| Coverage (`--cov=app`, branch) | **87%** |

Defect fixed during R1-01 (Windows-only): async psycopg rejected `ProactorEventLoop` — addressed via `backend/tests/conftest.py` SelectorEventLoop policy. No production API/schema change.

Root frontend (local gate matching R1-02 workflow):

| Step | Result |
|---|---|
| `npm ci` | PASS |
| `npm run typecheck` | PASS |
| `npm run build` | PASS |

### Historical RC1 prep note (2026-07-23)

Earlier RC1 host run: **38 passed**, **8 skipped**, **0 failed** (auth/complaint integration skipped when Postgres unavailable). Superseded by Sprint R1 evidence above.

```bash
cd backend
# Compose Postgres on host port 5433 by default
set POSTGRES_HOST=localhost
set POSTGRES_PORT=5433
alembic upgrade head
pytest -q --cov=app --cov-report=term
```

## OpenAPI

| Check | Status |
|---|---|
| Runtime routers wired in `backend/app/api/router.py` | PASS |
| Auth/Complaint/Queue/SLA/Attachment/Notification/IAM documented | PASS |
| Error envelope documented | PASS |

## Docker

| Check | Status |
|---|---|
| Backend multi-stage | PASS |
| Non-root user | PASS |
| Healthcheck | PASS |
| Restart policy | PASS (`unless-stopped`) |
| Alembic upgrade head | PASS (entrypoint) |
| Graceful shutdown | PASS (`--timeout-graceful-shutdown 30`) |
| Frontend multi-stage + non-root | PASS |

## Known Issues

### Critical

- None

### High

- None blocking GO

### Medium

- Foundation frontend CI is minimal (typecheck + build only; no Vitest/Playwright by design — Sprint R1-02)
- Role→permission SoT still code-seeded (`rbac` / IAM seeds) pending API-062

### Low

- pgAdmin not started by default (intentional; `tools` profile)
- Default local JWT secret allowed only in `development`

## Known Limitations (product)

- No MFA, SSO/OAuth, LDAP, password reset, social login
- No external email/WebSocket push channels beyond notification queue APIs
- No mobile client
- No Customer Master write-back
- No broker-backed enterprise event bus in this Compose stack

## Sign-off

| Role | Decision |
|---|---|
| Engineering (Sprint R1) | **GO** — Postgres integration suite green; root frontend CI added |
| Security / Ops | Confirm vault secrets + TLS before shared env promote |
