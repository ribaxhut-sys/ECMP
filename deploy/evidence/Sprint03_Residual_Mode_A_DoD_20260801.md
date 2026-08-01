# Sprint-03 Residual — Mode A DoD (2026-08-01)

| Field | Value |
|---|---|
| Status | **Scoped** under DEC-021 |
| Not started as code in this change | Intentional — avoid double-build |

## Decision matrix

| Residual | Mode A DoD now? | Action |
|---|---|---|
| API-005 list | Already in `implementation/backend` | Covered by G2 regression |
| FR-020 notif stub | Already in sprint tree | Covered |
| FR-040 dashboard queues | **No** — defer unless PO expands DoD | Future Work until API-040 freeze |
| FR-030 SLA event-clock (Sprint) | **No** until separate process needs broker re-eval | Prefer not dual-build vs VPS `modules/sla/`; Cutover DEC later |
| VPS SLA/dashboard analogs | Lab ops only | Not claimed as case-service FR-030/040 |
| API-010 | Deferred ACR-002 | Skip |
| Mode B | CLOSED C-7 | Skip |

## Rule

Do not implement Sprint FR-030/040 in both trees. Choose Cutover DEC before porting.

## Decision status (Mode A Batch-1 RC)

| Topic | Verdict for Mode A RC | Blocks RC cut? |
|---|---|---|
| FR-040 dashboard queues | **DEFER** (Future Work) unless PO expands DoD + freezes API-040 | **No** — deferral is the decision |
| FR-030 SLA event-clock (Sprint) | **DEFER** until broker re-eval / Cutover DEC | **No** — deferral is the decision |

PO/Board may still **countersign** this matrix; blank countersign ≠ reopen implementation. Do not forge Accept.
