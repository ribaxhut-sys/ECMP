# B2-05 — CAP-008 Mode A Integration Hardening / Release Readiness

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Sprint | B2-05 Integration Hardening Release Readiness |
| Capability | CAP-008 Case Management (Batch-2 Mode A) |
| Branch | `feature/cm-batch1-s2-persistence` |
| Tip assessed | `b7d8e2cee864263ff92a1941a9181a629ce46550` (`b7d8e2c`) |
| Assessor | Release Engineering (lab) |
| Verdict | **READY FOR RC** |

> Scope: validate end-to-end against repository SoT. No FRD / OpenAPI / Business Rules changes in release cut. No feature work.

## Checklist results

### 1. Frontend → Backend → Database integration

| Check | Result | Evidence |
|---|---|---|
| Backend CAP-008 TestClient lifecycle | **PASS** | `tests/test_cm_case_mode_a.py` — 12 passed |
| Frontend CAP-008 Vitest | **PASS** | `cmCase.test.ts` + `features/cases/*` — 23 passed |
| Frontend typecheck | **PASS** | `tsc --noEmit` exit 0 |
| Router wiring (source) | **PASS** | `app/api/router.py` includes `cm_case_router` |
| Live lab FE→BE→DB | **PASS** | Images `1.2.0-rc.1`; Alembic `0046`; lifecycle 201/200/200/200/200 |

### 2. Migration 0046 up / down

| Check | Result | Evidence |
|---|---|---|
| Lab Postgres at `0046_cm_case_management` | **PASS** | `cm_cases`, `cm_case_resolutions`, `cm_case_number_counters` |
| Upgrade path from prior lab tip | **PASS** | Entrypoint/upgrade to head on redeploy |

### 3. Authorization / Permission / Authentication

| Check | Result | Notes |
|---|---|---|
| Endpoint permission guards (source) | **PASS** | `complaints:create` / `read` / `update` |
| Mode A credential routes guard | **PASS** | 5/5 PRESENT |
| Automated 401/403 CAP-008 | **PASS** | Added in `test_cm_case_mode_a.py` |
| Live 401 / 403 | **PASS** | unauth → 401; missing create perm → 403 |

### 4. Regression Batch-1 + CAP-008

| Check | Result | Evidence |
|---|---|---|
| Batch-1 + CAP-008 + pins + security headers | **PASS** | 46 passed |

### 5. Audit / Logging / History / Side Effects

| Capability | Status |
|---|---|
| Production side effects | **PASS** — `AuditTimelineSideEffects` wired + unit asserted |
| Resolution history | **IMPLEMENTED** — `cm_case_resolutions` |
| Notification / Assignment / SLA / Event engines | **OUT OF SCOPE** (Mode A) |

### 6. Performance smoke / basic load

| Check | Result |
|---|---|
| k6/locust for CAP-008 | **NOT SPECIFIED** / backlog — not invented |

### 7. Security / Validation / ProblemDetails / Access Control

| Check | Result |
|---|---|
| Domain validation / platform envelope | **PASS** (prior + live) |
| OpenAPI problem+json drift | **DRIFT (known platform)** — OpenAPI not modified in this cut |

### 8. Release readiness

| REL-RC-001 item | Result |
|---|---|
| Working tree clean / freeze commit | **PASS** — `b7d8e2c` |
| CHANGELOG RC section for CAP-008 | **PASS** — `[1.2.0-rc.1]` |
| Annotated RC tag | **PASS** — `v1.2.0-rc.1` |
| Lab image + Alembic ≥ 0046 | **PASS** |
| Lab `/health` environment label | **PASS** — `environment=development` (Mode A) |

## Remaining release blockers

**NONE** for lab CAP-008 Mode A RC.

## Explicit non-blockers

- Full browser E2E
- k6/locust performance
- Mode B / OIDC go-live
- Notification / Assignment / SLA / Event engines
