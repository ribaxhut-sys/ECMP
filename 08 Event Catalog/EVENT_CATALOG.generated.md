# Event Catalog (Generated)

| Field | Value |
|---|---|
| ID | EVT-CAT-001 |
| Version | 0.4 |
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
| EVT-002 | CaseAssigned | ECMF | Planned | Emitted when a case is assigned/reassigned |
| EVT-003 | StatusChanged | ECMF | Planned | Emitted on valid workflow status transition (BR-001) |
| EVT-004 | SLABreached | KPI | Planned | Emitted when SLA threshold is breached |
| EVT-005 | CaseClosed | ECMF | Planned | Emitted when a case is closed |
| EVT-006 | ConfigChanged | Administration | Planned | Emitted when effective configuration changes (BR-ADM-02) |
| EVT-007 | CaseReopened | ECMF | Proposed | Emitted when a closed case is reopened (BR-ECMF-07); proposed addition beyond Blueprint minimal set |

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
