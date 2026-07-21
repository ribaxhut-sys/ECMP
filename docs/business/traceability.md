# Traceability

| Field | Value |
|---|---|
| ID | EAR-PORTAL-MIRROR |
| Version | 0.2 |
| Owner | Enterprise Architecture |
| Reviewer | PMO |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

The traceability matrix (TRC-001) links every delivery chain end-to-end: Domain → Blueprint goal (BP) → Business Rule (BR) → Functional Requirement (FR) → API → Event → Test Case → Sprint.

- Nine links (TRC-L-001..009) currently cover ECMF, Core Platform, CRM, Notification, KPI and Dashboard.
- Approved Sprint-01 links: case create/get (FR-001/FR-002, API-001/API-002, EVT-001, TC-001/TC-002/TC-005).
- Planned Sprint-02/03 links: assignment, status transition, customer 360, notifications, SLA breach, dashboard queues.
- The markdown table is synced from `traceability.yaml` by `tools/sync_traceability_md.py` — edit the YAML, not the table.
- An artifact dictionary spells out every BP/BR/FR/API/EVT/TC ID used.

**Canonical source:** `26 Traceability/TRACEABILITY_MATRIX.md`.
