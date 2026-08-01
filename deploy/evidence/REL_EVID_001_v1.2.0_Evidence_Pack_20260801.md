# REL-EVID-001 Evidence Pack — ECMP v1.2.0 candidate (updated)

| Field | Value |
|---|---|
| ID | REL-EVID-001 / v1.2.0-prep |
| Date | 2026-08-01 (updated after closure attempt) |
| Candidate | `v1.2.0-rc.1` @ `6890f50` |
| Result | **INCOMPLETE for production GO** |

## 0. Release identity

| Field | Value |
|---|---|
| Version / tag (candidate) | `v1.2.0-rc.1` (final `v1.2.0` not cut) |
| Git commit SHA | `6890f50d8243ba30589a3d88f0c0efcef791ce01` |
| Target | production (requested) |
| Compose | `docker-compose.prod.yml` |
| IMAGE_TAG / APP_VERSION | `1.2.0-rc.1` |

## 1. Configuration validator

| Item | Value |
|---|---|
| Result | **FAIL** (5 AuthN/OIDC issues) |
| Closure attempt | `PROD_CFG_CLOSURE_v1.2.0_20260801.md` |
| Compose config | **FAIL** (OIDC_JWKS_URL required); ACME fallback **PASS** |

## 2. Security tests

| Item | Value |
|---|---|
| Result | **PASS** — 169 passed, 3 skipped |

## 3. Authentication

| Item | Value |
|---|---|
| jwt + OIDC | **No** — contract BLOCKED |
| Login/refresh prod smoke | **Not run** |

## 4. Audit

| Item | Value |
|---|---|
| Platform audit acknowledged | Yes |
| Destructive maintenance planned | No |

## 5. Backup

| Item | Value |
|---|---|
| Result | **PASS** |
| Evidence | `OPS_BAK_EVID_v1.2.0_20260801.md` |
| SHA-256 | `31a4fa582f99d0e851fe4ae689dd36bae81fd43f39cfded65e714f1bb0457b6a` |

## 6. Recovery

| Item | Value |
|---|---|
| Lab evidence | **PASS** — `OPS_RCV_EVID_v1.2.0_20260801.md` |
| Prod jwt restore smoke | **Blocked** |

## 7. Smoke

| Item | Value |
|---|---|
| Lab | PASS |
| Prod jwt | Blocked |

## 8. Approvals (REL-APR-001)

See `REL_APR_OPS_EVID_v1.2.0_20260801.md` — all required roles **No-Go**.

## 9. Decision

**NO-GO** for production release `v1.2.0`.
