# Event Catalog (Generated)

| Field | Value |
|---|---|
| ID | EVT-CAT-001 |
| Version | 0.7 |
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
| EVT-CM-001 | ComplaintCreated | ECMF | Planned | Batch 1 Aggregate create success (FR-001); status REGISTERED; no Case |
| EVT-CM-002 | CreateReplayed | ECMF | Planned | Idempotent replay of create (Request Id or Channel Message Id) |
| EVT-CM-003 | CreateRedirectedToExisting | ECMF | Planned | Create abandoned; actor redirected to existing Complaint (D-06) |
| EVT-CM-004 | DuplicateCheckOutcomeRecorded | ECMF | Planned | Duplicate check outcome on create path |
| EVT-CM-005 | NotificationOutboxEnqueued | ECMF | Planned | Opt-in notification enqueued to ECMP outbox after create (ADR-009) |
| EVT-CM-010 | CustomerValidated | ECMF | Planned | Successful customer search/confirm (FR-002) |
| EVT-CM-011 | CustomerValidationFailed | ECMF | Planned | not found / ambiguous / degraded / blocked enumeration outcome |
| EVT-CM-012 | CustomerReferenceEnriched | ECMF | Planned | UNVERIFIED Complaint enriched with verified CustomerId |
| EVT-CM-020 | DuplicateWarned | ECMF | Planned | Duplicate candidates at or above threshold |
| EVT-CM-021 | DuplicateOverridden | ECMF | Planned | Authorized override with justification |
| EVT-CM-022 | DuplicateLinked | ECMF | Planned | Possible-duplicate / related linkage recorded |
| EVT-CM-023 | DuplicateRedirectedToExisting | ECMF | Planned | Redirect decision to existing Complaint |
| EVT-CM-024 | DuplicateRecommendedExisting | ECMF | Planned | Recommend continue on existing Complaint; no Case create in Batch 1 |
| EVT-CM-025 | DuplicateCheckDegraded | ECMF | Planned | Duplicate check unavailable / timeout |
| EVT-CM-026 | DuplicateLaterReviewEnqueued | ECMF | Planned | Later-review work item for degraded duplicate check |
| EVT-CM-030 | AttachmentUploaded | ECMF | Planned | Attachment ACTIVE with integrity hash |
| EVT-CM-031 | AttachmentSuperseded | ECMF | Planned | Prior attachment version superseded |
| EVT-CM-032 | AttachmentVoided | ECMF | Planned | Void-with-reason (no physical delete) |
| EVT-CM-033 | AttachmentTransferred | ECMF | Planned | Staged evidence transferred to surviving Complaint (D-06); semantics OQ-CM-B1-014 |
| EVT-CM-034 | AttachmentAccess | ECMF | Planned | Sensitive attachment download/access audited |
| EVT-CM-040 | CaseEscalatedToPusat | ECMF | Planned | Case escalated Cabang→Pusat with Escalation Package (DEC-F4 / FR-CM-010) |
| EVT-CM-041 | CaseEscalationReturned | ECMF | Planned | Pusat returned escalation to originating branch (reason code + note) |
| EVT-CM-042 | CaseResolvedWithVisibility | ECMF | Planned | Case resolved; includes resultVisibility when Pusat path (DEC-F4) |
| EVT-CM-043 | ResultVisibilityChanged | ECMF | Planned | Post-resolve result_visibility changed with audit fields |
| EVT-CM-044 | CaseAccessDenied | ECMF | Planned | Optional security audit when Case read denied by org/result_visibility |

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

### EVT-CM-001 — ComplaintCreated
- `complaintId`: string
- `complaintNumber`: string
- `customerId`: string
- `status`: string
- `requestId`: string
- `channelMessageId`: string
- `createdAt`: datetime
- `createdBy`: string

### EVT-CM-002 — CreateReplayed
- `complaintId`: string
- `requestId`: string
- `channelMessageId`: string
- `replayedAt`: datetime
- `actorId`: string

### EVT-CM-003 — CreateRedirectedToExisting
- `survivingComplaintId`: string
- `stagingToken`: string
- `actorId`: string
- `redirectedAt`: datetime

### EVT-CM-004 — DuplicateCheckOutcomeRecorded
- `complaintId`: string
- `outcome`: string
- `policyVersion`: string
- `recordedAt`: datetime

### EVT-CM-005 — NotificationOutboxEnqueued
- `complaintId`: string
- `outboxId`: string
- `enqueuedAt`: datetime

### EVT-CM-010 — CustomerValidated
- `customerId`: string
- `keyType`: string
- `asOf`: datetime
- `actorId`: string

### EVT-CM-011 — CustomerValidationFailed
- `keyType`: string
- `outcome`: string
- `actorId`: string
- `occurredAt`: datetime

### EVT-CM-012 — CustomerReferenceEnriched
- `complaintId`: string
- `previousCustomerRef`: string
- `customerId`: string
- `enrichedAt`: datetime

### EVT-CM-020 — DuplicateWarned
- `customerId`: string
- `candidateCount`: integer
- `warnedAt`: datetime

### EVT-CM-021 — DuplicateOverridden
- `complaintId`: string
- `justificationRef`: string
- `actorId`: string
- `overriddenAt`: datetime

### EVT-CM-022 — DuplicateLinked
- `sourceComplaintId`: string
- `targetComplaintId`: string
- `linkType`: string
- `linkedAt`: datetime

### EVT-CM-023 — DuplicateRedirectedToExisting
- `survivingComplaintId`: string
- `actorId`: string
- `redirectedAt`: datetime

### EVT-CM-024 — DuplicateRecommendedExisting
- `existingComplaintId`: string
- `recommendation`: string
- `recommendedAt`: datetime

### EVT-CM-025 — DuplicateCheckDegraded
- `degradedFlag`: boolean
- `reason`: string
- `occurredAt`: datetime

### EVT-CM-026 — DuplicateLaterReviewEnqueued
- `workItemId`: string
- `customerId`: string
- `enqueuedAt`: datetime

### EVT-CM-030 — AttachmentUploaded
- `attachmentId`: string
- `complaintId`: string
- `integrityHash`: string
- `uploadedAt`: datetime

### EVT-CM-031 — AttachmentSuperseded
- `attachmentId`: string
- `supersededAttachmentId`: string
- `supersededAt`: datetime

### EVT-CM-032 — AttachmentVoided
- `attachmentId`: string
- `reason`: string
- `voidedAt`: datetime
- `actorId`: string

### EVT-CM-033 — AttachmentTransferred
- `attachmentId`: string
- `fromStagingToken`: string
- `survivingComplaintId`: string
- `transferredAt`: datetime

### EVT-CM-034 — AttachmentAccess
- `attachmentId`: string
- `actorId`: string
- `accessedAt`: datetime
- `classification`: string

### EVT-CM-040 — CaseEscalatedToPusat
- `caseId`: string
- `complaintId`: string
- `fromBranchId`: string
- `toUnit`: string
- `reason`: string
- `escalatedBy`: string
- `escalatedAt`: datetime

### EVT-CM-041 — CaseEscalationReturned
- `caseId`: string
- `complaintId`: string
- `returnedToBranchId`: string
- `returnReasonCode`: string
- `returnNote`: string
- `returnedBy`: string
- `returnedAt`: datetime

### EVT-CM-042 — CaseResolvedWithVisibility
- `caseId`: string
- `complaintId`: string
- `resolutionCode`: string
- `resultVisibility`: string
- `resolvedBy`: string
- `resolvedAt`: datetime

### EVT-CM-043 — ResultVisibilityChanged
- `caseId`: string
- `complaintId`: string
- `fromVisibility`: string
- `toVisibility`: string
- `changedBy`: string
- `changedAt`: datetime
- `changeNote`: string

### EVT-CM-044 — CaseAccessDenied
- `caseId`: string
- `actorId`: string
- `actorBranchId`: string
- `deniedAt`: datetime
- `reasonCode`: string
