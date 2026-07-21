# ECMP Sprint 0 Discovery Report

> **Historical/archived** (2026-07-21): dipindahkan dari root repo ke `27 Project Decisions/archive/`. Konten dipertahankan apa adanya sebagai artefak historis; sudah digantikan oleh decision records (DEC-001 dst.) dan baseline resmi.

| Field | Value |
|---|---|
| Document | `ECMP_SPRINT0_DISCOVERY_REPORT.md` |
| Date | 2026-07-21 |
| Scope | Repository discovery & development readiness only (no implementation) |
| Sources | EKR folders `00`–`27`, `ai/`, `ai-platform/`, `implementation/`, `.github/`, ADRs, Blueprint v2.1 |
| Verdict | **ARCHITECTURE_REVIEW_REQUIRED** |

---

## 1. Current Repository Architecture

ECMP is a **monorepo** with two layers:

```text
EKR (knowledge / governance SoT)
├── 00–27 numbered knowledge folders
├── ai/                 compatibility AI context pack
├── ai-platform/        canonical AI policies, memory, packs, eval
├── docs/ + site/       MkDocs developer portal content
└── tools/              Engineering OS (eos.py, RAG, impact, etc.)

implementation/         application code (thin bootstrap)
├── backend/            FastAPI Case Service (Sprint-01 slice)
├── portal/             Developer Portal (EKR tooling UI — not product UI)
├── frontend/           empty (.gitkeep)
├── infrastructure/     empty (.gitkeep)
├── deployment/         empty (.gitkeep)
└── tests/              empty (.gitkeep)
```

**Documented product architecture (EKR):** seven business domains — Core Platform, CRM, ECMF, KPI & Performance, Dashboard & Analytics, Notification, Administration — with event-driven integration (ADR-001), ECMP not Customer Master SoR (ADR-002), configuration-first (ADR-003).

**Stated coding principle (this discovery brief):**  
`Presentation → Application → Domain`, with Infrastructure implementing inner-layer interfaces; business rules not in controllers/UI.

**What exists in code today:** a single-module FastAPI app (`implementation/backend/app/main.py`) with HTTP handlers, validation, in-memory store, auth stub, and event stub co-located. **No Presentation / Application / Domain / Infrastructure package split.**

---

## 2. Existing Technology Stack

| Concern | Approved (ADR-004) | Present in repo |
|---|---|---|
| Language | Python 3.12+ | Python (local cache shows 3.14 used for tests) |
| API | FastAPI | FastAPI ✅ |
| Validation | (implied Pydantic) | Pydantic v2 ✅ |
| Persistence | PostgreSQL + Alembic | **Not wired** (in-memory `dict` only) |
| DB drivers / ORM | Expected next | **Absent** from `requirements.txt` |
| Contracts | OpenAPI in `07 API Catalog/openapi/` | `case-service.v1.yaml` ✅ |
| Events | `08 Event Catalog/events/events.yaml` | EVT-001 stub emit ✅; **duplicate** draft catalog also exists |
| Auth | Bearer + permission claims | Hard-coded `dev-token` ✅ (placeholder) |
| Frontend | Deferred | Empty folder |
| Container / compose | Not in ADR-004; G0 expects it | **Absent** |
| Message broker | Follow-up ADR | In-process list only |

**Backend deps (`implementation/backend/requirements.txt`):**  
`fastapi`, `uvicorn`, `pydantic`, `httpx`, `pytest` — no SQLAlchemy, Alembic, psycopg/asyncpg, or structured logging libs.

---

## 3. Existing Implementation Status

### 3.1 Implemented (thin / bootstrap)

| Component | Status | Evidence |
|---|---|---|
| Health endpoint | Done | `GET /health` |
| Create case | Done (in-memory) | `POST /cases` — FR-001 / API-001 |
| Get case | Done (in-memory) | `GET /cases/{id}` — FR-002 / API-002 |
| Initial status `REGISTERED` | Done | Matches BR-001 / FR-001a |
| CaseCreated emit stub | Done | In-process `EVENTS` list (EVT-001) |
| Dev auth placeholder | Done | `Authorization: Bearer dev-token` |
| Permission checks | Partial | `cases:create` / `cases:read` on fixed principal |
| API tests | Partial | 4 tests in `tests/test_cases.py` |
| OpenAPI catalog | Done for slice | `07 API Catalog/openapi/case-service.v1.yaml` |
| Traceability (slice) | Done | `26 Traceability/traceability.yaml` TRC-L-001/002 Approved |
| Developer Portal | Done (meta) | `implementation/portal` — RAG/impact/orchestrate UI |

### 3.2 Partially implemented

| Component | Gap |
|---|---|
| AuthZ | Single hard-coded user/permissions; no Role/Permission entities, no org-unit scope |
| Events | Emitted to memory list; no outbox, no broker, no durable emit |
| Customer reference | Accepts any non-empty `customerId`; `customerVerified=false` always; no CM stub contract in `09` |
| Error model | OpenAPI defines `{code,message}`; runtime returns FastAPI default `detail` strings |
| Case domain model | Flat dict in handler; no entities, repositories, or business-action services |
| Documentation GO signals | README / Sprint-01 say GO; readiness roadmap says G0 before B1 |

### 3.3 Missing vs core concepts (this brief)

| Concept | In EKR Data Dictionary / Blueprint? | In code? |
|---|---|---|
| Customer (reference) | Yes (`Customer Reference`) | ID field only |
| Case | Yes (`Case Header`) | Create/get only |
| Case Timeline | Closest: Case Activity / Status History | No |
| Case Note | Closest: Comment / Customer Notes | No |
| Attachment | Yes | No |
| Escalation (branch → HO + reason) | **Not as described** (SLA/escalation reminder only) | No |
| Appointment | **No** | No |
| Schedule Slot | **No** | No |
| Work Order | **No** | No |
| User / Role / Permission | Yes (Core Platform) | Stub principal only |
| Branch | Closest: Organization Unit / channel=`BRANCH` | No Branch entity |
| Audit Log | Yes | **Not persisted / not written** |

### 3.4 Layer / folder structure vs Clean Architecture

Expected (brief): Presentation → Application → Domain ← Infrastructure.

Actual:

```text
implementation/backend/app/main.py   ← all layers in one file
implementation/backend/tests/
```

No domain services, no repositories, no business-action commands, no UI product layer.

---

## 4. Existing Database / Migration Status

| Item | Status |
|---|---|
| PostgreSQL connection | Missing |
| Alembic / migrations | **Missing** (no `alembic.ini`, no revisions) |
| `docker-compose` for DB | **Missing** |
| Physical schema (Case, AuditLog, Outbox) | **Missing** (called out as G0 deliverable in readiness roadmap) |
| Data Dictionary | Draft entity list; Case sample attributes **diverge** from FRD/OpenAPI (`category` vs `caseType`, sample status values, `sla_due_at` mandatory in sample) |
| Seed data | None |

**Conclusion:** Persistence foundation for Sprint 0 / G0 is **not started**. Current create/get loses all data on process restart.

---

## 5. Authentication / RBAC Status

| Item | Status |
|---|---|
| `10 Security and Access Standards` | README placeholder only — **no Role Matrix document** |
| AuthN model ADR | Not accepted (SA lists SSO/auth as open; ADR-004 only locks slice Bearer) |
| Runtime AuthN | Bearer required; only `dev-token` accepted |
| Runtime AuthZ | Permission set hard-coded on that token |
| User / Role / Permission persistence | Missing |
| Org / Branch scoping (BR-CP-02, BR-ECMF-02) | TBD in rules; not implemented |
| Product actors in FRD | “Customer Service (CS)” — **not** “Branch Officer” / “Head Office” |

---

## 6. Audit / Logging Status

| Requirement | Source | Status |
|---|---|---|
| Immutable audit on significant writes | BR-CP-03, BR-ECMF-01, Blueprint | **Not implemented** |
| FRD §9: create **and read** access logged | FRD-001 | **Not implemented**; readiness roadmap challenges audit-on-read |
| Case timeline / activity log | Blueprint ECMF | **Not implemented** |
| Append-only audit store | SA §6 | **Not designed in code** |
| Request / correlation ID | G0 readiness item | **Missing** |
| Application structured logging standard | `21` planned | **Missing** |

Event stub is **not** an audit log.

---

## 7. Testing Status

| Area | Status |
|---|---|
| Unit/API tests for create/get/health/401/404 | Present (`test_cases.py`) |
| AuthZ 403 (wrong token / missing perm) | Partial (wrong token → 403; no multi-role matrix tests) |
| Validation 400 enum cases | Not comprehensively covered |
| Persistence / migration tests | N/A (no DB) |
| Contract tests vs OpenAPI | Missing |
| Integration / outbox / audit tests | Missing |
| `13 Test Strategy` | Placeholder README only |
| Frontend / E2E product tests | N/A |
| CI running `pytest` | **No** (docs CI only) |

---

## 8. CI/CD Status

| Workflow | Purpose | Product backend? |
|---|---|---|
| `.github/workflows/ear-docs.yml` | `eos.py --all` + MkDocs strict build | No |
| `.github/workflows/ai-review.yml` | Advisory AI review pack | No |

Missing for implementation readiness:

- Backend install + migrate + pytest gate
- Container build/publish
- Environment promotion standards (`14 Deployment Standards` is empty placeholder)
- Branch protection / CODEOWNERS for contract PRs (called out in readiness roadmap)

---

## 9. Architecture Compliance Findings

### 9.1 Alignment with approved EKR baseline (Blueprint v2.1 + ADRs + Sprint-01)

| Principle | Compliance |
|---|---|
| Not Customer Master SoR (ADR-002 / BR-003) | Compliant (stores `customerId` only) |
| OpenAPI-first for endpoints | Compliant for create/get |
| Event catalog for CaseCreated | Compliant (stub) |
| Config-first workflow (ADR-003) | N/A for slice (fixed initial status only) |
| PostgreSQL + Alembic (ADR-004) | **Non-compliant** (documented as next; still absent) |
| Audit-first on writes (SA / BR) | **Non-compliant** |
| Domain-oriented boundaries | Conceptual only; single service bootstrap OK for slice |
| Business rules not in controllers | **Violated** — validation & permissions live in route handlers |

### 9.2 Critical mismatch: discovery brief “approved business baseline” vs EKR SoT

The discovery task lists an **approved** baseline including:

1. All customers initially served through a **branch**
2. Branch officers search/view centralized customer data
3. Multiple active Cases per customer
4. Case as core concept
5. Per-Case lifecycle & history
6. Branch **initial diagnosis**
7. Resolve at branch when possible
8. Escalate to **Head Office** when not
9. Explicit **escalation reason**
10. Select from **HO schedule slots**
11. No arbitrary manual schedules
12. **Double-booking / concurrency** prevention
13. HO notification on escalation submit
14. Case changes via **Business Actions** (not generic edit)
15. Timeline/audit for important changes

**Authoritative EKR findings:**

| Baseline item | In Blueprint v2.1 | In DD / FRD / OpenAPI | In code |
|---|---|---|---|
| Branch-first service model | **No** (CS / Handler / Supervisor actors) | No Branch entity | No |
| Branch diagnosis → HO escalate | **No** (assignment + SLA escalation language) | No Escalation entity as described | No |
| Schedule Slot / Appointment | **No** (0 hits in Blueprint extract) | No | No |
| Work Order | **No** | No | No |
| Business Actions pattern | **No** explicit pattern | Generic create/get API | Direct POST body |
| Case core + audit/timeline | Yes (Case + Activity/Status History) | Partial docs | Partial (Case only) |
| KAK document | **Not found anywhere in repository** | — | — |

**Implication:** Implementing the brief’s baseline as-is would **contradict Blueprint Out of Scope / invent features** unless Blueprint, Rules, FRD, catalogs, and ADRs are formally revised (AI Rules #12 / #11). Conversely, implementing only Sprint-01 FRD ignores the brief’s stated business baseline.

### 9.3 Documentation inconsistencies (within repo)

| Issue | Detail |
|---|---|
| Dual GO authority | Root README & `Sprint-01.md` = Approved GO; `IMPLEMENTATION_READINESS_ROADMAP.md` = **G0 mandatory** before B1 product coding |
| Dual BR ID schemes | Sprint `BR-001…` vs enterprise `BR-ECMF-01…` |
| Dual Event catalogs | Normative intent: `events/events.yaml`; also draft `ECMP_Event_Catalog_v1.0.yaml` with different payload shapes (`category` vs `caseType`) |
| SA vs ADR-004 | SA §10 still says stack undecided / ADR-004 “not created”; ADR-004 **Accepted** for FastAPI/PG |
| ADR status | ADR-001..003 still Draft/Proposed; only ADR-004 Accepted |
| Error schema drift | OpenAPI `Error{code,message}` vs FastAPI `detail` |
| Data Dictionary vs FRD Case shape | Attribute naming and mandatory fields differ |
| Security / Deployment / Test Strategy / Integration Catalog | Mostly empty READMEs |
| Layered Clean Architecture | Required by this brief; **not** ADR’d in EKR |

### 9.4 Architectural violations in current code (relative to stated principles)

1. **All business logic in controller** (`main.py` routes).
2. **No Domain layer** — Case is a dict, not an aggregate with invariants.
3. **No Application services / Business Actions** — unrestricted request mapping to store.
4. **No Infrastructure abstractions** — store and event list are globals.
5. **AuthZ duplicated in handlers** rather than Core Platform / shared policy module.
6. **Non-durable events** — crash loses CaseCreated intent (roadmap requires outbox for B1).

These are expected for a bootstrap demo, but they are **not** Sprint 0 / G0 complete.

---

## 10. Critical Gaps

### P0 — Stop-the-line before feature expansion

1. **Business baseline conflict** between discovery brief (branch / HO / scheduling / work orders) and EKR Blueprint v2.1 + FRD-001.
2. **KAK missing** from repository — cannot validate “approved” baseline provenance.
3. **Conflicting build authorization** (Sprint-01 GO vs G0 gate).
4. **No persistence / migrations / compose** despite ADR-004.
5. **No write-path audit** despite Critical BRs.
6. **No Role Access Matrix** (`10` empty).
7. **Clean Architecture layering** requested but not decided in ADR — risk of ad-hoc structure.

### P1 — Blocks solid Sprint 0 / G0 floor

8. Error envelope not aligned to OpenAPI.
9. Dual Event / BR SoT not killed.
10. Customer Master stub contract absent (`09`).
11. CI does not run backend tests.
12. Request/correlation ID missing.
13. Outbox table missing.
14. Technical Standards (`21`) empty beyond checklist.

### P2 — Deferred but track

15. Broker ADR, SSO ADR, frontend ADR.
16. Full lifecycle (assign/status), Notification, SLA, CRM 360 search.
17. Product UI (frontend empty; portal is DX only).

---

## 11. Sprint 0 Recommended Work Breakdown

Treat Sprint 0 as **G0 — Slice Freeze & Platform Floor** from `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md`, **plus** an explicit Architecture Review gate for the business-baseline conflict.

### Task S0-0 — Architecture / Business Reconciliation (BLOCKING)

| Activity | Outcome |
|---|---|
| Locate/import KAK or formally supersede with Blueprint v2.1 | Single business SoT |
| Decision: adopt Blueprint CS/ECMF model **or** revise Blueprint/FRD for branch–HO–slot model | ADR + updated BR/FR |
| Decide whether Presentation→Application→Domain is mandatory for backend | New ADR or SA amendment |
| Resolve Sprint-01 GO vs G0 | Written Build Authorization policy |

**Files expected:**  
`01 Business Blueprint/*`, `02 Business Rules/*`, `03 Functional Requirements/*`, `04 Solution Architecture/*`, `05 Architecture Decision Records/*`, `06 Data Dictionary/*`, `27 Project Decisions/*`, `ai/sprint/*`, possibly new KAK path under `01` or `27`.

### Task S0-1 — Single SoT freeze (active slice)

- Declare delivery BR SoT (`BR-001…` vs `BR-ECMF-*`).
- Event SoT = `08 Event Catalog/events/events.yaml` only; mark/reconcile duplicate YAML.
- Patch FRD audit/idempotency decisions (write-audit required; read-audit deferred unless BO funds).
- Document `caseId` strategy + UTC rule + Bearer claims shape.

**Files:** `02…`, `03…/ECMP_FRD_ECMF_v0.1.md`, `08 Event Catalog/*`, `26 Traceability/*`, `27 Project Decisions/*`.

### Task S0-2 — Contracts for B1 floor

- OpenAPI Error `{code,message}` + validation mapping.
- Minimal Role matrix (`cases:create` / `cases:read`).
- CM Integration Stub in `09`.
- Align Data Dictionary Case section to FRD/OpenAPI (non-normative banner for samples).

**Files:** `07 API Catalog/openapi/case-service.v1.yaml`, `10 Security and Access Standards/*`, `09 Integration Catalog/*`, `06 Data Dictionary/*`.

### Task S0-3 — Platform floor (readiness engineering only)

- Add SQLAlchemy/Alembic + driver deps (no stack redesign).
- Alembic revision 0: `cases`, `audit_log`, `outbox`.
- `docker-compose.yml` for PostgreSQL.
- Request-id middleware stub.
- Error handler aligning to OpenAPI.
- Optional skeleton packages: `domain/`, `application/`, `infrastructure/`, `api/` **only if ADR from S0-0 mandates it**.

**Files:**  
`implementation/backend/requirements.txt`,  
`implementation/backend/alembic/*`,  
`implementation/backend/app/**` (or new package tree),  
`implementation/infrastructure/docker-compose.yml` (or repo-root compose),  
`implementation/backend/README.md`,  
`21 Technical Standards/*` (local run / env / error convention).

### Task S0-4 — CI green on current + migration smoke

- GitHub workflow: install backend deps → migrate → pytest.
- Keep docs workflow separate.

**Files:** `.github/workflows/*` (new backend CI), possibly `implementation/backend/tests/*`.

### Task S0-5 — Explicit non-goals for Sprint 0

Do **not** implement in Sprint 0: assign/status, Notification product, Schedule Slot, Appointment, Work Order, Branch–HO escalation flows, product frontend — unless S0-0 formally expands Blueprint scope and catalogs first.

---

## 12. Files Expected to Change (by task)

| Task | Primary files |
|---|---|
| S0-0 | `01 Business Blueprint/`, `04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`, `05 Architecture Decision Records/` (new ADR(s)), `27 Project Decisions/`, `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md`, `ai/sprint/Sprint-01.md`, root `README.md` |
| S0-1 | `02 Business Rules/*`, `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md`, `08 Event Catalog/events/events.yaml`, `08 Event Catalog/ECMP_Event_Catalog_v1.0.yaml`, `26 Traceability/traceability.yaml` |
| S0-2 | `07 API Catalog/openapi/case-service.v1.yaml`, `09 Integration Catalog/`, `10 Security and Access Standards/`, `06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md` |
| S0-3 | `implementation/backend/**`, `implementation/infrastructure/**` or compose at agreed path, `21 Technical Standards/` |
| S0-4 | `.github/workflows/`, `implementation/backend/tests/` |

No deletes/renames of existing EKR structure required for Sprint 0 unless S0-0 explicitly decides to retire the duplicate event catalog file.

---

## 13. Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Coding against wrong business model (branch/HO vs CS/ECMF) | Large rework; catalog/ADR violations | Complete S0-0 before any feature code |
| Treating Sprint-01 “GO” as license to skip G0 | Non-durable demo becomes “done” | Enforce Build Authorization checklist |
| Inventing Schedule/Appointment/Work Order without catalogs | AI Rules #2/#6/#12 breach | Catalog-first or OQ |
| Dual BR/Event SoT | Conflicting tests & AI context | Kill dualism in S0-1 |
| Audit-on-read as written in FRD | Storage/latency cost | BO decision in G0; patch FRD |
| Premature Clean Architecture scaffolding without ADR | Inconsistent packages | ADR in S0-0 |
| Continuing in-memory as primary store | Data loss; false confidence | Compose + Alembic 0 in S0-3 |
| Empty Security / Deployment standards at UAT | Late compliance ambush | Minimal Role matrix + secrets/env notes in G0 |
| Portal mistaken for product UI | Wrong UX investment | Keep portal DX-only; frontend deferred per ADR-004 |

---

## 14. Baseline Comparison Matrix (summary)

| # | Approved baseline (discovery brief) | Repo SoT today | Gap class |
|---|---|---|---|
| 1 | Customers via branch | Org unit / channel optional; CS actors | **Business model** |
| 2 | Branch officers search customer | Planned CRM FR-010; not built | Missing / model |
| 3 | Multiple active Cases | Allowed by silence; not constrained | OK / unspecified |
| 4 | Case core | Yes | Partial impl |
| 5 | Lifecycle & history | Documented; not built | Missing |
| 6 | Branch diagnosis | Not in Blueprint | **Business model** |
| 7 | Resolve at branch | Not in Blueprint | **Business model** |
| 8 | Escalate to HO | Not in Blueprint | **Business model** |
| 9 | Escalation reason | Not in catalogs | **Business model** |
| 10 | HO schedule slots | Absent | **Missing concept** |
| 11 | No arbitrary schedules | Absent | **Missing concept** |
| 12 | Double-book prevention | Absent | **Missing concept** |
| 13 | HO notify on escalation | Notification domain exists; not this flow | Missing |
| 14 | Business Actions | Not specified; generic API | Pattern gap |
| 15 | Timeline/audit | Required in BR/SA; not in code | Critical eng gap |

---

## 15. Verdict

```text
ARCHITECTURE_REVIEW_REQUIRED
```

**Why not READY_FOR_SPRINT_0:** Sprint 0 platform-floor work cannot safely start until the **business SoT conflict** (branch–HO–scheduling baseline vs Blueprint v2.1 / FRD-001) and **layering ADR** are resolved; otherwise engineering will either invent out-of-scope features or ignore the stated approved baseline.

**Why not READY_WITH_BLOCKERS alone:** Blockers are not only missing compose/CI/DB — the **authoritative business architecture itself is contested**. That requires Architecture Board / Business Owner review before readiness engineering proceeds under a single SoT.

**Allowed after review approval:** execute Sprint 0 / G0 tasks S0-1…S0-4 against the **reconciled** baseline, still without product feature expansion beyond readiness engineering.

---

*End of discovery. No implementation changes were made except creation of this report.*
