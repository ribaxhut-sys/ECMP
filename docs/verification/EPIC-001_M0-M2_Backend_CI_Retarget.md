# EPIC-001 M0–M2 Verification Report — Backend CI Retarget

| Field | Value |
|---|---|
| Epic | EPIC-001 CI/CD Foundation Refactoring |
| Scope | M0 Decision Freeze · M1 Backend CI Retarget · M2 Tooling Bootstrap |
| Date | 2026-07-25 |
| Status | Complete (analysis + implementation for M0–M2 only) |
| Decision | [DEC-019](../../27%20Project%20Decisions/DEC-019_Engineering_Foundation_Canonical_Trees_EPIC001_v1.0.md) |

## Deliverables

| # | Artifact | Status |
|---|---|---|
| 1 | `.github/workflows/backend-ci.yml` | Updated — targets `backend/` |
| 2 | `backend/requirements-dev.txt` | Added — pinned tools |
| 3 | `backend/pyproject.toml` | Added — Ruff (+ pytest/coverage metadata) |
| 4 | This verification report | Done |
| 5 | Future work M3–M7 | Listed below |
| — | `27 Project Decisions/DEC-019_…md` | M0 decision freeze |

## M0 — Decision freeze (confirmed)

| Tree | Role |
|---|---|
| `backend/` | Production backend (canonical CI target) |
| `frontend/` | Production frontend (canonical; CI retarget = M3+) |
| `implementation/backend/` | Legacy Sprint-01 track — **removed from Backend CI** |
| `implementation/frontend/` | Legacy Vite track — out of Backend CI |

Python: **3.13** (aligned with `backend/Dockerfile`).

## M1 — Backend CI retarget (confirmed)

Workflow evidence:

- Triggers only: `backend/**`, `07 API Catalog/openapi/**`, `.github/workflows/backend-ci.yml`
- `defaults.run.working-directory: backend`
- Removed from Backend CI: `implementation/backend`, `tools`, `implementation/portal`
- Kept: OpenAPI validation, Alembic `upgrade head`, pytest + coverage, pip-audit on `backend/requirements.txt`

## M2 — Tooling bootstrap (confirmed)

| Tool | Pin | Notes |
|---|---|---|
| Python (CI) | 3.13 | Matches `python:3.13-slim` |
| ruff | 0.12.5 | Config: `backend/pyproject.toml` |
| pytest-cov | 6.2.1 | Coverage gate remains 90% |
| openapi-spec-validator | 0.7.2 | Product + draft specs under OpenAPI catalog |
| PyYAML | 6.0.2 | Spec load |
| pip-audit | 2.9.0 | security-audit job |

Ruff discovery (local):

```text
Settings path: "<repo>/backend/pyproject.toml"
```

## Verification matrix

| Check | Result | Evidence |
|---|---|---|
| Backend CI targets `backend/` | **PASS** | `working-directory: backend`; path filters |
| Complaint tests are executed | **PASS (wired)** | `pytest` runs full `backend/tests/`; modules include 13 `test_complaint*.py` files |
| Queue tests are executed | **PASS (wired)** | Same suite; 5 `test_queue*.py` files |
| Alembic runs against `backend/` | **PASS (wired)** | Step `alembic upgrade head` with cwd `backend`; local `alembic heads` → `0032_complaint_sla` |
| Ruff uses backend configuration | **PASS** | `ruff check --show-settings` → `backend/pyproject.toml` |
| OpenAPI validation | **PASS (local)** | All 7 YAML specs under `07 API Catalog/openapi` validated |
| Complaint/Queue domain unit tests (no Docker) | **PASS (local)** | `test_complaint_domain` + `test_queue_domain` + `test_complaint_application` → **37 passed** |

### Local limitation

Docker Desktop was unavailable during verification, so full Postgres + `alembic upgrade` + full pytest suite could not be executed on this machine. CI on `ubuntu-latest` with the Postgres 16 service is the authoritative full run.

### Lint gate posture

`ruff check app tests` reports **~93 findings** against the new config (mostly I001/F401/B017/E501). Per EPIC-001 constraints (no Complaint/Queue/business fixes in this slice), the lint step is **`continue-on-error: true`**. Config is authoritative; **hard lint gate is follow-up**, not M0–M2.

## Explicit non-goals (not done)

- Portal CI / Tools CI / Docs CI split
- Release pipeline
- Product `frontend/` CI retarget
- Governance doc / AI-facts / CODEOWNERS sync (M6)
- Ruff auto-fix or business-code lint burn-down
- Complaint / Queue / migration code changes

## Future work (M3–M7)

| Phase | Work |
|---|---|
| **M3** | `portal-ci.yml` — `implementation/portal/**` only (lint / smoke) |
| **M4** | `tools-ci.yml` — `tools/**` only (pinned Ruff + unit tests when present) |
| **M5** | `docs-ci.yml` — path-filtered MkDocs/EOS (split from always-on `ear-docs.yml`); optional AI eval gate retained |
| **M6** | Retarget product `frontend-ci.yml` → `frontend/` (Next.js); freeze or legacy-job for `implementation/frontend`; CODEOWNERS + AI facts + README/test-strategy pointer sync |
| **M7** | `release.yml` (tag gates); Ruff hard gate after debt burn-down; optional Docker build artifact in Backend CI; coverage baseline review if 90% fails on first green |

## STOP

M0–M2 complete. Awaiting approval before M3+.
