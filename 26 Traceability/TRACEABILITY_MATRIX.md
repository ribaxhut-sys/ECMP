# ECMP Traceability Matrix

| Field | Value |
|---|---|
| ID | TRC-001 |
| Version | 0.1 |
| Owner | BA Lead / QA Lead |
| Reviewer | PMO / Enterprise Architecture |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | auto |
| Next Review | auto |

> Synced from `traceability.yaml` by `tools/sync_traceability_md.py`.

| Link | Domain | BP | BR | FR | API | Event | Test | Sprint | Status |
|---|---|---|---|---|---|---|---|---|---|
| TRC-L-009 | Core Platform | BP-001 | BR-008 | FR-001c | API-001 | — | TC-005 | Sprint-01 | Approved |
| TRC-L-001 | ECMF | BP-001 | BR-001 | FR-001 | API-001 | EVT-001 | TC-001 | Sprint-01 | Approved |
| TRC-L-002 | ECMF | BP-001 | BR-007 | FR-002 | API-002 | — | TC-002 | Sprint-01 | Approved |
| TRC-L-003 | ECMF | BP-002 | BR-002 | FR-003 | API-003 | EVT-002, EVT-003 | TC-003 | Sprint-02 | Approved |
| TRC-L-004 | ECMF | BP-002 | BR-001 | FR-004 | API-004 | EVT-003 | TC-004 | Sprint-02 | Approved |
| TRC-L-005 | CRM | BP-003 | BR-003 | FR-010 | API-010 | — | TC-010 | Sprint-02 | Planned |
| TRC-L-006 | Notification | BP-004 | BR-004 | FR-020 | — | EVT-001, EVT-002 | TC-020 | Sprint-02 | Approved |
| TRC-L-007 | KPI | BP-005 | BR-005 | FR-030 | — | EVT-004, EVT-001, EVT-003, EVT-005, EVT-007 | TC-030 | Sprint-03 | Planned |
| TRC-L-008 | Dashboard | BP-006 | BR-006 | FR-040 | API-040 | — | TC-040 | Sprint-03 | Planned |
| TRC-L-010 | ECMF | BP-001 | BR-007 | FR-005 | API-005 | — | TC-006 | Sprint-03B | Approved |

## Artifact Dictionary

### BP
- `BP-001`: Complaint can be registered and tracked end-to-end
- `BP-002`: Assignment and status follow configured workflow
- `BP-003`: Customer 360 available during handling
- `BP-004`: Stakeholders notified on key case events
- `BP-005`: SLA achievement measurable automatically
- `BP-006`: Supervisors can monitor operational queues

### BR
- `BR-001`: Status transitions must follow configured workflow
- `BR-002`: Assignment requires authorized role/unit
- `BR-003`: Customer master is read-only reference in ECMP
- `BR-004`: Notifications only for configured events/recipients
- `BR-005`: SLA calculated automatically by category/priority
- `BR-006`: Dashboard views are role and org scoped
- `BR-007`: Case create/read requires authenticated permission cases:create or cases:read
- `BR-008`: Significant writes persist immutable append-only audit record in same transaction

### FR
- `FR-001`: Create complaint case linked to customer
- `FR-001c`: Persist immutable audit record on successful create
- `FR-002`: Retrieve case details by id
- `FR-003`: Assign/reassign case
- `FR-004`: Change case status via allowed transitions
- `FR-010`: Search/view customer 360
- `FR-020`: Send notification on case assignment/creation
- `FR-030`: Detect and record SLA breach
- `FR-040`: Show operational case queue dashboard
- `FR-005`: List cases, paginated and filtered (status/priority/caseType/assigneeId)

### API
- `API-001`: POST /v1/cases
- `API-002`: GET /v1/cases/{caseId}
- `API-003`: POST /v1/cases/{caseId}/assign
- `API-004`: POST /v1/cases/{caseId}/status
- `API-005`: GET /v1/cases (paginated, filtered list — case-service.v1.yaml v1.5.0, Sprint-03B)
- `API-010`: GET /v1/customers/{customerId}
- `API-040`: GET /v1/dashboard/queues

### EVENTS
- `EVT-001`: CaseCreated
- `EVT-002`: CaseAssigned
- `EVT-003`: StatusChanged
- `EVT-004`: SLABreached
- `EVT-005`: CaseClosed
- `EVT-006`: ConfigChanged
- `EVT-007`: CaseReopened (Proposed)

### TESTS
- `TC-001`: Create complaint with valid customer succeeds
- `TC-002`: Get case by id returns case
- `TC-003`: Assign case updates assignee and emits event
- `TC-004`: Invalid status transition rejected
- `TC-005`: Audit record persisted on create (same transaction)
- `TC-010`: Customer 360 retrieval succeeds
- `TC-020`: Notification stub handles CaseAssigned
- `TC-030`: SLA breach event emitted when overdue
- `TC-040`: Dashboard queue view scoped by role/org
- `TC-006`: List cases paginated and filtered by status/priority/caseType/assigneeId

## Maintenance Rule

Update `traceability.yaml` first, then run `python tools/sync_traceability_md.py` (or `run_engineering_os.py`).
