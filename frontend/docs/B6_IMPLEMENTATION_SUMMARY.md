# Batch B6 — Implementation Summary

| Field | Value |
|---|---|
| Batch | B6 — Queue Supervisor full priority (WF-001-R1) |
| Date | 2026-08-05 |
| Status | Complete |

## Scope delivered

- **SCR-Q-02 complete** — fixed priority segments:
  1. New Escalation (visible; action **stub** — no SCR-WS-11)
  2. SLA at-risk / overdue
  3. Unassigned (B1 reused)
- **Pending approval** segment from B5 preserved (after SLA, before Unassigned)
- Escalation count banner
- Mock seeds: `cmp-b6-esc-001`, `cmp-b6-sla-001`

## Explicitly out of scope

SCR-WS-11 · Escalation handling workflow · History · Timeline · Mode B · Backend/API/DB · New status transitions

## Files added

| Path | Role |
|---|---|
| `src/features/supervisor-assign/components/PriorityQueueCards.tsx` | Escalation + SLA cards + banner |
| `docs/B6_IMPLEMENTATION_SUMMARY.md` | This summary |

## Files modified

| Path | Change |
|---|---|
| `src/features/supervisor-assign/mock/assignmentRepository.ts` | `escalationNew`, list helpers, B6 seeds |
| `src/features/supervisor-assign/mock/useAssignmentRepository.ts` | Expose B6 lists |
| `src/features/supervisor-assign/mock/assignmentRepository.test.ts` | B6 tests |
| `src/features/supervisor-assign/index.ts` | Export B6 APIs |
| `src/features/supervisor-assign/components/SupervisorQueue.tsx` | Priority segment order |
| `src/shared/config/uiBatch.ts` | `B6` |
| `src/shared/config/uiBatch.test.ts` | B6 coverage |
| `messages/en.json`, `messages/id.json` | `supervisorQueuePriority` + shell B6 |
| `.env.example`, `.env.local` | `NEXT_PUBLIC_ECMP_UI_BATCH=B6` |

## Components created

EscalationQueueCard · SlaRiskQueueCard · EscalationCountBanner

## Components reused

SupervisorQueue · AssignmentCard · PendingReviewCard · WorkspaceLayout · PageHeader · Empty · Badge · Button · Card · Alert · mock repo / B0–B5

## Verification

```bash
cd frontend
# NEXT_PUBLIC_ECMP_UI_BATCH=B6
npm run typecheck && npm run lint && npm run check:i18n
npm test -- src/features/supervisor-assign src/shared/config/uiBatch.test.ts
npm run build
# Confirm no /queue/escalation or SCR-WS-11 route
# supervisor / mock → Queue order: Escalation → SLA → Pending → Unassigned
# Escalation “Handle” disabled (stub)
```
