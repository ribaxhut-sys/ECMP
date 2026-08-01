# ECMP CM Batch 1 — S3 Operational Migrate Gate

| Field | Value |
|---|---|
| Document ID | GOV-S3-CM-B1-MIG-001 |
| Date | 2026-07-29 |
| Status | 🟢 Complete (local Docker `ecmp`) |
| Scope | Apply Alembic `0040→0043` to local Compose Postgres + post-migrate API smoke |
| Prior classification | READY WITH CONDITIONS (S3 Release Readiness session) |

## Objective

Clear **Condition 1** of the S3 Release Recommendation for the **local Docker** environment: apply Batch 1 schema to the live `ecmp` database and smoke ` /api/v1/cm/*` against the upgraded schema.

## Preconditions

| Check | Result |
|---|---|
| Target DB | Docker `ecmp-postgres` host port **5433**, database `ecmp` |
| Pre-revision | `0039_admin_rbac_repair` |
| `cm_batch1_*` tables before | none |
| Running `ecmp-backend` OpenAPI | **no** `/api/v1/cm/*` paths (image lag) |
| Safety | `pg_dump` before upgrade |

## Execution

1. `pg_dump` → `backend/_s3_migrate_artifacts/ecmp_pre_0043_20260729T073747Z.sql` (~1.9 MB)
2. `alembic upgrade head` with `DATABASE_URL=postgresql+psycopg://ecmp:ecmp@localhost:5433/ecmp`
3. ORM metadata vs DB columns for all `cm_batch1_*` tables
4. Smoke via **local code + TestClient** (not the lagging container): search → confirm → create (Idempotency-Key) → get → replay

## Results

| Check | Result |
|---|---|
| Post-revision | `0043_cm_batch1_foundation` (head) |
| Tables created | 11 `cm_batch1_*` |
| ORM mismatches | **0** |
| Smoke search | 200 (`CUST-10001`) |
| Smoke confirm | 200 (`locked=true`) |
| Smoke create | 201 (`CM-00000001`, `caseCreated=false`, `REGISTERED`) |
| Smoke get | 200 |
| Smoke replay | 200 (`replayed=true`, same `complaintId`) |
| Regression suite | **74 passed** (`test_cm_batch1*.py`) |

### Tables present after upgrade

- `cm_batch1_complaints`
- `cm_batch1_idempotency`
- `cm_batch1_channel_messages`
- `cm_batch1_customer_locks`
- `cm_batch1_number_counters`
- `cm_batch1_duplicate_decisions`
- `cm_batch1_attachments`
- `cm_batch1_attachment_staging`
- `cm_batch1_attachment_history`
- `cm_batch1_later_review_items`
- `cm_batch1_outbox`

## Non-goals (unchanged)

- No new APIs / FRD / OpenAPI / Event Catalog changes
- No Event Publisher / Notification Worker
- No Enterprise Master Customer HTTP
- No rebuild/redeploy of `ecmp-backend` image (explicitly deferred this task)
- No application of migrations to non-local environments

## Remaining conditions (still open)

| # | Condition | Status after this gate |
|---|---|---|
| 1 | Apply `0040→0043` + smoke on **target** env | **CLEARED for local Docker `ecmp`** |
| 2 | Agreed Master Customer stance for release env | Open |
| 3 | Accept residuals as release exceptions (stub AV, confirm-lock gap, in-process enum, persist-only outbox) | Open — needs Architecture Board |
| 4 | Redeploy backend build that includes Batch 1 + `/live`/`/ready` | Open — **required** before claiming container HTTP readiness |

## Operational risk introduced

The running `ecmp-backend` container image **does not** contain revisions `0040–0043`. If that container restarts, its entrypoint (`alembic upgrade head`) may fail with *Can't locate revision identified by '0043'* until the image is rebuilt from current `backend/` sources.

**Recommended next operational step (requires approval):** rebuild/restart `ecmp-backend` from local tree so Compose HTTP surface matches the DB head.

## Classification update (local Docker only)

| Scope | Prior | After this gate |
|---|---|---|
| Local Docker DB schema | Behind head (`0039`) | **At head (`0043`)** |
| Local CM API via TestClient + live DB | Untested on live DB | **PASS** |
| Overall Batch 1 production release | READY WITH CONDITIONS | **READY WITH CONDITIONS** (condition 1 local cleared; 2–4 remain) |

---

*End of GOV-S3-CM-B1-MIG-001.*
