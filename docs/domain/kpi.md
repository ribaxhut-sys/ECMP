# Domain — KPI

| Field | Value |
|---|---|
| ID | EAR-PORTAL-DOM-KPI |
| Version | 0.2 |
| Owner | Performance Owner |
| Reviewer | Operations |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

The KPI & Performance domain measures service performance and SLA compliance from operational events.

- **Scope**: metric definitions, targets, SLA calculation, breach facts, unit/agent performance.
- **Event produced**: SLABreached (EVT-004) when an SLA threshold is crossed; consumes case lifecycle events (EVT-001/003/005/007) to run SLA clocks.
- **Data**: Metric Definition, Target, SLA Rule (SoT: Administration, ADR-008 — KPI only reads active values via EVT-006), Performance Fact, Breach Event.
- **Rule**: every calculated KPI must be traceable to source transactions (BR-KPI-04).

Canonical AI context: `ai/domain/kpi.md`  
Detailed architecture: `20 Domain Architecture/KPI/` · `11 SLA and KPI Matrix/`
