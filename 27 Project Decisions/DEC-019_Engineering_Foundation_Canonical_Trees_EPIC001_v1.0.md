# Decision Record — Engineering Foundation Canonical Trees (EPIC-001 M0)

| Field | Value |
|---|---|
| ID | DEC-019 |
| Version | 1.0 |
| Owner | Tech Lead / Principal DevOps |
| Reviewer | Solution Architect |
| Approver | Engineering Manager (delegated via EPIC-001 approval) |
| Status | Approved |
| Last Review | 2026-07-25 |
| Next Review | 2026-10-25 |

- Type: Project Decision (non-ADR)
- Status: Accepted
- Date: 2026-07-25
- Related: EPIC-001 CI/CD Foundation Refactoring (M0–M2)

## Context

The repository contains two parallel application trees. Production Go-Live v1.0.0
ships from root `backend/` + `frontend/` (Compose). Backend CI historically targeted
`implementation/backend/` (Sprint-01 case-service slice), so production Complaint /
Queue code was never exercised by Backend CI.

## Decision

| Tree | Classification | CI owner (EPIC-001) |
|---|---|---|
| `backend/` | **Production backend** (canonical) | `backend-ci.yml` (M1+) |
| `frontend/` | **Production frontend** (canonical) | `frontend-ci.yml` (M3+; not in M0–M2) |
| `implementation/backend/` | **Legacy track** (Sprint-01 case-service) | Out of Backend CI scope |
| `implementation/frontend/` | **Legacy track** (Vite sprint UI) | Out of product Frontend CI scope |

### Runtime Python

Align Backend CI Python with production image: **Python 3.13**
(`backend/Dockerfile` uses `python:3.13-slim`).

### Formatter / linter

Backend uses **Ruff** (pinned) with config under `backend/pyproject.toml`.
Black is not introduced.

## Rationale

- Matches Compose, release notes (`docs/releases/v1.0.0.md`), and live Complaint BC.
- Stops false confidence from greening CI against a non-production tree.
- Leaves legacy tracks in-repo for history without claiming production CI coverage.

## Impact

- `backend-ci.yml` retargets to `backend/` (M1).
- Portal / tools / docs domain CI deferred to M3–M5.
- Governance docs that still point at `implementation/backend` as “the” backend
  remain stale until M6 (explicitly out of M0–M2 scope).

## Follow-up

- M3–M7: portal-ci, tools-ci, docs-ci, frontend retarget, release.yml, governance sync.
- Lint zero-debt hard gate after Ruff burn-down (not part of M0–M2).

## Links

- Production release: `docs/releases/v1.0.0.md`
- Compose: `docker-compose.yml`
- Backend tooling: `backend/requirements-dev.txt`, `backend/pyproject.toml`
