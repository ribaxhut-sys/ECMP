# Core Request Context (CAPABILITY-002)

| Field | Value |
|---|---|
| ID | CAPABILITY-002 |
| Version | 1.0 |
| Owner | Backend Platform |
| Status | Implemented |
| Last Review | 2026-07-24 |

## Purpose

`RequestContext` is the **platform execution context** for a single request.
Every Application Service that needs org / branch / user / tracing data
receives this object — not loose `organization_id` / `branch_id` / `user_id`
parameters.

This capability does **not** implement Authentication or Authorization.
Identity fields may be empty (`None` / empty frozensets) until Auth is wired.

## Architecture

```text
HTTP Request
    ↓
FastAPI Dependency  (get_request_context)
    ↓
RequestContextFactory
    ↓
RequestContext  (immutable)
    ↓
Application Service
    ↓
Domain / Repository
```

| Layer | Responsibility | Must not |
|---|---|---|
| Domain (`domain/request_context.py`) | Immutable contract | Know FastAPI / HTTP / JWT |
| Application (`application/context_factory.py`) | Build context from plain data | Read headers / import FastAPI |
| Infrastructure (`infrastructure/fastapi_provider.py`) | Read headers, generate ids, DI | Contain business rules |
| Controllers | `Depends(get_request_context)` | Parse headers themselves |
| Repository | Persist domain state | Create or own RequestContext |

## Lifecycle

1. Request arrives with optional stub headers.
2. `get_request_context` reads header constants (never hardcoded strings in controllers).
3. Missing `X-Request-Id` / `X-Correlation-Id` → generated UUIDs.
4. Missing org / branch / user / locale / timezone → `None`.
5. Factory produces immutable `RequestContext`.
6. Controller injects context and passes it to Application.
7. Domain remains framework-independent (uses context only if needed).

## Stub headers

| Constant | Header |
|---|---|
| `HEADER_REQUEST_ID` | `X-Request-Id` |
| `HEADER_CORRELATION_ID` | `X-Correlation-Id` |
| `HEADER_ORGANIZATION_ID` | `X-Organization-Id` |
| `HEADER_BRANCH_ID` | `X-Branch-Id` |
| `HEADER_USER_ID` | `X-User-Id` |
| `HEADER_LOCALE` | `X-Locale` |
| `HEADER_TIMEZONE` | `X-Timezone` |

Missing headers never raise. Authentication will validate later.

## Dependency injection

```python
from typing import Annotated

from fastapi import Depends

from app.core.request_context import RequestContext, get_request_context


@router.post("/example")
async def create_something(
    payload: CreateRequest,
    ctx: Annotated[RequestContext, Depends(get_request_context)],
) -> Response:
    return await service.create(ctx, payload)
```

## Application usage

Prefer:

```python
async def create_queue(self, context: RequestContext, data: CreateQueueInput) -> QueueDto:
    ...
```

Avoid:

```python
async def create_queue(
    self,
    organization_id: UUID,
    branch_id: UUID,
    user_id: UUID,
    ...
) -> QueueDto:
```

## Fields

| Field | Type | Notes |
|---|---|---|
| `request_id` | `str` | Always set (generated if absent) |
| `correlation_id` | `str` | Always set (generated if absent) |
| `organization_id` | `UUID \| None` | Stub header |
| `branch_id` | `UUID \| None` | Stub header |
| `user_id` | `UUID \| None` | Stub header |
| `roles` | `frozenset[str]` | Empty until Auth |
| `permissions` | `frozenset[str]` | Empty until Auth |
| `locale` | `str \| None` | Optional |
| `timezone` | `str \| None` | Optional |

Logging may key off `request_id`, `correlation_id`, `organization_id`,
`branch_id` when a logging framework is introduced.

## Future Authentication integration

A later Authentication capability will:

1. Validate credentials (JWT / session / OAuth — out of scope here).
2. Resolve user, roles, and permissions.
3. Populate the same `RequestContext` via the factory (or a richer builder).
4. Keep Application / Domain free of FastAPI and HTTP.

Controllers continue to use `Depends(get_request_context)` — no redesign required.
