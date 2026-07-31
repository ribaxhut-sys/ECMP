# DEC-021 — Organization Hierarchy Descendant Scope (O-06)

| Field | Value |
|---|---|
| ID | DEC-021 |
| Version | 0.1 |
| Date | 2026-07-31 |
| Owner | Solution Architect |
| Reviewer | Security Architect / Business Owner |
| Approver | Architecture Board / Business Owner (pending) |
| Status | 🟡 **Proposed** |
| Related | ADR-018 O-06; SEC-ORG-SYNC-001; PROGRAM-ORG-GAP-DELIVERY-001 |
| Mode B | Does **not** unlock Mode B |

---

## 1. Context

ADR-018 defers **hierarchy traversal / descendant scope semantics** (O-06). Silent expansion (e.g. “user at org sees all descendant branches”) is a high AuthZ risk if assumed in code.

---

## 2. Decision (Proposed)

**Until this DEC is Accepted:**

1. ECMP AuthZ **MUST NOT** expand Organization References to descendant units.
2. Scope evaluation uses **exact** resolved `organization_id` / `branch_id` / `department_id` on the identity (and complaint scope rules already defined for Mode A), not inferred children.
3. Ambiguous hierarchy → **deny** unsafe expansion (align ADR-018 R-08).

**Working recommendation for future Accept (not in force until Accepted):**

| Option | Description | Lean |
|---|---|---|
| A — Exact-ref only (no descendants) | Simplest; safest | **Recommended default** |
| B — Explicit descendant allowlist claim | EP supplies allowed child set | Possible later |
| C — Full subtree walk from org projection | Requires EP tree integrity + policy | Highest risk; defer |

---

## 3. Consequences if Accepted later

- AuthZ libraries must not implement recursive branch walks without citing Accepted DEC-021 Option B/C
- Org sync projections may store parent links for display/reporting without using them for AuthZ expansion

---

## 4. Non-goals

- Does not define Complaint Roles
- Does not unlock Mode B
- Does not authorize schema

---

## 5. Open

Await Business Owner / Architecture Board Accept or revise Options.

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-31 | Proposed — exact-ref only interim rule |

---

*End of DEC-021.*
