# AI Evaluation Facts (Indexed Corpus)

| Field | Value |
|---|---|
| ID | AIP-EVAL-FACTS |
| Version | 1.0 |
| Owner | Enterprise Architecture |
| Reviewer | Agent Owners |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

These facts are intentionally indexed for golden-question evaluation.

## Architecture
- ECMP does **not** own customer master data. It is not System of Record; customer master is read-only via `customerId`.
- Architecture trade-offs must be recorded in an **ADR** (Architecture Decision Record).
- Integration between ECMF and KPI/Notification is **event-driven** / asynchronous via domain events.

## Business / ECMF Sprint-01
- Initial status of a newly created case is **REGISTERED**.
- Create and get case are covered by **FR-001** and **FR-002**.

## Coding
- Sprint-01 backend stack is **Python / FastAPI** (ADR-004).
- Backend code must live under `implementation/backend`.
- After create case, emit **CaseCreated** / **EVT-001**.

## QA
- Source of traceability links is `26 Traceability/traceability.yaml`.
- Acceptance test id for create case includes **TC-001**.

## Security
- Permissions required: `cases:create` and `cases:read`.
- Audit trail cannot be deleted; it is immutable.
