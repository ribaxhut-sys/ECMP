# ECMP Platform — CI Coverage Gate Restore (≥90%)

| Field | Value |
|---|---|
| Document ID | GOV-PLATFORM-CI-COV-001 |
| Date | 2026-07-29 |
| Status | 🟢 Complete |
| Epic | EPIC-PLATFORM |
| Task | TASK-PLATFORM-CI-COV-001 |

## Objective

Restore measured `app` coverage to **≥90%** and enforce the gate in CI / `pyproject.toml` (Test Strategy / DoD). Tests and gate only — no business-logic, migration, or API contract changes.

## Baseline → Result

| Metric | Before | After |
|---|---|---|
| Total coverage (branch-inclusive) | ~86.85–89.75% | **90.59%** |
| Suite | — | **1128 passed**, 170 warnings |
| Gate | `--cov-fail-under=86` (had drifted) | `--cov-fail-under=90` |

Evidence DB: throwaway `ecmp_ci_qa` on `localhost:5433`.

## Changes

### Gate (already aligned)

- `.github/workflows/backend-ci.yml` — `--cov-fail-under=90`
- `backend/pyproject.toml` — `[tool.coverage.report] fail_under = 90`

### Tests added (coverage only)

- `backend/tests/test_async_session.py`
- `backend/tests/test_users_repository_coverage.py`
- `backend/tests/test_platform_coverage_boost.py`
- `backend/tests/test_platform_repo_coverage.py`
- `backend/tests/test_users_schema_coverage.py`
- `backend/tests/test_sla_repository_coverage.py`
- `backend/tests/test_platform_cov_batch2.py`
- `backend/tests/test_platform_cov_final_push.py`
- `backend/tests/test_platform_cov_90_gate.py` (final push past 90%)

## Explicit non-changes

- No OpenAPI / Event Catalog edits
- No Alembic revisions
- No product feature behavior changes
- No ADR-012 / Keycloak / F4 / outbox publisher work

## Verification command

```powershell
$env:DATABASE_URL = "postgresql+psycopg://ecmp:ecmp@localhost:5433/ecmp_ci_qa"
python -m pytest -q --cov=app --cov-report=term --cov-fail-under=90 --tb=no
# Required test coverage of 90% reached. Total coverage: 90.59%
# 1128 passed
```

---

*End of GOV-PLATFORM-CI-COV-001.*
