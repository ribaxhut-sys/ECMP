# Domain Navigator — Workflow

| Field | Value |
|---|---|
| ID | EOS-NAV-WF |
| Version | 0.1 |
| Owner | Automation / Architecture |
| Reviewer | PMO / Enterprise Architecture |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-24 |
| Next Review | auto |

> Command concept: _Masuk ke domain Workflow_

## Quick Pack

- Domain Architecture: `20 Domain Architecture/Workflow/README.md`
- Workflow Architecture: `20 Domain Architecture/Workflow/WORKFLOW_ARCHITECTURE.md`
- Workflow Guide: `20 Domain Architecture/Workflow/WORKFLOW_GUIDE.md` (TASK-052)

## Business Rules

- —

## FRD

- —

## API

- — (no HTTP in TASK-052)

## Events (runtime consumers)

- ComplaintCreated
- ComplaintAssigned
- ComplaintAccepted
- ComplaintInProgress
- ComplaintResolved
- ComplaintClosed
- ComplaintEscalated

## Tests

- `backend/tests/test_workflow.py`

## Active / Related Sprints

- Sprint-14 (TASK-052)

## ADR

- `ADR-008` — Workflow Config ownership (Administration) — distinct from this runtime layer
- `ADR-009` — Message Broker Deferral

## Notes

Do not confuse with Administration **Workflow Config** (Case status matrix).
