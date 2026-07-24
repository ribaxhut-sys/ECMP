# 07 API Catalog


| Field | Value |
|---|---|
| ID | API-000 |
| Version | 0.2 |
| Owner | Backend Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Katalog kontrak API ECMP (internal dan exposed), termasuk versioning dan ownership.

## Owner
- Document Owner: API Owner / Tech Lead
- Reviewers: Solution Architect, Consumers, Security

## Status
Approved (baseline) — case-service v1 terkatalog (create/get + lifecycle actions, konsolidasi Sprint-03A); API planned mengikuti Traceability.

## API Inventory

### case-service v1 — [`openapi/case-service.v1.yaml`](./openapi/case-service.v1.yaml) v1.7.0 — **NORMATIF (satu-satunya spec)**
| API ID | Method & Endpoint | Description | Auth | Status |
|---|---|---|---|---|
| API-001 | POST /v1/cases | Create case (FR-001, emit EVT-001 CaseCreated) | bearerAuth, permission `cases:create` | 🟢 Implemented (Sprint-01) |
| API-002 | GET /v1/cases/{caseId} | Get case by id (FR-002) | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-01) |
| API-003 | POST /v1/cases/{caseId}/assign | Assign/reassign case (FR-003, emit EVT-002 + EVT-003; status non-assignable = 409 INVALID_STATE) | bearerAuth, permission `cases:assign` | 🟢 Implemented (Sprint-02B) |
| API-004 | POST /v1/cases/{caseId}/status | Change case status via allowed transition (FR-004, emit EVT-003; transisi ilegal = 409 INVALID_TRANSITION) | bearerAuth, permission `cases:status` | 🟢 Implemented (Sprint-02B) |
| API-005 | GET /v1/cases | List case terpaginasi/terfilter (FR-005; filter status/priority/caseType/assigneeId; sort tetap createdAt desc) | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-03B) |
| API-006 | GET /v1/cases/{caseId}/timeline | Timeline + Audit History (projection over `audit_log`) | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-06) |
| API-007 | GET /v1/cases/{caseId}/notes | List append-only internal notes | bearerAuth, permission `cases:read` | 🟢 Implemented (Sprint-06) |
| API-008 | POST /v1/cases/{caseId}/notes | Create append-only internal note | bearerAuth, permission `cases:notes:create` | 🟢 Implemented (Sprint-06) |
| — | GET /health | Liveness check (di luar prefix /v1) | None | 🟢 Implemented |
| — | GET /health/ready | Readiness check — DB `SELECT 1` (Sprint-08) | None | 🟢 Implemented |

### complaint-service v1 — [`openapi/complaint-service.v1.yaml`](./openapi/complaint-service.v1.yaml) **1.0.0** — foundation stack (Production)
| API ID | Method & Endpoint | Description | Auth | Status |
|---|---|---|---|---|
| API-201 | POST /api/v1/complaints | Create complaint (status NEW; multi-source/target via DEC-018; legacy customerId→CUSTOMER/BRANCH; audit `complaint.create`) | bearerAuth, permission `complaints:create` | 🟢 Implemented |
| API-202 | GET /api/v1/complaints | List complaints (paginated/filtered) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-203 | GET /api/v1/complaints/{id} | Get complaint by id | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-204 | PUT /api/v1/complaints/{id} | Update complaint fields (status immutable; audit `complaint.update`) | bearerAuth, permission `complaints:update` | 🟢 Implemented |
| API-224 | PATCH /api/v1/complaints/{id}/status | Validated status transition (TASK-009; RESOLVED only via API-225; invalid → 400; timeline + audit) | bearerAuth, permission `complaints:update` | 🟢 Implemented |
| API-225 | POST /api/v1/complaints/{id}/resolution | Resolve (IN_PROGRESS→RESOLVED; mandatory resolution record; timeline `complaint.resolved`) | bearerAuth, permission `complaints:update` | 🟢 Implemented |
| API-226 | GET /api/v1/complaints/{id}/resolution | Get current resolution (404 if none) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-205 | POST /api/v1/complaints/{id}/assign | Assign/reassign (NEW→ASSIGNED; history retained; timeline written; reason required on reassign) | bearerAuth, role `SUPERVISOR` + permission `complaints:assign` | 🟢 Implemented |
| API-206 | GET /api/v1/complaints/{id}/assignments | List assignment history | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-207 | POST /api/v1/complaints/{id}/escalate | Escalate (ASSIGNED/IN_PROGRESS→ESCALATED; rejects NEW/RESOLVED/CLOSED) | bearerAuth, role `SUPERVISOR` + permission `complaints:escalate` | 🟢 Implemented |
| API-208 | GET /api/v1/complaints/{id}/escalations | List escalation history | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-301 | POST /api/v1/complaints/{id}/escalations | Escalation Request Branch→HO (status REQUESTED; IN_PROGRESS only; no Resolution; one active) | bearerAuth, permission `complaints:update` | 🟢 Implemented |
| API-302 | GET /api/v1/escalations/{id} | Get escalation detail by id | bearerAuth, permission `escalations:read` | 🟢 Implemented |
| API-303 | POST /api/v1/escalations/{id}/approve | Approve REQUESTED escalation (HO Scheduler/Admin; once only) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-304 | POST /api/v1/escalations/{id}/reject | Reject REQUESTED escalation (HO Scheduler/Admin; once only) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-305 | POST /api/v1/escalations/{id}/appointments | Book appointment on APPROVED escalation (one active; no engineer overlap) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-306 | GET /api/v1/appointments/{id} | Get appointment by id | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-307 | POST /api/v1/appointments/{id}/check-in | Customer check-in for BOOKED appointment (once only) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-308 | POST /api/v1/appointments/{id}/complete | Complete CHECKED_IN appointment (once only; result COMPLETED/PARTIALLY_COMPLETED) | bearerAuth, role HO Engineer/Admin + `appointments:complete` | 🟢 Implemented |
| API-309 | POST /api/v1/appointments/{id}/no-show | Mark BOOKED appointment as customer no-show (once only) | bearerAuth, role HO Scheduler/Admin + `escalations:review` | 🟢 Implemented |
| API-310 | POST /api/v1/complaints/{id}/final-resolution | Submit Final Resolution after COMPLETED appointment (once only; complaint stays IN_PROGRESS) | bearerAuth, role HO Engineer/Admin + `appointments:complete` | 🟢 Implemented |
| API-311 | GET /api/v1/complaints/{id}/final-resolution | Get submitted Final Resolution (404 if none) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-312 | POST /api/v1/complaints/{id}/close | Explicit Complaint Closure after Final Resolution (once; escalation stays open) | bearerAuth, role Branch Supervisor/Admin + `complaints:close` | 🟢 Implemented |
| API-313 | POST /api/v1/escalations/{id}/close | Explicit Escalation Closure after Complaint Closure (once; complaint stays CLOSED) | bearerAuth, role Head Office Admin + `escalations:close` | 🟢 Implemented |
| API-314 | GET /api/v1/complaints/{id}/sla | SLA record (immutable due dates + evaluated PENDING/COMPLETED/BREACHED statuses) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-315 | GET /api/v1/sla/policies | List SLA policies (target durations; at most one active) | bearerAuth, permission `sla:read` | 🟢 Implemented |
| API-316 | POST /api/v1/sla/policies | Create SLA policy (inactive until activated) | bearerAuth, permission `sla:manage` | 🟢 Implemented |
| API-317 | PUT /api/v1/sla/policies/{id}/activate | Activate SLA policy (sole active; future complaints only) | bearerAuth, permission `sla:manage` | 🟢 Implemented |
| API-318 | GET /api/v1/kpi/summary | KPI Foundation live aggregates (complaints + SLA completed/breached; filters) | bearerAuth, permission `kpi:read` | 🟢 Implemented |
| API-319 | GET /api/v1/dashboard/summary | Dashboard Summary orchestration (header + SLA + recent timeline ≤10) | bearerAuth, permission `dashboard:read` | 🟢 Implemented |
| API-320 | GET /api/v1/settings/public | List PUBLIC system settings | None (public) | 🟢 Implemented |
| API-321 | GET /api/v1/settings | List all system settings (PUBLIC + PROTECTED) | bearerAuth, permission `settings:read` | 🟢 Implemented |
| API-322 | PUT /api/v1/settings/{key} | Update setting value (typed validation) | bearerAuth, permission `settings:update` | 🟢 Implemented |
| API-323 | POST /api/v1/attachments | Multipart upload (objectType+objectId; SHA-256; StorageProvider) | bearerAuth, permission `attachment:create` | 🟢 Implemented |
| API-324 | GET /api/v1/attachments/{id} | Attachment metadata | bearerAuth, permission `attachment:read` | 🟢 Implemented |
| API-325 | GET /api/v1/attachments/{id}/download | Download file bytes | bearerAuth, permission `attachment:read` | 🟢 Implemented |
| API-326 | DELETE /api/v1/attachments/{id} | Soft-delete attachment | bearerAuth, permission `attachment:delete` | 🟢 Implemented |
| API-327 | GET /api/v1/notification/templates | List notification templates (optional activeOnly) | bearerAuth, permission `notification:read` | 🟢 Implemented |
| API-328 | POST /api/v1/notification/templates | Create notification template | bearerAuth, permission `notification:create` | 🟢 Implemented |
| API-329 | GET /api/v1/notification/templates/{id} | Get notification template | bearerAuth, permission `notification:read` | 🟢 Implemented |
| API-330 | PUT /api/v1/notification/templates/{id} | Update notification template | bearerAuth, permission `notification:update` | 🟢 Implemented |
| API-331 | DELETE /api/v1/notification/templates/{id} | Soft-delete template (`isActive=false`) | bearerAuth, permission `notification:delete` | 🟢 Implemented |
| API-332 | POST /api/v1/notifications | Enqueue notification (PENDING only; no send) | bearerAuth, permission `notification:create` | 🟢 Implemented |
| API-333 | GET /api/v1/notifications | List notification queue | bearerAuth, permission `notification:read` | 🟢 Implemented |
| API-334 | GET /api/v1/notifications/{id} | Get notification queue item | bearerAuth, permission `notification:read` | 🟢 Implemented |
| API-335 | POST /api/v1/notifications/{id}/cancel | Cancel PENDING queue item | bearerAuth, permission `notification:update` | 🟢 Implemented |
| API-336 | GET /api/v1/audit | List platform audit logs (filters: entityType/entityId/actorId/action/dateFrom/dateTo) | bearerAuth, permission `audit:read` | 🟢 Implemented |
| API-337 | GET /api/v1/audit/{id} | Get platform audit log by id | bearerAuth, permission `audit:read` | 🟢 Implemented |
| API-338 | GET /api/v1/roles | List roles (optional activeOnly / includeSystem) | bearerAuth, permission `role:read` | 🟢 Implemented |
| API-339 | POST /api/v1/roles | Create role (non-system; code uppercase) | bearerAuth, permission `role:create` | 🟢 Implemented |
| API-340 | GET /api/v1/roles/{id} | Get role by id | bearerAuth, permission `role:read` | 🟢 Implemented |
| API-341 | PUT /api/v1/roles/{id} | Update role (name/description/isActive; code immutable) | bearerAuth, permission `role:update` | 🟢 Implemented |
| API-342 | DELETE /api/v1/roles/{id} | Soft-delete role (system roles → 409) | bearerAuth, permission `role:delete` | 🟢 Implemented |
| API-343 | GET /api/v1/permissions | List permissions (optional activeOnly / includeSystem / module) | bearerAuth, permission `permission:read` | 🟢 Implemented |
| API-344 | POST /api/v1/permissions | Create permission (non-system; code `module:action`) | bearerAuth, permission `permission:create` | 🟢 Implemented |
| API-345 | GET /api/v1/permissions/{id} | Get permission by id | bearerAuth, permission `permission:read` | 🟢 Implemented |
| API-346 | PUT /api/v1/permissions/{id} | Update permission (name/description/isActive; code/module immutable) | bearerAuth, permission `permission:update` | 🟢 Implemented |
| API-347 | DELETE /api/v1/permissions/{id} | Soft-delete permission (system permissions → 409) | bearerAuth, permission `permission:delete` | 🟢 Implemented |
| API-348 | GET /api/v1/roles/{id}/permissions | List permissions assigned to a role | bearerAuth, permission `role_permission:read` | 🟢 Implemented |
| API-349 | PUT /api/v1/roles/{id}/permissions | Replace full permission set for a role (empty clears) | bearerAuth, permission `role_permission:update` | 🟢 Implemented |
| API-350 | GET /api/v1/permissions/{id}/roles | List roles that have a permission | bearerAuth, permission `role_permission:read` | 🟢 Implemented |
| API-351 | GET /api/v1/users/{id}/roles | List roles assigned to a user (junction) | bearerAuth, permission `user_role:read` | 🟢 Implemented |
| API-352 | PUT /api/v1/users/{id}/roles | Replace full role set for a user (empty clears) | bearerAuth, permission `user_role:update` | 🟢 Implemented |
| API-353 | GET /api/v1/roles/{id}/users | List users that have a role (junction) | bearerAuth, permission `user_role:read` | 🟢 Implemented |
| API-354 | GET /api/v1/roles/{id}/data-scopes | List data scopes for a role | bearerAuth, permission `data_scope:read` | 🟢 Implemented |
| API-355 | PUT /api/v1/roles/{id}/data-scopes | Replace full data-scope set for a role (empty clears) | bearerAuth, permission `data_scope:update` | 🟢 Implemented |

### queue-service v1 — [`openapi/queue-service.v1.yaml`](./openapi/queue-service.v1.yaml) **1.1.0** — Queue REST + Operations (TASK-064 / CAPABILITY-003)
| API ID | Method & Endpoint | Description | Auth | Status |
|---|---|---|---|---|
| API-360 | POST /api/v1/queues | Create visit-context Queue | None (Request Context ready) | 🟢 Implemented |
| API-361 | GET /api/v1/queues | List queues by organizationId | None (Request Context ready) | 🟢 Implemented |
| API-362 | GET /api/v1/queues/{queueId} | Get queue by id | None (Request Context ready) | 🟢 Implemented |
| API-363 | PUT /api/v1/queues/{queueId} | Update queue fields | None (Request Context ready) | 🟢 Implemented |
| API-364 | DELETE /api/v1/queues/{queueId} | Delete queue | None (Request Context ready) | 🟢 Implemented |
| API-365 | POST /api/v1/queues/{queueId}/tickets | Issue WAITING ticket (OPEN queue only) | None (Request Context ready) | 🟢 Implemented |
| API-366 | GET /api/v1/queues/{queueId}/tickets | List tickets for queue | None (Request Context ready) | 🟢 Implemented |
| API-367 | GET /api/v1/tickets/{ticketId} | Get ticket by id | None (Request Context ready) | 🟢 Implemented |
| API-368 | PUT /api/v1/tickets/{ticketId} | Update ticket priority/status | None (Request Context ready) | 🟢 Implemented |
| API-369 | DELETE /api/v1/tickets/{ticketId} | Delete ticket | None (Request Context ready) | 🟢 Implemented |
| API-370 | POST /api/v1/queues/{queueId}/counters | Create counter | None (Request Context ready) | 🟢 Implemented |
| API-371 | GET /api/v1/queues/{queueId}/counters | List counters for queue | None (Request Context ready) | 🟢 Implemented |
| API-372 | PUT /api/v1/counters/{counterId} | Update counter | None (Request Context ready) | 🟢 Implemented |
| API-373 | DELETE /api/v1/counters/{counterId} | Delete counter | None (Request Context ready) | 🟢 Implemented |
| API-374 | POST /api/v1/queues/{queueId}/open | Open queue (operational) | None (Request Context ready) | 🟢 Implemented |
| API-375 | POST /api/v1/queues/{queueId}/close | Close queue (operational) | None (Request Context ready) | 🟢 Implemented |
| API-376 | POST /api/v1/queues/{queueId}/issue-ticket | Issue ticket (Domain number A001…) | None (Request Context ready) | 🟢 Implemented |
| API-377 | POST /api/v1/queues/{queueId}/call-next | Call next WAITING → CALLED | None (Request Context ready) | 🟢 Implemented |
| API-378 | POST /api/v1/tickets/{ticketId}/recall | Recall CALLED/SERVING ticket | None (Request Context ready) | 🟢 Implemented |
| API-379 | POST /api/v1/tickets/{ticketId}/complete | Complete ticket | None (Request Context ready) | 🟢 Implemented |
| API-380 | POST /api/v1/tickets/{ticketId}/skip | Skip ticket | None (Request Context ready) | 🟢 Implemented |
| API-381 | POST /api/v1/tickets/{ticketId}/cancel | Cancel ticket | None (Request Context ready) | 🟢 Implemented |

### complaint-domain-service v1 — [`openapi/complaint-domain-service.v1.yaml`](./openapi/complaint-domain-service.v1.yaml) **1.4.0** — Complaint Domain Foundation + Processing + Assignment + Escalation + SLA (CAPABILITY-004…008)
| API ID | Method & Endpoint | Description | Auth | Status |
|---|---|---|---|---|
| API-390 | POST /api/v1/complaints | Create visit-context Complaint (status OPEN; queueTicketId required) | None (Request Context ready) | 🟢 Implemented |
| API-391 | GET /api/v1/complaints | List complaints by organizationId | None (Request Context ready) | 🟢 Implemented |
| API-392 | GET /api/v1/complaints/{complaintId} | Get complaint by id | None (Request Context ready) | 🟢 Implemented |
| API-393 | PUT /api/v1/complaints/{complaintId} | Update fields; lifecycle OPEN→IN_PROGRESS→RESOLVED→CLOSED (+ reopen) | None (Request Context ready) | 🟢 Implemented |
| API-394 | DELETE /api/v1/complaints/{complaintId} | Hard-delete complaint | None (Request Context ready) | 🟢 Implemented |
| API-395 | GET /api/v1/tickets/{ticketId}/complaints | List complaints for a queue ticket | None (Request Context ready) | 🟢 Implemented |
| API-396 | POST /api/v1/tickets/{ticketId}/complaints | Create complaint bound to ticket path | None (Request Context ready) | 🟢 Implemented |
| API-397 | POST /api/v1/complaints/{complaintId}/start | Start processing OPEN→IN_PROGRESS | None (Request Context ready) | 🟢 Implemented |
| API-398 | POST /api/v1/complaints/{complaintId}/resolve | Resolve IN_PROGRESS→RESOLVED (+ Resolution VO) | None (Request Context ready) | 🟢 Implemented |
| API-399 | POST /api/v1/complaints/{complaintId}/close | Close RESOLVED→CLOSED (resolution immutable; completes active SLA) | None (Request Context ready) | 🟢 Implemented |
| API-400 | POST /api/v1/complaints/{complaintId}/reopen | Reopen RESOLVED→IN_PROGRESS | None (Request Context ready) | 🟢 Implemented |
| API-401 | POST /api/v1/complaints/{complaintId}/assign | First active Assignment (USER); rejects if active exists | None (Request Context ready) | 🟢 Implemented |
| API-402 | POST /api/v1/complaints/{complaintId}/reassign | Release active + append new Assignment | None (Request Context ready) | 🟢 Implemented |
| API-403 | POST /api/v1/complaints/{complaintId}/unassign | Release active Assignment | None (Request Context ready) | 🟢 Implemented |
| API-404 | GET /api/v1/complaints/{complaintId}/assignment | Current active Assignment | None (Request Context ready) | 🟢 Implemented |
| API-405 | GET /api/v1/complaints/{complaintId}/assignments | Append-only Assignment history | None (Request Context ready) | 🟢 Implemented |
| API-406 | POST /api/v1/complaints/{complaintId}/escalate | Append current Escalation (level must increase) | None (Request Context ready) | 🟢 Implemented |
| API-407 | GET /api/v1/complaints/{complaintId}/escalation | Current Escalation | None (Request Context ready) | 🟢 Implemented |
| API-408 | GET /api/v1/complaints/{complaintId}/escalations | Append-only Escalation history | None (Request Context ready) | 🟢 Implemented |
| API-409 | POST /api/v1/complaints/{complaintId}/sla/start | Start ComplaintSLA from SLAPolicy (default when omitted) | None (Request Context ready) | 🟢 Implemented |
| API-410 | POST /api/v1/complaints/{complaintId}/sla/complete | Complete active ComplaintSLA | None (Request Context ready) | 🟢 Implemented |
| API-411 | POST /api/v1/complaints/{complaintId}/sla/recalculate | Manual breach detection + remaining time | None (Request Context ready) | 🟢 Implemented |
| API-412 | GET /api/v1/complaints/{complaintId}/sla | Get active (or latest) ComplaintSLA | None (Request Context ready) | 🟢 Implemented |

| API-209 | GET /api/v1/complaints/{id}/timeline | Immutable timeline from `complaint_timelines` (includes SLA `sla.*.completed` / `sla.*.breached` SYSTEM events) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-210 | GET /api/v1/reports/summary | Report summary (COUNT; optional branchId/dateFrom/dateTo) | bearerAuth, permission `reports:read` | 🟢 Implemented |
| API-211 | GET /api/v1/reports/by-status | Counts by ComplaintStatus (GROUP BY) | bearerAuth, permission `reports:read` | 🟢 Implemented |
| API-212 | GET /api/v1/reports/by-branch | Counts by branch (GROUP BY; total DESC) | bearerAuth, permission `reports:read` | 🟢 Implemented |
| API-213 | POST /api/v1/users | Create user (unique username/email; bcrypt password; default isActive=true) | bearerAuth, permission `users:create` | 🟢 Implemented |
| API-214 | GET /api/v1/users | List users (paginated) | bearerAuth, permission `users:read` | 🟢 Implemented |
| API-215 | GET /api/v1/users/{id} | Get user by id | bearerAuth, permission `users:read` | 🟢 Implemented |
| API-216 | PUT /api/v1/users/{id} | Update user (password re-hashed when provided; hash never exposed) | bearerAuth, permission `users:update` | 🟢 Implemented |
| API-217 | PATCH /api/v1/users/{id}/status | Soft activate/deactivate (`isActive`) | bearerAuth, permission `users:update` | 🟢 Implemented |
| API-218 | POST /api/v1/auth/login | Login (bcrypt; JWT access 15m; HttpOnly refresh cookie 7d; audit `auth.login`) | None (public) | 🟢 Implemented |
| API-219 | POST /api/v1/auth/refresh | Rotate refresh cookie; issue new access token (audit `auth.refresh`) | Refresh cookie | 🟢 Implemented |
| API-220 | POST /api/v1/auth/logout | Revoke refresh token + clear cookie (audit `auth.logout`) | Refresh cookie | 🟢 Implemented |
| API-221 | GET /api/v1/auth/me | Current user + roles/permissions | bearerAuth | 🟢 Implemented |
| API-222 | GET /api/v1/customers | List local customer references (paginated; optional `q`) | bearerAuth, permission `complaints:read` | 🟢 Implemented |
| API-223 | GET /api/v1/branches | List active branch references (paginated; optional `q`) | bearerAuth, permission `complaints:read` | 🟢 Implemented |

> **2026-07-24 (CAPABILITY-008 Complaint SLA Foundation):**
> complaint-domain-service v1.4 — API-409…412 start/complete/recalculate/get SLA.
> ComplaintSLA child entity + SLAPolicy; at most one active SLA per Complaint;
> due_at = started_at + target_minutes; remaining + breach detection; close
> completes active SLA. Tables `complaint_sla_policies` + `complaint_case_slas`
> (CA BC; legacy `sla_policies` / `sla_records` unchanged). No Scheduler /
> Notification / Escalation trigger / Timeline / Dashboard / Auth.
>
> **2026-07-24 (CAPABILITY-007 Complaint Escalation Foundation):**
> complaint-domain-service v1.3 — API-406…408 escalate + current/history.
> Escalation child entity; at most one current per Complaint; append-only
> history; level must strictly increase; does not change Assignment or
> lifecycle status. Table `complaint_case_escalations` (CA BC; legacy
> `complaint_escalations` unchanged). No SLA / Scheduler / Notification /
> Timeline / Auth.
>
> **2026-07-24 (CAPABILITY-006 Complaint Assignment Foundation):**
> complaint-domain-service v1.2 — API-401…405 assign/reassign/unassign +
> current/history. Assignment child entity; at most one active per Complaint;
> append-only history; does not change lifecycle status. Table
> `complaint_case_assignments` (CA BC; legacy `complaint_assignments` unchanged).
> No Escalation / SLA / Notification / Timeline / Auth.
>
> **2026-07-24 (CAPABILITY-005 Complaint Processing):**
> complaint-domain-service v1.1 — API-397…400 start/resolve/close/reopen.
> Resolution VO; domain lifecycle reopen RESOLVED→IN_PROGRESS; resolution
> immutable after CLOSED. No Timeline / Escalation / SLA / Auth.
>
> **2026-07-24 (CAPABILITY-004 Complaint Domain Foundation):**
> complaint-domain-service v1 — API-390…396 Complaint CRUD + ticket-nested
> list/create. Clean Architecture BC (`app.modules.complaint`); table
> `complaint_cases`; lifecycle OPEN→IN_PROGRESS→RESOLVED→CLOSED. No Queue
> domain coupling (queueTicketId only). No Workflow / Auth / SLA.
>
> **2026-07-24 (CAPABILITY-003 Queue Operations):** queue-service v1.1 —
> API-374…381 open/close/issue-ticket/call-next/recall/complete/skip/cancel.
> Domain ticket numbers (A001…). Display / Kiosk / Voice / Auth out of scope.
>
> **2026-07-24 (TASK-064 Queue REST API Foundation):** queue-service
> v1 — API-360…373 Queue / QueueTicket / QueueCounter CRUD. Controllers
> → Application → Repository Interface → SQLAlchemy. No auth enforcement
> (Request Context ready). No Call Next / Display / Kiosk / Redis.
>
> **2026-07-24 (TASK-041 Permission Cache Optimization):** Refactored
> process-local IAM cache into `IamCacheService` (permissions /
> data_scopes / principals) with entry metadata, metrics, and unified
> `invalidate_iam_user` / `invalidate_iam_all`. No Authorization API,
> resolver, or Login/JWT changes; no Redis.
>
> **2026-07-24 (TASK-040 Authorization Middleware Refinement):** Unified
> AuthZ pipeline (Authentication → Permission Resolver → Permission Check
> → optional Data Scope Resolver/Check → Endpoint) under
> `app/core/authorization/` with facade `app/core/auth.py`. Helpers
> `require_permissions` / `require_roles` / `require_data_scope` /
> `resolve_effective_scope` unchanged for routers. Error envelope:
> 401 `UNAUTHENTICATED`, 403 `FORBIDDEN` (permission), 403
> `DATA_SCOPE_DENIED` (scope). No public API path changes; no auto
> domain filtering; IAM cache reused.
>
> **2026-07-24 (TASK-039 Data Scope Enforcement):** Authorization Layer
> adds `DataScopeResolver` (User→UserRole→Role→DataScope→EffectiveScope)
> with shared IAM cache (5 min TTL). Public helpers:
> `resolve_effective_scope`, `require_data_scope`. Endpoints opt in —
> Complaint/Settings/Attachment/Notification/Audit were not auto-wired.
> Login/JWT and Permission Resolver unchanged.
>
> **2026-07-24 (TASK-038 Dynamic Permission Resolver):** Authorization
> Engine now resolves permissions via User → UserRole → Role →
> RolePermission → Permission (`permission_resolver.py` + 5-minute
> in-memory `permission_cache.py`). Login JWT carries `sub` + `roles`
> only; `/auth/me` returns permissions from the resolver. Migration
> `0025_permission_resolver` seeds runtime permission codes, role
> matrix, and backfills `user_roles`. Out of scope: Data Scope
> filtering (TASK-039+).
>
> **2026-07-24 (TASK-037 Data Scope Foundation):** complaint-service —
> API-354 get role data scopes / API-355 replace role data scopes.
> Module `app/modules/iam/data_scope`. Table `data_scopes` (migration
> `0024_data_scopes`) with unique `(role_id, scope_type, scope_value)`.
> Types: GLOBAL / ORGANIZATION / BRANCH / SELF / CUSTOM. PUT is full
> replace (empty clears). Audit `role.data_scopes.updated`. Permissions
> `data_scope:read|update` seeded. Out of scope: Authorization Engine
> integration, automatic endpoint filtering, login/JWT changes.
>
> **2026-07-24 (TASK-036 User-Role Assignment):** complaint-service —
> API-351 get user roles / API-352 replace user roles /
> API-353 get role users. Module `app/modules/iam/user_role`. Junction
> table `user_roles` (migration `0023_user_roles`) with CASCADE from
> users/roles; unique `(user_id, role_id)`. PUT is full replace (empty
> clears). System roles may be assigned. Does not mutate `users.role_id`.
> Audit `user.roles.updated`. Permissions `user_role:read|update` seeded.
> Out of scope: Authorization Engine rewrite, Data Scope (TASK-037+).
>
> **2026-07-24 (TASK-035 Role-Permission Matrix):** complaint-service —
> API-348 get role permissions / API-349 replace role permissions /
> API-350 get permission roles. Module `app/modules/iam/role_permission`.
> Junction table `role_permissions` (migration `0022_role_permissions`)
> with CASCADE from roles/permissions; unique `(role_id, permission_id)`.
> PUT is full replace (empty clears). System roles may be updated.
> Audit `role.permissions.updated`. Permissions
> `role_permission:read|update` seeded. Out of scope: Authorization
> Engine rewrite, user↔role assignment (TASK-036+).
>
> **2026-07-24 (TASK-034 Permission Management):** complaint-service —
> API-343 list / API-344 create / API-345 get / API-346 update /
> API-347 soft-delete. Module `app/modules/iam/permission`. New
> `permissions` table (migration `0021_permissions`) with seed catalog
> (`complaint:*`, `assignment:*`, `appointment:*`, `resolution:*`,
> `escalation:*`, `dashboard:read`, `settings:*`, `attachment:*`,
> `notification:*`, `audit:read`, `role:*`, `permission:*`) as system.
> Audit hooks CREATE/UPDATE/DELETE (`permission.created|updated|deleted`).
> Permissions `permission:read|create|update|delete`. Out of scope:
> role↔permission matrix, Authorization Engine rewrite (TASK-035+).
>
> **2026-07-24 (TASK-033 Role Management):** complaint-service —
> API-338 list / API-339 create / API-340 get / API-341 update /
> API-342 soft-delete. Module `app/modules/iam/role`. Evolves existing
> `roles` table (migration `0020_roles`: `is_system`, widen code/name,
> seed SUPER_ADMIN/ADMIN/SUPERVISOR/AGENT/VIEWER as system). Audit hooks
> CREATE/UPDATE/DELETE. Permissions `role:read|create|update|delete`.
> Out of scope: user↔role assignment, permission matrix (TASK-034+).
>
> **2026-07-24 (TASK-031 Audit Log):** complaint-service —
> API-336 list / API-337 get. Module `app/modules/audit`. Platform table
> `audit_logs` (migration `0019_audit`; legacy rows moved to
> `audit_logs_legacy`). Synchronous `AuditService.log/get/list`. Secrets
> redacted. Hooks: Settings update, Notification Template CRUD, Attachment
> delete. Permission `audit:read`. Out of scope: Kafka/Rabbit/worker/
> realtime/search/dashboard. Not Complaint Timeline.
>
> **2026-07-24 (TASK-030 Notification Foundation):** complaint-service —
> API-327–331 template CRUD / API-332 enqueue / API-333–334 queue read /
> API-335 cancel. Module `app/modules/notification`. Tables
> `notification_templates` + `notification_queue` (migration
> `0018_notification`). Settings seed: `notification.enabled`,
> `notification.default.channel`, `notification.max.retry`. Soft-delete
> templates via `is_active=false` (no `deleted_at` on template contract).
> Permissions `notification:read|create|update|delete`. Out of scope:
> SMTP, WhatsApp, FCM, scheduler, retry worker, SEND endpoint.
>
> **2026-07-23 (TASK-029 Attachment Management):** complaint-service —
> API-323 upload / API-324 metadata / API-325 download / API-326 soft-delete.
> Module `app/modules/attachment`. Polymorphic `attachments` table
> (`object_type` + `object_id`). Local `StorageProvider` via settings
> `storage.provider`, `storage.root.path`, `storage.max.upload.mb`,
> `storage.allowed.mime` (migration `0017_attachments`). Permissions
> `attachment:create` / `attachment:read` / `attachment:delete`.
> Out of scope: virus scan, S3/MinIO, hard delete, Complaint domain coupling.
>
> **2026-07-24 (TASK-043 Complaint Routing Foundation):**
> Central `ComplaintRoutingService` resolves immutable `ComplaintRoute`
> (receiverType/receiverId/assignmentContext/routingReason). Supported
> pairs: CUSTOMER→BRANCH, BRANCH→HEAD_OFFICE, HEAD_OFFICE→BRANCH,
> SYSTEM→HEAD_OFFICE. Invalid pairs → 400. Assignment Engine unchanged.
> See `20 Domain Architecture/ECMF/COMPLAINT_ROUTING.md`.
>
> **2026-07-24 (TASK-042 / DEC-018 Multi-Source Multi-Target Complaint):**
> complaint-service — API-201 create accepts optional `sourceType` /
> `sourceId` / `targetType` / `targetId` (VARCHAR enums). Legacy
> `customerId` (+ optional `branchId`) remains and implies CUSTOMER→BRANCH.
> Single `complaints` table; no subtype entities. Assignment/Timeline/
> Resolution/Appointment/Escalation/AuthZ unchanged.
>
> **2026-07-23 (TASK-028 System Settings):** complaint-service —
> API-320 public list / API-321 full list / API-322 update by key.
> Module `app/modules/settings`. Table `settings` with typed values
> (STRING/INTEGER/BOOLEAN/JSON/URL/EMAIL) and PUBLIC/PROTECTED visibility.
> Seeded defaults include company.*, app.*, dashboard.recent.limit,
> complaint.number.prefix. Permissions `settings:read` / `settings:update`.
> Out of scope: Attachment, Notification, Audit Log UI.
>
> **2026-07-23 (TASK-027 Dashboard API / DEC-016):** complaint-service —
> API-319 `GET /api/v1/dashboard/summary`. Module `app/modules/dashboard`.
> Orchestration only — composes KPI (header + SLA), Timeline (≤10 recent
> events), and Complaint (numbers). No DB queries in dashboard, no KPI
> calculation, no charts/caching/websocket. Permission `dashboard:read`.
>
> **2026-07-23 (TASK-026 KPI Foundation / DEC-015):** complaint-service —
> API-318 `GET /api/v1/kpi/summary`. Module `app/modules/kpi`. Live
> aggregates from complaints + `sla_records` (no KPI tables / migration /
> scheduler). Permission `kpi:read`. Filters: dateFrom/dateTo, branchId,
> category, priority. Dashboard KPI Summary Card (cards only).
>
> **2026-07-23 (TASK-025 SLA Timeline Integration / DEC-014):** complaint-service —
> On SLA status change to COMPLETED or BREACHED, append SYSTEM-actor events
> to `complaint_timelines` (`sla.<stage>.completed` / `sla.<stage>.breached`).
> No duplicate events on idempotent re-evaluation. Reuses API-209; no new
> endpoints. No notifications / scheduler / KPI.
>
> **2026-07-23 (TASK-024 SLA Breach Detection / DEC-013):** complaint-service —
> Evaluate SLA statuses from immutable `*_due_at` snapshots and completion
> facts (`PENDING` / `COMPLETED` / `BREACHED`). Triggers: complaint create,
> assignment, appointment complete, resolution finalize, escalation close,
> complaint close, and API-314 read. Never re-reads policy; never rewrites
> deadlines. No scheduler / cron / notifications / KPI / dashboard.
>
> **2026-07-23 (TASK-023 SLA Deadline Calculator / DEC-012):** complaint-service —
> On complaint create, evaluate the active SLA policy once and persist
> immutable due-at snapshots on `sla_records` (assignment / appointment /
> resolution / escalation / overall). Reject create when no active policy.
> Statuses remain `PENDING`. Existing rows never recalculated. No breach /
> countdown / scheduler / notification / dashboard / KPI. API-314 surfaces
> populated due dates; no new public endpoints.
>
> **2026-07-23 (TASK-022 SLA Policy & Configuration):** complaint-service —
> API-315 list / API-316 create / API-317 activate. Table `sla_policies`
> (migration `0015_sla_policy`). At most one active policy. New complaints
> use the active policy for deadline snapshots (TASK-023). Existing
> complaints are not recalculated. No countdown / breach / scheduler /
> KPI / dashboard.
>
> **2026-07-23 (TASK-021 SLA Domain Foundation):** complaint-service —
> API-314 `GET /api/v1/complaints/{id}/sla`. Module `app/modules/sla`.
> Migration `0014_sla_foundation` (`sla_records`, 1:1 complaint).
> Statuses default `PENDING`; deadlines NULL. No timers / calculations /
> breach detection / dashboard / KPI / notifications.
>
> **2026-07-23 (TASK-020 Escalation Closure):** complaint-service —
> API-313 `POST /api/v1/escalations/{id}/close` after Complaint Closure.
> Timeline `escalation.closed`. Migration `0013_escalation_closure`.
> Escalation → `CLOSED`; complaint remains `CLOSED`. Reopen / SLA /
> notification / approval / auto-close out of scope.
>
> **2026-07-23 (TASK-019 Complaint Closure):** complaint-service —
> API-312 `POST .../close` after Final Resolution. Timeline
> `complaint.closed`. Migration `0012_complaint_closure`. Complaint →
> `CLOSED`; escalation remains unchanged until API-313. Reopen /
> notification / SLA / auto-close out of scope.
>
> **2026-07-23 (TASK-018 Final Resolution / DEC-011):** complaint-service —
> API-310 submit Final Resolution after `COMPLETED` appointment; API-311 GET.
> Timeline `complaint.final_resolution_submitted`. Migration
> `0011_final_resolution`. Complaint stays `IN_PROGRESS`; escalation stays
> `APPROVED`. Closure / approval / notification / SLA out of scope.
>
> **2026-07-23 (TASK-017 Customer No Show / DEC-010):** complaint-service —
> API-309 no-show for `BOOKED` appointments → `NO_SHOW`. Timeline
> `complaint.appointment_no_show`. Migration `0010_appointment_no_show`.
> Does not auto-close complaint or escalation. Reschedule / rebooking /
> notification / SLA out of scope.
>
> **2026-07-23 (TASK-016 Appointment Completion / DEC-009):** complaint-service —
> API-308 complete for `CHECKED_IN` appointments → `COMPLETED`. Timeline
> `complaint.appointment_completed`. Migration `0009_appointment_completion`.
> Does not auto-close complaint or escalation. No-show / notification /
> survey / SLA / calendar out of scope.
>
> **2026-07-23 (TASK-015 Customer Check-In / DEC-008):** complaint-service —
> API-307 check-in for `BOOKED` appointments → `CHECKED_IN`. Timeline
> `complaint.appointment_checked_in`. Migration `0008_appointment_checkin`.
> No-show / notification out of scope.
>
> **2026-07-23 (TASK-014 Appointment Booking / DEC-007):** complaint-service —
> API-305 book appointment on `APPROVED` escalation + API-306 get by id.
> Timeline `complaint.appointment_booked`. Migration `0007_appointments`.
> Status `BOOKED` only; calendar/slots/check-in/completion/notification out of
> scope. Escalation GET embeds optional `activeAppointment`.
>
> **2026-07-23 (TASK-012 Escalation Review):** complaint-service — API-303
> approve + API-304 reject for `REQUESTED` escalations. Permission
> `escalations:review` for HO Scheduler / Admin. Timeline
> `complaint.escalation_approved` / `complaint.escalation_rejected`.
> Migration `0006_escalation_review`. Appointment booking delivered in TASK-014.
>
> **2026-07-23 (TASK-011 Escalation Request):** complaint-service — API-301
> (`POST /api/v1/complaints/{id}/escalations`) + API-302
> (`GET /api/v1/escalations/{id}`). Branch → HO request with status
> `REQUESTED`; timeline `complaint.escalation_requested`. Review/Approve
> out of scope. Migration `0005_complaint_escalations` extends
> `complaint_escalations` with request fields.
>
> **2026-07-23 (TASK-010 Complaint Resolution):** complaint-service — API-225
> (`POST /api/v1/complaints/{id}/resolution`) + API-226 GET current resolution.
> `IN_PROGRESS`→`RESOLVED` only via resolution form/endpoint; PATCH status
> matrix no longer allows direct RESOLVED.
>
> **2026-07-23 (TASK-009):** complaint-service — API-224 status transition
> (`PATCH /api/v1/complaints/{id}/status`) with validated matrix; `PENDING`
> added to ComplaintStatus. NEW→ASSIGNED remains Assign (API-205).
>
> **2026-07-23 (TASK-008):** complaint-service — timeline UI uses API-209
> (`GET /api/v1/complaints/{id}/timeline`) read-only. Sort is newest-first;
> `actorName` added for display. Create writes `complaint.created`; priority
> update writes `complaint.updated` with `changeType=PRIORITY_CHANGED`.
>
> **2026-07-23 (TASK-007):** complaint-service — assignee UI uses existing API-205
> (`POST /api/v1/complaints/{id}/assign`) + API-214 user list (`isActive=true`) as
> reference picker. User schema adds optional `roleCode`/`roleName` so assignee
> select shows Name + Role without exposing UUIDs.
>
> **2026-07-23 (TASK-005):** complaint-service — added API-223 branch reference list for Create Complaint `branchId` selection (active `branches` rows; no UUID typing).
>
> **2026-07-23 (TASK-004):** complaint-service — added API-222 local customer reference list for Create Complaint selection (local `customers` cache; not Customer Master SoR / not API-010).
>
> **2026-07-23 (TASK-016 / Production Go-Live):** complaint-service OpenAPI `info.version` set to **1.0.0** (Production). No path/schema additions; go-live only.
>
> **2026-07-23 (TASK-014 / RC1):** complaint-service OpenAPI `info.version` set to **1.0.0-rc1** (application Release Candidate). No path/schema additions; code freeze active.
>
> **2026-07-23 (TASK-010):** complaint-service contract baseline — production authentication API-218..API-221 (login/refresh/logout/me; refresh rotation; HttpOnly Secure SameSite=Lax cookie). Prior catalog label was v1.7.0.
>
> **2026-07-23 (TASK-008):** complaint-service — added user management API-213..API-217.
>
> **2026-07-23 (TASK-007 reporting slice):** complaint-service v1.5.0 — added reporting foundation API-210..API-212.
>
> **2026-07-23 (TASK-006):** complaint-service v1.4.0 — added API-209 Timeline read (`GET /api/v1/complaints/{id}/timeline`).
>
> **2026-07-23 (CR-001 stabilization):** complaint-service bumped to v1.3.0 — removed `REGISTERED`/`PENDING_REVIEW`/`REOPENED`; status SoT is `ComplaintStatus` (`NEW`, `ASSIGNED`, `IN_PROGRESS`, `ESCALATED`, `RESOLVED`, `CLOSED`); timeline events standardized; response/error envelopes aligned. No path or auth contract changes.
>
> **2026-07-22 (Sprint-03A, DEC-006 D6/U-6):** `case-actions.v1.yaml` dikonsolidasikan ke `case-service.v1.yaml` — kini satu-satunya spec normatif untuk case-service. `case-actions.v1.yaml` masih ada di disk tetapi ditandai `x-status: superseded` (paths kosong) dan tidak lagi dibaca oleh tooling/test; dipertahankan hanya agar tautan lama tidak 404. Tidak ada perubahan perilaku API atau payload event — murni sinkronisasi katalog terhadap runtime yang sudah berjalan sejak Sprint-02B.
>
> **2026-07-22 (Sprint-03B):** API-005 (list cases) di-freeze dan diimplementasikan; merged ke `case-service.v1.yaml` v1.5.0 dari draft `dashboard-queues.v1.draft.yaml`. Sort dikunci `createdAt` descending (keputusan CTO, design review Sprint-03B) — sort dapat dikonfigurasi eksplisit di luar scope versi ini. API-010 (Customer 360 read) **ditunda** — lihat `implementation/backend/ACR_SPRINT02B.md` ACR-002: draft/FRD-003 mengasumsikan profil pelanggan nyata, bertentangan dengan larangan fabrikasi data di INT-001 untuk mode stub.
>
> **2026-07-23 (foundation TASK-003):** complaint-service v1.0.0 added for the root `backend/` stack (`/api/v1/complaints`). Parallel to case-service; assignment/escalation/timeline remain out of scope.

### Planned
| API ID | Method & Endpoint | Description | Draft spec | Status |
|---|---|---|---|---|
| API-010 | GET /v1/customers/{customerId} | Customer reference read (CRM) — **ditunda, lihat ACR-002** | [`drafts/customer-read.v1.draft.yaml`](./openapi/drafts/customer-read.v1.draft.yaml) | Deferred |
| API-040 | GET /v1/dashboard/queues | Dashboard queues (Sprint-03) | [`drafts/dashboard-queues.v1.draft.yaml`](./openapi/drafts/dashboard-queues.v1.draft.yaml) | Planned |

> **Label gate:** G1 = gate masuk Sprint-02 (lihat `13 Test Strategy`); "Sprint-02 / gate G1" merujuk hal yang sama.

### Candidate (FRD-007 Administration — belum ada draft spec)
Kandidat API Administration/Core Platform **API-050..API-059** (admin-config: reference data, workflow/SLA config, calendars, escalation, templates, change-requests, versions, settings, audit-config) dan **API-060..API-062** (Core Platform SoT: users, roles, role-permission) didefinisikan di [`../03 Functional Requirements/ECMP_FRD_Administration_v0.1.md`](../03%20Functional%20Requirements/ECMP_FRD_Administration_v0.1.md) §8. Status **Candidate** — belum boleh dibuat draft normatif sebelum FRD-007 DoR; draft OpenAPI wajib dibuat di `openapi/drafts/` sebelum implementasi (contract-first).

### Konvensi `openapi/drafts/`
File di `openapi/drafts/` (penamaan `<nama>.v<major>.draft.yaml`, `info.version: *-draft`, `x-status: draft`) adalah **skeleton non-normatif**: bahan review contract-first untuk memenuhi entry gate G1 ("OpenAPI merged sebelum kode"). Draft menjadi normatif **hanya setelah** direview dan di-merge ke spec berversi (mis. `case-service.v1.yaml`) di gate G1. Katalog/generator hanya mencakup spec normatif — draft tidak dihitung sebagai kontrak yang boleh diimplementasikan.

## Minimum Contents (v1)
- [x] API inventory — 1 service (case-service v1), lihat tabel di atas
- [x] OpenAPI/Swagger specs — [`openapi/case-service.v1.yaml`](./openapi/case-service.v1.yaml)
- [x] Auth requirements per API — via `bearerAuth` (JWT; slice phase static token DEV/CI, ADR-007), 401/403 dibedakan
- [x] Error model standard — `Error{code, message, details?}` di semua response error
- [x] Versioning & deprecation policy — URL prefix `/v1`, breaking change bump prefix (ADR-006)
- [x] Pagination standard — dirujuk ke `../21 Technical Standards` (berlaku saat ada endpoint list)
- [x] SLAs for API availability/latency — baseline DEC-005: [`NFR Specification`](../04%20Solution%20Architecture/ECMP_NFR_Specification_v0.1.md) (availability 99.5%, p95 baca <300ms / tulis <800ms) dan [`SLA Matrix`](../11%20SLA%20and%20KPI%20Matrix/ECMP_SLA_Matrix_v0.1.md)

## Template Fields (per API)
- API Name
- Domain
- Endpoint
- Method
- Description
- AuthN/AuthZ
- Request/Response schema
- Owner
- Version
- Status
- Consumers

## Naming
File OpenAPI aktual: `<service>.v<major>.yaml` (contoh: `case-service.v1.yaml`) — versi major di nama file mengikuti prefix URL `/v<major>` per ADR-006; versi minor/patch dicatat di field `info.version` dalam spec.

## Boundary Note
- API Catalog = kontrak interface
- Integration Catalog = mapping ke sistem eksternal / pola integrasi

## Related
- `../08 Event Catalog`
- `../09 Integration Catalog`
- `../04 Solution Architecture`
