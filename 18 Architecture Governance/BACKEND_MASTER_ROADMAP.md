# ECMP Backend Master Roadmap

| Field | Value |
|---|---|
| Document ID | BMR-001 |
| Version | 0.1 |
| Owner | Lead Software Engineer |
| Reviewer | Solution Architect / Architecture Board |
| Status | 🟡 Active — pending Architecture Board approvals between tasks |
| Last Update | 2026-08-21 |
| Production Ready | **No** (backend-wide). CM Batch 1 **lab/synthetic** track: READY WITH CONDITIONS accepted |

## Purpose

Single execution roadmap for completing the ECMP **backend** to Production Ready. Every implementation task must belong to exactly one Epic. Work is derived only from FRD, OpenAPI, Event Catalog, approved architecture, this roadmap, and the existing repository.

## Production Ready criteria (binding)

- All approved Epics COMPLETE
- No module remains PARTIAL for in-scope approved functionality
- No unfinished approved functionality remains
- No temporary placeholder remains except intentionally approved stubs
- Migrations verified; tests passing; release/config/dependency/ops readiness complete
- Known risks documented

## Priority order (binding)

1. Blocking defects  
2. Broken tests  
3. Missing approved functionality  
4. Architecture gaps  
5. Integration gaps  
6. Technical debt  
7. Hardening  
8. Performance  
9. Documentation  

## Epic register

| Epic ID | Name | Status | Progress |
|---|---|---|---|
| EPIC-CM-B1 | Complaint Management Batch 1 (FR-001…FR-004) | **READY (lab)** | Features COMPLETE; Mode A lab COMPLETE evidence **GOV-MODEA-M3C-001** (2026-07-31); lab READY WITH CONDITIONS **accepted** (EX-20260729-01); canonical HTTP **DEC-026** `/api/v1/cm`; API-500…513 |
| EPIC-CM-B1-OPS | Batch 1 release cutover (redeploy, config stance, exceptions) | **COMPLETE (lab)** | OPS-01/01b/02/03 + lab countersign done; Docker recreate optional follow-up |
| EPIC-PLATFORM | Platform / CI / auth / observability (approved ADR track) | PARTIAL | Existing platform modules; not fully signed Production Ready |
| EPIC-ECMF-LEGACY | Legacy case/complaint stack (pre–Batch 1) | **RETIRED HTTP (Mode A)** | Foundation `/api/v1/complaints` **unmounted** + `complaints*` **DROP** (DEC-026 M-026-1…3 / Alembic `0072`); CA BC ticket-nested **tetap**; defect-driven only |
| EPIC-CM-F4 | Escalation / Resolution (DEC-F4 / FRD-CM-002) | **NOT APPROVED FOR CODE** | Spec/OpenAPI/review packs exist; implementation blocked until Board unlock |

---

## EPIC-CM-B1 — Complaint Management Batch 1

### Objective
Deliver LOCKED FRD-CM-001 v1.1 Batch 1 (registration, customer search/confirm/360-min, duplicate detection, attachments) on durable persistence with catalog-aligned APIs and persist-only outbox.

### Scope
- Modules: `backend/app/modules/cm_batch1/`, `backend/app/integrations/customer/`
- Migrations: `0040`…`0045` (`0045` later-review `complaint_id`)
- APIs: API-500…513 under `/api/v1/cm/...` (plus shared attachment CAP alignments; API-513 supervisor queue)
- Events: outbox persist only (publisher out of Batch 1 S3)
- **DEC-020:** Aggregate SoT for Batch 1 intake; does **not** retire `/api/v1/complaints`; does **not** mount `complaint_foundation_router`; cutover only via future Retirement DEC

### Dependencies
- FRD-CM-001 v1.1 LOCKED
- OpenAPI `complaint-management-batch1.v1.yaml`
- ADR-014 / ADR-015 (architecture baseline; no redesign in feature code)
- DEC-020 dual-SoT coexistence (Accepted)
- Platform DB/session/auth envelope

### Current Progress
- S0 contracts / S1 slice / S2 persistence+duplicate+attachments / foundation 0043 / CustomerProvider DI — **done**
- S3 verification — **READY WITH CONDITIONS** (chat + tests)
- Local Docker migrate gate (`0040→0043` + TestClient smoke) — **done** (`GOV-S3-CM-B1-MIG-001`)

### Remaining Work
- Moved to **EPIC-CM-B1-OPS** (cutover / conditions)

### Definition of Done
- Feature FR-001…FR-004 behaviour per LOCKED FRD + OpenAPI
- Migrations reversible; tests green
- Release classification **READY** (not merely READY WITH CONDITIONS) after OPS epic conditions cleared

---

## EPIC-CM-B1-OPS — Batch 1 release cutover

### Objective
Clear remaining S3 conditions so Batch 1 can be classified **READY** for a named environment.

### Scope
- Rebuild/redeploy backend image containing Batch 1 + health probes
- Document / set `CUSTOMER_PROVIDER` stance per environment
- Architecture Board acceptance of residual stubs/gaps as release exceptions
- Optional post-deploy HTTP smoke on `/api/v1/cm/*` via container

### Dependencies
- EPIC-CM-B1 feature complete
- Local DB at `0043` (done for Docker `ecmp`)

### Current Progress
- All OPS tasks for local lab cutover — **COMPLETE**
- EX-20260729-01 — **Countersigned lab/synthetic-only** (2026-07-29)
- Optional: Docker recreate to apply `CUSTOMER_PROVIDER` env when daemon returns

### Remaining Work
- None for EPIC-CM-B1-OPS lab scope
- Real-customer Production Ready remains **out of scope** until EX-A/B/C exit + optional Business Owner/Security countersigns on the exception pack

### Definition of Done
- Board signs READY (or READY WITH CONDITIONS explicitly accepted for a named env) — **met for lab/synthetic via mission Architecture countersign**
- Container HTTP path matches DB head — **met** (when Docker last verified)
- Residuals recorded as approved exceptions — **met** (EX-A…EX-H)

---

## EPIC-PLATFORM — Platform track (summary)

### Objective
Keep existing platform floor (auth, CI, health, audit envelope, outbox infrastructure where already present) production-safe without inventing new product features.

### Scope / Remaining
- Inventory and close only **approved** ADR/DEC platform gaps (e.g. JWT target mode, observability activation) when Board prioritizes them
- Do not expand into broker selection until ADR-009 revisit is approved
- **Proposed (pending approval):** `TASK-PLATFORM-OPS-SEED-001` — close TD-OPS-002/003 (GoLive password drift + ADMIN empty `role_permissions`)

### Dependencies
- Existing ADRs / DECs
- Ops approval for password reset / seed repair (EX pack)

### Current Progress
- PARTIAL — floor exists; lab CM works via `golive_supervisor` and (after 0044) `golive_admin`
- **TASK-PLATFORM-OPS-SEED-001 (narrow):** TD-OPS-003 **CLOSED** via `0044_admin_rbac_repair`
- **TASK-PLATFORM-CI-COV-001:** **CLOSED** — measured coverage **90.59%**; CI/`pyproject` `--cov-fail-under=90` green (1128 passed on `ecmp_ci_qa`)
- TD-OPS-002 (agent/viewer password drift) — **still open** (ops cleanup deferred)
- **ADR-012 Accepted** (2026-07-29) via `GOV-CS-ADR-012` / **TASK-PLATFORM-ADR012-ACCEPT-001** (governance only)
- **SEC-MIG-001 Phase 0** (decision) — **completed**
- **TASK-PLATFORM-SECMIG-P1-001 / SEC-MIG Phase 1** — **COMPLETE** (Keycloak + profile `auth` + realm-as-code `ecmp` + OPS-IDP-001); **no application auth wiring**
- SEC-MIG Phase 2 (`ECMP_AUTH_MODE` / JWKS validator / OpenAPI+CI dual-mode) — **STILL REQUIRES separate Architecture approval**
- ADR-010 SIT activation remains blocked until SEC-MIG Phase 3

### Remaining Work (approval-gated)
1. **TASK-PLATFORM-ADR012-ACCEPT-001** — **COMPLETE**
2. **TASK-PLATFORM-SECMIG-P1-001** — **COMPLETE** (Phase 1 IdP baseline; infra + ops docs only)
3. **SEC-MIG Phase 2** — propose as a **separate** task; **blocked until Architecture approval** (no JWT/`ECMP_AUTH_MODE`/OpenAPI/CI wiring until then)
4. TD-OPS-002 password drift — **excluded** from current track (ops cleanup deferred by Architecture)
5. ADR-009 Eventing epic unlock before outbox publisher

### Explicit non-authorization (Phase 1 complete does **not** authorize Phase 2+)

Phase 1 completion does **not** authorize:

- JWT validation / JWKS consumption in ECMP
- `ECMP_AUTH_MODE` runtime switch
- `backend/app` authentication changes
- migrations / OpenAPI / CI dual-mode suites
- SIT/UAT shared-env activation (Phase 3)

### Definition of Done (TASK-PLATFORM-OPS-SEED-001)
- Investigate why `0039_admin_rbac_repair` did not yield ADMIN grants in OPS01 DB
- Repair seed/migration **or** documented runbook so ADMIN matrix includes CM permissions as intended
- Align GoLive agent/viewer passwords with docs **or** correct docs (no silent secret invent unless approved)
- Evidence: login + CM permission smoke
- Close or reclassify TD-OPS-002/003 in BMR + EX pack; no EX-A…H product-scope change

### Definition of Done (Epic)
- Platform gates required for backend Production Ready are evidenced and signed

---

## EPIC-ECMF-LEGACY — Legacy complaint/case stack

### Objective
Preserve backward-compatible legacy modules; fix only verified defects.

### Remaining Work
- HTTP Foundation **unmounted**; tabel `complaints*` **DROP** (H1 — tidak di-merge ke CM)
- CA BC `complaint_cases*` + ticket-nested router **tetap** — bukan objek DEC-026
- Defect-driven only pada sisa CA BC; jangan menghidupkan `/api/v1/complaints`

---

## EPIC-CM-F4 — Escalation / Resolution

### Objective
Future batch per DEC-F4 / FRD-CM-002 Draft.

### Status
**Blocked** — implementation must not start until Architecture Board unlocks coding after FRD/ADR acceptance.

### Remaining Work
- None until approval

---

## Discovered work (pending classification / approval)

| ID | Discovery | Classification | Impact | Recommended order |
|---|---|---|---|---|
| TD-CM-001 | Confirm lock not enforced on create | Known gap (S1/S2) | Medium | **Closed (Mode A lab)** — create requires confirm lock matching `customerId` (2026-07-31) |
| TD-CM-002 | EnumerationGuard in-process only | Soft limit | Medium | Exception or shared-store epic |
| TD-CM-003 | Antivirus `STUB_ONLY` default | Integration gap | Medium | Exception until AV adapter approved |
| TD-CM-004 | Enterprise CustomerProvider UNAVAILABLE | Integration gap / approved stub | High for real-customer prod | Separate integration epic after approval |
| TD-CM-005 | Create→attachment bind split TX / later-review path | Known design residual | Low–Medium | Visibility API-513 + `complaintId` (M3b/M3d); TX harden only if approved |
| TD-OPS-001 | Compose backend image lag vs DB head after local migrate | Operational | High on container restart | Mitigated by TASK-OPS-01 rebuild |
| TD-OPS-002 | Documented GoLive agent/viewer passwords fail login (401) | Operational / secret drift | Agent UAT path broken | Record in exception pack / reset only if approved |
| TD-OPS-003 | ADMIN role has 0 `role_permissions` in local DB | Data/seed debt | **Closed** by `0044_admin_rbac_repair` (GOV-PLATFORM-OPS-SEED-001) |

---

## Execution rule

After each completed task: produce the standard implementation report and **wait for Architecture approval** before starting the next ranked task.

**Next recommended task (pending approval):** Propose **SEC-MIG Phase 2** (JWT validation path / `ECMP_AUTH_MODE`) as a separate Architecture-approved task. Phase 1 IdP baseline is complete; do **not** start Phase 2 without Board unlock.
