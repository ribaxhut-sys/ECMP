# Event Catalog

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

The Event Catalog is the single normative source (`events/events.yaml`) for ECMP domain events: payload (camelCase), producer, consumers, delivery guarantee (at-least-once, ADR-001) and per-event idempotency rules. Current events:

- **EVT-001 CaseCreated** (ECMF) — Implemented
- **EVT-002 CaseAssigned** (ECMF) — Planned
- **EVT-003 StatusChanged** (ECMF) — Planned
- **EVT-004 SLABreached** (KPI) — Planned
- **EVT-005 CaseClosed** (ECMF) — Planned
- **EVT-006 ConfigChanged** (Administration) — Planned
- **EVT-007 CaseReopened** (ECMF) — Proposed

Events are emitted via the transactional outbox (ADR-009); a generated markdown view lives at `08 Event Catalog/EVENT_CATALOG.generated.md`.

**Canonical source:** `08 Event Catalog/README.md` and `08 Event Catalog/events/events.yaml`.
