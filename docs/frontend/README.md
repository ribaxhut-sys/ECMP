# ECMP Frontend Architecture Docs

| Field | Value |
|---|---|
| ID | FE-DOCS-HUB |
| Program | PROGRAM-FRONTEND-001 |
| Owner | Frontend Lead / Solution Architect |
| Status | 🟢 Active |
| Last Review | 2026-07-30 |
| Current architecture | FE-ARCH-001 **v1.2** — Lifecycle **BASELINE** (PROGRAM-ADR-002 BR-003) |
| Current standards | FE-STD-001 **v1.0** — Lifecycle **BASELINE** (PROGRAM-ADR-002 BR-004) |
| Implementation Authorization | AUTHORIZED WITH CONDITIONS (PROGRAM-ADR-002 BR-008) |

## Purpose

Hub for **frontend architecture and development standards** documentation. Application code lives under `frontend/` (canonical) and must not be invented from this folder.

## Documents

| Document | ID | Description |
|---|---|---|
| `UI_BASELINE.md` (repository root) | ECMP-UI-BASELINE-001 | **Official UI Freeze** — product UI LOCKED; change policy |
| [FRONTEND_ARCHITECTURE_v1.2.md](./FRONTEND_ARCHITECTURE_v1.2.md) | FE-ARCH-001 | **Current** frontend architecture — Lifecycle **BASELINE** |
| [FRONTEND_DEVELOPMENT_STANDARDS_v1.0.md](./FRONTEND_DEVELOPMENT_STANDARDS_v1.0.md) | FE-STD-001 | **Current** frontend development standards — Lifecycle **BASELINE** |
| [FRONTEND_ARCHITECTURE_v1.1.md](./FRONTEND_ARCHITECTURE_v1.1.md) | FE-ARCH-001 | ARCHIVED (prior PHASE-0A revision) |
| [FRONTEND_ARCHITECTURE_v1.0.md](./FRONTEND_ARCHITECTURE_v1.0.md) | FE-ARCH-001 | ARCHIVED (prior PHASE-0 initial) |
| [FRONTEND_CI_QUALITY_POLICY_v1.0.md](./FRONTEND_CI_QUALITY_POLICY_v1.0.md) | FE-CI-POL-001 | **Accepted with Conditions** — Root Frontend CI / a11y working target / coverage |
| [FRONTEND_CI_QUALITY_POLICY_COUNTERSIGN_v1.0.md](./FRONTEND_CI_QUALITY_POLICY_COUNTERSIGN_v1.0.md) | FE-CI-POL-CS-001 | Countersign record (2026-07-30) |
| [FRONTEND_CI_QUALITY_POLICY_v0.1.md](./FRONTEND_CI_QUALITY_POLICY_v0.1.md) | FE-CI-POL-001 | Historical Proposed draft (superseded) |
| [OPEN_DECISIONS.md](./OPEN_DECISIONS.md) | FE-OD-001 | Remaining open decisions |

## Canonical vs legacy

| Tree | Classification |
|---|---|
| `frontend/` | Production product UI / Enterprise Business Module (DEC-019) |
| `implementation/frontend/` | Legacy Vite sprint UI (ADR-013) |

## Principles (summary)

| Class | Items |
|---|---|
| Locked (ADR-014/015 Accepted with Conditions; Mode B runtime CLOSED) | ECMP is Enterprise Business Module; AuthN owned by Enterprise Platform; ECMP owns business capabilities |
| Locked | Topology independence; Role-Permission SoT = Core Platform (ADR-008); deployment-supplied config; API ownership flow |

## Glossary (short)

| Term | Meaning |
|---|---|
| Enterprise Platform | Shared enterprise host (AuthN, identity directory, org, session, enterprise nav) |
| Core Platform | ECMP domain; Role-Permission SoT (ADR-008) |
| Business Module | ECMP Complaint Management (and future modules) |

## Related EKR locations

- ADR index (canonical generated): `05 Architecture Decision Records/ADR_INDEX.generated.md`
- ADR index (folder README): `05 Architecture Decision Records/README.md`
- ADR index (portal mirror): `docs/architecture/adr-index.md`
- UX specs: `12 UI UX Spec/`
- API contracts: `07 API Catalog/openapi/`
- Security: `10 Security and Access Standards/`
- Core Platform domain: `20 Domain Architecture/Core Platform/`
- Deployment / infra (future topology SoT): outside FE-ARCH; see OD-FE-007
- Repository navigation: `00 Repository Guide/REPOSITORY_INDEX.md`
