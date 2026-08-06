# Batch B4 — Implementation Summary

| Field | Value |
|---|---|
| Batch | B4 — Submit (WF-001-R1) |
| Date | 2026-08-05 |
| Status | Complete |

## Scope delivered

- **SCR-WS-05** Submit for Review — resolution summary, C-EVID-MIN list, evidence checklist, confirm submit, Cancel → SCR-WS-04
- Transition: `IN_PROGRESS` → `PENDING_REVIEW` → Return Q-01
- Submit CTA enabled from SCR-WS-04 when Batch B4+
- Mock repo: `PENDING_REVIEW`, `resolutionSummary`, `evidenceItems`, `submitForReview`, `addMinimalEvidence`

## Explicitly out of scope

Approve · Reject · Return to Branch · Supervisor decision · Timeline · Dashboard · Formal Evidence Supporting Views (R2) · Backend/API/DB · Mode B · Batch B5+

## Files added

| Path | Role |
|---|---|
| `src/features/submit-review/components/SubmitWorkspace.tsx` | SCR-WS-05 |
| `src/features/submit-review/components/ResolutionSummary.tsx` | Resolution input |
| `src/features/submit-review/components/EvidenceListMin.tsx` | C-EVID-MIN |
| `src/features/submit-review/components/EvidenceChecklist.tsx` | “Bukti cukup?” |
| `src/features/submit-review/components/SubmitConfirmDialog.tsx` | Confirm submit |
| `src/features/submit-review/index.ts` | Barrel |
| `src/app/(app)/queue/submit/[id]/page.tsx` | Submit route |
| `docs/B4_IMPLEMENTATION_SUMMARY.md` | This summary |

## Files modified

| Path | Change |
|---|---|
| `src/features/supervisor-assign/mock/assignmentRepository.ts` | B4 status + submit/evidence |
| `src/features/supervisor-assign/mock/useAssignmentRepository.ts` | Expose B4 actions |
| `src/features/supervisor-assign/mock/assignmentRepository.test.ts` | B4 tests |
| `src/features/supervisor-assign/index.ts` | Export B4 APIs |
| `src/features/officer-handle/components/HandlingWorkspace.tsx` | Enable Submit CTA (B4+) |
| `src/shared/config/uiBatch.ts` | `B4` |
| `src/shared/config/uiBatch.test.ts` | B4 coverage |
| `messages/en.json`, `messages/id.json` | `submitReview` + shell B4 |
| `.env.example`, `.env.local` | `NEXT_PUBLIC_ECMP_UI_BATCH=B4` |

## Components created

SubmitWorkspace · ResolutionSummary · EvidenceListMin · EvidenceChecklist · SubmitConfirmDialog

## Components reused

WorkspaceLayout · PermissionGuard · PageHeader · Card · Badge · Button · Input · Textarea · Modal · Alert · Empty · HandlingWorkspace CTA · mock repo / B0–B3

## Verification

```bash
cd frontend
# NEXT_PUBLIC_ECMP_UI_BATCH=B4
npm run typecheck && npm run lint && npm run check:i18n
npm test -- src/features/supervisor-assign src/shared/config/uiBatch.test.ts
npm run build
# officer / mock → Queue → open IN_PROGRESS → Submit for review
# fill resolution → confirm → returns to Q-01 (item gone from assigned queue)
# Cancel → back to SCR-WS-04
# supervisor assign (B1) + intake (B3) still work
```
