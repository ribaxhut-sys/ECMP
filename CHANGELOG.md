# Changelog

All notable changes to the ECMP application/repository release line are documented here.
API contract versioning remains governed by ADR-006 and OpenAPI `info.version`
(see `16 Release Management/ECMP_Release_Management_v0.1.md` §1).

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Repository versioning follows [SemVer](https://semver.org/) as defined in
`16 Release Management/ECMP_Repository_Versioning_Policy_v0.1.md`.

## [Unreleased]

### Notes

- Post-`v1.0.0`: only hotfixes and approved change requests (new SemVer PATCH or new `rc.N` per versioning policy).

### Added

- GOV-DEC-F4 (`18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`): Cabang→Pusat escalation path, HQ return (reason code + note), `result_visibility` at Resolve with later change + audit.
- GOV-IMPACT-DEC-F4 (`26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md`): manual impact analysis for DEC-F4.
- GOV-CS-DEC-F4 (`18 Architecture Governance/reviews/ECMP_DEC_F4_Architecture_Board_Countersign_Pack_v1.0.md`): Architecture Board countersign pack; F4-OQ-01/02 closed.
- TC-CAT-CM-F4-001 (`13 Test Strategy/ECMP_UAT_Catalog_DEC_F4_v1.0.md`): UAT-F4-01…11.
- FRD-CM-002 Draft (`03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_v0.1.md`): FR-CM-010…015.
- Planned OpenAPI `complaint-management-esc-res.v1.yaml` (API-520…526 / API-CM-F4-001…007).
- Planned events EVT-CM-040…044 in `08 Event Catalog/events/events.yaml`.
- RTM-CM-F4-001 Draft (`26 Traceability/ECMP_RTM_Complaint_Management_DEC_F4_v0.1.md`).
- FRD-CM-ESC-OUTLINE-001 retained as outline pointer to FRD-CM-002.

### Changed

- BR-CM-CAT-001 Draft → **v1.1**: BR-007 / BR-008 amended for DEC-F4 (FRD-CM-001 Batch 1 LOCKED remains unchanged).

## [1.0.0] - 2026-07-29

### Notes

- Final Production promotion of branch `release/v1.0.0` at commit `6cb12fe`.
- RC line: `v1.0.0-rc2` → `v1.0.0-rc3` → `v1.0.0-rc4` → **`v1.0.0`**.
- Supersedes the premature local annotated tag formerly named `v1.0.0` on `bbe4504` (to be archived as `archive/v1.0.0-2026-07-23-foundation` before retag — see B4 tag migration plan).

### Added

- Production release of foundation stack (`backend/` + `frontend/` + Compose + production proxy profiles).
- Release notes: `docs/releases/v1.0.0.md`.
- Production deployment report: `docs/releases/PRODUCTION_DEPLOYMENT_REPORT.md`.
- Production rollback runbook: `docs/releases/ROLLBACK_v1.0.0.md` (rollback target **`v1.0.0-rc4`**).
- Production deployment checklist: `docs/deployment-checklist.md` (v1.0.0).
- Sprint R6-03: production configuration hardening — structured startup validation (`ConfigValidationError`), `ENVIRONMENT=test`, config CLI (`scripts/validate-production-config.py`), deployment docs under `docs/deployment/`, report `docs/releases/R6-03_PRODUCTION_CONFIGURATION_REPORT.md`.
- Release blocker B2: separate `GET /live` (liveness) and `GET /ready` (readiness with startup + DB `SELECT 1`, HTTP 503 when not ready). Docker healthchecks call `/ready`.
- Release blocker B3: production reverse proxy + TLS reference — Caddy (`docker-compose.prod.yml`, automatic HTTPS), Nginx alternative (`docker-compose.prod.nginx.yml`), proxy configs under `deploy/proxy/`, guide `docs/deployment/TLS_REVERSE_PROXY.md`, `.env.production.example`.
- Internationalization (i18n) infrastructure restored on the dashboard UI (`en` / `id`).
- Capability surface: Auth (incl. password management), Complaints, Assignment, Escalation, Resolutions, Appointments, Timeline, Queue, SLA, Attachments, Notifications, Search, Reporting/KPI/Dashboard, Users/IAM, Branches/Customers, Settings, Audit.

### Changed

- Application version set to **1.0.0** (backend, frontend, OpenAPI `info.version`, API Catalog).
- Promoted from Release Candidate **v1.0.0-rc4** after Identity, configuration, health, and TLS readiness gates.
- CI workflows support feature and release branches; release pipeline stabilized for Alembic head and npm audit.
- Legacy frontend password-policy module retired in favor of shared auth routes / backend policy.

### Security

- Sprint R6-03: fail-fast rejects localhost/non-HTTPS CORS origins in production, misaligned password-reset base URL vs `ALLOWED_ORIGINS`, unknown `EMAIL_PROVIDER` / `JWT_ALGORITHM`, and `DEBUG=true` outside development/test.
- Release blocker B3: production compose publishes only proxy ports 80/443; HSTS at edge; `FORWARDED_ALLOW_IPS` + uvicorn `--proxy-headers` / `--forwarded-allow-ips` for trusted `X-Forwarded-*`.
- Production JWT secret rotation required before go-live (secret guard enforced).
- TLS termination at reverse proxy for Secure refresh cookies.

### Known Limitations

- No MFA, SSO/OAuth/OIDC, LDAP, or social login.
- Production SMTP depends on configured `EMAIL_PROVIDER` (development may use `logging`).
- In-memory login lockout is per-process (multi-replica deployments do not share counters).
- No mobile client; no broker-backed enterprise event bus in the Compose foundation stack.
- Role→permission map is code-seeded until Core Platform SoT (API-062).
- ECMP is not Customer Master SoR (no Customer Master write-back).

## [1.0.0-rc4] - 2026-07-28

### Added

- Sprint R6-02B/C: Change / Forgot / Reset Password UI (API-410…412).
- Admin Reset Password on Users page (API-413) with one-time temporary password UX.
- `PASSWORD_CHANGE_REQUIRED` force-change redirect (no lockout loop).
- Release notes: `docs/releases/v1.0.0-rc4.md`; UAT evidence under `docs/verification/` and `docs/uat-r6-02b-evidence.json`.

### Security

- Production fail-fast: no localhost `PASSWORD_RESET_FRONTEND_BASE_URL`; no `EMAIL_PROVIDER=logging` outside development.

### Known Limitations

- Temporary password from admin reset is shown once in the UI and cannot be re-fetched.
- Access JWTs expire naturally after password change (~15 minutes); refresh tokens are revoked immediately.
- HTTPS termination and R6-03 production config hardening deferred to final `v1.0.0`.

## [1.0.0-rc3] - 2026-07-28

### Added

- Sprint R6-02: Identity & RBAC consolidation into source (password management APIs, preferred language, admin RBAC repair migrations **0037–0039**).
- Password policy helpers, email module scaffolding, force-password-change flows.
- Role assignment policy and primary-role sync hardening.
- Release artifact provenance / clean-tree RC gate (R6-01).
- Identity & RBAC UAT harness: `docs/verification/r6_02_identity_rbac_uat.py`.

### Security

- Auth/IAM path consolidation for password change, reset, and admin reset contracts.
- Production-oriented guards for password-reset configuration introduced with Identity domain.

### Known Limitations

- End-to-end password management UI and admin reset UX completed in **v1.0.0-rc4**.

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

- Sprint R1-03: refreshed release notes / RC gate report for v1.0.0 scope + Postgres test evidence (910 passed / 0 failed / 0 skipped / 87% coverage).
- `.env.example` documents local DEVELOPMENT convenience credentials and R2/R3 required production overrides.
- Root frontend `package.json` adds `typecheck` script for CI.

### Known Limitations

- In-memory login lockout is per-process (multi-replica deployments do not share counters).
- Local Compose still embeds browser-reachable `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000` when explicitly set in `.env` (required for local stack; not a silent default).

## 1.0.0-rc1 - 2026-07-23

### Notes

- Historical foundation Release Candidate documentation (`docs/releases/v1.0.0-rc1.md`). Git tag `v1.0.0-rc1` was never published; section is intentionally unlinked in the footer. Do not use as a rollback target.

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

- No MFA, SSO/OAuth, LDAP, password reset, social login (password reset delivered in later RCs).
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

[Unreleased]: https://github.com/hutbeon-hub/ECMP/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/hutbeon-hub/ECMP/releases/tag/v1.0.0
[1.0.0-rc4]: https://github.com/hutbeon-hub/ECMP/releases/tag/v1.0.0-rc4
[1.0.0-rc3]: https://github.com/hutbeon-hub/ECMP/releases/tag/v1.0.0-rc3
[1.0.0-rc2]: https://github.com/hutbeon-hub/ECMP/releases/tag/v1.0.0-rc2
[0.8.0-rc.1]: https://github.com/hutbeon-hub/ECMP/releases/tag/v0.8.0-rc.1
