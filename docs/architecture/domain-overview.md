# Domain Architecture Overview

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

Domain architecture (DOM-000, 🟢 Approved baseline) documents bounded contexts, key flows, data ownership and integration touchpoints per ECMP domain:

- **Core Platform** (DOM-CP-001) — auth, org, config, append-only audit; RBAC SoT (ADR-008).
- **CRM** (DOM-CRM-001) — customer 360; read-only cache of the external Customer Master (ADR-002).
- **ECMF** (DOM-ECMF-001..003) — complaint/inquiry lifecycle, Case aggregate, and the baseline case state machine.
- **Administration** (DOM-ADM-001) — workflow/SLA config SoT; emits EVT-006.
- **KPI** (DOM-KPI-001) — metrics & SLA measurement from events; emits EVT-004.
- **Dashboard** (DOM-DASH-001) — read-only operational/executive views.
- **Notification** (DOM-NOTIF-001) — event-driven notifications with delivery log.
- **Channel** (DOM-CH-001) — boundary-only, out of core build scope (OQ-001).

**Canonical source:** `20 Domain Architecture/README.md`.
