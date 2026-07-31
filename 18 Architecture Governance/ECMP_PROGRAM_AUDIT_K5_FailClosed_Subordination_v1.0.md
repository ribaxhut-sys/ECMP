# PROGRAM — Audit K-5 Fail-Closed Subordination Remediation

| Field | Value |
|---|---|
| Document ID | GOV-AUDIT-K5-001 |
| Program | PROGRAM-AUDIT-K5-001 |
| Version | 1.0 |
| Date | 2026-07-30 |
| Prepared by | ECMP Documentation Administrator / Solution Architect |
| Audience | Architecture Board / Security Architect / PMO |
| Status | 🟢 **Recorded — Authoring remediation complete** |
| Related audit | Independent Program Audit 2026-07-30 — **K-5** / BLK-06 |
| Board Accept of ADR-016/017/018? | **Yes** — **Accepted with Conditions** (PROGRAM-BOARD-006 **BR-011** / **BR-012** / **BR-013**; C-B6-1…C-B6-7); Mode B remains **CLOSED** |

---

## 1. Purpose

Close audit **K-5** by removing the ADR-018 §14 “governance profile allows” fail-open lever and aligning ADR-017 §13 / ADR-018 §15 with the ADR-016 §9.3 subordination standard — **without inventing** a Board Accept Resolution for ADR-016/017/018.

---

## 2. Problem (audit finding)

ADR-018 §14 previously allowed degraded AuthZ posture when a “governance profile allows,” while §15 placed sync profiles under Integration/Architecture change control **below** Architecture Board — creating a path to loosen fail-closed AuthZ without Board.

---

## 3. Remediation applied (Proposed ADR bodies)

| ADR | Change |
|---|---|
| ADR-016 §9.3 | Expanded subordination standard: profiles must not loosen fail-closed rules; Board required for any relaxation; cross-ref 017/018 |
| ADR-017 §13 | Explicit fail-closed subordination row aligned to ADR-016 §9.3 |
| ADR-018 §14 | Sync-unavailable row rewritten: last-known only if refs resolvable; **no** profile-granted degraded allow; Board required for exceptions; new prohibited behavior #7 |
| ADR-018 §15 | Fail-closed subordination row + Mode B org-gap prerequisite cross-ref |

Document history rows: ADR-016/017/018 **1.0a** (2026-07-30).

---

## 4. Board disposition (PROGRAM-BOARD-006)

PROGRAM-BOARD-005 Review completed; PROGRAM-BOARD-006 **Accepted with Conditions** ADR-016/017/018 including 1.0a fail-closed subordinations.

1. C-B6-2 adopts ADR-016 §9.3 subordination as binding.
2. This remediation file is evidence of authoring; Accept authority is BOARD-006.
3. Any future fail-closed relaxation still requires a subsequent Board Resolution.

---

## 5. Explicit Non-Authority

- Does not Accept ADR-016, ADR-017, or ADR-018
- Does not unlock Mode B (C-7 CLOSED)
- Does not authorize Identity Adapter / OpenAPI enterprise `securitySchemes`

| Rev | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | Audit K-5 authoring remediation recorded |
