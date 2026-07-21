# Domain — ECMF

| Field | Value |
|---|---|
| ID | EAR-PORTAL-DOM-ECMF |
| Version | 0.2 |
| Owner | ECMF PO |
| Reviewer | Architect |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

ECMF (Enterprise Complaint Management Framework) is the transactional core of ECMP: end-to-end complaint/inquiry handling with workflow, SLA and auditability.

- **Scope**: register, classify, assign, process, review/approve, close, reopen, root cause, SLA clocks.
- **Key flow**: Request → Validate → Classify → Assign → Process → Review → Approve? → Close → KPI/Dashboard.
- **Core data**: Case Header, Activity, Attachment, Comment, Status History, SLA Clock, Root Cause, Resolution.
- **Events produced**: CaseCreated (EVT-001), CaseAssigned (EVT-002), StatusChanged (EVT-003), CaseClosed (EVT-005), CaseReopened (EVT-007, Proposed) — SoT `08 Event Catalog/events/events.yaml`.
- **Status machine**: baseline enum and transition matrix in `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` (SoT for Case status values).

Canonical AI context: `ai/domain/ecmf.md`  
Detailed architecture: `20 Domain Architecture/ECMF/`
