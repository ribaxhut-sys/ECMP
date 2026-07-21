# ECMP Business Blueprint v2.1 — Markdown Extract

| Field | Value |
|---|---|
| ID | BP-EXT-001 |
| Version | 1.0 |
| Owner | Business Analyst |
| Reviewer | Solution Architect / Domain POs |
| Approver | Business Owner |
| Status | 🟢 Approved (extract of approved baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

> Dokumen ini adalah **ekstrak markdown navigable** dari `ECMP_Business_Blueprint_v2.1.docx` (baseline resmi per **DEC-001**). Bila ada perbedaan, `.docx` yang menang; perbedaan wajib dilaporkan sebagai defect dokumentasi. Ekstrak ini dibuat agar Blueprint dapat dirujuk per-section oleh FRD (`03`), BR (`02`), dan traceability (`26`).

## 1. Executive Summary
ECMP (Enterprise Complaint Management Platform) adalah platform pengelolaan complaint & inquiry pelanggan end-to-end: registrasi, klasifikasi, assignment, penanganan berbasis workflow, SLA/KPI otomatis, dashboard operasional/eksekutif, dan notifikasi event-driven — dengan audit trail immutable sebagai fondasi. ECMP **bukan** system of record master pelanggan; Customer 360 dibangun dari master eksternal (read-only) diperkaya konteks interaksi/case ECMP.

Rantai kapabilitas bisnis: Customer Inquiry → Complaint Management → Case Resolution → Performance Monitoring → Executive Reporting → Continuous Improvement (lihat `ai/01_business.md`).

## 2. Scope Boundary

### 2.1 In Scope
- Customer 360 (dari master eksternal, read-only)
- Inquiry & Complaint lifecycle (ECMF): register, classify, assign, process, review/approve, close, reopen, root cause
- Workflow, assignment, escalation, approval (configuration-first)
- SLA/KPI otomatis dari event operasional
- Dashboard operasional & eksekutif (role/org scoped, read-only)
- Notifikasi event-driven (opt-in per konfigurasi)
- Administrasi konfigurasi (kategori, prioritas, SLA param, role, workflow) dengan approval & audit
- Audit trail immutable (Core Platform)

### 2.2 Out of Scope
- Menjadi Customer Master system of record (BR-CRM-01 / BR-003)
- Billing / core banking / product master ownership
- Membangun aplikasi channel eksternal (hanya integrasi boundary)
- AI assistant / predictive analytics (fase mendatang)
- **Branch Officer / Head Office escalation / Schedule Slot / Appointment / Work Order — dinyatakan di luar lingkup per DEC-001** sampai ada revisi Blueprint yang di-approve Architecture Board

## 3. Domain Landscape (7 Domain + Boundary)

| Domain | Tanggung Jawab | Referensi Detail |
|---|---|---|
| Core Platform | Fondasi bersama: AuthN/AuthZ, organisasi, konfigurasi, audit trail immutable, reference data | `20 Domain Architecture/Core Platform/` |
| CRM | Customer 360 dari master eksternal + riwayat interaksi & case terkait; search/verify customer | `20 Domain Architecture/CRM/` |
| ECMF | Complaint/inquiry lifecycle end-to-end dengan workflow, SLA, auditability | `20 Domain Architecture/ECMF/` |
| KPI & Performance | Definisi metrik, target, kalkulasi SLA, breach facts, kinerja unit/agent — dari event operasional | `20 Domain Architecture/KPI/` |
| Dashboard & Analytics | View operasional/eksekutif berbasis role dengan drill-down ke case; read-only | `20 Domain Architecture/Dashboard/` |
| Notification | Notifikasi event-driven: rule/template, resolusi penerima, delivery log, retry | `20 Domain Architecture/Notification/` |
| Administration | Pengelolaan konfigurasi/reference (configuration-first) dengan approval & versioning | `20 Domain Architecture/` |
| Channel (boundary) | Batas integrasi intake/outbound; aplikasi channel di luar core scope | `ai/domain/channel.md` |

## 4. Capability Map (ID stabil — selaras `26 Traceability/traceability.yaml` artifacts.bp)

| BP ID | Capability Statement | Domain Utama | FR Terkait |
|---|---|---|---|
| BP-001 | Complaint can be registered and tracked end-to-end | ECMF | FR-001, FR-001a/b/c, FR-002 |
| BP-002 | Assignment and status follow configured workflow | ECMF | FR-003, FR-004 |
| BP-003 | Customer 360 available during handling | CRM | FR-010 |
| BP-004 | Stakeholders notified on key case events | Notification | FR-020 |
| BP-005 | SLA achievement measurable automatically | KPI | FR-030 |
| BP-006 | Supervisors can monitor operational queues | Dashboard | FR-040 |

ID `BP-001..BP-006` bersifat **stabil** dan hanya boleh berubah lewat update traceability + Blueprint secara bersamaan.

## 5. Conceptual Workflow per Domain

### 5.1 ECMF (case lifecycle)
Request → Validate → Classify → Assign → Process → Review → Approve? → Close → KPI/Dashboard.
Status set baseline (lihat `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md`, DOM-ECMF-003): `REGISTERED → ASSIGNED → IN_PROGRESS → PENDING_REVIEW → CLOSED → (REOPENED)`. Transisi hanya sesuai workflow configuration (BR-001 / BR-ECMF-03).

### 5.2 CRM (customer 360)
Search → Verify → View 360 → Open/Link Case → Add Interaction Note. Master data read-only; perubahan master hanya via integrasi resmi (BR-CRM-01/04).

### 5.3 Core Platform
Authenticate → Authorize (role + org unit) → Serve request → Persist immutable audit untuk write signifikan (BR-CP-01..04, BR-008).

### 5.4 KPI & Performance
Consume domain events → Hitung SLA clock per kategori/prioritas → Deteksi breach → Emit `SLABreached` (EVT-004) → Feed dashboard/reporting (BR-005, BR-KPI-01..04).

### 5.5 Dashboard & Analytics
Login (role/org scope) → Pilih view queue/workload/SLA → Filter/drill-down ke case → Export/snapshot. Read-only, tidak memutasi transaksi (BR-DASH-01..04).

### 5.6 Notification
Event → Match rule/template (opt-in) → Resolve recipients (role/assignment/org) → Deliver → Log → Retry bila gagal (BR-NOTIF-01..04).

### 5.7 Administration
Request perubahan konfigurasi → Klasifikasi kritikal? → Approval (bila kritikal, BR-ADM-01) → Aktivasi versioned/effective-dated → Audit + emit `ConfigChanged` (EVT-006).

## 6. Integration Concept
- **Customer Master (eksternal)**: sumber `customerId`; ECMP read-only. Mode stub Sprint-01: terima customerId non-kosong, tandai `customerVerified=false` (FRD-001 §8).
- **Event bus internal**: ECMF/KPI/Administration memproduksi EVT-001..007 (SoT: `08 Event Catalog/events/events.yaml`); delivery at-least-once, konsumen idempotent (ADR-001).
- **Channel**: hanya boundary integrasi; tidak ada aplikasi channel dalam core scope.

## 7. Governance
- **Baseline & perubahan lingkup**: Blueprint v2.1 + FRD-001 adalah baseline resmi (DEC-001). Perubahan lingkup lewat revisi Blueprint yang di-approve Architecture Board; fitur out-of-scope dilarang dimodelkan.
- **Otorisasi build**: GO Sprint-01 = slice create/get + gate G0; Build-1 menunggu G0 exit (DEC-002).
- **Business rules**: skema delivery `BR-0xx` adalah SoT implementasi; katalog enterprise `BR-<Domain>-NN` referensi kebijakan (DEC-003). Baseline default nilai [TBD] ditetapkan di DEC-004.
- **Lifecycle artefak**: lihat `ECMP_RACI_Role_Matrix_Annex_v0.1.md` (BP-RACI-001) untuk RACI Blueprint/BR/FRD/ADR/Rilis.
- **Traceability**: setiap kapabilitas BP tertelusur BP→BR→FR→API/EVT/TC di `26 Traceability/traceability.yaml`.

## 8. Roadmap (indikatif, selaras traceability sprint)
| Fase | Isi | Kapabilitas |
|---|---|---|
| Sprint-01 (G0 + slice) | Create/get case, write-audit, platform floor | BP-001 (partial), BP-003 (Planned) |
| Sprint-02 (Build-1, pasca G0 exit) | Assign, status transition, notification | BP-002, BP-004 |
| Sprint-03 | SLA breach, dashboard queue | BP-005, BP-006 |

## Related
- `ECMP_Business_Blueprint_v2.1.docx` (baseline .docx)
- `ECMP_Capability_Register_v0.1.md` (BP-CAP-001)
- `ECMP_RACI_Role_Matrix_Annex_v0.1.md` (BP-RACI-001)
- `../02 Business Rules/ECMP_Business_Rules_v1.0.md`
- `../26 Traceability/traceability.yaml`
- `../27 Project Decisions/DEC-001_Business_Baseline_SoT_v1.0.md`
