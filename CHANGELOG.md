# Changelog

All notable changes to the ECMP application/repository release line are documented here.
API contract versioning remains governed by ADR-006 and OpenAPI `info.version`
(see `16 Release Management/ECMP_Release_Management_v0.1.md` §1).

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Repository versioning follows [SemVer](https://semver.org/) as defined in
`16 Release Management/ECMP_Repository_Versioning_Policy_v0.1.md`.

## [Unreleased]

### Notes

- Post-v1.0.0: only hotfixes and approved change requests.

## [1.0.0] - 2026-07-23

### Added

- Production release of foundation stack (`backend/` + `frontend/` + Compose).
- Release notes: `docs/releases/v1.0.0.md`.
- Production deployment report: `docs/releases/PRODUCTION_DEPLOYMENT_REPORT.md`.
- Production rollback runbook: `docs/releases/ROLLBACK_v1.0.0.md`.
- Production deployment checklist: `docs/deployment-checklist.md` (v1.0.0).

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
- No email/WebSocket notifications; no mobile client.
- Role→permission map is code-defined until Core Platform SoT (API-062).
- Foundation health probe is combined `GET /health` (not separate `/health/live` + `/health/ready` paths).
- Resolve/Close complaint transition APIs are not in foundation OpenAPI (status changes via assign/escalate only).

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

[Unreleased]: https://github.com/nandeshut/ECMP/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/nandeshut/ECMP/releases/tag/v1.0.0
[1.0.0-rc1]: https://github.com/nandeshut/ECMP/releases/tag/v1.0.0-rc1
[0.8.0-rc.1]: https://github.com/nandeshut/ECMP/releases/tag/v0.8.0-rc.1
