# Security Test Suite (SECMIG-P5-006)

| Field | Value |
|---|---|
| ID | SEC-TEST-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Related | TASK-PLATFORM-SECMIG-P5-006 |

## Purpose

Selective verification gate for backend **foundation security** coverage after
P5-001A…P5-005. **No runtime behavior changes** — tests and CI documentation only.

## Entry point

From `backend/`:

```bash
python scripts/run_security_tests.py -q
# equivalent:
pytest -m security -q
```

Marker: `@pytest.mark.security` (registered in `pytest.ini` / `pyproject.toml`).

## Included modules

| Module | Scope |
|---|---|
| `tests/test_secmig_p5_*.py` | P5-001A…P5-006 workstreams |
| `tests/test_secmig_p6_secure_config.py` | P6-001 secure configuration baseline |
| `tests/test_login_protection.py` | Login lockout unit |
| `tests/test_authorization_middleware.py` | AuthZ pipeline unit |
| `tests/test_secmig_p2_auth.py` | AuthN JWT / JWKS |
| `tests/test_security_headers.py` | Security headers smoke |

HTTP smoke (Postgres required): lockout → 429 + `Retry-After`; bad Bearer → 401 +
`TOKEN_REJECTED`; permission deny → 403 + `PERMISSION_DENIED`.

## CI

Backend CI already runs the full pytest suite (includes `-m security` tests).
Use the entry point above for a **security-only** job or local pre-merge check:

```bash
cd backend
python scripts/run_security_tests.py -q
```
