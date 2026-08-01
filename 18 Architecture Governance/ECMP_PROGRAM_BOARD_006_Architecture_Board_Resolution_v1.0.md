# PROGRAM-BOARD-006 — Architecture Board Resolution

| Field | Value |
|---|---|
| Document ID | GOV-BR-BOARD-006 |
| Program | PROGRAM-BOARD-006 |
| Resolution IDs | **BR-011**, **BR-012**, **BR-013** |
| Version | 1.0 |
| Date | 2026-07-30 |
| Prepared by | Architecture Board Secretary (Documentation Administrator) |
| Convening authority | **Project Owner chat instruction** 2026-07-30 — “lanjut” after PROGRAM-BOARD-005 Ready-for-Resolution (convene PROGRAM-BOARD-006) |
| Audience | Architecture Board / Solution Architect / Security Architect / Tech Lead / PMO |
| Status | 🟢 **Recorded** |
| Prior Review | PROGRAM-BOARD-005 — Ready for Resolution (`ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_v1.0.md`) |
| Prior Resolution (baseline) | PROGRAM-BOARD-004 (BR-009 / BR-010; C-3 Bilateral; C-7 Mode B CLOSED) |

---

## 1. Meeting Information

| Item | Value |
|---|---|
| Body | Architecture Board |
| Session | PROGRAM-BOARD-006 — Architecture Board Resolution |
| Date | 2026-07-30 |
| Subject package | ADR-016 v1.0 (+1.0a) + ADR-017 v1.0 (+1.0a) + ADR-018 v1.0 (+1.0a) |
| Inputs considered | PROGRAM-BOARD-005 Review (Ready for Resolution; RC-1…RC-7); ADR-016/017/018 bodies incl. K-5 fail-closed; PROGRAM-MODE-B-ORG-GAP-001 (K-7); PROGRAM-BOARD-004; Independent Program Audit addendum |
| Secretary | Architecture Board Secretary |
| Decision mode | **Package decision** (016 / 017 / 018 accepted or rejected only together) |

---

## 2. Decision

**Decision:** **ACCEPT WITH CONDITIONS**

| ADR | Version | Prior Board Disposition | New Board Decision |
|---|---|---|---|
| ADR-016 — Enterprise Protocol & Binding | v1.0 (+1.0a) | Proposed; BOARD-005 Ready for Resolution | **Accepted with Conditions** (BR-011) |
| ADR-017 — Enterprise Entitlement Architecture | v1.0 (+1.0a) | Proposed; BOARD-005 Ready for Resolution | **Accepted with Conditions** (BR-012) |
| ADR-018 — Enterprise Organization Synchronization | v1.0 (+1.0a) | Proposed; BOARD-005 Ready for Resolution | **Accepted with Conditions** (BR-013) |

Acceptance of this package records architecture for protocol binding, entitlement, and organization synchronization under Mode B **design**. It does **not** by itself authorize Mode B implementation, Batch-2 delivery, or enterprise customer production (see §4 Condition **C-B6-1** / PROGRAM-BOARD-004 **C-7** and §5).

---

## 3. Accepted Documents

| ID | Title | Path | Lifecycle effect |
|---|---|---|---|
| ADR-016 | Enterprise Protocol & Binding v1.0 | `05 Architecture Decision Records/ECMP_ADR_016_Enterprise_Protocol_Binding_v1.0.md` | **Accepted with Conditions** (BR-011) |
| ADR-017 | Enterprise Entitlement Architecture v1.0 | `05 Architecture Decision Records/ECMP_ADR_017_Enterprise_Entitlement_Architecture_v1.0.md` | **Accepted with Conditions** (BR-012) |
| ADR-018 | Enterprise Organization Synchronization Architecture v1.0 | `05 Architecture Decision Records/ECMP_ADR_018_Enterprise_Organization_Synchronization_Architecture_v1.0.md` | **Accepted with Conditions** (BR-013) |

### Package integrity (binding)

1. ADR-016, ADR-017, and ADR-018 are accepted **only as a coordinated package**.
2. ADR-015 remains the **Source of Truth** for Identity Contract claim content; ADR-016 must not silently edit claim tables.
3. ADR-008 remains the **Source of Truth** for ECMP permissions; ADR-017 entitlements ≠ permissions.
4. ADR-014 remains the ownership boundary for the ECMP business module; this package fills deferred protocol / entitlement / org-sync architecture.
5. ADR-013 remains **active** (PROGRAM-ADR-002 BR-007). This Resolution does **not** supersede ADR-013.
6. DEC-020 remains **Accepted** and unchanged: dual complaint SoT / namespace coexistence; no Mode B / Batch-2 / enterprise-customer unlock.
7. Document revision **1.0a** (K-5 fail-closed subordination) is **in scope** of this Accept (normative text as of 2026-07-30).

### Supersession intent

No prior Accepted heads exist for ADR-016/017/018. Canonical files remain the v1.0 paths above (including 1.0a body revisions). This Resolution does **not** rewrite ADR normative sections beyond metadata lifecycle flip under §6 F-2.

---

## 4. Conditions

Mandatory conditions of acceptance. All are binding until explicitly closed by a subsequent Board Resolution or Decision Record that cites this document. Conditions adopt PROGRAM-BOARD-005 advisory **RC-1…RC-7**.

### C-B6-1 — Mode B, Batch-2, and Enterprise customer remain CLOSED (reaffirm C-7)

Notwithstanding Accept With Conditions of ADR-016 / ADR-017 / ADR-018:

| Gate | Status after PROGRAM-BOARD-006 | Note |
|---|---|---|
| **Mode B** (Enterprise AuthN / SSO / enterprise identity runtime / OpenAPI enterprise `securitySchemes` / Mode B UI bridge / Identity Adapter coding) | **CLOSED** | Acceptance of architecture ADRs ≠ implementation unlock |
| **Batch-2** | **CLOSED** | Unchanged |
| **Enterprise customer** | **CLOSED** | Unchanged; aligns with DEC-020 explicit non-goals |

PROGRAM-BOARD-004 **C-7** remains in force and is **reaffirmed** by this Resolution.

### C-B6-2 — Fail-closed subordination standard (K-5 / ADR-016 §9.3)

1. ADR-016 §9.3 subordination standard is **binding** for all protocol-binding, entitlement, and org-sync **profiles**.
2. Profiles must not loosen fail-closed AuthN/AuthZ rules.
3. Any relaxation of fail-closed posture requires a **subsequent Architecture Board Resolution**.

### C-B6-3 — Organization-model gap is a Mode B unlock prerequisite (K-7)

1. PROGRAM-MODE-B-ORG-GAP-001 (`ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`) is **adopted**.
2. Three-level organization resolvability (per ADR-014 / ADR-018) remains an unmet **implementation** prerequisite for any future Mode B unlock.
3. Accept of ADR-018 does **not** waive this prerequisite and does **not** claim schema delivery.

### C-B6-4 — Bilateral Contract obligations extend (reaffirm C-3)

PROGRAM-BOARD-004 **C-3** (ADR-015 Bilateral Contract) is **reaffirmed**. Enterprise Platform obligations introduced by this package (protocol presentation, entitlement supply, organization SoR/sync expectations) are **bilateral** — not an ECMP-private wishlist detachable from Enterprise Platform delivery.

### C-B6-5 — Mode B coding authorization sequencing

When (and only when) a future Board Resolution unlocks Mode B implementation tasks:

1. Coding / OpenAPI enterprise `securitySchemes` / Identity Adapter work must respect sequencing **ADR-016 → ADR-017 → ADR-018** for dependent gates.
2. Package Accept does **not** by itself authorize that coding.

### C-B6-6 — ADR-007 / ADR-012 relationship remains Pending

Relationship disposition for ADR-007 / ADR-012 remains **Pending** per PROGRAM-BOARD-004 F-7. This Resolution does **not** silently subsume, supersede, or Mode-A-only-confine those ADRs.

### C-B6-7 — Canonical ADR Index hygiene (metadata)

1. Update canonical ADR Index, `05/README.md`, and portal mirror so ADR-016/017/018 show **Accepted with Conditions** with BR-011 / BR-012 / BR-013.
2. Update PROGRAM-ADR-002 disposition table.
3. Do **not** invent Mode B unlock language in index hygiene.

**Owner (execution):** Repository Documentation Administrator / Solution Architect  
**Gate:** Index and disposition tables consistent; Mode B remains CLOSED.

---

## 5. Non-Granted Authority

This Resolution **does not** grant authority to:

1. Enable **Mode B** AuthN, enterprise SSO, Identity Adapter runtime, or OpenAPI enterprise `securitySchemes`.
2. Start **OD-FE-002** browser/auth protocol bridge as an unlocked implementation track.
3. Treat FE-ARCH / FE-STD **BASELINE** as proof that Mode B is unlocked for delivery.
4. Unlock **Batch-2** or **enterprise customer** production.
5. Supersede **ADR-013** via frontend documentation or this package (BR-007 remains binding).
6. Execute Mode A → Mode B **cutover** / user linking without a future Board-approved cutover DEC.
7. Force-merge complaint implementation stacks or retire `/api/v1/complaints` (DEC-020 coexistence remains).
8. Reinterpret ADR-007 / ADR-012 beyond Relationship Pending without a separate Board disposition.
9. Waive the **org-model gap** Mode B prerequisite (C-B6-3) by Accept alone.
10. Loosen fail-closed AuthN/AuthZ via subordinate profiles (C-B6-2).

---

## 6. Required Follow-up

| # | Action | Owner | Depends on | Notes |
|---|---|---|---|---|
| F-1 | Execute **C-B6-7** (canonical index + mirrors + PROGRAM-ADR-002 disposition) | Documentation Admin / SA | This Resolution | No ADR body rewrite of normative sections |
| F-2 | Record ADR lifecycle status flip to **Accepted with Conditions** on ADR-016/017/018 headers / Board Disposition lines — **metadata only** | ADR Editor / Board Chair delegate | This Resolution | Not Mode B unlock |
| F-3 | Preserve C-B6-1 / C-7 gates in BMR / Implementation Authorization communications | Tech Lead / PMO | This Resolution | Mode B / Batch-2 / enterprise customer CLOSED |
| F-4 | Future Mode B unlock Resolution — only when org-gap prerequisite + operational readiness + explicit Board unlock | Architecture Board | C-B6-3 + C-B6-1 | Separate from this Accept |
| F-5 | Separate Board disposition for ADR-007 / ADR-012 (BOARD-004 F-7) | Architecture Board | Ongoing | Must not silently redefine Mode B claim SoT (ADR-015) |

**Stop condition for this Secretary task:** Resolution recorded + F-1/F-2 metadata hygiene in the same delivery where tasked. Mode B unlock is **out of scope**.

---

## 7. Board Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Architecture Board Chair (convening via Project Owner instruction) | — | 2026-07-30 | ☑ **Accept with Conditions** (PROGRAM-BOARD-006) |
| Security Architect | | | ☐ Countersign noted |
| Solution Architect | | | ☐ Countersign noted |
| Tech Lead | | | ☐ Informed |
| Business Owner | | | ☐ Informed |
| PMO | | | ☐ Recorded |

**Recorded decision text (verbatim intent):**

> Architecture Board **ACCEPTS WITH CONDITIONS** ADR-016 v1.0 (+1.0a), ADR-017 v1.0 (+1.0a), and ADR-018 v1.0 (+1.0a) as a coordinated package under PROGRAM-BOARD-006 (**BR-011** / **BR-012** / **BR-013**). Mandatory conditions **C-B6-1**…**C-B6-7** apply. Under **C-B6-1**, Mode B, Batch-2, and Enterprise customer remain **CLOSED** (PROGRAM-BOARD-004 C-7 reaffirmed). Under **C-B6-3**, the organization-model gap remains a Mode B unlock prerequisite.

**Secretary attestation:** This document records the Board decision stated for PROGRAM-BOARD-006. It does not unlock Mode B and does not implement application code.

---

## Related paths

- `18 Architecture Governance/ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_v1.0.md`
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`
- `18 Architecture Governance/ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`
- `18 Architecture Governance/ECMP_PROGRAM_AUDIT_K5_FailClosed_Subordination_v1.0.md`
- `05 Architecture Decision Records/ECMP_ADR_016_Enterprise_Protocol_Binding_v1.0.md`
- `05 Architecture Decision Records/ECMP_ADR_017_Enterprise_Entitlement_Architecture_v1.0.md`
- `05 Architecture Decision Records/ECMP_ADR_018_Enterprise_Organization_Synchronization_Architecture_v1.0.md`

---

*End of GOV-BR-BOARD-006 / PROGRAM-BOARD-006. Governance record only — Mode B / Batch-2 / enterprise customer remain CLOSED.*
