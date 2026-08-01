# ECMP Sprint-08 — Production Readiness: Implementation Plan

> **Historical (P6-003):** This plan targeted the **legacy** pack under `implementation/backend/`.
> Canonical production/ops stack is root **`backend/`** + `docs/deployment/` +
> `15 Operations Runbook/` Backup & Recovery guides (OPS-BAK-001 / OPS-RST-001 / OPS-DR-001 /
> OPS-RCV-001). Gap rows below that say restore drill **MISSING** are **obsolete** — a DEV scratch
> drill PASS exists (`15 Operations Runbook/evidence/restore-drill-20260722/`). Shared-env drill
> remains Planned. Application probes are foundation **`/live`** / **`/ready`**, not `/health`.
> Do not implement schedulers/WAL/PITR from this historical plan without a new authorized task.

Engineering plan only — no code. Grounded in reading actual source (`app/settings.py`, `app/main.py`,
`app/db.py`, `app/auth.py`, CI workflows) and the repo's own governance documents (ADR-010, TS-001,
DEP-001, SEC-STD-001, OPS-DR-001), not on assumptions about what a "production readiness" sprint
usually contains.

## 0. Governance conflict — read this before the rest of the plan

Two of the CTO's P1 items collide head-on with decisions this repository has already made and
approved. Flagging per the verification protocol ("stop if you need a business decision") rather than
silently building around it or silently skipping it.

**ADR-010 (Deployment Platform Baseline, Approved 2026-07-21)** and **TS-001 §7** explicitly state:
Dockerfile, container registry, tagging standard, and any production compose file are **prohibited
from being built speculatively** ("dilarang membangun Dockerfile 'sekalian'") until the SIT/UAT
baseline is activated — and that baseline **cannot** activate until ADR-007's target auth phase
(JWT/OIDC) is live. Verified in `app/auth.py`: authentication is still the ADR-007 **slice phase**
(static env-var bearer tokens, fixed dev principals) — the target phase has not shipped. So "Docker
review, production compose" (item 5) is currently gated shut by the project's own approved
architecture decision, not an oversight to fix in this sprint.

**OPS-DR-001 (DR/BCP Plan, status Draft)** documents the backup strategy (`pg_dump` daily + WAL
archiving) as explicitly **Planned**, with an explicit note: "DEV lokal tidak di-backup" and the whole
plan is gated to graduate out of Draft only when the SIT/UAT baseline activates — the same trigger as
above. "Database backup strategy, restore verification" (item 6) has the same blocker: there's no
shared environment yet to back up or restore.

**What this sprint can legitimately do without violating ADR-010:**
- Review and document the *existing* DEV docker-compose (Postgres-only) — that artifact already
  exists and is in scope for review.
- Produce a **readiness checklist**: exactly what unblocks SIT/UAT activation (ADR-007 target auth)
  and what gets built the moment it does (Dockerfile, registry, prod compose, `pg_dump`/WAL
  automation, restore drill). This is planning, not building — consistent with "do not write code."
- Expand environment documentation for what's real today (DEV + CI), matching DEP-001's own honesty
  principle.

**What this sprint should NOT do:** author a Dockerfile, a production `docker-compose.prod.yml`, or
an actual backup automation script. Doing so would be exactly the "build spekulatif" ADR-010
prohibits, and would need to be thrown away or reworked once real auth/platform decisions land.
**Recommend the CTO either (a) explicitly waive ADR-010 §4/TS-001 §7 for this sprint via the
Exception Request process (`18 Architecture Governance/reviews/EXCEPTION_REQUEST.md`), or (b)
accept items 5 and 6 as documentation/checklist-only this sprint**, deferring the actual build to
whenever ADR-007 target auth activation is scheduled. The plan below treats them as (b) unless told
otherwise.

---

## 1. Repository Audit (relevant to production readiness)

- **Runtime**: FastAPI app, single process, `uvicorn app.main:app`. No process manager config,
  no `workers` setting, no gunicorn wrapper anywhere in the repo — confirmed via grep, nothing found.
- **Config**: `app/settings.py` reads everything from env vars, has no hardcoded secrets (confirmed),
  and already has `validate_runtime_config()` which fails fast outside `ECMP_ENV=dev` if default
  tokens or `ECMP_ENABLE_DEV_ENDPOINTS` are left on — called from `main.py`'s `lifespan()`. This is a
  real, working production-safety gate already in place.
- **CORS**: no `CORSMiddleware` anywhere in `app/main.py` (confirmed via grep). The only reason the
  app works cross-origin today is the **Vite dev-server proxy** (`vite.config.ts`, `/v1 → :8000`),
  which only exists in `npm run dev` — it does not exist in the built production bundle
  (`vite build` output is static files with no proxy). This is a real gap for any future deployment
  where frontend and backend aren't served from the same origin.
- **Security headers**: none set anywhere (no middleware, no `X-Frame-Options`,
  `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`). Confirmed by
  grep across `app/`.
- **Logging**: no `logging` module usage anywhere in `app/` (grep confirmed zero matches outside
  Alembic's own `fileConfig` boilerplate). TS-001 §6 labels structured logging + correlation-id as
  "backlog gate G1" — checking `18 Architecture Governance/README.md`'s gate table: **G1 sits before
  assign/status code, which shipped in Sprint-02B**. G1 has already passed. So, unlike the
  Docker/backup items above, building structured logging now is **not** premature — it's overdue
  backlog, not speculative gold-plating.
- **Health endpoint**: one `/health` route, returns a static status/service/sprint payload, no DB
  connectivity check, no distinction between liveness and readiness.
- **Dependency audit**: `backend-ci.yml` already runs `pip-audit` on `requirements.txt` as a separate
  CI job. `frontend-ci.yml` has no equivalent `npm audit` step — confirmed by reading the workflow
  file in full.
- **Frontend bundle**: no bundle analyzer, no `manualChunks`, no `rollup-plugin-visualizer` anywhere
  in `vite.config.ts` — confirmed. Route-level code splitting is also absent: `router.tsx` imports
  `CaseQueuePage` and `CaseDetailPage` eagerly; only the three sub-panels *inside* Case Detail
  (`CaseActivityTimeline`, `AuditHistoryPanel`, `NotesPanel`) are `lazy()`-loaded, a Sprint-06 decision
  that's still sound but doesn't cover the top-level route split.
- **Backend queries**: reviewed `list_cases`, `get_case_timeline`, `list_case_notes`,
  `list_outbox_events` in `service.py` — each issues one `session.query(...)` per call, no loops
  issuing per-row queries found. This is a targeted review of the request-path queries, not an
  exhaustive audit of every code path.

## 2. Architecture Review

The backend's layering (ADR-005: `main.py → service.py → models.py/db.py`) and config-via-env
approach (`settings.py`) are already production-appropriate patterns — this sprint extends what's
there rather than restructuring it. `db.py`'s `get_engine()`/`get_session()` is a plain
create-once-reuse pattern with no connection pool tuning (`pool_size`, `max_overflow`, `pool_timeout`
are all SQLAlchemy defaults) — reasonable for now, worth a one-line settings hook rather than a
redesign, since real pool tuning needs load data this project doesn't have yet (same "no speculative
tuning" principle ADR-009/ADR-010 already establish for this codebase).

No architectural changes are proposed. Every item below is additive (new middleware, new module,
new checklist doc) or configuration (env var, CI step) — nothing here touches `service.py`'s business
logic or the API contract.

## 3. Gap Analysis — IMPLEMENTED vs MISSING

| Area | Item | Status |
|---|---|---|
| Config | Env var-based configuration | **IMPLEMENTED** — `settings.py` |
| Config | Fail-fast validation outside dev | **IMPLEMENTED** — `validate_runtime_config()`, called in `lifespan()` |
| Config | Secrets never in source | **IMPLEMENTED** — `.env` gitignored, `.env.example` has no real secrets |
| Config | Production-safe defaults (dev endpoints off, docs off) | **IMPLEMENTED** — `_dev` flag gates `/_dev/*` and `/_dev/docs` |
| Config | Documented secrets path for shared/prod env (vault) | **MISSING** — SEC-STD-001 §7 marks this "TBD bersama keputusan platform"; still TBD |
| Observability | Structured (JSON) logging | **MISSING** |
| Observability | Request id / correlation id propagation | **MISSING** |
| Observability | Error reporting beyond the existing error envelope | **MISSING** — errors are returned to caller correctly (`errors.py`) but not logged/captured server-side |
| Observability | Health endpoint | **PARTIALLY IMPLEMENTED** — `/health` exists but is liveness-only, no DB check, no `/ready` |
| Security | CORS policy | **MISSING** — works today only via dev-only Vite proxy |
| Security | Security headers | **MISSING** |
| Security | Backend dependency audit in CI | **IMPLEMENTED** — `pip-audit` job in `backend-ci.yml` |
| Security | Frontend dependency audit in CI | **MISSING** — no `npm audit` step in `frontend-ci.yml` |
| Security | Secret-leakage review (git history, logs, error responses) | **MISSING** — not yet performed |
| Performance | Route-level frontend code splitting | **MISSING** — only sub-panel splitting exists |
| Performance | Bundle size visibility/analysis tooling | **MISSING** |
| Performance | Backend startup review | **PARTIALLY IMPLEMENTED** — fast today (SQLite/Postgres create-on-demand, no heavy init) but never measured/documented |
| Performance | Query review of hot paths | **IMPLEMENTED** (reviewed, no issues found — see §1) |
| Deployment | Dev docker-compose (Postgres) | **IMPLEMENTED** |
| Deployment | Application Dockerfile / prod compose | **MISSING — and currently prohibited by ADR-010 until SIT/UAT trigger** (see §0) |
| Deployment | Environment documentation (DEV/CI) | **IMPLEMENTED** — DEP-001; could be extended (see §4) |
| Backup/Recovery | Documented backup strategy | **IMPLEMENTED as a plan** — OPS-DR-001 §2 (status: Planned/Draft, correctly so) |
| Backup/Recovery | Actual backup automation | **MISSING — blocked, no shared env exists to back up** (see §0) |
| Backup/Recovery | Restore verification / drill | **MISSING — blocked, same reason** |

## 4. Production Readiness Checklist

**P0 — actionable this sprint:**
1. Add `CORSMiddleware` to `app/main.py`, origins driven by a new `ECMP_ALLOWED_ORIGINS` env var
   (comma-separated, empty/unset = same-origin only — safe default). Documented in `.env.example`.
2. Add a security-headers middleware (or `fastapi`-compatible equivalent) setting
   `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and a
   conservative `Content-Security-Policy` for the API responses (JSON API, so CSP is minimal — mainly
   defense-in-depth, not asset-serving).
3. Add structured logging: one `logging.config.dictConfig` setup in a new `app/logging_config.py`,
   JSON formatter, invoked at app startup. Must comply with the *already-binding* rule in TS-001 §6:
   no PII (`description`, `subject`, customer payload) in log lines — only IDs and technical metadata.
4. Add request-id/correlation-id middleware: generate a UUID per request if `X-Request-Id` isn't
   supplied by the caller, attach to the structured log context, echo back in the response header.
5. Extend `/health` into two endpoints per common practice: keep `/health` as liveness (no
   dependencies), add `/health/ready` that checks DB connectivity (`SELECT 1`) — matches OPS-DR-001
   §3 step 6's existing expectation of "verifikasi `GET /health`" during restore, now with a real
   dependency check available for that same use.
6. Add `npm audit --audit-level=high` (or equivalent) as a step in `frontend-ci.yml`, mirroring the
   backend's `pip-audit` job.
7. Manual secret-leakage review: grep git history and current tree for accidentally committed
   credentials, confirm `.env` was never committed (check `.gitignore` coverage + `git log --all
   --full-history -- '**/.env'`), confirm no token/PII ends up in the new structured logs from item 3.
8. Frontend: convert `CaseQueuePage`/`CaseDetailPage` route elements in `router.tsx` to `lazy()` +
   `Suspense`, consistent with the pattern already used for sub-panels.
9. Add a bundle-analysis step: `rollup-plugin-visualizer` (dev-dependency only, zero runtime cost) or
   `vite build --mode analyze`, wired as an optional local script (`npm run analyze`), not a CI gate —
   this is a visibility tool, not a pass/fail check, since no size budget has been set yet (setting one
   without real user data would be the same "spekulatif" pattern ADR-009/010 already reject).
10. Document backend startup: run `uvicorn` locally, record cold-start time and first-request
    latency once, write it into `14 Deployment Standards` as a baseline reference — not a new
    engineered optimization, since nothing measured so far indicates a problem.

**P1 — checklist/documentation only, pending CTO decision from §0:**
11. Extend `DEP-001` with a "What activates SIT/UAT" appendix: restates ADR-010's trigger (ADR-007
    target auth live) and lists, in order, the artifacts that get built at that point (Dockerfile,
    registry/tagging standard, prod compose, `ECMP_ALLOWED_ORIGINS` real values, vault/secret
    manager wiring, `pg_dump`/WAL automation, first restore drill). This turns "production
    deployment" from an open question into a tracked, ordered checklist for whenever the trigger
    fires — useful now even though nothing on it gets built now.
12. Same treatment for OPS-DR-001: add a "pre-activation checklist" so the restore-drill step (§7,
    already required "minimal 1x sebelum UAT") has a concrete task list ready to execute, without
    building the automation prematurely.

## 5. File Impact

| File | Change |
|---|---|
| `implementation/backend/app/main.py` | Add `CORSMiddleware`, security-headers middleware, request-id middleware, `/health/ready` route |
| `implementation/backend/app/settings.py` | Add `allowed_origins()` reading `ECMP_ALLOWED_ORIGINS` |
| New: `implementation/backend/app/logging_config.py` | Structured logging setup |
| `implementation/backend/app/db.py` | Add a `ping()`/connectivity-check helper used by `/health/ready` |
| `implementation/backend/.env.example` | Document `ECMP_ALLOWED_ORIGINS` |
| `.github/workflows/frontend-ci.yml` | Add `npm audit` step |
| `implementation/frontend/src/routes/router.tsx` | Route-level `lazy()` + `Suspense` for both pages |
| `implementation/frontend/vite.config.ts` | Add optional `analyze` build script/plugin (dev-dependency only) |
| `implementation/frontend/package.json` | Add `analyze` script, `rollup-plugin-visualizer` devDependency |
| `14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md` | Add SIT/UAT activation appendix (§4 item 11); add measured startup baseline (item 10) |
| `15 Operations Runbook/ECMP_DR_BCP_Plan_v0.1.md` | Add pre-activation restore-drill checklist (§4 item 12) |

No OpenAPI/contract changes. No ADR changes (an Exception Request is optional, per §0, only if the
CTO wants items 5/6 built now instead of documented).

## 6. Risks

| Risk | Notes |
|---|---|
| Building Docker/backup automation now would violate ADR-010/TS-001 §7 | See §0 — this is the primary risk of this sprint if scope isn't explicitly narrowed by the CTO |
| Structured logging could leak PII if not reviewed carefully | `description`/`subject` fields are exactly what TS-001 §6 already prohibits from logs; new logging code must be reviewed against that rule before merge, not after |
| CORS default must fail closed | `ECMP_ALLOWED_ORIGINS` unset must mean same-origin-only, not wildcard — a permissive default here would be a real vulnerability, not just a config gap |
| Bundle analysis / route splitting could be over-engineered without size data | Scoped deliberately as visibility tooling only, no enforced budget, matching the project's stated anti-gold-plating pattern |
| `npm audit` in CI could surface pre-existing transitive vulnerabilities with no immediate fix | Recommend `--audit-level=high` (not `critical` or unfiltered) as a starting gate, informational for lower severities, to avoid an unrelated blocked merge queue on day one |
| Health/readiness split changes existing `/health` contract consumers may depend on | `/health` response shape is kept unchanged; `/health/ready` is additive, not a breaking change |

## 7. Acceptance Criteria

1. `app/main.py` sends `Access-Control-Allow-Origin` only for origins in `ECMP_ALLOWED_ORIGINS`; unset env var means no CORS headers at all (same-origin only).
2. All responses include `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, and a CSP header.
3. Every log line is JSON, includes a request id, and a manual review confirms zero PII fields appear across a full manual smoke-test session (create/get/assign/status/list/timeline/notes).
4. `/health` response is byte-identical to today's; `/health/ready` returns 200 with a DB check when DB is reachable, 503 when it isn't (verified by stopping Postgres and calling it).
5. `frontend-ci.yml` runs `npm audit` and fails the build on high/critical findings.
6. `router.tsx`'s two page routes are lazy-loaded; manual check confirms the initial JS payload (network tab, production build) is smaller than before the change.
7. `npm run analyze` produces a bundle visualization locally; not wired into CI as a gate.
8. `DEP-001` and `OPS-DR-001` each have a new section listing what happens at SIT/UAT activation, in dependency order, with ADR-007 target auth explicitly named as the trigger.
9. No Dockerfile, production compose file, or backup automation script exists in the repo as a result of this sprint, unless the CTO explicitly authorizes an ADR-010 exception before work starts.
10. Manual secret-leakage review completed and documented (git history check, `.env` gitignore confirmation, review of new log output) — findings recorded even if the result is "nothing found."

## 8. Technical Debt

- **Connection pool tuning left at SQLAlchemy defaults** (§2) — deliberately deferred until real load
  data exists; noted so it isn't forgotten once traffic patterns are known.
- **CSP is minimal/defense-in-depth only** — this is a JSON API with no server-rendered HTML, so a
  strict content policy has limited value today; revisit if the frontend is ever served from the same
  origin as the API in a way that changes that assumption.
- **`/health/ready`'s DB check is a single `SELECT 1`** — doesn't check outbox drain lag, disk space,
  or downstream dependencies (there are none yet). Sufficient for current architecture; would need
  revisiting if async workers or external integrations are added.
- **Frontend bundle budget is not enforced** — visibility only, by design (§4 item 9). A real budget
  needs either a size target from the team or comparison data from a first production deployment,
  neither of which exists yet.
- **The entire P1 Docker/backup item set is technical debt by governance design, not oversight** —
  ADR-010 explicitly defers it to a named trigger. This isn't a gap to feel behind on; it's a decision
  already made and documented. Re-surface it automatically once ADR-007 target auth activation is
  scheduled, per the checklist in §4 items 11-12.

---

## Related
- `05 Architecture Decision Records/ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md` (the governing constraint for §0)
- `21 Technical Standards/ECMP_Technical_Standards_v0.1.md` §6 (logging, now unblocked), §7 (Docker, still blocked)
- `14 Deployment Standards/ECMP_Deployment_Standards_v0.1.md`, `15 Operations Runbook/ECMP_DR_BCP_Plan_v0.1.md`
- `10 Security and Access Standards/ECMP_Security_Standards_v0.1.md`
- `18 Architecture Governance/reviews/EXCEPTION_REQUEST.md` (path to unblock §0 if CTO chooses to)
- `implementation/frontend/IMPLEMENTATION_PLAN_SPRINT07_STABILIZATION.md` (prior sprint, now closed)
