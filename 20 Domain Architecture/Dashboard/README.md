# Domain Architecture — Dashboard

| Field | Value |
|---|---|
| ID | DOM-DASH-001 |
| Version | 1.0 |
| Owner | Dashboard PO |
| Reviewer | Solution Architect |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
Visualisasi operasional dan eksekutif berbasis role dengan drill-down ke konteks case. **Read-only** — dashboard tidak boleh mengubah data transaksi (BR-DASH-03).

## Bounded Context
Konteks Read Model / Projection: konsumsi domain events → bangun aggregated view per persona. Tampilan mengikuti role + organisasi user login (BR-DASH-01 → delivery BR-006); otorisasi tetap via Core Platform (BR-DASH-04).

## In Scope
- Persona dashboards (queue/workload/SLA views)
- Filters dan snapshots/export
- Drill-down ke case context (navigasi, bukan mutasi)

## Out of Scope
- Mutasi data transaksi (BR-DASH-03); perhitungan KPI (milik KPI)

## Key Components
- Event Projector (idempotent consumer), Aggregated Metrics store, Widget Config per persona, Saved Filter, Report Snapshot.

## Key Flows
Event masuk → update projection → user buka dashboard → filter view by role+org (BR-006) → drill-down ke case. Angka harus reconcile dengan sumber; lag ditandai timestamp "as of" (BR-DASH-02).

## Data Ownership
Dashboard Widget Config, Aggregated Metrics (derived), Saved Filter, Report Snapshot = Dashboard. Data sumber tetap milik domain penghasil event.

## Integrations
- **Events consumed** (per events.yaml): EVT-001 CaseCreated, EVT-002 CaseAssigned, EVT-003 StatusChanged, EVT-004 SLABreached, EVT-005 CaseClosed, EVT-007 CaseReopened.
- **Events produced:** tidak ada.
- Otorisasi view via Core Platform (BR-DASH-04 / BR-007).

## NFR Considerations
Reconciliation ke data sumber wajib (BR-DASH-02); retention Report Snapshot [TBD].

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Open Questions
- Retention policy Report Snapshot [TBD] (lihat `../../06 Data Dictionary`).
