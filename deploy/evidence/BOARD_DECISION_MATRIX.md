# BOARD DECISION MATRIX — Mode A Batch-1

| Field | Value |
|---|---|
| Document ID | BOARD-MX-MA-B1-001 |
| Date | 2026-08-01 |
| SHA / Branch | `1608245` / `feature/cm-batch1-s2-persistence` |
| Approvals in this file | **None** |
| Rule | Recommended Option = prepared lean only; Status remains open until Board records a vote |

| Decision | Description | Available Options | Recommended Option | Impact | Risk | Owner | Status |
|---|---|---|---|---|---|---|---|
| B-1 DEC ID Collision | Two files share DEC-020; two share DEC-021 (different topics). Citations ambiguous until renumber policy chosen. Ref: `DEC_ID_Collision_Register_20260801.md` | **A** Keep O-06 as DEC-021; renumber G2 → DEC-023 (+ citations). **B** Keep G2 as DEC-021; renumber O-06 → next free ID (+ OQ/ADR-018 citations). **C** Keep both files; introduce explicit suffixes via new numbering policy | **A** (executed decision) | Documentation integrity; citation cleanup across G2 / OQ / ADR-018; no Mode B unlock; no Approved substance rewrite | High if unresolved (wrong DEC meaning in audits); Medium execution risk if citations missed | Architecture Board / PMO | **APPROVED — Option A** (`EXT-HD-RC-MA-B1-20260801`) |
| B-2 Release Tag Strategy | REL-TAG-001 forbids annotated release tags on feature-branch tips without merge to default branch or explicit waiver. Tip is on `feature/cm-batch1-s2-persistence` | **A** Merge to `main` → create RC tag. **B** Temporary Lab Waiver → create RC tag on feature branch | **B** (executed decision) | Determines legal tag ref; gates CHANGELOG/SemVer cut sequence; Option A may surface merge/W-D07 issues; Option B creates policy exception | High either path if unmanaged: A = merge risk; B = policy/exception risk and lab-only tag confusion | Architecture Board + Release Manager | **APPROVED — Option B** (`EXT-HD-RC-MA-B1-20260801`) |
| B-3 Mode B posture for this RC | Confirm Mode B remains closed for Mode A Batch-1 lab RC path | **Keep CLOSED** (in-scope). Unlock Mode B = **out of scope** for this meeting | Keep CLOSED | Preserves ADR-014/015 deferred impl; avoids inventing IdP contract | High if unlocked without real IdP contract | Board (affirm) / SA / Security | **PENDING HUMAN DECISION** (affirmation) |
| B-4 SemVer RC identity | Choose `vX.Y.Z-rc.N` for Mode A Batch-1; avoid colliding meaning with foundation `v1.0.0` line | Board may defer detail to RM within chosen tag path; SemVer string itself is RM/PMO choice | **v1.1.0-rc.1** | Enables CHANGELOG section + annotated tag message | High if tag cut without identity | Release Manager / PMO | **COMPLETE — v1.1.0-rc.1** (`EXT-HD-RC-MA-B1-20260801`) |
| B-5 Proceed to post-Board human gates | After B-1/B-2: authorize owners to collect U-5 + REL-RC-001 signatures and freeze tree (no auto-sign) | **Authorize sequence** / **Defer RC path** | Authorize sequence only after B-1 and B-2 recorded | Unblocks RC preparation work; does **not** equal READY FOR RC | Medium if Board authorizes without resolving B-1/B-2 | Board chair → RM / TL / SA / BO / QA | **PENDING HUMAN DECISION** |

---

## Explicit non-decisions (out of Board invent-scope today)

| Item | Status |
|---|---|
| Production Enterprise Ready | Not proposed |
| Full Mixed VPS promote | Not authorized (RAB limited scope) |
| FR-030 / FR-040 implementation | DEFER (Mode A DoD) |
| API / DB / ADR Approved body changes | Forbidden in this pack |
| Forged U-5 / REL-RC-001 / Security signatures | Forbidden |

---

*Votes must be recorded outside this matrix (minutes / Board record). Do not fill vote cells here via automation.*
