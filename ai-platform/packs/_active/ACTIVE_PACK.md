# Active Domain Pack — ecmf

| Field | Value |
|---|---|
| ID | AIP-PACK-ACTIVE |
| Version | 0.1 |
| Owner | Automation |
| Reviewer | PMO / Enterprise Architecture |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | auto |
| Next Review | auto |

> Selected pack: `ai-platform/packs/ecmf/pack.md`

# Domain Knowledge Pack — ECMF

| Field | Value |
|---|---|
| ID | PACK-ECMF |
| Version | 1.0 |
| Owner | ECMF PO / Solution Architect |
| Reviewer | BA / Tech Lead |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Memory | v1 |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Load this pack instead of whole repository

### Core context
- `ai-platform/policies/ai-rules.md`
- `ai-platform/memory/v1/memory_ecmf.md` (or generate via memory builder)
- `ai/domain/ecmf.md`
- `ai/sprint/Sprint-01.md`

### Business / Requirements
- `01 Business Blueprint/` (ECMF sections)
- `02 Business Rules/ECMP_Business_Rules_Sprint01_v0.1.md`
- `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md`

### Architecture / Decisions
- `20 Domain Architecture/ECMF/`
- `20 Domain Architecture/navigator/ecmf.md`
- ADR-001, ADR-002, ADR-004

### Contracts
- `07 API Catalog/openapi/case-service.v1.yaml` (API-001/002)
- `08 Event Catalog/events/events.yaml` (EVT-001+)

### Traceability
- Links with domain=ECMF in `26 Traceability/traceability.yaml`

### Default prompts
- Implement: `implement-feature@v1`
- Review: `code-review@v1`
- Requirements: `frd-generator@v1`

