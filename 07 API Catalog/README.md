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

> **2026-07-22 (Sprint-03A, DEC-006 D6/U-6):** `case-actions.v1.yaml` dikonsolidasikan ke `case-service.v1.yaml` — kini satu-satunya spec normatif untuk case-service. `case-actions.v1.yaml` masih ada di disk tetapi ditandai `x-status: superseded` (paths kosong) dan tidak lagi dibaca oleh tooling/test; dipertahankan hanya agar tautan lama tidak 404. Tidak ada perubahan perilaku API atau payload event — murni sinkronisasi katalog terhadap runtime yang sudah berjalan sejak Sprint-02B.
>
> **2026-07-22 (Sprint-03B):** API-005 (list cases) di-freeze dan diimplementasikan; merged ke `case-service.v1.yaml` v1.5.0 dari draft `dashboard-queues.v1.draft.yaml`. Sort dikunci `createdAt` descending (keputusan CTO, design review Sprint-03B) — sort dapat dikonfigurasi eksplisit di luar scope versi ini. API-010 (Customer 360 read) **ditunda** — lihat `implementation/backend/ACR_SPRINT02B.md` ACR-002: draft/FRD-003 mengasumsikan profil pelanggan nyata, bertentangan dengan larangan fabrikasi data di INT-001 untuk mode stub.

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
