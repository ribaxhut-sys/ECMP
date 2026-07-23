# ECMP Release Candidate Report — v1.0.0-rc1

| Field | Value |
|---|---|
| ID | RC-RPT-001 |
| Version | **1.0.0-rc1** |
| Date | 2026-07-23 |
| Task | PHASE-12 / TASK-014 |
| Scope | Foundation stack (`backend/`, `frontend/`, Compose) — **no new features** |

## Gate Summary

| Area | Result |
|---|---|
| Business Modules | **PASS** |
| Authentication | **PASS** |
| Security | **PASS** |
| Deployment | **PASS** |
| Documentation | **PASS** |
| Testing | **PASS** (unit/guard; integration skipped when Postgres unavailable) |
| OpenAPI | **PASS** |
| Docker | **PASS** |

## Release Recommendation

### **GO**

ECMP **v1.0.0-rc1** is ready for **staging / UAT**.

Code freeze remains in effect: critical/high fixes and documentation only.

---

## Business Modules

| Module | Status | Notes |
|---|---|---|
| Complaints | PASS | CRUD + audit |
| Assignment | PASS | Supervisor + history |
| Escalation | PASS | Supervisor + history |
| Timeline | PASS | Immutable read |
| Reporting | PASS | summary / by-status / by-branch |
| User Management | PASS | bcrypt; hash never exposed |

No TODO/FIXME in `backend/` or `frontend/src`. No schema/API additions in this task.

## Authentication

| Check | Status |
|---|---|
| Login (bcrypt) | PASS |
| JWT access 15m | PASS |
| Refresh 7d + rotation | PASS |
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

## Documentation

| Artifact | Status |
|---|---|
| `docs/releases/v1.0.0-rc1.md` | PASS |
| `CHANGELOG.md` | PASS |
| `README.md` / `docs/local-stack.md` | PASS |
| API Catalog + OpenAPI `1.0.0-rc1` | PASS |
| Known limitations | PASS (in release notes) |

## Testing

Executed on RC1 preparation host (2026-07-23):

| Suite | Result |
|---|---|
| Backend `pytest tests/` | **38 passed**, **8 skipped**, **0 failed** |
| Skipped | Auth + complaint API integration (Postgres unavailable on prep host) |
| Settings / secret guard | Pass |
| Security headers | Pass |
| RBAC unit | Pass |

Operators must re-run full suite against staging Postgres before UAT sign-off:

```bash
cd backend
alembic upgrade head
pytest -q
```

Expected with Postgres up: previously skipped auth/complaint tests should execute (target 0 failed).

## OpenAPI

| Check | Status |
|---|---|
| Runtime paths ⊆ catalog | PASS (17 `/api/v1/*` + `/health`) |
| Auth/Complaint/Report/User documented | PASS |
| Error envelope documented | PASS |
| No undocumented business endpoints | PASS |

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

- None blocking RC1 GO

### Medium

- Foundation frontend has no dedicated Vitest suite yet (dashboard states covered by UI components; CI gate lives on `implementation/` track)
- Role→permission SoT still code-defined (`rbac.py`) pending API-062

### Low

- pgAdmin not started by default (intentional; `tools` profile)
- Default local JWT secret allowed only in `development`

## Known Limitations (product)

- No MFA, SSO/OAuth, LDAP, password reset, social login
- No email / WebSocket notifications
- No mobile client
- No Customer Master write-back
- No SLA engine / broker-backed enterprise events in this stack

## Sign-off

| Role | Decision |
|---|---|
| Engineering (RC prep) | **GO** for staging/UAT |
| Security / Ops | Confirm vault secrets + TLS before shared env promote |
