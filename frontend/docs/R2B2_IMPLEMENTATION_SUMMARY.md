# Batch R2-B2 — Implementation Summary

| Field | Value |
|---|---|
| Batch | R2-B2 — Reopen Chain (WF-001-R2) |
| WF IDs | WF-001-06 · WF-001-17 · WF-001-10 |
| Screens | SCR-WS-03 · SCR-WS-12 (+ HX-02 closure) · SCR-WS-07 (+ HX-01) |
| Date | 2026-08-05 |
| Status | Complete (mock-only) |

## Done Definition (repository)

> Intake route reopen → Supervisor approve/reject → Officer continuation + history

## Scope delivered

- **SCR-WS-03** Reopen Routing (`/workspace/reopen/[id]`)
- **SCR-WS-12** Reopen Approval (`/queue/reopen-review/[id]`) + **SCR-HX-02** closure portion
- **SCR-WS-07** Reopened Continuation (`/queue/reopened/[id]`) + **SCR-HX-01** continuation portion
- Mock transitions: `requestReopen` → `approveReopen`/`rejectReopen` → `continueReopened`
- Status `REOPENED`; seeds closed / pending / reopened
- Intake closed-case branch; Supervisor pending-reopen segment; Officer queue route

## Explicitly Out of Scope

SCR-WS-08/11 · Escalation · SCR-SV-01/02 · Backend/API/DB · Mode B · R2-B3+

## Files Added

| Path | Role |
|---|---|
| `features/reopen-routing/` | SCR-WS-03 |
| `features/reopen-approval/` | SCR-WS-12 + HX-02 + pending card |
| `features/reopened-continuation/` | SCR-WS-07 |
| `src/app/(app)/workspace/reopen/[id]/page.tsx` | Route WS-03 |
| `src/app/(app)/queue/reopen-review/[id]/page.tsx` | Route WS-12 |
| `src/app/(app)/queue/reopened/[id]/page.tsx` | Route WS-07 |
| `docs/R2B2_IMPLEMENTATION_SUMMARY.md` | This summary |

## Files Modified

| Path | Change |
|---|---|
| `assignmentRepository.ts` (+ test, hook, index) | Reopen state machine + seeds |
| `IntakeWorkspace.tsx` | Closed → WS-03 |
| `SupervisorQueue.tsx` | Pending reopen segment |
| `OfficerQueue.tsx` / `OfficerQueueCard.tsx` / `HandlingWorkspace.tsx` | REOPENED routing |
| `DecisionHistoryPanel.tsx` | `variant="reopen"` + reopen history types |
| `SubmitWorkspace.tsx` | Accept REOPENED |
| `uiBatch.ts` (+ test) | `R2B2` |
| `messages/en.json`, `id.json` | reopen namespaces |
| `.env.local`, `.env.example` | `R2B2` |

## Components Created

ReopenRoutingWorkspace · ReopenApprovalWorkspace · ClosureHistoryPanel · PendingReopenCard · ReopenedContinuationWorkspace

## Components Reused

DecisionHistoryPanel · HandlingContext · ProgressNotesPanel · Approval mutual-exclusive pattern · PermissionGuard · Timeline · Submit path · mock repo / R1–R2B1 shell

## Verification Steps

```bash
cd frontend
# NEXT_PUBLIC_ECMP_UI_BATCH=R2B2
npm run typecheck && npm run lint && npm run check:i18n
npm test -- src/features/supervisor-assign src/shared/config/uiBatch.test.ts
npm run build
# Officer intake → lookup CUST-3001 → Route reopen (WS-03)
# Supervisor → Pending reopen → Approve (WS-12 + HX-02) → Queue
# Officer → Reopened item → Continue (WS-07 + HX-01) → Submit
# Supervisor pending seed: Reject reopen keeps CLOSED
```
