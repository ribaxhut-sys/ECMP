# Sprint F6 — Frontend MVP Finish

**Status:** Complete  
**Scope:** Dashboard polish, search integration, navigation/UX/permission consistency before UAT.  
**Out of scope:** Redesign, architecture refactor, backend/API changes, React Query, notifications, theme, performance, a11y overhaul, UAT fixes.

## 1. Pages updated

| Area | Change |
|---|---|
| Dashboard | Wired status/branch/latest widgets; summary title; Suspense; `dashboard:read` gate |
| Header search | Submits to `/complaints?keyword=` (API-388 via list) |
| Complaints list | `complaints:read` / `complaints:create` gates on load + actions |
| Create Complaint | `complaints:create` gate + Empty state |
| Complaint Detail / Edit | Load failures use shared `ErrorState` |
| Settings / SLA | Loading → `Skeleton`; load error → `ErrorState`; deny → `Empty` |
| Quick Actions | Routes to Queue / Assignments / Resolutions |

## 2. Dashboard improvements

- API-319 overview (summary, SLA, recent activity)
- Reports by-status / by-branch widgets (existing report APIs)
- Latest complaints via API-388 `searchComplaints`
- Partial widget failures degrade to empty; overview failure → ErrorState
- Recent activity / latest rows link into Complaints
- Responsive grid: status + branch side-by-side on `lg+`

## 3. Search integration

- Header search → `/complaints?keyword=…` (no new global endpoint)
- Gated on `complaints:read`
- Tablet/mobile: search toggle in header
- List modules already used API-388 (Complaints, Queue, Assignments, Resolutions) — unchanged

## 4. Permission review

| Action | Permission |
|---|---|
| Dashboard view / refresh | `dashboard:read` |
| Header search | `complaints:read` |
| Complaints list / View | `complaints:read` |
| Create Complaint | `complaints:create` |
| Edit Complaint | `complaints:update` (existing) |
| Quick Actions | Per-action permission filter |
| Module row actions | Existing F2–F5 gates unchanged |

Unavailable actions are hidden (not disabled stubs).

## 5. Known limitations remaining

- Users module is implemented (list + admin reset); not an empty placeholder
- Notifications and theme controls remain disabled placeholders (out of scope)
- No dedicated global search API — header uses complaint search only
- Recent activity links by complaint number keyword (overview payload has no complaint id)
- Dashboard report widgets require report permissions; missing data shows empty, not hard fail
- Mobile layout is basic (drawer + header search); not mobile-optimized
- Attachment enrichment / list composition patterns from F3–F5 unchanged
- Reports page now wires API-210…212 (permission `reports:read`); advanced filters/export remain out of scope

## 6. Commit

`git log -1 --oneline -- frontend/`
