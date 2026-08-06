# BC-000 — ECMP Business Constitution

| Field | Value |
|---|---|
| Document ID | BC-000 |
| Title | ECMP Business Constitution — Mode A Baseline |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | **NORMATIVE — Mode A Baseline** |
| Milestone | Governance Phase 1 |
| Authority | Derived exclusively from approved governance decisions (Phase 0) |
| Subordination | **Board Resolution → ADR → EA Documents → ECMP-CONSTITUTION-001 → BC-000** |
| Applicability | **Mode A only** |
| Does not | Unlock Mode B · invent Business Rules · specify UI, API, database, or code · reinterpret Phase 0 decisions |

---

# 1 Purpose

## BC-1.1

| Field | Content |
|---|---|
| **Clause ID** | BC-1.1 |
| **Requirement** | BC-000 SHALL be the highest-level **business** normative document for the ECMP Complaint Management Module under Mode A. BC-000 SHALL define **what** governs ECMP business behaviour. BC-000 SHALL NOT define **how** ECMP is implemented. |
| **Rationale** | Separates constitutional business obligations from implementation, UX screens, and technical design. |
| **Source Artifact(s)** | GC-000; DRR-000 §7; DL-046 |
| **Decision ID(s)** | DL-046; GC-000 |

## BC-1.2

| Field | Content |
|---|---|
| **Clause ID** | BC-1.2 |
| **Requirement** | Every normative statement in BC-000 SHALL be traceable to one or more approved governance decisions. A statement that cannot be traced SHALL NOT appear as a constitutional requirement. |
| **Rationale** | Prevents invention of business decisions inside the Constitution. |
| **Source Artifact(s)** | GC-000 §7–§8; DRR-000 methodology |
| **Decision ID(s)** | GC-000 |

## BC-1.3

| Field | Content |
|---|---|
| **Clause ID** | BC-1.3 |
| **Requirement** | BC-000 SHALL remain subordinate to Board Resolutions, ADRs, EA Documents, and ECMP-CONSTITUTION-001 (DL-046). BC-000 SHALL NOT override Board or ADR decisions. |
| **Rationale** | Preserves the locked conflict-order of the module operating constitution. |
| **Source Artifact(s)** | ECMP-CONSTITUTION-001; DL-046 |
| **Decision ID(s)** | DL-046 |

## BC-1.4

| Field | Content |
|---|---|
| **Clause ID** | BC-1.4 |
| **Requirement** | The North Star of ECMP SHALL remain: complete the Complaint Management Module with correct architecture so that, when Enterprise integration opens, only integration mechanisms change—not the complaint business domain. |
| **Rationale** | Binding project mission for all subordinate artefacts. |
| **Source Artifact(s)** | ECMP-CONSTITUTION-001; DL-046 |
| **Decision ID(s)** | DL-046 |

---

# 2 Scope

## BC-2.1 — Mode A

| Field | Content |
|---|---|
| **Clause ID** | BC-2.1 |
| **Requirement** | This Constitution SHALL apply to **Mode A**: the authorized delivery strategy that completes the Complaint Management Module without waiting for Enterprise Platform integration. Mode A and Mode B SHALL NOT be treated as two products or two target architectures; the target remains one Business Module. |
| **Rationale** | Mode A is delivery strategy, not a separate product. |
| **Source Artifact(s)** | ECMP-CONSTITUTION-001 §4; DL-046 |
| **Decision ID(s)** | DL-046 |

## BC-2.2 — In Scope (Mode A)

| Field | Content |
|---|---|
| **Clause ID** | BC-2.2 |
| **Requirement** | Mode A constitutional scope SHALL include: Complaint lifecycle domain behaviour; Head Office Escalation limited to **Branch ↔ Head Office**; Appointment as part of the **same** Complaint Lifecycle (not a separate lifecycle); Case management rules locked for Mode A; one SLA Constitution for the Complaint Lifecycle; operational personas Complaint Officer, Supervisor, and Manager; write-audit and immutable audit obligations; configuration-versus-hardcoded rule classification; Role-Permission SoT in Core Platform; Workflow Config SoT in Administration with ECMF as enforcer; and the prohibition on ECMP being Customer Master SoR. |
| **Rationale** | Aggregates approved Mode A business decisions required for constitutional coverage. |
| **Source Artifact(s)** | DL-066; DL-067; DL-068; DL-001; DL-023; DL-024; DL-019; DL-025; DL-026; DL-031; DL-056; DL-063; DL-064; DL-065; GC-000 |
| **Decision ID(s)** | DL-066; DL-067; DL-068; DL-001; DL-023; DL-024; DL-019; DL-025; DL-026; DL-031; DL-056; DL-063; DL-064; DL-065 |

## BC-2.3 — Out of Scope (pointer)

| Field | Content |
|---|---|
| **Clause ID** | BC-2.3 |
| **Requirement** | Capabilities listed in **§11 Out of Scope** SHALL NOT be treated as constituted Mode A obligations. Their inclusion SHALL require a new Decision Record and Governance Review before any constitutional amendment. |
| **Rationale** | Business Owner explicit OOS boundary. |
| **Source Artifact(s)** | DL-066; GC-000; BO-WS-000 |
| **Decision ID(s)** | DL-066 |

---

# 3 Governance Hierarchy

## BC-3.1

| Field | Content |
|---|---|
| **Clause ID** | BC-3.1 |
| **Requirement** | Normative precedence for **business content** under Mode A SHALL follow: **Business Constitution (BC-000)** → Business Principles (when issued) → Business Rules (`BR-0xx`) → UX contracts (approved) → Domain specifications → Architecture (ADR/EA) → Implementation. A lower layer SHALL NOT contradict a higher layer without a governed Decision Record. |
| **Rationale** | Establishes reading order for business governance without inventing missing Business Principles content. |
| **Source Artifact(s)** | DL-003; DL-047; GC-000 §6; DRR-000 §7 |
| **Decision ID(s)** | DL-003; DL-047; GC-000 |

## BC-3.2

| Field | Content |
|---|---|
| **Clause ID** | BC-3.2 |
| **Requirement** | Delivery work SHALL be classified into exactly one category: **A — Constitution**, **B — Specification**, or **C — Implementation**, per GOV-001. Category C SHALL NOT proceed without Category B readiness (DoR). Spontaneous proposals for new platforms, engines, out-of-scope capabilities, or wholesale redesigns SHALL NOT be advanced without Board/ADR authority. |
| **Rationale** | Prevents mixing permanent rules, specifications, and implementation. |
| **Source Artifact(s)** | DL-047; ECMP-GOV-001 |
| **Decision ID(s)** | DL-047 |

## BC-3.3

| Field | Content |
|---|---|
| **Clause ID** | BC-3.3 |
| **Requirement** | Business rule identifiers used by this Constitution and subordinate catalogues SHALL use the `BR-0xx` scheme. |
| **Rationale** | Single ID scheme for business rules. |
| **Source Artifact(s)** | DL-003 |
| **Decision ID(s)** | DL-003 |

## BC-3.4

| Field | Content |
|---|---|
| **Clause ID** | BC-3.4 |
| **Requirement** | Dual Sources of Truth for Case/Complaint namespaces SHALL remain until a Retirement DEC is issued. Force-merge or silent retirement of dual-SoT SHALL NOT occur. |
| **Rationale** | Forbidden behaviour under the module constitution and dual-SoT decisions. |
| **Source Artifact(s)** | DL-023; DL-044; DL-046; DL-027 |
| **Decision ID(s)** | DL-023; DL-044; DL-046; DL-027 |

---

# 4 Definitions

Normative definitions only. Terms without an approved Decision Log definition are marked **RESERVED** and SHALL NOT be used as if constituted.

## BC-4.1 Complaint

| Field | Content |
|---|---|
| **Clause ID** | BC-4.1 |
| **Requirement** | **Complaint** SHALL mean the complaint business aggregate that may originate from multiple source types and target Branch or Head Office, while remaining a single aggregate. |
| **Rationale** | Multi-source/multi-target model without splitting the aggregate. |
| **Source Artifact(s)** | DL-006 |
| **Decision ID(s)** | DL-006 |

## BC-4.2 Case (and Ticket)

| Field | Content |
|---|---|
| **Clause ID** | BC-4.2 |
| **Requirement** | **Case** SHALL mean a work unit under a Complaint subject to Mode A Case Management rules (DL-024) and the applicable state-machine definition for its SoT (DL-023). The term **Ticket**, as listed among module capabilities in ECMP-CONSTITUTION-001, SHALL NOT be construed in this Constitution as a requirement that every Complaint has exactly one Ticket/Case at registration. |
| **Rationale** | Aligns vocabulary with approved Case decisions; avoids inventing a 1:1 Ticket rule contradicted by BQ-002. |
| **Source Artifact(s)** | DL-023; DL-024; DL-046 (capability list) |
| **Decision ID(s)** | DL-023; DL-024; DL-046 |

## BC-4.3 Timeline

| Field | Content |
|---|---|
| **Clause ID** | BC-4.3 |
| **Requirement** | **Timeline** SHALL mean the chronological business record of significant Complaint/Case events, including events required when SLA status changes. |
| **Rationale** | SLA Constitution requires Timeline Events for SLA changes. |
| **Source Artifact(s)** | DL-067; DL-018 (related; implementation detail out of BC depth) |
| **Decision ID(s)** | DL-067 |

## BC-4.4 Event

| Field | Content |
|---|---|
| **Clause ID** | BC-4.4 |
| **Requirement** | **Event** (Timeline Event) SHALL mean a recorded occurrence on the Timeline that captures a business-significant change. SLA-related changes SHALL be recorded as Timeline Events. |
| **Rationale** | Uniform SLA Constitution obligation. |
| **Source Artifact(s)** | DL-067 |
| **Decision ID(s)** | DL-067 |

## BC-4.5 Organization

| Field | Content |
|---|---|
| **Clause ID** | BC-4.5 |
| **Requirement** | For Mode A constitutional scope, **Organization** units referenced by Escalation SHALL include **Branch** and **Head Office** on the path Branch ↔ Head Office. Regional Office SHALL NOT be part of that path. |
| **Rationale** | Scope Consolidation Mode A. |
| **Source Artifact(s)** | DL-066 |
| **Decision ID(s)** | DL-066 |

## BC-4.6 Persona

| Field | Content |
|---|---|
| **Clause ID** | BC-4.6 |
| **Requirement** | **Persona** SHALL mean a business actor class in the operational closed set: Complaint Officer, Supervisor, Manager. Administrator SHALL be outside that operational closed set (configuration persona). |
| **Rationale** | Approved merge and closed set. |
| **Source Artifact(s)** | DL-001; DL-068 |
| **Decision ID(s)** | DL-001; DL-068 |

## BC-4.7 Assignment

| Field | Content |
|---|---|
| **Clause ID** | BC-4.7 |
| **Requirement** | **Assignment** in Mode A SHALL mean assignment at **Unit** level. Assignment to an individual Assigned User SHALL be outside Mode A. |
| **Rationale** | Mode A Case baseline. |
| **Source Artifact(s)** | DL-024 (BQ-006) |
| **Decision ID(s)** | DL-024 |

## BC-4.8 Escalation

| Field | Content |
|---|---|
| **Clause ID** | BC-4.8 |
| **Requirement** | **Escalation** (Head Office Escalation) SHALL mean the official Complaint Lifecycle capability transferring work along **Branch ↔ Head Office**. |
| **Rationale** | Business Owner Scope Consolidation. |
| **Source Artifact(s)** | DL-066 |
| **Decision ID(s)** | DL-066 |

## BC-4.9 Snapshot

| Field | Content |
|---|---|
| **Clause ID** | BC-4.9 |
| **Requirement** | **Snapshot** (SLA Policy binding) SHALL mean the binding of a Case to an SLA Policy Version under Mode A. Mode A SHALL bind SLA Policy Version without activating countdown (**bind-without-clock**). Detailed calculator/breach-engine behaviour SHALL be governed by Business Rules and subordinate specifications under the single SLA Constitution (DL-067), not redefined here as implementation steps. |
| **Rationale** | Combines BQ-005 with BO SLA Constitution without importing implementation-only DEC-012/013 into constitutional HOW. |
| **Source Artifact(s)** | DL-024 (BQ-005); DL-067; DL-019 |
| **Decision ID(s)** | DL-024; DL-067; DL-019 |

## BC-4.10 Owner (constitutional sense)

| Field | Content |
|---|---|
| **Clause ID** | BC-4.10 |
| **Requirement** | **Owner** of a configuration or authorization SoT SHALL mean the party named by the applicable ownership decision (Administration for Workflow Config definition; Core Platform for Role-Permission; ECMF as enforcer of workflow transitions). |
| **Rationale** | Prevents dual authoritative copies. |
| **Source Artifact(s)** | DL-025; DL-056 |
| **Decision ID(s)** | DL-025; DL-056 |

## BC-4.11 Receiving Organization — RESERVED

| Field | Content |
|---|---|
| **Clause ID** | BC-4.11 |
| **Requirement** | The term **Receiving Organization** is **RESERVED**. No approved Decision Log record defines this exact term as constitutional vocabulary. BC-000 SHALL NOT invent its meaning. |
| **Rationale** | Traceability rule: no untraceable definitions. |
| **Source Artifact(s)** | GC-000 validation principle; DL-012 status PENDING for formal DEC |
| **Decision ID(s)** | — (gap acknowledged; not filled) |

## BC-4.12 Current Owning Organization — RESERVED

| Field | Content |
|---|---|
| **Clause ID** | BC-4.12 |
| **Requirement** | The term **Current Owning Organization** is **RESERVED**. No approved Decision Log record defines this exact term as constitutional vocabulary. BC-000 SHALL NOT invent its meaning. |
| **Rationale** | Traceability rule: no untraceable definitions. |
| **Source Artifact(s)** | GC-000 validation principle; DL-012 status PENDING for formal DEC |
| **Decision ID(s)** | — (gap acknowledged; not filled) |

---

# 5 Constitutional Principles

## BC-5.1

| Field | Content |
|---|---|
| **Clause ID** | BC-5.1 |
| **Requirement** | ECMP SHALL be a Complaint Management **Business Module**, not an Enterprise Platform, Enterprise OS, generic multi-module framework, SDK, marketplace, or enterprise portal/runtime registry. |
| **Rationale** | Product boundary. |
| **Source Artifact(s)** | DL-046 |
| **Decision ID(s)** | DL-046 |

## BC-5.2

| Field | Content |
|---|---|
| **Clause ID** | BC-5.2 |
| **Requirement** | ECMP SHALL NOT be the System of Record for customer master data. Customer data held locally SHALL be treated as read-only cache relative to Customer Master. |
| **Rationale** | Data ownership boundary. |
| **Source Artifact(s)** | DL-031 |
| **Decision ID(s)** | DL-031 |

## BC-5.3

| Field | Content |
|---|---|
| **Clause ID** | BC-5.3 |
| **Requirement** | There SHALL be exactly one official **SLA Constitution** for the entire Complaint Lifecycle. SLA SHALL be computed according to uniform business rules. Every SLA change SHALL be recorded as Timeline Event(s). Technical implementation detail SHALL follow this Constitution and Business Rules. |
| **Rationale** | Business Owner SLA disposition closing conflicting business readings. |
| **Source Artifact(s)** | DL-067; GC-000 |
| **Decision ID(s)** | DL-067 |

## BC-5.4

| Field | Content |
|---|---|
| **Clause ID** | BC-5.4 |
| **Requirement** | A Complaint MAY be registered without a Case. Every Complaint MUST have at least one Case within one working day after `REGISTERED`. The Supervisor Queue MUST surface Complaints that miss this threshold. |
| **Rationale** | Mode A Case baseline. |
| **Source Artifact(s)** | DL-024 (BQ-002) |
| **Decision ID(s)** | DL-024 |

## BC-5.5

| Field | Content |
|---|---|
| **Clause ID** | BC-5.5 |
| **Requirement** | Closing a Case SHALL transition that Case to `CLOSED` only and MUST NOT automatically close the Complaint Aggregate. |
| **Rationale** | Separates Case closure from Complaint closure. |
| **Source Artifact(s)** | DL-024 (BQ-007) |
| **Decision ID(s)** | DL-024 |

## BC-5.6

| Field | Content |
|---|---|
| **Clause ID** | BC-5.6 |
| **Requirement** | Rules classified as **Hardcoded** (including mandatory authentication, immutable audit trail, read-only dashboard nature, and mandatory resolution at closure as listed in ADR-003 / DL-026) SHALL NOT be disableable configuration options. Rules classified as **Configuration** SHALL be managed via versioned configuration with effective dating. |
| **Rationale** | Protects integrity rules while allowing operational change of process rules. |
| **Source Artifact(s)** | DL-026; DL-064 |
| **Decision ID(s)** | DL-026; DL-064 |

## BC-5.7

| Field | Content |
|---|---|
| **Clause ID** | BC-5.7 |
| **Requirement** | Write-audit SHALL be mandatory. Read-audit SHALL remain deferred until a later Decision Record activates it. |
| **Rationale** | Approved audit obligation with explicit deferral. |
| **Source Artifact(s)** | DL-063 |
| **Decision ID(s)** | DL-063 |

## BC-5.8

| Field | Content |
|---|---|
| **Clause ID** | BC-5.8 |
| **Requirement** | Appointment SHALL be part of official Mode A scope and SHALL follow the same Complaint Lifecycle; Appointment SHALL NOT constitute a separate lifecycle. |
| **Rationale** | Scope Consolidation. |
| **Source Artifact(s)** | DL-066 |
| **Decision ID(s)** | DL-066 |

## BC-5.9

| Field | Content |
|---|---|
| **Clause ID** | BC-5.9 |
| **Requirement** | Head Office Escalation SHALL be part of the official Complaint Lifecycle, limited to Branch ↔ Head Office. |
| **Rationale** | Scope Consolidation. |
| **Source Artifact(s)** | DL-066 |
| **Decision ID(s)** | DL-066 |

## BC-5.10

| Field | Content |
|---|---|
| **Clause ID** | BC-5.10 |
| **Requirement** | Experience work inside Case Workspace SHALL obey CWX Golden Rules: Business First; Case is the Product (Queue as entry); Context Before Action; Zero Duplicate Context; Progressive Disclosure; Context-Aware Experience; Experience Above Implementation; No Rewrite Without Decision; Reference, Don't Redefine. CWX SHALL NOT redefine Business Rules, API, Domain Model, or Architecture. |
| **Rationale** | Locked experience constitution. |
| **Source Artifact(s)** | DL-027 |
| **Decision ID(s)** | DL-027 |

---

# 6 Timeline Constitution

## BC-6.1

| Field | Content |
|---|---|
| **Clause ID** | BC-6.1 |
| **Requirement** | SLA-related changes SHALL be recorded on the Timeline as Events. |
| **Rationale** | Uniform SLA Constitution. |
| **Source Artifact(s)** | DL-067 |
| **Decision ID(s)** | DL-067 |

## BC-6.2

| Field | Content |
|---|---|
| **Clause ID** | BC-6.2 |
| **Requirement** | Audit trails that record governed writes SHALL be **immutable**. Authorization overrides SHALL be performed only by Administrator with recorded justification and audit trail. |
| **Rationale** | Hardcoded integrity + override accountability. |
| **Source Artifact(s)** | DL-064; DL-026 |
| **Decision ID(s)** | DL-064; DL-026 |

## BC-6.3

| Field | Content |
|---|---|
| **Clause ID** | BC-6.3 |
| **Requirement** | Changes to Role-Permission configuration and Workflow Config SHALL be audited. |
| **Rationale** | Critical configuration accountability. |
| **Source Artifact(s)** | DL-065 |
| **Decision ID(s)** | DL-065 |

## BC-6.4

| Field | Content |
|---|---|
| **Clause ID** | BC-6.4 |
| **Requirement** | This Constitution SHALL NOT prescribe Timeline Event payload schemas, API shapes, storage tables, or actor-id encoding. Those details SHALL be specified in Event Catalog / Business Rules / subordinate specifications consistent with BC-6.1–BC-6.3. |
| **Rationale** | Constitution states WHAT, not HOW. |
| **Source Artifact(s)** | GC-000; DL-067 |
| **Decision ID(s)** | DL-067; GC-000 |

## BC-6.5

| Field | Content |
|---|---|
| **Clause ID** | BC-6.5 |
| **Requirement** | Baseline SLA calendar SHALL be **24×7**. Working-day calendars SHALL remain DEFERRED until a Business Owner DEC activates them. Pause/Resume SLA SHALL remain DEFERRED for CAP-006 v1. Case-type SLA differentiation SHALL remain DEFERRED until a Business Owner DEC. |
| **Rationale** | Locked CAP-006 business closures and baseline defaults. |
| **Source Artifact(s)** | DL-019; DL-004 |
| **Decision ID(s)** | DL-019; DL-004 |

## BC-6.6

| Field | Content |
|---|---|
| **Clause ID** | BC-6.6 |
| **Requirement** | Numeric SLA/NFR baseline targets approved as baseline ARB values SHALL be treated as **references** revisable by Business Owner via DEC, not as irreversible constants of this Constitution. |
| **Rationale** | Reversible baselines. |
| **Source Artifact(s)** | DL-005; DL-004 |
| **Decision ID(s)** | DL-005; DL-004 |

---

# 7 Organization Constitution

## BC-7.1

| Field | Content |
|---|---|
| **Clause ID** | BC-7.1 |
| **Requirement** | Escalation routing under this Constitution SHALL use the path **Branch → Head Office** (and return along that path as constituted by later approved Escalation decisions). **Regional Office** SHALL NOT be a node on the complaint escalation path. |
| **Rationale** | Scope Consolidation Mode A. |
| **Source Artifact(s)** | DL-066 |
| **Decision ID(s)** | DL-066 |

## BC-7.2

| Field | Content |
|---|---|
| **Clause ID** | BC-7.2 |
| **Requirement** | Complaint targeting SHALL support `BRANCH` and `HEAD_OFFICE` targets within the single Complaint aggregate model. |
| **Rationale** | Multi-target complaint model. |
| **Source Artifact(s)** | DL-006 |
| **Decision ID(s)** | DL-006 |

## BC-7.3

| Field | Content |
|---|---|
| **Clause ID** | BC-7.3 |
| **Requirement** | Detailed visibility, return, and result-audience rules from DEC-F4 SHALL NOT be elevated to constitutional force in BC-000 until DEC-F4 formal approval/countersign is complete (DL-012 remains PENDING for formal DEC). Branch ↔ Head Office **scope** remains constituted by DL-066. |
| **Rationale** | Do not promote PENDING formal DEC content into Constitution. |
| **Source Artifact(s)** | DL-012; DL-066; DRR-000; GC-000 |
| **Decision ID(s)** | DL-066 (scope); DL-012 (pending formal) |

## BC-7.4

| Field | Content |
|---|---|
| **Clause ID** | BC-7.4 |
| **Requirement** | Enterprise Organization Master / Organization Sync as Mode B enterprise integration SHALL remain Out of Scope for this Constitution (see §11). |
| **Rationale** | Mode B CLOSED; BO OOS list. |
| **Source Artifact(s)** | DL-046; DL-066; DL-013/014 conditions |
| **Decision ID(s)** | DL-046; DL-066 |

---

# 8 Persona Constitution

## BC-8.1 — Closed set

| Field | Content |
|---|---|
| **Clause ID** | BC-8.1 |
| **Requirement** | The operational persona closed set SHALL be: **Complaint Officer**, **Supervisor**, **Manager**. Adding or splitting personas SHALL require a governed persona revision. |
| **Rationale** | Approved merge to three personas. |
| **Source Artifact(s)** | DL-001; DL-068 |
| **Decision ID(s)** | DL-001; DL-068 |

## BC-8.2 — Complaint Officer

| Field | Content |
|---|---|
| **Clause ID** | BC-8.2 |
| **Requirement** | Complaint Officer SHALL be the single operational persona combining former Front Office/Customer Service and Resolver/Handler responsibilities, with situational modes **intake** and **active handling**. Assignment and closure authority SHALL remain Supervisor R/A by default; any assign/close capability for Complaint Officer SHALL be conditional on Authorization permission. |
| **Rationale** | Merge decision without elevating authority. |
| **Source Artifact(s)** | DL-001 |
| **Decision ID(s)** | DL-001 |

## BC-8.3 — Supervisor

| Field | Content |
|---|---|
| **Clause ID** | BC-8.3 |
| **Requirement** | Supervisor SHALL retain R/A for `ASSIGNED` and `CLOSED` (as stated in the merge decision). Mode A Resolve path SHALL require Supervisor Approval before Case `CLOSED` (`IN_PROGRESS → RESOLVED →` Supervisor Approval `→ CLOSED`). |
| **Rationale** | Authority retention + Mode A closure path. |
| **Source Artifact(s)** | DL-001; DL-024 (BQ-008) |
| **Decision ID(s)** | DL-001; DL-024 |

## BC-8.4 — Manager

| Field | Content |
|---|---|
| **Clause ID** | BC-8.4 |
| **Requirement** | Manager SHALL be a valid Business Persona. Manager Workspace/Dashboard implementation MAY be deferred. Existence of the Manager persona SHALL NOT depend on UI readiness. |
| **Rationale** | Business Owner persona disposition. |
| **Source Artifact(s)** | DL-068; DL-062 (delivery deferral context) |
| **Decision ID(s)** | DL-068 |

## BC-8.5 — Administrator

| Field | Content |
|---|---|
| **Clause ID** | BC-8.5 |
| **Requirement** | Administrator SHALL remain outside the operational closed set and SHALL act as configuration persona. Authorization overrides (BR-CP-02 class) SHALL be restricted to Administrator with recorded justification and audit trail. |
| **Rationale** | Persona boundary + override control. |
| **Source Artifact(s)** | DL-001; DL-064 |
| **Decision ID(s)** | DL-001; DL-064 |

## BC-8.6

| Field | Content |
|---|---|
| **Clause ID** | BC-8.6 |
| **Requirement** | This Constitution SHALL NOT specify screens, navigation layouts, or wireframes for any persona. |
| **Rationale** | No UI specification in BC. |
| **Source Artifact(s)** | GC-000; milestone constraints |
| **Decision ID(s)** | GC-000 |

---

# 9 Complaint Lifecycle Constitution

## BC-9.1 — Dual lifecycle definitions

| Field | Content |
|---|---|
| **Clause ID** | BC-9.1 |
| **Requirement** | Two Case state-machine definitions SHALL coexist explicitly: **Definition A** (DOM-ECMF-003): `REGISTERED → ASSIGNED → IN_PROGRESS → PENDING_REVIEW → CLOSED → REOPENED`; **Definition B** (BR-CM-CAT): `CREATED → ASSIGNED → IN_PROGRESS → PENDING/ESCALATED → RESOLVED → CLOSED` with `CANCELLED` before final resolution. Each SHALL apply only within its declared SoT. Silent overwrite of one definition by the other SHALL NOT occur. |
| **Rationale** | Approved dual SoT Option O3. |
| **Source Artifact(s)** | DL-023; DL-044 |
| **Decision ID(s)** | DL-023; DL-044 |

## BC-9.2 — Entry

| Field | Content |
|---|---|
| **Clause ID** | BC-9.2 |
| **Requirement** | Complaint intake SHALL allow registration without creating a Case at registration time. Timing of the mandatory first Case SHALL follow BC-5.4. |
| **Rationale** | BQ-011 / BQ-002. |
| **Source Artifact(s)** | DL-024 |
| **Decision ID(s)** | DL-024 |

## BC-9.3 — Multi-source entry

| Field | Content |
|---|---|
| **Clause ID** | BC-9.3 |
| **Requirement** | Complaint sources SHALL include at least `CUSTOMER`, `BRANCH`, `HEAD_OFFICE`, and `SYSTEM` under the single aggregate model. |
| **Rationale** | Multi-source decision. |
| **Source Artifact(s)** | DL-006 |
| **Decision ID(s)** | DL-006 |

## BC-9.4 — Ownership & Assignment

| Field | Content |
|---|---|
| **Clause ID** | BC-9.4 |
| **Requirement** | Mode A Assignment SHALL be at Unit level only (BC-4.7). Default maximum Cases per Complaint SHALL be five; override policy beyond that SHALL be outside Mode A. |
| **Rationale** | BQ-003 / BQ-006. |
| **Source Artifact(s)** | DL-024 |
| **Decision ID(s)** | DL-024 |

## BC-9.5 — Escalation

| Field | Content |
|---|---|
| **Clause ID** | BC-9.5 |
| **Requirement** | Escalation along Branch ↔ Head Office SHALL be an official lifecycle capability (BC-5.9). Aggregate states `PENDING`/`ESCALATED` SHALL remain defined but SHALL NOT be exposed in Mode A delivery surface per BQ-009. |
| **Rationale** | Scope + Mode A exposure rule. |
| **Source Artifact(s)** | DL-066; DL-024 (BQ-009) |
| **Decision ID(s)** | DL-066; DL-024 |

## BC-9.6 — Appointment within lifecycle

| Field | Content |
|---|---|
| **Clause ID** | BC-9.6 |
| **Requirement** | Appointment capabilities authorized by the approved DEC-007…011 chain (booking, check-in, completion, no-show, and related Final Resolution bounds) SHALL be treated as Mode A lifecycle capabilities under DL-066. Calendar View, Slot Generator, Work Order, and appointment-related notification/auto-close SHALL remain Out of Scope until a new Decision Record. |
| **Rationale** | Cumulative appointment scope without importing API HOW. |
| **Source Artifact(s)** | DL-066; DL-007; DL-008; DL-009; DL-010; DL-011 |
| **Decision ID(s)** | DL-066 (normative consolidation); DL-007…011 (authorized bounds) |

## BC-9.7 — Resolution

| Field | Content |
|---|---|
| **Clause ID** | BC-9.7 |
| **Requirement** | Mode A Resolve SHALL require a Comment; Attachment MAY be optional; Complaint Attachments MAY be reused. Mode A path SHALL follow BC-8.3. |
| **Rationale** | BQ-010 / BQ-008. |
| **Source Artifact(s)** | DL-024 |
| **Decision ID(s)** | DL-024 |

## BC-9.8 — Closure & Cancel

| Field | Content |
|---|---|
| **Clause ID** | BC-9.8 |
| **Requirement** | Case closure SHALL obey BC-5.5. `CANCELLED` SHALL be included in Mode A with reasons including Duplicate, Wrong Input, and Customer Cancellation. |
| **Rationale** | BQ-007 / BQ-014. |
| **Source Artifact(s)** | DL-024 |
| **Decision ID(s)** | DL-024 |

## BC-9.9 — Case numbering

| Field | Content |
|---|---|
| **Clause ID** | BC-9.9 |
| **Requirement** | Case Number SHALL be independent of Complaint Number and SHALL use format `CASE-YYYY-NNNNNN`. |
| **Rationale** | BQ-004. |
| **Source Artifact(s)** | DL-024 |
| **Decision ID(s)** | DL-024 |

## BC-9.10 — SLA binding in lifecycle

| Field | Content |
|---|---|
| **Clause ID** | BC-9.10 |
| **Requirement** | Each Case SHALL bind an SLA Policy Version. Countdown SHALL NOT be activated in Mode A (**bind-without-clock**), subject to the single SLA Constitution (BC-5.3) for business meaning and Timeline recording. |
| **Rationale** | BQ-005 + DL-067. |
| **Source Artifact(s)** | DL-024; DL-067 |
| **Decision ID(s)** | DL-024; DL-067 |

---

# 10 Governance Rules

## BC-10.1 — Decision hierarchy

| Field | Content |
|---|---|
| **Clause ID** | BC-10.1 |
| **Requirement** | Conflict order SHALL be: Board Resolution → ADR → EA Documents → ECMP-CONSTITUTION-001 → BC-000 → Business Principles (when issued) → Business Rules → lower artefacts. |
| **Rationale** | Locked subordination. |
| **Source Artifact(s)** | DL-046; BC-3.1 |
| **Decision ID(s)** | DL-046 |

## BC-10.2 — Traceability

| Field | Content |
|---|---|
| **Clause ID** | BC-10.2 |
| **Requirement** | Every BC clause SHALL cite Source Artifact(s) and Decision ID(s). Amendments to BC-000 SHALL cite the authorizing Decision Record. |
| **Rationale** | Constitutional hygiene. |
| **Source Artifact(s)** | GC-000; milestone requirements |
| **Decision ID(s)** | GC-000 |

## BC-10.3 — Document precedence among Phase 0 packs

| Field | Content |
|---|---|
| **Clause ID** | BC-10.3 |
| **Requirement** | For reconstructing *why* a clause exists, readers SHOULD consult DL-000 and GC-000. For *what* is normative under Mode A business governance, BC-000 SHALL prevail over BO-000/BO-WS-000 workshop text once issued, provided BC-000 remains faithful to those approved decisions. |
| **Rationale** | Workshop packs prepare decisions; Constitution states them. |
| **Source Artifact(s)** | GC-000; BO-000 |
| **Decision ID(s)** | GC-000 |

## BC-10.4 — Change control

| Field | Content |
|---|---|
| **Clause ID** | BC-10.4 |
| **Requirement** | Changes to constitutional content SHALL be Category A (Constitution) under GOV-001 and SHALL be rare. Expanding Out-of-Scope items into scope SHALL require a new Decision Record and Governance Review. |
| **Rationale** | GOV-001 + BO OOS notes. |
| **Source Artifact(s)** | DL-047; DL-066; GC-000 |
| **Decision ID(s)** | DL-047; DL-066 |

## BC-10.5 — Ownership of configuration and authorization

| Field | Content |
|---|---|
| **Clause ID** | BC-10.5 |
| **Requirement** | Workflow transition definitions SHALL be owned by Administration; ECMF SHALL enforce active configuration and reject invalid transitions. Role-Permission SoT SHALL be Core Platform; Administration SHALL configure through Core Platform APIs without holding an authoritative duplicate. |
| **Rationale** | ADR-008 ownership split. |
| **Source Artifact(s)** | DL-025; DL-056 |
| **Decision ID(s)** | DL-025; DL-056 |

## BC-10.6 — Baseline business SoT

| Field | Content |
|---|---|
| **Clause ID** | BC-10.6 |
| **Requirement** | The historical business baseline SoT remains Blueprint v2.1 + FRD-001 (DL-002). Normative Mode A scope carve-outs for Escalation and Appointment SHALL be read from **DL-066**, not from the superseded OOS sentences of DEC-001 alone. |
| **Rationale** | Prevents wrong scope citation. |
| **Source Artifact(s)** | DL-002; DL-066; GC-000 |
| **Decision ID(s)** | DL-002; DL-066 |

---

# 11 Out of Scope

The following SHALL remain outside this Constitution’s Mode A obligations until a new Decision Record and Governance Review authorize inclusion. This section lists exclusions; it does not redefine them.

| # | Excluded capability | Source |
|---|---|---|
| 1 | Mode B coding / production Enterprise SSO, Identity Adapter runtime, portal embed, enterprise `securitySchemes` | DL-046; Board C-7 / C-B6-1 |
| 2 | Regional Office on complaint escalation path | DL-066 |
| 3 | Work Order | DL-066; DL-002 historical OOS |
| 4 | Calendar View / Slot Generator / Schedule Slot / Scheduling systems | DL-066; DL-007…011 bounds |
| 5 | Enterprise Integration (as product Mode B) | DL-066; DL-046 |
| 6 | Enterprise Organization Master / Org Sync engine as Mode B product | DL-013/014 conditions; DL-066 |
| 7 | Customer Master write-back except explicitly authorized integration | DL-031 |
| 8 | Assigned User assignment (individual) in Mode A | DL-024 BQ-006 |
| 9 | Override policy for >5 Cases per Complaint (outside Mode A) | DL-024 BQ-003 |
| 10 | Working-day SLA calendar; Pause/Resume SLA; per-case-type SLA differentiation | DL-019 DEFERRED |
| 11 | Read-audit | DL-063 deferred |
| 12 | Manager/Executive dashboard delivery (v0.1 Supervisor-only) | DL-062; DL-068 (persona ≠ delivery) |
| 13 | Force-merge / retire dual-SoT without Retirement DEC | DL-044; DL-046 |
| 14 | UX Foundation package content as Approved baseline (status Draft pending Review) | DL-069; M-11 |

---

# Appendix A — Normative References

| ID | Artifact |
|---|---|
| DL-000 | `docs/governance/DL-000-Decision-Log.md` (v1.1) |
| DRR-000 | `docs/governance/DRR-000-Decision-Readiness-Review.md` |
| BO-000 | `docs/governance/BO-000-Business-Owner-Resolution-Pack.md` |
| BO-WS-000 | `docs/governance/BO-WS-000-P1-Business-Owner-Workshop.md` |
| GC-000 | `docs/governance/GC-000-Governance-Closure-BC-Readiness.md` |
| ECMP-CONSTITUTION-001 | `18 Architecture Governance/ECMP_CONSTITUTION_001_…` / portal mirror |
| GOV-001 | Delivery governance categories (via DL-047) |
| CWX-000 | Case Workspace Experience Constitution (via DL-027) |

Primary decision IDs consumed: **DL-001, DL-002, DL-003, DL-004, DL-005, DL-006, DL-007…011 (bounds), DL-019, DL-023, DL-024, DL-025, DL-026, DL-027, DL-031, DL-046, DL-047, DL-056, DL-062 (context), DL-063, DL-064, DL-065, DL-066, DL-067, DL-068, DL-069 (hygiene note), DL-044 (dual-SoT prohibition).**

---

# Appendix B — Complete Traceability Matrix

| BC Clause | Originating Decision ID(s) | Originating Artifact(s) |
|---|---|---|
| BC-1.1 | DL-046; GC-000 | ECMP-CONSTITUTION-001; GC-000 |
| BC-1.2 | GC-000 | GC-000 |
| BC-1.3 | DL-046 | ECMP-CONSTITUTION-001 |
| BC-1.4 | DL-046 | ECMP-CONSTITUTION-001 |
| BC-2.1 | DL-046 | ECMP-CONSTITUTION-001 |
| BC-2.2 | DL-066…068; DL-001; DL-023; DL-024; DL-019; DL-025; DL-026; DL-031; DL-056; DL-063…065 | DL-000; GC-000 |
| BC-2.3 | DL-066 | DL-066; GC-000 |
| BC-3.1 | DL-003; DL-047; GC-000 | DL-000; GC-000 |
| BC-3.2 | DL-047 | GOV-001 |
| BC-3.3 | DL-003 | DEC-003 |
| BC-3.4 | DL-023; DL-044; DL-046; DL-027 | DL-000 |
| BC-4.1 | DL-006 | DEC-018 |
| BC-4.2 | DL-023; DL-024; DL-046 | DL-000 |
| BC-4.3 | DL-067 | BO-002 / DL-067 |
| BC-4.4 | DL-067 | DL-067 |
| BC-4.5 | DL-066 | DL-066 |
| BC-4.6 | DL-001; DL-068 | DL-000 |
| BC-4.7 | DL-024 | BQ-006 |
| BC-4.8 | DL-066 | DL-066 |
| BC-4.9 | DL-024; DL-067; DL-019 | BQ-005; BO-002 |
| BC-4.10 | DL-025; DL-056 | ADR-008 |
| BC-4.11 | — RESERVED | Gap acknowledged |
| BC-4.12 | — RESERVED | Gap acknowledged |
| BC-5.1 | DL-046 | ECMP-CONSTITUTION-001 |
| BC-5.2 | DL-031 | ADR-002 |
| BC-5.3 | DL-067 | BO-002 |
| BC-5.4 | DL-024 | BQ-002 |
| BC-5.5 | DL-024 | BQ-007 |
| BC-5.6 | DL-026; DL-064 | ADR-003 |
| BC-5.7 | DL-063 | OQ-007 resolution |
| BC-5.8 | DL-066 | BO-005 |
| BC-5.9 | DL-066 | BO-001 |
| BC-5.10 | DL-027 | CWX-000 |
| BC-6.1 | DL-067 | DL-067 |
| BC-6.2 | DL-064; DL-026 | ADR-003; DEC-004 |
| BC-6.3 | DL-065 | ADR-008 §3 |
| BC-6.4 | DL-067; GC-000 | GC-000 |
| BC-6.5 | DL-019; DL-004 | CAP-006 BQ; DEC-004 |
| BC-6.6 | DL-005; DL-004 | DEC-005; DEC-004 |
| BC-7.1 | DL-066 | DL-066 |
| BC-7.2 | DL-006 | DEC-018 |
| BC-7.3 | DL-066; DL-012 | DRR/GC |
| BC-7.4 | DL-046; DL-066 | DL-000 |
| BC-8.1–8.5 | DL-001; DL-068; DL-024; DL-064 | DL-000 |
| BC-8.6 | GC-000 | GC-000 |
| BC-9.1 | DL-023; DL-044 | DEC-BQ001; DEC-020 |
| BC-9.2–9.4 | DL-024; DL-006 | Mode A BQ pack; DEC-018 |
| BC-9.5 | DL-066; DL-024 | DL-000 |
| BC-9.6 | DL-066; DL-007…011 | DL-000 |
| BC-9.7–9.10 | DL-024; DL-067 | DL-000 |
| BC-10.1–10.6 | DL-046; DL-047; DL-025; DL-056; DL-002; DL-066; GC-000 | DL-000; GC-000 |
| §11 | DL-066; DL-046; DL-024; DL-019; DL-063; DL-062; DL-044; DL-069 | GC-000 |

---

# Appendix C — Glossary References

| Term | See |
|---|---|
| Complaint | BC-4.1 |
| Case / Ticket | BC-4.2 |
| Timeline / Event | BC-4.3; BC-4.4 |
| Organization / Branch / Head Office | BC-4.5; BC-7.1 |
| Persona | BC-4.6; §8 |
| Assignment | BC-4.7 |
| Escalation | BC-4.8; BC-9.5 |
| Snapshot (SLA bind) | BC-4.9 |
| Owner (SoT) | BC-4.10 |
| Receiving Organization | BC-4.11 RESERVED |
| Current Owning Organization | BC-4.12 RESERVED |
| Mode A / Mode B | BC-2.1; §11 |
| Dual SoT | BC-3.4; BC-9.1 |
| SLA Constitution | BC-5.3 |

---

# Appendix D — Validation Report

| Check | Result | Notes |
|---|---|---|
| No new business decisions invented | **PASS** | RESERVED used where DL lacked terms |
| No repository contradictions introduced | **PASS** | Dual SoT & bind-without-clock stated explicitly; F4 not over-promoted |
| Every normative clause has traceability | **PASS** | Appendix B |
| No implementation guidance | **PASS** | BC-6.4 excludes schemas/APIs/DB |
| No UI specification | **PASS** | BC-8.6 |
| No database specification | **PASS** | — |
| No API specification | **PASS** | Appointment bounds without endpoint IDs as requirements |
| No source code discussion | **PASS** | — |
| Prompt example “exactly one Ticket” excluded | **PASS** | Contradicts DL-024 BQ-002 |
| Mode B excluded from obligations | **PASS** | §11 |
| Governance history unmodified | **PASS** | Only BC-000 created |

**Gaps acknowledged (not filled):** BC-4.11, BC-4.12; DEC-F4 detailed visibility (pending formal); Business Principles document not created (hierarchy placeholder only).

---

# Appendix E — Constitution Coverage Matrix

| Approved decision (BC-eligible / P1) | Represented in BC-000? | Where |
|---|---|---|
| DL-001 Personas merge | YES | §4, §8 |
| DL-002 Baseline (+ read via DL-066) | YES | BC-10.6 |
| DL-003 BR-0xx | YES | BC-3.3 |
| DL-004 BR defaults / 24×7 | YES | BC-6.5; BC-6.6 |
| DL-005 SLA/NFR targets as reference | YES | BC-6.6 |
| DL-006 Multi-source/target | YES | BC-4.1; BC-9.3; BC-7.2 |
| DL-007…011 Appointment bounds | YES (via DL-066) | BC-9.6; §11 |
| DL-019 CAP-006 business closure | YES | BC-6.5; BC-4.9 |
| DL-023 Dual CSM | YES | BC-9.1 |
| DL-024 Mode A Case baseline | YES | §5, §9 |
| DL-025 Workflow Config SoT | YES | BC-10.5 |
| DL-026 Configuration-First | YES | BC-5.6 |
| DL-027 CWX Golden Rules | YES | BC-5.10 |
| DL-031 Not customer SoR | YES | BC-5.2 |
| DL-044 Dual SoT no force-merge | YES | BC-3.4 |
| DL-046 Module constitution / Mode A | YES | §1, §2, §10, §11 |
| DL-047 GOV-001 | YES | BC-3.2; BC-10.4 |
| DL-056 Role-Permission SoT | YES | BC-10.5 |
| DL-063 Write-audit | YES | BC-5.7 |
| DL-064 Immutable audit + override | YES | BC-6.2 |
| DL-065 Config audit | YES | BC-6.3 |
| DL-066 Scope Consolidation | YES | §2, §5, §7, §9, §11 |
| DL-067 SLA Constitution | YES | BC-5.3; §6 |
| DL-068 Manager persona | YES | BC-8.4 |
| DL-069 UX status sync | YES (note only) | §11 item 14 |
| DL-012 DEC-F4 formal | **NOT elevated** | BC-7.3 explains PENDING |
| Mode B ADR chain | **Excluded** | §11 |

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-05 | Initial Mode A Business Constitution from Phase 0 approved decisions |

---

*End of BC-000.*
