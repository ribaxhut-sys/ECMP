# Complaint REST API (CAPABILITY-004…008)

Normative OpenAPI: `07 API Catalog/openapi/complaint-domain-service.v1.yaml`

| API ID | Method | Path |
|---|---|---|
| API-390 | POST | `/api/v1/complaints` |
| API-391 | GET | `/api/v1/complaints?organizationId=` |
| API-392 | GET | `/api/v1/complaints/{complaintId}` |
| API-393 | PUT | `/api/v1/complaints/{complaintId}` |
| API-394 | DELETE | `/api/v1/complaints/{complaintId}` |
| API-395 | GET | `/api/v1/tickets/{ticketId}/complaints` |
| API-396 | POST | `/api/v1/tickets/{ticketId}/complaints` |
| API-397 | POST | `/api/v1/complaints/{complaintId}/start` |
| API-398 | POST | `/api/v1/complaints/{complaintId}/resolve` |
| API-399 | POST | `/api/v1/complaints/{complaintId}/close` |
| API-400 | POST | `/api/v1/complaints/{complaintId}/reopen` |
| API-401 | POST | `/api/v1/complaints/{complaintId}/assign` |
| API-402 | POST | `/api/v1/complaints/{complaintId}/reassign` |
| API-403 | POST | `/api/v1/complaints/{complaintId}/unassign` |
| API-404 | GET | `/api/v1/complaints/{complaintId}/assignment` |
| API-405 | GET | `/api/v1/complaints/{complaintId}/assignments` |
| API-406 | POST | `/api/v1/complaints/{complaintId}/escalate` |
| API-407 | GET | `/api/v1/complaints/{complaintId}/escalation` |
| API-408 | GET | `/api/v1/complaints/{complaintId}/escalations` |
| API-409 | POST | `/api/v1/complaints/{complaintId}/sla/start` |
| API-410 | POST | `/api/v1/complaints/{complaintId}/sla/complete` |
| API-411 | POST | `/api/v1/complaints/{complaintId}/sla/recalculate` |
| API-412 | GET | `/api/v1/complaints/{complaintId}/sla` |

## Mounting

| Router | Routes | Use |
|---|---|---|
| `complaint_api_router` | API-395…396 | Production (no path clash with legacy ECMF) |
| `complaint_foundation_router` | API-390…412 | Isolated tests + future cutover |

## Envelope

Success: `{ "data": ... }` (`DataResponse`)

Delete: `204 No Content`

Errors: `{ "code", "message", "details?" }`

## Request DTOs (processing)

| Request | Fields |
|---|---|
| `ResolveRequest` | `summary` (required), `resolvedBy` (required) |
| `CloseRequest` | optional empty body |
| `ReopenRequest` | `reason` (optional; not persisted) |

## Request DTOs (assignment)

| Request | Fields |
|---|---|
| `AssignRequest` | `assigneeType`, `assigneeId`, `assignedBy` |
| `ReassignRequest` | `assigneeType`, `assigneeId`, `assignedBy` |
| `UnassignRequest` | `releasedBy`, `reason?` |

## Request DTOs (escalation)

| Request | Fields |
|---|---|
| `EscalateRequest` | `level`, `reason`, `escalatedBy` |

## Request DTOs (SLA)

| Request | Fields |
|---|---|
| `StartSLARequest` | `policyId?` (default policy when omitted) |
| `RecalculateRequest` | `currentTime` (required) |

## Response DTO (`ComplaintResponse`)

`complaintId` · `queueTicketId` · `category` · `title` · `description` ·
`priority` · `status` · `createdAt` · `updatedAt` · `resolution?`

`resolution`: `{ summary, resolvedBy, resolvedAt }` or `null`.

## Response DTO (`AssignmentResponse`)

`assignmentId` · `complaintId` · `assigneeType` · `assigneeId` ·
`assignedAt` · `assignedBy` · `releasedAt?` · `isActive`

## Response DTO (`EscalationResponse`)

`escalationId` · `level` · `reason` · `escalatedBy` · `escalatedAt` · `isCurrent`

## Response DTO (`ComplaintSLAResponse`)

`slaId` · `policyId` · `policyName` · `targetMinutes` · `startedAt` · `dueAt` ·
`completedAt?` · `remainingMinutes` · `isActive` · `isBreached` · `breachedAt?`

Never expose Domain Entity or ORM.

## Notes

- Closing a Complaint (API-399) completes any active SLA (Rule 4).
- Foundation GET `/sla` coexists with legacy ECMF GET `/api/v1/complaints/{id}/sla`
  only when routers are mounted separately (tests use foundation router alone).
