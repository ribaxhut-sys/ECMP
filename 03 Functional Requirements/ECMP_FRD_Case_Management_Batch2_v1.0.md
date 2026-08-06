# ECMP Functional Requirements Document — Case Management Batch 2 Mode A

| Field | Value |
|---|---|
| Document ID | FRD-CM-B2-001 |
| Title | Case Management — FRD Batch 2 Mode A (CAP-008) |
| Filename | `ECMP_FRD_Case_Management_Batch2_v1.0.md` |
| Version | 1.0 |
| Document Status | 🔒 **LOCKED** — Mode A CAP-008 SoT (lab RC `v1.2.0-rc.1`) |
| Owner | Business Analyst / Domain PO ECMF |
| Reviewer | Solution Architect, Operations Lead, Compliance |
| Approver | Business Owner / Architecture Board |
| Module | Complaint Management Module only |
| Capability | **CAP-008** |
| Batch | Batch-2 Mode A |
| Locked | 2026-08-01 |
| Last Review | 2026-08-01 |
| Related OpenAPI | `07 API Catalog/openapi/cm-case-management.v1.yaml` **1.0.0** (API-530…535) — Implemented (lab) |
| Related RC | `deploy/evidence/REL_RC_001_CAP-008_Mode_A_Assessment_20260801.md` — PASS (lab) |
| Related SoT Closure | `deploy/evidence/CAP-008_SoT_Closure_20260801.md` |
| Related BCS | `docs/product/CAP-008_Case_Management_Business_Capability_Specification_v1.0.md` (v1.2) — LOCKED |
| Related BR | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001) — LOCKED |
| Related Transition Matrix | BR-CM-CAT-001 Case Aggregate Transition Matrix — LOCKED |
| Related Operational Specification | Embedded herein (Unit Ownership · Mode A Delivery Transition Subset · Close Case Checklist · FR-004 Rename) — LOCKED |
| Related Batch-1 | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (FRD-CM-001) — LOCKED |
| Related Governance Baseline | `docs/governance/BC-000-Business-Constitution.md`; `docs/governance/BC-001-Business-Principles.md`; `docs/governance/BC-002-Business-Rules.md`; `docs/governance/BC-003-Business-Glossary.md`; `docs/business/BW-000-Business-Workflow-Constitution.md` |
| Precedence | If this FRD conflicts with the approved Mode A governance baseline (BC-000…BC-003, BW-000), **the baseline prevails**. |
| Related DEC | DEC-BQ001 O3; DEC-MODEA-B2-001; DEC-020; CTO D-02 |
| Gate status | Business Lock READY · Board Unlock READY · Residual BQ **ZERO** |

> **Authoring rules:** Repository is the only Source of Truth. Do not invent behavior. If the repository states **NOT SPECIFIED**, this FRD states **NOT SPECIFIED**.
>
> **Namespace:** FR-001…FR-006 in this document = Batch-2 CAP-008 (Case under Complaint Aggregate). **Not** Sprint FRD-001 IDs. **Not** FRD-CM-001 Batch-1 IDs. Dual SoT (DEC-020 / DEC-BQ001 O3) applies.
>
> **This document does not modify** Business Rules, CAP-008 BCS, Transition Matrix, or Decisions.

---

## Table of Contents

1. [Document Control](#1-document-control)
2. [Purpose](#2-purpose)
3. [Scope](#3-scope)
4. [Business Context](#4-business-context)
5. [Definitions](#5-definitions)
6. [Actors](#6-actors)
7. [Functional Requirements](#7-functional-requirements)
8. [Business Validation Rules](#8-business-validation-rules)
9. [Acceptance Criteria](#9-acceptance-criteria)
10. [Traceability Matrix](#10-traceability-matrix)
11. [Appendix](#11-appendix)
12. [Document History](#12-document-history)

---

## 1. Document Control

### 1.1 Document identity

| Item | Value |
|---|---|
| ID | FRD-CM-B2-001 |
| Filename | ECMP_FRD_Case_Management_Batch2_v1.0.md |
| Status | 🔒 **LOCKED** |
| Capability | CAP-008 |
| SoT Case status (Aggregate) | BR-CM-CAT-001 Definition B (DEC-BQ001 O3) |
| SoT Case status (Sprint) | DOM-ECMF-003 — **not interchangeable** |

### 1.2 Quality rules

- RFC-2119: **MUST**, **SHALL**, **SHOULD**, **MAY**
- No inventing Business Rules or transitions
- No Out-of-Scope capabilities as acceptance
- Authorization is ECMP-internal
- ECMP is not Customer Master SoR
- API catalog IDs for Aggregate CAP-008 Case slice: **API-530…535** (`cm-case-management.v1.yaml` v1.0.0) — **not** Sprint `API-001…`
- EVT catalog IDs Aggregate CAP-008: **NOT SPECIFIED** (matrix business event names ≠ EVT IDs; do not silently map to Sprint `EVT-001…`)

### 1.3 Locked prerequisites (read-only)

| Gate | Status |
|---|---|
| Business Lock | READY |
| Board Unlock | READY |
| Residual BQ | ZERO |
| CAP-008 | LOCKED |
| BR-CM-CAT-001 | LOCKED |
| Transition Matrix | LOCKED |
| Operational Specification | LOCKED |

### 1.4 Explicit non-goals of this LOCK

Event Catalog design (EVT IDs remain **NOT SPECIFIED**) · Mode B · Identity redesign · Business Rules changes · CAP-008 BCS redesign · Production promote / OIDC.

> **SoT Closure 2026-08-01:** FRD status → **LOCKED**; OpenAPI Aggregate CAP-008 synchronized to Implemented (lab). No FR body redesign; no business scope change.

---

## 2. Purpose

Provide the **LOCKED** Functional Requirements for Batch-2 Mode A Case Management under the Complaint Aggregate (**CAP-008**), enabling:

1. Create Case under an existing Complaint
2. Add Case to an existing Complaint
3. View Case (including Timeline read)
4. Update Case Status (Mode A Delivery Transition Subset)
5. Resolve Case
6. Close Case

This closes the Batch-1 operational gap (CTO D-02 / FRD-CM-001): Complaint may be `REGISTERED` without a Case work item; CAP-008 supplies the Case path after intake.

---

## 3. Scope

### 3.1 In Scope

| FR | Title |
|---|---|
| FR-001 | Create Case |
| FR-002 | Add Case to Existing Complaint |
| FR-003 | View Case |
| FR-004 | Update Case Status |
| FR-005 | Resolve Case |
| FR-006 | Close Case |

Mandatory reuse from Batch-1 (not redesigned): Complaint Aggregate Root; `CustomerId` only; no Case-at-intake (D-02 / BQ-011); Attachment membership; ECMP-internal authorization; Mode B closed.

### 3.2 Out of Scope

Assignment Engine (BR-005 full) · SLA Engine countdown/breach (BR-006 full) · Notification Engine · Dashboard (BR-019) · Reporting (BR-020) · Mode B · Identity redesign · AI · Escalation Engine full (BR-007 / DEC-F4 delivery) · Complaint Closure Aggregate (BR-009 full) · Reopen (BR-015) · Batch-1 FR redesign · Enterprise Platform / SDK · Non-status Case attribute mutation after create (**NOT SPECIFIED** as a Mode A FR; not FR-004).

---

## 4. Business Context

### 4.1 Why Case exists

Per BR-CM-CAT-001 and CAP-008:

- **Complaint** = Aggregate Root (business container).
- **Case** = operational work unit under Complaint.
- Assignment and SLA belong to Case (engines themselves OUT OF SCOPE for CAP-008 Mode A delivery).
- Without Case, Batch-1 leaves `REGISTERED` Complaints without operational work items.

### 4.2 Locked Mode A Delivery Baseline (DEC-MODEA-B2-001)

| BQ | Locked policy |
|---|---|
| BQ-002 | MAY register without Case; MUST ≥1 Case within **1 working day** after `REGISTERED` (BC-5.4 timing threshold; **not** Working Day SLA calendar activation); Supervisor Queue shows exceedances |
| BQ-003 | Max Cases per Complaint = **5** (Mode A) |
| BQ-004 | Case Number independent; format **`CASE-YYYY-NNNNNN`** |
| BQ-005 | Bind SLA Policy Version; countdown **NOT** activated |
| BQ-006 | Assignment **Unit level only**; Assigned User outside Mode A |
| BQ-007 | Close Case ≠ auto Close Complaint |
| BQ-008 | `IN_PROGRESS` → `RESOLVED` → Supervisor Approval → `CLOSED` |
| BQ-009 | `PENDING` / `ESCALATED` remain in Aggregate matrix; Mode A Delivery **does NOT expose** them |
| BQ-010 | Resolve requires Comment; Attachment optional; Complaint Attachment may be reused |
| BQ-011 | D-02 retained; no Case-at-intake; timing = BQ-002 |
| BQ-014 | `CANCELLED` included; reasons: Duplicate, Wrong Input, Customer Cancellation |

### 4.3 Dual SoT

| Path | Case SoT |
|---|---|
| Aggregate Batch-2 Mode A (this FRD) | BR-CM-CAT-001 Definition B |
| Sprint / case-centric | DOM-ECMF-003 |

Not interchangeable. Complaint `REGISTERED` ≠ Case `REGISTERED` (DOM-ECMF-003).

---

## 5. Definitions

### 5.1 Glossary

| Term | Definition |
|---|---|
| Complaint | Aggregate Root — customer complaint/request as one business whole |
| Case | Operational work unit under Complaint |
| CustomerId | Sole customer reference stored on Complaint |
| Case Number | Independent Case identity; format `CASE-YYYY-NNNNNN` (BQ-004) |
| Resolution | Formal Case outcome record (BR-008) |
| Timeline | Human-readable chronological projection (BR-017) |
| Audit Trail | Immutable significant-write record (BR-016) |
| Unit ownership | Mode A operational ownership = Organization Unit (see §5.2) |

### 5.2 Unit Ownership Semantics (Mode A) — Operational Specification LOCKED

**Unit ownership**  
Operational ownership of a Case in Mode A = the **Organization Unit** that is the assignment target (destination unit / unit queue). Assignment exists **only at Case level**, not Complaint (BR-004 / BR-005). Mode A: assignment is **Unit level only**; **Assigned User is outside Mode A** (BQ-006).

**Operational responsibility**  
Mode A Case operational responsibility attaches to the **owning Unit**. There is no individual assignee in Mode A (BQ-006). Claim / auto-route / bulk user reassignment = Assignment Engine = **OUT OF SCOPE** CAP-008.

**State ownership (Mode A)**

| State | Ownership semantics |
|---|---|
| `CREATED` | Case exists; **no** active assignment yet (matrix) |
| `ASSIGNED` | Unit ownership active (Mode A = Unit/queue; not user) |
| `IN_PROGRESS` | Unit ownership continues; active work in owning Unit |
| `RESOLVED` | Resolution Accepted; Unit ownership continues until Close |
| `CLOSED` / `CANCELLED` | Terminal; no Case-level exit |

`PENDING` / `ESCALATED`: Aggregate ownership remains defined in BR-CM-CAT; **not exposed** in Mode A Delivery (BQ-009).

**Resolve responsibility**  
Complaint Officer (active handling) proposes; Supervisor approves on Mode A path (BQ-008). Case → `RESOLVED` only after Resolution **Accepted** (BR-008). Resolve of another’s Case without Supervisor rights is rejected (BR-008 E3).

**Supervisor responsibility**  
Unit assign/reassign; multi-Case oversight; approve/reject Resolution; Close Case (primary); aging exceedance Supervisor Queue (BQ-002).

### 5.3 Case states

Aggregate SoT states: `CREATED` · `ASSIGNED` · `IN_PROGRESS` · `PENDING` · `ESCALATED` · `RESOLVED` · `CLOSED` · `CANCELLED`

**Mode A Delivery exposed:** `CREATED` · `ASSIGNED` · `IN_PROGRESS` · `RESOLVED` · `CLOSED` · `CANCELLED`  
**Not exposed:** `PENDING` · `ESCALATED` (BQ-009)

**Not Case states:** `PENDING_APPROVAL` (Resolution proposal status); `REOPENED` (Complaint status).

---

## 6. Actors

> **Persona alignment (BC-8 / BG-018):** Operational closed set = **Complaint Officer**, **Supervisor**, **Manager**. Legacy Agent / Petugas Frontline / Case Handler → **Complaint Officer**. **Manager** remains valid; CAP-008 delivery surface **MAY** omit Manager workspace (DL-068).

| Actor | Role in CAP-008 Mode A |
|---|---|
| Complaint Officer *(legacy: Agent / Petugas Frontline — intake)* | Create / Add Case; View Case & Timeline in scope |
| Complaint Officer *(legacy: Case Handler — active handling)* | View; Update Status (subset); propose Resolve; read Timeline/Attachment/Comment per rights |
| Supervisor Unit | Create/Add; Unit assign/reassign; View across handlers in unit; approve/reject Resolution; Close Case (primary); aging queue |
| Manager | Valid business persona; Mode A CAP-008 workspace **MAY** deferred |
| Administrator | Configure Case types/categories, resolution catalog, max Case, workflow parameters |
| System | Case Number; enforce preconditions; Audit + Timeline; reject orphan Case; reject hard-delete; Complaint `REGISTERED`→`IN_PROGRESS` on first Case |
| Customer | Complaint source; **no** direct module login in Mode A CAP-008 |

Regional / Head Office officers are **not** primary CAP-008 Mode A actors (Escalation Engine full / DEC-F4 detail delivery not exposed; Regional = **Out of Scope for Mode A** path).

### 6.1 Allowed actor matrix (Mode A)

| Action | Actors (SoT) | Mode A bound |
|---|---|---|
| Create / Add Case | Complaint Officer, Supervisor Unit, System (± Complaint Officer active-handling if granted) | Authorized unit/role; valid destination Unit |
| Assign / reassign Unit | Supervisor Unit / System | Unit only; Assigned User rejected |
| `ASSIGNED`→`IN_PROGRESS` | Complaint Officer in owning Unit **or** Supervisor Unit | No new roles |
| Update Case Status | Complaint Officer, Supervisor Unit, System | Role + Unit guard |
| Resolve (propose) | Complaint Officer (active handling) | Comment required (BQ-010) |
| Resolve (approve) | Supervisor Unit | BQ-008 |
| Close Case | Supervisor Unit (primary); Complaint Officer **if configured** | Handler-close activation Mode A = **NOT SPECIFIED** |
| Cancel | Supervisor (primary) / authorized actor | Mode A reasons BQ-014 |

---

## 7. Functional Requirements

### FR Catalog Summary

| FR | Title | Priority |
|---|---|---|
| FR-001 | Create Case | Must |
| FR-002 | Add Case to Existing Complaint | Must |
| FR-003 | View Case | Must |
| FR-004 | Update Case Status | Must |
| FR-005 | Resolve Case | Must |
| FR-006 | Close Case | Must |

---

### FR-001 Create Case

#### Purpose

Create an operational Case under a valid Complaint so work can be Unit-assigned, SLA Policy Version-bound (without Mode A countdown), and traced via Timeline/Audit — without splitting the Complaint Aggregate (BR-004; CAP-008 UC-CAP02-01).

#### Business Goal

Convert a Batch-1 `REGISTERED` (or active) Complaint into a Case-backed operational workload; prevent orphan Complaints beyond BQ-002 aging; preserve Aggregate integrity.

#### Actors

Agent / Petugas Frontline; Supervisor Unit; System; Case Handler **if granted create rights**; Administrator (configuration only).

#### Trigger

Actor selects **Create Case** on a Complaint that may receive a new Case; or System-assisted path when policy allows. Case-at-intake on Batch-1 Complaint create remains **inactive** (BQ-011 / D-02). Mandatory Case timing after `REGISTERED` = BQ-002.

#### Preconditions

1. Parent Complaint exists.
2. Complaint is not `CLOSED` without reopen (BR-004 E1; reopen OUT OF SCOPE CAP-008).
3. Actor is authorized (ECMP-internal AuthZ) for the unit/role.
4. Case type/category/priority are active configuration values.
5. Case count on Complaint **&lt; 5** (BQ-003).
6. Complaint `CustomerId` exists (verified or UNVERIFIED per Batch-1 policy).
7. Actor is authenticated; organization unit is resolvable.

#### Main Flow

1. Actor selects parent Complaint.
2. Actor enters Case type/category, subject, work description, priority, and **initial destination Unit** (Mode A).
3. System generates unique Case Number `CASE-YYYY-NNNNNN` (BQ-004), independent of Complaint Number.
4. System sets initial status:
   - `CREATED` if Unit assignment is not performed in the same business action; or
   - `ASSIGNED` if Create + **Unit assignment only** in one action (BR-004 A1; BQ-006).
5. System **SHALL bind SLA Policy Version**; countdown **NOT** activated (BQ-005).
6. System writes Timeline “Case Created” (BR-017) and Audit (BR-016).
7. If this is the first Case on a `REGISTERED` Complaint, Complaint status becomes `IN_PROGRESS` (BR-004).
8. System presents the Case (Case Number, status, parent Complaint).

#### Alternative Flow

| ID | Description |
|---|---|
| A1 | Create with Unit assignment only → initial `ASSIGNED`; Assigned User rejected (BQ-006) |
| A2 | Parallel Cases on same Complaint while N &lt; 5 (BQ-003) |
| A3 | Informational / follow-up Case type (BR-004 A3) — still a formal Case; SLA Policy Version bound; countdown still NOT activated |

#### Exception Flow

| ID | Condition | Behavior |
|---|---|---|
| E1 | Complaint `CLOSED` | MUST reject |
| E2 | Max Case = 5 | MUST reject |
| E3 | Mandatory attributes missing / type inactive | MUST reject |
| E4 | Unauthorized | MUST reject + security audit |
| E5 | Assigned User supplied | MUST reject (BQ-006) |
| E6 | No parent Complaint | MUST reject |
| E7 | Mandatory Audit/Timeline write fails | MUST fail business create |

#### Validation Rules

| Field / rule | Requirement |
|---|---|
| Parent Complaint | Required; status allows new Case |
| Case type | Active |
| Subject / Description | Required per policy |
| Priority | Valid configured value |
| Destination Unit | Valid Organization unit |
| Case count | N &lt; 5 |
| Case Number | System-generated `CASE-YYYY-NNNNNN` |
| Assigned User | Forbidden in Mode A |
| SLA | Policy Version bound; countdown not started |

#### State Transition

| From | To | Notes |
|---|---|---|
| *(none)* | `CREATED` | Default without simultaneous Unit assign |
| *(none)* | `ASSIGNED` | Create + Unit assignment only |
| Complaint `REGISTERED` | Complaint `IN_PROGRESS` | First Case effect (BR-004) |

Forbidden: orphan Case; DOM-ECMF-003 enums; Assigned User.

#### Postconditions

- Case exists under the same Complaint; unique Case Number.
- Initial status `CREATED` or `ASSIGNED` (Unit).
- SLA Policy Version bound; countdown not started.
- Timeline + Audit recorded.
- If first Case from `REGISTERED`: Complaint = `IN_PROGRESS`.
- Hard-delete unavailable.

#### Acceptance Criteria

1. AC-01: Authorized Create with mandatory attributes → Case with `CASE-YYYY-NNNNNN`, initial status per BR-CM-CAT, Timeline “Case Created” + Audit. **[BQ-004]**
2. AC-02: First Case on Batch-1 `REGISTERED` → Case count = 1 and Complaint = `IN_PROGRESS`.
3. AC-04: Complaint `CLOSED` → Create rejected.
4. AC-05: Case without parent Complaint → rejected.
5. AC-05b: `REGISTERED` without Case &gt; 1 working day → Supervisor Queue exceedance. **[BQ-002]**
6. AC-17: SLA Policy Version bound; countdown NOT activated. **[BQ-005]**
7. AC-18: No Assignment Engine auto-route/claim/bulk; Unit assignment only. **[BQ-006]**

#### Referenced Business Rules

BR-004; BR-016; BR-017; BR-CAP02-R01…R08, R11, R12, R19 (CAP-008 BCS mapping).

#### Referenced CAP

CAP-008 — UC-CAP02-01.

#### Referenced Decisions

DEC-MODEA-B2-001 (BQ-002…006, BQ-011); DEC-BQ001 O3; CTO D-02 / BQ-011; DEC-020 (namespace coexistence).

#### Traceability

| Item | Ref |
|---|---|
| CAP | CAP-008 |
| UC | UC-CAP02-01 |
| BR | BR-004, BR-016, BR-017 |
| DEC/BQ | DEC-MODEA-B2-001; BQ-002…006,011; DEC-BQ001 O3 |
| AC | AC-01, AC-02, AC-04, AC-05, AC-05b, AC-17, AC-18 |
| API | API-530 |
| EVT | **NOT SPECIFIED** |
| TC | Lab suite `backend/tests/test_cm_case_mode_a.py` (REL-RC-001); formal TC-catalog IDs deferred |

#### Purpose

Add a new Case to an existing Complaint (including continuation / split paths) without creating a new Complaint — enforcing No Duplicate Work (BR-014; CAP-008 UC-CAP02-02). **Not** “Add Complaint to Existing Case”.

#### Business Goal

Handle additional work aspects under one Aggregate; avoid duplicate Complaints for the same customer issue context.

#### Actors

Agent / Petugas Frontline; Supervisor Unit; System; Case Handler if granted.

#### Trigger

Continuation on existing Complaint; Supervisor-approved split; manual **Add Case**; or Batch-1 duplicate recommend-only path executed in Batch-2.

#### Preconditions

Same as FR-001; Complaint allows additional Case; N &lt; 5.

#### Main Flow

1. Actor opens existing Complaint.
2. Actor selects **Add Case** and enters new work attributes (type/category/subject/description/priority/destination Unit).
3. System persists child Case with new Case Number; initial status `CREATED` or `ASSIGNED` (Unit) per FR-001 rules.
4. System writes Timeline “Case Created” and Audit.
5. System **MUST NOT** create a new Complaint.

#### Alternative Flow

| ID | Description |
|---|---|
| A1 | From Batch-1 duplicate recommend-only → Add Case in Batch-2 |
| A2 | Multi-Case split (each Case Unit-owned; SLA Policy Version bound; countdown NOT activated) |

#### Exception Flow

Same E1–E7 as FR-001, plus:

| ID | Condition | Behavior |
|---|---|---|
| E8 | Attempt to create new Complaint when same context should continue | Business duplicate guidance; **MUST NOT** create Case-under-Case |

#### Validation Rules

Same as FR-001 create validations; additionally: target MUST be an existing Complaint; result MUST increase Case count by 1 without new Aggregate.

#### State Transition

Entry same as FR-001: → `CREATED` or → `ASSIGNED` (Unit). Complaint `REGISTERED`→`IN_PROGRESS` applies only if this is the first Case.

#### Postconditions

- Case count N → N+1 (N+1 ≤ 5) on the same Complaint.
- No new Complaint.
- Timeline + Audit recorded.

#### Acceptance Criteria

1. AC-03: N &lt; 5 → Add succeeds (N+1); N = 5 → rejected. **[BQ-003]**
2. AC-04: Complaint `CLOSED` → Add rejected.

#### Referenced Business Rules

BR-004; BR-014; BR-016; BR-017; BR-CAP02-R02, R05, R08, R10, R11, R12.

#### Referenced CAP

CAP-008 — UC-CAP02-02.

#### Referenced Decisions

DEC-MODEA-B2-001 (BQ-003); CTO D-02 (duplicate recommend path; Case create deferred to Batch-2).

#### Traceability

| Item | Ref |
|---|---|
| CAP | CAP-008 |
| UC | UC-CAP02-02 |
| BR | BR-004, BR-014, BR-016, BR-017 |
| DEC/BQ | BQ-003; D-02 |
| AC | AC-03, AC-04 |
| API | API-531 |
| EVT | **NOT SPECIFIED** |
| TC | Lab suite `backend/tests/test_cm_case_mode_a.py` (REL-RC-001); formal TC-catalog IDs deferred |

---

### FR-003 View Case

#### Purpose

Allow authorized actors to read a Case within Aggregate and org/role bounds, including parent Complaint, CustomerId, and Timeline access (CAP-008 UC-CAP02-03 / UC-CAP02-07 read path; BR-017).

#### Business Goal

Provide operational visibility for handling, supervision, and auditability without mutating Case state.

#### Actors

Agent / Petugas Frontline; Case Handler; Supervisor Unit; System (presentation).

#### Trigger

Actor opens a Case from Complaint detail, aging queue, or operational search.

#### Preconditions

1. Case exists.
2. Actor has read rights for org/role scope.
3. If opened in a Complaint context, Case MUST belong to that Complaint (membership).

#### Main Flow

1. System displays Case header: Case Number, status, parent Complaint, CustomerId, priority/type (as available).
2. System displays Case attribute summary.
3. System provides Timeline access (time-ordered; append-only projection).
4. System displays Resolution / Attachment / Comment per **read** rights.

#### Alternative Flow

| ID | Description |
|---|---|
| A1 | View from multi-Case Complaint list |
| A2 | Sensitive-field masking for limited roles |
| A3 | Timeline filter / drill-down (UC-CAP02-07) |

#### Exception Flow

| ID | Condition | Behavior |
|---|---|---|
| E1 | Unauthorized | MUST reject |
| E2 | CaseId not member of Complaint context | MUST reject |
| E3 | Manual Timeline reorder | MUST reject |

#### Validation Rules

| Rule | Requirement |
|---|---|
| AuthZ read | Required |
| Membership | Case MUST belong to Complaint context when contextualized |
| Mutation | View MUST NOT change Case status |

#### State Transition

None. View Case **MUST NOT** change Case status.

#### Postconditions

- No status/attribute mutation from View.
- Whether every ordinary View requires Audit: **NOT SPECIFIED** beyond BR-016 general (“selected sensitive reads”); if policy triggers, follow BR-016.

#### Acceptance Criteria

1. AC-06: Authorized View shows at least Case Number, status, parent Complaint, CustomerId, priority/type (as available).
2. AC-07: Cross-membership View rejected.
3. AC-08: After a successful Case write, Timeline shows related events in time order and user cannot rewrite history.

#### Referenced Business Rules

BR-017; BR-004 constraints; BR-012 membership when Attachment shown; BR-CAP02-R01, R16, R19.

#### Referenced CAP

CAP-008 — UC-CAP02-03; UC-CAP02-07 (Timeline read).

#### Referenced Decisions

DEC-BQ001 O3 (Aggregate Case vocabulary on display); DEC-020 (do not confuse with Sprint case-centric IDs).

#### Traceability

| Item | Ref |
|---|---|
| CAP | CAP-008 |
| UC | UC-CAP02-03 / UC-CAP02-07 |
| BR | BR-017; BR-004; BR-012 (read) |
| DEC/BQ | DEC-BQ001 O3; DEC-020 |
| AC | AC-06, AC-07, AC-08 |
| API | API-532 (Mode A CAP-008). Do **not** equate to API-525/526 Planned (FRD-CM-002) |
| EVT | **NOT SPECIFIED** |
| TC | Lab suite `backend/tests/test_cm_case_mode_a.py` (REL-RC-001); formal TC-catalog IDs deferred |

---

### FR-004 Update Case Status

#### Purpose

Change Case status **only** via the **Mode A Delivery Transition Subset** (Appendix B), filtered from the locked BR-CM-CAT-001 Case Aggregate Transition Matrix (DEC-BQ001 O3; CAP-008 UC-CAP02-04).

#### Business Goal

Enforce configuration-first, auditable Case lifecycle progression under Unit ownership without exposing out-of-delivery states or Assigned User.

#### Actors

Case Handler; Supervisor Unit; System.

#### Trigger

Actor selects an allowed Mode A status transition (including Cancel with BQ-014 reason; Unit reassign remaining in `ASSIGNED`).

#### Preconditions

1. Case is not terminal (`CLOSED` / `CANCELLED`).
2. Transition exists in Appendix B Mode A Delivery Transition Subset.
3. Actor authorized in Unit ownership (Case Handler / Supervisor Unit / System).
4. Reason present when guard requires (cancel; configured reassign policy).
5. Assigned User must not be a Mode A target (BQ-006).

#### Main Flow

1. Actor selects target status / status action.
2. Actor enters reason when required.
3. System validates Appendix B and BR-CM-CAT forbidden transitions.
4. System persists status (or Unit ownership change on `ASSIGNED`→`ASSIGNED`).
5. System writes Timeline + Audit.
6. Business event name per matrix (e.g. CaseWorkStarted, CaseCancelled, CaseReassigned) — **not** an EVT catalog ID.

#### Alternative Flow

| ID | Description |
|---|---|
| A1 | Attempts involving `PENDING`/`ESCALATED` in Mode A Delivery MUST be rejected as not exposed (BQ-009) |
| A2 | Cancel with Mode A reasons: Duplicate / Wrong Input / Customer Cancellation (BQ-014) |
| A3 | `ASSIGNED`→`ASSIGNED` Unit reassign (append-only history; not Assigned User) |

#### Exception Flow

| ID | Condition | Behavior |
|---|---|---|
| E1 | Forbidden / outside Appendix B | MUST reject; status unchanged |
| E2 | Missing required reason | MUST reject |
| E3 | Assigned User target | MUST reject |
| E4 | Unauthorized | MUST reject + audit |
| E5 | Terminal Case | MUST reject |

#### Validation Rules

| Rule | Requirement |
|---|---|
| Transition set | Must be in Appendix B |
| Forbidden matrix | BR-CM-CAT §3 fully applies |
| Unit assign | Unit only |
| Cancel reason | One of Mode A reasons (BQ-014) when cancelling |
| Audit/Timeline | Mandatory on success |

#### State Transition

Normative: **Appendix B**. Summary of Mode A allowed edges:

| From | To |
|---|---|
| `CREATED` | `ASSIGNED` |
| `CREATED` | `CANCELLED` |
| `ASSIGNED` | `IN_PROGRESS` |
| `ASSIGNED` | `ASSIGNED` (Unit reassign) |
| `ASSIGNED` | `CANCELLED` |
| `IN_PROGRESS` | `ASSIGNED` |
| `IN_PROGRESS` | `CANCELLED` |
| `IN_PROGRESS` | `RESOLVED` | via FR-005 (Resolution Accepted), not status-only without resolution |
| `RESOLVED` | `CLOSED` | via FR-006 (Close checklist), not FR-004 without Close preconditions |

#### Postconditions

- Status equals target, or Unit ownership changed on `ASSIGNED` without enum change.
- Timeline + Audit on success.
- No hard-delete.

#### Acceptance Criteria

1. AC-09: Allowed transition → exact target status + Timeline/Audit.
2. AC-10: Forbidden transition → status unchanged.
3. AC-11: Unit only; Assigned User rejected. **[BQ-006]**
4. AC-11b: Mode A Delivery does not expose `PENDING`/`ESCALATED`. **[BQ-009]**
5. AC-11c: Cancel with Mode A reason → `CANCELLED`. **[BQ-014]**

#### Referenced Business Rules

BR-CM-CAT Case Aggregate Transition Matrix; BR-016; BR-017; BR-CAP02-R09, R11, R12, R18, R19.

#### Referenced CAP

CAP-008 — UC-CAP02-04.

#### Referenced Decisions

DEC-BQ001 O3; DEC-MODEA-B2-001 (BQ-001/006/009/014).

#### Traceability

| Item | Ref |
|---|---|
| CAP | CAP-008 |
| UC | UC-CAP02-04 |
| BR / Matrix | BR-CM-CAT Matrix; Appendix B |
| DEC/BQ | DEC-BQ001 O3; BQ-001/006/009/014 |
| AC | AC-09, AC-10, AC-11, AC-11b, AC-11c |
| Namespace | Do not overwrite **FRD-CM-001 FR-004 Attachment Upload** |
| Non-scope | Non-status attribute mutation after create = **NOT SPECIFIED** as Mode A FR |
| API | API-533 |
| EVT | **NOT SPECIFIED** |
| TC | Lab suite `backend/tests/test_cm_case_mode_a.py` (REL-RC-001); formal TC-catalog IDs deferred |

---

### FR-005 Resolve Case

#### Purpose

Record and accept Case Resolution until Case status is `RESOLVED` after Resolution **Accepted**, with Mode A Comment required (BQ-010), append-only history (BR-008), without closing the Complaint.

#### Business Goal

Evidence-based completion of Case substantive work under Unit ownership, ready for Supervisor Approval and Close.

#### Actors

Case Handler (propose); Supervisor Unit (approve); System; Administrator (resolution catalog).

#### Trigger

Actor selects **Propose Resolution** / **Resolve Case**.

#### Preconditions

1. Case status on Mode A Delivery path that allows resolve: **`IN_PROGRESS`** (BQ-008; Appendix B). Resolve from `PENDING`/`ESCALATED` exists in Aggregate matrix but is **not exposed** in Mode A → **NOT SPECIFIED** as Mode A delivery path.
2. Active resolution catalog.
3. Category evidence policy known.
4. Mode A Unit assignment applies (BQ-006); actor is Case Handler of owning Unit or authorized Supervisor.
5. Comment required for Resolve (BQ-010).
6. Attachment optional; Complaint Attachment may be reused (BQ-010).

#### Main Flow

1. Case Handler enters resolution code, summary, actions, customer impact, evidence (if required), and **Comment** (required).
2. Attachment MAY be added or Complaint Attachment MAY be reused.
3. System validates completeness for Case type/category.
4. Resolution proposal status = `PENDING_APPROVAL` (**not** a Case state).
5. Supervisor reviews (Mode A path requires Supervisor Approval before `CLOSED` — BQ-008; Case becomes `RESOLVED` only after Resolution **Accepted** per BR-008 / BR-CAP02-R13).
6. On **Accepted**: Case → `RESOLVED`; Resolution History + Timeline + Audit written.
7. System **MUST NOT** auto-close Complaint (BQ-007). Complaint Closure evaluation = BR-009 — **OUT OF SCOPE** for CAP-008 default execution.

#### Alternative Flow

| ID | Description |
|---|---|
| A1 | Supervisor reject → return to work + mandatory reason; history retained; Case not `RESOLVED` |
| A2 | Multi-attempt Resolution History before final; no overwrite of prior entries |
| A3 | Partial/workaround code + follow-up Case via FR-002 when needed (BR-008 A2) |

#### Exception Flow

| ID | Condition | Behavior |
|---|---|---|
| E1 | Mandatory category evidence missing | MUST reject; Case not Resolved/Closed |
| E2 | Comment missing | MUST reject (BQ-010) |
| E3 | Resolve outside Unit/Supervisor rights | MUST reject (BR-008 E3) |
| E4 | Invalid resolution code | MUST reject |
| E5 | Case not `IN_PROGRESS` on Mode A Delivery | MUST reject |
| E6 | DEC-F4 `result_visibility` / Resolve-by-Pusat | OUT OF SCOPE CAP-008 Mode A; **NOT SPECIFIED** as Mode A delivery requirement |

#### Validation Rules

| Rule | Requirement |
|---|---|
| Case status | `IN_PROGRESS` (Mode A Delivery) |
| Resolution code | Valid active catalog value |
| Summary | Required |
| Comment | Required (BQ-010) |
| Evidence | Per category policy |
| Approval | Accepted before Case `RESOLVED` |
| Complaint auto-close | Forbidden |

#### State Transition

| From | To | Guard |
|---|---|---|
| `IN_PROGRESS` | `RESOLVED` | Complete resolution; Comment required; mandatory evidence satisfied; Resolution **Accepted**; authorized actor |

Forbidden Mode A Delivery: `ASSIGNED`→`RESOLVED`; `CREATED`→`RESOLVED`; exposed `PENDING`/`ESCALATED` resolve paths.

#### Postconditions

- Case = `RESOLVED` only after Accepted.
- Resolution History append-only.
- Resolve Comment recorded.
- Complaint not auto-`CLOSED`.
- SLA countdown remains NOT activated in Mode A (no SLA Engine stop-clock claim in CAP-008).

#### Acceptance Criteria

1. AC-12: Eligible Case + Comment + complete Accepted resolution → Case = `RESOLVED`. **[BQ-008 / BQ-010]**
2. AC-13: Missing mandatory evidence → reject; status not Resolved/Closed.

#### Referenced Business Rules

BR-008; BR-012; BR-013; BR-016; BR-017; BR-CAP02-R13, R14, R17, R11, R12.

#### Referenced CAP

CAP-008 — UC-CAP02-05.

#### Referenced Decisions

DEC-MODEA-B2-001 (BQ-008, BQ-010); DEC-F4 deferred (Escalation OOS for CAP-008 Mode A).

#### Traceability

| Item | Ref |
|---|---|
| CAP | CAP-008 |
| UC | UC-CAP02-05 |
| BR | BR-008, BR-013, BR-012, BR-016, BR-017 |
| DEC/BQ | BQ-008, BQ-010 |
| AC | AC-12, AC-13 |
| API | API-534 (Mode A CAP-008). Do **not** silently equate to API-523 Planned (FRD-CM-002 / DEC-F4) |
| EVT | **NOT SPECIFIED** |
| TC | Lab suite `backend/tests/test_cm_case_mode_a.py` (REL-RC-001); formal TC-catalog IDs deferred |

---

### FR-006 Close Case

#### Purpose

Close the Case work cycle after Resolution Accepted / Case `RESOLVED` and Supervisor Approval completed, setting Case `CLOSED` with `closedBy` + timestamp + Timeline/Audit — **without** closing the Complaint Aggregate (BQ-007; CAP-008 UC-CAP02-06).

#### Business Goal

Officially end Case operational cycle while keeping Aggregate Complaint open until BR-009 (out of CAP-008 default).

#### Actors

Supervisor Unit (primary closer); Case Handler **if configured** — Mode A activation of Handler-close = **NOT SPECIFIED**; System.

#### Trigger

Authorized actor selects **Close Case** after Case `RESOLVED` and Supervisor Approval completed (BQ-008).

#### Preconditions — Close Case Checklist (Operational Specification LOCKED)

| # | Item | Status |
|---|---|---|
| 1 | Case status = `RESOLVED` | SPECIFIED |
| 2 | Final Resolution **Accepted** still valid | SPECIFIED |
| 3 | Supervisor Approval after `RESOLVED` completed | SPECIFIED (BQ-008) |
| 4 | Closer authorized — Supervisor Unit (primary) | SPECIFIED |
| 5 | Case Handler as closer | **NOT SPECIFIED** — matrix: “Handler if configured”; Mode A does not lock activation |
| 6 | Comment / Attachment at Close moment | **NOT SPECIFIED** for Close — Comment required on **Resolve** (BQ-010) |
| 7 | Category evidence at Close moment | **NOT SPECIFIED** for Close — enforced on Resolve (BR-008 E1) |
| 8 | “Checklist Case” items beyond #1–#4 | **NOT SPECIFIED** — SoT says checklist satisfied without enumeration |

**Normative minimum before `CLOSED` = #1 + #2 + #3 + #4.**

#### Main Flow

1. System evaluates checklist minimum (#1–#4).
2. Supervisor Unit confirms Close Case.
3. System sets Case = `CLOSED` + timestamp + `closedBy`.
4. System writes Timeline + Audit (CaseClosed business event name).
5. System **MUST NOT** close Complaint Aggregate (BQ-007), including when this is the last open Case (AC-16).

#### Alternative Flow

| ID | Description |
|---|---|
| A1 | CANCELLED path is not close-with-resolution; use `CANCELLED` via FR-004 (BQ-014) |
| A2 | Business signal for Complaint Closure when all Cases done — BR-009 execution **OUT OF SCOPE** CAP-008 default |
| A3 | Case Handler as closer — **NOT SPECIFIED** whether Mode A activates this configuration |

#### Exception Flow

| ID | Condition | Behavior |
|---|---|---|
| E1 | Not yet `RESOLVED` | MUST reject |
| E2 | Supervisor Approval not completed | MUST reject |
| E3 | Unauthorized | MUST reject |
| E4 | Attempt to auto-close Complaint | MUST NOT occur |

#### Validation Rules

| Rule | Requirement |
|---|---|
| Checklist | Minimum #1–#4 required |
| Items #5–#8 | **NOT SPECIFIED** — must not be invented as mandatory Mode A Close gates |
| Complaint | MUST remain not auto-closed |
| Audit fields | `closedBy` + timestamp required on success |

#### State Transition

| From | To | Guard |
|---|---|---|
| `RESOLVED` | `CLOSED` | Checklist minimum #1–#4; authorized closer |

Forbidden: Close from non-`RESOLVED`; Close that closes Complaint; un-close.

#### Postconditions

- Case = `CLOSED` (terminal).
- `closedBy` + timestamp present.
- Timeline + Audit present.
- Complaint status does not become `CLOSED` solely due to Close Case.
- No Case-level exit from `CLOSED` (rework via BR-015 + new Case — OUT OF SCOPE CAP-008).

#### Acceptance Criteria

1. AC-14: `RESOLVED` + Supervisor Approval completed → Close → Case = `CLOSED` with closedBy + timestamp. **[BQ-008]**
2. AC-15: Successful Close with other Cases still open → Complaint not `CLOSED` solely due to one Case.
3. AC-16: Close of last open Case → Complaint remains open (Close Case ≠ auto Complaint Closure). **[BQ-007]**

#### Referenced Business Rules

BR-CM-CAT `RESOLVED→CLOSED`; BR-016; BR-017; BR-CAP02-R13, R15, R11, R12; BR-009 boundary (not executed).

#### Referenced CAP

CAP-008 — UC-CAP02-06.

#### Referenced Decisions

DEC-MODEA-B2-001 (BQ-007, BQ-008).

#### Traceability

| Item | Ref |
|---|---|
| CAP | CAP-008 |
| UC | UC-CAP02-06 |
| BR / Matrix | `RESOLVED→CLOSED`; Appendix C |
| DEC/BQ | BQ-007, BQ-008 |
| AC | AC-14, AC-15, AC-16 |
| API | API-535 |
| EVT | **NOT SPECIFIED** |
| TC | Lab suite `backend/tests/test_cm_case_mode_a.py` (REL-RC-001); formal TC-catalog IDs deferred |

---

## 8. Business Validation Rules

| ID | Rule |
|---|---|
| V-01 | Case MUST have a valid parent Complaint |
| V-02 | One Complaint MAY have 1..N Cases; Mode A max N = **5** |
| V-03 | Batch-1 Complaint MAY start without Case (D-02); MUST have ≥1 Case within 1 working day after `REGISTERED` (BQ-002; BC-5.4 timing) |
| V-04 | Case Number = `CASE-YYYY-NNNNNN`, unique, independent of Complaint Number |
| V-05 | Mode A assignment = Unit only; Assigned User rejected |
| V-06 | SLA Policy Version MUST bind; countdown MUST NOT activate in Mode A |
| V-07 | Case status changes only via Appendix B / BR-CM-CAT; forbidden matrix applies fully |
| V-08 | `PENDING`/`ESCALATED` not exposed in Mode A Delivery |
| V-09 | Hard-delete Case forbidden; cancel via `CANCELLED` + BQ-014 reason |
| V-10 | Successful Create / Status change / Resolve / Close MUST write Timeline + Audit |
| V-11 | Resolve requires Comment; Attachment optional |
| V-12 | Close Case MUST NOT auto-close Complaint |
| V-13 | Mode A path: `IN_PROGRESS` → `RESOLVED` → Supervisor Approval → `CLOSED` |
| V-14 | Authorization ECMP-internal; Mode B OUT |
| V-15 | DOM-ECMF-003 enums forbidden on Aggregate Case CAP-008 |
| V-16 | Attachment anchored to Case MUST share Aggregate membership |
| V-17 | Close checklist minimum = Appendix C #1–#4; beyond = **NOT SPECIFIED** |
| V-18 | Case Handler closer activation Mode A = **NOT SPECIFIED** |
| V-19 | Notification Engine / Dashboard / Reporting / AI are not CAP-008 acceptance (AC-19/AC-20) |

---

## 9. Acceptance Criteria

Catalog from CAP-008 BCS §9 + Mode A locks (cross-FR).

### Create / Add

| ID | Criterion |
|---|---|
| AC-01 | Create success → `CASE-YYYY-NNNNNN` + initial status + Timeline/Audit **[BQ-004]** |
| AC-02 | First Case on `REGISTERED` → Complaint `IN_PROGRESS` |
| AC-03 | Add Case N&lt;5 → N+1; N=5 → reject **[BQ-003]** |
| AC-04 | Complaint `CLOSED` → Create/Add reject |
| AC-05 | Case without Complaint → reject 100% |
| AC-05b | Aging &gt;1 working day without Case → Supervisor Queue exceedance **[BQ-002]** |

### View / Timeline

| ID | Criterion |
|---|---|
| AC-06 | View minimum fields present |
| AC-07 | Cross-membership rejected |
| AC-08 | Timeline append-only after successful write |

### Update Status

| ID | Criterion |
|---|---|
| AC-09 | Allowed → exact target + Timeline/Audit |
| AC-10 | Forbidden → unchanged |
| AC-11 | Unit only; Assigned User rejected **[BQ-006]** |
| AC-11b | `PENDING`/`ESCALATED` not exposed **[BQ-009]** |
| AC-11c | Mode A cancel reasons → `CANCELLED` **[BQ-014]** |

### Resolve / Close

| ID | Criterion |
|---|---|
| AC-12 | Eligible + Comment + Accepted → `RESOLVED` **[BQ-008/010]** |
| AC-13 | Missing mandatory evidence → reject |
| AC-14 | `RESOLVED` + Supervisor Approval → `CLOSED` + closedBy/timestamp **[BQ-008]** |
| AC-15 | Close one Case ≠ Complaint auto-`CLOSED` if others open |
| AC-16 | Close last open Case ≠ auto Complaint Closure **[BQ-007]** |

### Honesty / non-goals

| ID | Criterion |
|---|---|
| AC-17 | Bind SLA Policy Version; countdown NOT activated **[BQ-005]** |
| AC-18 | No Assignment Engine auto-route/claim/bulk **[BQ-006]** |
| AC-19 | Mode B not CAP-008 acceptance |
| AC-20 | No Dashboard / Reporting / Notification Engine / AI acceptance |

---

## 10. Traceability Matrix

### 10.1 FR → CAP → UC → BR → DEC/BQ → AC

| FR | CAP | UC | BR / Matrix | DEC / BQ | AC |
|---|---|---|---|---|---|
| FR-001 Create Case | CAP-008 | UC-CAP02-01 | BR-004; BR-016; BR-017 | DEC-MODEA-B2-001; BQ-002…006,011 | AC-01,02,04,05,05b,17,18 |
| FR-002 Add Case | CAP-008 | UC-CAP02-02 | BR-004; BR-014 | BQ-003 | AC-03,04 |
| FR-003 View Case | CAP-008 | UC-CAP02-03/07 | BR-017; R01/R16/R19 | DEC-BQ001 O3; DEC-020 | AC-06,07,08 |
| FR-004 Update Case Status | CAP-008 | UC-CAP02-04 | BR-CM-CAT Matrix; Appendix B | DEC-BQ001 O3; BQ-001/006/009/014 | AC-09,10,11,11b,11c |
| FR-005 Resolve Case | CAP-008 | UC-CAP02-05 | BR-008; R13/R14/R17 | BQ-008/010 | AC-12,13 |
| FR-006 Close Case | CAP-008 | UC-CAP02-06 | `RESOLVED→CLOSED`; Appendix C | BQ-007/008 | AC-14,15,16 |

### 10.2 API / Event / Test

| FR (document-local) | Trace ID | API Catalog | Event Catalog | Test evidence |
|---|---|---|---|---|
| FR-001 Create Case | FR-CM-B2-001 | API-530 | **NOT SPECIFIED** | `backend/tests/test_cm_case_mode_a.py` (REL-RC-001) |
| FR-002 Add Case | FR-CM-B2-002 | API-531 | **NOT SPECIFIED** | same lab suite |
| FR-003 View Case | FR-CM-B2-003 | API-532 | **NOT SPECIFIED** | same lab suite |
| FR-004 Update Case Status | FR-CM-B2-004 | API-533 | **NOT SPECIFIED** | same lab suite |
| FR-005 Resolve Case | FR-CM-B2-005 | API-534 | **NOT SPECIFIED** | same lab suite |
| FR-006 Close Case | FR-CM-B2-006 | API-535 | **NOT SPECIFIED** | same lab suite |

OpenAPI SoT: `07 API Catalog/openapi/cm-case-management.v1.yaml` v1.0.0. Formal TC-catalog IDs = deferred (not invented).

### 10.3 Locked source artifacts (read-only for this authoring)

| Artifact | Role |
|---|---|
| CAP-008 BCS v1.2 | Capability / UC / AC baseline |
| BR-CM-CAT-001 | BR-004/008 + Transition Matrix SoT |
| DEC-BQ001 O3 | Dual SoT Case status |
| DEC-MODEA-B2-001 | BQ lock pack |
| FRD-CM-001 v1.1 | Batch-1 intake; D-02 |
| Operational Specification | Embedded §§5.2, Appendix B/C/D |

---

## 11. Appendix

### Appendix A — Unit Ownership Semantics

See §5.2 (normative Operational Specification LOCKED).

### Appendix B — Mode A Delivery Transition Subset (Operational Specification LOCKED)

**Parent SoT:** BR-CM-CAT Case Aggregate Transition Matrix (unchanged).  
**Delivery filter:** BQ-006, BQ-008, BQ-009, BQ-014 + CAP-008 UC-04 A1.

#### B.1 States exposed

`CREATED` · `ASSIGNED` · `IN_PROGRESS` · `RESOLVED` · `CLOSED` · `CANCELLED`

**Not exposed:** `PENDING` · `ESCALATED`

#### B.2 Initial

| From | To | Guard Mode A |
|---|---|---|
| *(none)* | `CREATED` | Create/Add success without simultaneous Unit assign |
| *(none)* | `ASSIGNED` | Create/Add + Unit assignment only (BQ-006); Assigned User rejected |

#### B.3 Allowed (explicit — no hidden transitions)

| From | To | Mode A intent |
|---|---|---|
| `CREATED` | `ASSIGNED` | First Unit assign |
| `CREATED` | `CANCELLED` | Cancel + BQ-014 reason |
| `ASSIGNED` | `IN_PROGRESS` | Start work (Handler Unit / Supervisor Unit) |
| `ASSIGNED` | `ASSIGNED` | Reassign **Unit** |
| `ASSIGNED` | `CANCELLED` | Cancel + BQ-014 reason |
| `IN_PROGRESS` | `ASSIGNED` | Reassign Unit |
| `IN_PROGRESS` | `RESOLVED` | Resolution Accepted (+ Comment BQ-010) — FR-005 |
| `IN_PROGRESS` | `CANCELLED` | Cancel + BQ-014 reason |
| `RESOLVED` | `CLOSED` | Supervisor Approval completed (BQ-008) — FR-006 |

#### B.4 Forbidden (Mode A Delivery)

1. All BR-CM-CAT §3 forbidden transitions.
2. Any transition with `PENDING` or `ESCALATED` as from/to (BQ-009).
3. Assignment/reassignment to Assigned User (BQ-006).
4. `RESOLVED`→`CLOSED` without Supervisor Approval (BQ-008).
5. Close Case that closes Complaint Aggregate (BQ-007).
6. DOM-ECMF-003 enums on Aggregate Case CAP-008.
7. Reopen by mutating `CLOSED` → working Case status.

#### B.5 Terminal

| State | Terminal |
|---|---|
| `CLOSED` | Yes |
| `CANCELLED` | Yes |

### Appendix C — Close Case Checklist

See FR-006 Preconditions. Normative minimum = #1–#4. Items #5–#8 = **NOT SPECIFIED**.

### Appendix D — FR-004 Rename (Operational Specification LOCKED)

| Field | Value |
|---|---|
| FR ID (Batch-2 document-local) | **FR-004** |
| Title (normative) | **Update Case Status** |
| Former informal title | Update Case |
| Aligns to | CAP-008 §2.1; UC-CAP02-04 |
| Non-scope | Non-status attribute mutation after create — **NOT SPECIFIED** as Mode A FR |
| Collision warning | Do not overwrite **FRD-CM-001 FR-004 Attachment Upload** |

### Appendix E — NOT SPECIFIED register

| # | Topic | FRD statement |
|---|---|---|
| 1 | Case Handler as closer Mode A | **NOT SPECIFIED** |
| 2 | Comment/Attachment required at Close moment | **NOT SPECIFIED** |
| 3 | Category evidence required at Close moment | **NOT SPECIFIED** |
| 4 | Checklist Case items beyond #1–#4 | **NOT SPECIFIED** |
| 5 | OpenAPI Aggregate CAP-008 for FR-001…006 | **SPECIFIED** — API-530…535 / `cm-case-management.v1.yaml` v1.0.0 (SoT Closure 2026-08-01) |
| 6 | EVT catalog IDs Aggregate CAP-008 | **NOT SPECIFIED** |
| 7 | Formal TC-catalog IDs CAP-008 | **Deferred** — lab evidence `backend/tests/test_cm_case_mode_a.py` (REL-RC-001); IDs not invented |
| 8 | Non-status Case attribute mutation after create | **NOT SPECIFIED** |
| 9 | Mode A Resolve from `PENDING`/`ESCALATED` | **NOT SPECIFIED** as delivery path |
| 10 | DEC-F4 `result_visibility` on CAP-008 Mode A | **NOT SPECIFIED** / OUT |
| 11 | Sensitive-read Audit mandatory on every View | **NOT SPECIFIED** beyond BR-016 general |

---

## 12. Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-08-01 | ECMP Functional Specification Author | Draft v1.0 complete authoring from locked CAP-008, BR-CM-CAT, Transition Matrix, DEC-MODEA-B2-001, DEC-BQ001 O3, and locked Operational Specification (embedded). Status = Draft v1.0. NOT SPECIFIED copied without invention. BR/CAP/Matrix/DEC not modified. |
| 1.0 LOCKED | 2026-08-01 | Architecture Review Board (SoT Closure) | Status → **LOCKED**. Sync API-530…535 + lab test suite refs to match RC-validated implementation. EVT IDs remain NOT SPECIFIED. No FR redesign; no BR/BCS/scope/Mode B change. Evidence: `deploy/evidence/CAP-008_SoT_Closure_20260801.md`. |
| 1.0 LOCKED + BC/BW align | 2026-08-05 | Documentation Architect | Alignment P-03/P-06/P-07/P-08: BC/BW precedence; persona → Complaint Officer + Manager; BQ-002 working day wording; Regional OOS note. **No FR redesign.** |
