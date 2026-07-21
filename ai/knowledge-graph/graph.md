# ECMP Knowledge Graph (View)

> **DEPRECATED** — snapshot manual; superseded oleh `graph.generated.md` / `graph.generated.yaml`
> (di-generate `tools/generate_knowledge_graph.py`; file manual ini bukan input generator).

| Field | Value |
|---|---|
| ID | AI-KG-002 |
| Version | 0.2 |
| Owner | Enterprise Architecture |
| Reviewer | BA / Architect |
| Approver | Architecture Board |
| Status | 🔴 Deprecated |
| Last Review | 2026-07-21 |
| Next Review | 2026-10-21 |

Source machine graph: `graph.yaml` (deprecated — lihat banner di atas)

CAP-0xx mengikuti `01 Business Blueprint/ECMP_Capability_Register_v0.1.md` (BP-CAP-001).

```mermaid
flowchart TD
  BG[Business Goal] --> CAP1[CAP-001 Case Registration & Retrieval]
  BG --> CAP2[CAP-002 Case Assignment]
  BG --> CAP3[CAP-003 Workflow Status Transition]
  BG --> CAP4[CAP-004 Customer 360 View]
  BG --> CAP6[CAP-006 SLA Measurement]

  CAP1 --> ECMF[Domain: ECMF]
  CAP2 --> ECMF
  CAP3 --> ECMF
  CAP4 --> CRM[Domain: CRM]
  CAP6 --> KPI[Domain: KPI]

  ECMF --> FR1[FR-001 Create Case]
  CRM --> FR1
  FR1 --> API1[API POST /v1/cases]
  FR1 --> API2[API GET /v1/cases/caseId]
  FR1 --> EVT1[EVT CaseCreated]
  API1 --> EVT1
  EVT1 --> NOTIF[Domain: Notification]
  KPI --> EVT4[EVT SLABreached]
  FR1 --> TC1[TC-001]
  API1 --> TC1
```

## Impact Analysis Example
Changing `POST /v1/cases` impacts: FR-001, EVT-001, Notification consumers, TC-001, and potentially CRM linkage assumptions.
