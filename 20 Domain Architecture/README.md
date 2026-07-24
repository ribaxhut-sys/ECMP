# 20 Domain Architecture

| Field | Value |
|---|---|
| ID | DOM-000 |
| Version | 1.0 |
| Owner | Domain Architect / SA |
| Reviewer | Tech Leads |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Menyimpan arsitektur detail per domain bisnis ECMP (diagram, bounded context, komponen, sequence). Baseline mengikuti DEC-001 (Blueprint v2.1 + FRD-001); konsep Branch/HO/Schedule/WorkOrder tidak dimodelkan.

## Owner
- Document Owner: Solution Architect
- Domain contributors: masing-masing Domain Product Owner / Tech Lead

## Status
Approved (baseline) — 2026-07-21

## Domain Index
| DOM-ID | Domain | Doc | Scope note |
|---|---|---|---|
| DOM-CP-001 | Core Platform | `Core Platform/README.md` | Auth, org, config, audit append-only; SoT Role-Permission (ADR-008) |
| DOM-CRM-001 | CRM | `CRM/README.md` | Customer 360; cache read-only Customer Master (ADR-002) |
| DOM-ECMF-001 | ECMF | `ECMF/README.md` | Complaint/inquiry lifecycle; enforcer workflow config |
| DOM-ECMF-002 | ECMF — Case Aggregate | `ECMF/CASE_AGGREGATE.md` | Case sebagai Aggregate Root + Business Actions catalog |
| DOM-ECMF-003 | ECMF — Case State Machine | `ECMF/CASE_STATE_MACHINE.md` | Baseline status enum + matriks transisi + guards |
| DOM-ADM-001 | Administration | `Administration/README.md` | Workflow/SLA Config SoT (ADR-008); approval BR-ADM-01; EVT-006 |
| DOM-KPI-001 | KPI | `KPI/README.md` | Metrics & SLA measurement dari event; EVT-004 |
| DOM-DASH-001 | Dashboard | `Dashboard/README.md` | Read-only operational/executive views |
| DOM-NOTIF-001 | Notification | `Notification/README.md` | Event-driven notifications + delivery log |
| DOM-WF-001 | Workflow | `Workflow/README.md` | Orchestration planning from Complaint events (TASK-052; no execution) |
| DOM-EXEC-001 | Execution | `Execution/README.md` | Shared ExecutionPlan infrastructure (TASK-053; PLANNED only) |
| DOM-DELIVERY-001 | Delivery | `Delivery/README.md` | Shared DeliveryEngine foundation (TASK-057; prepare only) |
| DOM-QUEUE-001 | Queue | `Queue/README.md` | Queue domain + application foundation (TASK-061…062; no infra) |
| DOM-CH-001 | Channel | `Channel/README.md` | Boundary-only; out of scope core build (OQ-001) |

## Minimum Contents (per domain)
- [x] Context notes (bounded context per domain README)
- [x] Component diagram (source: `../23 Assets/mermaid/ecmp-context.mmd`)
- [x] Key flows / sequence (section Key Flows per domain; state machine di DOM-ECMF-003)
- [x] Data ownership notes (section Data Ownership per domain)
- [x] Integration touchpoints (events produced/consumed per `../08 Event Catalog/events/events.yaml`)
- [x] Open questions (section Open Questions per domain)

## Related
- `../01 Business Blueprint`
- `../04 Solution Architecture`
- `../05 Architecture Decision Records` (khususnya ADR-002, ADR-005, ADR-008, ADR-009)
- `../08 Event Catalog`
- `../19 Reference Architecture`
- `../23 Assets`
