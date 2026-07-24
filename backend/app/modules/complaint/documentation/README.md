# Complaint Domain Foundation + Processing + Assignment + Escalation + SLA

| Field | Value |
|---|---|
| ID | DOM-COMPLAINT-001 |
| Version | 1.4 |
| Owner | Backend Lead |
| Status | 🟢 Implemented |
| Last Review | 2026-07-24 |

## Objective

Independent **Complaint** bounded context: domain model, repository port,
SQLAlchemy persistence, CRUD + processing + assignment + escalation + SLA
application services, and REST API.

Complaint knows **why** the customer came. QueueTicket knows **that** they came.
Assignment knows **who** is responsible. Escalation knows **handling level**.
SLA knows **due time / remaining / breach**. None of Assignment, Escalation, or
SLA changes lifecycle status.

## Relationship

```text
Organization → Branch → Queue → QueueTicket
                                   ├─ Complaint A → Assignment* → Escalation* → SLA*
                                   └─ Complaint B → (future Workflow)
```

- One QueueTicket → many Complaints
- Complaint stores `queue_ticket_id` only (no Queue entity / no FK to Queue tables)
- One Complaint → at most one **active** Assignment; history is append-only
- One Complaint → at most one **current** Escalation; history is append-only
- One Complaint → at most one **active** ComplaintSLA
- Queue does not know Complaint detail

## In Scope

- Complaint aggregate + status/priority enums + Resolution VO + Assignment + Escalation + SLA
- SLAPolicy entity (shared configuration)
- Lifecycle validation in Domain
  (`OPEN → IN_PROGRESS → RESOLVED → CLOSED`; reopen `RESOLVED → IN_PROGRESS`)
- Aggregate operations: `start_processing` · `resolve` · `close` · `reopen`
- Assignment operations: `assign` · `reassign` · `unassign` (status unchanged)
- Escalation operation: `escalate` (status + assignment unchanged; level↑ only)
- SLA operations: `start_sla` · `complete_sla` · breach / remaining (status unchanged)
- Repository ports + async SQLAlchemy adapters (CRUD persistence only)
- `ComplaintCrudApplicationService` · `ComplaintProcessingApplicationService`
  · `ComplaintAssignmentApplicationService` · `ComplaintEscalationApplicationService`
  · `ComplaintSLAApplicationService`
- REST CRUD + processing + assignment + escalation + SLA + ticket-nested list/create
- OpenAPI `complaint-domain-service.v1.yaml` (API-390…412)
- Unit + integration tests

## Out of Scope

Workflow · Timeline · Comment · Attachment ·
Notification · Queue Display · Dashboard · AI · Operations · Authentication ·
Scheduler · Auto-escalation · Escalation Trigger · Rule Engine

## Module Layout

```text
backend/app/modules/complaint/
  domain/           # models, lifecycle, Resolution, Assignment, Escalation, SLA, ports
  application/      # DTO, domain service, CRUD + processing + assignment + escalation + SLA
  infrastructure/   # ORM, mapper, SQLAlchemy repositories, DI
  api/              # routers, controllers, requests, responses
  documentation/    # this pack
```

## Coexistence

Legacy ECMF module `app.modules.complaints` / `app.modules.sla` remains
for assign/escalate/SLA and owns production `/api/v1/complaints` CRUD (auth required).

CAPABILITY-004…008 is a separate Clean Architecture BC:

- Tables: `complaint_cases` + `complaint_case_assignments` + `complaint_case_escalations`
  + `complaint_sla_policies` + `complaint_case_slas`
- Production mount: ticket-nested routes (`/api/v1/tickets/{id}/complaints`)
- Full surface: `complaint_foundation_router` (tests + OpenAPI catalog API-390…412)
- No Queue domain imports — `queue_ticket_id` reference only
