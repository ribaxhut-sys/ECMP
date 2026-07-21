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
Approved (baseline) — case-service v1 terkatalog; API planned mengikuti Traceability.

## API Inventory

### case-service v1 — [`openapi/case-service.v1.yaml`](./openapi/case-service.v1.yaml)
| API ID | Method & Endpoint | Description | Auth | Status |
|---|---|---|---|---|
| API-001 | POST /v1/cases | Create case (FR-001, emit EVT-001 CaseCreated) | bearerAuth, permission `cases:create` | 🟢 Implemented (Sprint-01) |
| API-002 | GET /v1/cases/{caseId} | Get case by id (FR-002) | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-01) |
| — | GET /health | Health check (di luar prefix /v1) | None | 🟢 Implemented |

### Planned
| API ID | Method & Endpoint | Description | Draft spec | Status |
|---|---|---|---|---|
| API-003 | POST /v1/cases/{caseId}/assign | Assign case (Sprint-02 / gate G1) | [`drafts/case-actions.v1.draft.yaml`](./openapi/drafts/case-actions.v1.draft.yaml) | Planned |
| API-004 | POST /v1/cases/{caseId}/status | Change case status (Sprint-02 / gate G1) | [`drafts/case-actions.v1.draft.yaml`](./openapi/drafts/case-actions.v1.draft.yaml) | Planned |
| API-005 | GET /v1/cases | List case terpaginasi (page/pageSize per `21 Technical Standards` §3; filter status/priority/caseType/assigneeId; Sprint-02) | [`drafts/dashboard-queues.v1.draft.yaml`](./openapi/drafts/dashboard-queues.v1.draft.yaml) | Planned |
| API-010 | GET /v1/customers/{customerId} | Customer reference read (CRM, Sprint-02) | [`drafts/customer-read.v1.draft.yaml`](./openapi/drafts/customer-read.v1.draft.yaml) | Planned |
| API-040 | GET /v1/dashboard/queues | Dashboard queues (Sprint-03) | [`drafts/dashboard-queues.v1.draft.yaml`](./openapi/drafts/dashboard-queues.v1.draft.yaml) | Planned |

> **Label gate:** G1 = gate masuk Sprint-02 (lihat `13 Test Strategy`); "Sprint-02 / gate G1" merujuk hal yang sama.

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
