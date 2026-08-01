# PROGRAM — Organization-Model Gap Delivery Plan v0.1 (Draft)

| Field | Value |
|---|---|
| Document ID | GOV-ORG-GAP-PLAN-001 |
| Program | PROGRAM-ORG-GAP-DELIVERY-001 |
| Version | 0.1 |
| Date | 2026-07-31 |
| Prepared by | Solution Architect / Documentation Administrator |
| Audience | Tech Lead / Security Architect / PMO / Architecture Board |
| Status | 🟡 **Draft** |
| Prerequisite record | `ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md` (K-7 / C-B6-3) |
| Integration profile | `ECMP_ORG_SYNC_INTEGRATION_PROFILE_v0.1.md` (SEC-ORG-SYNC-001) |
| Mode B unlock | **Not authorized** by this plan |
| Schema migration | **Not authorized** by this plan alone |

---

## 1. Purpose

Turn the binding Mode B org-gap **prerequisite** into a phased **delivery plan**: what to build, in what order, with what evidence — without unlocking Mode B or inventing Event Catalog / OpenAPI contracts prematurely.

---

## 2. Goal state (definition of “gap closed”)

ECMP can **resolve** ADR-015 required Organization References for AuthZ:

| Claim | Resolves to |
|---|---|
| `organization_id` | Non-authoritative projection row (enterprise opaque id) |
| `branch_id` | Non-authoritative projection row linked to organization |
| `department_id` | Non-authoritative projection row linked to organization (+ branch as required by profile) |

Fail-closed: any unresolvable required ref → **deny** scope-dependent AuthZ (ADR-018 §14).

Evidence bar remains SEC-ORG-SYNC-001 §8. Closing the gap **still requires** a separate Board Resolution to open C-B6-1 / C-7.

---

## 3. As-is vs to-be

| Layer | As-is | To-be (planned) |
|---|---|---|
| Organization | Missing | `organizations` projection (enterprise id PK/unique) |
| Branch | Mode A `branches` (`code`-centric, local) | Enterprise-aligned `branch_id` projection; coexistence with Mode A TBD in Phase B |
| Department | Missing | `departments` projection |
| Sync | N/A | Hybrid pull + login-time (SEC-ORG-SYNC-001) |
| SoR | N/A | Enterprise Platform (ECMP consume-only) |

---

## 4. Phased delivery (safe order)

### Phase A — Design freeze (docs only) — **this document + profiles**

| # | Work | Owner | Exit |
|---|---|---|---|
| A1 | Org Sync Integration Profile Draft | Integration / SA | SEC-ORG-SYNC-001 v0.1 **done** |
| A2 | This delivery plan | SA | This file |
| A3 | O-06 / O-07 Proposed DECs | SA / BO | DEC-021 / DEC-022 Proposed |
| A4 | EP bilateral on org id shapes | SA / EP | Pack P2 countersign |

**No code.** Mode B CLOSED.

### Phase B — Projection schema & Mode A coexistence design (requires separate delivery authorization)

| # | Work | Constraint |
|---|---|---|
| B1 | Conceptual DDL for `organizations` / `departments` / enterprise `branch_id` | ADR-018 non-SoR; soft-delete / `as_of` fields |
| B2 | Decision: evolve Mode A `branches` vs parallel enterprise projection table | Must not break Mode A complaint FKs without DEC |
| B3 | Alembic migration **only after** Tech Lead + SA delivery authorization citing this plan | Migration ≠ Mode B unlock |
| B4 | Repository/read APIs for resolvability checks (internal) | No enterprise OpenAPI `securitySchemes` |

**Still no Mode B AuthN.** May land under Mode A foundation hardening if authorized.

### Phase C — Sync adapters (pull + login-time hooks) — gated

| # | Work | Gate |
|---|---|---|
| C1 | EP org pull client (contract from bilateral pack) | EP API contract agreed |
| C2 | Login-time ensure-resolve hook behind **feature flag off by default** | Flag must not enable Mode B AuthN |
| C3 | Periodic reconciler job | Fail-closed metrics; no fabricate |
| C4 | Push/events | Only after Event Catalog Board-accepted need (O-02) |

### Phase D — Evidence & unlock eligibility (not unlock itself)

| # | Evidence | Maps to |
|---|---|---|
| D1 | Tests: missing org/branch/dept → deny | SEC-ORG-SYNC §8.2 |
| D2 | Tests: sync down + unresolvable → deny | §8.3 |
| D3 | Bilateral EP feed confirmation recorded | §8.4 |
| D4 | Board Mode B unlock Resolution (future) | C-B6-1 open — **separate** |

---

## 5. Dependencies

```
EP bilateral (P2) ──► Phase B/C contracts
DEC-021 (O-06)    ──► any descendant AuthZ feature
DEC-022 (O-07)    ──► restructure/orphan remediation jobs
Mode A coexistence DEC (future) ──► B2 branch strategy
BOARD unlock      ──► only after D1–D3 + C-B6-3 evidence
```

---

## 6. Risks

| Risk | Mitigation |
|---|---|
| Dual `branches` semantics confuse Mode A | Explicit B2 DEC before migration |
| Team treats Phase B as Mode B unlock | C-B6-1 reaffirmation in every phase exit |
| EP delay blocks ids | Keep projections empty → fail closed; no fake rows |
| Descendant scope assumed in code | DEC-021 Proposed default = no silent expansion |

---

## 7. Explicit Non-Authorization

- Mode B / Batch-2 / enterprise customer remain CLOSED
- No Identity Adapter / OD-FE-002 / OpenAPI enterprise schemes
- No Alembic commit authorized by this Draft alone
- No Event Catalog invention

---

## 8. Related

- `ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`
- `ECMP_ORG_SYNC_INTEGRATION_PROFILE_v0.1.md`
- `ECMP_PROGRAM_SAFE_NEXT_001_Prioritized_Safe_Work_Queue_v1.0.md`
- ADR-018; PROGRAM-BOARD-006 C-B6-3

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-31 | Initial Draft plan — Phases A–D; Mode B CLOSED |

---

*End of GOV-ORG-GAP-PLAN-001.*
