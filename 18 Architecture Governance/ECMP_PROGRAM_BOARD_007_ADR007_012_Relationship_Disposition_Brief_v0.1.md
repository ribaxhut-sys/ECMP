# PROGRAM-BOARD-007 — ADR-007 / ADR-012 Relationship Disposition Brief (Draft)

| Field | Value |
|---|---|
| Document ID | GOV-BR-BOARD-007-BRIEF |
| Version | 0.1 |
| Status | 🟡 **Draft — Pending Architecture Board Decision** |
| Date | 2026-07-31 |
| Owner | Solution Architect / Board Secretary (draft) |
| Approver | Architecture Board (not yet convened for this disposition) |
| Closes | Independent review **REC-01**; PROGRAM-BOARD-004 **F-7**; PROGRAM-BOARD-006 **C-B6-6** / **F-5** |
| Does **not** | Unlock Mode B; Accept new ADRs; rewrite ADR-014/015 normative text; authorize entitlement/SSO coding |

## 1. Purpose

Close the open **Relationship Pending** disposition between:

- **ADR-007** — Authentication Architecture (slice / target AuthN)
- **ADR-012** — Target Authentication Architecture (SEC-AUTH-001 / IdP baseline)

relative to the **Accepted with Conditions** enterprise package:

- **ADR-014** v1.4 (BR-009) — ECMP as Enterprise Business Module
- **ADR-015** v1.3 (BR-010) — Enterprise Identity Contract (Bilateral)
- **ADR-016 / 017 / 018** (BR-011…013) — protocol / entitlement / org-sync **design** (Mode B implementation still **CLOSED**)

This brief does **not** invent Board acceptance. It packages options already disclosed in ADR-014 § Relationship / ADR-015 § Relationship so the Board can record one disposition.

## 2. Why this is still open (not a promotion gap)

| Audit / review claim | Fact after BOARD-004 / BOARD-006 |
|---|---|
| “Promote ADR-014/015 from Proposed” | **Already done** — Accepted with Conditions (BR-009 / BR-010) |
| “No entitlement architecture” | ADR-017 Accepted with Conditions; **implementation** gated by **C-7 / C-B6-1** |
| “REC-01 unanswered” | **Correct** — F-7 / C-B6-6 remain Pending |
| “Mode A permanent vs transitional undecided” | Partially implied (Mode A delivery authorized; Mode B deferred) but **IdP/local AuthN relationship** still needs explicit Board language |

**Category error to avoid:** scoring Mode A runtime against Mode B contract clauses (Entitlement Gate, full ADR-015 claim acceptance) as delivery defects while Mode B remains CLOSED.

## 3. Decision question for the Board

> Relative to Mode B (ADR-014 Entitlement Gate → ADR-015 identity acceptance → ADR-008 Role-Permission SoT), what is the status of **ADR-007** and **ADR-012**?

Board must pick **one row** (or a Board-defined “Other” that still answers both columns).

| Option ID | Disposition | AuthZ flow consequence | Claim vocabulary consequence |
|---|---|---|---|
| **D-1** | **Mode A–only** | ADR-007 / ADR-012 govern Mode A (lab / delivery hedge) only. Mode B access **never** authorized by ADR-012 AuthN success alone. | Historical claims (`sub`, `roles[]`, `orgUnitId`, …) are **not** Mode B SoT; Mode B uses ADR-015 only (after unlock). |
| **D-2** | **Subsumed** as Enterprise Platform IdP implementation detail | An IdP chosen under ADR-012 **may** implement Enterprise Platform AuthN, but Mode B still requires Entitlement Gate + ADR-008 after ADR-015 acceptance. Subsumption ≠ collapse AuthN→AuthZ. | Wire/token fields require **governed binding** (ADR-016+) to ADR-015; no silent redefine. |
| **D-3** | **Other (Board-defined)** | Must still state how Mode B relates to Entitlement Gate, Identity Contract, and ADR-008. | Claim reconciliation mandatory if historical vocabularies remain. |

**Recommended draft for discussion (not a decision):** **D-1 (Mode A–only)** for ADR-007 and ADR-012 as *applicability*, with a note that physical IdP product reuse under Mode B is allowed only via **D-2-style** binding after Mode B unlock — i.e. product reuse ≠ ADR-012 remaining the Mode B AuthZ SoT. Board may instead adopt pure **D-2** if it prefers a single narrative (“Keycloak/IdP becomes EP IdP”).

## 4. Companion question — Mode A hedge posture

Record explicitly (one sentence each):

1. **Mode A** remains the **authorized delivery hedge** under Implementation Authorization (AUTHORIZED WITH CONDITIONS) until a future Mode B unlock Resolution + org-gap prerequisite (C-B6-3) + cutover DEC.
2. Mode A local credential / users / shell surfaces are **expected** under the hedge; they are **not** evidence that ADR-014 Accept failed.
3. Mode A → Mode B **cutover** (user linking: local `users.id` remain FK anchors; `external_user_id` alternate key) requires a **separate Accepted DEC** — already stated in ADR-014; this brief does not author that DEC.

## 5. Out of scope (do not attach to this Resolution)

- Implementing Enterprise Entitlement Gate, ADR-015 claim gate, or enterprise OpenAPI `securitySchemes`
- Force-merging complaint SoT namespaces (DEC-020 unchanged)
- Superseding ADR-013 (BR-007)
- Rewriting ADR-014/015 claim tables
- Treating this brief as Mode B coding authorization

## 6. Mode A engineering note (already actionable without this Board vote)

Independent of REC-01: IdP JWT path (`JwtAuthenticationStrategy` + `RoleMapper`) must **not** pass through privileged codes `ADMIN` / `ADMINISTRATOR` / `SUPER_ADMIN` from IdP `roles[]` (aligns with ADR-014 “enterprise roles shall not automatically become ECMP roles”). Local HS256 / DB-assigned admin for Mode A lab remains separate. This is **containment hardening**, not Mode B Entitlement Gate.

## 7. Proposed Resolution skeleton (for Secretary when Board convenes)

> Architecture Board **DISPOSES** ADR-007 and ADR-012 relationship to the ADR-014/015 package as **\<D-1 | D-2 | D-3\>** under PROGRAM-BOARD-007 (**BR-0xx**).  
> Mode B / Batch-2 / Enterprise customer remain **CLOSED** (C-7 / C-B6-1 reaffirmed).  
> Follow-up: update Relationship tables / index footnotes on ADR-007, ADR-012, ADR-014, ADR-015 (**metadata / disposition lines only**); no normative claim rewrite.

## 8. Follow-up actions (after Board vote only)

| ID | Action | Owner |
|---|---|---|
| F-1 | Record BR id + chosen option on ADR-007 / ADR-012 / ADR-014 / ADR-015 Relationship rows | ADR Editor |
| F-2 | Update canonical ADR Index footnotes | Documentation Admin |
| F-3 | Communicate to FE (OD-FE-002) and Security that Mode B claim SoT remains ADR-015 | Tech Lead |
| F-4 | Do **not** start Mode B coding from this disposition alone | All |

## 9. Traceability

| Source | Item |
|---|---|
| Independent ADR-014 review | `REC-01` |
| PROGRAM-BOARD-004 | **F-7** |
| PROGRAM-BOARD-006 | **C-B6-6**, **F-5** |
| ADR-014 v1.4 | Relationship + ADR-012 disclosure options |
| ADR-015 v1.3 | Relationship (parallel proposals) |

## Document history

| Version | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-31 | Draft brief for Board convening; no decision recorded |
