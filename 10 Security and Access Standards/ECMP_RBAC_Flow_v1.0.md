# ECMP Authorization Flow — RBAC + Data Scope + Middleware

| Field | Value |
|---|---|
| ID | SEC-RBAC-FLOW-001 |
| Version | 1.3 |
| Owner | Platform / Security |
| Status | 🟢 Implemented (TASK-038 + TASK-039 + TASK-040 + TASK-041) |
| Last Review | 2026-07-24 |

## Purpose

Describe how the Authorization Engine resolves **permissions** (TASK-038) and
**data scopes** (TASK-039), and how the **Authorization Middleware** (TASK-040)
runs them as one pipeline.

## Middleware pipeline (TASK-040)

```text
Request
  ↓
Authentication          JWT Bearer → user_id + roles
  ↓
Permission Resolver     TASK-038 (IAM cache; skip if JWT has permissions claim)
  ↓
Permission Check        require_permissions / require_roles
  ↓
Data Scope Resolver     TASK-039 (IAM cache; optional / opt-in)
  ↓
Data Scope Check        require_data_scope (optional / opt-in)
  ↓
Endpoint
```

Public helpers share this pipeline. Endpoints that only use
`require_permissions(...)` keep the same behavior and do not run data-scope
steps.

## Permission resolution (TASK-038)

```text
User
  → UserRole
    → Role (active, not deleted)
      → RolePermission
        → Permission (active, not deleted)
          → Set<permissionCode>
```

## Data scope resolution (TASK-039)

```text
User
  → UserRole
    → Role (active, not deleted)
      → DataScope
        → EffectiveScope
```

| Scope type | Meaning |
|---|---|
| `GLOBAL` | Access all data |
| `ORGANIZATION` | Organization id(s) in `scope_value` |
| `BRANCH` | Branch id(s) in `scope_value` |
| `SELF` | Own records only |
| `CUSTOM` | Caller-defined `scope_value` |

## Dependency flow

| Step | Module | Dependency / helper |
|---|---|---|
| Authentication | `authorization/authentication.py` | `get_current_principal` |
| Permission Resolver | `iam/permission_resolver.py` | called inside `get_current_principal` |
| Permission Check | `authorization/permission_check.py` | `require_permissions`, `require_roles` |
| Data Scope Resolver | `iam/data_scope_resolver.py` | via `resolve_effective_scope` |
| Data Scope Check | `authorization/data_scope_check.py` | `require_data_scope` |
| Facade | `core/auth.py` | re-exports for existing routers |

## Error responses (standardized)

| HTTP | Code | Message (default) | When |
|---|---|---|---|
| 401 | `UNAUTHENTICATED` | Unauthenticated (or specific JWT reason) | Missing/invalid Bearer |
| 403 | `FORBIDDEN` | Permission denied | Missing permission / role |
| 403 | `DATA_SCOPE_DENIED` | Data scope denied | Opt-in scope check failed |

Envelope remains `{ code, message, details? }`. `PermissionDeniedError` and
`DataScopeDeniedError` subclass `ForbiddenError` so existing
`except ForbiddenError` / test asserts stay valid.

## Public helpers

| Helper | Use |
|---|---|
| `require_permissions(*codes)` | FastAPI dependency — permission check |
| `require_roles(*codes)` | FastAPI dependency — JWT role check |
| `require_data_scope(*types)` | FastAPI dependency — opt-in scope check (`GLOBAL` satisfies) |
| `resolve_effective_scope(user_id, session)` | Service-layer scope resolve |
| `DataScopeResolver.resolve_scopes(userId)` | Full `EffectiveScope` |
| Domain gates | `require_supervisor_assign`, … (compose permissions + roles) |

## Cache (shared IAM — TASK-041)

| Item | Value |
|---|---|
| Store | Process in-memory `IamCacheService` (`permission_cache` module) |
| Namespaces | `permissions`, `data_scopes`, `principals` (optional) |
| Key | `userId` (UUID) |
| TTL | 5 minutes |
| Entry | `value`, `created_at`, `expires_at`, `ttl` |
| Metrics | `hit`, `miss`, `entry_count`, `expired`, `invalidated` |
| Permissions | `get_permission_cache()` |
| Data scopes | `get_data_scope_cache()` |
| Invalidate user | `invalidate_iam_user(userId)` on user↔role writes |
| Invalidate all | `invalidate_iam_all()` on role↔permission and data-scope writes |

Design detail: [`ECMP_IAM_Cache_Design_v1.0.md`](./ECMP_IAM_Cache_Design_v1.0.md).

## Out of scope

- Automatic row filtering on Complaint / Settings / Attachment / Notification / Audit endpoints
- Embedding permissions or scopes in JWT
- Changing Login/JWT issuance
- Changing Permission Resolver or Data Scope Resolver public APIs
- Redis / distributed cache
- New audit events

## Related code

- `backend/app/core/auth.py` (facade)
- `backend/app/core/authorization/` (pipeline modules)
- `backend/app/modules/iam/permission_resolver.py`
- `backend/app/modules/iam/data_scope_resolver.py`
- `backend/app/modules/iam/permission_cache.py`
- `backend/app/dependencies/__init__.py`
