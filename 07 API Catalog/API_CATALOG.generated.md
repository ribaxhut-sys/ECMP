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
| `complaint-service.v1.yaml` | ECMP Complaint Service API | 1.0.0 | 37 |

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

## `complaint-service.v1.yaml`

| ID | Operation | Summary |
|---|---|---|
| API-218 | `POST /api/v1/auth/login` | Login |
| API-219 | `POST /api/v1/auth/refresh` | Refresh access token |
| API-220 | `POST /api/v1/auth/logout` | Logout |
| API-221 | `GET /api/v1/auth/me` | Current authenticated user |
| API-201 | `POST /api/v1/complaints` | Create complaint |
| API-202 | `GET /api/v1/complaints` | List complaints |
| API-203 | `GET /api/v1/complaints/{id}` | Get complaint by id |
| API-204 | `PUT /api/v1/complaints/{id}` | Update complaint |
| API-224 | `PATCH /api/v1/complaints/{id}/status` | Change complaint status |
| API-225 | `POST /api/v1/complaints/{id}/resolution` | Resolve complaint |
| API-226 | `GET /api/v1/complaints/{id}/resolution` | Get current complaint resolution |
| API-310 | `POST /api/v1/complaints/{id}/final-resolution` | Submit final resolution |
| API-311 | `GET /api/v1/complaints/{id}/final-resolution` | Get final resolution |
| API-312 | `POST /api/v1/complaints/{id}/close` | Close complaint |
| API-205 | `POST /api/v1/complaints/{id}/assign` | Assign or reassign complaint |
| API-206 | `GET /api/v1/complaints/{id}/assignments` | List assignment history |
| API-207 | `POST /api/v1/complaints/{id}/escalate` | Escalate complaint |
| API-301 | `POST /api/v1/complaints/{id}/escalations` | Request escalation (Branch → Head Office) |
| API-208 | `GET /api/v1/complaints/{id}/escalations` | List escalation history |
| API-302 | `GET /api/v1/escalations/{id}` | Get escalation by id |
| API-303 | `POST /api/v1/escalations/{id}/approve` | Approve escalation request |
| API-304 | `POST /api/v1/escalations/{id}/reject` | Reject escalation request |
| API-305 | `POST /api/v1/escalations/{id}/appointments` | Book appointment for approved escalation |
| API-306 | `GET /api/v1/appointments/{id}` | Get appointment by id |
| API-307 | `POST /api/v1/appointments/{id}/check-in` | Check in customer for booked appointment |
| API-308 | `POST /api/v1/appointments/{id}/complete` | Complete checked-in appointment |
| API-309 | `POST /api/v1/appointments/{id}/no-show` | Mark booked appointment as customer no-show |
| API-209 | `GET /api/v1/complaints/{id}/timeline` | Get complaint timeline |
| API-210 | `GET /api/v1/reports/summary` | Complaint report summary |
| API-211 | `GET /api/v1/reports/by-status` | Complaint counts by status |
| API-212 | `GET /api/v1/reports/by-branch` | Complaint counts by branch |
| API-222 | `GET /api/v1/customers` | List customer references |
| API-223 | `GET /api/v1/branches` | List branch references |
| API-213 | `POST /api/v1/users` | Create user |
| API-214 | `GET /api/v1/users` | List users |
| API-215 | `GET /api/v1/users/{id}` | Get user by id |
| API-216 | `PUT /api/v1/users/{id}` | Update user |
| API-217 | `PATCH /api/v1/users/{id}/status` | Activate or deactivate user |
