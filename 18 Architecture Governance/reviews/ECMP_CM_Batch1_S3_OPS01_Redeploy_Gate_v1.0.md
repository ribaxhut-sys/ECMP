# ECMP CM Batch 1 — S3 TASK-OPS-01 / 01b Redeploy + HTTP Smoke

| Field | Value |
|---|---|
| Document ID | GOV-S3-CM-B1-OPS01-001 |
| Date | 2026-07-29 |
| Status | 🟢 Complete (local Docker) |
| Epic | EPIC-CM-B1-OPS |
| Tasks | TASK-OPS-01, TASK-OPS-01b |

## Objective

Rebuild/restart local Compose `ecmp-backend` from current sources; verify probes and CM OpenAPI surface; complete HTTP smoke on `:8000` using a working GoLive account **without password resets**.

## TASK-OPS-01 results

| Check | Result |
|---|---|
| `docker compose up -d --build backend` | PASS |
| Entrypoint Alembic | PASS at `0043_cm_batch1_foundation` |
| `GET /health` `/live` `/ready` | 200 |
| OpenAPI `/api/v1/cm/*` | **9 paths** |

## TASK-OPS-01b auth probe (no resets)

| Username | Login | CM usable? |
|---|---|---|
| `golive_admin` | 200 | No — ADMIN has 0 role_permissions; CM search 403 |
| `golive_supervisor` | 200 | **Yes** — `complaints:read` + `complaints:create` |
| `golive_engineer` | 200 | Read-only for create path |
| `golive_scheduler` | 200 | Read-only for create path |
| `golive_agent` | 401 | Documented password drift |
| `golive_viewer` | 401 | Documented password drift |
| `golive_admin22` | 401 | — |

## HTTP smoke (as `golive_supervisor`)

Flow: search → confirm → create → get → replay

| Step | Result |
|---|---|
| `POST /api/v1/cm/customers/search` (`CN-10002`) | 200 → `CUST-10002` |
| `POST /api/v1/cm/customers/confirm` | 200 `locked=true` |
| `POST /api/v1/cm/complaints` + Idempotency-Key | 201 `CM-00000002`, `REGISTERED`, `caseCreated=false` |
| `GET /api/v1/cm/complaints/{id}` | 200 |
| Replay same Idempotency-Key | 200 `replayed=true` |

Note: first create attempt on `CUST-10001` correctly returned **400 Duplicate Warning** (prior S3 TestClient smoke row) — FR-003 behaviour; smoke continued on `CUST-10002`.

## Condition status (local Docker)

| # | Condition | Status |
|---|---|---|
| 1 | Migrate + smoke | **CLEARED** (DB + container HTTP) |
| 2 | Master Customer stance | Open |
| 3 | Residual exceptions Board acceptance | Open |
| 4 | Redeploy matching Batch 1 build | **CLEARED** for local Compose |

Overall Batch 1 release classification remains **READY WITH CONDITIONS** until OPS-02/OPS-03 close.

---

*End of GOV-S3-CM-B1-OPS01-001.*
