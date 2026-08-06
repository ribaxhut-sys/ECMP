# BC-001 — ECMP Business Principles

| Field | Value |
|---|---|
| Document ID | BC-001 |
| Title | ECMP Business Principles — Mode A Baseline |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | **NORMATIVE GUIDANCE — Mode A Baseline** |
| Milestone | Governance Phase 1 |
| Authority | Derived exclusively from **BC-000**; secondary reference to Phase 0 packs only |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → **BC-000** → **BC-001** → Business Rules → … |
| Applicability | **Mode A only** |
| Does not | Add constitutional requirements · invent Business Rules · specify UI/API/database/code · unlock Mode B · modify BC-000 |

---

# 1 Purpose

## 1.1 Role of Business Principles

BC-001 states the **guiding business principles** that interpret BC-000 into consistent business behaviour for Business, UX, Domain, Architecture, and Engineering teams.

Principles answer: *How should we think and decide when applying the Constitution?*  
They do **not** answer: *Which screen, endpoint, table, or class implements it?*

## 1.2 Relationship with BC-000

| Rule | Statement |
|---|---|
| Derivation | Every principle in BC-001 SHALL be derivable from one or more BC-000 clauses. |
| No new constitution | BC-001 SHALL NOT introduce new constitutional requirements. |
| Conflict | If BC-001 and BC-000 appear to differ, **BC-000 SHALL prevail**. |
| Downstream | Business Rules, Workflow, UX, and Implementation SHALL NOT contradict BC-001 without a governed Decision Record that also amends or clarifies BC-000 as required. |

## 1.3 Audience

Teams SHALL use BC-001 as primary **design guidance** for Mode A business behaviour without needing to read implementation artefacts. Constitutional obligations remain in BC-000.

---

# 2 Principle Hierarchy

```
Board Resolution / ADR / EA Documents / ECMP-CONSTITUTION-001
        ↓
Business Constitution (BC-000)     ← WHAT SHALL govern
        ↓
Business Principles (BC-001)       ← HOW to interpret & apply (this document)
        ↓
Business Rules (BR-0xx)
        ↓
Workflow / Domain specifications
        ↓
UX contracts (approved)
        ↓
Architecture
        ↓
Implementation
```

A lower layer SHALL NOT contradict a higher layer without a governed Decision Record (BC-000 BC-3.1).

---

# 3 Principles

---

## BP-001 — Business Before Technology

| Field | Content |
|---|---|
| **Principle ID** | BP-001 |
| **Name** | Business Before Technology |
| **Statement** | Business meaning and domain behaviour SHALL be decided and preserved before technology choices. Technology SHALL serve the Complaint Management Module; it SHALL NOT redefine the complaint business domain. |
| **Business Intent** | Keep the complaint domain stable so that future Enterprise integration changes mechanisms, not business meaning. |
| **Business Rationale** | The North Star and the Constitution’s separation of WHAT from HOW exist to stop delivery from inventing product scope through technical convenience. |
| **Implications** | Prefer clarifying BC-000 / BR before inventing features. Reject “platform”, “engine”, or “framework” expansions that are not constituted. Do not treat dual-SoT technical coexistence as permission to invent a third business model. |
| **Referenced Constitution Clause(s)** | BC-1.1; BC-1.4; BC-5.1; BC-5.10; BC-6.4; BC-8.6 |
| **Referenced Decision(s)** | DL-046; DL-027; GC-000 |

---

## BP-002 — Separation of Business and Implementation

| Field | Content |
|---|---|
| **Principle ID** | BP-002 |
| **Name** | Separation of Business and Implementation |
| **Statement** | Constitutional and principle-level statements SHALL define business obligations. Implementation detail (interfaces, storage, code structure) SHALL remain in subordinate artefacts and SHALL NOT be smuggled into business norms. |
| **Business Intent** | Allow multiple technical realisations without rewriting business truth. |
| **Business Rationale** | BC-000 explicitly forbids prescribing schemas, APIs, screens, or storage in the Constitution; principles inherit that discipline. |
| **Implications** | When documenting a rule, state the business obligation first. Put technical realisation in specification/implementation layers. Do not cite code paths as business authority. |
| **Referenced Constitution Clause(s)** | BC-1.1; BC-6.4; BC-8.6; BC-3.1 |
| **Referenced Decision(s)** | DL-046; DL-047; GC-000 |

---

## BP-003 — Decision Traceability

| Field | Content |
|---|---|
| **Principle ID** | BP-003 |
| **Name** | Decision Traceability |
| **Statement** | Every business-normative claim used in design or delivery SHALL be traceable to BC-000 and, through BC-000, to approved Decision ID(s). Untestable or untraceable “business needs” SHALL NOT be treated as binding. |
| **Business Intent** | Prevent silent invention of obligations. |
| **Business Rationale** | Phase 0 closed Priority-1 gaps precisely so BC-000 could be written without invention; principles must preserve that discipline. |
| **Implications** | New obligations require a Decision Record. RESERVED terms in BC-000 SHALL NOT be used as if defined. Workshop anecdotes without Decision IDs are non-binding. |
| **Referenced Constitution Clause(s)** | BC-1.2; BC-10.2; BC-4.11; BC-4.12 |
| **Referenced Decision(s)** | GC-000; DL-000 methodology |

---

## BP-004 — Governance Before Design

| Field | Content |
|---|---|
| **Principle ID** | BP-004 |
| **Name** | Governance Before Design |
| **Statement** | Design and delivery SHALL follow governed categories (Constitution → Specification → Implementation). Spontaneous redesigns, new engines, or out-of-scope capabilities SHALL NOT proceed without the required Board/ADR/Decision authority. |
| **Business Intent** | Stop mixing permanent rules, specifications, and build work in one leap. |
| **Business Rationale** | GOV-001 classification is constitutionalised in BC-000 to keep change control rare and auditable for Category A. |
| **Implications** | Classify work as A/B/C before designing. Do not “just build” Mode B or OOS items. Expanding §11 Out of Scope requires Decision Record + Governance Review. |
| **Referenced Constitution Clause(s)** | BC-3.2; BC-10.4; BC-2.3; BC-1.3 |
| **Referenced Decision(s)** | DL-047; DL-066; DL-046 |

---

## BP-005 — Single Complaint Lifecycle

| Field | Content |
|---|---|
| **Principle ID** | BP-005 |
| **Name** | Single Complaint Lifecycle |
| **Statement** | Complaint handling SHALL be understood as one Complaint Lifecycle. Appointment and Head Office Escalation SHALL participate in that lifecycle; they SHALL NOT invent a parallel product lifecycle. |
| **Business Intent** | One business journey for complaint work, even when multiple capabilities apply. |
| **Business Rationale** | Business Owner Scope Consolidation placed Escalation and Appointment inside the same lifecycle deliberately. |
| **Implications** | Do not design Appointment as a standalone product. Do not treat Escalation as a separate application. Case work remains under the Complaint aggregate rules in BC-000. |
| **Referenced Constitution Clause(s)** | BC-5.8; BC-5.9; BC-4.1; BC-9.5; BC-9.6; BC-2.2 |
| **Referenced Decision(s)** | DL-066; DL-006 |

---

## BP-006 — Timeline First

| Field | Content |
|---|---|
| **Principle ID** | BP-006 |
| **Name** | Timeline First |
| **Statement** | Business-significant changes, including SLA-related changes, SHALL be reflected on the Timeline. Teams SHALL treat the Timeline as the business memory of what happened—not as an optional log. |
| **Business Intent** | Make complaint history reconstructable for operations, accountability, and service commitments. |
| **Business Rationale** | The single SLA Constitution requires Timeline Events for SLA changes; write-audit and immutable audit reinforce chronological accountability. |
| **Implications** | When defining a business change, ask what Timeline Event(s) it produces. Do not design silent SLA mutations. Do not confuse Timeline obligations with UI history widgets. |
| **Referenced Constitution Clause(s)** | BC-5.3; BC-4.3; BC-4.4; BC-6.1; BC-5.7 |
| **Referenced Decision(s)** | DL-067; DL-063 |

---

## BP-007 — Immutable Business Evidence

| Field | Content |
|---|---|
| **Principle ID** | BP-007 |
| **Name** | Immutable Business Evidence |
| **Statement** | Governed write evidence and audit trails SHALL be immutable. Integrity rules classified as Hardcoded SHALL NOT be turned off by configuration. Overrides SHALL be exceptional, justified, and audited. |
| **Business Intent** | Protect trust in the complaint record and in critical controls. |
| **Business Rationale** | BC-000 hardens immutable audit and separates Configuration rules from Hardcoded integrity rules. |
| **Implications** | Do not propose “admin switches” that disable audit or mandatory authentication. Overrides remain Administrator-only with justification. Configuration changes to roles/workflow remain auditable. |
| **Referenced Constitution Clause(s)** | BC-6.2; BC-6.3; BC-5.6; BC-5.7; BC-8.5 |
| **Referenced Decision(s)** | DL-064; DL-065; DL-026; DL-063 |

---

## BP-008 — Controlled Escalation

| Field | Content |
|---|---|
| **Principle ID** | BP-008 |
| **Name** | Controlled Escalation |
| **Statement** | Escalation SHALL be an official lifecycle capability limited to **Branch ↔ Head Office**. Regional paths and enterprise-wide escalation models SHALL NOT be assumed. |
| **Business Intent** | Enable Head Office handling without reopening rejected discovery scope (Regional, Work Order, Calendar). |
| **Business Rationale** | DL-066 / BC-000 Scope Consolidation closed the escalation OOS gap with an explicit narrow path. |
| **Implications** | Design escalation only on the constituted path. Do not introduce Regional nodes. Do not elevate PENDING DEC-F4 detail to principle-level force until formalised (BC-7.3). |
| **Referenced Constitution Clause(s)** | BC-5.9; BC-4.8; BC-7.1; BC-7.3; BC-9.5; §11 |
| **Referenced Decision(s)** | DL-066 |

---

## BP-009 — Organization-Aware Operations

| Field | Content |
|---|---|
| **Principle ID** | BP-009 |
| **Name** | Organization-Aware Operations |
| **Statement** | Complaint operations SHALL respect constituted organisation units (Branch and Head Office for escalation/targeting). ECMP SHALL NOT behave as Enterprise Organization Master under Mode A principles. |
| **Business Intent** | Keep organisational meaning clear without claiming enterprise org ownership. |
| **Business Rationale** | Multi-target complaints and Branch↔HO escalation are constituted; enterprise org sync remains Out of Scope. |
| **Implications** | Use Branch/Head Office vocabulary from BC-000. Do not invent Receiving/Current Owning Organization semantics (RESERVED). Do not build Mode B org-sync product behaviour under Mode A guise. |
| **Referenced Constitution Clause(s)** | BC-4.5; BC-7.1; BC-7.2; BC-7.4; BC-4.11; BC-4.12; §11 |
| **Referenced Decision(s)** | DL-066; DL-006; DL-046 |

---

## BP-010 — One SLA Constitution

| Field | Content |
|---|---|
| **Principle ID** | BP-010 |
| **Name** | One SLA Constitution |
| **Statement** | Service-time commitments SHALL be read through a single SLA Constitution for the Complaint Lifecycle: uniform business rules, Timeline recording of SLA changes, and Mode A bind-without-clock for Case policy binding—without treating deferred CAP-006 runtime items as active obligations. |
| **Business Intent** | End conflicting “business readings” of SLA while keeping deferred items deferred. |
| **Business Rationale** | Business Owner approved one SLA Constitution; BC-000 also locks 24×7 baseline and defers working-day/pause/case-type differentiation. |
| **Implications** | Do not invent a second business SLA meaning per technical namespace. Do not activate deferred SLA behaviours without DEC. Treat numeric baselines as revisable references. |
| **Referenced Constitution Clause(s)** | BC-5.3; BC-4.9; BC-9.10; BC-6.5; BC-6.6 |
| **Referenced Decision(s)** | DL-067; DL-024; DL-019; DL-005 |

---

## BP-011 — Explicit Duality Without Silent Merge

| Field | Content |
|---|---|
| **Principle ID** | BP-011 |
| **Name** | Explicit Duality Without Silent Merge |
| **Statement** | Where BC-000 recognises dual Case state definitions / dual SoT, teams SHALL name the applicable definition explicitly. Silent overwrite, force-merge, or “pick one quietly” SHALL NOT occur. |
| **Business Intent** | Prevent false unity that corrupts lifecycle meaning. |
| **Business Rationale** | Dual SoT was an approved decision, not an accident; retirement requires a Retirement DEC. |
| **Implications** | Always state which definition/SoT a design applies to. Do not “simplify” by deleting the other definition in documents or behaviour without governance. |
| **Referenced Constitution Clause(s)** | BC-3.4; BC-9.1 |
| **Referenced Decision(s)** | DL-023; DL-044; DL-046 |

---

## BP-012 — Honest Persona Capability

| Field | Content |
|---|---|
| **Principle ID** | BP-012 |
| **Name** | Honest Persona Capability |
| **Statement** | Operational personas SHALL remain the closed set Complaint Officer, Supervisor, and Manager. Manager SHALL remain a valid Business Persona even when Manager Workspace delivery is deferred. Persona existence SHALL NOT be treated as a promise of immediate UI capability. |
| **Business Intent** | Keep actor model stable without over-promising delivery surfaces. |
| **Business Rationale** | Business Owner separated persona validity from workspace readiness. |
| **Implications** | Do not remove Manager from the closed set to “match v0.1 dashboard”. Do not imply Manager dashboard is constituted as delivered. Supervisor retains default assign/close authority patterns in BC-000. |
| **Referenced Constitution Clause(s)** | BC-8.1; BC-8.2; BC-8.3; BC-8.4; BC-4.6 |
| **Referenced Decision(s)** | DL-001; DL-068; DL-062 |

---

## BP-013 — Scope Discipline

| Field | Content |
|---|---|
| **Principle ID** | BP-013 |
| **Name** | Scope Discipline |
| **Statement** | Capabilities listed as Out of Scope in BC-000 SHALL be treated as non-obligations for Mode A. Desire, lab experiments, or adjacent enterprise ideas SHALL NOT promote them into principles or implied scope. |
| **Business Intent** | Protect Mode A completion and prevent scope creep. |
| **Business Rationale** | Business Owner and Constitution explicitly fence Mode B, Regional, Work Order, Calendar/Scheduling, and Enterprise Integration. |
| **Implications** | Label OOS work clearly. Require Decision Record + Governance Review before any OOS→in-scope move. Do not hide OOS features inside “helpful” Mode A designs. |
| **Referenced Constitution Clause(s)** | BC-2.3; BC-2.1; §11 |
| **Referenced Decision(s)** | DL-066; DL-046; GC-000 |

---

## BP-014 — Case Independence from Complaint Closure

| Field | Content |
|---|---|
| **Principle ID** | BP-014 |
| **Name** | Case Independence from Complaint Closure |
| **Statement** | Closing a Case SHALL NOT automatically close the Complaint Aggregate. Complaint-level and Case-level outcomes SHALL be reasoned separately unless a constituted rule says otherwise. |
| **Business Intent** | Preserve multi-Case Complaints and avoid accidental total closure. |
| **Business Rationale** | Mode A baseline explicitly forbids auto-closing the aggregate when a Case closes. |
| **Implications** | Designs and rules must not assume one Case closure ends the Complaint. Reporting language must distinguish Case closed vs Complaint closed. |
| **Referenced Constitution Clause(s)** | BC-5.5; BC-5.4; BC-9.8 |
| **Referenced Decision(s)** | DL-024 |

---

## BP-015 — Experience Serves Business Context

| Field | Content |
|---|---|
| **Principle ID** | BP-015 |
| **Name** | Experience Serves Business Context |
| **Statement** | Case Workspace experience SHALL follow CWX Golden Rules as business experience principles: business first, case as product, context before action, no duplicate context, progressive disclosure, context-aware experience, experience above implementation, no rewrite without decision, reference don’t redefine. Experience SHALL NOT redefine Business Rules or domain ownership. |
| **Business Intent** | Keep human work coherent with constituted lifecycle without letting UX reinvent the business. |
| **Business Rationale** | BC-000 elevates CWX Golden Rules as constitutional experience obligations without specifying screens. |
| **Implications** | UX proposals must cite business context needs. UX SHALL NOT silently merge dual-SoT. UX SHALL NOT invent OOS capabilities. Screen specs remain outside BC-001. |
| **Referenced Constitution Clause(s)** | BC-5.10; BC-8.6; BC-3.4 |
| **Referenced Decision(s)** | DL-027; DL-001 |

---

# 4 Principle Relationships

```
BP-001 Business Before Technology
    ├── supports → BP-002 Separation of Business and Implementation
    ├── supports → BP-004 Governance Before Design
    └── supports → BP-015 Experience Serves Business Context

BP-003 Decision Traceability
    ├── required by → all other BPs (no untraceable “principle inflation”)
    └── supports → BP-004 Governance Before Design

BP-005 Single Complaint Lifecycle
    ├── requires → BP-008 Controlled Escalation
    ├── requires → BP-009 Organization-Aware Operations
    └── aligns with → BP-014 Case Independence from Complaint Closure

BP-006 Timeline First
    ├── reinforced by → BP-007 Immutable Business Evidence
    └── aligns with → BP-010 One SLA Constitution

BP-011 Explicit Duality Without Silent Merge
    └── protects → BP-005 / BP-015 from false simplification

BP-012 Honest Persona Capability
    └── bounded by → BP-013 Scope Discipline (delivery ≠ constitution)

BP-013 Scope Discipline
    └── constrains → every principle’s application under Mode A
```

**Reading tip:** Start from BP-001 + BP-003 + BP-013 for any new initiative; then apply lifecycle (BP-005), time (BP-006/010), organisation (BP-008/009), and persona (BP-012) as relevant.

---

# 5 Principle-to-Constitution Matrix

| Principle | Primary BC Clause(s) | Primary Decision(s) |
|---|---|---|
| BP-001 Business Before Technology | BC-1.1; BC-1.4; BC-5.1; BC-5.10 | DL-046; DL-027 |
| BP-002 Separation of Business and Implementation | BC-1.1; BC-6.4; BC-8.6; BC-3.1 | DL-046; DL-047 |
| BP-003 Decision Traceability | BC-1.2; BC-10.2 | GC-000 |
| BP-004 Governance Before Design | BC-3.2; BC-10.4; BC-2.3 | DL-047; DL-066 |
| BP-005 Single Complaint Lifecycle | BC-5.8; BC-5.9; BC-9.5; BC-9.6 | DL-066 |
| BP-006 Timeline First | BC-5.3; BC-6.1; BC-4.3; BC-4.4 | DL-067 |
| BP-007 Immutable Business Evidence | BC-6.2; BC-5.6; BC-5.7 | DL-064; DL-026; DL-063 |
| BP-008 Controlled Escalation | BC-5.9; BC-7.1; BC-7.3 | DL-066 |
| BP-009 Organization-Aware Operations | BC-4.5; BC-7.2; BC-7.4 | DL-066; DL-006 |
| BP-010 One SLA Constitution | BC-5.3; BC-9.10; BC-6.5 | DL-067; DL-024; DL-019 |
| BP-011 Explicit Duality Without Silent Merge | BC-3.4; BC-9.1 | DL-023; DL-044 |
| BP-012 Honest Persona Capability | BC-8.1; BC-8.4 | DL-001; DL-068 |
| BP-013 Scope Discipline | BC-2.3; §11 | DL-066; DL-046 |
| BP-014 Case Independence from Complaint Closure | BC-5.5; BC-9.8 | DL-024 |
| BP-015 Experience Serves Business Context | BC-5.10; BC-8.6 | DL-027 |

---

# 6 Guidance

Guidance below directs **judgement**. It does **not** specify screens, APIs, databases, or code.

## 6.1 Business Design

- Start from BC-000 obligations, then select applicable principles (usually BP-001, BP-003, BP-013).
- Express new needs as candidate Business Rules (`BR-0xx`) only after confirming constitutional coverage.
- Treat Out of Scope lists as hard fences, not backlog suggestions.

## 6.2 UX

- Use BP-015 and BP-012 to shape experience intent without drawing screens in this document.
- Prefer context-before-action and no duplicate business context (CWX via BC-5.10).
- Do not imply Manager Workspace is delivered; do not drop Manager from the actor model.
- Do not silently unify dual-SoT experiences (BP-011).

## 6.3 Domain

- Keep one Complaint Lifecycle narrative (BP-005).
- Distinguish Case closure from Complaint closure (BP-014).
- Name which state-machine definition applies (BP-011).
- Keep Escalation on Branch ↔ Head Office only (BP-008).

## 6.4 Architecture

- Preserve separation of business norms from technical mechanisms (BP-002).
- Do not force-merge dual SoT (BP-011).
- Do not introduce Mode B integration architecture as Mode A principle fulfilment (BP-013).
- Honour SoT ownership distinctions constituted in BC-000 when shaping boundaries (without restating implementation).

## 6.5 Implementation

- Implement only after Specification readiness (BP-004).
- Ensure business-significant changes remain explainable on the Timeline (BP-006).
- Never disable Hardcoded integrity via configuration convenience (BP-007).
- Refuse undocumented “business requirements” that lack Decision/BC traceability (BP-003).

---

# Appendix A — Normative References

| ID | Artifact | Role |
|---|---|---|
| BC-000 | `docs/governance/BC-000-Business-Constitution.md` | **Primary** — sole source of principle derivation |
| DL-000 | `docs/governance/DL-000-Decision-Log.md` | Secondary — decision IDs cited via BC-000 |
| DRR-000 | `docs/governance/DRR-000-Decision-Readiness-Review.md` | Secondary |
| BO-000 / BO-WS-000 / GC-000 | `docs/governance/*` | Secondary — historical Phase 0 context |

If any secondary source differs from BC-000, **BC-000 prevails**.

---

# Appendix B — Traceability Matrix

| Principle | BC Clause(s) | Decision ID(s) |
|---|---|---|
| BP-001 | BC-1.1; BC-1.4; BC-5.1; BC-5.10; BC-6.4; BC-8.6 | DL-046; DL-027; GC-000 |
| BP-002 | BC-1.1; BC-6.4; BC-8.6; BC-3.1 | DL-046; DL-047; GC-000 |
| BP-003 | BC-1.2; BC-10.2; BC-4.11; BC-4.12 | GC-000 |
| BP-004 | BC-3.2; BC-10.4; BC-2.3; BC-1.3 | DL-047; DL-066; DL-046 |
| BP-005 | BC-5.8; BC-5.9; BC-4.1; BC-9.5; BC-9.6; BC-2.2 | DL-066; DL-006 |
| BP-006 | BC-5.3; BC-4.3; BC-4.4; BC-6.1; BC-5.7 | DL-067; DL-063 |
| BP-007 | BC-6.2; BC-6.3; BC-5.6; BC-5.7; BC-8.5 | DL-064; DL-065; DL-026; DL-063 |
| BP-008 | BC-5.9; BC-4.8; BC-7.1; BC-7.3; BC-9.5 | DL-066 |
| BP-009 | BC-4.5; BC-7.1; BC-7.2; BC-7.4; BC-4.11; BC-4.12 | DL-066; DL-006; DL-046 |
| BP-010 | BC-5.3; BC-4.9; BC-9.10; BC-6.5; BC-6.6 | DL-067; DL-024; DL-019; DL-005 |
| BP-011 | BC-3.4; BC-9.1 | DL-023; DL-044; DL-046 |
| BP-012 | BC-8.1; BC-8.2; BC-8.3; BC-8.4; BC-4.6 | DL-001; DL-068; DL-062 |
| BP-013 | BC-2.1; BC-2.3; §11 | DL-066; DL-046; GC-000 |
| BP-014 | BC-5.5; BC-5.4; BC-9.8 | DL-024 |
| BP-015 | BC-5.10; BC-8.6; BC-3.4 | DL-027; DL-001 |

---

# Appendix C — Validation Report

| Check | Result | Notes |
|---|---|---|
| No new business decisions introduced | **PASS** | Principles interpret BC-000 only |
| No contradiction with BC-000 | **PASS** | Dual SoT, bind-without-clock, OOS, RESERVED terms preserved |
| Every principle has constitutional references | **PASS** | §3 + Appendix B |
| Every principle has decision traceability | **PASS** | Via BC-000 cited Decision IDs |
| No UI / API / database / code guidance | **PASS** | §6 explicitly non-implementational |
| BC-000 unmodified | **PASS** | This milestone creates BC-001 only |
| Candidate “Complete Traceability” covered | **PASS** | as BP-003 |
| Candidate “Timeline First” covered | **PASS** | as BP-006 |
| Candidate “Immutable Business Events” covered | **PASS** | as BP-007 (evidence/events/audit) |
| No principle invented for RESERVED org terms | **PASS** | BP-009 forbids using RESERVED terms as defined |

**Not promoted to principles (unsupported as new meaning):** any Regional escalation model; Mode B integration behaviours; Receiving/Current Owning Organization semantics; “exactly one Ticket at registration”.

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-05 | Initial Mode A Business Principles derived from BC-000 |

---

*End of BC-001.*
