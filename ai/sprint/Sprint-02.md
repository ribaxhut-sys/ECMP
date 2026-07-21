# Sprint-02 — Assignment, Status, Notification Hook

| Field | Value |
|---|---|
| ID | AI-SPRINT-02 |
| Version | 0.2 |
| Owner | PMO / ECMF PO |
| Reviewer | Solution Architect / Tech Lead |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2026-09-21 |

## Goal
Extend case lifecycle with assignment/status transitions and notification trigger hooks.

## In Scope
- Assign/reassign case
- Status transition guards (configured subset)
- Emit CaseAssigned + StatusChanged
- Notification consumer stub for assignment events

## Out of Scope
- Full SLA breach engine
- Executive dashboards
- Advanced approval workflows

## Context to Load
- `ai/domain/ecmf.md`
- `ai/domain/notification.md`
- `ai/06_events.md`
- `ai/07_security.md`
- Sprint-01 outcomes

## Deliverables
| ID | Deliverable | Acceptance |
|---|---|---|
| S02-D1 | Assign API/command | Authz + tests |
| S02-D2 | Status transition API/command | Invalid transitions rejected |
| S02-D3 | Event emissions | Catalog + tests |
| S02-D4 | Notification stub | Handles CaseAssigned |

> Note: this scope diverges from `IMPLEMENTATION_READINESS_ROADMAP.md`, which states "Notification is not in Build-2" — **this Sprint-02.md governs** as the more current planning document; the roadmap is historical per its banner.
