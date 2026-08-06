# Batch B3 — Implementation Summary

| Field | Value |
|---|---|
| Batch | B3 — Intake (WF-001-R1) |
| Date | 2026-08-05 |
| Status | Complete |

## Scope delivered

- **SCR-WS-01** New Intake — customer reference lookup, intake form (subject / description / category / channel / priority), completeness checklist, Hold to complete, Forward / Register when complete
- **SCR-WS-02** Follow-up — active-case context, follow-up notes, Save follow-up (no duplicate primary)
- Shared mock repo extended: register intake → `REGISTERED`, held drafts, follow-up notes, customer reference cache
- Active-case routing from New Intake → Follow-up (blocks duplicate register)
- After register / hold / follow-up: remain on workspace (not Queue)

## Explicitly out of scope

Officer Queue changes · Supervisor Queue changes · Assignment · Timeline · Approval · Submit for Review · Case Management · Evidence workflow · Dashboard · Backend / API / DB · Real AuthN · Mode B · Batch B4+

## Files added

| Path | Role |
|---|---|
| `src/features/intake/components/IntakeWorkspace.tsx` | SCR-WS-01 |
| `src/features/intake/components/CustomerReferencePanel.tsx` | Customer lookup |
| `src/features/intake/components/IntakeFormFields.tsx` | Intake fields |
| `src/features/intake/components/CompletenessChecklist.tsx` | Completeness side panel |
| `src/features/intake/components/RegisterConfirmDialog.tsx` | Register confirm |
| `src/features/intake/components/FollowUpWorkspace.tsx` | SCR-WS-02 |
| `src/features/intake/components/FollowUpContext.tsx` | Follow-up context / summary |
| `src/features/intake/index.ts` | Barrel |
| `src/app/(app)/workspace/follow-up/[id]/page.tsx` | Follow-up route |
| `docs/B3_IMPLEMENTATION_SUMMARY.md` | This summary |

## Files modified

| Path | Change |
|---|---|
| `src/features/supervisor-assign/mock/assignmentRepository.ts` | B3 fields + register / hold / follow-up / customer lookup |
| `src/features/supervisor-assign/mock/useAssignmentRepository.ts` | Expose B3 actions |
| `src/features/supervisor-assign/mock/assignmentRepository.test.ts` | B3 tests |
| `src/features/supervisor-assign/index.ts` | Export B3 APIs |
| `src/shared/config/uiBatch.ts` | `B3`, `getShellBatchOverlineKey` |
| `src/shared/config/uiBatch.test.ts` | B3 coverage |
| `src/app/(app)/workspace/page.tsx` | B3 → IntakeWorkspace |
| B1/B2 overline consumers | Use `getShellBatchOverlineKey()` |
| `messages/en.json`, `messages/id.json` | `intake` + shell B3 |
| `.env.example`, `.env.local` | `NEXT_PUBLIC_ECMP_UI_BATCH=B3` |

## Components created

IntakeWorkspace · CustomerReferencePanel · IntakeFormFields · CompletenessChecklist · RegisterConfirmDialog · FollowUpWorkspace · FollowUpContext

## Components reused

AppLayout · PermissionGuard · WorkspaceLayout · PageHeader · Card · Badge · Button · Input · Select · Textarea · Modal · Alert · Empty · Supervisor mock repo / B0 nav / mockAuth

## Verification

```bash
cd frontend
# NEXT_PUBLIC_ECMP_UI_BATCH=B3
npm run typecheck && npm run lint && npm run check:i18n
npm test -- src/features/supervisor-assign src/shared/config/uiBatch.test.ts
npm run build
# login officer / mock → Workspace → lookup Hana → register
# lookup Ayu / Eko → Open follow-up → Save follow-up
# Hold incomplete draft → resume → Forward/Register
# login supervisor / mock → Assign still works (B1)
# officer handling mode → Queue + Handle still works (B2)
```
