# PROGRAM-BOARD-004 — Architecture Board Resolution

| Field | Value |
|---|---|
| Document ID | GOV-BR-BOARD-004 |
| Program | PROGRAM-BOARD-004 |
| Resolution IDs | **BR-009**, **BR-010** |
| Version | 1.0 |
| Date | 2026-07-30 |
| Prepared by | Architecture Board Secretary |
| Audience | Architecture Board / Solution Architect / Security Architect / Tech Lead / PMO |
| Status | 🟢 Recorded |
| Related program (authoring) | PROGRAM-ADR-004 (Board Readiness Revision Package) |
| Prior dispositions | PROGRAM-ADR-002 BR-005 / BR-006 (Needs Revision) — superseded as active disposition by this Resolution |

---

## 1. Meeting Information

| Item | Value |
|---|---|
| Body | Architecture Board |
| Session | PROGRAM-BOARD-004 — Architecture Board Resolution |
| Date | 2026-07-30 |
| Subject package | ADR-014 v1.4 + ADR-015 v1.3 (coordinated package) |
| Inputs considered | Independent Board Review (mission input); DEC-020 v1.0 (Accepted); ADR-014 v1.4; ADR-015 v1.3; PROGRAM-ADR-002 BR-001…BR-008 (traceability); PROGRAM-ADR-004 authoring disposition |
| Secretary | Architecture Board Secretary |
| Decision mode | Package decision (ADR-014 and ADR-015 accepted or rejected only together) |

---

## 2. Decision

**Decision:** **ACCEPT WITH CONDITIONS**

| ADR | Version | Prior Board Disposition | New Board Decision |
|---|---|---|---|
| ADR-014 — ECMP Enterprise Business Module | v1.4 | Revised — Pending Board Review (PROGRAM-ADR-004; prior BR-005 Needs Revision addressed) | **Accepted with Conditions** (BR-009) |
| ADR-015 — Enterprise Identity Contract | v1.3 | Revised — Pending Board Review (PROGRAM-ADR-004; prior BR-006 Needs Revision addressed) | **Accepted with Conditions** (BR-010) |

Identity Contract version remains **1.0** (document revision 1.3 does not change contract major/minor claim set).

Acceptance of this package records architecture ownership and contract boundaries. It does **not** by itself authorize Mode B implementation, Batch-2 delivery, or enterprise customer production (see §4 Condition C-7 and §5).

---

## 3. Accepted Documents

| ID | Title | Path | Lifecycle effect |
|---|---|---|---|
| ADR-014 | ECMP Enterprise Business Module v1.4 | `05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4.md` | **Accepted with Conditions** (BR-009) |
| ADR-015 | Enterprise Identity Contract v1.3 | `05 Architecture Decision Records/ECMP_ADR_015_Enterprise_Identity_Contract_v1.3.md` | **Accepted with Conditions** (BR-010) |

### Package integrity (binding)

1. ADR-014 and ADR-015 are accepted **only as a coordinated package**.
2. ADR-015 remains the **Source of Truth** for the Enterprise Identity Contract claim set consumed under Mode B.
3. ADR-013 remains **active** (PROGRAM-ADR-002 BR-007). This Resolution does **not** supersede ADR-013.
4. DEC-020 remains **Accepted** and unchanged: dual complaint SoT / namespace coexistence; no Mode B / Batch-2 / enterprise-customer unlock by DEC-020 or by this Resolution.

### Supersession intent (for index hygiene — execution under C-1)

| Prior file (historical) | Intent after this Resolution |
|---|---|
| `ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.0.md` | Historical / superseded by v1.4 (index hygiene) |
| `ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.3.md` | Historical / superseded by v1.4 (index hygiene) |
| `ECMP_ADR_015_Enterprise_Identity_Contract_v1.0.md` | Historical / superseded by v1.3 (index hygiene) |
| `ECMP_ADR_015_Enterprise_Identity_Contract_v1.2.md` | Historical / superseded by v1.3 (index hygiene) |

Canonical current files are **v1.4** (ADR-014) and **v1.3** (ADR-015) only. This Resolution does **not** rewrite ADR body text.

---

## 4. Conditions

Mandatory conditions of acceptance. All are binding until explicitly closed by a subsequent Board Resolution or Decision Record that cites this document.

### C-1 — Canonical ADR Index regeneration and supersession hygiene

1. Regenerate / update the **canonical ADR Index** so ADR-014 points to **v1.4** and ADR-015 points to **v1.3**, with lifecycle **Accepted** (with Conditions) and citation of BR-009 / BR-010.
2. Apply **supersession hygiene**: prior ADR-014 / ADR-015 revision files must not appear as current Proposed/Accepted heads in index, mirrors (`docs/architecture/adr-index.md`), or README disposition tables.
3. Update PROGRAM-ADR-002 traceability so BR-005 / BR-006 are recorded as **historical** Needs Revision dispositions superseded by BR-009 / BR-010 for the active package.
4. Do **not** invent silent supersession of Accepted ADRs outside this package (especially ADR-007, ADR-012, ADR-013). Relationship dispositions for ADR-007 / ADR-012 remain as proposed in the ADR package until a separate Board disposition.

**Owner (execution):** Repository Documentation Administrator / Solution Architect  
**Gate:** Index and disposition tables consistent before Mode B-related implementation tasks may be proposed.

### C-3 — Board declaration on the nature of ADR-015

**Board declares:**

> **ADR-015 is a Bilateral Contract** between the **Enterprise Platform** and the **ECMP Business Module**.

Meaning (normative for governance):

| Party | Binding expectation |
|---|---|
| Enterprise Platform | Owns enterprise identity; supplies identity conforming to the versioned contract (claim set, semantics, fail-closed posture as defined in ADR-015). |
| ECMP Business Module | Consumes identity only; must not modify enterprise identity; must enforce required-claim / fail-closed rules; must not treat ADR-015 as an ECMP-private wishlist detachable from Enterprise Platform obligations. |

**Rejected alternative for this Resolution:** treating ADR-015 as a unilateral **Consumer Requirement** only (ECMP-side requirement list without bilateral binding). That reading is **not** adopted.

Contract document version remains **1.0**. Protocol / conveyance / `aud` / `iss` binding remain out of scope of ADR-015 and of this Accept.

### C-7 — Mode B, Batch-2, and Enterprise customer remain CLOSED

Notwithstanding Accept With Conditions of ADR-014 / ADR-015:

| Gate | Status after PROGRAM-BOARD-004 | Note |
|---|---|---|
| **Mode B** (Enterprise AuthN / SSO / enterprise identity runtime / OpenAPI enterprise `securitySchemes` / Mode B UI bridge) | **CLOSED** | Acceptance of ownership/contract ADRs ≠ implementation unlock |
| **Batch-2** | **CLOSED** | Unchanged; requires separate Board unlock |
| **Enterprise customer** (real-customer / production enterprise customer enablement) | **CLOSED** | Unchanged; aligns with DEC-020 explicit non-goals |

DEC-020 dual-SoT coexistence and Mode A delivery posture under existing Implementation Authorization (**AUTHORIZED WITH CONDITIONS**) remain in force and are **not** expanded by this Resolution.

---

## 5. Non-Granted Authority

This Resolution **does not** grant authority to:

1. Enable **Mode B** AuthN, enterprise SSO, Identity Adapter runtime, or OpenAPI enterprise `securitySchemes`.
2. Start **OD-FE-002** browser/auth protocol bridge as an unlocked implementation track.
3. Treat FE-ARCH / FE-STD **BASELINE** as proof that Mode B / identity is Accepted for delivery (OD-FE-008 exit remains a separate documentation sync after index/status execution; Mode B stays CLOSED per C-7).
4. Unlock **Batch-2** Case work or EPIC-CM-F4 implementation beyond already governed draft/planned artifacts.
5. Unlock **enterprise customer** / real-customer production.
6. Supersede **ADR-013** via frontend documentation or this package (BR-007 remains binding).
7. Execute Mode A → Mode B **cutover** / user linking without a future Board-approved cutover DEC.
8. Force-merge complaint implementation stacks or retire `/api/v1/complaints` (DEC-020 coexistence remains).
9. Reinterpret ADR-007 / ADR-012 relationship beyond the package’s “Relationship Pending” proposals without a separate Board disposition.
10. Modify ADR-014 / ADR-015 normative claim tables or invent protocol binding under the cover of “Accept”.

---

## 6. Required Follow-up

| # | Action | Owner | Depends on | Notes |
|---|---|---|---|---|
| F-1 | Execute **C-1** (canonical ADR Index regeneration + supersession hygiene + disposition table sync) | Documentation Admin / SA | This Resolution | No ADR body rewrite |
| F-2 | Record ADR lifecycle status flip to **Accepted** (with Conditions) on ADR-014 v1.4 and ADR-015 v1.3 headers / Board Disposition lines — **metadata only** | ADR Editor / Board Chair delegate | C-1 started | Separate editorial task; not Mode B unlock |
| F-3 | Sync FE OD-FE-008 / LAP Pending Upstream exit language to reflect Accept With Conditions **without** opening Mode B | FE Documentation Owner | F-2 | OD-FE-002 remains gated |
| F-4 | Preserve C-7 gates in BMR / Implementation Authorization communications | Tech Lead / PMO | This Resolution | Mode B / Batch-2 / enterprise customer CLOSED |
| F-5 | Future protocol / binding ADR (`aud` / `iss` / conveyance) — propose when ready | Security Architect / SA | F-2 | Required before Mode B AuthN implementation may be authorized |
| F-6 | Future Mode A → Mode B cutover DEC — only when needed | Architecture Board | F-5 + operational readiness | Linking without email-as-key |
| F-7 | Separate Board disposition for ADR-007 / ADR-012 relationship (Mode A–only vs subsumption vs other) | Architecture Board | This Resolution | Must not silently redefine Mode B claim SoT (ADR-015) |

**Stop condition for this Secretary task:** Resolution recorded. Execution of F-1…F-7 is **out of scope** of PROGRAM-BOARD-004 Secretary output unless separately tasked.

---

## 7. Board Sign-off

| Role | Name | Date | Decision |
|---|---|---|---|
| Architecture Board Chair | | 2026-07-30 | ☑ **Accept with Conditions** (PROGRAM-BOARD-004) |
| Security Architect | | | ☐ Countersign noted |
| Solution Architect | | | ☐ Countersign noted |
| Tech Lead | | | ☐ Informed |
| Business Owner | | | ☐ Informed |
| PMO | | | ☐ Recorded |

**Recorded decision text (verbatim intent):**

> Architecture Board **ACCEPTS WITH CONDITIONS** ADR-014 v1.4 and ADR-015 v1.3 as a coordinated package under PROGRAM-BOARD-004 (BR-009 / BR-010). Mandatory conditions **C-1**, **C-3**, and **C-7** apply. Under **C-3**, ADR-015 is declared a **Bilateral Contract**. Under **C-7**, Mode B, Batch-2, and Enterprise customer remain **CLOSED**.

**Secretary attestation:** This document records the Board decision stated for PROGRAM-BOARD-004. It does not modify ADR normative contents and does not implement application code.

---

## Related paths

- `05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4.md`
- `05 Architecture Decision Records/ECMP_ADR_015_Enterprise_Identity_Contract_v1.3.md`
- `27 Project Decisions/DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md`
- `18 Architecture Governance/ECMP_PROGRAM_ADR_002_Board_Resolutions_v1.0.md`
- `18 Architecture Governance/README.md` (ADR lifecycle)

---

*End of GOV-BR-BOARD-004 / PROGRAM-BOARD-004. Governance record only — no ADR body edits; no code; Mode B / Batch-2 / enterprise customer remain CLOSED.*
