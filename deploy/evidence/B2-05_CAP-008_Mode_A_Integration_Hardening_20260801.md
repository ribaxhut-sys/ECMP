# B2-05 — CAP-008 Mode A Integration Hardening / Release Readiness

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Sprint | B2-05 Integration Hardening Release Readiness |
| Capability | CAP-008 Case Management (Batch-2 Mode A) |
| Branch | `feature/cm-batch1-s2-persistence` |
| Tip assessed | `b079079` (working tree **dirty**; CAP-008 mostly **untracked**) |
| Assessor | Release Engineering (lab) |
| Verdict | **NOT READY FOR RC** |

> Scope: validate end-to-end against repository SoT. No FRD / OpenAPI / Business Rules changes. No feature work.

## Checklist results

### 1. Frontend → Backend → Database integration

| Check | Result | Evidence |
|---|---|---|
| Backend CAP-008 TestClient lifecycle | **PASS** | `tests/test_cm_case_mode_a.py` — 9 passed |
| Frontend CAP-008 Vitest | **PASS** | `cmCase.test.ts` + `features/cases/*` — 9 passed |
| Frontend typecheck | **PASS** | `tsc --noEmit` exit 0 |
| Router wiring (source) | **PASS** | `app/api/router.py` includes `cm_case_router` |
| Live lab FE→BE→DB | **FAIL** | Running `ecmp-backend` image (2026-07-31) has **no** `cm_case` / `cm_batch1`; Alembic **0036**; `POST /api/v1/cm/cases` → **404** |

### 2. Migration 0046 up / down

| Check | Result | Evidence |
|---|---|---|
| Upgrade `→ 0046_cm_case_management` | **PASS** | Disposable DB `ecmp_b205_mig`; tables `cm_cases`, `cm_case_resolutions`, `cm_case_number_counters` |
| Downgrade `0046 → 0045` | **PASS** | `downgrade` present in migration; tables dropped |
| Re-upgrade to head | **PASS** | Back to `0046_cm_case_management` |
| Lab Postgres | **FAIL** | Production lab DB still at `0036_search_indexes` |

### 3. Authorization / Permission / Authentication

| Check | Result | Notes |
|---|---|---|
| Endpoint permission guards (source) | **PASS** | `complaints:create` / `read` / `update` on CAP-008 routes |
| Mode A credential routes guard | **PASS** | `check-mode-a-credential-routes.mjs` — 5/5 PRESENT (Mode A allowed) |
| Automated 401/403 CAP-008 cases | **GAP** | Not present in `test_cm_case_mode_a.py` (happy-path override only) |
| Live AuthN against CAP-008 | **BLOCKED** | Routes absent on running image |

### 4. Regression Batch-1 + CAP-008

| Check | Result | Evidence |
|---|---|---|
| Batch-1 + CAP-008 + alembic-head pins | **PASS** (after head-pin harden) | 114 passed (`/tmp/b2-05-pytest-final.txt`) |
| FE Batch-1 upload contract | **PASS** | `cmBatch1.upload.test.ts` — 3 passed |

### 5. Audit / Logging / History / Side Effects

| Capability | Status |
|---|---|
| Production side effects | **IMPLEMENTED** — `AuditTimelineSideEffects` (Audit + Complaint Timeline); wired in `get_case_service` |
| Resolution history | **IMPLEMENTED** — `cm_case_resolutions` + DTO `resolutionHistory` |
| Notification / Assignment / SLA / Event engines | **OUT OF SCOPE** (Mode A) — service module documents no engines |
| Idempotency-Key mandatory | **NOT SPECIFIED** for Mode A (header accepted, unused) |
| Automated audit assertions in CAP-008 tests | **GAP** — API tests use `NoOpSideEffects` |

### 6. Performance smoke / basic load

| Check | Result |
|---|---|
| Repo-supported k6/locust (or equivalent) for CAP-008 | **NOT SPECIFIED** / backlog per `13 Test Strategy/ECMP_Test_Strategy_v0.1.md` §6 (SIT blocker ADR-010) |
| Action | Reported only — **not invented** |

### 7. Security / Validation / ProblemDetails / Access Control

| Check | Result | Notes |
|---|---|---|
| Domain validation errors (ApiError codes) | **PASS** | e.g. `ASSIGNED_USER_NOT_ALLOWED_MODE_A`, `MAX_CASES_EXCEEDED`, `STATE_NOT_EXPOSED_MODE_A` |
| Platform error envelope | **PASS (platform)** | `{code,message,details}` via `ApiError` handler |
| OpenAPI `application/problem+json` media type | **DRIFT (known platform)** | Catalog declares problem+json; runtime uses JSON envelope — same as Batch-1 RC posture; OpenAPI not modified in this sprint |
| Security headers smoke | **PASS** | `tests/test_security_headers.py` with CAP-008 suite |

### 8. Release readiness (deploy / config / environment)

| REL-RC-001 item | Result |
|---|---|
| Working tree clean / freeze commit | **FAIL** — CAP-008 sources largely untracked; branch dirty |
| CHANGELOG RC section for CAP-008 | **FAIL** — no CAP-008 / 0046 section |
| Annotated RC tag | **FAIL** — not cut |
| Lab image + Alembic ≥ 0046 | **FAIL** — image stale @ 0036 |
| Lab `/health` environment label | **RISK** — reports `environment=production` on Mode A lab stack (S-03 class) |
| `validate-production-config.py` on host | **N/A host** — host Python lacks app deps; `.env.production.example` correctly requires `ECMP_AUTH_MODE=jwt` |

## Remaining release blockers (ordered)

1. Freeze CAP-008 SoT: commit tracked sources; clean tree for REL-RC-001.
2. Rebuild/redeploy lab backend+frontend from current tip; run Alembic to `0046_cm_case_management`.
3. Add CHANGELOG RC section + REL-RC-001 assessment/sign-off for CAP-008 Mode A.
4. (Recommended) CAP-008 automated 401/403 + AuditTimelineSideEffects assertion tests.
5. Align lab `ENVIRONMENT` label with Mode A auth posture before any promote language.

## Explicit non-blockers for internal lab RC (once 1–3 close)

- Full browser E2E (Test Strategy: not required for RC1).
- k6/locust performance (backlog until SIT).
- Mode B / OIDC go-live.
- Notification / Assignment / SLA / Event engines (Mode A out of scope).
