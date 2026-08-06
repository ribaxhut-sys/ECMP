# Batch B1 — Implementation Summary

| Field | Value |
|---|---|
| Batch | B1 — Supervisor Assign loop (WF-001-R1) |
| Date | 2026-08-05 |
| Status | Complete |

## Scope delivered

- **SCR-Q-02** Supervisor Queue — **Unassigned segment only** (REGISTERED complaints)
- **SCR-WS-09** Assignment Workspace — select unit → confirm → cancel
- Assignment flow: `REGISTERED` → visible in queue → assign unit → `ASSIGNED` → removed from unassigned queue
- Mock assignment repository (in-memory; no backend / API / DB)
- Supervisor-only access to Assignment Workspace via `PermissionGuard` (`shell:queue_supervisor`)
- Navigation: Supervisor Queue ↔ Assignment Workspace ↔ Back to Queue

## Out of scope (honoured)

Officer Queue · Complaint Detail · Timeline · Case · Approval · Escalation · Dashboard · Search redesign · Backend/API/DB · Real AuthN · Mode B · UX/governance doc changes

## Files added

| Path | Role |
|---|---|
| `src/features/supervisor-assign/mock/assignmentRepository.ts` | Mock complaints + units + assign |
| `src/features/supervisor-assign/mock/assignmentRepository.test.ts` | Unit tests |
| `src/features/supervisor-assign/mock/useAssignmentRepository.ts` | `useSyncExternalStore` hook |
| `src/features/supervisor-assign/components/SupervisorQueue.tsx` | SCR-Q-02 unassigned |
| `src/features/supervisor-assign/components/AssignmentCard.tsx` | Queue item card |
| `src/features/supervisor-assign/components/AssignmentWorkspace.tsx` | SCR-WS-09 |
| `src/features/supervisor-assign/components/UnitSelector.tsx` | Destination unit select |
| `src/features/supervisor-assign/components/AssignmentSummary.tsx` | Case context summary |
| `src/features/supervisor-assign/components/AssignmentConfirmation.tsx` | Confirm body |
| `src/features/supervisor-assign/components/AssignmentDialog.tsx` | Confirm modal |
| `src/features/supervisor-assign/index.ts` | Barrel |
| `src/app/(app)/queue/assign/[id]/page.tsx` | Assignment route |
| `src/shared/config/uiBatch.test.ts` | Batch gate tests |
| `docs/B1_IMPLEMENTATION_SUMMARY.md` | This summary |

## Files modified

| Path | Change |
|---|---|
| `src/shared/config/uiBatch.ts` | `isBatchB1`, `isShellUiBatch`; mock auth on B1 |
| `src/app/(app)/queue/page.tsx` | B1 supervisor → SupervisorQueue; officer placeholder |
| `src/app/(app)/workspace/page.tsx` | B1 overline |
| `src/app/page.tsx` | Shell batch → `/workspace` |
| `src/app/login/page.tsx` | Shell batch entry redirect |
| `src/auth/AuthProvider.tsx` | Shell batch mock login path |
| `src/shared/layouts/app-layout/Sidebar.tsx` | Shell batch nav |
| `src/shared/layouts/app-layout/Header.tsx` | Shell batch (no search) |
| `src/features/shell/ShellPlaceholderPage.tsx` | Officer deferred description key |
| `messages/en.json`, `messages/id.json` | `supervisorAssign` + shell B1 keys |
| `.env.example` | Document `B1` |
| `.env.local` | `NEXT_PUBLIC_ECMP_UI_BATCH=B1` (gitignored) |

## Components created

SupervisorQueue · AssignmentCard · AssignmentWorkspace · UnitSelector · AssignmentSummary · AssignmentConfirmation · AssignmentDialog

## Components reused

AppLayout · Header · Sidebar · WorkspaceLayout · EmptyWorkspace · PermissionGuard · PageHeader · Breadcrumb · Card · Badge · Button · Select · Modal · Alert · Empty · Skeleton · ShellPlaceholderPage · B0_NAV · mockAuth personas

## Technical decisions

1. **New feature folder `supervisor-assign`** — avoids colliding with API-backed `features/complaints/AssignmentCard` and `features/assignments/*`.
2. **Gate `NEXT_PUBLIC_ECMP_UI_BATCH=B1`** — includes B0 shell behaviour via `isShellUiBatch()`; mock auth stays on.
3. **In-memory store + `useSyncExternalStore`** — assign updates local state only; no persistence across full page reload (seed resets).
4. **Permission** — Assignment Workspace gated by `shell:queue_supervisor` (mock persona Supervisor). Officer/Manager/Admin see PermissionGuard fallback on `/queue/assign/[id]`.
5. **Officer `/queue` in B1** — remains placeholder (Batch B2). Supervisor gets SCR-Q-02 unassigned only (no SLA/escalation segments — B6).
6. **No locked UX/business docs modified.**

## How to run

```bash
cd frontend
# ensure .env.local has NEXT_PUBLIC_ECMP_UI_BATCH=B1
npm run build && npm run start
# open http://localhost:3000/login — demo: supervisor / mock
# Queue → open item → select unit → Confirm assign → item leaves Unassigned
```

## Validation

- `npm run typecheck`
- `npm run lint`
- `npm run check:i18n`
- `npm test` (assignmentRepository + uiBatch)
- `npm run build`
