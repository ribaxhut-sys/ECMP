# Domain — Dashboard

| Field | Value |
|---|---|
| ID | EAR-PORTAL-DOM-DASH |
| Version | 0.2 |
| Owner | Dashboard PO |
| Reviewer | Architect |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

The Dashboard domain delivers role-based operational and executive views with drill-down to cases.

- **Scope**: queue/workload/SLA views, filters, snapshots/export.
- **Constraint**: strictly read-only — no direct transaction mutation from the dashboard; views are role- and org-scoped (BR-006).
- **Data**: widget configs, aggregated metrics (must reconcile to source, BR-DASH-02), saved filters, report snapshots.
- **API (B2-14 Implemented)**: API-040 `GET /v1/dashboard/queues` — Sprint ECMF Case SoT; normative `dashboard-queues.v1.yaml` 1.0.0.

Canonical AI context: `ai/domain/dashboard.md`  
Detailed architecture: `20 Domain Architecture/Dashboard/`
