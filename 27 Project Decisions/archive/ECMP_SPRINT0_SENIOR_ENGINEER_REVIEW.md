# ECMP Sprint 0 — Senior Engineer Validation & Implementation Plan

> **Historical/archived** (2026-07-21): dipindahkan dari root repo ke `27 Project Decisions/archive/`. Konten dipertahankan apa adanya sebagai artefak historis; sudah digantikan oleh decision records (DEC-001 dst.) dan baseline resmi.

| Field | Value |
|---|---|
| Reviewer role | Senior Enterprise Software Engineer |
| Basis | `ECMP_SPRINT0_DISCOVERY_REPORT.md` cross-checked against live repository at `D:\ECMP` |
| Scope | Validate the discovery report, classify proposed Sprint 0 work, flag over-engineering, output one ordered, minimal, testable Sprint 0 plan |
| Constraint | No redesign, no speculative features, no code written in this pass |

---

## 1. Validation of the Discovery Report

I read `implementation/backend/app/main.py`, `requirements.txt`, `tests/test_cases.py`, both `.github/workflows/*.yml`, ADR-004, `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md`, `ai/sprint/Sprint-01.md`, `10 Security and Access Standards/README.md`, `09 Integration Catalog/README.md`, both event catalog files, and the Blueprint/FRD markdown mirrors. The discovery report is **accurate**. Findings below are per your focus list, each marked against what I independently confirmed in the code, not just repeated from the report.

**Architecture boundaries / dependency direction.** Confirmed. `main.py` is one file: Pydantic schemas, route handlers, an auth function, a permission check, an in-memory dict, and event emission all live together. There is no `domain/`, `application/`, or `infrastructure/` package, and no dependency-inversion boundary exists to violate yet — there's simply one layer. The "Presentation → Application → Domain ← Infrastructure" principle stated in project docs is aspirational, not enforced, and not yet ADR'd as mandatory for the backend. Confirmed as report states.

**Authentication design.** Confirmed. `require_user()` accepts any `Authorization: Bearer <token>` header, hardcodes acceptance of the literal string `dev-token`, and returns a fixed principal (`cs.agent.1`) with a fixed permission set. There is no token issuance, no expiry, no user store. This is a placeholder, correctly labeled as such by the report — not a security defect at this stage, but not usable past a single-developer demo.

**RBAC.** Confirmed absent as a real model. `require_perm()` checks membership in a hardcoded Python `set`. There is no Role or Permission entity, no persistence, and `10 Security and Access Standards/README.md` is a template checklist with every box unchecked — no Role Matrix exists anywhere in the repo.

**Database and migration foundation.** Confirmed missing entirely. `requirements.txt` contains only `fastapi`, `uvicorn`, `pydantic`, `httpx`, `pytest` — no SQLAlchemy, no Alembic, no `psycopg`/`asyncpg`. There is no `alembic.ini`, no `docker-compose.yml` anywhere in the repo, no migration revisions. `CASES: dict[str, dict] = {}` is the entire persistence layer and is lost on process restart. This directly contradicts ADR-004 (Accepted, PostgreSQL + Alembic), which I read in full — the decision is locked, the implementation of that decision has not started.

**Transaction boundaries.** Confirmed: none exist, because there is no database. `create_case()` mutates two Python globals (`CASES`, `EVENTS`) with no atomicity guarantee. This matters specifically because Sprint 0 must land Case + AuditLog + Outbox as one transaction on day one of real persistence — retrofitting that after the fact is exactly the kind of rework the readiness roadmap already warns about.

**Auditability.** Confirmed missing. The `EVENTS` list is an in-process integration-event stub, not an audit trail — it has no actor/action/before-after shape and disappears on restart. No append-only audit store exists in code or schema. Business Rules docs (BR-CP-03 et al.) call for write-path audit; nothing implements it.

**Error handling.** Confirmed inconsistent. `07 API Catalog/openapi/case-service.v1.yaml` declares an `Error{code,message}` schema, but the running app raises `HTTPException(status_code=..., detail="...")`, which FastAPI serializes as `{"detail": "..."}`. A client coded against the OpenAPI contract will get a shape mismatch on every 400/401/403/404.

**Configuration/secrets.** Not mentioned as a distinct P0 in the discovery report, but I checked directly: there is no `.env.example`, no settings module, no secrets handling of any kind. `dev-token` is a literal string in source. This needs to be named explicitly as its own Sprint 0 concern (see Task 2 below) — it's small, but it's a real gap the discovery report only touches indirectly through the auth section.

**Logging.** Confirmed missing. No structured logging library, no request/correlation ID, no log statements at all in `main.py`. Readiness roadmap independently flags this (item 20 in its G0 deliverables), which corroborates the discovery report.

**Testing strategy.** Confirmed: 4 tests in `tests/test_cases.py` covering health, happy-path create/get, 401, 404. No 403-with-wrong-permission-but-valid-token case, no validation-enum negative tests, no contract test against the OpenAPI spec, no DB/migration tests (nothing to test yet). `13 Test Strategy/README.md` is an empty placeholder.

**CI foundation.** Confirmed. Two workflows exist: `ear-docs.yml` (runs `tools/eos.py --all` and an MkDocs strict build) and `ai-review.yml` (advisory AI review pack generation). Neither installs backend dependencies, runs `pytest`, or builds/runs anything in `implementation/backend`. Backend tests currently only run if a developer runs them locally. This is accurately reported.

**One item I verified independently rather than take on faith:** the report's most serious claim — that the discovery brief's "branch → Head Office escalation → schedule slot → work order" business baseline is *not* in the accepted EKR sources. I grepped `docs/business/blueprint.md`, the FRD, and Business Rules v1.0 for `branch`, `head office`, `schedule slot`, `work order`, `escalat*`. Zero hits for the business-model sense of "branch" or for Head Office, scheduling, or work orders; the one "BRANCH" hit in the FRD is a channel enum value (`CALL, EMAIL, BRANCH`), not an actor or process. This confirms the report's finding: that baseline is not present in the accepted Blueprint/FRD. I did not open the binary `.docx` Blueprint directly (only its generated markdown mirror), so treat this as strong corroboration, not 100% exhaustive proof — but it is consistent with everything else in the repo.

**Conclusion on validation: the discovery report is trustworthy.** I did not find any claim in it that the repository contradicts. Where I have adjustments, they are about *how the Sprint 0 work should be sequenced and scoped*, not about the facts.

---

## 2. Task Classification

Classifying every task the discovery report proposed (S0-0 through S0-5), plus the G0 deliverable list already drafted in `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md` (which I'm treating as part of "the proposal," since it's an existing artifact in-repo covering the same gate). Where the roadmap and the discovery report propose the same thing, I classify it once.

| # | Proposed task | Source | Classification | Reasoning |
|---|---|---|---|---|
| 1 | Resolve business-baseline conflict (branch/HO/scheduling vs Blueprint/FRD) | S0-0 | **MUST** | Blocking by definition — coding against the wrong business model produces throwaway work. Confirmed real conflict, not report noise. |
| 2 | Locate or formally supersede the missing "KAK" document | S0-0 | **SHOULD** | Real gap (provenance of the disputed baseline is untraceable), but it's a documentation/decision action, not an engineering blocker to *readiness engineering*. Can run in parallel with Task 2 below. |
| 3 | Decide whether Clean Architecture layering is mandatory (new ADR) | S0-0 | **MUST** | Cheap decision, high leverage — must be settled before any package structure is created, or Sprint 0 itself will produce ad-hoc layering that has to be redone. |
| 4 | Resolve Sprint-01 "GO" vs G0-gate contradiction | S0-0 | **MUST** | Two documents currently give conflicting build authorization. This is a governance fix (edit a status field / add a decision record), not engineering — do it first, it's nearly free. |
| 5 | Declare single BR ID scheme for delivery (`BR-001…` vs `BR-<Domain>-NN`) | S0-1 | **SHOULD** | Real inconsistency, but does not block engineering — code can reference the Sprint BR IDs today without waiting. Do it, but it's not gating. |
| 6 | Declare Event SoT, reconcile/retire duplicate event catalog | S0-1 | **MUST** | Confirmed real divergence between `events/events.yaml` and `ECMP_Event_Catalog_v1.0.yaml`. A developer implementing EVT-001 today has two different, disagreeing sources. Cheap to fix, high risk if left. |
| 7 | Patch FRD audit/idempotency decisions (write-audit required, read-audit deferred, idempotency out of scope) | S0-1 / G0 #3-4 | **MUST** | Directly determines what Sprint 0's schema and Build-1 code must implement. Without this written down, "audit" is undefined scope. |
| 8 | Document `caseId` strategy, UTC rule, Bearer claims shape | S0-1 / G0 #5-7 | **MUST** | Small, concrete, removes ambiguity that would otherwise be invented ad hoc during coding. |
| 9 | OpenAPI Error `{code,message}` + validation mapping | S0-2 / G0 #11 | **MUST** | Contract already exists but code doesn't honor it — this is a correctness bug against an Accepted contract, not new scope. |
| 10 | Minimal Role matrix (`cases:create`/`cases:read` only) | S0-2 / G0 #14 | **MUST** | Needed to replace the hardcoded permission set with something traceable. Keep it to the two permissions that exist in code today — nothing more. |
| 11 | CM (Customer Master) Integration Stub Contract in `09` | S0-2 / G0 #13 | **SHOULD** | Useful to document current stub behavior (`customerVerified=false` always), but the code already behaves consistently without it; this formalizes rather than unblocks. Can land same sprint, non-blocking for Task list below. |
| 12 | Align Data Dictionary Case section to FRD/OpenAPI naming | S0-2 | **SHOULD** | Real drift, developer confusion risk, but doesn't block schema/migration work if the migration is built from FRD/OpenAPI directly (which it should be regardless). |
| 13 | Add SQLAlchemy/Alembic + DB driver deps | S0-3 / G0 #18 | **MUST** | Nothing else in Sprint 0 is possible without this. |
| 14 | Alembic revision 0: `cases`, `audit_log`, `outbox` | S0-3 / G0 #15 | **MUST** | The core deliverable of the entire gate — this is "the smallest correct foundation." |
| 15 | `docker-compose.yml` for PostgreSQL | S0-3 / G0 #17 | **MUST** | Required for both local dev and CI to exercise the migration; no way to prove Task 14 works without it. |
| 16 | Request-id / correlation-id middleware stub | S0-3 / G0 #20 | **SHOULD** | Genuinely useful and cheap, but the system has zero structured logging today, so a correlation ID with nothing to correlate is lower leverage than the DB/CI work. Do it, but after persistence lands. |
| 17 | Error handler aligned to OpenAPI | S0-3 | **MUST** | Same item as #9, listed under implementation rather than contract — one task, not two. |
| 18 | Optional skeleton packages `domain/`, `application/`, `infrastructure/`, `api/` "only if ADR mandates it" | S0-3 | **CONDITIONAL — becomes MUST or REMOVE based on Task 3** | Correctly gated by the report itself. Do not scaffold packages speculatively; either the ADR says yes (then do the minimal split needed for Case+Audit+Outbox only) or the ADR says defer (then leave `main.py` as is for this gate). |
| 19 | GitHub Actions: install backend deps → migrate → pytest, green | S0-4 / G0 #19 | **MUST** | Without this, every other Sprint 0 deliverable can regress silently the moment someone merges. |
| 20 | Explicit non-goals list (no assign/status/notification/schedule/appointment/work order in Sprint 0) | S0-5 | **MUST** | Costs nothing to write, prevents scope creep during the gate — directly serves your instruction not to add speculative features. |
| 21 | Workflow-config ownership decision (Administration vs Core) | G0 #8 | **LATER** | Real governance question, but it has zero effect on Create/Get, the only slice in scope. Nothing in Sprint 0 needs this answered. Defer to G1 (assign/status gate), as the roadmap itself already schedules it there. |
| 22 | Retention policy interim decision | G0 #9 | **SHOULD** | One sentence in a decision record ("retain indefinitely until Compliance sprint"). Cheap, removes an open question, but not gating for schema-0 (a retention *policy* doesn't change the *schema*). |
| 23 | OQ-001/OQ-003 (channel scope, CQRS deferred) written up | G0 #10 | **LATER** | CQRS is not remotely relevant to a two-endpoint slice. Channel-out-of-scope is already true by omission (no channel logic in code). Writing this down is housekeeping, not a blocker — defer without risk. |
| 24 | SA/ADR index editorial sync | G0 #21 | **LATER** | Pure documentation hygiene, zero engineering risk if deferred a sprint. |

### Explicit REMOVE

| Recommendation | Why it's REMOVE, not just LATER |
|---|---|
| Idempotency keys for `POST /cases` | The roadmap itself already recommends deferring this, and I agree it should be actively dropped from Sprint 0 scope (not just postponed as an open question) — a single hardcoded dev principal cannot produce duplicate concurrent requests in any way that matters yet. Revisit only when a real multi-client integration exists. |
| Audit-on-read (logging every `GET /cases/{id}`) | Confirmed nowhere implemented, and the roadmap's own CTO-gate section flags this as a storage/latency cost that was "unchallenged" in v1. For a two-endpoint internal slice with one hardcoded user, read-audit produces volume with no investigative value yet. Write-audit (on create) is sufficient for Sprint 0. |
| Message broker selection/integration | Correctly deferred by ADR-004 itself ("broker tech follow-up"). An in-process outbox table with no consumer is the entire Sprint 0 scope here — do not evaluate Kafka/RabbitMQ/etc. now. |
| Any Branch / Head Office / Schedule Slot / Appointment / Work Order modeling, even as "just the schema" | These are not in the accepted Blueprint or FRD (verified above). Building schema, endpoints, or even ADRs for them in Sprint 0 would be inventing product scope ahead of the business decision this report correctly flags as blocking (Task 1). Do not touch until Task 1 is resolved and, if approved, scoped as its own gate. |
| Full Clean Architecture scaffold (all four layers, generic repository interfaces, CQRS-ready structure) as a default | Over-engineered for a two-endpoint service. If Task 3's ADR mandates layering at all, the correct Sprint 0 scope is the *minimum* split needed to keep Case creation logic out of the route handler and behind one repository interface — not a full framework of generic ports/adapters, unit-of-work abstractions, or domain event buses. That belongs later if/when the service actually has multiple aggregates and cross-cutting policies to justify it. |
| SSO / external Identity Provider integration | Out of scope by ADR-004 (Bearer + role claims only, frontend/SSO deferred). Nothing in Sprint 0 needs it; don't let "RBAC" work drift into IdP integration. |
| Generic "audit framework" (pluggable sinks, async audit bus, configurable retention engine) | Sprint 0 needs one `audit_log` table and one synchronous insert inside the create-case transaction. Anything more general is solving a problem that doesn't exist at n=2 endpoints. |

---

## 3. Over-Engineering Flags (summary)

Beyond the REMOVE list above, two structural risks are worth naming explicitly because they're the kind of thing that creeps in mid-sprint even after a plan is agreed:

1. **Package-structure ceremony ahead of the ADR.** The discovery report already guards against this correctly ("only if ADR from S0-0 mandates it"), but it's worth restating as a hard rule: do not create `domain/`, `application/`, `infrastructure/` folders speculatively while Task 3 is still open. A premature four-layer split around a single two-endpoint aggregate produces more indirection than value and will likely be reshaped once Case actually has business-action methods worth isolating.

2. **Outbox-pattern gold-plating.** The roadmap correctly scopes this as "persist Case + Audit + one Outbox row in one transaction; in-process publisher may drain it." That's right. The risk is building this as a general "event publishing framework" (retry backoff, dead-letter handling, multiple event types, publisher abstraction interfaces) when Sprint 0 has exactly one event (`CaseCreated`) and no consumer. Build the table and the one insert; do not build a framework around it.

Everything else proposed in the discovery report and the readiness roadmap is proportionate to a two-endpoint service that is contractually committed (via ADR-004) to PostgreSQL + Alembic + write-audit + outbox-based durability. None of it reads as gold-plating once the REMOVE items above are cut.

---

## 4. Final Ordered Sprint 0 Plan

Ordering principle: governance/decision tasks that are nearly free and unblock everything else go first; then contract fixes; then the platform floor (DB/migration/compose); then error handling and CI, which need the floor to exist to be testable; non-blocking documentation hygiene tasks are folded in wherever they're cheapest, not treated as separate gates. Nothing here builds Branch/HO/Scheduling/Work-Order concepts, an Idempotency mechanism, read-audit, a broker, or a four-layer framework — all excluded per Section 3.

### Task 0 — Resolve business-baseline conflict (decision record)
- **Objective:** Get an explicit, dated decision on whether ECMP proceeds on the Blueprint v2.1 / FRD-001 (CS/ECMF) model or the discovery brief's branch–HO–scheduling model, and record it so engineering has one baseline.
- **Files/modules affected:** `27 Project Decisions/` (new decision record), `01 Business Blueprint/README.md` or `05 Architecture Decision Records/` (pointer only), `ai/sprint/Sprint-01.md` (status field), `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md` (status field).
- **Implementation requirements:** No code. Written decision naming the Decision Authority (per roadmap: SA/Architecture Board), the chosen baseline, and explicit confirmation that Sprint 0 / Build-1 proceed on Case create/get only regardless of outcome.
- **Acceptance criteria:** A single dated, owned document exists stating which baseline is authoritative; `Sprint-01.md` status and the readiness roadmap's gate status no longer contradict each other.
- **Tests required:** None (documentation task). Verification = grep repo for "GO" vs "G0" contradiction resolved; single BR/business-model reference in both files.
- **Dependencies:** None. This is the first task because everything else assumes an unambiguous target.

### Task 1 — Non-goals declaration for Sprint 0
- **Objective:** Explicitly record what will not be built this gate, to prevent scope creep while the DB/CI floor is under construction.
- **Files/modules affected:** `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md` (G0 section) or a new `27 Project Decisions/` entry.
- **Implementation requirements:** List: no assign/status, no Notification, no Schedule Slot/Appointment/Work Order, no Branch/HO escalation flow, no product frontend, no idempotency, no read-audit, no broker selection.
- **Acceptance criteria:** Document merged; referenced from Sprint 0 PR template or checklist if one exists.
- **Tests required:** None.
- **Dependencies:** Task 0.

### Task 2 — Architecture layering decision (ADR)
- **Objective:** Decide, in writing, whether Presentation→Application→Domain←Infrastructure layering is mandatory for the backend now, or deferred until the service has more than one aggregate.
- **Files/modules affected:** New ADR in `05 Architecture Decision Records/` (e.g., `ECMP_ADR_005_Backend_Layering_v1.0.md`).
- **Implementation requirements:** Recommend: defer full layering; require only that Case-creation business logic (validation beyond simple field checks, ID generation, audit-record construction) live in one non-route module/function, callable independently of FastAPI, so it's unit-testable without an HTTP client. This is the minimum that keeps the door open without building a framework.
- **Acceptance criteria:** ADR merged with a clear Accepted/Proposed status and a concrete statement of what Sprint 0 code must and must not contain structurally.
- **Tests required:** None directly; this ADR is what Task 8 below is graded against.
- **Dependencies:** Task 0.

### Task 3 — Event catalog SoT reconciliation
- **Objective:** Eliminate the two disagreeing event catalog files.
- **Files/modules affected:** `08 Event Catalog/events/events.yaml` (kept, normative), `08 Event Catalog/ECMP_Event_Catalog_v1.0.yaml` (retired or marked generated/non-normative with a banner pointing to the normative file).
- **Implementation requirements:** No schema redesign — confirm `EVT-001 CaseCreated` payload in the normative file matches what `main.py` currently emits (`caseId`, `customerId`, `caseType`, `priority`, `subject`, `status`, `createdAt`, `createdBy`); fix whichever side is wrong.
- **Acceptance criteria:** Exactly one file is normative; the other is either deleted or has a banner declaring it non-normative/generated; `EVT-001` payload shape matches code.
- **Tests required:** None (doc/contract task) — this feeds Task 9's outbox payload directly, so a mismatch here becomes an integration bug later if skipped.
- **Dependencies:** None; can run in parallel with Task 0–2.

### Task 4 — OpenAPI error contract + write-audit/idempotency decision patch
- **Objective:** Make the API contract state exactly what Sprint 0 will implement: `Error{code,message}` on all error responses, write-audit required on create, read-audit and idempotency explicitly out of scope for this gate, `caseId` format, UTC timestamp rule, and Bearer claims shape (`userId`, `permissions[]`).
- **Files/modules affected:** `07 API Catalog/openapi/case-service.v1.yaml`, `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md`.
- **Implementation requirements:** Add/confirm `Error` schema on 400/401/403/404/422 responses in the OpenAPI file; patch FRD §9-equivalent section with the audit/idempotency decision from Task 0's authority; state `caseId` as the current `CASE-<10-char-hex>` format already used in code (don't invent a new format) unless there's a reason to change it — if unchanged, just document it.
- **Acceptance criteria:** OpenAPI file validates (lint clean); FRD no longer says "recommended" for idempotency without a resolution; caseId/UTC/claims shape all stated in one place.
- **Tests required:** OpenAPI spec lint (`openapi-spec-validator` or equivalent) passes in CI (folds into Task 11).
- **Dependencies:** Task 0.

### Task 5 — Minimal Role Matrix (`cases:create`, `cases:read` only)
- **Objective:** Replace "empty README placeholder" with a one-page matrix scoped to exactly the two permissions that exist in code.
- **Files/modules affected:** `10 Security and Access Standards/` (new `ECMP_Role_Access_Matrix_v0.1.md` or `.xlsx` per the folder's stated naming convention).
- **Implementation requirements:** One role ("CS Agent") mapped to `cases:create` + `cases:read`; explicitly state no other roles/permissions are in scope this gate.
- **Acceptance criteria:** Matrix merged; matches the permission set literally present in `main.py`'s `require_user()`.
- **Tests required:** None (doc task) — implementation correctness is verified by Task 8's tests.
- **Dependencies:** None.

### Task 6 — CM Integration Stub Contract (light)
- **Objective:** Document the already-existing behavior (`customerId` accepted as opaque string, `customerVerified` always `false`, no real Customer Master call) as an accepted stub contract.
- **Files/modules affected:** `09 Integration Catalog/` (new short entry using the folder's template fields).
- **Implementation requirements:** No code change — this documents current behavior, it does not add a CM client.
- **Acceptance criteria:** Entry merged stating pattern=stub, no external call, `customerVerified=false` fixed for this gate.
- **Tests required:** None.
- **Dependencies:** None.

### Task 7 — Add DB dependencies and local Postgres via docker-compose
- **Objective:** Give the repo the ability to run a real PostgreSQL instance locally and in CI.
- **Files/modules affected:** `implementation/backend/requirements.txt` (add `sqlalchemy`, `alembic`, and one driver — `psycopg[binary]` or `asyncpg`, consistent with whichever SQLAlchemy execution style is chosen), new `docker-compose.yml` (repo root or `implementation/infrastructure/`), `implementation/backend/README.md` (local run instructions), `implementation/backend/.env.example` (new — `DATABASE_URL`, no real secrets).
- **Implementation requirements:** Compose file runs Postgres only (no app container required for Sprint 0); `.env.example` documents the connection string shape; no secret values committed.
- **Acceptance criteria:** `docker compose up -d` produces a reachable Postgres on a documented port; `.env.example` exists and `.env` (if created locally) is gitignored (confirm `.gitignore` already covers this — verify, don't assume).
- **Tests required:** Manual/CI smoke: container starts, `pg_isready` (or equivalent) succeeds.
- **Dependencies:** None structurally, but sequenced after Tasks 0–2 so schema decisions (Task 8) aren't started against a moving target.

### Task 8 — Alembic revision 0: `cases`, `audit_log`, `outbox`
- **Objective:** Land the smallest correct physical schema for the current slice: the Case table matching the existing Pydantic `Case` model, an append-only `audit_log` table, and an `outbox` table for durable `CaseCreated` emission.
- **Files/modules affected:** `implementation/backend/alembic/` (new: `env.py`, `versions/0001_initial.py`), `implementation/backend/alembic.ini`, `implementation/backend/app/db.py` or similar (new — engine/session setup only, no ORM models yet if Task 2's ADR defers full layering; otherwise `app/domain/models.py` per that ADR).
- **Implementation requirements:** Columns for `cases` mirror the existing `Case` Pydantic model exactly (no new fields invented): `case_id` (PK), `customer_id`, `case_type`, `priority`, `subject`, `description`, `status`, `channel` (nullable), `customer_verified`, `created_at`, `created_by`, `updated_at`, all timestamps UTC. `audit_log`: `id` (PK), `entity_type`, `entity_id`, `action`, `actor_id`, `payload` (JSON), `occurred_at`. `outbox`: `id` (PK), `event_id`, `event_name`, `payload` (JSON), `created_at`, `published_at` (nullable). No other tables (no Branch, no Appointment, no Role/Permission persistence yet — Task 5 documents roles but Sprint 0 doesn't need a `roles` table since there's exactly one hardcoded principal).
- **Acceptance criteria:** `alembic upgrade head` applies cleanly on an empty database created from Task 7's compose file; `alembic downgrade base` cleanly reverses it.
- **Tests required:** Migration smoke test (script or CI step) that spins up the compose DB, runs `upgrade head`, asserts the three tables and their columns exist, then runs `downgrade base` and asserts they're gone.
- **Dependencies:** Task 7 (needs a DB to migrate against), Task 4 (schema must match the documented `caseId` format and audit decision).

### Task 9 — Wire persistence, write-audit, and outbox into `POST /cases` / `GET /cases/{id}`
- **Objective:** Replace the in-memory `CASES`/`EVENTS` globals with real Postgres reads/writes; on create, insert Case + AuditLog + Outbox row in a single transaction.
- **Files/modules affected:** `implementation/backend/app/main.py` (route handlers updated to use DB session instead of dict), new thin module holding the create-case logic per Task 2's ADR (e.g., `app/cases.py` if layering is deferred, or `app/domain/case_service.py` if mandated), `implementation/backend/tests/test_cases.py` (updated to use a test DB/session fixture instead of clearing in-memory dicts).
- **Implementation requirements:** One SQL transaction per create: insert `cases` row, insert `audit_log` row (`action=CaseCreated`, `actor_id=<userId>`), insert `outbox` row (`event_name=CaseCreated`, payload matching Task 3's normative schema). `GET /cases/{id}` reads from `cases` table only — no audit write on read (per Task 4's decision). No idempotency key handling (excluded per Section 2). In-process publisher may drain the outbox synchronously after commit for local dev; no broker.
- **Acceptance criteria:** Restarting the process does not lose previously created cases (verifies real persistence, not the in-memory illusion). Killing the process between commit and outbox-drain leaves the outbox row intact (verifies durability of emit-intent). `GET` never writes to `audit_log`.
- **Tests required:** (a) create → restart-equivalent (new DB session) → get returns same case; (b) create → assert one row each in `cases`, `audit_log`, `outbox` with matching `case_id`; (c) existing 401/404 tests still pass against the DB-backed implementation; (d) a forced mid-transaction failure (e.g., invalid data at the DB layer) leaves no partial rows in any of the three tables.
- **Dependencies:** Task 8 (schema must exist), Task 2 (structural placement of the logic), Task 3 (outbox payload shape).

### Task 10 — Align error responses to OpenAPI `{code,message}`
- **Objective:** Make every error response (400/401/403/404/422) match the contract fixed in Task 4, replacing FastAPI's default `{"detail": ...}`.
- **Files/modules affected:** `implementation/backend/app/main.py` (or a new `app/errors.py` exception handler registered on the FastAPI app), `implementation/backend/tests/test_cases.py`.
- **Implementation requirements:** Add a FastAPI exception handler (or per-route error construction) that emits `{"code": "<STABLE_CODE>", "message": "<human message>"}` for `HTTPException` and for Pydantic validation errors (422). Codes should be simple and stable (e.g., `UNAUTHORIZED`, `FORBIDDEN`, `NOT_FOUND`, `VALIDATION_ERROR`) — do not build a general error-code registry/taxonomy beyond what these four endpoints need.
- **Acceptance criteria:** Every non-2xx response from `/cases` and `/cases/{id}` matches the OpenAPI `Error` schema exactly (field names and types).
- **Tests required:** For each of 401 (no token), 403 (wrong token), 404 (missing case), 400/422 (invalid `caseType`/`priority`, missing required field) — assert response body has exactly `code` and `message` keys with correct types.
- **Dependencies:** Task 4 (contract must be fixed first), Task 9 (needs DB-backed handlers to wrap consistently — can technically run in parallel with Task 9 if scoped only to auth/validation errors, but final verification needs both merged).

### Task 11 — Backend CI: install → migrate → pytest, green on every PR
- **Objective:** Make it impossible to merge a backend PR that breaks the migration or the test suite, closing the gap where only docs currently have CI.
- **Files/modules affected:** New `.github/workflows/backend-ci.yml`.
- **Implementation requirements:** Job spins up Postgres as a service container (or reuses Task 7's compose file), installs `implementation/backend/requirements.txt`, runs `alembic upgrade head` against the service DB, runs `pytest implementation/backend/tests`. Keep `ear-docs.yml` and `ai-review.yml` untouched and separate, per the roadmap's own binding rule.
- **Acceptance criteria:** Workflow runs on every PR touching `implementation/backend/**`; fails the PR check if migration or tests fail; passes green on current `main` after Tasks 8–10 land.
- **Tests required:** This task *is* the test-runner — verification is that a deliberately broken PR (bad migration or failing test) shows a red check, and the corrected version shows green.
- **Dependencies:** Tasks 7, 8, 9, 10 (nothing to run in CI until they exist).

### Task 12 — Request/correlation-ID stub
- **Objective:** Add a minimal middleware that attaches a request ID to each request/response and includes it in the (still-minimal) audit and error paths, so it exists before any real logging strategy is designed.
- **Files/modules affected:** `implementation/backend/app/main.py` (add middleware), `implementation/backend/tests/test_cases.py`.
- **Implementation requirements:** Generate a UUID per request if `X-Request-Id` header absent; echo it back on the response; make it available to the audit-log insert in Task 9 (add a nullable `request_id` column to `audit_log` in the same Task 8 migration if this task is sequenced before Task 8 is finalized — otherwise a small follow-up migration). No structured logging framework, no log aggregation — just the ID plumbing.
- **Acceptance criteria:** Every response includes `X-Request-Id`; if the client sends one, it's echoed unchanged; audit rows for `CaseCreated` include the request ID.
- **Tests required:** Assert response header present on a health check and a create call; assert a client-supplied `X-Request-Id` is echoed back unchanged.
- **Dependencies:** Task 9 (needs the audit-log write path to attach to).

### Task 13 — Data Dictionary Case section alignment (non-normative banner)
- **Objective:** Stop the Data Dictionary's sample Case attributes (`category` vs `caseType`, differing status values, mandatory `sla_due_at`) from silently disagreeing with the FRD/OpenAPI/schema that Task 8 just made real.
- **Files/modules affected:** `06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md`.
- **Implementation requirements:** Add a banner on the Case section stating "B1 attributes are normative in FRD/OpenAPI/Alembic revision 0; this section's samples are illustrative/non-normative pending reconciliation," rather than rewriting the whole document.
- **Acceptance criteria:** Banner present; no engineer can reasonably read this doc and implement a field that contradicts Task 8's schema.
- **Tests required:** None.
- **Dependencies:** Task 8 (need the real schema to point to).

### Task 14 — Retention interim decision record
- **Objective:** Close the open question of how long Case/Audit data is retained, so Task 8's schema isn't silently missing a TTL/retention field debate later.
- **Files/modules affected:** `27 Project Decisions/` (new short decision record).
- **Implementation requirements:** One line: "Case and Audit data retained indefinitely until Compliance defines a retention policy; no automatic deletion implemented in Sprint 0."
- **Acceptance criteria:** Decision record merged.
- **Tests required:** None.
- **Dependencies:** None; can land any time, included here for completeness of the gate checklist.

---

### Explicitly deferred out of this plan (tracked, not forgotten)

Workflow-config ownership decision, OQ-001/OQ-003 write-up, and SA/ADR-index editorial sync are real but non-blocking (classified LATER in Section 2) — leave them on the readiness roadmap's own backlog for G1, don't let them consume Sprint 0 calendar. Idempotency, read-audit, broker selection, and any Branch/HO/Scheduling/Work-Order modeling are REMOVE for this gate per Section 2/3 and should not reappear in a Sprint 0 PR without a new decision record reopening them.

---

## 5. Definition of Done for this Sprint 0 pass

- Tasks 0–14 merged.
- `docker compose up` → `alembic upgrade head` → `pytest` green locally and in the new backend CI workflow.
- `GET`/`POST /cases` error bodies match OpenAPI exactly.
- A restart of the backend process does not lose case data (real persistence proven, not asserted).
- Every write to `cases` produces exactly one `audit_log` row and one `outbox` row in the same transaction.
- No code or schema exists for Branch, Head Office escalation, Schedule Slot, Appointment, Work Order, idempotency keys, or a message broker.
- Two people who read `Sprint-01.md` and the readiness roadmap on the same day get the same answer about whether build is authorized.
