# API Catalog (Generated)

| Field | Value |
|---|---|
| ID | API-CAT-001 |
| Version | 0.2 |
| Owner | Backend Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | auto |
| Next Review | auto |

> Generated from OpenAPI files in `07 API Catalog/openapi`.

| Spec | Title | Version | Operations |
|---|---|---|---|
| `case-actions.v1.yaml` | ECMP Case Service API — Case Lifecycle Actions (SUPERSEDED) | 1.0.0 | 0 |
| `case-service.v1.yaml` | ECMP Case Service API | 1.7.0 | 10 |

## `case-actions.v1.yaml`

| ID | Operation | Summary |
|---|---|---|

## `case-service.v1.yaml`

| ID | Operation | Summary |
|---|---|---|
| — | `GET /health` | Service liveness check |
| — | `GET /health/ready` | Service readiness check |
| API-005 | `GET /v1/cases` | List cases (paginated, filtered) |
| API-001 | `POST /v1/cases` | Create case |
| API-002 | `GET /v1/cases/{caseId}` | Get case by id |
| API-003 | `POST /v1/cases/{caseId}/assign` | Assign or reassign case |
| API-004 | `POST /v1/cases/{caseId}/status` | Change case status via allowed transition |
| API-006 | `GET /v1/cases/{caseId}/timeline` | Get case timeline / audit trail |
| API-007 | `GET /v1/cases/{caseId}/notes` | List internal notes for a case |
| API-008 | `POST /v1/cases/{caseId}/notes` | Add an internal note (append-only) |
