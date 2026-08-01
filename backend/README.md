# ECMP Backend (Foundation)

FastAPI application for the Enterprise Complaint Management Platform.

**Version:** `1.0.0`

## Architecture position (read this first)

ECMP is a **Complaint Management business module**, not a standalone identity
provider. Per ADR-014 v1.4 / ADR-015 v1.3 (*Accepted with Conditions*,
PROGRAM-BOARD-004):

| Concern | Mode A — Standalone | Mode B — Enterprise (🔴 CLOSED, C-7) |
|---|---|---|
| Authentication | ECMP local credentials (HS256) | Enterprise Platform SSO (OIDC RS256) |
| User directory / password / MFA / session | ECMP | Enterprise Platform |
| Organization / branch / department | ECMP reference data | Enterprise Platform (ECMP holds references) |
| **Authorization (roles & permissions)** | **ECMP** | **ECMP** — after the Enterprise Entitlement Gate |

Two rules that hold in **both** modes:

1. **Permissions never come from the token.** They are always resolved from the
   Core Platform matrix in the database (ADR-008). `RoleMapper` additionally
   refuses to emit privileged codes (`ADMIN` / `ADMINISTRATOR` / `SUPER_ADMIN`)
   from IdP claims — enterprise roles do not become ECMP roles (ADR-015 §6).
2. **Mode divergence terminates at the Identity Adapter.** Domain modules must
   not branch on deployment mode.

### Relevant switches

| Variable | Default | Notes |
|---|---|---|
| `ECMP_AUTH_MODE` | `dev` | `dev` = local HS256, `jwt` = OIDC RS256. Forced to `jwt` in staging/production. |
| `ECMP_ENTERPRISE_MODE` | `false` | Mode B runtime switch. **Must stay `false` while C-7 is CLOSED.** Requires `ECMP_AUTH_MODE=jwt` and `ECMP_LOCAL_CREDENTIAL_AUTH=false`. |
| `ECMP_LOCAL_CREDENTIAL_AUTH` | `true` | Mode A credential surface. Startup **fails fast** if `true` in staging/production or under enterprise mode. |
| `LOG_FORMAT` | `json` | `text` for human-readable local output. |

## Local (without Docker)

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Liveness: `GET http://localhost:8000/live`  
Readiness: `GET http://localhost:8000/ready` (Docker healthcheck)

### Mode A — Batch-1 attachment ops hygiene (FR-004)

```bash
python scripts/cm_batch1_ops_hygiene.py probe-storage
python scripts/cm_batch1_ops_hygiene.py void-abandoned-staging
python scripts/cm_batch1_ops_hygiene.py all
```

Runbook: `../15 Operations Runbook/ECMP_CM_Batch1_Staging_TTL_Cleanup_v0.1.md`.  
Does not add OpenAPI routes; does not unlock Mode B; TD-OPS-002 remains deferred.
Legacy informational: `GET http://localhost:8000/health`

## Structure

```text
app/
  api/                 # HTTP routers (health)
  core/                # config, logging, JWT, auth, errors, middleware
    request_context/   # CAPABILITY-002 execution context (no Auth)
  db/                  # SQLAlchemy engine/session + mixins
  models/              # ORM models (ECMP v1.0 schema)
  modules/complaints/  # repository + service + schemas + router
  dependencies/        # DI foundation
alembic/               # migrations
```

### Core Request Context (CAPABILITY-002)

Platform execution context for Application services:

- Contract: `app.core.request_context.RequestContext` (immutable)
- Factory: `RequestContextFactory` (no FastAPI)
- DI: `Depends(get_request_context)` — controllers must not parse headers
- Docs: `app/core/request_context/README.md`

Does **not** implement Authentication / Authorization / JWT.

## Complaint API (JWT)

| Method | Path | Permission / Role |
|--------|------|-------------------|
| POST | `/api/v1/auth/login` | public |
| POST | `/api/v1/auth/refresh` | refresh cookie |
| POST | `/api/v1/auth/logout` | refresh cookie |
| GET | `/api/v1/auth/me` | bearer |
| POST | `/api/v1/complaints` | `complaints:create` |
| GET | `/api/v1/complaints` | `complaints:read` |
| GET | `/api/v1/complaints/{id}` | `complaints:read` |
| PUT | `/api/v1/complaints/{id}` | `complaints:update` |
| POST | `/api/v1/complaints/{id}/assign` | `SUPERVISOR` + `complaints:assign` |
| GET | `/api/v1/complaints/{id}/assignments` | `complaints:read` |
| POST | `/api/v1/complaints/{id}/escalate` | `SUPERVISOR` + `complaints:escalate` |
| GET | `/api/v1/complaints/{id}/escalations` | `complaints:read` |

Auth: access JWT 15m (`sub` + `roles`); refresh token HttpOnly Secure SameSite=Lax cookie 7d with rotation.
Permissions are **not** stored in the JWT — resolved per request via Dynamic Permission Resolver
(User → UserRole → Role → RolePermission → Permission) with a 5-minute in-memory IAM cache
(`app/modules/iam/permission_resolver.py`, `permission_cache.py` / `IamCacheService`). See
`10 Security and Access Standards/ECMP_RBAC_Flow_v1.0.md` and
`10 Security and Access Standards/ECMP_IAM_Cache_Design_v1.0.md`.
Audit actions: `auth.login`, `auth.refresh`, `auth.logout`.

Contract: `07 API Catalog/openapi/complaint-service.v1.yaml`

## Developer Guide — Authorization Middleware (TASK-040)

### Pipeline

```text
Request → Authentication → Permission Resolver → Permission Check
       → (optional) Data Scope Resolver → Data Scope Check → Endpoint
```

Implementation: `app/core/authorization/` with facade `app/core/auth.py` (existing
imports keep working).

### Public helpers

| Helper | Step |
|--------|------|
| `require_permissions(...)` | Permission Check |
| `require_roles(...)` | Role Check (JWT roles) |
| `require_data_scope(...)` | Data Scope Check (opt-in) |
| `resolve_effective_scope(user_id, session)` | Data Scope Resolver (service) |

```python
from app.core.auth import require_permissions, require_data_scope, resolve_effective_scope
```

Endpoints that only use `require_permissions()` are unchanged — data-scope steps
are not run unless the endpoint opts in.

### Error responses

| HTTP | Code | Meaning |
|------|------|---------|
| 401 | `UNAUTHENTICATED` | Missing/invalid Bearer |
| 403 | `FORBIDDEN` | Permission / role denied |
| 403 | `DATA_SCOPE_DENIED` | Opt-in data scope check failed |

### IAM Cache (TASK-041)

Process-local `IamCacheService` in `permission_cache.py` (no Redis). Namespaces:
permissions, data_scopes, principals (optional).

| API | Behavior |
|-----|----------|
| `get` / `set` / `delete` / `invalidate` | Keyed by `userId`, TTL 5 minutes |
| `invalidate_all` / `cleanup_expired` / `stats` | Namespace maintenance + metrics |
| `invalidate_iam_user(userId)` | After user↔role assignment changes |
| `invalidate_iam_all()` | After role↔permission or data-scope writes |
| Metrics | `hit`, `miss`, `entry_count`, `expired`, `invalidated` |

Design: `../10 Security and Access Standards/ECMP_IAM_Cache_Design_v1.0.md`.

### Adding a permission to a role

Use Role-Permission Matrix APIs (`API-348–350`). Do **not** edit a static map for runtime auth.
Migration `0025_permission_resolver` seeds the baseline matrix formerly held in `ROLE_PERMISSIONS`.

### Data Scope (opt-in)

```python
from typing import Annotated
from fastapi import Depends
from app.core.auth import require_data_scope, resolve_effective_scope
from app.modules.iam.data_scope_resolver import EffectiveScope

scope = resolve_effective_scope(user_id, session)

@router.get("/example")
def example(
    scope: Annotated[EffectiveScope, Depends(require_data_scope("BRANCH", "SELF"))],
):
    # GLOBAL also passes; otherwise BRANCH or SELF required
    ...
```

Complaint / Settings / Attachment / Notification / Audit are **not** auto-filtered.

See `10 Security and Access Standards/ECMP_RBAC_Flow_v1.0.md`.

## Developer Guide — Complaint Routing Foundation (TASK-043)

### Rule

All initial destination decisions live in `app/modules/routing` only.

Do **not** put source/target → receiver matrices in Complaint Service,
Assignment Service, Notification, SLA, or KPI.

### Flow

```text
API-201 Create Complaint
  → ComplaintService.create
      → ComplaintRoutingService.resolve_route(source_*, target_*)
      → apply ComplaintRoute.assignment_context → branch_id (if BRANCH)
      → persist + audit/timeline (route metadata)
  → later: Assignment Engine (API-205) assigns a user — unchanged
```

### Default routes

| Source | Target | Receiver |
|--------|--------|----------|
| CUSTOMER | BRANCH | BRANCH |
| BRANCH | HEAD_OFFICE | HEAD_OFFICE |
| HEAD_OFFICE | BRANCH | BRANCH |
| SYSTEM | HEAD_OFFICE | HEAD_OFFICE |

Unsupported pairs raise `VALIDATION_ERROR` (`Invalid complaint route.`).

Legacy `customerId` (+ optional `branchId`) still maps to CUSTOMER→BRANCH.

Architecture: `../20 Domain Architecture/ECMF/COMPLAINT_ROUTING.md`.

## Developer Guide — Complaint Context Foundation (TASK-044)

### Rule

`ComplaintContext` is an **immutable read model** assembled on demand.
Do **not** create a `complaint_contexts` table or cache layer.

Future modules (Dashboard, KPI, Notification, Workflow, AI) should consume
`ComplaintContext` instead of joining Complaint / Assignment / SLA ad hoc.

### Flow

```text
ComplaintContextService.build_context(complaintId)
  → load Complaint
  → load current Assignment (if any)
  → load SlaRecord (if any)
  → ComplaintRoutingService.resolve_route(source_*, target_*)
  → return frozen ComplaintContext

refresh_context(complaintId)  # re-assemble from live data (no cache)
```

### Complaint Service

Optional helpers (no HTTP API change):

- `ComplaintService.get_context(complaint_id)`
- `ComplaintService.refresh_context(complaint_id)`

### Module

`backend/app/modules/complaint_context/`

Architecture: `../20 Domain Architecture/ECMF/COMPLAINT_CONTEXT.md`.

## Developer Guide — Complaint Event Foundation (TASK-045)

### Rule

Significant Complaint lifecycle transitions produce an immutable
`ComplaintEvent` via `ComplaintEventFactory` only.

Do **not** introduce Kafka / RabbitMQ / Redis Streams / Pub-Sub,
and do **not** create an event-store table in this task.

### Flow

```text
ComplaintService.create / change_status / close
  → (business write + audit/timeline unchanged)
  → ComplaintEventFactory.create_* (...)
  → immutable ComplaintEvent (in memory only)
  → EventDispatcher.dispatch(event)   # TASK-046
```

### Event types

`ComplaintCreated` · `ComplaintAssigned` · `ComplaintAccepted` ·
`ComplaintInProgress` · `ComplaintResolved` · `ComplaintClosed` ·
`ComplaintEscalated`

### Module

`backend/app/modules/complaint_events/`

Architecture: `../20 Domain Architecture/ECMF/COMPLAINT_EVENTS.md`.

Catalog: `../08 Event Catalog/events/events.yaml` (EVT-009 … EVT-015).

## Developer Guide — In-Process Event Dispatcher (TASK-046)

### Rule

`ComplaintService` is a **producer only**. It must never import or name
concrete consumers. Delivery goes exclusively through `EventDispatcher`.

This is **not** an Event Bus, Kafka, RabbitMQ, or Event Store.

### Flow

```text
ComplaintService
  → ComplaintEventFactory.create_* (...)
  → EventDispatcher.dispatch(event)
  → EventHandler.handle(event)  (registration order, sync)
  → DispatchResult { success_count, failed_count, handler_results }
```

### API

- `register(handler)` / `unregister(handler)`
- `dispatch(event) -> DispatchResult`
- `registered_handlers()`

### Error handling

One handler failure does **not** stop remaining handlers. Failures are
collected in `DispatchResult` and must not abort the business write.

### Module

`backend/app/modules/event_dispatcher/`

Architecture: `../20 Domain Architecture/ECMF/EVENT_DISPATCHER.md`.

### Out of scope

Do not implement Workflow / Dashboard / AI / KPI handlers
in TASK-046. Notification consumer arrived in TASK-047;
Dashboard/KPI projections in TASK-050/051; Workflow foundation in TASK-052.

## Developer Guide — Notification Domain Foundation (TASK-047)

### Rule

Notification is the first `EventDispatcher` consumer. It **builds**
immutable `Notification` objects from Complaint events.

Do **not** deliver via email / WhatsApp / SMS / Push / WebSocket.
Do **not** persist these objects to a database in this task.
`ComplaintService` must **never** import Notification.

### Flow

```text
ComplaintService
  → ComplaintEventFactory
  → EventDispatcher.dispatch(event)
  → NotificationEventHandler.handle(event)
  → NotificationFactory.from_event(event)
  → immutable Notification (in-memory store only)
```

### Model fields

`notification_id` · `notification_type` · `created_at` · `recipient` ·
`title` · `message` · `severity` · `source_event` · `payload`

### Registration

Composition root (`app/dependencies/events.py`) registers
`NotificationEventHandler` on the shared dispatcher. Routers inject that
dispatcher into `ComplaintService`.

### Module

`backend/app/modules/notification/` — `event_models`, `factory`, `handler`,
`memory`, `registration` (alongside TASK-030 template/queue foundation).

Architecture: `../20 Domain Architecture/Notification/EVENT_CONSUMER.md`.

Event Consumer Guide: `../20 Domain Architecture/Notification/EVENT_CONSUMER.md`.

## Developer Guide — Notification Intent Foundation (TASK-048)

### Rule

`NotificationIntent` describes **WHAT** should be delivered.
Transport adapters (future) decide **HOW**.

Do **not** implement email / WhatsApp / SMS / Push / WebSocket adapters.
Do **not** persist or queue intents in this task.
Do **not** change the `Notification` model.

### Flow

```text
NotificationEventHandler
  → NotificationFactory.from_event(event)
  → Notification
  → NotificationIntentFactory.from_notification(notification)
  → NotificationIntent (in-memory store only)
```

### Intent fields

`intent_id` · `created_at` · `notification_id` · `recipient_key` ·
`preferred_channels` · `priority` · `template_key` · `variables` ·
`metadata`

### Channel enum (no implementation)

`EMAIL` · `WHATSAPP` · `PUSH` · `SMS` · `WEBSOCKET`

### Module

`backend/app/modules/notification/` — `intent_models`, `intent_factory`,
`intent_memory` (handler builds intent after Notification).

Architecture: `../20 Domain Architecture/Notification/NOTIFICATION_INTENT.md`.

## Developer Guide — Notification Delivery Foundation (TASK-049)

### Rule

`NotificationDelivery` is a **planned delivery action**.

It is **not** transport, **not** sending, and **not** a queue.

Do **not** implement email / WhatsApp / SMS / Push / WebSocket adapters.
Do **not** introduce SENT/FAILED/RETRY statuses in this task.
Do **not** change Notification or NotificationIntent models.

### Flow

```text
NotificationEventHandler
  → Notification
  → NotificationIntent
  → NotificationDeliveryFactory.from_intent(intent)
  → NotificationDelivery × N (one per preferred channel, status=PLANNED)
```

### Delivery fields

`delivery_id` · `created_at` · `intent_id` · `channel` · `recipient_key` ·
`priority` · `template_key` · `variables` · `status` · `metadata`

### Status

`PLANNED` only.

### Module

`backend/app/modules/notification/` — `delivery_models`, `delivery_factory`,
`delivery_memory` (handler builds deliveries after Intent).

Architecture: `../20 Domain Architecture/Notification/DELIVERY_FOUNDATION.md`.

## Developer Guide — Dashboard Projection Foundation (TASK-050)

### Rule

`DashboardProjection` is a **read model** updated only from Complaint events.

Do **not** query Complaint aggregates during projection updates.
Do **not** call `ComplaintService` from the projector.
Do **not** add an HTTP projection endpoint in this task.
Do **not** persist the projection (no DB / cache / materialized view).

### Flow

```text
ComplaintService
  → ComplaintEventFactory
  → EventDispatcher.dispatch(event)
  → DashboardProjectionHandler.handle(event)
  → DashboardProjectionStore.apply(event)
  → immutable DashboardProjection snapshot
```

### Projection fields

`total_complaints` · `open_complaints` · `assigned_complaints` ·
`in_progress_complaints` · `resolved_complaints` · `closed_complaints` ·
`escalated_complaints` · `breached_sla` · `updated_at`

### Module

`backend/app/modules/dashboard/` — `projection_models`, `projection_store`,
`projection_handler`, `projection_registration`.

Architecture / Projection Guide:
`../20 Domain Architecture/Dashboard/PROJECTION_GUIDE.md`.

## Developer Guide — KPI Projection Foundation (TASK-051)

### Rule

`KpiProjection` is a **read model** updated only from Complaint events.

Do **not** query Complaint aggregates during projection updates.
Do **not** call `ComplaintService` from the projector.
Do **not** add an HTTP projection endpoint in this task.
Do **not** persist the projection (no DB / cache / materialized view).
Do **not** wire this into the existing `KpiService` summary API (TASK-026).

### Flow

```text
ComplaintService
  → ComplaintEventFactory
  → EventDispatcher.dispatch(event)
  → KpiProjectionHandler.handle(event)
  → KpiProjectionStore.apply(event)
  → immutable KpiProjection snapshot
```

### Projection fields

`total_received` · `total_closed` · `total_resolved` · `total_escalated` ·
`current_open` · `current_in_progress` · `sla_breached` ·
`closure_rate` · `resolution_rate` · `updated_at`

### Calculation rules

```text
closure_rate     = closed / received   (0.0 if received == 0)
resolution_rate  = resolved / received (0.0 if received == 0)
```

### Module

`backend/app/modules/kpi/` — `projection_models`, `projection_store`,
`projection_handler`, `projection_registration`.

Architecture / Projection Guide:
`../20 Domain Architecture/KPI/PROJECTION_GUIDE.md`.

## Developer Guide — Workflow Foundation (TASK-052)

### Rule

Workflow is an **orchestration planner** over Complaint events.

Do **not** execute step actions.
Do **not** invoke Notification, Assignment, or external systems.
Do **not** own Complaint business logic / mutate Complaint aggregates.
Do **not** add an HTTP workflow endpoint in this task.
Do **not** persist definitions or instances (in-memory only).
Do **not** confuse this with Administration **Workflow Config** (ADR-008
status-transition matrix).

### Flow

```text
ComplaintService
  → ComplaintEventFactory
  → EventDispatcher.dispatch(event)
  → WorkflowEventHandler.handle(event)
  → WorkflowEngine.process(event)
  → WorkflowRegistry.match(trigger)
  → WorkflowInstanceStore.add(CREATED instance)
```

### Matching

Exact match on `event.event_type` ↔ `WorkflowTrigger` value. Multiple
definitions may match one event → multiple `WorkflowInstance`s. No match →
no instance.

### Supported triggers

`ComplaintCreated` · `ComplaintAssigned` · `ComplaintAccepted` ·
`ComplaintInProgress` · `ComplaintResolved` · `ComplaintClosed` ·
`ComplaintEscalated`

### Instance status

`CREATED` only. Planned actions are recorded with `executed: false`.

### Module

`backend/app/modules/workflow/` — `models`, `factory`, `registry`, `store`,
`engine`, `handler`, `registration`.

Architecture / Guide:
`../20 Domain Architecture/Workflow/WORKFLOW_ARCHITECTURE.md`,
`../20 Domain Architecture/Workflow/WORKFLOW_GUIDE.md`.

## Developer Guide — Execution Plan Foundation (TASK-053)

### Rule

`ExecutionPlan` is **shared infrastructure**. Workflow is one producer.

Do **not** execute tasks.
Do **not** invoke `ExecutionRegistry` handlers.
Do **not** invoke Notification, Assignment, or external systems.
Do **not** add an HTTP execution endpoint in this task.
Do **not** persist plans (in-memory only).
Do **not** change `WorkflowDefinition` / `WorkflowInstance` models.

### Flow

```text
WorkflowEventHandler
  → WorkflowEngine → WorkflowInstance (CREATED)
  → WorkflowExecutionProducer (on_instances)
  → ExecutionPlanner.from_workflow(instance)
  → ExecutionPlanStore.add(PLANNED plan)
```

### Planner mapping (Workflow)

| WorkflowStep | ExecutionTask |
|---|---|
| `action_type` | `task_type` |
| `order` | `order` |
| `configuration` | `configuration` |
| `configuration.target` or `workflow.step:{name}` | `target` |
| — | `executed=false` |

### Status

Plan: `PLANNED` only. Task: `executed=false` by default.

### Module

`backend/app/modules/execution/` — `models`, `planner`, `store`, `registry`,
`workflow_producer`.

Architecture / Guide:
`../20 Domain Architecture/Execution/EXECUTION_ARCHITECTURE.md`,
`../20 Domain Architecture/Execution/EXECUTION_GUIDE.md`.

## Migrations

```bash
# inside backend container or local venv with DATABASE_URL pointing at Postgres
alembic upgrade head
alembic current
```
