# 05 Architecture Decision Records (ADR)


| Field | Value |
|---|---|
| ID | ADR-000 |
| Version | 0.1 |
| Owner | Solution Architect |
| Reviewer | Architecture Board |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Mencatat keputusan arsitektur penting beserta konteks, opsi, konsekuensi, dan status.

## Owner
- Document Owner: Solution Architect
- Reviewers: Tech Leads, Security Architect, Architecture Board

## Status
Draft

## Minimum Contents (v1)
- [x] ADR template (canonical in `../24 Templates/ADR_TEMPLATE.md`)
- [x] ADR index
- [x] Initial ADRs (event-driven integration, data ownership, configuration-first)
- [x] Additional ADRs (layering, API versioning, authentication, Role-Permission SoT, broker deferral)

## ADR Template
Gunakan template di `../24 Templates/ADR_TEMPLATE.md`.

Sections:
1. Title
2. Status (Proposed / Accepted / Superseded / Deprecated)
3. Context
4. Decision Drivers
5. Options Considered
6. Decision
7. Consequences
8. Compliance / Follow-up

## Naming
`ECMP_ADR_<NNN>_<Short_Title>_vX.Y.md`

Example: `ECMP_ADR_001_Use_Event_Driven_Case_Updates_v1.0.md`

## Related
- `../04 Solution Architecture`
- `../18 Architecture Governance`
- `../19 Reference Architecture`
- `../24 Templates`
- `../27 Project Decisions` (non-ADR decisions only)

## Index
| ADR | Title | Status |
|---|---|---|
| 001 | [Event-Driven Domain Integration](./ECMP_ADR_001_Event_Driven_Domain_Integration_v1.0.md) | Accepted |
| 002 | [ECMP Not System of Record for Customer Data](./ECMP_ADR_002_ECMP_Not_System_Of_Record_v1.0.md) | Accepted |
| 003 | [Configuration-First Principle](./ECMP_ADR_003_Configuration_First_Principle_v1.0.md) | Accepted |
| 004 | [Implementation Stack Sprint-01](./ECMP_ADR_004_Implementation_Stack_Sprint01_v1.0.md) | Accepted |
| 005 | [Backend Layering (minimal split)](./ECMP_ADR_005_Backend_Layering_v1.0.md) | Accepted |
| 006 | [API Versioning Strategy](./ECMP_ADR_006_API_Versioning_v1.0.md) | Accepted |
| 007 | [Authentication Model (slice + target)](./ECMP_ADR_007_Authentication_Model_v1.0.md) | Accepted |
| 008 | [Role-Permission Matrix SoT & Workflow Config Ownership](./ECMP_ADR_008_RBAC_SoT_Workflow_Ownership_v1.0.md) | Accepted |
| 009 | [Message Broker — Deferred (outbox first)](./ECMP_ADR_009_Message_Broker_Deferral_v1.0.md) | Accepted |
| 010 | [Deployment Platform Baseline (DEV/CI/SIT-UAT; PROD deferred)](./ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md) | Accepted |
| 011 | [Frontend — Deferred (API-first)](./ECMP_ADR_011_Frontend_Deferral_v1.0.md) | Accepted |
| 012 | [Target Authentication Architecture](./ECMP_ADR_012_Target_Authentication_Architecture_v1.0.md) | Proposed |
| 013 | [Frontend Technology Stack](./ECMP_ADR_013_Frontend_Technology_Stack_v1.0.md) | Approved |
| 014 | [ECMP Enterprise Business Module](./ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.0.md) | Proposed |
| 015 | [Enterprise Identity Contract](./ECMP_ADR_015_Enterprise_Identity_Contract_v1.0.md) | Proposed |
