# Batch B0 — Implementation Summary

| Field | Value |
|---|---|
| Batch | B0 — Running Application Shell (WF-001-R1) |
| Date | 2026-08-05 |
| Status | Complete |

## Scope delivered

- Login (username / password / Sign in / Forgot password link)
- Global shell: Header + Sidebar + content area (reused `AppLayout`)
- Persona-aware B0 navigation (`/workspace`, `/queue`, `/settings`)
- Breadcrumb via `PageHeader` on placeholders
- `WorkspaceLayout`, `EmptyWorkspace`, `PermissionGuard`, `LoadingScreen`
- Mock authentication (4 personas) — no backend required when `NEXT_PUBLIC_ECMP_UI_BATCH=B0`
- Officer work-mode toggle (intake ↔ handling)
- Responsive layout (existing sidebar drawer + tokens)
- Theme tokens unchanged (reuse)

## Out of scope (honoured)

Complaint list/detail, timeline, assignment, approval, dashboard KPI, search logic, API/DB.

## Files added

| Path | Role |
|---|---|
| `src/shared/config/uiBatch.ts` | Batch / mock gates |
| `src/auth/mockAuth.ts` | Mock personas + sessionStorage |
| `src/auth/mockAuth.test.ts` | Unit tests |
| `src/shared/layouts/app-layout/b0Nav.ts` | B0 nav catalog |
| `src/shared/layouts/app-layout/b0Nav.test.ts` | Unit tests |
| `src/shared/layouts/shell/*` | WorkspaceLayout, EmptyWorkspace, PermissionGuard, LoadingScreen |
| `src/features/shell/*` | ShellPlaceholderPage |
| `src/app/(app)/workspace/page.tsx` | Intake / Manager placeholder |
| `.env.local` | `NEXT_PUBLIC_ECMP_UI_BATCH=B0` (gitignored) |

## Files modified

| Path | Change |
|---|---|
| `src/auth/AuthProvider.tsx` | Mock session path + work mode |
| `src/shared/layouts/app-layout/Sidebar.tsx` | B0 nav + home href |
| `src/shared/layouts/app-layout/Header.tsx` | Disable search in B0; work-mode toggle |
| `src/shared/layouts/app-layout/index.ts` | Export B0 nav |
| `src/shared/layouts/index.ts` | Export shell components |
| `src/app/login/page.tsx` | Mock demo accounts + entry redirect |
| `src/app/(app)/queue/page.tsx` | B0 placeholder vs existing queue |
| `src/app/page.tsx` | B0 → `/workspace` |
| `messages/en.json`, `messages/id.json` | `shell` + `nav.workspace` |
| `.env.example` | Document batch/mock env |

## Components created

WorkspaceLayout · EmptyWorkspace · PermissionGuard · LoadingScreen · ShellPlaceholderPage · B0_NAV_* · mockAuth

## Components reused

AppLayout · Header · Sidebar · RequireAuth · AuthenticatedShell · AuthLayout · IdentityBrand · PageHeader · Breadcrumb · PageContainer · Button · Input · Card · Alert · Skeleton · LanguageSwitcher · theme tokens

## Technical decisions

1. **Reuse shell, don’t rewrite** — B0 switches nav/auth via `NEXT_PUBLIC_ECMP_UI_BATCH=B0`; legacy `APP_NAV_ITEMS` intact for non-B0.
2. **Mock auth only in B0** — sessionStorage; passwords any non-empty for known usernames (`officer`, `supervisor`, `manager`, `admin`).
3. **Placeholders on `/workspace` and `/queue` in B0** — real queue view remains for non-mock sessions.
4. **Manager** — no nav items; landing explains deferred dashboard (BC-8.4 / WF-001-R1).
5. **No locked UX/business docs modified.**

## How to run

```bash
cd frontend
# ensure .env.local has NEXT_PUBLIC_ECMP_UI_BATCH=B0
npm run build && npm run start
# open http://localhost:3000/login — demo: officer / mock
```

## Validation

- `npm run typecheck` — pass
- `npm run lint` — pass
- `npm run check:i18n` — pass
- unit tests b0Nav + mockAuth + nav — pass
- `npm run build` — pass (after oxide platform binary present)
- `npm run start` — Ready; `/login`, `/workspace` routes present
