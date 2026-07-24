# ECMP IAM Cache Design

| Field | Value |
|---|---|
| ID | SEC-IAM-CACHE-001 |
| Version | 1.0 |
| Owner | Platform / Security |
| Status | 🟢 Implemented (TASK-041) |
| Last Review | 2026-07-24 |
| Related | TASK-038, TASK-039, TASK-040, SEC-RBAC-FLOW-001 |

## Purpose

Document the process-local IAM cache used by Permission Resolver and Data Scope
Resolver. Optimization focus: consistency, invalidation, organization, metrics,
and maintainability — **without** changing Authorization API, resolver behavior,
Login/JWT, or introducing Redis.

## Architecture

```text
                    ┌─────────────────────────────────┐
                    │        IamCacheService          │
                    │     (process singleton)         │
                    ├─────────────────────────────────┤
                    │ permissions  → PermissionCache  │
                    │ data_scopes  → UserScopedTtlCache│
                    │ principals   → UserScopedTtlCache│ (optional)
                    └─────────────────────────────────┘
                              ▲
          ┌───────────────────┼───────────────────┐
          │                   │                   │
 PermissionResolver   DataScopeResolver    Write services
   (TASK-038)            (TASK-039)         invalidate_*
```

| Namespace | Consumers | Key |
|---|---|---|
| `permissions` | `PermissionResolver` | `userId` |
| `data_scopes` | `DataScopeResolver` | `userId` |
| `principals` | Reserved / optional | `userId` |

Store: **in-memory only** (`backend/app/modules/iam/permission_cache.py`).
No distributed cache.

## Cache entry

| Field | Meaning |
|---|---|
| `value` | Cached payload |
| `created_at` | Monotonic timestamp at `set` |
| `expires_at` | `created_at + ttl` |
| `ttl` | TTL seconds used for this entry |

Default TTL: **5 minutes** (`DEFAULT_TTL_SECONDS = 300`).

## Cache API

Per namespace (`UserScopedTtlCache` / `PermissionCache` facade):

| Method | Behavior |
|---|---|
| `get(userId)` | Return value or `None` (miss / expired) |
| `set(userId, value)` | Upsert with new TTL window |
| `delete(userId)` | Remove one key; returns whether present |
| `invalidate(userId)` | Same as delete (void) |
| `invalidate_all()` | Clear namespace; returns count removed |
| `cleanup_expired()` | Eager purge of expired keys |
| `stats()` | Metrics snapshot |

`IamCacheService` additionally:

| Method | Behavior |
|---|---|
| `invalidate(userId)` | All namespaces for one user |
| `invalidate_all()` | All namespaces |
| `cleanup_expired()` | All namespaces |
| `stats()` | `{ permissions, data_scopes, principals }` |

Module helpers:

- `get_iam_cache()` / `get_permission_cache()` / `get_data_scope_cache()` / `get_principal_cache()`
- `invalidate_iam_user(userId)` — user↔role writes
- `invalidate_iam_all()` — role↔permission and role data-scope writes

## Metrics

| Counter | Meaning |
|---|---|
| `hit` | Successful `get` of non-expired entry |
| `miss` | `get` with missing or expired key |
| `entry_count` | Live entries in store |
| `expired` | Entries dropped because TTL elapsed |
| `invalidated` | Entries removed via delete / invalidate / invalidate_all |

## Invalidation matrix

| Write path | Helper | Effect |
|---|---|---|
| UserRole assign / remove / replace | `invalidate_iam_user(userId)` | Permissions + scopes + principals for that user |
| RolePermission assign / remove / replace | `invalidate_iam_all()` | Full IAM clear (role matrix affects many users) |
| DataScope create / update / delete / replace | `invalidate_iam_all()` | Full IAM clear (role scopes affect many users) |

Single helpers avoid duplicated per-service invalidate logic.

## Thread safety

- `threading.RLock` per namespace
- Short critical sections (lookup / mutate / metric bump)
- No external concurrency dependencies
- Safe under concurrent FastAPI workers in one process (per-process cache)

## Non-goals

- Redis / shared cluster cache
- Embedding permissions or scopes in JWT
- Changing Permission / Data Scope resolver public APIs
- Changing Authorization Middleware endpoints
- Domain auto-filtering (Complaint, Settings, Attachment, Notification, Audit)

## Related code

- `backend/app/modules/iam/permission_cache.py`
- `backend/app/modules/iam/permission_resolver.py`
- `backend/app/modules/iam/data_scope_resolver.py`
- `backend/app/modules/iam/user_role/service.py`
- `backend/app/modules/iam/role_permission/service.py`
- `backend/app/modules/iam/data_scope/service.py`
- `10 Security and Access Standards/ECMP_RBAC_Flow_v1.0.md`
