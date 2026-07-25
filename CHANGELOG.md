# Changelog

All notable changes to the ECMP application/repository release line are documented here.
API contract versioning remains governed by ADR-006 and OpenAPI `info.version`
(see `16 Release Management/ECMP_Release_Management_v0.1.md` §1).

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Repository versioning follows [SemVer](https://semver.org/) as defined in
`16 Release Management/ECMP_Repository_Versioning_Policy_v0.1.md`.

## [Unreleased]

### Notes

- Post-`v1.0.0-rc2`: only hotfixes and approved change requests until final `v1.0.0` promotion gate.

## [1.0.0-rc2] - 2026-07-25

### Added

- Sprint R1-02: minimal root frontend CI (`.github/workflows/root-frontend-ci.yml`) — `npm ci`, typecheck, build only.
- Sprint R2-03: configurable in-memory login brute-force protection (`LOGIN_RATE_LIMIT_ENABLED`, `LOGIN_MAX_FAILED_ATTEMPTS`, `LOGIN_LOCKOUT_SECONDS`) — HTTP `429 RATE_LIMITED` without Redis.
- Sprint R3: Release Candidate packaging — `docs/releases/v1.0.0-rc2.md`, smoke report, UAT accounts guide.

### Security

- Sprint R2-01: runtime secret guard rejects weak/default `POSTGRES_PASSWORD` and (when set) `PGADMIN_DEFAULT_PASSWORD` outside development (same fail-fast model as `JWT_SECRET_KEY`).
- Sprint R2-02: Compose requires credentials via `.env` — no silent `ecmp` / `admin` / `change-me-in-production` password fallbacks.
- Sprint R2-03: login lockout keyed by client IP + username.
- Sprint R2-04: production frontend builds fail if `NEXT_PUBLIC_API_BASE_URL` is missing (no silent `http://localhost:8000` embed).

### Fixed

- Sprint R1-01: Windows async Postgres integration tests — SelectorEventLoop policy in `backend/tests/conftest.py` (psycopg rejects ProactorEventLoop).

### Changed

- Sprint R1-03: refreshed `docs/releases/v1.0.0.md`, `docs/releases/RC1_REPORT.md` for current v1.0.0 scope + Postgres test evidence (910 passed / 0 failed / 0 skipped / 87% coverage).
- `.env.example` documents local DEVELOPMENT convenience credentials and R2/R3 required production overrides.
- Root frontend `package.json` adds `typecheck` script for CI.

### Known Limitations

- In-memory login lockout is per-process (multi-replica deployments do not share counters).
- Local Compose still embeds browser-reachable `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` when explicitly set in `.env` (required for local stack; not a silent default).

## [1.0.0] - 2026-07-23

### Added

- Production release of foundation stack (`backend/` + `frontend/` + Compose).
- Release notes: `docs/releases/v1.0.0.md`.
- Production deployment report: `docs/releases/PRODUCTION_DEPLOYMENT_REPORT.md`.
- Production rollback runbook: `docs/releases/ROLLBACK_v1.0.0.md`.
- Production deployment checklist: `docs/deployment-checklist.md` (v1.0.0).
- Capability surface (current): Auth, Complaints, Assignment, Escalation, Resolutions, Appointments, Timeline, Queue, SLA, Attachments, Notifications, Search, Reporting/KPI/Dashboard, Users/IAM, Branches/Customers, Settings, Audit.

### Changed

- Application version set to **1.0.0** (backend, frontend, OpenAPI `info.version`, API Catalog).
- Promoted from Release Candidate **v1.0.0-rc1** after staging/UAT gate (TASK-014).

### Fixed

- Backend entrypoint CRLF → LF (Linux container shebang).
- Auth logout `204` FastAPI response registration (`response_class=Response`).
- Pin `bcrypt==4.0.1` for passlib compatibility (password hash/verify).

### Security

- Production JWT secret rotation required before go-live (secret guard enforced).
- TLS termination expected at reverse proxy for Secure refresh cookies.

### Known Limitations

- No MFA, SSO/OAuth, LDAP, password reset, social login.
- No external email/WebSocket push channels beyond notification queue APIs; no mobile client.
- Role→permission map is code-seeded until Core Platform SoT (API-062).
- Foundation health probe is combined `GET /health` (not separate `/health/live` + `/health/ready` paths).
- No broker-backed enterprise event bus in the Compose foundation stack.

## [1.0.0-rc1] - 2026-07-23

### Added

- Foundation stack Release Candidate **v1.0.0-rc1** (`backend/` + `frontend/` + Compose).
- Production authentication: login, refresh rotation, logout, `/auth/me` (API-218..API-221).
- Complaint lifecycle modules: complaints, assignments, escalations, timelines.
- Reporting aggregates and user management APIs.
- Dashboard UI with login/logout and RBAC-gated quick actions.
- Release notes: `docs/releases/v1.0.0-rc1.md`.
- Deployment checklist: `docs/deployment-checklist.md`.

### Security

- JWT access (15m) + HttpOnly Secure SameSite=Lax refresh cookie (7d) with rotation.
- Secret guard rejects weak/default `JWT_SECRET_KEY` outside development.
- Trusted Host middleware outside development.
- Security headers (nosniff, frame deny, referrer, CSP).
- Hardened CORS method/header allow-lists.
- OpenAPI `/docs` `/redoc` `/openapi.json` disabled outside development.
- Request logs omit Authorization and token values.

### Changed

- Application version set to `1.0.0-rc1` (backend, frontend, OpenAPI `info.version`, catalog).
- Backend Docker: multi-stage build, non-root user, Alembic on start, graceful shutdown.
- Compose: backend healthcheck; frontend waits on healthy backend; pgAdmin under `tools` profile.

### Known Limitations

- No MFA, SSO/OAuth, LDAP, password reset, social login.
- No email/WebSocket notifications; no mobile client.
- Role→permission map is code-defined until Core Platform SoT (API-062).

## [0.8.0-rc.1] - 2026-07-22

### Added

- First Release Candidate tag line for internal / DEV validation (RC1) on the
  `implementation/` case-service track.
- Scope inherits Sprint-09 closed baseline (UAT plan v0.2, operational readiness
  runbooks) plus Sprint-10 quality/release gates.

### Notes

- Shared SIT/UAT/PROD deployment remains **out of scope** until JWT/OIDC
  (ADR-012 Phase 3) is accepted and active (ADR-010 / DEP-CHK-001).
- This RC is for internal DEV/CI validation only.

[Unreleased]: https://github.com/nandeshut/ECMP/compare/v1.0.0-rc2...HEAD
[1.0.0-rc2]: https://github.com/nandeshut/ECMP/releases/tag/v1.0.0-rc2
[1.0.0]: https://github.com/nandeshut/ECMP/releases/tag/v1.0.0
[1.0.0-rc1]: https://github.com/nandeshut/ECMP/releases/tag/v1.0.0-rc1
[0.8.0-rc.1]: https://github.com/nandeshut/ECMP/releases/tag/v0.8.0-rc.1
