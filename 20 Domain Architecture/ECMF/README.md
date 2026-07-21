# Domain Architecture — ECMF

| Field | Value |
|---|---|
| ID | DOM-ECMF-001 |
| Version | 1.0 |
| Owner | ECMF PO / Solution Architect |
| Reviewer | BA Lead / Tech Leads |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
End-to-end complaint/inquiry management: registrasi, klasifikasi, assignment, processing, review/approval, closure, reopen — dengan SLA clock dan auditability penuh (BR-008).

## Bounded Context
- **Konteks:** Case Management. ECMF adalah domain transaksional inti ECMP; entitas pusatnya adalah **Case** sebagai Aggregate Root (lihat `CASE_AGGREGATE.md`, DOM-ECMF-002).
- **ECMF = enforcer, bukan pemilik workflow config (ADR-008):** definisi status & transisi adalah konfigurasi bisnis milik Administration; ECMF memuat config aktif (via EVT-006) dan menolak transisi invalid. ECMF tidak mendefinisikan transisi sendiri (lihat `CASE_STATE_MACHINE.md`, DOM-ECMF-003).
- **Baseline scope (DEC-001):** Blueprint v2.1 + FRD-001. Konsep Branch/HO/Schedule/WorkOrder **dilarang dimodelkan** di domain ini.
- **Ubiquitous language:** Case, Case Type (COMPLAINT/INQUIRY), Priority, Status, Assignment, Resolution, Root Cause, SLA Clock, Reopen.

## In Scope
- Registration (Sprint-01 — implemented), classification, assignment
- Processing, review/approval
- Closure (resolusi wajib per BR-ECMF-06), reopen (BR-ECMF-07), root cause
- SLA clocks dan escalation triggers (perhitungan otomatis dari konfigurasi kategori+prioritas, BR-ECMF-05 → delivery BR-005)
- Audit trail lengkap tiap transaksi case (BR-ECMF-01 → delivery BR-008)

## Out of Scope
- Definisi workflow config & SLA config — milik Administration (ADR-008)
- Data master pelanggan — read-only reference dari CRM/Customer Master (ADR-002)
- Perhitungan KPI/agregasi — milik KPI dan Dashboard
- Branch/HO/Schedule/WorkOrder modeling (DEC-001)

## Key Components
| Komponen | Layer (ADR-005) | Tanggung jawab |
|---|---|---|
| Case API | Presentation | Endpoint business action (API-001..API-004); AuthN/AuthZ via Core Platform |
| Case Application Service | Application | Orkestrasi business action, transaksi, audit write (BR-008), outbox write |
| Case Aggregate | Domain | Invariants Case (DOM-ECMF-002): transisi valid, customerId immutable, audit wajib |
| Case State Machine (enforcer) | Domain | Validasi transisi terhadap Workflow Config aktif (DOM-ECMF-003, BR-001) |
| SLA Clock | Domain | Timer per case/tahapan dari SLA Config (BR-005); breach detection di KPI |
| Case Repository + Outbox | Infrastructure | Persistence + transactional outbox (ADR-009) |

## Key Flows
1. **RegisterCase (Sprint-01, implemented):** POST `/v1/cases` → validasi payload + customerId (stub mode: `customerVerified=false`) → status awal `REGISTERED` (FR-001a) → persist Case + audit record `case.create` + outbox EVT-001 dalam **satu transaksi** (FR-001c, ADR-009) → 201.
2. **GetCase (Sprint-01, implemented):** GET `/v1/cases/{caseId}` → AuthZ `cases:read` → 200/404 (FR-002).
3. **Full lifecycle (desain G1, planned):** Request → Validate → Classify → Assign → Process → Review → Approve? → Close → (Reopen?) → KPI/Dashboard. Enforcement transisi = gate G1; Sprint-01 hanya status `REGISTERED`.
4. **Config reload:** konsumsi EVT-006 ConfigChanged → reload workflow/SLA config aktif.

## Data Ownership
| Entity | Ownership | Catatan |
|---|---|---|
| Case Header | ECMF (SoT) | Aggregate Root — lihat DOM-ECMF-002 |
| Case Activity, Comment, Attachment | ECMF | Bagian aggregate Case (future — belum di Sprint-01) |
| Status History | ECMF | Basis SLA Clock; append-only |
| SLA Clock | ECMF (nilai berjalan) | Aturan/parameter dari SLA Config milik Administration |
| Root Cause, Resolution | ECMF | Resolusi wajib saat closure (BR-ECMF-06) |
| Workflow Config | **Administration** (ADR-008) | ECMF hanya enforcer |
| Customer Reference | **Customer Master** via CRM | Read-only (ADR-002) |

## Integrations
- **Events produced** (SoT: `../../08 Event Catalog/events/events.yaml`):
  - EVT-001 CaseCreated (implemented, Sprint-01)
  - EVT-002 CaseAssigned (planned)
  - EVT-003 StatusChanged (planned)
  - EVT-005 CaseClosed (planned)
  - EVT-007 CaseReopened (Proposed di katalog; planned)
- **Events consumed:** EVT-006 ConfigChanged (reload workflow/SLA config aktif).
- **APIs:** API-001 POST /v1/cases, API-002 GET /v1/cases/{caseId} (implemented); API-003 POST /v1/cases/{caseId}/assign, API-004 POST /v1/cases/{caseId}/status (planned, Sprint-02 / gate G1).
- Semua emit via transactional outbox (ADR-009); at-least-once, consumer idempotent (ADR-001).

## NFR Considerations
- Setiap significant write wajib audit record immutable dalam transaksi yang sama (BR-008 / FR-001c).
- Idempotency-Key out of scope Sprint-01 (DEC-002).
- Timestamps ISO-8601 UTC; `caseId` format `CASE-<10-hex>` (FRD-001 §7).
- Layering minimal per ADR-005; dilarang framework publisher generik sebelum broker nyata (ADR-009).

## Diagram Links
- Source: `../../23 Assets/mermaid/case-state-machine.mmd`, `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Detailed Docs
- `CASE_AGGREGATE.md` (DOM-ECMF-002) — Case sebagai Aggregate Root + Business Actions catalog
- `CASE_STATE_MACHINE.md` (DOM-ECMF-003) — enum status baseline + matriks transisi + guards

## Open Questions
Seluruh [TBD] rule ECMF telah ditutup dengan baseline per `27 Project Decisions/DEC-004_BR_Baseline_Defaults_v1.0.md` (dapat direvisi BO via DEC baru):
- Aturan akses lintas unit (BR-ECMF-02) — **ditutup**: aksi tulis hanya oleh supervisor unit induk; unit lain read-only.
- Kategori wajib evidence saat closure (BR-ECMF-06) — **ditutup**: wajib untuk COMPLAINT, opsional untuk INQUIRY.
- Jangka waktu maksimum reopen sejak closure (BR-ECMF-07) — **ditutup**: 30 hari kalender.
- Kalender kerja SLA clock (BR-ECMF-05) — **ditutup**: baseline 24x7 (lihat `../../11 SLA and KPI Matrix`).
