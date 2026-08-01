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
| `case-service.v1.yaml` | ECMP Case Service API | 1.7.0 | 12 |
| `complaint-domain-service.v1.yaml` | ECMP Complaint Domain Service API | 1.4.0 | 23 |
| `complaint-management-batch1.v1.yaml` | ECMP Complaint Management Batch 1 API | 1.0.0-planned | 13 |
| `complaint-management-esc-res.v1.yaml` | ECMP Complaint Management Escalation & Resolution API (DEC-F4) | 1.0.0-planned | 7 |
| `complaint-service.v1.yaml` | ECMP Complaint Service API | 1.0.0 | 101 |
| `queue-service.v1.yaml` | ECMP Queue Service API | 1.1.0 | 22 |

## `case-actions.v1.yaml`

| ID | Operation | Summary |
|---|---|---|

## `case-service.v1.yaml`

| ID | Operation | Summary |
|---|---|---|
| — | `GET /live` | Service liveness check |
| — | `GET /ready` | Service readiness check |
| — | `GET /health` | Service health (legacy informational) |
| — | `GET /version` | Release artifact provenance |
| API-005 | `GET /v1/cases` | List cases (paginated, filtered) |
| API-001 | `POST /v1/cases` | Create case |
| API-002 | `GET /v1/cases/{caseId}` | Get case by id |
| API-003 | `POST /v1/cases/{caseId}/assign` | Assign or reassign case |
| API-004 | `POST /v1/cases/{caseId}/status` | Change case status via allowed transition |
| API-006 | `GET /v1/cases/{caseId}/timeline` | Get case timeline / audit trail |
| API-007 | `GET /v1/cases/{caseId}/notes` | List internal notes for a case |
| API-008 | `POST /v1/cases/{caseId}/notes` | Add an internal note (append-only) |

## `complaint-domain-service.v1.yaml`

| ID | Operation | Summary |
|---|---|---|
| API-390 | `POST /api/v1/complaints` | Create complaint |
| API-391 | `GET /api/v1/complaints` | List complaints by organization |
| API-392 | `GET /api/v1/complaints/{complaintId}` | Get complaint by id |
| API-393 | `PUT /api/v1/complaints/{complaintId}` | Update complaint |
| API-394 | `DELETE /api/v1/complaints/{complaintId}` | Delete complaint |
| API-397 | `POST /api/v1/complaints/{complaintId}/start` | Start complaint processing |
| API-398 | `POST /api/v1/complaints/{complaintId}/resolve` | Resolve complaint |
| API-399 | `POST /api/v1/complaints/{complaintId}/close` | Close complaint |
| API-400 | `POST /api/v1/complaints/{complaintId}/reopen` | Reopen complaint |
| API-401 | `POST /api/v1/complaints/{complaintId}/assign` | Assign complaint |
| API-402 | `POST /api/v1/complaints/{complaintId}/reassign` | Reassign complaint |
| API-403 | `POST /api/v1/complaints/{complaintId}/unassign` | Unassign complaint |
| API-404 | `GET /api/v1/complaints/{complaintId}/assignment` | Get current assignment |
| API-405 | `GET /api/v1/complaints/{complaintId}/assignments` | List assignment history |
| API-406 | `POST /api/v1/complaints/{complaintId}/escalate` | Escalate complaint |
| API-407 | `GET /api/v1/complaints/{complaintId}/escalation` | Get current escalation |
| API-408 | `GET /api/v1/complaints/{complaintId}/escalations` | List escalation history |
| API-409 | `POST /api/v1/complaints/{complaintId}/sla/start` | Start complaint SLA |
| API-410 | `POST /api/v1/complaints/{complaintId}/sla/complete` | Complete complaint SLA |
| API-411 | `POST /api/v1/complaints/{complaintId}/sla/recalculate` | Recalculate complaint SLA |
| API-412 | `GET /api/v1/complaints/{complaintId}/sla` | Get complaint SLA |
| API-395 | `GET /api/v1/tickets/{ticketId}/complaints` | List complaints by queue ticket |
| API-396 | `POST /api/v1/tickets/{ticketId}/complaints` | Create complaint for queue ticket |

## `complaint-management-batch1.v1.yaml`

| ID | Operation | Summary |
|---|---|---|
| API-500 | `POST /api/v1/cm/complaints` | Create Complaint (idempotent; no Case) |
| API-501 | `GET /api/v1/cm/complaints/{complaintId}` | Get Complaint confirmation/detail |
| API-502 | `POST /api/v1/cm/customers/search` | Search Customer by exactly one key type |
| API-503 | `POST /api/v1/cm/customers/confirm` | Confirm / lock CustomerId in session context |
| API-504 | `GET /api/v1/cm/customers/{customerId}/batch1-360` | Batch 1 Customer 360 minimum |
| API-505 | `POST /api/v1/cm/duplicates/check` | Check duplicate Complaint candidates |
| API-506 | `POST /api/v1/cm/duplicates/decisions` | Record duplicate decision / linkage |
| API-507 | `POST /api/v1/attachments` | Upload attachment (Batch 1 semantics) |
| API-508 | `POST /api/v1/cm/attachments/transfer` | Transfer staged attachments to surviving Complaint |
| API-509 | `GET /api/v1/complaints/{id}/attachments` | List attachments for Complaint |
| API-510 | `GET /api/v1/attachments/{id}` | Get attachment metadata |
| API-512 | `DELETE /api/v1/attachments/{id}` | Logical void (not physical delete) |
| API-511 | `GET /api/v1/attachments/{id}/download` | Download attachment bytes |

## `complaint-management-esc-res.v1.yaml`

| ID | Operation | Summary |
|---|---|---|
| API-520 | `POST /api/v1/cm/cases/{caseId}/escalate-to-pusat` | Escalate Case Cabang → Pusat |
| API-521 | `POST /api/v1/cm/cases/{caseId}/return-escalation` | Return escalation to originating branch |
| API-522 | `GET /api/v1/cm/pusat/escalated-queue` | Pusat handler queue (escalated Cases only) |
| API-523 | `POST /api/v1/cm/cases/{caseId}/resolve` | Resolve Case (Pusat path requires result_visibility) |
| API-524 | `PATCH /api/v1/cm/cases/{caseId}/result-visibility` | Change result_visibility after Resolve |
| API-525 | `GET /api/v1/cm/cases/{caseId}` | Get Case with visibility enforcement |
| API-526 | `GET /api/v1/cm/cases` | List/search Cases with visibility enforcement |

## `complaint-service.v1.yaml`

| ID | Operation | Summary |
|---|---|---|
| API-218 | `POST /api/v1/auth/login` | Login |
| API-219 | `POST /api/v1/auth/refresh` | Refresh access token |
| API-220 | `POST /api/v1/auth/logout` | Logout |
| API-221 | `GET /api/v1/auth/me` | Current authenticated user |
| API-410 | `POST /api/v1/auth/forgot-password` | Request password reset |
| API-411 | `POST /api/v1/auth/reset-password` | Reset password with token |
| API-201 | `POST /api/v1/complaints` | Create complaint |
| API-202 | `GET /api/v1/complaints` | List complaints |
| API-388 | `GET /api/v1/complaints/search` | Search and filter complaints |
| API-203 | `GET /api/v1/complaints/{id}` | Get complaint by id |
| API-204 | `PUT /api/v1/complaints/{id}` | Update complaint |
| API-224 | `PATCH /api/v1/complaints/{id}/status` | Change complaint status |
| API-225 | `POST /api/v1/complaints/{id}/resolution` | Resolve complaint |
| API-226 | `GET /api/v1/complaints/{id}/resolution` | Get current complaint resolution |
| API-310 | `POST /api/v1/complaints/{id}/final-resolution` | Submit final resolution |
| API-311 | `GET /api/v1/complaints/{id}/final-resolution` | Get final resolution |
| API-314 | `GET /api/v1/complaints/{id}/sla` | Get complaint SLA |
| API-315 | `GET /api/v1/sla/policies` | List SLA policies |
| API-316 | `POST /api/v1/sla/policies` | Create SLA policy |
| API-317 | `PUT /api/v1/sla/policies/{id}/activate` | Activate SLA policy |
| API-312 | `POST /api/v1/complaints/{id}/close` | Close complaint |
| API-205 | `POST /api/v1/complaints/{id}/assign` | Assign or reassign complaint |
| API-206 | `GET /api/v1/complaints/{id}/assignments` | List assignment history |
| API-207 | `POST /api/v1/complaints/{id}/escalate` | Escalate complaint |
| API-301 | `POST /api/v1/complaints/{id}/escalations` | Request escalation (Branch → Head Office) |
| API-208 | `GET /api/v1/complaints/{id}/escalations` | List escalation history |
| API-302 | `GET /api/v1/escalations/{id}` | Get escalation by id |
| API-313 | `POST /api/v1/escalations/{id}/close` | Close escalation |
| API-303 | `POST /api/v1/escalations/{id}/approve` | Approve escalation request |
| API-304 | `POST /api/v1/escalations/{id}/reject` | Reject escalation request |
| API-305 | `POST /api/v1/escalations/{id}/appointments` | Book appointment for approved escalation |
| API-306 | `GET /api/v1/appointments/{id}` | Get appointment by id |
| API-307 | `POST /api/v1/appointments/{id}/check-in` | Check in customer for booked appointment |
| API-308 | `POST /api/v1/appointments/{id}/complete` | Complete checked-in appointment |
| API-309 | `POST /api/v1/appointments/{id}/no-show` | Mark booked appointment as customer no-show |
| API-209 | `GET /api/v1/complaints/{id}/timeline` | Get complaint timeline |
| API-318 | `GET /api/v1/kpi/summary` | KPI foundation summary |
| API-389 | `GET /api/v1/dashboard/summary` | Dashboard complaint summary |
| API-390 | `GET /api/v1/dashboard/queue` | Dashboard queue summary |
| API-391 | `GET /api/v1/dashboard/sla` | Dashboard SLA summary |
| API-392 | `GET /api/v1/dashboard/notifications` | Dashboard notification summary |
| API-393 | `GET /api/v1/dashboard/trends` | Dashboard complaint trends |
| API-394 | `GET /api/v1/dashboard/kpi` | Dashboard KPI rates |
| API-319 | `GET /api/v1/dashboard/overview` | Dashboard overview composition |
| API-320 | `GET /api/v1/settings/public` | List public settings |
| API-321 | `GET /api/v1/settings` | List all settings |
| API-322 | `PUT /api/v1/settings/{key}` | Update setting value |
| API-386 | `GET /api/v1/attachments` | List attachments |
| API-323 | `POST /api/v1/attachments` | Upload attachment |
| API-324 | `GET /api/v1/attachments/{id}` | Get attachment metadata |
| API-326 | `DELETE /api/v1/attachments/{id}` | Logically delete attachment |
| API-325 | `GET /api/v1/attachments/{id}/download` | Download attachment file |
| API-387 | `GET /api/v1/complaints/{id}/attachments` | List attachments for a complaint |
| API-327 | `GET /api/v1/notification/templates` | List notification templates |
| API-328 | `POST /api/v1/notification/templates` | Create notification template |
| API-329 | `GET /api/v1/notification/templates/{id}` | Get notification template |
| API-330 | `PUT /api/v1/notification/templates/{id}` | Update notification template |
| API-331 | `DELETE /api/v1/notification/templates/{id}` | Soft-delete notification template |
| API-333 | `GET /api/v1/notifications` | List notification queue |
| API-332 | `POST /api/v1/notifications` | Enqueue notification |
| API-334 | `GET /api/v1/notifications/{id}` | Get notification queue item |
| API-335 | `POST /api/v1/notifications/{id}/cancel` | Cancel pending notification |
| API-356 | `POST /api/v1/notifications/{id}/retry` | Retry failed notification |
| API-357 | `POST /api/v1/notifications/{id}/process` | Process notification via stub provider |
| API-382 | `GET /api/v1/timeline` | List activity timeline entries |
| API-384 | `POST /api/v1/timeline` | Create timeline entry (internal/testing) |
| API-383 | `GET /api/v1/timeline/{id}` | Get activity timeline entry |
| API-385 | `GET /api/v1/complaints/{id}/activity-timeline` | List CAPABILITY-010 timeline for a complaint |
| API-336 | `GET /api/v1/audit` | List audit logs |
| API-337 | `GET /api/v1/audit/{id}` | Get audit log |
| API-338 | `GET /api/v1/roles` | List roles |
| API-339 | `POST /api/v1/roles` | Create role |
| API-340 | `GET /api/v1/roles/{id}` | Get role |
| API-341 | `PUT /api/v1/roles/{id}` | Update role |
| API-342 | `DELETE /api/v1/roles/{id}` | Delete role |
| API-343 | `GET /api/v1/permissions` | List permissions |
| API-344 | `POST /api/v1/permissions` | Create permission |
| API-345 | `GET /api/v1/permissions/{id}` | Get permission |
| API-346 | `PUT /api/v1/permissions/{id}` | Update permission |
| API-347 | `DELETE /api/v1/permissions/{id}` | Delete permission |
| API-348 | `GET /api/v1/roles/{id}/permissions` | List role permissions |
| API-349 | `PUT /api/v1/roles/{id}/permissions` | Replace role permissions |
| API-350 | `GET /api/v1/permissions/{id}/roles` | List permission roles |
| API-353 | `GET /api/v1/roles/{id}/users` | List role users |
| API-354 | `GET /api/v1/roles/{id}/data-scopes` | List role data scopes |
| API-355 | `PUT /api/v1/roles/{id}/data-scopes` | Replace role data scopes |
| API-210 | `GET /api/v1/reports/summary` | Complaint report summary |
| API-211 | `GET /api/v1/reports/by-status` | Complaint counts by status |
| API-212 | `GET /api/v1/reports/by-branch` | Complaint counts by branch |
| API-222 | `GET /api/v1/customers` | List customer references |
| API-223 | `GET /api/v1/branches` | List branch references |
| API-213 | `POST /api/v1/users` | Create user |
| API-214 | `GET /api/v1/users` | List users |
| API-412 | `POST /api/v1/users/me/change-password` | Change own password |
| API-414 | `PATCH /api/v1/users/me/preferred-language` | Update own preferred language |
| API-215 | `GET /api/v1/users/{id}` | Get user by id |
| API-216 | `PUT /api/v1/users/{id}` | Update user |
| API-351 | `GET /api/v1/users/{id}/roles` | List user roles |
| API-352 | `PUT /api/v1/users/{id}/roles` | Replace user roles |
| API-217 | `PATCH /api/v1/users/{id}/status` | Activate or deactivate user |
| API-413 | `POST /api/v1/users/{id}/reset-password` | Admin reset user password |

## `queue-service.v1.yaml`

| ID | Operation | Summary |
|---|---|---|
| API-360 | `POST /api/v1/queues` | Create queue |
| API-361 | `GET /api/v1/queues` | List queues by organization |
| API-362 | `GET /api/v1/queues/{queueId}` | Get queue by id |
| API-363 | `PUT /api/v1/queues/{queueId}` | Update queue |
| API-364 | `DELETE /api/v1/queues/{queueId}` | Delete queue |
| API-365 | `POST /api/v1/queues/{queueId}/tickets` | Issue queue ticket |
| API-366 | `GET /api/v1/queues/{queueId}/tickets` | List tickets for queue |
| API-367 | `GET /api/v1/tickets/{ticketId}` | Get ticket by id |
| API-368 | `PUT /api/v1/tickets/{ticketId}` | Update ticket |
| API-369 | `DELETE /api/v1/tickets/{ticketId}` | Delete ticket |
| API-370 | `POST /api/v1/queues/{queueId}/counters` | Create queue counter |
| API-371 | `GET /api/v1/queues/{queueId}/counters` | List counters for queue |
| API-372 | `PUT /api/v1/counters/{counterId}` | Update counter |
| API-373 | `DELETE /api/v1/counters/{counterId}` | Delete counter |
| API-374 | `POST /api/v1/queues/{queueId}/open` | Open queue |
| API-375 | `POST /api/v1/queues/{queueId}/close` | Close queue |
| API-376 | `POST /api/v1/queues/{queueId}/issue-ticket` | Issue ticket (operation) |
| API-377 | `POST /api/v1/queues/{queueId}/call-next` | Call next ticket |
| API-378 | `POST /api/v1/tickets/{ticketId}/recall` | Recall ticket |
| API-379 | `POST /api/v1/tickets/{ticketId}/complete` | Complete ticket |
| API-380 | `POST /api/v1/tickets/{ticketId}/skip` | Skip ticket |
| API-381 | `POST /api/v1/tickets/{ticketId}/cancel` | Cancel ticket |
