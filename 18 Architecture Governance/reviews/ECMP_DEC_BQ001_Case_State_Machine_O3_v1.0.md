# DEC-BQ001 — Case State Machine (Option O3)

| Field | Value |
|---|---|
| Document ID | GOV-DEC-BQ001 |
| Decision ID | DEC-BQ001 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Owner | Domain PO ECMF / Solution Architect |
| Reviewer | Architecture Board, Operations Lead |
| Approver | Business Owner / Architecture Board |
| Status | **APPROVED** |
| BQ | BQ-001 / BQ-CAP02-001 |
| Option approved | **O3** (+ Aggregate uses Definition B) |
| Batch | Batch-2 Mode A / CAP-02 |
| Related | DEC-020 (dual SoT), FRD-CM-001 (LOCKED), BR-CM-CAT-001, DOM-ECMF-003 |

---

## 1. Background

BQ-001 exists because the repository contains **two incompatible Case status definitions**:

| Definition | Source | Case status model |
|---|---|---|
| **A** | DOM-ECMF-003 (Approved) | `REGISTERED` → `ASSIGNED` → `IN_PROGRESS` → `PENDING_REVIEW` → `CLOSED` → `REOPENED` |
| **B** | BR-CM-CAT-001 (Draft, conceptual) | `CREATED` → `ASSIGNED` → `IN_PROGRESS` → `PENDING` / `ESCALATED` → `RESOLVED` → `CLOSED`, with `CANCELLED` before final resolution |

Batch-2 CAP-02 (Create / Update / Resolve / Close Case) cannot be Business-Locked without a canonical enum and matrix.  
Batch-1 already locks Complaint as Aggregate Root and Case as child — that semantics conflicts with Case-as-intake in DOM-ECMF-003.  
This decision records the Architecture Board approval of **Option O3** from the BQ-001 Decision Package. No redesign. No new options.

---

## 2. Repository Evidence

| Evidence | Path / ID | Relevance |
|---|---|---|
| CAP-02 BCS — BQ-CAP02-001 BLOCKING | `docs/product/CAP-02_Case_Management_Business_Capability_Specification_v1.0.md` | Asks which Case state machine is SoT for Batch-2 Mode A |
| BR-CM-CAT-001 Case ringkas (Definition B) | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` | Conceptual Case states for Aggregate model |
| DOM-ECMF-003 Case Status SoT (Definition A) | `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` | Approved Sprint / case-centric matrix |
| FRD-CM-001 LOCKED — Aggregate + Case create in Batch 2 | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` | Complaint root; Case child; Case create deferred (CTO D-02) |
| Dual SoT coexistence | `27 Project Decisions/DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md` | Aggregate vs Sprint paths; no silent overwrite |
| Decision Package BQ-001 | Prepared 2026-08-01 (Architecture Board Secretary) | Options O1 / O2 / O3; recommendation **O3** |

---

## 3. Approved Option

**Option O3 — Dual SoT explicit (Sprint = Definition A; Aggregate CAP-02 = Definition B)**

| Aspek | Isi (from Decision Package — unchanged) |
|---|---|
| Description | DOM-ECMF-003 remains SoT Case for the Sprint / case-centric path. BR-CM-CAT Case becomes SoT Case for Batch-2 Aggregate (CAP-02). Not interchangeable; no silent overwrite. |
| Advantages | Honours Batch-1 locked + DOM Approved; allows CAP-02 to proceed without breaking Sprint freeze; aligns with Aggregate vs Sprint coexistence already stated in FRD-CM-001 / API Catalog. |
| Risks | Two Case status vocabularies; requires naming discipline; Definition B must be completed promptly or O3 is operationally empty. |
| Repository impact | No mandatory rewrite of DOM-ECMF-003; must document SoT boundary and complete matrix B under BR-CM-CAT (follow-up BU-02). |
| Business impact | CAP-02 uses Case child (`CREATED`…); Sprint keeps baseline until a separate cutover DEC. |
| Migration impact | No forced Sprint→Aggregate migration now; future cutover requires its own DEC. |

Options **O1** and **O2** were considered in the Decision Package and are **not approved**.

---

## 4. Decision Statement

**Status: APPROVED**

> The Architecture Board approves **Option O3** for BQ-001 (Case State Machine):  
> (1) **DOM-ECMF-003** remains the Source of Truth for Case status enum and transition matrix on the **Sprint / case-centric** path;  
> (2) **BR-CM-CAT-001 Case state model** (Definition B: `CREATED` → `ASSIGNED` → `IN_PROGRESS` → `PENDING` / `ESCALATED` → `RESOLVED` → `CLOSED`, with `CANCELLED` before final resolution) is the Source of Truth for **Case under Complaint Aggregate** for **Batch-2 Mode A / CAP-02**;  
> (3) the two SoTs are **not interchangeable** and must not silently overwrite each other’s IDs, enums, or contracts;  
> (4) Complaint status `REGISTERED` (Batch-1) must not be treated as identical to Case status `REGISTERED` (DOM-ECMF-003);  
> (5) this approval does **not** by itself complete Definition B — a complete Aggregate Case transition matrix must be produced and recorded under BR-CM-CAT (follow-up);  
> (6) this decision does **not** authorize FRD Batch-2, OpenAPI changes, Mode B work, or resolution of BQ-002+.

| Field | Value |
|---|---|
| Decision ID | DEC-BQ001 |
| BQ | BQ-001 / BQ-CAP02-001 |
| Option approved | O3 (+ Aggregate uses Definition B) |
| Approver | Architecture Board / Business Owner |
| Decision Date | 2026-08-01 |
| Status | **APPROVED** |

---

## 5. Scope

- BQ-001 / BQ-CAP02-001 Case State Machine canonical choice for Batch-2 Mode A / CAP-02.
- Dual SoT boundary: Sprint = DOM-ECMF-003; Aggregate CAP-02 = BR-CM-CAT Definition B.
- Explicit non-equivalence of Complaint `REGISTERED` and Case `REGISTERED` (DOM).

---

## 6. Out of Scope

- FRD Batch-2  
- OpenAPI / API catalog changes  
- Implementation / code changes  
- Mode B / Identity / SSO  
- BQ-002 and later CAP-02 business questions  
- Supersede, delete, or rewrite DOM-ECMF-003  
- Forced Sprint→Aggregate enum migration  
- Assignment Engine / SLA Engine / Notification Engine  

---

## 7. Repository Impact

| Area | Impact under O3 |
|---|---|
| DOM-ECMF-003 | Unchanged — remains Sprint SoT |
| BR-CM-CAT-001 | Follow-up: record complete Case Aggregate transition matrix (BU-02); later status lock (BU-04) |
| CAP-02 BCS | Follow-up: close BQ-001 citation; state machine SoT reference (BU-03) |
| FRD-CM-001 | Unchanged (LOCKED) |
| DEC-020 | Affirmed — dual SoT coexistence |
| Code / OpenAPI | None in this DEC |

---

## 8. Follow-up Work

Per Decision Package Required Follow-up (O3 approved):

1. Produce complete Case Aggregate transition matrix for Definition B (allowed / forbidden / entry / exit / business guards).  
2. Update BR-CM-CAT-001 with that matrix (no module redesign; no Assignment/SLA engines).  
3. Record SoT boundary in BR-CM-CAT (Sprint = DOM-ECMF-003; Aggregate CAP-02 = Definition B).  
4. After matrix + boundary recorded: proceed Board Unlock remaining tasks (BU-02…BU-04).  
5. **No FRD yet. No OpenAPI yet. No BQ-002. No Mode B.**

---

## 9. Related Documents

| Document | Path |
|---|---|
| This decision | `18 Architecture Governance/reviews/ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md` |
| Countersign pack | `18 Architecture Governance/reviews/ECMP_DEC_BQ001_Architecture_Board_Countersign_Pack_v1.0.md` |
| CAP-02 BCS | `docs/product/CAP-02_Case_Management_Business_Capability_Specification_v1.0.md` |
| BR-CM-CAT-001 | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` |
| DOM-ECMF-003 | `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` |
| FRD-CM-001 | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` |
| DEC-020 | `27 Project Decisions/DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md` |
| Open Questions | `27 Project Decisions/OPEN_QUESTIONS.md` (BQ-001) |

---

## Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-08-01 | Architecture Board Secretary / Repository Maintainer | Record APPROVED Option O3 from BQ-001 Decision Package |

---

*End of DEC-BQ001 v1.0 — Status APPROVED.*
