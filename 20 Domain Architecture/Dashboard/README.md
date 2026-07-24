# Domain Architecture — Dashboard

| Field | Value |
|---|---|
| ID | DOM-DASH-001 |
| Version | 1.1 |
| Owner | Dashboard PO |
| Reviewer | Solution Architect |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline + TASK-050 projection foundation) |
| Last Review | 2026-07-24 |
| Next Review | 2027-01-21 |

## Objective
Visualisasi operasional dan eksekutif berbasis role dengan drill-down ke konteks case. **Read-only** — dashboard tidak boleh mengubah data transaksi (BR-DASH-03).

**TASK-050 (Dashboard Projection Foundation):** in-process `DashboardProjection`
updated only from Complaint events via `EventDispatcher`. No HTTP endpoint yet;
no DB persistence.

## Bounded Context
Konteks Read Model / Projection: konsumsi domain events → bangun aggregated view per persona. Tampilan mengikuti role + organisasi user login (BR-DASH-01 → delivery BR-006); otorisasi tetap via Core Platform (BR-DASH-04).

## In Scope
- Persona dashboards (queue/workload/SLA views)
- Filters dan snapshots/export
- Drill-down ke case context (navigasi, bukan mutasi)
- **TASK-050:** event-driven in-memory operational counters

## Out of Scope
- Mutasi data transaksi (BR-DASH-03); perhitungan KPI (milik KPI)
- TASK-050: HTTP projection API, DB/materialized view, cache tier

## Key Components
- Event Projector (idempotent consumer), Aggregated Metrics store, Widget Config per persona, Saved Filter, Report Snapshot.
- **TASK-050 runtime:** `DashboardProjectionHandler` → `DashboardProjectionStore` → immutable `DashboardProjection`.

## Key Flows
Event masuk → update projection → user buka dashboard → filter view by role+org (BR-006) → drill-down ke case. Angka harus reconcile dengan sumber; lag ditandai timestamp "as of" (BR-DASH-02).

**TASK-050:** ComplaintEvent → EventDispatcher → DashboardProjectionHandler → in-memory snapshot (`updated_at` = as-of).

## Data Ownership
Dashboard Widget Config, Aggregated Metrics (derived), Saved Filter, Report Snapshot = Dashboard. Data sumber tetap milik domain penghasil event.

## Integrations
- **Events consumed** (per events.yaml): EVT-001 CaseCreated, EVT-002 CaseAssigned, EVT-003 StatusChanged, EVT-004 SLABreached, EVT-005 CaseClosed, EVT-007 CaseReopened.
- **TASK-050 also consumes in-process:** EVT-009…EVT-015 (`ComplaintCreated` … `ComplaintEscalated`) via `EventDispatcher` (not broker).
- **Events produced:** tidak ada.
- Otorisasi view via Core Platform (BR-DASH-04 / BR-007).

## NFR Considerations
Reconciliation ke data sumber wajib (BR-DASH-02); retention Report Snapshot [TBD].
TASK-050 projection is process-local (lost on restart) — foundation only.

## Diagram Links
- Source: `../../23 Assets/mermaid/ecmp-context.mmd`
- Export: —

## Detailed Docs
- `PROJECTION_GUIDE.md` (ARCH-DASH-PROJECTION-001) — Dashboard Projection Guide (TASK-050)

## Open Questions
- Retention policy Report Snapshot [TBD] (lihat `../../06 Data Dictionary`).
