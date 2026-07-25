# ECMP Smoke Test Report — v1.0.0-rc2

| Field | Value |
|---|---|
| ID | SMOKE-RPT-RC2 |
| Version | **1.0.0-rc2** |
| Date | 2026-07-25 |
| Environment | Local Compose (`ecmp-postgres`, `ecmp-backend`, `ecmp-frontend`) |
| Executor | Release Engineering (Sprint R3) |
| Scope | Backend · Frontend · Database · Authentication · Complaint workflow · Queue workflow |

## Summary

| Area | Result | Notes |
|---|---|---|
| Backend | **PASS** | `GET /health` → `status=ok`, `database=up`, `version=1.0.0`, `environment=production` |
| Frontend | **PASS** | `GET http://localhost:3000/login` → HTTP 200 |
| Database | **PASS** | Postgres 16 healthy; DB `ecmp`; roles/users present |
| Authentication | **PASS** | Login for Admin / Supervisor / Officer (Agent); `/auth/me`; docs disabled (404) |
| Complaint workflow | **PASS** | Create → Get → Assign → Escalate |
| Queue workflow | **CONDITIONAL** | Queue routers present in repo; **not registered in currently running backend image** (61 routes). Re-verify after rebuild from `v1.0.0-rc2`. |

**Overall RC2 smoke (host stack as of 2026-07-25): PASS with Queue rebuild follow-up.**

---

## Backend

| Step | Expected | Result |
|---|---|---|
| Container healthy | `ecmp-backend` healthy | PASS |
| `GET /health` | `status=ok`, `database=up` | PASS |
| Interactive docs in production | `/openapi.json` → 404 | PASS |
| R2 unit guards (host pytest) | settings + login protection | PASS (12) |

## Frontend

| Step | Expected | Result |
|---|---|---|
| Container healthy | `ecmp-frontend` healthy | PASS |
| Login page | HTTP 200 | PASS |
| Typecheck (workspace) | `npm run typecheck` | PASS |

## Database

| Step | Expected | Result |
|---|---|---|
| Postgres healthy | `ecmp-postgres` healthy | PASS |
| Engine | PostgreSQL 16.x | PASS |
| Connectivity | Backend reports `database=up` | PASS |
| Seed roles | `ADMIN`, `SUPERVISOR`, `AGENT`, `VIEWER` present | PASS |

## Authentication

| Account | Login | Result |
|---|---|---|
| `golive_admin` / `GoLive!Admin#2026` | `POST /api/v1/auth/login` | PASS (role `ADMIN`) |
| `golive_supervisor` / `GoLive!Supv#2026` | login + `/auth/me` permissions | PASS |
| `golive_agent` / `GoLive!Agent#2026` (Officer) | login | PASS |
| `golive_viewer` | login | **MISS** — create per UAT accounts guide |

Note: In this environment `golive_admin` returned an empty `permissions[]` from `/auth/me` while still authenticating. Prefer **Supervisor** for operational smoke actions until Admin permission matrix is repaired for that user (see UAT guide).

## Complaint workflow

Executed as `golive_supervisor` against customer `5289872b-4b7b-45c2-a2c1-9e52ad43b8b7`:

| Step | API | Result |
|---|---|---|
| Create | `POST /api/v1/complaints` | PASS → `a6ed525e-…` status `NEW` |
| Read | `GET /api/v1/complaints/{id}` | PASS |
| Assign | `POST …/assign` (`assigneeId` = golive_agent) | PASS → `ASSIGNED` |
| Escalate | `POST …/escalate` (`escalatedToUserId` = golive_engineer) | PASS → `ESCALATED` |
| Reports | `GET /api/v1/reports/summary` | PASS |

## Queue workflow

| Step | Expected | Result |
|---|---|---|
| `GET /api/v1/queues` on running image | List or authz error | **FAIL/404** — route absent in running container |
| Source tree | `queue_api_router` included in `app/api/router.py` | PASS (code present) |
| Follow-up | Rebuild backend from `v1.0.0-rc2` and re-run list/create ticket smoke | **REQUIRED before GO** |

Suggested post-rebuild checks:

1. `GET /api/v1/queues?page=1&pageSize=20` (authorized role)
2. Create queue (if permitted) or use seeded queue
3. Create ticket / call next / complete counter path per OpenAPI queue-service

## Sign-off

| Role | Decision | Date |
|---|---|---|
| Release Engineer | RC2 smoke recorded — Queue rebuild follow-up | 2026-07-25 |
| QA / UAT | _pending_ | |
| Product Owner | _pending_ | |
