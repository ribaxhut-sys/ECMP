# Sprint F5 — Resolution Workflow

**Status:** Complete  
**Scope:** Resolution list + submit resolution / final resolution / escalation request / close escalation / close complaint.  
**Out of scope:** Edit resolution (no API), Sprint F6, dashboard redesign, notifications, performance work.

## 1. Folder structure

```
frontend/src/
  app/(app)/resolutions/
    page.tsx
  features/resolutions/
    ResolutionListView.tsx
    ResolutionRowActions.tsx
    resolutionListFilters.ts
    index.ts
  lib/api/
    resolutions.ts
```

## 2. Screens implemented

| Screen | Route | Notes |
|---|---|---|
| Resolution List | `/resolutions` | Complaint, status, assignee, resolution status/time, final resolution, escalation, branch, priority; search/filter/sort; pagination; loading/empty/error |
| Resolution Detail | — | No dedicated detail API; **Open** → `/complaints/[id]` |

## 3. Backend APIs consumed

| ID | Endpoint | Use |
|---|---|---|
| API-388 | `GET /api/v1/complaints/search` | List base |
| API-206 | `GET …/assignments` | Assignee column |
| API-226 | `GET …/resolution` | Resolution status / time |
| API-225 | `POST …/resolution` | Submit resolution |
| API-311 | `GET …/final-resolution` | Final resolution status |
| API-310 | `POST …/final-resolution` | Submit final resolution |
| API-208 | `GET …/escalations` | Escalation status |
| API-301 | `POST …/escalations` | Request escalation |
| API-313 | `POST /api/v1/escalations/{id}/close` | Close escalation |
| API-312 | `POST …/close` | Close complaint |
| API-223 | `GET /api/v1/branches` | Branch labels / filter |

No mocked APIs. No backend or contract changes. No edit-resolution endpoint exists.

## 4. Resolution actions

| Action | Permission | API |
|---|---|---|
| Submit Resolution | `complaints:update` | API-225 |
| Edit Resolution | — | **Not available** (no PUT/PATCH) |
| Submit Final Resolution | `appointments:complete` | API-310 |
| Request Escalation | `complaints:update` | API-301 |
| Close Escalation | `escalations:close` | API-313 |
| Close Complaint | `complaints:close` | API-312 |
| Open | `complaints:read` | Complaint Detail |

## 5. Known limitations

- No global `/resolutions` list API — composed from complaint search + per-row enrichment.
- Edit resolution is unsupported by OpenAPI.
- Enrichment issues 4 parallel GETs per visible row (assignee/resolution/final/escalation); 404 treated as empty.
- Backend may reject actions when complaint state is invalid; errors surface in the confirm dialog.
- Escalation approve/reject remain on Complaint Detail (not part of this list action set).

## 6. Commit

`git log -1 --oneline -- frontend/`
