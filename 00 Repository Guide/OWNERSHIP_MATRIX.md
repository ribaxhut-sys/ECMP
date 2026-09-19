# Ownership Matrix

| Field | Value |
|---|---|
| ID | EAR-STD-004 |
| Version | 1.0a |
| Owner | Enterprise Architecture / PMO |
| Reviewer | Architecture Board |
| Approver | CIO / Program Sponsor |
| Status | 🟢 Approved |
| Last Review | 2026-07-31 |
| Next Review | 2027-01-21 |

## Folder Ownership

| Folder | Owner Role | Backup | Primary Reviewer |
|---|---|---|---|
| 00 Repository Guide | Enterprise Architecture | PMO | Solution Architect |
| 01 Business Blueprint | Business Analyst | Business Owner | Architecture / Ops |
| 02 Business Rules | Business Analyst | Domain PO | Compliance / Ops |
| 03 Functional Requirements | Business Analyst | Domain PO | QA / Architect |
| 04 Solution Architecture | Solution Architect | Chief Architect | Security / Tech Leads |
| 05 Architecture Decision Records | Solution Architect | Chief Architect | Architecture Board |
| 06 Data Dictionary | Data Architect | BA Lead | Security / Compliance |
| 07 API Catalog | Backend Lead | API Owner | Solution Architect |
| 08 Event Catalog | Integration Lead | Solution Architect | Domain Tech Leads |
| 09 Integration Catalog | Integration Lead | Solution Architect | External System Owners |
| 10 Security and Access Standards | Security Architect | InfoSec | Compliance |
| 11 SLA and KPI Matrix | Operations Lead | Performance Owner | Business Owner |
| 12 UI UX Spec | UX Lead | Product Designer | BA / Frontend Lead |
| 13 Test Strategy | QA Lead | Test Architect | BA / Tech Leads |
| 14 Deployment Standards | DevOps Lead | Platform Lead | Security / SRE |
| 15 Operations Runbook | SRE / Operations | Support Lead | DevOps |
| 16 Release Management | Release Manager | PMO | QA / Ops |
| 17 Compliance | Compliance Officer | Risk | Security / Legal |
| 18 Architecture Governance | Architecture Board Chair | Chief Architect | PMO |
| 19 Reference Architecture | Chief Architect | Solution Architect | Tech Leads |
| 20 Domain Architecture | Domain Architect / SA | Domain PO | Tech Leads |
| 21 Technical Standards | Tech Lead | Platform Lead | Solution Architect |
| 22 Engineering Handbook | Engineering Manager | Tech Lead | All squads |
| 23 Assets | Solution Architect | UX Lead | PMO |
| 24 Templates | PMO | Enterprise Architecture | Architecture Board |
| 25 Glossary | Business Analyst | Domain PO | Architecture |
| 26 Traceability | BA Lead / QA Lead | PMO | Compliance |
| 27 Project Decisions | PMO | Product Owner | Stakeholders |
| docs/frontend (hub) | Frontend Lead / Solution Architect | UX Lead | Architecture Board |
| docs/architecture (portal mirrors) | Enterprise Architecture | PMO | Solution Architect |

## Accountability Rule
Owner bertanggung jawab atas akurasi, review schedule, dan status dokumen di foldernya.

## Code / namespace ownership (DEC-026 after M-026-2)

Complement to folder ownership. Foundation HTTP lifecycle **unmounted** (DEC-026 Accepted with Conditions). Tables `complaints*` **DROP** (M-026-3 / Alembic `0072`) — not merged to CM (H1). CA BC unchanged.

| Namespace / stack | Code owner path | Consumers MUST treat as | Mount posture (production) |
|---|---|---|---|
| `/api/v1/cm` · CM Batch 1 Aggregate + Case | `backend/app/modules/cm_batch1/` · `cm_case/` | Canonical Single SoT (DEC-025 / DEC-026) | Mounted (`cm_batch1_router`, `cm_case_router`) |
| `/api/v1/complaints` · Legacy ECMF lifecycle | `backend/app/modules/complaints/` (+ related) | **Retired HTTP** — do not call; tables **DROP** (Alembic `0072`) | **Unmounted** (DEC-026 M-026-2) |
| Visit-linked CA BC (`complaint_cases*`) | `backend/app/modules/complaint/` | Ticket-nested only; **not** Aggregate; **not** Foundation retire set | Ticket-nested via `complaint_api_router`; full `complaint_foundation_router` **unmounted** |

Mode B / enterprise customer remain **CLOSED** (PROGRAM-BOARD-006 **C-B6-1** / PROGRAM-BOARD-004 **C-7**).

| Rev | Date | Notes |
|---|---|---|
| 1.0a | 2026-07-31 | DEC-020 dual-SoT code/namespace ownership rows (Mode A hygiene; no Mode B unlock) |
| 1.0b | 2026-08-13 | DEC-026 M-026-2: `/api/v1/complaints` unmounted; CM = canonical; CA BC unchanged |
| 1.0c | 2026-08-13 | M-026-3: `complaints*` DROP (Alembic `0072`); unused-leave wording retired |
