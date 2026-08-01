# Changelog

All notable changes to the ECMP application/repository release line are documented here.
API contract versioning remains governed by ADR-006 and OpenAPI `info.version`
(see `16 Release Management/ECMP_Release_Management_v0.1.md` §1).

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Repository versioning follows [SemVer](https://semver.org/) as defined in
`16 Release Management/ECMP_Repository_Versioning_Policy_v0.1.md`.

## [Unreleased]

### Notes

- Post-`v1.2.0-rc.1`: only hotfixes and approved change requests (new SemVer PATCH or new `rc.N` per versioning policy).

## [1.2.0-rc.1] - 2026-08-01

### Notes

- Mode A **CAP-008 Case Management** Release Candidate `v1.2.0-rc.1` (lab / Batch-2 Mode A).
- Authorized ref (B-2 Option B pattern): `feature/cm-batch1-s2-persistence` @
  `b7d8e2cee864263ff92a1941a9181a629ce46550` (`b7d8e2c`).
- Assessment: `deploy/evidence/REL_RC_001_CAP-008_Mode_A_Assessment_20260801.md` — **PASS (lab)**.
- Scope: internal/lab DEV validation of CAP-008 Mode A (FR-001…FR-006) — **not** Production /
  Mode B / Enterprise Platform / Notification·Assignment·SLA·Event engines.
- Alembic head for this RC: `0046_cm_case_management`.
- Annotated tag `v1.2.0-rc.1` (never move tags).

### Added

- CAP-008 Mode A Case Management: backend module `backend/app/modules/cm_case/`
  (create / get / status / resolve / close), Alembic `0046_cm_case_management`
  (`cm_cases`, `cm_case_resolutions`, `cm_case_number_counters`).
- CAP-008 OpenAPI catalog (engineering SoT): `07 API Catalog/openapi/cm-case-management.v1.yaml`.
- CAP-008 frontend surfaces: `frontend/src/features/cases/`, routes under
  `frontend/src/app/(app)/complaints/cm/cases/`, client `frontend/src/lib/api/cmCase*.ts`.
- CAP-008 Mode A tests: `backend/tests/test_cm_case_mode_a.py` (lifecycle + 401/403 +
  `AuditTimelineSideEffects`); FE `cmCase.test.ts`.
- Integration hardening evidence: `deploy/evidence/B2-05_CAP-008_Mode_A_Integration_Hardening_20260801.md`.
- REL-RC-001 assessment: `deploy/evidence/REL_RC_001_CAP-008_Mode_A_Assessment_20260801.md`.

### Changed

- Router wiring: `backend/app/api/router.py` mounts CAP-008 `cm_case` router.
- Frontend API barrel exports CAP-008 clients (`frontend/src/lib/api/index.ts`).
- Alembic head-pin tests updated for `0046_cm_case_management`.

## [1.1.0-rc.1] - 2026-08-01

### Notes

- Mode A Batch-1 **Release Candidate** `v1.1.0-rc.1` (lab / W-SOD-1).
- Authorized ref (B-2 Option B): `feature/cm-batch1-s2-persistence` @ `16082454659d7f511e5296d0bd9531185766e6db` (`1608245`).
- External decisions: B-1 Option A; B-2 Option B; U-5 COMPLETE; QA/TL COMPLETE; REL-RC-001 §5 Go (`EXT-HD-RC-MA-B1-20260801`).
- Scope: internal/lab DEV validation — **not** Production / Mode B / Enterprise Platform.
- Annotated tag prepared; create only when explicitly permitted (never move tags).

### Added


- Mode A **M3d**: EX-G later-review `complaintId` (nullable) on API-513 — Alembic `0045`; bind-failure enqueue anchors Aggregate Complaint; supervisor UI deep-link. Degraded duplicate pre-create remains `null`. No Case create / Mode B.
- Mode A **M3c**: Module Lab COMPLETE Evidence Pack — `18 Architecture Governance/ECMP_PROGRAM_MODE_A_M3C_Module_Lab_COMPLETE_Evidence_Pack_v1.0.md` (GOV-MODEA-M3C-001). Claim = lab/synthetic Batch-1 COMPLETE under BR-008; **not** Mode B / Batch-2 / real-customer Production Ready.
- Mode A **M3b HARDENED**: API-513 supervisor queue end-to-end round-trip + edge cases (empty, limit cap, aging threshold boundary, unknown reason pass-through); FE `cmBatch1SupervisorQueue` contract helpers. No resolve / Case create / Mode B.
- Mode A **M3b** later-review / aging visibility: `API-513` `GET /api/v1/cm/supervisor/queue` + FE `/complaints/cm/supervisor` (OPEN work items + no-Case aging; read-only; no Case create / M4 / Mode B).
- Mode A **M3 CLOSED (intake)**: Batch-1 Aggregate UI — create/confirm, customer search/confirm/360, duplicate panel, FR-004 staging upload + logical void, confirmation bound attachments (API-507…512 / DEC-020 coexistence). Foundation list unchanged (no Retirement DEC).
- Mode A Batch-1 AC harden: **TD-CM-001 / EX-D** — confirm lock enforced on `POST /api/v1/cm/complaints`; FR-004 AC3 lab malware-reject test. Shared cron **not** started.
- Mode A **M6** Complaint ops hygiene: `backend/scripts/cm_batch1_ops_hygiene.py` (storage probe + abandoned staging TTL void) + runbook `15 Operations Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md`. TD-OPS-002 password drift remains deferred; Mode B CLOSED.
- PROGRAM-BOARD-008: Architecture Board **draft pack** — EA-TARGET-CM-001 + EA-PLATFORM-001 under `04 Solution Architecture/board-drafts/` (lifecycle DRAFT; **not** implementation tickets); HOST Gate binding recommendation; companion **DTM-001** (`26 Traceability/ECMP_DTM_001_Decision_Traceability_Matrix_v0.1.md`). Mode B remains CLOSED (C-B6-1 / C-7).
- PROGRAM-SAFE-NEXT-001: prioritized safe queue P1–P4 — org-gap delivery plan, EP bilateral review pack, DEC-021/022 (O-06/O-07 Proposed), Mode A next-work priority; Mode B remains CLOSED.
- PROGRAM-ENTERPRISE-PROFILES-001: Draft subordinate profiles (no Mode B coding) — Binding OIDC (`SEC-BIND-OIDC-001`), Entitlement representation (`SEC-ENT-REP-001`), Org Sync integration (`SEC-ORG-SYNC-001`); pack `18 Architecture Governance/ECMP_PROGRAM_ENTERPRISE_PROFILES_001_Subordinate_Profiles_Draft_Pack_v0.1.md`. Mode B CLOSED (C-B6-1); org-gap prerequisite remains (C-B6-3).
- PROGRAM-BOARD-006 (`18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`): **Accept With Conditions** ADR-016/017/018 (**BR-011** / **BR-012** / **BR-013**); conditions C-B6-1…C-B6-7; Mode B / Batch-2 / enterprise customer remain **CLOSED**; org-gap Mode B prerequisite (C-B6-3) adopted.
- PROGRAM-BOARD-005 (`18 Architecture Governance/ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_v1.0.md`): Architecture Board Review **CONVENED** — ADR-016/017/018 package **Ready for Resolution**; recommended conditions RC-1…RC-7 for BOARD-006; **no Accept**; Mode B CLOSED (C-7).
- Audit **K-5** / **K-7**: ADR-016/017/018 rev 1.0a close ADR-018 §14 profile fail-open and align subordination to ADR-016 §9.3; ADR-014 1.4a + `ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md` elevate org-model gap to **Mode B unlock prerequisite**. ADRs 016–018 remain Proposed; Mode B CLOSED (C-7).
- Audit **K-4** closed (shared-profile): OPS-RST-EVID-20260730-SHARED — writers stopped, restore to `ecmp_k4_shared_restore`, `ECMP_ENV=shared` + `ECMP_AUTH_MODE=jwt` + Keycloak IdP, `/live` `/ready`, local credential disabled, IdP `/auth/me` PASS; SO delegate via Project Owner instruction with C-K4 conditions (no production cutover / Mode B unlock).
- Audit **K-6**: program identity records under `18 Architecture Governance/` — ENTERPRISE-001 PHASE-0/1A, PROGRAM-ADR-004, PROGRAM-DOC-001, PROGRAM-IMPLEMENTATION-001, PROGRAM-BOARD-005/006 **Pending** stubs (no invented Accept / Mode B unlock).
- Audit **K-4** progress: foundation lab restore evidence `15 Operations Runbook/evidence/restore-drill-20260730/` (OPS-RST-EVID-20260730) — procedure PASS with `/live` `/ready` + dual audit tables; **does not** close shared-env RR-1 (SO sign-off pending).
- AUDIT K-3 / AEN-03: Mode A credential-route build guard — `frontend/scripts/check-mode-a-credential-routes.mjs` + Root FE CI inventory/self-test; backend `ECMP_LOCAL_CREDENTIAL_AUTH` / `ECMP_ENTERPRISE_MODE` fail-fast (staging/production + enterprise) and runtime gate on login/forgot/reset/change/admin-reset. Mode B remains CLOSED (C-7).
- AUDIT-ADD-20260730-F0 (`18 Architecture Governance/ECMP_AUDIT_ADDENDUM_Independent_Program_Audit_20260730_Fase0_v1.0.md`): addendum Independent Program Audit 2026-07-30 — Fase 0 / K-1 / K-2 / **K-3** marked **REMEDIATED**; K-4…K-8 and missing BOARD-005/006 remain open; Mode B CLOSED (C-7).
- FE-CI-POL-001 Phase C: coverage hard-fail live in `root-frontend-ci.yml` (thresholds ≥40% lines/statements); expanded unit tests (`fileTypes`, `quickActionConfig`, `passwordPolicy`) — 29 tests.
- FE-CI-POL-CS-001 / FE-CI-POL-001 **v1.0**: countersign record — **Accepted with Conditions** (Project Owner chat instruction 2026-07-30). Closes OD-FE-003 / 009 (working target) / 010. Mode B remains CLOSED; no WCAG conformance claim granted.
- Mode A FE a11y smoke: axe-core suite (`npm run test:a11y`) on Button/Alert/Input/Breadcrumb; Root Frontend CI warn-mode; expanded unit tests for `cn` + `APP_NAV_ITEMS`.
- Mode A FE unit harness: Vitest + Testing Library; helper tests; `npm run test:coverage` in Root Frontend CI (warn-mode per FE-CI-POL-001 / OD-FE-010 Phase B).
- Mode A Reports UI (`frontend/src/features/reports/`): wires API-210…212 with `reports:read` gate; reuses dashboard by-status / by-branch widgets.
- FE Root CI Phase B partial: ESLint CLI hard-gate + npm audit warn in `root-frontend-ci.yml` (FE-CI-POL-001 progress; OD-FE-003 still Proposed pending countersign).
- FE-CI-POL-001 (`docs/frontend/FRONTEND_CI_QUALITY_POLICY_v0.1.md`): **Proposed** Root Frontend CI quality policy for OD-FE-003 / OD-FE-009 / OD-FE-010 (phased gates; WCAG 2.2 AA recommendation pending UX; coverage warn/fail thresholds pending Tech Lead). Mode A only — no Mode B unlock; no CI hard-gate added until lint toolchain/env ready.
- PROGRAM-GOV-001 PHASE-1: repository navigation links for `docs/frontend/` and ADR portal mirror (`00 Repository Guide/REPOSITORY_INDEX.md`, `OWNERSHIP_MATRIX.md`).
- PROGRAM-GOV-001 PHASE-1: ADR lifecycle documents `Rejected` status (`18 Architecture Governance/README.md`, `24 Templates/ADR_TEMPLATE.md`, `STATUS_BADGES.md` note).
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

- PROGRAM-BOARD-004 **F-3** governance sync (documentation only): FE-ARCH / FE-STD / OPEN_DECISIONS / FE docs hub — ADR-014 v1.4 / ADR-015 v1.3 cited as **Accepted with Conditions** (BR-009 / BR-010); LAP-01..03 Pending Upstream **retired** → Locked; **OD-FE-008 CLOSED**. Mode B / Batch-2 / enterprise customer remain **CLOSED** (C-7). No Mode B AuthN, OpenAPI enterprise securitySchemes, or application code changes.
- PROGRAM-ADR-004 Board Readiness Revision Package: ADR-014 → v1.4, ADR-015 → v1.3 (editorial/governance clarifications only — notification ownership split, Containment Principle, Mode A→B cutover stance, org-model gap consequence, role-mapping governance, protocol deferral for aud/iss, hierarchy assumption, PII projection, audit correlation deferral). Disposition **Revised — Pending Board Review**; lifecycle remains **Proposed** (not Accepted). Mode B / Batch-2 / enterprise customer / OpenAPI contracts **not** unlocked. Prior package ID PROGRAM-ENTERPRISE-001 superseded as active authoring program ID by PROGRAM-ADR-004 (historical notes retained).
- PROGRAM-ENTERPRISE-001 FINAL EDITORIAL PACKAGE: ADR-014 → v1.3, ADR-015 → v1.2 (editorial only — ADR-012 disposition disclosure, terminology table, Identity SoT de-duplication, SEC-PWD-001 cross-refs, Board Resolution traceability); no architecture or Board decision changes.
- PROGRAM-ENTERPRISE-001 PHASE-2: coordinated ADR revision package — ADR-014 → v1.2, ADR-015 → v1.1 (Proposed, Needs Revision preserved; Identity Contract SoT = ADR-015; Role-Permission SoT = ADR-008; no supersession of ADR-013/007/012).
- PROGRAM-ADR-002 PHASE-0 (Board Resolution execution): canonical ADR lifecycle + Architecture Documents lifecycle recorded; FE-ARCH-001 / FE-STD-001 → **BASELINE**; ADR-013 remain active; ADR-014/015 Board Disposition **Needs Revision** (references/metadata only); Implementation Authorization **AUTHORIZED WITH CONDITIONS**. Traceability record: `18 Architecture Governance/ECMP_PROGRAM_ADR_002_Board_Resolutions_v1.0.md`.
- PROGRAM-GOV-001 PHASE-1 (administrative sync only): ADR indexes aligned for **ADR-012 Accepted** and full ADR-001..015 listing (`05 Architecture Decision Records/README.md`, `docs/architecture/adr-index.md` v0.3).
- PROGRAM-GOV-001 PHASE-1: stale ADR-012 “Proposed” references corrected in FE-ARCH traceability, ADR-013 numbering note, Solution Architecture, and SEC-AUTH-001 parenthetical (document Status badge not flipped).
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

[Unreleased]: https://github.com/hutbeon-hub/ECMP/compare/v1.1.0-rc.1...HEAD
[1.1.0-rc.1]: https://github.com/hutbeon-hub/ECMP/compare/v1.0.0...v1.1.0-rc.1
[1.0.0]: https://github.com/hutbeon-hub/ECMP/releases/tag/v1.0.0
[1.0.0-rc4]: https://github.com/hutbeon-hub/ECMP/releases/tag/v1.0.0-rc4
[1.0.0-rc3]: https://github.com/hutbeon-hub/ECMP/releases/tag/v1.0.0-rc3
[1.0.0-rc2]: https://github.com/hutbeon-hub/ECMP/releases/tag/v1.0.0-rc2
[0.8.0-rc.1]: https://github.com/hutbeon-hub/ECMP/releases/tag/v0.8.0-rc.1
