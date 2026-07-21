# Sprint-01 — Foundation & ECMF Case Core

| Field | Value |
|---|---|
| ID | AI-SPRINT-01 |
| Version | 1.0 |
| Owner | PMO / ECMF PO |
| Reviewer | Solution Architect / Tech Lead |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2026-08-21 |

## Goal
Establish implementation foundation and first vertical slice: create/view case linked to customer reference.

## Status
**APPROVED — GO for Sprint-01 slice + G0 platform floor** (per `27 Project Decisions/DEC-002`).
Build-1 features beyond the create/get slice (assign, status, SLA, notification) require G0 exit criteria sign-off first.

## In Scope
- Project bootstrap under `implementation/backend` (FastAPI per ADR-004)
- Case create + get (API-001, API-002)
- CaseCreated event emission contract (EVT-001)
- Basic authz placeholder (`cases:create`, `cases:read`)
- OpenAPI + Event catalog kept in sync
- Unit/API tests for create/get case
- Traceability rows kept current

## Out of Scope
- Full SLA engine
- Complex approval matrix
- Channel apps
- Customer master write-back
- List/search UI
- Frontend application

## Context to Load
- `ai-platform/policies/ai-rules.md`
- `ai/generated/memory_global.md`
- `ai/generated/memory_ecmf.md`
- `ai/domain/ecmf.md`
- `ai/domain/crm.md`
- `ai/04_api.md`
- `ai/06_events.md`
- `ai/08_standards.md`
- `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md`
- `05 Architecture Decision Records/ECMP_ADR_004_Implementation_Stack_Sprint01_v1.0.md`

## Deliverables
| ID | Deliverable | Acceptance |
|---|---|---|
| S01-D1 | Backend service skeleton (FastAPI) | App runs locally |
| S01-D2 | `POST /v1/cases`, `GET /v1/cases/{id}` | OpenAPI + tests pass |
| S01-D3 | CaseCreated event contract/publish hook | Present in events.yaml + emitted on create |
| S01-D4 | Traceability rows | FR/API/EVT/TC linked |

## Dependencies (resolved for GO)
- [x] FRD ECMF create/get — `FRD-001` Approved
- [x] Customer reference strategy — read-only `customerId` (BR-003)
- [x] Stack ADR — `ADR-004` Approved
- [x] API-001 / API-002 + EVT-001 synchronized

## Risks
- Customer Master integration may be stubbed initially (unverified customerId allowed)
- Message broker may be local/dev stub until broker ADR

## Definition of Ready
- Sprint Approved
- FRD Approved for slice
- ADR-004 Accepted
- OpenAPI + Event contracts updated

## Definition of Done
- Create/get endpoints working with tests
- EVT-001 emitted on create (stub OK if documented)
- Catalogs + traceability updated
- `python tools/eos.py health` passes
