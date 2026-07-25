# Sprint F3 — Queue Module

**Status:** Complete  
**Scope:** Queue dashboard (summary + list + supported actions) against frozen backend APIs.  
**Out of scope:** Assignment UX (assign-to-others), Resolution, Escalation, Notifications, dashboard redesign, caching, performance work.

## 1. Folder structure

```
frontend/src/
  app/(app)/queue/
    page.tsx                 # Queue dashboard (/queue)
  features/queue/
    QueueDashboardView.tsx
    QueueRowActions.tsx
    queueListFilters.ts
    index.ts
  lib/api/
    queue.ts                 # Thin typed wrappers only
    types.ts                 # DashboardComplaintSummary, UnassignComplaintRequest
```

## 2. Screens implemented

| Screen | Route | Notes |
|---|---|---|
| Queue Dashboard | `/queue` | Summary (API-389), list with status / assignee / priority / SLA, filters, pagination |
| Queue Detail | — | No dedicated queue detail API; **Open** navigates to `/complaints/[id]` |

## 3. Backend APIs consumed

| ID | Endpoint | Use |
|---|---|---|
| API-389 | `GET /api/v1/dashboard/summary` | Queue summary cards |
| API-388 | `GET /api/v1/complaints/search` | Queue list + filter + sort + pagination |
| API-206 | `GET /api/v1/complaints/{id}/assignments` | Assignee column enrichment |
| API-314 | `GET /api/v1/complaints/{id}/sla` | SLA indicator enrichment |
| API-205 | `POST /api/v1/complaints/{id}/assign` | Take (self-assign) |
| API-403 | `POST /api/v1/complaints/{id}/unassign` | Release |
| API-224 | `PATCH /api/v1/complaints/{id}/status` | Update status |

No mocked APIs. No backend or contract changes. Assign-to-others UI not built.

## 4. Queue actions

| Action | Permission | Notes |
|---|---|---|
| Refresh | — | Reloads summary + list |
| Take | `complaints:assign` | Assigns current user when unassigned |
| Release | `complaints:assign` | Unassigns active assignee (confirm modal) |
| Update status | `complaints:update` | Allowed transitions only (same matrix as F2) |
| Open | `complaints:read` | Complaint Detail |

## 5. Known limitations

- List items do not embed assignee/SLA; values are enriched per page via API-206 / API-314 (best-effort; shows "—" on failure).
- Release uses domain API-403; may fail for some legacy assignment rows — error surfaced in the confirm dialog.
- Assign-to-others / reassign UX intentionally not implemented (Assignment out of scope).
- Summary requires `dashboard:read`; list requires `complaints:read`.
- Visit-context queue-service (`/api/v1/queues`) is not this module.

## 6. Commit

`git log -1 --oneline -- frontend/`
