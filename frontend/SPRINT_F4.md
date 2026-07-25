# Sprint F4 — Assignment Module

**Status:** Complete  
**Scope:** Assignment list + Assign / Reassign / Cancel against frozen APIs.  
**Out of scope:** Resolution, Final Resolution, Escalation, Notifications, dashboard redesign, Search module, performance work.

## 1. Folder structure

```
frontend/src/
  app/(app)/assignments/
    page.tsx
  features/assignments/
    AssignmentListView.tsx
    AssignmentRowActions.tsx
    assignmentListFilters.ts
    index.ts
  lib/api/
    assignments.ts
```

## 2. Screens implemented

| Screen | Route | Notes |
|---|---|---|
| Assignment List | `/assignments` | Complaint number/title, current/previous assignee, Active/Unassigned, assigned time, branch, priority; search/filter/sort; server pagination; loading/empty/error |
| Assignment Detail | — | No dedicated detail API; **Open** → `/complaints/[id]` |

## 3. Backend APIs consumed

| ID | Endpoint | Use |
|---|---|---|
| API-388 | `GET /api/v1/complaints/search` | List base + filter/sort/page |
| API-206 | `GET /api/v1/complaints/{id}/assignments` | Current + previous assignee |
| API-205 | `POST /api/v1/complaints/{id}/assign` | Assign and Reassign (`reason` required on reassign) |
| API-403 | `POST /api/v1/complaints/{id}/unassign` | Cancel assignment |
| API-223 | `GET /api/v1/branches` | Branch labels / filter |
| API-214 | `GET /api/v1/users` | Assignee picker + filter |

No mocked APIs. No backend or contract changes. Domain API-401/402 not used (legacy API-205 already covers assign/reassign on the mounted path).

## 4. Assignment actions

| Action | Permission | API |
|---|---|---|
| Assign | `complaints:assign` | API-205 (no current assignee) |
| Reassign | `complaints:assign` | API-205 + required `reason` |
| Cancel | `complaints:assign` | API-403 |
| Open | `complaints:read` | Complaint Detail |

## 5. Known limitations

- No global `/assignments` list API — list is complaint search + per-row history enrichment.
- Previous assignee is best-effort from API-206 history (newest non-current).
- Cancel (API-403) may fail for some legacy rows — error shown in confirm dialog.
- Backend assign is limited to complaint statuses NEW/ASSIGNED; other statuses surface API errors.
- Domain `POST …/reassign` (API-402) not wired; reassign goes through API-205.

## 6. Commit

`git log -1 --oneline -- frontend/`
