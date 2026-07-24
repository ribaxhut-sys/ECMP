# Domain Architecture — KPI

| Field | Value |
|---|---|
| ID | DOM-KPI-001 |
| Version | 1.1 |
| Owner | Performance Owner |
| Reviewer | Operations Lead |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline + TASK-051 projection foundation) |
| Last Review | 2026-07-24 |
| Next Review | 2027-01-21 |

## Objective
Mengukur service performance dan SLA compliance dari event operasional — bukan input manual (BR-KPI-03).

## Bounded Context
Konteks Measurement: konsumsi domain events → hitung metric/SLA → hasilkan Performance Fact yang traceable ke transaksi sumber (BR-KPI-04). KPI tidak mengubah data transaksional.

**TASK-051 (KPI Projection Foundation):** in-process `KpiProjection`
read model updated only from Complaint events via `EventDispatcher`.
No aggregate reads, no `ComplaintService` calls, no HTTP projection API,
no persistence.

## In Scope
- Metric definitions dan targets (wajib formula, owner, periode — BR-KPI-01; perubahan via governance konfigurasi — BR-KPI-02)
- SLA calculation dari status history/SLA clock
- Breach detection → emit EVT-004 SLABreached
- TASK-051: in-memory KPI projection from ComplaintCreated…Escalated

## Out of Scope
- Visualisasi (milik Dashboard); definisi SLA parameter (milik Administration — SLA Config)
- TASK-051: HTTP projection API, DB/materialized view, cache tier

## Key Components
- Event Ingestor (idempotent consumer), SLA Calculator, Breach Detector, Performance Fact store, Metric Registry.
- **TASK-051 runtime:** `KpiProjectionHandler` → `KpiProjectionStore` → immutable `KpiProjection`.

## Key Flows
Event masuk → update SLA clock/status fact → deteksi breach → emit EVT-004 → finalisasi lead time saat CaseClosed; restart clock saat CaseReopened.

**TASK-051:** ComplaintEvent → EventDispatcher → KpiProjectionHandler → in-memory snapshot (`updated_at` = as-of).

## Data Ownership
Metric Definition, Target, Performance Fact, Breach Event = KPI. SLA Rule = sama dengan SLA Config milik Administration (KPI hanya reload nilai aktif via EVT-006).

## Integrations
- **Events consumed** (per events.yaml): EVT-001 CaseCreated (initialize SLA clock), EVT-003 StatusChanged (SLA clock / status history), EVT-005 CaseClosed (finalize performance fact), EVT-006 ConfigChanged (reload SLA rules), EVT-007 CaseReopened (restart SLA clock).
- **Events produced:** EVT-004 SLABreached (consumers: Notification, Dashboard).
- At-least-once (ADR-001); idempotency per aturan events.yaml.
- **TASK-051 runtime consumers:** ComplaintCreated, ComplaintAssigned, ComplaintAccepted, ComplaintInProgress, ComplaintResolved, ComplaintClosed, ComplaintEscalated → `KpiProjection`.

## NFR Considerations
Angka KPI wajib traceable ke transaksi sumber (BR-KPI-04); re-breach setelah reopen diperbolehkan (idempotency EVT-004).

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —
- Projection Guide: `PROJECTION_GUIDE.md` (TASK-051)

## Open Questions
- Daftar KPI yang boleh input manual (BR-KPI-03) — **ditutup** baseline DEC-004: tidak ada KPI manual di fase awal (daftar kosong).
- Kalender kerja untuk SLA (bersama BR-ECMF-05, `../../11 SLA and KPI Matrix`) — **ditutup** baseline DEC-004: 24x7 dulu; kalender kerja = konfigurasi fase berikut.

## Notes
TASK-051 projection is process-local (lost on restart) — foundation only.
Existing `KpiService` summary API (TASK-026) remains unchanged and is a
separate query path over operational tables.
