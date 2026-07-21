# Domain Architecture — KPI

| Field | Value |
|---|---|
| ID | DOM-KPI-001 |
| Version | 1.0 |
| Owner | Performance Owner |
| Reviewer | Operations Lead |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
Mengukur service performance dan SLA compliance dari event operasional — bukan input manual (BR-KPI-03).

## Bounded Context
Konteks Measurement: konsumsi domain events → hitung metric/SLA → hasilkan Performance Fact yang traceable ke transaksi sumber (BR-KPI-04). KPI tidak mengubah data transaksional.

## In Scope
- Metric definitions dan targets (wajib formula, owner, periode — BR-KPI-01; perubahan via governance konfigurasi — BR-KPI-02)
- SLA calculation dari status history/SLA clock
- Breach detection → emit EVT-004 SLABreached

## Out of Scope
- Visualisasi (milik Dashboard); definisi SLA parameter (milik Administration — SLA Config)

## Key Components
- Event Ingestor (idempotent consumer), SLA Calculator, Breach Detector, Performance Fact store, Metric Registry.

## Key Flows
Event masuk → update SLA clock/status fact → deteksi breach → emit EVT-004 → finalisasi lead time saat CaseClosed; restart clock saat CaseReopened.

## Data Ownership
Metric Definition, Target, Performance Fact, Breach Event = KPI. SLA Rule = sama dengan SLA Config milik Administration (KPI hanya reload nilai aktif via EVT-006).

## Integrations
- **Events consumed** (per events.yaml): EVT-001 CaseCreated (initialize SLA clock), EVT-003 StatusChanged (SLA clock / status history), EVT-005 CaseClosed (finalize performance fact), EVT-006 ConfigChanged (reload SLA rules), EVT-007 CaseReopened (restart SLA clock).
- **Events produced:** EVT-004 SLABreached (consumers: Notification, Dashboard).
- At-least-once (ADR-001); idempotency per aturan events.yaml.

## NFR Considerations
Angka KPI wajib traceable ke transaksi sumber (BR-KPI-04); re-breach setelah reopen diperbolehkan (idempotency EVT-004).

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Open Questions
- Daftar KPI yang boleh input manual (BR-KPI-03) — **ditutup** baseline DEC-004: tidak ada KPI manual di fase awal (daftar kosong).
- Kalender kerja untuk SLA (bersama BR-ECMF-05, `../../11 SLA and KPI Matrix`) — **ditutup** baseline DEC-004: 24x7 dulu; kalender kerja = konfigurasi fase berikut.
