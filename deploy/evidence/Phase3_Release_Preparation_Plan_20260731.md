# Phase 3 — Release Preparation Plan (Archive)

| Field | Value |
|---|---|
| Date | 2026-07-31 |
| Status | APPROVED PLAN (not executed) |
| Bound strategy | Release Branch + selective cherry-pick; no merge/rebase VPS `main` |

## Locked assumptions

- SoT: `origin/feature/cm-batch1-s2-persistence`
- Draft branch name: `release/cm-batch1-vps-sync` (or agreed equivalent)
- KEEP: `ad4a373`
- SPLIT: `96f52eb`, `2f1348a`, `a476ebf`, `41a0f48`
- Pick order after SPLIT: `96f52eb` → `2f1348a` → `a476ebf` → `ad4a373` → `41a0f48`

## DoR (may create branch + cherry-pick only when all true)

A-01 Base SHA locked · A-02 Split plans approved · A-03 Overlap note · A-04 behind-14 acceptance · A-05 Security PASS · A-06 Deployment PASS · A-07 Rollback pack · A-08 Evidence pack · A-09 Product scope · A-10 Go

Phase 3 stops at planning. Cut = Phase 5 after re-RAB GO.
