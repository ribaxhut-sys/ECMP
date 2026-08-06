# Batch R2-B1 — Implementation Summary

| Field | Value |
|---|---|
| Batch | R2-B1 — Reject Continuity (WF-001-R2) |
| WF ID | WF-001-09 |
| Screens | SCR-WS-06 · SCR-HX-01 (embedded portion) |
| Date | 2026-08-05 |
| Status | Complete (mock-only) |

## Done Definition (repository)

> Setelah Reject R1: Officer buka case → lihat alasan reject → resubmit → `PENDING_REVIEW`

## Scope delivered

- **SCR-WS-06** Rejected Resubmission workspace (`/queue/resubmit/[id]`)
- **SCR-HX-01** Decision History panel embedded (reject reason + reviewer + time)
- Reject reason mandatory on Supervisor Reject (unchanged B5) + persisted in `decisionHistory`
- Resubmit → `PENDING_REVIEW` → Return to Queue
- Return to active handling via `?continuity=edit` on SCR-WS-04
- Continuity gate: resubmit blocked without REJECT history
- Seed `cmp-r2b1-001` for Officer demo
- Queue badge **Rejected** + route to SCR-WS-06 when R2B1+

## Explicitly out of scope

Reopen · Escalation · SCR-WS-07/08/11/12 · SCR-HX-02 · SCR-SV-01/02 · Backend/API/DB · Mode B · R2-B2+

## Files Added

| Path | Role |
|---|---|
| `src/features/rejected-resubmission/components/RejectedResubmissionWorkspace.tsx` | SCR-WS-06 |
| `src/features/rejected-resubmission/components/DecisionHistoryPanel.tsx` | SCR-HX-01 embedded |
| `src/features/rejected-resubmission/components/RejectionContinuityBanner.tsx` | Reject highlight |
| `src/features/rejected-resubmission/index.ts` | Barrel |
| `src/app/(app)/queue/resubmit/[id]/page.tsx` | Route |
| `docs/R2B1_IMPLEMENTATION_SUMMARY.md` | This summary |

## Files Modified

| Path | Change |
|---|---|
| `src/features/supervisor-assign/mock/assignmentRepository.ts` | `decisionHistory`, reject/submit/approve history, helpers, seed |
| `src/features/supervisor-assign/mock/useAssignmentRepository.ts` | Expose R2-B1 APIs |
| `src/features/supervisor-assign/mock/assignmentRepository.test.ts` | Continuity + resubmit tests |
| `src/features/supervisor-assign/index.ts` | Exports |
| `src/features/officer-handle/components/OfficerQueue.tsx` | Route to resubmit |
| `src/features/officer-handle/components/OfficerQueueCard.tsx` | Rejected badge |
| `src/features/officer-handle/components/HandlingWorkspace.tsx` | Redirect / return-to-handling |
| `src/features/approval-review/components/ApprovalWorkspace.tsx` | Comment (history on reject) |
| `src/shared/config/uiBatch.ts` | `R2B1` gate |
| `src/shared/config/uiBatch.test.ts` | R2B1 coverage |
| `messages/en.json`, `messages/id.json` | `rejectedResubmission` + shell |
| `.env.example`, `.env.local` | `NEXT_PUBLIC_ECMP_UI_BATCH=R2B1` |

## Components Created

RejectedResubmissionWorkspace · DecisionHistoryPanel · RejectionContinuityBanner

## Components Reused

HandlingContext · ResolutionSummary · EvidenceListMin · EvidenceChecklist · SubmitConfirmDialog · WorkspaceLayout · PermissionGuard · PageHeader · Timeline · Badge · Alert · Modal · Button · Officer queue / mock repo / B0–B6 shell

## Verification Steps

```bash
cd frontend
# NEXT_PUBLIC_ECMP_UI_BATCH=R2B1
npm run typecheck && npm run lint && npm run check:i18n
npm test -- src/features/supervisor-assign src/shared/config/uiBatch.test.ts
npm run build
# Login officer → Queue → open Rejected seed (CMP-2026-0805-301)
#   → see HX-01 reject reason → correct → Resubmit → PENDING_REVIEW → Queue
# Login supervisor → reject another pending → officer opens → SCR-WS-06
# Return to active handling → progress notes → Continue resubmit
# B0–B6 paths remain available under R2B1 (isBatchAtLeast)
```
