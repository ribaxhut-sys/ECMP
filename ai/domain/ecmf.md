# Domain Context — ECMF

| Field | Value |
|---|---|
| ID | AI-DOM-ECMF |
| Version | 0.2 |
| Owner | ECMF PO / Solution Architect |
| Reviewer | BA Lead |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Objective
End-to-end complaint/inquiry management with workflow, SLA, auditability.

## In Scope
Register, classify, assign, process, review/approve, close, reopen, root cause, SLA clocks.

## Key Flow
Request → Validate → Classify → Assign → Process → Review → Approve? → Close → KPI/Dashboard

## Core Data
Case Header, Activity, Attachment, Comment, Status History, SLA Clock, Root Cause, Resolution

## Events
CaseCreated (EVT-001), CaseAssigned (EVT-002), StatusChanged (EVT-003), SLABreached (EVT-004, via KPI), CaseClosed (EVT-005), ConfigChanged (EVT-006, via Administration), CaseReopened (EVT-007, Proposed)
(SoT: `08 Event Catalog/events/events.yaml`)

## Detailed Docs
`20 Domain Architecture/ECMF/`
