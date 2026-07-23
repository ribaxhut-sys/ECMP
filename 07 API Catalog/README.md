# 07 API Catalog


| Field | Value |
|---|---|
| ID | API-000 |
| Version | 0.2 |
| Owner | Backend Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Katalog kontrak API ECMP (internal dan exposed), termasuk versioning dan ownership.

## Owner
- Document Owner: API Owner / Tech Lead
- Reviewers: Solution Architect, Consumers, Security

## Status
Approved (baseline) — case-service v1 terkatalog (create/get + lifecycle actions, konsolidasi Sprint-03A); API planned mengikuti Traceability.

## API Inventory

### case-service v1 — [`openapi/case-service.v1.yaml`](./openapi/case-service.v1.yaml) v1.7.0 — **NORMATIF (satu-satunya spec)**
| API ID | Method & Endpoint | Description | Auth | Status |
|---|---|---|---|---|
| API-001 | POST /v1/cases | Create case (FR-001, emit EVT-001 CaseCreated) | bearerAuth, permission `cases:create` | 🟢 Implemented (Sprint-01) |
| API-002 | GET /v1/cases/{caseId} | Get case by id (FR-002) | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-01) |
| API-003 | POST /v1/cases/{caseId}/assign | Assign/reassign case (FR-003, emit EVT-002 + EVT-003; status non-assignable = 409 INVALID_STATE) | bearerAuth, permission `cases:assign` | 🟢 Implemented (Sprint-02B) |
| API-004 | POST /v1/cases/{caseId}/status | Change case status via allowed transition (FR-004, emit EVT-003; transisi ilegal = 409 INVALID_TRANSITION) | bearerAuth, permission `cases:status` | 🟢 Implemented (Sprint-02B) |
| API-005 | GET /v1/cases | List case terpaginasi/terfilter (FR-005; filter status/priority/caseType/assigneeId; sort tetap createdAt desc) | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-03B) |
| API-006 | GET /v1/cases/{caseId}/timeline | Timeline + Audit History (projection over `audit_log`) | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-06) |
| API-007 | GET /v1/cases/{caseId}/notes | List append-only internal notes | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-06) |
| API-008 | POST /v1/cases/{caseId}/notes | Create append-only internal note | bearerAuth, permission `cases:notes:create` | 🟢 Implemented (Sprint-06) |
| — | GET /health | Liveness check (di luar prefix /v1) | None | 🟢 Implemented |
| — | GET /health/ready | Readiness check — DB `SELECT 1` (Sprint-08) | None | 🟢 Implemented |

### complaint-service v1 — [`openapi/complaint-service.v1.yaml`](./openapi/complaint-service.v1.yaml) **1.0.0** — foundation stack (Production)
| API ID | Method & Endpoint | Description | Auth | Status |
|---|---|---|---|---|
| API-201 | POST /api/v1/complaints | Create complaint (status NEW; audit `complaint.create`) | bearerAuth, permission `complaints:create` | 🟢 Implemented |
| API-202 | GET /api/v1/complaints | List complaints (paginated/filtered) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-203 | GET /api/v1/complaints/{id} | Get complaint by id | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-204 | PUT /api/v1/complaints/{id} | Update complaint fields (status immutable; audit `complaint.update`) | bearerAuth, permission `complaints:update` | 🟢 Implemented |
| API-224 | PATCH /api/v1/complaints/{id}/status | Validated status transition (TASK-009; RESOLVED only via API-225; invalid → 400; timeline + audit) | bearerAuth, permission `complaints:update` | 🟢 Implemented |
| API-225 | POST /api/v1/complaints/{id}/resolution | Resolve (IN_PROGRESS→RESOLVED; mandatory resolution record; timeline `complaint.resolved`) | bearerAuth, permission `complaints:update` | 🟢 Implemented |
| API-226 | GET /api/v1/complaints/{id}/resolution | Get current resolution (404 if none) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-205 | POST /api/v1/complaints/{id}/assign | Assign/reassign (NEW→ASSIGNED; history retained; timeline written; reason required on reassign) | bearerAuth, role `SUPERVISOR` + permission `complaints:assign` | 🟢 Implemented |
| API-206 | GET /api/v1/complaints/{id}/assignments | List assignment history | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-207 | POST /api/v1/complaints/{id}/escalate | Escalate (ASSIGNED/IN_PROGRESS→ESCALATED; rejects NEW/RESOLVED/CLOSED) | bearerAuth, role `SUPERVISOR` + permission `complaints:escalate` | 🟢 Implemented |
| API-208 | GET /api/v1/complaints/{id}/escalations | List escalation history | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-301 | POST /api/v1/complaints/{id}/escalations | Escalation Request Branch→HO (status REQUESTED; IN_PROGRESS only; no Resolution; one active) | bearerAuth, permission `complaints:update` | 🟢 Implemented |
| API-302 | GET /api/v1/escalations/{id} | Get escalation detail by id | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-303 | POST /api/v1/escalations/{id}/approve | Approve REQUESTED escalation (HO Scheduler/Admin; once only) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-304 | POST /api/v1/escalations/{id}/reject | Reject REQUESTED escalation (HO Scheduler/Admin; once only) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-305 | POST /api/v1/escalations/{id}/appointments | Book appointment on APPROVED escalation (one active; no engineer overlap) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-306 | GET /api/v1/appointments/{id} | Get appointment by id | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-307 | POST /api/v1/appointments/{id}/check-in | Customer check-in for BOOKED appointment (once only) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-308 | POST /api/v1/appointments/{id}/complete | Complete CHECKED_IN appointment (once only; result COMPLETED/PARTIALLY_COMPLETED) | bearerAuth, role HO Engineer/Admin + `appointments:complete` | 🟢 Implemented |
| API-309 | POST /api/v1/appointments/{id}/no-show | Mark BOOKED appointment as customer no-show (once only) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-310 | POST /api/v1/complaints/{id}/final-resolution | Submit Final Resolution after COMPLETED appointment (once only; complaint stays IN_PROGRESS) | bearerAuth, role HO Engineer/Admin + `appointments:complete` | 🟢 Implemented |
| API-311 | GET /api/v1/complaints/{id}/final-resolution | Get submitted Final Resolution (404 if none) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-209 | GET /api/v1/complaints/{id}/timeline | Immutable timeline from `complaint_timelines` (created_at DESC newest first; empty list OK; includes actorName) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-210 | GET /api/v1/reports/summary | Report summary (COUNT; optional branchId/dateFrom/dateTo) | bearerAuth, permission `reports:read` | 🟢 Implemented |
| API-211 | GET /api/v1/reports/by-status | Counts by ComplaintStatus (GROUP BY) | bearerAuth, permission `reports:read` | 🟢 Implemented |
| API-212 | GET /api/v1/reports/by-branch | Counts by branch (GROUP BY; total DESC) | bearerAuth, permission `reports:read` | 🟢 Implemented |
| API-213 | POST /api/v1/users | Create user (unique username/email; bcrypt password; default isActive=true) | bearerAuth, permission `users:create` | 🟢 Implemented |
| API-214 | GET /api/v1/users | List users (paginated) | bearerAuth, permission `users:read` | 🟢 Implemented |
| API-215 | GET /api/v1/users/{id} | Get user by id | bearerAuth, permission `users:read` | 🟢 Implemented |
| API-216 | PUT /api/v1/users/{id} | Update user (password re-hashed when provided; hash never exposed) | bearerAuth, permission `users:update` | 🟢 Implemented |
| API-217 | PATCH /api/v1/users/{id}/status | Soft activate/deactivate (`isActive`) | bearerAuth, permission `users:update` | 🟢 Implemented |
| API-218 | POST /api/v1/auth/login | Login (bcrypt; JWT access 15m; HttpOnly refresh cookie 7d; audit `auth.login`) | None (public) | 🟢 Implemented |
| API-219 | POST /api/v1/auth/refresh | Rotate refresh cookie; issue new access token (audit `auth.refresh`) | Refresh cookie | 🟢 Implemented |
| API-220 | POST /api/v1/auth/logout | Revoke refresh token + clear cookie (audit `auth.logout`) | Refresh cookie | 🟢 Implemented |
| API-221 | GET /api/v1/auth/me | Current user + roles/permissions | bearerAuth | 🟢 Implemented |
| API-222 | GET /api/v1/customers | List local customer references (paginated; optional `q`) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-223 | GET /api/v1/branches | List active branch references (paginated; optional `q`) | bearerAuth, permission `complaints:read` | 🟢 Implemented |

> **2026-07-23 (TASK-018 Final Resolution / DEC-011):** complaint-service —
> API-310 submit Final Resolution after `COMPLETED` appointment; API-311 GET.
> Timeline `complaint.final_resolution_submitted`. Migration
> `0011_final_resolution`. Complaint stays `IN_PROGRESS`; escalation stays
> `APPROVED`. Closure / approval / notification / SLA out of scope.
>
> **2026-07-23 (TASK-017 Customer No Show / DEC-010):** complaint-service —
> API-309 no-show for `BOOKED` appointments → `NO_SHOW`. Timeline
> `complaint.appointment_no_show`. Migration `0010_appointment_no_show`.
> Does not auto-close complaint or escalation. Reschedule / rebooking /
> notification / SLA out of scope.
>
> **2026-07-23 (TASK-016 Appointment Completion / DEC-009):** complaint-service —
> API-308 complete for `CHECKED_IN` appointments → `COMPLETED`. Timeline
> `complaint.appointment_completed`. Migration `0009_appointment_completion`.
> Does not auto-close complaint or escalation. No-show / notification /
> survey / SLA / calendar out of scope.
>
> **2026-07-23 (TASK-015 Customer Check-In / DEC-008):** complaint-service —
> API-307 check-in for `BOOKED` appointments → `CHECKED_IN`. Timeline
> `complaint.appointment_checked_in`. Migration `0008_appointment_checkin`.
> No-show / notification out of scope.
>
> **2026-07-23 (TASK-014 Appointment Booking / DEC-007):** complaint-service —
> API-305 book appointment on `APPROVED` escalation + API-306 get by id.
> Timeline `complaint.appointment_booked`. Migration `0007_appointments`.
> Status `BOOKED` only; calendar/slots/check-in/completion/notification out of
> scope. Escalation GET embeds optional `activeAppointment`.
>
> **2026-07-23 (TASK-012 Escalation Review):** complaint-service — API-303
> approve + API-304 reject for `REQUESTED` escalations. Permission
> `escalations:review` for HO Scheduler / Admin. Timeline
> `complaint.escalation_approved` / `complaint.escalation_rejected`.
> Migration `0006_escalation_review`. Appointment booking delivered in TASK-014.
>
> **2026-07-23 (TASK-011 Escalation Request):** complaint-service — API-301
> (`POST /api/v1/complaints/{id}/escalations`) + API-302
> (`GET /api/v1/escalations/{id}`). Branch → HO request with status
> `REQUESTED`; timeline `complaint.escalation_requested`. Review/Approve
> out of scope. Migration `0005_complaint_escalations` extends
> `complaint_escalations` with request fields.
>
> **2026-07-23 (TASK-010 Complaint Resolution):** complaint-service — API-225
> (`POST /api/v1/complaints/{id}/resolution`) + API-226 GET current resolution.
> `IN_PROGRESS`→`RESOLVED` only via resolution form/endpoint; PATCH status
> matrix no longer allows direct RESOLVED.
>
> **2026-07-23 (TASK-009):** complaint-service — API-224 status transition
> (`PATCH /api/v1/complaints/{id}/status`) with validated matrix; `PENDING`
> added to ComplaintStatus. NEW→ASSIGNED remains Assign (API-205).
>
> **2026-07-23 (TASK-008):** complaint-service — timeline UI uses API-209
> (`GET /api/v1/complaints/{id}/timeline`) read-only. Sort is newest-first;
> `actorName` added for display. Create writes `complaint.created`; priority
> update writes `complaint.updated` with `changeType=PRIORITY_CHANGED`.
>
> **2026-07-23 (TASK-007):** complaint-service — assignee UI uses existing API-205
> (`POST /api/v1/complaints/{id}/assign`) + API-214 user list (`isActive=true`) as
> reference picker. User schema adds optional `roleCode`/`roleName` so assignee
> select shows Name + Role without exposing UUIDs.
>
> **2026-07-23 (TASK-005):** complaint-service — added API-223 branch reference list for Create Complaint `branchId` selection (active `branches` rows; no UUID typing).
>
> **2026-07-23 (TASK-004):** complaint-service — added API-222 local customer reference list for Create Complaint selection (local `customers` cache; not Customer Master SoR / not API-010).
>
> **2026-07-23 (TASK-016 / Production Go-Live):** complaint-service OpenAPI `info.version` set to **1.0.0** (Production). No path/schema additions; go-live only.
>
> **2026-07-23 (TASK-014 / RC1):** complaint-service OpenAPI `info.version` set to **1.0.0-rc1** (application Release Candidate). No path/schema additions; code freeze active.
>
> **2026-07-23 (TASK-010):** complaint-service contract baseline — production authentication API-218..API-221 (login/refresh/logout/me; refresh rotation; HttpOnly Secure SameSite=Lax cookie). Prior catalog label was v1.7.0.
>
> **2026-07-23 (TASK-008):** complaint-service — added user management API-213..API-217.
>
> **2026-07-23 (TASK-007 reporting slice):** complaint-service v1.5.0 — added reporting foundation API-210..API-212.
>
> **2026-07-23 (TASK-006):** complaint-service v1.4.0 — added API-209 Timeline read (`GET /api/v1/complaints/{id}/timeline`).
>
> **2026-07-23 (CR-001 stabilization):** complaint-service bumped to v1.3.0 — removed `REGISTERED`/`PENDING_REVIEW`/`REOPENED`; status SoT is `ComplaintStatus` (`NEW`, `ASSIGNED`, `IN_PROGRESS`, `ESCALATED`, `RESOLVED`, `CLOSED`); timeline events standardized; response/error envelopes aligned. No path or auth contract changes.
>
> **2026-07-22 (Sprint-03A, DEC-006 D6/U-6):** `case-actions.v1.yaml` dikonsolidasikan ke `case-service.v1.yaml` — kini satu-satunya spec normatif untuk case-service. `case-actions.v1.yaml` masih ada di disk tetapi ditandai `x-status: superseded` (paths kosong) dan tidak lagi dibaca oleh tooling/test; dipertahankan hanya agar tautan lama tidak 404. Tidak ada perubahan perilaku API atau payload event — murni sinkronisasi katalog terhadap runtime yang sudah berjalan sejak Sprint-02B.
>
> **2026-07-22 (Sprint-03B):** API-005 (list cases) di-freeze dan diimplementasikan; merged ke `case-service.v1.yaml` v1.5.0 dari draft `dashboard-queues.v1.draft.yaml`. Sort dikunci `createdAt` descending (keputusan CTO, design review Sprint-03B) — sort dapat dikonfigurasi eksplisit di luar scope versi ini. API-010 (Customer 360 read) **ditunda** — lihat `implementation/backend/ACR_SPRINT02B.md` ACR-002: draft/FRD-003 mengasumsikan profil pelanggan nyata, bertentangan dengan larangan fabrikasi data di INT-001 untuk mode stub.
>
> **2026-07-23 (foundation TASK-003):** complaint-service v1.0.0 added for the root `backend/` stack (`/api/v1/complaints`). Parallel to case-service; assignment/escalation/timeline remain out of scope.

### Planned
| API ID | Method & Endpoint | Description | Draft spec | Status |
|---|---|---|---|---|
| API-010 | GET /v1/customers/{customerId} | Customer reference read (CRM) — **ditunda, lihat ACR-002** | [`drafts/customer-read.v1.draft.yaml`](./openapi/drafts/customer-read.v1.draft.yaml) | Deferred |
| API-040 | GET /v1/dashboard/queues | Dashboard queues (Sprint-03) | [`drafts/dashboard-queues.v1.draft.yaml`](./openapi/drafts/dashboard-queues.v1.draft.yaml) | Planned |

> **Label gate:** G1 = gate masuk Sprint-02 (lihat `13 Test Strategy`); "Sprint-02 / gate G1" merujuk hal yang sama.

### Candidate (FRD-007 Administration — belum ada draft spec)
Kandidat API Administration/Core Platform **API-050..API-059** (admin-config: reference data, workflow/SLA config, calendars, escalation, templates, change-requests, versions, settings, audit-config) dan **API-060..API-062** (Core Platform SoT: users, roles, role-permission) didefinisikan di [`../03 Functional Requirements/ECMP_FRD_Administration_v0.1.md`](../03%20Functional%20Requirements/ECMP_FRD_Administration_v0.1.md) §8. Status **Candidate** — belum boleh dibuat draft normatif sebelum FRD-007 DoR; draft OpenAPI wajib dibuat di `openapi/drafts/` sebelum implementasi (contract-first).

### Konvensi `openapi/drafts/`
File di `openapi/drafts/` (penamaan `<nama>.v<major>.draft.yaml`, `info.version: *-draft`, `x-status: draft`) adalah **skeleton non-normatif**: bahan review contract-first untuk memenuhi entry gate G1 ("OpenAPI merged sebelum kode"). Draft menjadi normatif **hanya setelah** direview dan di-merge ke spec berversi (mis. `case-service.v1.yaml`) di gate G1. Katalog/generator hanya mencakup spec normatif — draft tidak dihitung sebagai kontrak yang boleh diimplementasikan.

## Minimum Contents (v1)
- [x] API inventory — 1 service (case-service v1), lihat tabel di atas
- [x] OpenAPI/Swagger specs — [`openapi/case-service.v1.yaml`](./openapi/case-service.v1.yaml)
- [x] Auth requirements per API — via `bearerAuth` (JWT; slice phase static token DEV/CI, ADR-007), 401/403 dibedakan
- [x] Error model standard — `Error{code, message, details?}` di semua response error
- [x] Versioning & deprecation policy — URL prefix `/v1`, breaking change bump prefix (ADR-006)
- [x] Pagination standard — dirujuk ke `../21 Technical Standards` (berlaku saat ada endpoint list)
- [x] SLAs for API availability/latency — baseline DEC-005: [`NFR Specification`](../04%20Solution%20Architecture/ECMP_NFR_Specification_v0.1.md) (availability 99.5%, p95 baca <300ms / tulis <800ms) dan [`SLA Matrix`](../11%20SLA%20and%20KPI%20Matrix/ECMP_SLA_Matrix_v0.1.md)

## Template Fields (per API)
- API Name
- Domain
- Endpoint
- Method
- Description
- AuthN/AuthZ
- Request/Response schema
- Owner
- Version
- Status
- Consumers

## Naming
File OpenAPI aktual: `<service>.v<major>.yaml` (contoh: `case-service.v1.yaml`) — versi major di nama file mengikuti prefix URL `/v<major>` per ADR-006; versi minor/patch dicatat di field `info.version` dalam spec.

## Boundary Note
- API Catalog = kontrak interface
- Integration Catalog = mapping ke sistem eksternal / pola integrasi

## Related
- `../08 Event Catalog`
- `../09 Integration Catalog`
- `../04 Solution Architecture`
