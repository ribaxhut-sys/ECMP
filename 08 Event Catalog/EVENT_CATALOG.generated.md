# Event Catalog (Generated)

| Field | Value |
|---|---|
| ID | EVT-CAT-001 |
| Version | 0.6 |
| Owner | Integration Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | auto |
| Next Review | auto |

> Generated from `08 Event Catalog/events/events.yaml`.

| Event ID | Name | Producer | Status | Description |
|---|---|---|---|---|
| EVT-001 | CaseCreated | ECMF | Implemented | Emitted when a case is registered (FR-001b) |
| EVT-002 | CaseAssigned | ECMF | Implemented | Emitted when a case is assigned/reassigned (Sprint-02B). Payload FROZEN at gate G1 (DEC-006, 2026-07-21) — changes require a new freeze decision. |
| EVT-003 | StatusChanged | ECMF | Implemented | Emitted on valid workflow status transition (BR-001) (Sprint-02B). Payload FROZEN at gate G1 (DEC-006, 2026-07-21) — changes require a new freeze decision. |
| EVT-004 | SLABreached | KPI | Planned | Emitted when SLA threshold is breached |
| EVT-005 | CaseClosed | ECMF | Implemented | Emitted when a case is closed (Sprint-02B, PENDING_REVIEW→CLOSED only; other producing transitions remain out of scope) |
| EVT-006 | ConfigChanged | Administration | Planned | Emitted when effective configuration changes (BR-ADM-02) |
| EVT-007 | CaseReopened | ECMF | Proposed | Emitted when a closed case is reopened (BR-ECMF-07); proposed addition beyond Blueprint minimal set |
| EVT-008 | ConfigChangeRequested | Administration | Proposed | Emitted when a critical configuration change request is submitted for approval (BR-ADM-01, FRD-007 FR-063); proposed via ECMP_FRD_Administration_v0.1 |
| EVT-009 | ComplaintCreated | ECMF | Implemented | Emitted in-process when a Complaint is created (TASK-045 foundation; no bus yet) |
| EVT-010 | ComplaintAssigned | ECMF | Implemented | Standardized ComplaintAssigned event shape (TASK-045 factory; Assignment module unchanged) |
| EVT-011 | ComplaintAccepted | ECMF | Implemented | Emitted in-process when ASSIGNED transitions to IN_PROGRESS (assignee acceptance; TASK-045) |
| EVT-012 | ComplaintInProgress | ECMF | Implemented | Emitted in-process when Complaint status becomes IN_PROGRESS (TASK-045) |
| EVT-013 | ComplaintResolved | ECMF | Implemented | Standardized ComplaintResolved event shape (TASK-045 factory) |
| EVT-014 | ComplaintClosed | ECMF | Implemented | Emitted in-process when a Complaint is closed (TASK-045; API-312 path) |
| EVT-015 | ComplaintEscalated | ECMF | Implemented | Standardized ComplaintEscalated event shape (TASK-045 factory; Escalation module unchanged) |

## Payload Summary

### EVT-001 — CaseCreated
- `caseId`: string
- `customerId`: string
- `caseType`: string
- `priority`: string
- `subject`: string
- `status`: string
- `createdAt`: datetime
- `createdBy`: string

### EVT-002 — CaseAssigned
- `caseId`: string
- `assigneeId`: string
- `unitId`: string
- `assignedBy`: string
- `previousAssigneeId`: string
- `assignedAt`: datetime

### EVT-003 — StatusChanged
- `caseId`: string
- `fromStatus`: string
- `toStatus`: string
- `changedBy`: string
- `changedAt`: datetime
- `reason`: string

### EVT-004 — SLABreached
- `caseId`: string
- `slaId`: string
- `breachedAt`: datetime
- `dueAt`: datetime
- `severity`: string

### EVT-005 — CaseClosed
- `caseId`: string
- `resolutionCode`: string
- `closedBy`: string
- `closedAt`: datetime

### EVT-006 — ConfigChanged
- `configKey`: string
- `version`: string
- `oldValue`: object
- `newValue`: object
- `changedBy`: string
- `changedAt`: datetime
- `effectiveDate`: datetime

### EVT-007 — CaseReopened
- `caseId`: string
- `reopenedBy`: string
- `reopenedAt`: datetime
- `reason`: string

### EVT-008 — ConfigChangeRequested
- `changeRequestId`: string
- `configKey`: string
- `requestedBy`: string
- `requestedAt`: datetime
- `approverRole`: string
- `summary`: string

### EVT-009 — ComplaintCreated
- `eventId`: string
- `eventType`: string
- `occurredAt`: datetime
- `complaintId`: string
- `complaintNumber`: string
- `currentStatus`: string
- `priority`: string
- `sourceType`: string
- `sourceId`: string
- `targetType`: string
- `targetId`: string
- `routing`: object
- `contextReference`: string
- `payload`: object

### EVT-010 — ComplaintAssigned
- `eventId`: string
- `eventType`: string
- `occurredAt`: datetime
- `complaintId`: string
- `complaintNumber`: string
- `currentStatus`: string
- `priority`: string
- `sourceType`: string
- `sourceId`: string
- `targetType`: string
- `targetId`: string
- `routing`: object
- `contextReference`: string
- `payload`: object

### EVT-011 — ComplaintAccepted
- `eventId`: string
- `eventType`: string
- `occurredAt`: datetime
- `complaintId`: string
- `complaintNumber`: string
- `currentStatus`: string
- `priority`: string
- `sourceType`: string
- `sourceId`: string
- `targetType`: string
- `targetId`: string
- `routing`: object
- `contextReference`: string
- `payload`: object

### EVT-012 — ComplaintInProgress
- `eventId`: string
- `eventType`: string
- `occurredAt`: datetime
- `complaintId`: string
- `complaintNumber`: string
- `currentStatus`: string
- `priority`: string
- `sourceType`: string
- `sourceId`: string
- `targetType`: string
- `targetId`: string
- `routing`: object
- `contextReference`: string
- `payload`: object

### EVT-013 — ComplaintResolved
- `eventId`: string
- `eventType`: string
- `occurredAt`: datetime
- `complaintId`: string
- `complaintNumber`: string
- `currentStatus`: string
- `priority`: string
- `sourceType`: string
- `sourceId`: string
- `targetType`: string
- `targetId`: string
- `routing`: object
- `contextReference`: string
- `payload`: object

### EVT-014 — ComplaintClosed
- `eventId`: string
- `eventType`: string
- `occurredAt`: datetime
- `complaintId`: string
- `complaintNumber`: string
- `currentStatus`: string
- `priority`: string
- `sourceType`: string
- `sourceId`: string
- `targetType`: string
- `targetId`: string
- `routing`: object
- `contextReference`: string
- `payload`: object

### EVT-015 — ComplaintEscalated
- `eventId`: string
- `eventType`: string
- `occurredAt`: datetime
- `complaintId`: string
- `complaintNumber`: string
- `currentStatus`: string
- `priority`: string
- `sourceType`: string
- `sourceId`: string
- `targetType`: string
- `targetId`: string
- `routing`: object
- `contextReference`: string
- `payload`: object
