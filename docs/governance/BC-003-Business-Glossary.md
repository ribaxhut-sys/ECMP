# BC-003 — Business Glossary

| Field | Value |
|---|---|
| Document ID | BC-003 |
| Title | ECMP Business Glossary — Mode A Baseline |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | **NORMATIVE VOCABULARY — Mode A Baseline** |
| Milestone | Governance Phase 1 |
| Authority | Derived from **BC-000**, **BC-001**, **BW-000** only (secondary: DL-000, GC-000 via those artefacts) |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → BC-000 → BC-001 → BW-000 → **BC-003** → Business Rules / other artefacts |
| Applicability | **Mode A only** |
| Does not | Introduce new business concepts · redefine BC-000 · specify UI/API/database/code · unlock Mode B |

---

# 1 Purpose

BC-003 is the **authoritative business vocabulary** for ECMP Mode A.

| Rule | Statement |
|---|---|
| Authority | Downstream business documents, including Business Rules, SHALL use BC-003 terms without redefining them. |
| Derivation | Every defined term SHALL be traceable to BC-000, BC-001, and/or BW-000. |
| Conflict | If terminology conflicts, **BC-000 SHALL prevail**. |
| Invention | BC-003 SHALL NOT introduce new business concepts. |

---

# 2 Glossary Principles

| ID | Principle | Meaning |
|---|---|---|
| GP-01 | One official name | Each concept has one Official Name in this glossary. |
| GP-02 | Definition ≠ design | Definitions state business meaning, not screens, APIs, or storage. |
| GP-03 | Reserved stays reserved | RESERVED terms SHALL NOT be used as if defined. |
| GP-04 | Duality is explicit | Where dual definitions exist (Case states / SoT), both are named; neither silently replaces the other. |
| GP-05 | Mode A fence | Out-of-scope capabilities are not redefined here as in-scope vocabulary. |
| GP-06 | Traceability | Every entry cites Constitution / Principles / Workflow / Decisions as applicable. |

---

# 3 Core Business Terms

---

## BG-001 — Complaint

| Field | Content |
|---|---|
| **Term ID** | BG-001 |
| **Official Name** | Complaint |
| **Definition** | The complaint business aggregate that may originate from multiple source types and target Branch or Head Office, while remaining a single aggregate. |
| **Business Meaning** | The primary business container for complaint work under Mode A. |
| **Context** | Intake and multi-Case continuity; may exist temporarily without a Case. |
| **Related Terms** | Case; Aggregate; Lifecycle; Source Type; Target Type |
| **NOT TO BE CONFUSED WITH** | Case (a work unit under a Complaint); Ticket (see BG-003) |
| **Referenced Constitution** | BC-4.1; BC-5.4; BC-9.2; BC-9.3 |
| **Referenced Principles** | BP-005; BP-009 |
| **Referenced Workflow** | WS-01; WS-10; EP-01…04 |
| **Referenced Decisions** | DL-006; DL-024 |

---

## BG-002 — Case

| Field | Content |
|---|---|
| **Term ID** | BG-002 |
| **Official Name** | Case |
| **Definition** | A work unit under a Complaint subject to Mode A Case Management rules and the applicable state-machine definition for its Source of Truth. |
| **Business Meaning** | The unit of operational handling, assignment, resolve, and case-level closure. |
| **Context** | Mode A: Complaint MAY register without Case; ≥1 Case required within one working day after Complaint `REGISTERED`. |
| **Related Terms** | Complaint; State; Assignment; Resolution; Closure; Cancellation; Snapshot |
| **NOT TO BE CONFUSED WITH** | Complaint Aggregate; Ticket-as-mandatory-1:1-at-registration |
| **Referenced Constitution** | BC-4.2; BC-5.4; BC-9.1; BC-9.9 |
| **Referenced Principles** | BP-014; BP-011 |
| **Referenced Workflow** | WS-02…WS-09 |
| **Referenced Decisions** | DL-023; DL-024; DL-070 |

---

## BG-003 — Ticket

| Field | Content |
|---|---|
| **Term ID** | BG-003 |
| **Official Name** | Ticket |
| **Definition** | A capability term listed among Complaint Management Module capabilities in ECMP-CONSTITUTION-001. In BC-000 / BC-003, **Ticket SHALL NOT** be construed as requiring every Complaint to have exactly one Ticket/Case at registration. |
| **Business Meaning** | Informal/capability synonym territory; **Case** is the Mode A work-unit term of record. |
| **Context** | Prefer **Case** in Mode A business rules and workflow. |
| **Related Terms** | Case; Complaint |
| **NOT TO BE CONFUSED WITH** | A rule that Complaint:Case must be 1:1 at intake |
| **Referenced Constitution** | BC-4.2; BC-5.4 |
| **Referenced Principles** | BP-003 |
| **Referenced Workflow** | — (use Case stages) |
| **Referenced Decisions** | DL-046; DL-024 |

---

## BG-004 — Aggregate

| Field | Content |
|---|---|
| **Term ID** | BG-004 |
| **Official Name** | Complaint Aggregate (Aggregate) |
| **Definition** | The Complaint as a single aggregate root that may contain multiple Cases and must not be auto-closed by Case closure. |
| **Business Meaning** | Complaint-level continuity independent of individual Case outcomes. |
| **Context** | Multi-Case Complaints (default max five Cases in Mode A). |
| **Related Terms** | Complaint; Case; Closure |
| **NOT TO BE CONFUSED WITH** | Closing a Case |
| **Referenced Constitution** | BC-4.1; BC-5.5; BC-9.4 |
| **Referenced Principles** | BP-014; BP-005 |
| **Referenced Workflow** | WS-10; DG-06 |
| **Referenced Decisions** | DL-006; DL-024 |

---

## BG-005 — Timeline

| Field | Content |
|---|---|
| **Term ID** | BG-005 |
| **Official Name** | Timeline |
| **Definition** | The chronological business record of significant Complaint/Case events, including events required when SLA status changes. |
| **Business Meaning** | Business memory of what happened. |
| **Context** | Applies across the Complaint Lifecycle; not a UI widget specification. |
| **Related Terms** | Timeline Event; SLA; Lifecycle |
| **NOT TO BE CONFUSED WITH** | Screen “history panels” or technical log stores |
| **Referenced Constitution** | BC-4.3; BC-5.3; BC-6.1 |
| **Referenced Principles** | BP-006 |
| **Referenced Workflow** | SLA-T3; all stages producing significant changes |
| **Referenced Decisions** | DL-067 |

---

## BG-006 — Timeline Event

| Field | Content |
|---|---|
| **Term ID** | BG-006 |
| **Official Name** | Timeline Event (Event) |
| **Definition** | A recorded occurrence on the Timeline that captures a business-significant change. SLA-related changes SHALL be recorded as Timeline Events. |
| **Business Meaning** | One dated business fact on the Timeline. |
| **Context** | Constitution does not prescribe payload schemas. |
| **Related Terms** | Timeline; SLA; Business Event |
| **NOT TO BE CONFUSED WITH** | Technical message-broker events as product vocabulary |
| **Referenced Constitution** | BC-4.4; BC-6.1; BC-6.4 |
| **Referenced Principles** | BP-006; BP-007 |
| **Referenced Workflow** | SLA-T3 |
| **Referenced Decisions** | DL-067 |

---

## BG-007 — Business Event

| Field | Content |
|---|---|
| **Term ID** | BG-007 |
| **Official Name** | Business Event |
| **Definition** | Business-language reference to a business-significant recorded change. Under Mode A vocabulary, this SHALL be read as aligned with **Timeline Event** (BG-006), not as a second event taxonomy. |
| **Business Meaning** | Emphasises business significance of recorded change (evidence), without inventing a parallel catalogue. |
| **Context** | Used when speaking about immutable business evidence principles. |
| **Related Terms** | Timeline Event; Timeline |
| **NOT TO BE CONFUSED WITH** | A separate mandatory event model besides Timeline Event |
| **Referenced Constitution** | BC-4.4; BC-6.2 |
| **Referenced Principles** | BP-006; BP-007 |
| **Referenced Workflow** | — |
| **Referenced Decisions** | DL-067; DL-064 |

---

## BG-008 — Assignment

| Field | Content |
|---|---|
| **Term ID** | BG-008 |
| **Official Name** | Assignment |
| **Definition** | In Mode A, assignment of a Case at **Unit** level. Assignment to an individual Assigned User is outside Mode A. |
| **Business Meaning** | Who (which Unit) is responsible for Case work. |
| **Context** | Supervisor retains R/A patterns; Complaint Officer assign only if Authorization permits. |
| **Related Terms** | Unit; Case; Supervisor; Complaint Officer |
| **NOT TO BE CONFUSED WITH** | Assigned User (individual) assignment |
| **Referenced Constitution** | BC-4.7; BC-9.4; BC-8.2; BC-8.3 |
| **Referenced Principles** | BP-012 |
| **Referenced Workflow** | WS-03; DG-02 |
| **Referenced Decisions** | DL-024; DL-001 |

---

## BG-009 — Escalation

| Field | Content |
|---|---|
| **Term ID** | BG-009 |
| **Official Name** | Escalation (Head Office Escalation) |
| **Definition** | Official Complaint Lifecycle capability transferring work along **Branch ↔ Head Office**. |
| **Business Meaning** | Controlled elevation of work to Head Office without creating a separate product. |
| **Context** | Regional Office is not on the path. Mode A does not expose PENDING/ESCALATED surface labels. |
| **Related Terms** | Branch; Head Office; Lifecycle; Appointment |
| **NOT TO BE CONFUSED WITH** | Regional escalation; Work Order; a separate escalation application |
| **Referenced Constitution** | BC-4.8; BC-5.9; BC-7.1; BC-9.5 |
| **Referenced Principles** | BP-008; BP-005 |
| **Referenced Workflow** | WS-05; DG-03; DG-08 |
| **Referenced Decisions** | DL-066 |

---

## BG-010 — Approval

| Field | Content |
|---|---|
| **Term ID** | BG-010 |
| **Official Name** | Supervisor Approval (Approval) |
| **Definition** | Supervisor authority gate required on the Mode A path before Case `CLOSED` after Resolve (`IN_PROGRESS → RESOLVED →` Supervisor Approval `→ CLOSED`). |
| **Business Meaning** | Closure is not complete without Supervisor approval on this path. |
| **Context** | Distinct from Administrator configuration overrides. |
| **Related Terms** | Supervisor; Resolution; Closure |
| **NOT TO BE CONFUSED WITH** | Authorization override by Administrator |
| **Referenced Constitution** | BC-8.3; BC-9.7 |
| **Referenced Principles** | BP-012 |
| **Referenced Workflow** | WS-08; DG-05 |
| **Referenced Decisions** | DL-001; DL-024 |

---

## BG-011 — Resolution

| Field | Content |
|---|---|
| **Term ID** | BG-011 |
| **Official Name** | Resolution (Resolve) |
| **Definition** | Mode A Case resolve action that requires a Comment; Attachment MAY be optional; Complaint Attachments MAY be reused. |
| **Business Meaning** | Declaring Case work resolved pending Supervisor Approval for closure. |
| **Context** | Resolution is not automatic Complaint Aggregate closure. |
| **Related Terms** | Approval; Closure; Case; Final Resolution |
| **NOT TO BE CONFUSED WITH** | Closure; Cancellation; Final Resolution (appointment-chain bound) |
| **Referenced Constitution** | BC-9.7; BC-8.3 |
| **Referenced Principles** | BP-006; BP-014 |
| **Referenced Workflow** | WS-07; DG-04 |
| **Referenced Decisions** | DL-024 |

---

## BG-012 — Final Resolution

| Field | Content |
|---|---|
| **Term ID** | BG-012 |
| **Official Name** | Final Resolution |
| **Definition** | Appointment-lifecycle-related resolution bound constituted via the approved appointment chain: submitted after appointment completion under stated bounds; does not itself close Complaint or Escalation. |
| **Business Meaning** | Records final handling outcome tied to completed appointment path. |
| **Context** | Inside the same Complaint Lifecycle; not a separate lifecycle. |
| **Related Terms** | Appointment; Resolution; Closure |
| **NOT TO BE CONFUSED WITH** | Mode A Case Resolve (BG-011); Case Closure |
| **Referenced Constitution** | BC-9.6 |
| **Referenced Principles** | BP-005 |
| **Referenced Workflow** | WS-06 |
| **Referenced Decisions** | DL-066; DL-011 |

---

## BG-013 — Closure

| Field | Content |
|---|---|
| **Term ID** | BG-013 |
| **Official Name** | Closure (Case Closure) |
| **Definition** | Transition of a Case to `CLOSED` only. MUST NOT automatically close the Complaint Aggregate. |
| **Business Meaning** | Ends Case work, not necessarily Complaint work. |
| **Context** | Follows Supervisor Approval on Mode A resolve path. |
| **Related Terms** | Approval; Cancellation; Aggregate |
| **NOT TO BE CONFUSED WITH** | Complaint Aggregate closure; Cancellation |
| **Referenced Constitution** | BC-5.5; BC-9.8; BC-8.3 |
| **Referenced Principles** | BP-014 |
| **Referenced Workflow** | WS-09; DG-06; CR-01…03 |
| **Referenced Decisions** | DL-024 |

---

## BG-014 — Cancellation

| Field | Content |
|---|---|
| **Term ID** | BG-014 |
| **Official Name** | Cancellation |
| **Definition** | Mode A Case terminal outcome `CANCELLED`, with reasons including Duplicate, Wrong Input, and Customer Cancellation. |
| **Business Meaning** | Stops Case work for constituted cancel reasons without implying Complaint auto-closure. |
| **Context** | Alternate to the resolve→approve→close path. |
| **Related Terms** | Closure; Case |
| **NOT TO BE CONFUSED WITH** | Closure after Resolve+Approval |
| **Referenced Constitution** | BC-9.8 |
| **Referenced Principles** | BP-014 |
| **Referenced Workflow** | WS-09 |
| **Referenced Decisions** | DL-024 |

---

## BG-015 — Organization

| Field | Content |
|---|---|
| **Term ID** | BG-015 |
| **Official Name** | Organization |
| **Definition** | For Mode A constitutional scope, organisation units referenced by Escalation include **Branch** and **Head Office** on the path Branch ↔ Head Office. Regional Office is not part of that path. |
| **Business Meaning** | Organisational locus of complaint operations under Mode A escalation/targeting. |
| **Context** | ECMP is not Enterprise Organization Master under Mode A principles. |
| **Related Terms** | Branch; Head Office; Escalation |
| **NOT TO BE CONFUSED WITH** | Enterprise Organization Sync / Master (OOS Mode B) |
| **Referenced Constitution** | BC-4.5; BC-7.1; BC-7.4 |
| **Referenced Principles** | BP-009; BP-013 |
| **Referenced Workflow** | WS-05 |
| **Referenced Decisions** | DL-066; DL-046 |

---

## BG-016 — Branch

| Field | Content |
|---|---|
| **Term ID** | BG-016 |
| **Official Name** | Branch |
| **Definition** | Organisation unit on the constituted escalation path and a valid Complaint target type. |
| **Business Meaning** | Local operational node for complaint targeting and escalation origin/return path. |
| **Context** | Escalation: Branch → Head Office. |
| **Related Terms** | Head Office; Escalation; Organization |
| **NOT TO BE CONFUSED WITH** | Regional Office; Branch Officer (deprecated discovery concept) |
| **Referenced Constitution** | BC-4.5; BC-7.1; BC-7.2 |
| **Referenced Principles** | BP-008; BP-009 |
| **Referenced Workflow** | WS-05; EP-02 |
| **Referenced Decisions** | DL-066; DL-006 |

---

## BG-017 — Head Office

| Field | Content |
|---|---|
| **Term ID** | BG-017 |
| **Official Name** | Head Office |
| **Definition** | Organisation unit on the constituted escalation path and a valid Complaint target type. |
| **Business Meaning** | Central node for Head Office Escalation. |
| **Context** | Path limited to Branch ↔ Head Office. |
| **Related Terms** | Branch; Escalation |
| **NOT TO BE CONFUSED WITH** | Regional Office; Enterprise Platform headquarters as integration product |
| **Referenced Constitution** | BC-4.5; BC-5.9; BC-7.1; BC-7.2 |
| **Referenced Principles** | BP-008 |
| **Referenced Workflow** | WS-05; EP-03 |
| **Referenced Decisions** | DL-066; DL-006 |

---

## BG-018 — Complaint Officer

| Field | Content |
|---|---|
| **Term ID** | BG-018 |
| **Official Name** | Complaint Officer |
| **Definition** | Operational persona combining former Front Office/Customer Service and Resolver/Handler responsibilities, with situational modes intake and active handling. |
| **Business Meaning** | Primary operational worker for intake and handling. |
| **Context** | Assign/close only if Authorization permits; Supervisor retains default R/A for ASSIGNED/CLOSED. |
| **Related Terms** | Supervisor; Manager; Persona |
| **NOT TO BE CONFUSED WITH** | Separate CS Agent and Handler personas (deprecated split) |
| **Referenced Constitution** | BC-4.6; BC-8.1; BC-8.2 |
| **Referenced Principles** | BP-012; BP-015 |
| **Referenced Workflow** | WS-01; WS-04 |
| **Referenced Decisions** | DL-001 |

---

## BG-019 — Supervisor

| Field | Content |
|---|---|
| **Term ID** | BG-019 |
| **Official Name** | Supervisor |
| **Definition** | Operational persona retaining R/A for assignment/closure patterns and providing Supervisor Approval on the Mode A resolve→close path. |
| **Business Meaning** | Authority persona for assignment/closure governance of Cases. |
| **Context** | Supervisor Queue surfaces Complaints missing mandatory Case timing. |
| **Related Terms** | Approval; Assignment; Complaint Officer |
| **NOT TO BE CONFUSED WITH** | Manager; Administrator |
| **Referenced Constitution** | BC-8.1; BC-8.3; BC-5.4 |
| **Referenced Principles** | BP-012 |
| **Referenced Workflow** | WS-03; WS-08; EP-05; DG-05 |
| **Referenced Decisions** | DL-001; DL-024 |

---

## BG-020 — Manager

| Field | Content |
|---|---|
| **Term ID** | BG-020 |
| **Official Name** | Manager |
| **Definition** | Valid Business Persona in the operational closed set. Manager Workspace/Dashboard implementation MAY be deferred; persona existence does not depend on UI readiness. |
| **Business Meaning** | Aggregate/read-oriented business actor class—not Case assign/close authority by default. |
| **Context** | Honest persona capability: valid even when delivery deferred. |
| **Related Terms** | Persona; Supervisor |
| **NOT TO BE CONFUSED WITH** | A promise that Manager Workspace is already delivered |
| **Referenced Constitution** | BC-8.1; BC-8.4 |
| **Referenced Principles** | BP-012 |
| **Referenced Workflow** | — (no Manager Workspace stage in BW-000) |
| **Referenced Decisions** | DL-068; DL-001 |

---

## BG-021 — Administrator

| Field | Content |
|---|---|
| **Term ID** | BG-021 |
| **Official Name** | Administrator |
| **Definition** | Configuration persona outside the operational closed set. Authorization overrides of the constituted override class are restricted to Administrator with recorded justification and audit trail. |
| **Business Meaning** | Configures and exceptionally overrides; does not replace operational personas. |
| **Context** | Workflow Config / Role-Permission configuration ownership patterns remain as in BC-000. |
| **Related Terms** | Owner; Approval |
| **NOT TO BE CONFUSED WITH** | Supervisor Approval for Case closure |
| **Referenced Constitution** | BC-4.6; BC-8.5; BC-6.2; BC-10.5 |
| **Referenced Principles** | BP-007 |
| **Referenced Workflow** | — |
| **Referenced Decisions** | DL-001; DL-064 |

---

## BG-022 — Snapshot

| Field | Content |
|---|---|
| **Term ID** | BG-022 |
| **Official Name** | Snapshot (SLA Policy Binding) |
| **Definition** | Binding of a Case to an SLA Policy Version under Mode A. Mode A binds without activating countdown (**bind-without-clock**). |
| **Business Meaning** | Case is tied to a policy version for SLA constitution purposes without running Mode A countdown. |
| **Context** | Detail of calculators/engines is outside glossary/constitution HOW. |
| **Related Terms** | SLA; Case; Timeline Event |
| **NOT TO BE CONFUSED WITH** | Active countdown/clock runtime; CAP-006 deferred behaviours |
| **Referenced Constitution** | BC-4.9; BC-9.10; BC-5.3 |
| **Referenced Principles** | BP-010 |
| **Referenced Workflow** | WS-02; SLA-T1 |
| **Referenced Decisions** | DL-024; DL-067 |

---

## BG-023 — SLA

| Field | Content |
|---|---|
| **Term ID** | BG-023 |
| **Official Name** | SLA (Service Level) |
| **Definition** | Service-time commitments under the single official SLA Constitution for the Complaint Lifecycle: uniform business rules; SLA changes recorded as Timeline Events; Mode A Case policy bind-without-clock. |
| **Business Meaning** | One business reading of service time for the lifecycle. |
| **Context** | 24×7 baseline; working-day/pause/case-type differentiation deferred. |
| **Related Terms** | Snapshot; Timeline Event; Lifecycle |
| **NOT TO BE CONFUSED WITH** | A second conflicting business SLA meaning per technical namespace |
| **Referenced Constitution** | BC-5.3; BC-6.1; BC-6.5; BC-6.6; BC-9.10 |
| **Referenced Principles** | BP-010; BP-006 |
| **Referenced Workflow** | SLA-T1…T5 |
| **Referenced Decisions** | DL-067; DL-019; DL-005 |

---

## BG-024 — Appointment

| Field | Content |
|---|---|
| **Term ID** | BG-024 |
| **Official Name** | Appointment |
| **Definition** | Mode A lifecycle capability inside the same Complaint Lifecycle (not a separate lifecycle), within authorized bounds (booking, check-in, completion, no-show, related Final Resolution bounds). |
| **Business Meaning** | Scheduled/handled appointment work tied to the complaint journey. |
| **Context** | Calendar/Slot/Work Order remain Out of Scope. |
| **Related Terms** | Escalation; Final Resolution; Lifecycle |
| **NOT TO BE CONFUSED WITH** | A standalone appointment product/lifecycle; Calendar scheduling systems |
| **Referenced Constitution** | BC-5.8; BC-9.6 |
| **Referenced Principles** | BP-005; BP-013 |
| **Referenced Workflow** | WS-06; DG-07 |
| **Referenced Decisions** | DL-066; DL-007…011 |

---

## BG-025 — Lifecycle

| Field | Content |
|---|---|
| **Term ID** | BG-025 |
| **Official Name** | Complaint Lifecycle |
| **Definition** | The single constituted business journey of a Complaint, including Case work, Escalation, and Appointment as participating capabilities—not parallel products. |
| **Business Meaning** | One end-to-end complaint journey. |
| **Context** | Canonical stages defined in BW-000. |
| **Related Terms** | Workflow; State; Escalation; Appointment |
| **NOT TO BE CONFUSED WITH** | Separate Appointment lifecycle; Mode B enterprise journeys |
| **Referenced Constitution** | BC-5.8; BC-5.9; BC-2.2 |
| **Referenced Principles** | BP-005 |
| **Referenced Workflow** | §3 Canonical Complaint Lifecycle; WS-01…WS-10 |
| **Referenced Decisions** | DL-066; DL-024 |

---

## BG-026 — State

| Field | Content |
|---|---|
| **Term ID** | BG-026 |
| **Official Name** | State (Case State) |
| **Definition** | A named position in an applicable Case state-machine definition. Two definitions coexist: Definition A and Definition B; each applies only within its declared SoT. |
| **Business Meaning** | Where a Case sits in its allowed progression. |
| **Context** | Silent overwrite forbidden. Mode A does not expose PENDING/ESCALATED labels on delivery surface. |
| **Related Terms** | Definition A; Definition B; Dual SoT; Lifecycle |
| **NOT TO BE CONFUSED WITH** | Workflow Stage ID (WS-xx) which is a business-stage label in BW-000 |
| **Referenced Constitution** | BC-9.1; BC-9.5; BC-3.4 |
| **Referenced Principles** | BP-011 |
| **Referenced Workflow** | Business State Diagrams |
| **Referenced Decisions** | DL-023; DL-044 |

---

## BG-027 — Definition A / Definition B

| Field | Content |
|---|---|
| **Term ID** | BG-027 |
| **Official Name** | Case State Definition A / Definition B |
| **Definition** | **A:** `REGISTERED → ASSIGNED → IN_PROGRESS → PENDING_REVIEW → CLOSED → REOPENED`. **B:** `CREATED → ASSIGNED → IN_PROGRESS → PENDING/ESCALATED → RESOLVED → CLOSED` (+ `CANCELLED` before final resolution). |
| **Business Meaning** | Two explicit vocabularies of Case progression. |
| **Context** | Mode A resolve/close path aligns with Definition B style `… → RESOLVED →` Approval `→ CLOSED`. |
| **Related Terms** | State; Dual SoT |
| **NOT TO BE CONFUSED WITH** | A mandate to merge them into one unofficial hybrid |
| **Referenced Constitution** | BC-9.1; BC-8.3 |
| **Referenced Principles** | BP-011 |
| **Referenced Workflow** | §3.2; state diagrams |
| **Referenced Decisions** | DL-023 |

---

## BG-028 — Unit

| Field | Content |
|---|---|
| **Term ID** | BG-028 |
| **Official Name** | Unit |
| **Definition** | The organisational level at which Mode A Assignment occurs. |
| **Business Meaning** | Assignment target for Cases under Mode A. |
| **Context** | Distinct from individual Assigned User. |
| **Related Terms** | Assignment; Organization |
| **NOT TO BE CONFUSED WITH** | Assigned User |
| **Referenced Constitution** | BC-4.7; BC-9.4 |
| **Referenced Principles** | BP-012 |
| **Referenced Workflow** | WS-03; DG-02 |
| **Referenced Decisions** | DL-024 |

---

## BG-029 — Persona

| Field | Content |
|---|---|
| **Term ID** | BG-029 |
| **Official Name** | Persona |
| **Definition** | Business actor class. Operational closed set: Complaint Officer, Supervisor, Manager. Administrator is outside that closed set. |
| **Business Meaning** | Who acts in the business, independent of screen design. |
| **Context** | Closed set changes require governed persona revision. |
| **Related Terms** | Complaint Officer; Supervisor; Manager; Administrator |
| **NOT TO BE CONFUSED WITH** | Technical role-permission strings as definitions of persona |
| **Referenced Constitution** | BC-4.6; BC-8.1 |
| **Referenced Principles** | BP-012 |
| **Referenced Workflow** | — |
| **Referenced Decisions** | DL-001; DL-068 |

---

## BG-030 — Owner (SoT Owner)

| Field | Content |
|---|---|
| **Term ID** | BG-030 |
| **Official Name** | Owner |
| **Definition** | Party named by the applicable ownership decision for a configuration or authorization Source of Truth (Administration for Workflow Config definition; Core Platform for Role-Permission; ECMF as enforcer of workflow transitions). |
| **Business Meaning** | Who holds authoritative definition vs who enforces. |
| **Context** | Prevents dual authoritative copies. |
| **Related Terms** | Administrator; Workflow |
| **NOT TO BE CONFUSED WITH** | Case assignee Unit; Complaint “owner” in informal speech |
| **Referenced Constitution** | BC-4.10; BC-10.5 |
| **Referenced Principles** | BP-002 |
| **Referenced Workflow** | — |
| **Referenced Decisions** | DL-025; DL-056 |

---

## BG-031 — Mode A

| Field | Content |
|---|---|
| **Term ID** | BG-031 |
| **Official Name** | Mode A |
| **Definition** | Authorized delivery strategy that completes the Complaint Management Module without waiting for Enterprise Platform integration. Not a second product or second target architecture. |
| **Business Meaning** | Current governed delivery mode for this glossary. |
| **Context** | Mode B remains closed to coding/production integration behaviours. |
| **Related Terms** | Mode B (OOS for obligations) |
| **NOT TO BE CONFUSED WITH** | A permanently separate business domain from Mode B target |
| **Referenced Constitution** | BC-2.1; BC-2.2 |
| **Referenced Principles** | BP-013 |
| **Referenced Workflow** | Entire BW-000 |
| **Referenced Decisions** | DL-046 |

---

## BG-032 — Dual SoT

| Field | Content |
|---|---|
| **Term ID** | BG-032 |
| **Official Name** | Dual SoT (Dual Sources of Truth) |
| **Definition** | Constituted coexistence of dual Case/Complaint namespace definitions until a Retirement DEC; force-merge or silent retirement is forbidden. |
| **Business Meaning** | Two declared truths may coexist; designs must name which applies. |
| **Context** | Aligns with dual Case state definitions. |
| **Related Terms** | Definition A; Definition B; State |
| **NOT TO BE CONFUSED WITH** | Permission to invent a third unofficial model |
| **Referenced Constitution** | BC-3.4; BC-9.1 |
| **Referenced Principles** | BP-011 |
| **Referenced Workflow** | §3.2 |
| **Referenced Decisions** | DL-023; DL-044 |

---

# 4 Workflow Terms

---

## BG-033 — Workflow

| Field | Content |
|---|---|
| **Term ID** | BG-033 |
| **Official Name** | Business Workflow |
| **Definition** | The canonical Mode A complaint business flow defined by BW-000 (stages, gates, assignment, escalation, SLA touchpoints, closure). |
| **Business Meaning** | How work moves, in business terms. |
| **Context** | Subordinate to BC-000 / BC-001; not UI flow. |
| **Related Terms** | Lifecycle; Decision Gate; Stage |
| **NOT TO BE CONFUSED WITH** | Screen navigation flows |
| **Referenced Constitution** | BC-3.1 |
| **Referenced Principles** | BP-005; BP-001 |
| **Referenced Workflow** | BW-000 entire document |
| **Referenced Decisions** | via BC-000 / DL-024 / DL-066 |

---

## BG-034 — Workflow Stage

| Field | Content |
|---|---|
| **Term ID** | BG-034 |
| **Official Name** | Workflow Stage |
| **Definition** | A named business stage in BW-000 identified as WS-01…WS-10. |
| **Business Meaning** | A phase of the canonical lifecycle. |
| **Context** | Stages may interleave (e.g., Escalation/Appointment with Active Handling). |
| **Related Terms** | Lifecycle; Decision Gate; State |
| **NOT TO BE CONFUSED WITH** | Case State enum labels |
| **Referenced Constitution** | BC-9.* (via BW derivation) |
| **Referenced Principles** | BP-005 |
| **Referenced Workflow** | §3.1; §4 |
| **Referenced Decisions** | DL-024; DL-066 |

---

## BG-035 — Decision Gate

| Field | Content |
|---|---|
| **Term ID** | BG-035 |
| **Official Name** | Decision Gate |
| **Definition** | A constituted business checkpoint in BW-000 (DG-01…DG-08) that allows, blocks, or redirects progression. |
| **Business Meaning** | Pass/fail questions that protect constitutional rules during the flow. |
| **Context** | Examples: Case timing; Unit assignment; Branch↔HO path; Resolve Comment; Supervisor Approval; aggregate protection. |
| **Related Terms** | Workflow; Approval; Escalation |
| **NOT TO BE CONFUSED WITH** | Technical feature flags |
| **Referenced Constitution** | BC-5.4; BC-5.5; BC-7.1; BC-8.3; BC-9.5; BC-9.7 |
| **Referenced Principles** | BP-004; BP-014; BP-008 |
| **Referenced Workflow** | §6 Decision Gates |
| **Referenced Decisions** | DL-024; DL-066 |

---

## BG-036 — Entry Point

| Field | Content |
|---|---|
| **Term ID** | BG-036 |
| **Official Name** | Entry Point |
| **Definition** | A constituted business way into the lifecycle (EP-01…EP-05), including multi-source registration and Supervisor Queue threshold surveillance. |
| **Business Meaning** | How a Complaint journey begins or is forced forward when Case timing fails. |
| **Context** | All source entries remain one aggregate. |
| **Related Terms** | Complaint; Source Type |
| **NOT TO BE CONFUSED WITH** | UI login entry |
| **Referenced Constitution** | BC-9.3; BC-5.4 |
| **Referenced Principles** | BP-009; BP-005 |
| **Referenced Workflow** | §5 Entry Points |
| **Referenced Decisions** | DL-006; DL-024 |

---

## BG-037 — Source Type / Target Type

| Field | Content |
|---|---|
| **Term ID** | BG-037 |
| **Official Name** | Source Type / Target Type |
| **Definition** | Constituted Complaint source values include at least CUSTOMER, BRANCH, HEAD_OFFICE, SYSTEM. Target types include BRANCH and HEAD_OFFICE. |
| **Business Meaning** | Who/what originated the Complaint and where it is targeted. |
| **Context** | Single aggregate model. |
| **Related Terms** | Complaint; Branch; Head Office |
| **NOT TO BE CONFUSED WITH** | Persona names |
| **Referenced Constitution** | BC-9.3; BC-7.2 |
| **Referenced Principles** | BP-009 |
| **Referenced Workflow** | EP-01…04; WS-01 |
| **Referenced Decisions** | DL-006 |

---

## BG-038 — Bind-Without-Clock

| Field | Content |
|---|---|
| **Term ID** | BG-038 |
| **Official Name** | Bind-Without-Clock |
| **Definition** | Mode A rule that a Case binds an SLA Policy Version without activating countdown. |
| **Business Meaning** | Policy association without running Mode A SLA clock. |
| **Context** | Under the single SLA Constitution. |
| **Related Terms** | Snapshot; SLA |
| **NOT TO BE CONFUSED WITH** | “No SLA exists” |
| **Referenced Constitution** | BC-4.9; BC-9.10 |
| **Referenced Principles** | BP-010 |
| **Referenced Workflow** | SLA-T1 |
| **Referenced Decisions** | DL-024; DL-067 |

---

# 5 Governance Terms

---

## BG-039 — Business Constitution

| Field | Content |
|---|---|
| **Term ID** | BG-039 |
| **Official Name** | Business Constitution (BC-000) |
| **Definition** | Highest-level Mode A business normative document defining WHAT governs ECMP business behaviour. |
| **Business Meaning** | Source of constitutional obligations. |
| **Context** | Subordinate to Board/ADR/EA/ECMP-CONSTITUTION-001. |
| **Related Terms** | Business Principles; Business Glossary |
| **NOT TO BE CONFUSED WITH** | Implementation standards |
| **Referenced Constitution** | BC-1.1; BC-1.3 |
| **Referenced Principles** | BP-001 |
| **Referenced Workflow** | — |
| **Referenced Decisions** | DL-046; GC-000 |

---

## BG-040 — Business Principles

| Field | Content |
|---|---|
| **Term ID** | BG-040 |
| **Official Name** | Business Principles (BC-001) |
| **Definition** | Guiding principles that interpret BC-000 into business behaviour without adding constitutional requirements. |
| **Business Meaning** | How to apply the Constitution in judgement. |
| **Context** | Sits under BC-000; above Business Rules/Workflow application. |
| **Related Terms** | Business Constitution |
| **NOT TO BE CONFUSED WITH** | Business Rules catalogue |
| **Referenced Constitution** | BC-3.1 |
| **Referenced Principles** | BC-001 entire |
| **Referenced Workflow** | — |
| **Referenced Decisions** | via BC-000 |

---

## BG-041 — Business Rules

| Field | Content |
|---|---|
| **Term ID** | BG-041 |
| **Official Name** | Business Rules (`BR-0xx`) |
| **Definition** | Rule catalogue using the `BR-0xx` identifier scheme; subordinate to BC-000 / BC-001 / BC-003 vocabulary. |
| **Business Meaning** | Detailed operational rules that must not redefine glossary concepts. |
| **Context** | Configuration vs Hardcoded classification remains as in BC-000. |
| **Related Terms** | Business Constitution; Glossary |
| **NOT TO BE CONFUSED WITH** | Business Principles |
| **Referenced Constitution** | BC-3.3; BC-5.6 |
| **Referenced Principles** | BP-003 |
| **Referenced Workflow** | — |
| **Referenced Decisions** | DL-003; DL-026 |

---

# 6 Reserved Terms

These terms are **RESERVED**. They SHALL NOT be used as if they had Mode A official definitions.

| Term ID | Official Name | Status | Note | Source |
|---|---|---|---|---|
| BG-R01 | Receiving Organization | **RESERVED** | No approved Decision Log / BC-000 definition | BC-4.11 |
| BG-R02 | Current Owning Organization | **RESERVED** | No approved Decision Log / BC-000 definition | BC-4.12 |

Related non-vocabulary fences (not defined as in-scope terms): Regional Office as escalation node; Work Order; Calendar/Slot scheduling systems; Mode B integration product terms as Mode A obligations (BC-000 §11).

---

# 7 Deprecated Terms

| Former term | Status | Replace with | Reason / Source |
|---|---|---|---|
| Front Office / Customer Service (as separate operational persona) | **Deprecated for closed set** | Complaint Officer | DL-001; BC-8.2 |
| Resolver / Case Handler (as separate operational persona) | **Deprecated for closed set** | Complaint Officer | DL-001; BC-8.2 |
| Four-persona operational closed set | **Deprecated** | Three-persona set | DL-001; BC-8.1 |
| PDS-000 as active persona SoT | **Superseded** | PDS-001 (still Draft package) / BC persona terms | DL-001 |
| Reading DEC-001 OOS for Escalation/Appointment as current Mode A scope | **Superseded for those carve-outs** | DL-066 / BC-5.8 / BC-5.9 | BC-10.6 |
| Ticket meaning “mandatory one work unit at registration” | **Rejected reading** | Case + BC-5.4 timing rules | BC-4.2 |
| Branch Officer (discovery baseline concept) | **Out of Scope / not Mode A vocabulary** | — | historical DEC-001 OOS; not reconstituted |

---

# Appendix A — Alphabetical Index

| Term | Term ID |
|---|---|
| Administrator | BG-021 |
| Aggregate (Complaint Aggregate) | BG-004 |
| Appointment | BG-024 |
| Approval (Supervisor Approval) | BG-010 |
| Assignment | BG-008 |
| Bind-Without-Clock | BG-038 |
| Branch | BG-016 |
| Business Constitution | BG-039 |
| Business Event | BG-007 |
| Business Principles | BG-040 |
| Business Rules | BG-041 |
| Cancellation | BG-014 |
| Case | BG-002 |
| Closure | BG-013 |
| Complaint | BG-001 |
| Complaint Lifecycle | BG-025 |
| Complaint Officer | BG-018 |
| Current Owning Organization | BG-R02 (RESERVED) |
| Decision Gate | BG-035 |
| Definition A / Definition B | BG-027 |
| Dual SoT | BG-032 |
| Entry Point | BG-036 |
| Escalation | BG-009 |
| Final Resolution | BG-012 |
| Head Office | BG-017 |
| Lifecycle | BG-025 |
| Manager | BG-020 |
| Mode A | BG-031 |
| Organization | BG-015 |
| Owner | BG-030 |
| Persona | BG-029 |
| Receiving Organization | BG-R01 (RESERVED) |
| Resolution (Resolve) | BG-011 |
| SLA | BG-023 |
| Snapshot | BG-022 |
| Source Type / Target Type | BG-037 |
| State | BG-026 |
| Supervisor | BG-019 |
| Ticket | BG-003 |
| Timeline | BG-005 |
| Timeline Event | BG-006 |
| Unit | BG-028 |
| Workflow | BG-033 |
| Workflow Stage | BG-034 |

---

# Appendix B — Concept Relationship Matrix

| Concept | Relates to | Relationship |
|---|---|---|
| Complaint | Case | Aggregate may contain 0..n Cases (Mode A timing rules apply) |
| Case | Complaint | Work unit under Aggregate |
| Ticket | Case | Capability synonym territory; Case is Mode A term of record |
| Timeline | Timeline Event | Timeline is the series; Event is one occurrence |
| Business Event | Timeline Event | Aligned reading; not a second taxonomy |
| Assignment | Unit | Mode A assignment target |
| Escalation | Branch, Head Office | Path only |
| Appointment | Lifecycle | Inside same lifecycle |
| Resolution | Approval | Resolve then Supervisor Approval before Closure |
| Closure | Aggregate | Case closure ≠ Aggregate closure |
| Snapshot | SLA | Policy bind without Mode A clock |
| Decision Gate | Workflow Stage | Gates protect stage progression |
| Persona | Complaint Officer / Supervisor / Manager | Closed set |
| Dual SoT | Definition A / B | Explicit coexistence |

```
Complaint (Aggregate)
  └── Case(s)
        ├── Assignment → Unit
        ├── Escalation → Branch ↔ Head Office
        ├── Appointment → (same Lifecycle)
        ├── Resolve → Approval → Closure
        └── Cancellation
Timeline ← Timeline Events (incl. SLA changes)
```

---

# Appendix C — Traceability Matrix

| Term ID | BC-000 | BC-001 | BW-000 | Decision(s) |
|---|---|---|---|---|
| BG-001 | BC-4.1 | BP-005 | WS-01 | DL-006; DL-024 |
| BG-002 | BC-4.2 | BP-014 | WS-02…09 | DL-023; DL-024; DL-070 |
| BG-003 | BC-4.2 | BP-003 | — | DL-046; DL-024 |
| BG-004 | BC-5.5 | BP-014 | WS-10; DG-06 | DL-024 |
| BG-005 | BC-4.3 | BP-006 | SLA-T3 | DL-067 |
| BG-006 | BC-4.4 | BP-006 | SLA-T3 | DL-067 |
| BG-007 | BC-4.4; BC-6.2 | BP-007 | — | DL-067; DL-064 |
| BG-008 | BC-4.7 | BP-012 | WS-03 | DL-024 |
| BG-009 | BC-4.8; BC-5.9 | BP-008 | WS-05 | DL-066 |
| BG-010 | BC-8.3 | BP-012 | WS-08 | DL-001; DL-024 |
| BG-011 | BC-9.7 | BP-006 | WS-07 | DL-024 |
| BG-012 | BC-9.6 | BP-005 | WS-06 | DL-066; DL-011 |
| BG-013 | BC-5.5 | BP-014 | WS-09 | DL-024 |
| BG-014 | BC-9.8 | BP-014 | WS-09 | DL-024 |
| BG-015…017 | BC-4.5; BC-7.* | BP-008; BP-009 | WS-05 | DL-066; DL-006 |
| BG-018…021 | BC-8.* | BP-012 | various | DL-001; DL-068; DL-064 |
| BG-022…023 | BC-4.9; BC-5.3 | BP-010 | SLA-T* | DL-024; DL-067 |
| BG-024 | BC-5.8 | BP-005 | WS-06 | DL-066 |
| BG-025…027 | BC-9.1; BC-5.8 | BP-005; BP-011 | §3 | DL-023; DL-066 |
| BG-028…032 | BC-4.7; BC-3.4; BC-2.1 | BP-011…013 | various | DL-024; DL-044; DL-046 |
| BG-033…038 | via BW | BP-005 | BW-000 | DL-024; DL-066 |
| BG-039…041 | BC-1.*; BC-3.* | BC-001 | — | DL-046; DL-003 |
| BG-R01…R02 | BC-4.11; BC-4.12 | BP-003 | — | — |

---

# Appendix D — Validation Report

| Check | Result | Notes |
|---|---|---|
| No new concepts introduced | **PASS** | RESERVED preserved; Business Event aligned to Timeline Event |
| No contradiction with BC-000 | **PASS** | Ticket/Case timing; dual states; OOS fences |
| No contradiction with BC-001 | **PASS** | Principles cited, not extended |
| No contradiction with BW-000 | **PASS** | Stage/gate vocabulary mirrored |
| Every definition traceable | **PASS** | Appendix C |
| No UI/API/DB/code | **PASS** | — |
| No workflow redesign | **PASS** | Glossary only |
| No constitutional changes | **PASS** | BC-000 unmodified |

**Note:** Legacy portal mirror `docs/business/glossary.md` points to `25 Glossary/GLOSSARY.md`. For **Mode A Phase 1 business governance vocabulary**, **BC-003 prevails** for terms it defines. Competing redefinitions in other glossaries SHALL NOT override BC-003 for Mode A business documents.

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-05 | Initial Mode A Business Glossary from BC-000 / BC-001 / BW-000 |

---

*End of BC-003.*
