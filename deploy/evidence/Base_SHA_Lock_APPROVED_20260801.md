# Base SHA Lock — APPROVED (Lab Operator)

| Field | Value |
|---|---|
| Date | 2026-08-01 |
| Status | **APPROVED** (WP-01) |
| Base ref | `origin/feature/cm-batch1-s2-persistence` |
| Base SHA (full) | `2bf779d136a96c1c167abbacb51bf6e9a215791f` |
| Base SHA (short) | `2bf779d` |
| Tip subject | `fix(ci): sort imports in secmig P5 atomic claim tests` |
| Verified at | 2026-08-01 (fetch origin) |
| Not allowed as base | VPS `main` @ `41a0f48` / current diverged tip |

## Decision

Release branch (when RAB authorizes Phase 5) **must** be cut from `2bf779d` unless a **newer** tip of the same SoT branch is re-locked in writing before cut.

If tip moves: re-run WP-01; do not silently advance.

## Approval

| Role | Name | Date | Decision |
|---|---|---|---|
| Tech Lead | Lab Operator (ribaxhut-sys / chat mandate 2026-08-01) | 2026-08-01 | **Approve** |
| Release Manager | Lab Operator (same; SoD waiver W-SOD-1) | 2026-08-01 | **Approve** |

Supersedes: `Base_SHA_Lock_DRAFT_20260731.md`
