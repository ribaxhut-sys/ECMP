# DEC-022 — Upstream Org Restructure / Orphan Remediation (O-07)

| Field | Value |
|---|---|
| ID | DEC-022 |
| Version | 0.1 |
| Date | 2026-07-31 |
| Owner | Solution Architect / Business Owner |
| Reviewer | Security Architect / PMO |
| Approver | Architecture Board / Business Owner (pending) |
| Status | 🟡 **Proposed** |
| Related | ADR-018 O-07; SEC-ORG-SYNC-001; PROGRAM-ORG-GAP-DELIVERY-001 |
| Mode B | Does **not** unlock Mode B |

---

## 1. Context

When Enterprise Platform retires or restructures org units, live complaints may still reference former `organization_id` / `branch_id` / `department_id`. ADR-018 forbids inventing replacement hierarchy; remediation policy was deferred (O-07).

---

## 2. Decision (Proposed)

**Until this DEC is Accepted, interim operating rule:**

1. **Do not** silently rewrite historical Organization References on complaints to a “new” unit invented by ECMP.
2. **Do not** fabricate projection rows to keep AuthZ open.
3. For **new** AuthZ decisions: if required refs are unresolvable or marked inactive per fail-closed rules → **deny** (ADR-018 §14).
4. Historical complaint **read** of past references remains for audit/integrity; write/transition that depends on live scope may deny.

**Working recommendation for future Accept (pick one primary + optional break-glass):**

| Option | Description | Lean |
|---|---|---|
| A — Retain historical refs; block new scoped actions if inactive/unresolvable | Preserves audit; fail closed | **Recommended default** |
| B — Controlled re-scope workflow (human-approved map old→new) | Needs UX + audit trail | Later enhancement |
| C — Auto-map via EP restructure event | Requires trusted EP signal + Event Catalog | Only after O-02 Board need |

Break-glass re-scope (Option B) must be audited and must not be Mode A password bypass.

---

## 3. Consequences if Accepted later

- Sync job marks projections inactive; does not delete history needed for complaint FK integrity
- Ops runbook for Option B (if chosen) before production enterprise customer

---

## 4. Non-goals

- No Event Catalog entries invented here
- No Mode B unlock
- No schema authorization

---

## 5. Open

Await Business Owner / Architecture Board Accept.

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-31 | Proposed — retain + fail-closed interim |

---

*End of DEC-022.*
