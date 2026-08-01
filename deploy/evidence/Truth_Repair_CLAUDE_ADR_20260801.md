# Truth-repair note — CLAUDE.md + ADR-014/015 (2026-08-01)

| Field | Value |
|---|---|
| Status | Done (no new ADR IDs invented) |

## Finding

SoT Batch-1 already contains:

- `ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4.md` — Accepted with Conditions (Mode B Closed C-7)
- `ECMP_ADR_015_Enterprise_Identity_Contract_v1.3.md` — Accepted with Conditions (Bilateral; Mode B Closed C-7)

Earlier VPS tip / docs-branch CLAUDE referenced ADR-014/015 without guaranteeing those files were on the active branch. After PR #2 merge tip `6bae8aa`, files **exist**.

## Action

1. Restored/aligned root `CLAUDE.md` as working constitution (Bahasa Indonesia).  
2. Point section 3 at existing ADR-014/015 filenames — **do not** create competing Proposed ADR-014/015 stubs.  
3. Mode B remain **BLOCKED / CLOSED** per Board C-7 until bilateral IdP contract evidence — see `Mode_B_Blocked_Pending_IdP_Contract_20260801.md`.
