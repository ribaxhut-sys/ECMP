# BC-002 — Business Rules

| Field | Value |
|---|---|
| Document ID | BC-002 |
| Title | ECMP Business Rules — Mode A Baseline |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | **NORMATIVE RULEBOOK — Mode A Baseline** |
| Milestone | Governance Phase 1 |
| Authority | Derived from BC-000 · BC-001 · BC-003 · BW-000 (secondary: DL-000, GC-000) |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → BC-000 → BC-001 → **BC-002** ↔ BW-000 / BC-003 → UX → Implementation |
| Applicability | **Mode A only** |
| Does not | Add constitutional principles · add workflow stages · redefine glossary · specify UI/API/DB/code |

**Conflict rule:** If BC-002 conflicts with BC-000, **BC-000 SHALL prevail**.

**Vocabulary rule:** Terms SHALL mean as defined in **BC-003**.

---

# 1 Purpose

BC-002 is the **operational business rulebook** for ECMP Mode A complaint handling.

| Layer | Role |
|---|---|
| BC-000 | WHAT shall govern (constitution) |
| BC-001 | HOW to interpret (principles) |
| BC-003 | WHAT words mean (glossary) |
| BW-000 | HOW work flows (workflow stages/gates) |
| **BC-002** | WHICH operational rules apply at triggers |

BC-002 SHALL NOT invent new governance decisions. Every rule SHALL be traceable to the artefacts above.

---

# 2 Rule Hierarchy

```
Board / ADR / EA / ECMP-CONSTITUTION-001
        ↓
Business Constitution (BC-000)
        ↓
Business Principles (BC-001)
        ↓
Business Rules (BC-002)     ← this document
        ↓
Workflow (BW-000)
        ↓
State Machine (as constituted; not redesigned here)
        ↓
UX (approved contracts)
        ↓
Implementation
```

---

# 3 Rule Categories

| Prefix | Category |
|---|---|
| BR-GEN | General Rules |
| BR-CMP | Complaint Rules |
| BR-CAS | Case Rules |
| BR-TL | Timeline Rules |
| BR-ASN | Assignment Rules |
| BR-ESC | Escalation Rules |
| BR-APP | Approval Rules |
| BR-RES | Resolution Rules |
| BR-CLO | Closure Rules |
| BR-ORG | Organization Rules |
| BR-SLA | SLA Rules |
| BR-GOV | Governance Rules |

**Classification values:** Mandatory · Conditional · Optional · Deferred · Reserved

---

# 4 Rules

---

## 4.1 General Rules

### BR-GEN-001 — Mode A Applicability

| Field | Content |
|---|---|
| **Rule ID** | BR-GEN-001 |
| **Title** | Mode A Applicability |
| **Classification** | Mandatory |
| **Statement** | These Business Rules SHALL apply to Mode A only. Mode B behaviours SHALL NOT be treated as Mode A obligations. |
| **Business Context** | Delivery strategy fence. |
| **Trigger** | Any application of ECMP business rules. |
| **Preconditions** | Mode A baseline in force. |
| **Postconditions** | Only Mode A obligations are enforced. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | All |
| **Referenced Glossary Terms** | BG-031 Mode A |
| **Referenced Constitution Clause(s)** | BC-2.1; BC-2.2; §11 |
| **Referenced Principle(s)** | BP-013 |
| **Referenced Decision(s)** | DL-046 |

### BR-GEN-002 — Single Complaint Lifecycle

| Field | Content |
|---|---|
| **Rule ID** | BR-GEN-002 |
| **Title** | Single Complaint Lifecycle |
| **Classification** | Mandatory |
| **Statement** | Escalation and Appointment SHALL participate in the same Complaint Lifecycle. They SHALL NOT constitute a separate product lifecycle. |
| **Business Context** | Scope Consolidation. |
| **Trigger** | Design or execution of Escalation or Appointment. |
| **Preconditions** | Complaint Lifecycle in scope. |
| **Postconditions** | Capabilities remain inside one lifecycle. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-05; WS-06 |
| **Referenced Glossary Terms** | BG-025; BG-009; BG-024 |
| **Referenced Constitution Clause(s)** | BC-5.8; BC-5.9 |
| **Referenced Principle(s)** | BP-005 |
| **Referenced Decision(s)** | DL-066 |

### BR-GEN-003 — Dual State Definitions Explicit

| Field | Content |
|---|---|
| **Rule ID** | BR-GEN-003 |
| **Title** | Dual Case State Definitions |
| **Classification** | Mandatory |
| **Statement** | Definition A and Definition B SHALL coexist explicitly. A design or rule application SHALL name the applicable definition. Silent overwrite SHALL NOT occur. |
| **Business Context** | Dual SoT / dual CSM. |
| **Trigger** | Any Case state transition interpretation. |
| **Preconditions** | Case exists under a declared SoT. |
| **Postconditions** | Applicable definition is identifiable. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-02…WS-09 |
| **Referenced Glossary Terms** | BG-026; BG-027; BG-032 |
| **Referenced Constitution Clause(s)** | BC-9.1; BC-3.4 |
| **Referenced Principle(s)** | BP-011 |
| **Referenced Decision(s)** | DL-023; DL-044 |

### BR-GEN-004 — Out of Scope Fence

| Field | Content |
|---|---|
| **Rule ID** | BR-GEN-004 |
| **Title** | Out of Scope Fence |
| **Classification** | Mandatory |
| **Statement** | Capabilities listed in BC-000 §11 SHALL NOT be treated as Mode A Business Rules obligations. |
| **Business Context** | Scope discipline. |
| **Trigger** | Proposal to use Regional, Work Order, Calendar/Scheduling, Mode B integration, Assigned User, etc. |
| **Preconditions** | BC-000 §11 in force. |
| **Postconditions** | OOS capability not enforced as Mode A rule. |
| **Exceptions** | New Decision Record + Governance Review authorizing inclusion. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-031 |
| **Referenced Constitution Clause(s)** | BC-2.3; §11 |
| **Referenced Principle(s)** | BP-013 |
| **Referenced Decision(s)** | DL-066; DL-046 |

### BR-GEN-005 — Glossary Binding

| Field | Content |
|---|---|
| **Rule ID** | BR-GEN-005 |
| **Title** | Glossary Binding |
| **Classification** | Mandatory |
| **Statement** | Business Rules SHALL use BC-003 Official Names and Definitions. Rules SHALL NOT redefine glossary terms. |
| **Business Context** | Vocabulary integrity. |
| **Trigger** | Authoring or applying any Business Rule. |
| **Preconditions** | BC-003 in force. |
| **Postconditions** | Terms match BC-003. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | All |
| **Referenced Glossary Terms** | All BG-* |
| **Referenced Constitution Clause(s)** | BC-3.1 |
| **Referenced Principle(s)** | BP-003 |
| **Referenced Decision(s)** | GC-000 |

### BR-GEN-006 — Module Boundary

| Field | Content |
|---|---|
| **Rule ID** | BR-GEN-006 |
| **Title** | Complaint Module Boundary |
| **Classification** | Mandatory |
| **Statement** | ECMP SHALL operate as a Complaint Management Business Module. It SHALL NOT be treated as Enterprise Platform, Enterprise OS, generic multi-module framework, SDK, marketplace, or enterprise portal/runtime registry. |
| **Business Context** | Product boundary. |
| **Trigger** | Scope or design expansion proposals. |
| **Preconditions** | — |
| **Postconditions** | Expansion rejected unless governed otherwise. |
| **Exceptions** | Board/ADR authority for true enterprise matters outside this rulebook. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-031 |
| **Referenced Constitution Clause(s)** | BC-5.1; BC-1.4 |
| **Referenced Principle(s)** | BP-001 |
| **Referenced Decision(s)** | DL-046 |

### BR-GEN-007 — Not Customer Master SoR

| Field | Content |
|---|---|
| **Rule ID** | BR-GEN-007 |
| **Title** | Not Customer Master SoR |
| **Classification** | Mandatory |
| **Statement** | ECMP SHALL NOT be System of Record for customer master data. Local customer data SHALL be treated as read-only relative to Customer Master. |
| **Business Context** | Data ownership. |
| **Trigger** | Any write intent to customer master attributes. |
| **Preconditions** | Customer data used in complaint context. |
| **Postconditions** | No unauthorized write-back. |
| **Exceptions** | Explicitly authorized integration only (still OOS as general Mode A product behaviour per §11 item 7). |
| **Related Workflow Stage(s)** | WS-01 |
| **Referenced Glossary Terms** | BG-001 |
| **Referenced Constitution Clause(s)** | BC-5.2; §11 |
| **Referenced Principle(s)** | BP-013 |
| **Referenced Decision(s)** | DL-031 |

---

## 4.2 Complaint Rules

### BR-CMP-001 — Single Aggregate

| Field | Content |
|---|---|
| **Rule ID** | BR-CMP-001 |
| **Title** | Single Complaint Aggregate |
| **Classification** | Mandatory |
| **Statement** | A Complaint SHALL remain a single aggregate regardless of source type or target type. |
| **Business Context** | Multi-source/multi-target without split. |
| **Trigger** | Complaint registration. |
| **Preconditions** | Valid source intent. |
| **Postconditions** | One Complaint Aggregate exists. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-01 |
| **Referenced Glossary Terms** | BG-001; BG-004 |
| **Referenced Constitution Clause(s)** | BC-4.1; BC-9.3 |
| **Referenced Principle(s)** | BP-005; BP-009 |
| **Referenced Decision(s)** | DL-006 |

### BR-CMP-002 — Allowed Sources

| Field | Content |
|---|---|
| **Rule ID** | BR-CMP-002 |
| **Title** | Allowed Complaint Sources |
| **Classification** | Mandatory |
| **Statement** | Complaint sources SHALL include at least CUSTOMER, BRANCH, HEAD_OFFICE, and SYSTEM. |
| **Business Context** | Multi-source entry. |
| **Trigger** | WS-01 registration. |
| **Preconditions** | — |
| **Postconditions** | Source type recorded within aggregate model. |
| **Exceptions** | None in Mode A baseline. |
| **Related Workflow Stage(s)** | WS-01; EP-01…04 |
| **Referenced Glossary Terms** | BG-037; BG-001 |
| **Referenced Constitution Clause(s)** | BC-9.3 |
| **Referenced Principle(s)** | BP-009 |
| **Referenced Decision(s)** | DL-006 |

### BR-CMP-003 — Allowed Targets

| Field | Content |
|---|---|
| **Rule ID** | BR-CMP-003 |
| **Title** | Allowed Complaint Targets |
| **Classification** | Mandatory |
| **Statement** | Complaint targeting SHALL support BRANCH and HEAD_OFFICE. |
| **Business Context** | Multi-target model. |
| **Trigger** | WS-01 registration. |
| **Preconditions** | Complaint being registered. |
| **Postconditions** | Target type within constituted set. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-01 |
| **Referenced Glossary Terms** | BG-037; BG-016; BG-017 |
| **Referenced Constitution Clause(s)** | BC-7.2 |
| **Referenced Principle(s)** | BP-009 |
| **Referenced Decision(s)** | DL-006 |

### BR-CMP-004 — Registration Without Case

| Field | Content |
|---|---|
| **Rule ID** | BR-CMP-004 |
| **Title** | Registration Without Case |
| **Classification** | Optional |
| **Statement** | A Complaint MAY be registered without creating a Case at registration time. |
| **Business Context** | Intake flexibility. |
| **Trigger** | WS-01. |
| **Preconditions** | Complaint registration. |
| **Postconditions** | Complaint exists; Case may be absent. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-01 |
| **Referenced Glossary Terms** | BG-001; BG-002 |
| **Referenced Constitution Clause(s)** | BC-9.2; BC-5.4 |
| **Referenced Principle(s)** | BP-005 |
| **Referenced Decision(s)** | DL-024 |

### BR-CMP-005 — Mandatory First Case Timing

| Field | Content |
|---|---|
| **Rule ID** | BR-CMP-005 |
| **Title** | Mandatory First Case Timing |
| **Classification** | Mandatory |
| **Statement** | Every Complaint MUST have at least one Case within one working day after Complaint `REGISTERED`. The Supervisor Queue MUST surface Complaints that miss this threshold. |
| **Business Context** | Prevent orphan Complaints. |
| **Trigger** | Elapse of one working day after registration without Case; or continuous surveillance. |
| **Preconditions** | Complaint registered. |
| **Postconditions** | Case established or threshold visible to Supervisor. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-02; EP-05; DG-01 |
| **Referenced Glossary Terms** | BG-001; BG-002; BG-019 |
| **Referenced Constitution Clause(s)** | BC-5.4 |
| **Referenced Principle(s)** | BP-005 |
| **Referenced Decision(s)** | DL-024 |

---

## 4.3 Case Rules

### BR-CAS-001 — Case Numbering

| Field | Content |
|---|---|
| **Rule ID** | BR-CAS-001 |
| **Title** | Case Number Independence |
| **Classification** | Mandatory |
| **Statement** | Case Number SHALL be independent of Complaint Number and SHALL use format `UNIT-YYMM-NNNN` (e.g. `TAB-2608-0001`). Complaint Number SHALL use `CM{UNIT}-YYMM-NNNN` (e.g. `CMTAB-2608-0001`). |
| **Business Context** | Identity clarity. |
| **Trigger** | WS-02 Case establishment. |
| **Preconditions** | Case being created. |
| **Postconditions** | Case Number assigned per format. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-02 |
| **Referenced Glossary Terms** | BG-002 |
| **Referenced Constitution Clause(s)** | BC-9.9 |
| **Referenced Principle(s)** | BP-003 |
| **Referenced Decision(s)** | DL-024; DL-070 |

### BR-CAS-002 — Maximum Cases Default

| Field | Content |
|---|---|
| **Rule ID** | BR-CAS-002 |
| **Title** | Maximum Cases per Complaint |
| **Classification** | Mandatory |
| **Statement** | Default maximum Cases per Complaint SHALL be five. Override policy beyond five SHALL be outside Mode A. |
| **Business Context** | Multi-Case control. |
| **Trigger** | Attempt to create additional Case. |
| **Preconditions** | Complaint exists. |
| **Postconditions** | Case count ≤ 5 under Mode A default. |
| **Exceptions** | Outside-Mode-A override policy (not constituted here). |
| **Related Workflow Stage(s)** | WS-02; WS-10 |
| **Referenced Glossary Terms** | BG-002; BG-004 |
| **Referenced Constitution Clause(s)** | BC-9.4; §11 |
| **Referenced Principle(s)** | BP-014; BP-013 |
| **Referenced Decision(s)** | DL-024 |

### BR-CAS-003 — Mode A Surface Labels PENDING/ESCALATED

| Field | Content |
|---|---|
| **Rule ID** | BR-CAS-003 |
| **Title** | Mode A Non-Exposure of PENDING/ESCALATED Labels |
| **Classification** | Mandatory |
| **Statement** | Aggregate states PENDING and ESCALATED SHALL remain defined but SHALL NOT be exposed on the Mode A delivery surface. |
| **Business Context** | Mode A exposure rule with Escalation still official. |
| **Trigger** | Presentation or Mode A surface labelling of Case/Complaint state. |
| **Preconditions** | Mode A delivery. |
| **Postconditions** | Those labels not exposed on Mode A surface. |
| **Exceptions** | None for Mode A surface. |
| **Related Workflow Stage(s)** | WS-05; DG-08 |
| **Referenced Glossary Terms** | BG-026; BG-009 |
| **Referenced Constitution Clause(s)** | BC-9.5 |
| **Referenced Principle(s)** | BP-011; BP-008 |
| **Referenced Decision(s)** | DL-024; DL-066 |

---

## 4.4 Timeline Rules

### BR-TL-001 — SLA Changes on Timeline

| Field | Content |
|---|---|
| **Rule ID** | BR-TL-001 |
| **Title** | SLA Changes Produce Timeline Events |
| **Classification** | Mandatory |
| **Statement** | Every SLA-related change SHALL be recorded as Timeline Event(s). |
| **Business Context** | One SLA Constitution + Timeline First. |
| **Trigger** | Any SLA-related change. |
| **Preconditions** | Timeline exists for the Complaint/Case context. |
| **Postconditions** | Timeline Event(s) recorded. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-02; SLA-T3; all SLA touchpoints |
| **Referenced Glossary Terms** | BG-005; BG-006; BG-023 |
| **Referenced Constitution Clause(s)** | BC-5.3; BC-6.1; BC-4.4 |
| **Referenced Principle(s)** | BP-006; BP-010 |
| **Referenced Decision(s)** | DL-067 |

### BR-TL-002 — Write-Audit Mandatory

| Field | Content |
|---|---|
| **Rule ID** | BR-TL-002 |
| **Title** | Write-Audit Mandatory |
| **Classification** | Mandatory |
| **Statement** | Write-audit SHALL be mandatory for governed writes. |
| **Business Context** | Accountability. |
| **Trigger** | Governed write (registration, assignment, resolve, close, config, etc.). |
| **Preconditions** | Write occurring. |
| **Postconditions** | Write-audit recorded. |
| **Exceptions** | None for write path. |
| **Related Workflow Stage(s)** | WS-01…WS-09 |
| **Referenced Glossary Terms** | BG-007 |
| **Referenced Constitution Clause(s)** | BC-5.7 |
| **Referenced Principle(s)** | BP-007 |
| **Referenced Decision(s)** | DL-063 |

### BR-TL-003 — Read-Audit Deferred

| Field | Content |
|---|---|
| **Rule ID** | BR-TL-003 |
| **Title** | Read-Audit Deferred |
| **Classification** | Deferred |
| **Statement** | Read-audit SHALL remain deferred until a Decision Record activates it. |
| **Business Context** | Explicit deferral. |
| **Trigger** | Read operations. |
| **Preconditions** | — |
| **Postconditions** | No Mode A mandatory read-audit obligation. |
| **Exceptions** | Future DEC activation. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | — |
| **Referenced Constitution Clause(s)** | BC-5.7; §11 |
| **Referenced Principle(s)** | BP-013 |
| **Referenced Decision(s)** | DL-063 |

### BR-TL-004 — Immutable Audit Trails

| Field | Content |
|---|---|
| **Rule ID** | BR-TL-004 |
| **Title** | Immutable Audit Trails |
| **Classification** | Mandatory |
| **Statement** | Audit trails that record governed writes SHALL be immutable. |
| **Business Context** | Integrity of evidence. |
| **Trigger** | Any attempt to alter audit evidence. |
| **Preconditions** | Audit record exists. |
| **Postconditions** | Record remains unchanged. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | All governed writes |
| **Referenced Glossary Terms** | BG-007 |
| **Referenced Constitution Clause(s)** | BC-6.2; BC-5.6 |
| **Referenced Principle(s)** | BP-007 |
| **Referenced Decision(s)** | DL-064; DL-026 |

---

## 4.5 Assignment Rules

### BR-ASN-001 — Unit-Level Assignment

| Field | Content |
|---|---|
| **Rule ID** | BR-ASN-001 |
| **Title** | Unit-Level Assignment Only |
| **Classification** | Mandatory |
| **Statement** | Mode A Assignment SHALL be at Unit level only. |
| **Business Context** | Mode A assignment model. |
| **Trigger** | WS-03 assignment. |
| **Preconditions** | Case requires assignment. |
| **Postconditions** | Case assigned to Unit. |
| **Exceptions** | None in Mode A. |
| **Related Workflow Stage(s)** | WS-03; DG-02 |
| **Referenced Glossary Terms** | BG-008; BG-028 |
| **Referenced Constitution Clause(s)** | BC-4.7; BC-9.4 |
| **Referenced Principle(s)** | BP-012 |
| **Referenced Decision(s)** | DL-024 |

### BR-ASN-002 — Assigned User Outside Mode A

| Field | Content |
|---|---|
| **Rule ID** | BR-ASN-002 |
| **Title** | Assigned User Outside Mode A |
| **Classification** | Mandatory |
| **Statement** | Assignment to an individual Assigned User SHALL NOT be part of Mode A Business Rules. |
| **Business Context** | OOS individual assignment. |
| **Trigger** | Attempt to assign to person rather than Unit. |
| **Preconditions** | Mode A. |
| **Postconditions** | Assignment rejected as Mode A path. |
| **Exceptions** | Outside Mode A (not defined here). |
| **Related Workflow Stage(s)** | WS-03; DG-02 |
| **Referenced Glossary Terms** | BG-008 |
| **Referenced Constitution Clause(s)** | BC-4.7; §11 |
| **Referenced Principle(s)** | BP-013 |
| **Referenced Decision(s)** | DL-024 |

### BR-ASN-003 — Assignment Authority

| Field | Content |
|---|---|
| **Rule ID** | BR-ASN-003 |
| **Title** | Assignment Authority |
| **Classification** | Conditional |
| **Statement** | Supervisor SHALL retain R/A for assignment patterns. Complaint Officer MAY assign only if Authorization permits. |
| **Business Context** | Persona authority. |
| **Trigger** | Assignment decision. |
| **Preconditions** | Actor is Supervisor or permitted Complaint Officer. |
| **Postconditions** | Valid authority exercised. |
| **Exceptions** | Unauthorized Complaint Officer SHALL NOT assign. |
| **Related Workflow Stage(s)** | WS-03 |
| **Referenced Glossary Terms** | BG-018; BG-019; BG-008 |
| **Referenced Constitution Clause(s)** | BC-8.2; BC-8.3 |
| **Referenced Principle(s)** | BP-012 |
| **Referenced Decision(s)** | DL-001 |

---

## 4.6 Escalation Rules

### BR-ESC-001 — Escalation In Scope

| Field | Content |
|---|---|
| **Rule ID** | BR-ESC-001 |
| **Title** | Escalation Is Official Lifecycle Capability |
| **Classification** | Mandatory |
| **Statement** | Head Office Escalation SHALL be an official Complaint Lifecycle capability. |
| **Business Context** | Scope Consolidation. |
| **Trigger** | Need to escalate. |
| **Preconditions** | Complaint/Case in lifecycle. |
| **Postconditions** | Escalation treated as in-scope capability. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-05 |
| **Referenced Glossary Terms** | BG-009; BG-025 |
| **Referenced Constitution Clause(s)** | BC-5.9 |
| **Referenced Principle(s)** | BP-008; BP-005 |
| **Referenced Decision(s)** | DL-066 |

### BR-ESC-002 — Branch to Head Office Path Only

| Field | Content |
|---|---|
| **Rule ID** | BR-ESC-002 |
| **Title** | Branch ↔ Head Office Path Only |
| **Classification** | Mandatory |
| **Statement** | Escalation routing SHALL use Branch → Head Office only. Regional Office SHALL NOT be a node on the path. |
| **Business Context** | Controlled Escalation. |
| **Trigger** | WS-05; DG-03. |
| **Preconditions** | Escalation requested. |
| **Postconditions** | Path confined to Branch ↔ Head Office. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-05; DG-03 |
| **Referenced Glossary Terms** | BG-016; BG-017; BG-009 |
| **Referenced Constitution Clause(s)** | BC-7.1; BC-4.5 |
| **Referenced Principle(s)** | BP-008; BP-013 |
| **Referenced Decision(s)** | DL-066 |

### BR-ESC-003 — DEC-F4 Detail Not Elevated

| Field | Content |
|---|---|
| **Rule ID** | BR-ESC-003 |
| **Title** | DEC-F4 Detail Not Binding Yet |
| **Classification** | Reserved |
| **Statement** | Detailed visibility, return, and result-audience rules from DEC-F4 SHALL NOT be enforced as Mode A Business Rules until formal DEC approval/countersign is complete. |
| **Business Context** | PENDING formal DEC. |
| **Trigger** | Attempt to apply F4 detail as binding rule. |
| **Preconditions** | DL-012 still pending formal. |
| **Postconditions** | Only path scope (BR-ESC-002) binds. |
| **Exceptions** | After formal DEC, rules may be added via governed update. |
| **Related Workflow Stage(s)** | WS-05 |
| **Referenced Glossary Terms** | BG-009 |
| **Referenced Constitution Clause(s)** | BC-7.3 |
| **Referenced Principle(s)** | BP-003 |
| **Referenced Decision(s)** | DL-066; DL-012 |

---

## 4.7 Approval Rules

### BR-APP-001 — Supervisor Approval Before Case Closed

| Field | Content |
|---|---|
| **Rule ID** | BR-APP-001 |
| **Title** | Supervisor Approval Before Case Closed |
| **Classification** | Mandatory |
| **Statement** | On the Mode A resolve path, Case SHALL NOT reach `CLOSED` without Supervisor Approval after Resolve. |
| **Business Context** | Closure gate. |
| **Trigger** | Transition toward Case closure after Resolve. |
| **Preconditions** | Case resolved under Mode A path. |
| **Postconditions** | Approval recorded or closure blocked. |
| **Exceptions** | Cancellation path (BR-CLO-003) does not use this resolve approval sequence. |
| **Related Workflow Stage(s)** | WS-08; DG-05; CR-01 |
| **Referenced Glossary Terms** | BG-010; BG-013; BG-019 |
| **Referenced Constitution Clause(s)** | BC-8.3 |
| **Referenced Principle(s)** | BP-012 |
| **Referenced Decision(s)** | DL-001; DL-024 |

### BR-APP-002 — Administrator Override Distinct

| Field | Content |
|---|---|
| **Rule ID** | BR-APP-002 |
| **Title** | Administrator Override Distinct from Supervisor Approval |
| **Classification** | Conditional |
| **Statement** | Authorization overrides of the constituted override class SHALL be performed only by Administrator with recorded justification and audit trail. Such overrides SHALL NOT replace Supervisor Approval for Case closure. |
| **Business Context** | Separate control planes. |
| **Trigger** | Authorization override request. |
| **Preconditions** | Actor is Administrator; justification provided. |
| **Postconditions** | Override audited; Case closure still follows BR-APP-001 when on resolve path. |
| **Exceptions** | None that collapse the two concepts. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-021; BG-010 |
| **Referenced Constitution Clause(s)** | BC-8.5; BC-6.2 |
| **Referenced Principle(s)** | BP-007 |
| **Referenced Decision(s)** | DL-064 |

---

## 4.8 Resolution Rules

### BR-RES-001 — Resolve Requires Comment

| Field | Content |
|---|---|
| **Rule ID** | BR-RES-001 |
| **Title** | Resolve Requires Comment |
| **Classification** | Mandatory |
| **Statement** | Mode A Resolve SHALL require a Comment. |
| **Business Context** | Completeness of resolution. |
| **Trigger** | WS-07 Resolve. |
| **Preconditions** | Case in active handling / ready to resolve. |
| **Postconditions** | Comment present; Case resolved pending approval. |
| **Exceptions** | None for Mode A Resolve. |
| **Related Workflow Stage(s)** | WS-07; DG-04 |
| **Referenced Glossary Terms** | BG-011 |
| **Referenced Constitution Clause(s)** | BC-9.7 |
| **Referenced Principle(s)** | BP-007 |
| **Referenced Decision(s)** | DL-024 |

### BR-RES-002 — Attachment Optional on Resolve

| Field | Content |
|---|---|
| **Rule ID** | BR-RES-002 |
| **Title** | Attachment Optional on Resolve |
| **Classification** | Optional |
| **Statement** | Attachment MAY be provided on Resolve. Complaint Attachments MAY be reused. |
| **Business Context** | Evidence flexibility. |
| **Trigger** | WS-07. |
| **Preconditions** | Resolve in progress. |
| **Postconditions** | Attachment present or absent without blocking if Comment exists. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-07 |
| **Referenced Glossary Terms** | BG-011 |
| **Referenced Constitution Clause(s)** | BC-9.7 |
| **Referenced Principle(s)** | BP-006 |
| **Referenced Decision(s)** | DL-024 |

### BR-RES-003 — Final Resolution Bounds

| Field | Content |
|---|---|
| **Rule ID** | BR-RES-003 |
| **Title** | Final Resolution Does Not Auto-Close |
| **Classification** | Conditional |
| **Statement** | When Final Resolution bounds from the appointment chain apply, Final Resolution SHALL NOT by itself close the Complaint or Escalation. |
| **Business Context** | Appointment-chain outcome vs Case/Complaint closure. |
| **Trigger** | Final Resolution under WS-06 bounds. |
| **Preconditions** | Appointment completion path as constituted. |
| **Postconditions** | Final Resolution recorded; Complaint/Escalation not auto-closed by that fact alone. |
| **Exceptions** | None that invent auto-close. |
| **Related Workflow Stage(s)** | WS-06 |
| **Referenced Glossary Terms** | BG-012; BG-024 |
| **Referenced Constitution Clause(s)** | BC-9.6 |
| **Referenced Principle(s)** | BP-005; BP-014 |
| **Referenced Decision(s)** | DL-066; DL-011 |

### BR-RES-004 — Appointment Inside Lifecycle

| Field | Content |
|---|---|
| **Rule ID** | BR-RES-004 |
| **Title** | Appointment Inside Same Lifecycle |
| **Classification** | Mandatory |
| **Statement** | Appointment capabilities within authorized bounds SHALL be executed inside the Complaint Lifecycle. Treating Appointment as a separate lifecycle SHALL NOT be allowed. |
| **Business Context** | DG-07. |
| **Trigger** | Appointment activity. |
| **Preconditions** | Appointment applicable under constituted bounds. |
| **Postconditions** | Remains same lifecycle. |
| **Exceptions** | Calendar/Slot/Work Order remain OOS (not enabled by this rule). |
| **Related Workflow Stage(s)** | WS-06; DG-07 |
| **Referenced Glossary Terms** | BG-024; BG-025 |
| **Referenced Constitution Clause(s)** | BC-5.8; BC-9.6 |
| **Referenced Principle(s)** | BP-005; BP-013 |
| **Referenced Decision(s)** | DL-066 |

---

## 4.9 Closure Rules

### BR-CLO-001 — Case Closure Does Not Close Aggregate

| Field | Content |
|---|---|
| **Rule ID** | BR-CLO-001 |
| **Title** | Case Closure Does Not Close Aggregate |
| **Classification** | Mandatory |
| **Statement** | Closing a Case SHALL transition that Case to `CLOSED` only and MUST NOT automatically close the Complaint Aggregate. |
| **Business Context** | Aggregate protection. |
| **Trigger** | WS-09 Case closure; DG-06. |
| **Preconditions** | Supervisor Approval on resolve path (BR-APP-001) when applicable. |
| **Postconditions** | Case closed; Complaint continuity remains (WS-10). |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-09; WS-10; DG-06 |
| **Referenced Glossary Terms** | BG-013; BG-004 |
| **Referenced Constitution Clause(s)** | BC-5.5 |
| **Referenced Principle(s)** | BP-014 |
| **Referenced Decision(s)** | DL-024 |

### BR-CLO-002 — Mode A Resolve-Close Path

| Field | Content |
|---|---|
| **Rule ID** | BR-CLO-002 |
| **Title** | Mode A Resolve-Close Path |
| **Classification** | Mandatory |
| **Statement** | Mode A closure path SHALL follow: active handling → Resolve → Supervisor Approval → Case `CLOSED`. |
| **Business Context** | Canonical close sequence. |
| **Trigger** | Intent to close via resolve path. |
| **Preconditions** | BR-RES-001 satisfied. |
| **Postconditions** | Case `CLOSED` only after approval. |
| **Exceptions** | Cancellation path BR-CLO-003. |
| **Related Workflow Stage(s)** | WS-07; WS-08; WS-09; CR-01 |
| **Referenced Glossary Terms** | BG-011; BG-010; BG-013 |
| **Referenced Constitution Clause(s)** | BC-8.3 |
| **Referenced Principle(s)** | BP-012 |
| **Referenced Decision(s)** | DL-024 |

### BR-CLO-003 — Cancellation Allowed

| Field | Content |
|---|---|
| **Rule ID** | BR-CLO-003 |
| **Title** | Cancellation Allowed |
| **Classification** | Conditional |
| **Statement** | A Case MAY be `CANCELLED` in Mode A for reasons including Duplicate, Wrong Input, and Customer Cancellation. |
| **Business Context** | Alternate terminal. |
| **Trigger** | Cancel decision with constituted reason. |
| **Preconditions** | Constituted reason applies. |
| **Postconditions** | Case `CANCELLED`; Complaint not auto-closed. |
| **Exceptions** | Reasons outside constituted list not authorized by this rule. |
| **Related Workflow Stage(s)** | WS-09 |
| **Referenced Glossary Terms** | BG-014 |
| **Referenced Constitution Clause(s)** | BC-9.8 |
| **Referenced Principle(s)** | BP-014 |
| **Referenced Decision(s)** | DL-024 |

---

## 4.10 Organization Rules

### BR-ORG-001 — Organization Vocabulary for Escalation

| Field | Content |
|---|---|
| **Rule ID** | BR-ORG-001 |
| **Title** | Organization Vocabulary for Escalation |
| **Classification** | Mandatory |
| **Statement** | Escalation organisation units SHALL be Branch and Head Office only for the constituted path. |
| **Business Context** | Organization-aware operations. |
| **Trigger** | Escalation routing. |
| **Preconditions** | Escalation in progress. |
| **Postconditions** | Only Branch/Head Office used. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | WS-05 |
| **Referenced Glossary Terms** | BG-015; BG-016; BG-017 |
| **Referenced Constitution Clause(s)** | BC-4.5; BC-7.1 |
| **Referenced Principle(s)** | BP-009; BP-008 |
| **Referenced Decision(s)** | DL-066 |

### BR-ORG-002 — Reserved Organization Terms

| Field | Content |
|---|---|
| **Rule ID** | BR-ORG-002 |
| **Title** | Reserved Organization Terms |
| **Classification** | Reserved |
| **Statement** | Receiving Organization and Current Owning Organization SHALL NOT be used as if defined Mode A business terms. |
| **Business Context** | RESERVED vocabulary. |
| **Trigger** | Drafting rules/designs using those names. |
| **Preconditions** | — |
| **Postconditions** | Terms unused as defined. |
| **Exceptions** | Future Decision Record defining them. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-R01; BG-R02 |
| **Referenced Constitution Clause(s)** | BC-4.11; BC-4.12 |
| **Referenced Principle(s)** | BP-003 |
| **Referenced Decision(s)** | — |

### BR-ORG-003 — No Enterprise Org Master in Mode A

| Field | Content |
|---|---|
| **Rule ID** | BR-ORG-003 |
| **Title** | No Enterprise Org Master Obligation in Mode A |
| **Classification** | Mandatory |
| **Statement** | Mode A Business Rules SHALL NOT require ECMP to act as Enterprise Organization Master or Mode B Org Sync product. |
| **Business Context** | OOS enterprise org. |
| **Trigger** | Proposal to own enterprise org hierarchy in Mode A. |
| **Preconditions** | Mode A. |
| **Postconditions** | Proposal rejected as Mode A rule. |
| **Exceptions** | Mode B governed unlock (outside this rulebook). |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-015; BG-031 |
| **Referenced Constitution Clause(s)** | BC-7.4; §11 |
| **Referenced Principle(s)** | BP-013 |
| **Referenced Decision(s)** | DL-046; DL-066 |

---

## 4.11 SLA Rules

### BR-SLA-001 — One SLA Constitution

| Field | Content |
|---|---|
| **Rule ID** | BR-SLA-001 |
| **Title** | One SLA Constitution |
| **Classification** | Mandatory |
| **Statement** | SLA SHALL be interpreted under exactly one official SLA Constitution for the Complaint Lifecycle with uniform business rules. |
| **Business Context** | End conflicting business readings. |
| **Trigger** | Any SLA interpretation. |
| **Preconditions** | Case/Complaint in lifecycle. |
| **Postconditions** | Single business reading applied. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | SLA-T2 |
| **Referenced Glossary Terms** | BG-023 |
| **Referenced Constitution Clause(s)** | BC-5.3 |
| **Referenced Principle(s)** | BP-010 |
| **Referenced Decision(s)** | DL-067 |

### BR-SLA-002 — Bind Policy Version Without Clock

| Field | Content |
|---|---|
| **Rule ID** | BR-SLA-002 |
| **Title** | Bind Policy Version Without Clock |
| **Classification** | Mandatory |
| **Statement** | Each Case SHALL bind an SLA Policy Version. Countdown SHALL NOT be activated in Mode A (bind-without-clock). |
| **Business Context** | Snapshot binding. |
| **Trigger** | WS-02 Case establishment / SLA-T1. |
| **Preconditions** | Case being established. |
| **Postconditions** | Policy Version bound; no Mode A countdown. |
| **Exceptions** | None in Mode A. |
| **Related Workflow Stage(s)** | WS-02; SLA-T1 |
| **Referenced Glossary Terms** | BG-022; BG-038; BG-023 |
| **Referenced Constitution Clause(s)** | BC-9.10; BC-4.9 |
| **Referenced Principle(s)** | BP-010 |
| **Referenced Decision(s)** | DL-024; DL-067 |

### BR-SLA-003 — Calendar Baseline 24×7

| Field | Content |
|---|---|
| **Rule ID** | BR-SLA-003 |
| **Title** | Calendar Baseline 24×7 |
| **Classification** | Mandatory |
| **Statement** | Baseline SLA calendar SHALL be 24×7. |
| **Business Context** | Baseline default. |
| **Trigger** | SLA calendar interpretation. |
| **Preconditions** | — |
| **Postconditions** | 24×7 applied. |
| **Exceptions** | None until DEC changes baseline. |
| **Related Workflow Stage(s)** | SLA-T4 |
| **Referenced Glossary Terms** | BG-023 |
| **Referenced Constitution Clause(s)** | BC-6.5 |
| **Referenced Principle(s)** | BP-010 |
| **Referenced Decision(s)** | DL-019; DL-004 |

### BR-SLA-004 — Working Day / Pause / Case-Type Differentiation Deferred

| Field | Content |
|---|---|
| **Rule ID** | BR-SLA-004 |
| **Title** | Deferred SLA Behaviours |
| **Classification** | Deferred |
| **Statement** | Working-day calendars, Pause/Resume SLA, and per-case-type SLA differentiation SHALL remain deferred until Business Owner DEC activation. |
| **Business Context** | Explicit CAP-006 deferrals. |
| **Trigger** | Request to use deferred behaviours. |
| **Preconditions** | — |
| **Postconditions** | Behaviour not enforced. |
| **Exceptions** | Future DEC. |
| **Related Workflow Stage(s)** | SLA-T4 |
| **Referenced Glossary Terms** | BG-023 |
| **Referenced Constitution Clause(s)** | BC-6.5; §11 |
| **Referenced Principle(s)** | BP-013 |
| **Referenced Decision(s)** | DL-019 |

### BR-SLA-005 — Numeric Targets Are References

| Field | Content |
|---|---|
| **Rule ID** | BR-SLA-005 |
| **Title** | Numeric Targets Are References |
| **Classification** | Mandatory |
| **Statement** | Numeric SLA/NFR baseline targets SHALL be treated as references revisable by Business Owner via DEC, not irreversible constants of this rulebook. |
| **Business Context** | Reversible baselines. |
| **Trigger** | Citing numeric targets. |
| **Preconditions** | Baseline values published. |
| **Postconditions** | Values used as references. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | SLA-T5 |
| **Referenced Glossary Terms** | BG-023 |
| **Referenced Constitution Clause(s)** | BC-6.6 |
| **Referenced Principle(s)** | BP-010 |
| **Referenced Decision(s)** | DL-005; DL-004 |

---

## 4.12 Governance Rules

### BR-GOV-001 — Conflict Order

| Field | Content |
|---|---|
| **Rule ID** | BR-GOV-001 |
| **Title** | Conflict Order |
| **Classification** | Mandatory |
| **Statement** | Conflict order SHALL be Board Resolution → ADR → EA Documents → ECMP-CONSTITUTION-001 → BC-000 → BC-001 → Business Rules → lower artefacts. |
| **Business Context** | Precedence. |
| **Trigger** | Document conflict. |
| **Preconditions** | Conflicting statements exist. |
| **Postconditions** | Higher layer prevails. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-039; BG-040 |
| **Referenced Constitution Clause(s)** | BC-10.1; BC-1.3 |
| **Referenced Principle(s)** | BP-004 |
| **Referenced Decision(s)** | DL-046 |

### BR-GOV-002 — Configuration vs Hardcoded

| Field | Content |
|---|---|
| **Rule ID** | BR-GOV-002 |
| **Title** | Configuration vs Hardcoded |
| **Classification** | Mandatory |
| **Statement** | Rules classified Hardcoded (including immutable audit trail and mandatory authentication as constituted) SHALL NOT be disableable configuration options. Configuration-class rules SHALL use versioned configuration with effective dating. |
| **Business Context** | Integrity vs operational flexibility. |
| **Trigger** | Attempt to toggle integrity controls via config. |
| **Preconditions** | Rule classification known. |
| **Postconditions** | Hardcoded remains enforced. |
| **Exceptions** | None for Hardcoded class. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-041 |
| **Referenced Constitution Clause(s)** | BC-5.6 |
| **Referenced Principle(s)** | BP-007 |
| **Referenced Decision(s)** | DL-026; DL-064 |

### BR-GOV-003 — Config and Role-Permission Audit

| Field | Content |
|---|---|
| **Rule ID** | BR-GOV-003 |
| **Title** | Config and Role-Permission Audit |
| **Classification** | Mandatory |
| **Statement** | Changes to Role-Permission configuration and Workflow Config SHALL be audited. |
| **Business Context** | Critical configuration accountability. |
| **Trigger** | Config change. |
| **Preconditions** | Change submitted. |
| **Postconditions** | Audit recorded. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-030 |
| **Referenced Constitution Clause(s)** | BC-6.3; BC-10.5 |
| **Referenced Principle(s)** | BP-007 |
| **Referenced Decision(s)** | DL-065; DL-025; DL-056 |

### BR-GOV-004 — Persona Closed Set

| Field | Content |
|---|---|
| **Rule ID** | BR-GOV-004 |
| **Title** | Persona Closed Set |
| **Classification** | Mandatory |
| **Statement** | Operational personas SHALL be Complaint Officer, Supervisor, and Manager only. Adding or splitting personas SHALL require governed revision. Manager MAY have deferred Workspace without losing persona validity. |
| **Business Context** | Honest persona capability. |
| **Trigger** | Actor modelling / authorization mapping to personas. |
| **Preconditions** | — |
| **Postconditions** | Closed set respected. |
| **Exceptions** | Administrator remains outside closed set by design. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-029; BG-018; BG-019; BG-020; BG-021 |
| **Referenced Constitution Clause(s)** | BC-8.1; BC-8.4; BC-8.5 |
| **Referenced Principle(s)** | BP-012 |
| **Referenced Decision(s)** | DL-001; DL-068 |

### BR-GOV-005 — No Force-Merge Dual SoT

| Field | Content |
|---|---|
| **Rule ID** | BR-GOV-005 |
| **Title** | No Force-Merge Dual SoT |
| **Classification** | Mandatory |
| **Statement** | Dual SoT SHALL remain until a Retirement DEC. Force-merge or silent retirement SHALL NOT occur. |
| **Business Context** | Explicit duality. |
| **Trigger** | Proposal to merge SoTs silently. |
| **Preconditions** | Dual SoT in force. |
| **Postconditions** | Duality preserved. |
| **Exceptions** | Retirement DEC only. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-032 |
| **Referenced Constitution Clause(s)** | BC-3.4; §11 |
| **Referenced Principle(s)** | BP-011 |
| **Referenced Decision(s)** | DL-044; DL-046 |

### BR-GOV-006 — OOS Expansion Requires Decision

| Field | Content |
|---|---|
| **Rule ID** | BR-GOV-006 |
| **Title** | OOS Expansion Requires Decision |
| **Classification** | Mandatory |
| **Statement** | Expanding any BC-000 §11 Out of Scope item into Mode A obligations SHALL require a new Decision Record and Governance Review before Business Rules may enforce it. |
| **Business Context** | Change control. |
| **Trigger** | Scope expansion request. |
| **Preconditions** | Item currently OOS. |
| **Postconditions** | No enforcement until Decision+Review. |
| **Exceptions** | None. |
| **Related Workflow Stage(s)** | — |
| **Referenced Glossary Terms** | BG-031 |
| **Referenced Constitution Clause(s)** | BC-10.4; BC-2.3 |
| **Referenced Principle(s)** | BP-004; BP-013 |
| **Referenced Decision(s)** | DL-047; DL-066 |

---

# 5 Business Rule Matrix

| Rule ID | Category | Classification | Title |
|---|---|---|---|
| BR-GEN-001 | General | Mandatory | Mode A Applicability |
| BR-GEN-002 | General | Mandatory | Single Complaint Lifecycle |
| BR-GEN-003 | General | Mandatory | Dual Case State Definitions |
| BR-GEN-004 | General | Mandatory | Out of Scope Fence |
| BR-GEN-005 | General | Mandatory | Glossary Binding |
| BR-GEN-006 | General | Mandatory | Complaint Module Boundary |
| BR-GEN-007 | General | Mandatory | Not Customer Master SoR |
| BR-CMP-001 | Complaint | Mandatory | Single Complaint Aggregate |
| BR-CMP-002 | Complaint | Mandatory | Allowed Complaint Sources |
| BR-CMP-003 | Complaint | Mandatory | Allowed Complaint Targets |
| BR-CMP-004 | Complaint | Optional | Registration Without Case |
| BR-CMP-005 | Complaint | Mandatory | Mandatory First Case Timing |
| BR-CAS-001 | Case | Mandatory | Case Number Independence |
| BR-CAS-002 | Case | Mandatory | Maximum Cases per Complaint |
| BR-CAS-003 | Case | Mandatory | Non-Exposure PENDING/ESCALATED |
| BR-TL-001 | Timeline | Mandatory | SLA Changes → Timeline Events |
| BR-TL-002 | Timeline | Mandatory | Write-Audit Mandatory |
| BR-TL-003 | Timeline | Deferred | Read-Audit Deferred |
| BR-TL-004 | Timeline | Mandatory | Immutable Audit Trails |
| BR-ASN-001 | Assignment | Mandatory | Unit-Level Assignment |
| BR-ASN-002 | Assignment | Mandatory | Assigned User Outside Mode A |
| BR-ASN-003 | Assignment | Conditional | Assignment Authority |
| BR-ESC-001 | Escalation | Mandatory | Escalation Official |
| BR-ESC-002 | Escalation | Mandatory | Branch↔HO Path Only |
| BR-ESC-003 | Escalation | Reserved | DEC-F4 Detail Not Binding |
| BR-APP-001 | Approval | Mandatory | Supervisor Approval Before Closed |
| BR-APP-002 | Approval | Conditional | Admin Override Distinct |
| BR-RES-001 | Resolution | Mandatory | Resolve Requires Comment |
| BR-RES-002 | Resolution | Optional | Attachment Optional |
| BR-RES-003 | Resolution | Conditional | Final Resolution No Auto-Close |
| BR-RES-004 | Resolution | Mandatory | Appointment Inside Lifecycle |
| BR-CLO-001 | Closure | Mandatory | Case≠Aggregate Closure |
| BR-CLO-002 | Closure | Mandatory | Resolve-Close Path |
| BR-CLO-003 | Closure | Conditional | Cancellation Allowed |
| BR-ORG-001 | Organization | Mandatory | Branch/HO Vocabulary |
| BR-ORG-002 | Organization | Reserved | Reserved Org Terms |
| BR-ORG-003 | Organization | Mandatory | No Enterprise Org Master Mode A |
| BR-SLA-001 | SLA | Mandatory | One SLA Constitution |
| BR-SLA-002 | SLA | Mandatory | Bind-Without-Clock |
| BR-SLA-003 | SLA | Mandatory | Calendar 24×7 |
| BR-SLA-004 | SLA | Deferred | Deferred SLA Behaviours |
| BR-SLA-005 | SLA | Mandatory | Numeric Targets References |
| BR-GOV-001 | Governance | Mandatory | Conflict Order |
| BR-GOV-002 | Governance | Mandatory | Configuration vs Hardcoded |
| BR-GOV-003 | Governance | Mandatory | Config/Role Audit |
| BR-GOV-004 | Governance | Mandatory | Persona Closed Set |
| BR-GOV-005 | Governance | Mandatory | No Force-Merge Dual SoT |
| BR-GOV-006 | Governance | Mandatory | OOS Expansion Requires Decision |

**Totals:** 47 rules — Mandatory 36 · Conditional 5 · Optional 2 · Deferred 2 · Reserved 2

---

# 6 Rule-to-Workflow Matrix

| Rule ID | Primary WS / Gate / Touchpoint |
|---|---|
| BR-CMP-004; BR-CMP-001…003 | WS-01; EP-01…04 |
| BR-CMP-005; BR-CAS-001…002; BR-SLA-002 | WS-02; DG-01; SLA-T1 |
| BR-ASN-001…003 | WS-03; DG-02 |
| BR-GEN-002; BR-CAS-003 | WS-04; WS-05; DG-08 |
| BR-ESC-001…003; BR-ORG-001 | WS-05; DG-03 |
| BR-RES-003…004 | WS-06; DG-07 |
| BR-RES-001…002 | WS-07; DG-04 |
| BR-APP-001; BR-CLO-002 | WS-08; DG-05 |
| BR-CLO-001; BR-CLO-003 | WS-09; DG-06 |
| BR-CLO-001; BR-CAS-002 | WS-10 |
| BR-TL-001; BR-SLA-001…005 | SLA-T1…T5 |
| BR-GEN-*; BR-GOV-*; BR-ORG-002…003; BR-APP-002; BR-TL-002…004 | Cross-cutting |

---

# 7 Rule-to-Constitution Matrix

| BC Clause cluster | Rules |
|---|---|
| BC-2.* / §11 Scope | BR-GEN-001; BR-GEN-004; BR-GOV-006; BR-ORG-003; BR-ASN-002 |
| BC-3.4 / BC-9.1 Duality | BR-GEN-003; BR-GOV-005; BR-CAS-003 |
| BC-4.1 / BC-9.3 Complaint model | BR-CMP-001…003 |
| BC-5.4 / BC-9.2 Case timing | BR-CMP-004…005 |
| BC-4.7 / BC-9.4 Assignment | BR-ASN-001…003; BR-CAS-002 |
| BC-5.8–5.9 / BC-7.1 Escalation & Appointment | BR-GEN-002; BR-ESC-001…002; BR-RES-004; BR-ORG-001 |
| BC-7.3 F4 | BR-ESC-003 |
| BC-4.11–4.12 Reserved | BR-ORG-002 |
| BC-5.3 / BC-4.9 / BC-6.* / BC-9.10 SLA | BR-SLA-001…005; BR-TL-001 |
| BC-5.5 / BC-8.3 / BC-9.7–9.8 Closure path | BR-APP-001; BR-RES-001…002; BR-CLO-001…003 |
| BC-5.7 / BC-6.2–6.3 Audit | BR-TL-002…004; BR-GOV-003; BR-APP-002 |
| BC-5.1–5.2 / BC-5.6 Boundary & Hardcoded | BR-GEN-006…007; BR-GOV-002 |
| BC-8.* Personas | BR-GOV-004; BR-ASN-003; BR-APP-001 |
| BC-9.6 Final Resolution / Appointment bounds | BR-RES-003…004 |
| BC-9.9 Numbering | BR-CAS-001 |
| BC-10.* Governance | BR-GOV-001…006; BR-GEN-005 |

---

# 8 Coverage Report

| BC-000 area | Covered by BC-002? | Notes |
|---|---|---|
| Purpose / hierarchy | YES | BR-GOV-001; BR-GEN-005 |
| Mode A scope / OOS | YES | BR-GEN-001; BR-GEN-004; BR-GOV-006 |
| Dual SoT / CSM | YES | BR-GEN-003; BR-GOV-005; BR-CAS-003 |
| Complaint multi-source/target | YES | BR-CMP-001…003 |
| Case timing / numbering / max | YES | BR-CMP-004…005; BR-CAS-001…002 |
| Assignment Unit-only | YES | BR-ASN-* |
| Escalation Branch↔HO | YES | BR-ESC-*; BR-ORG-001 |
| Appointment same lifecycle | YES | BR-RES-004; BR-GEN-002 |
| Resolve / Approval / Close / Cancel | YES | BR-RES-*; BR-APP-*; BR-CLO-* |
| SLA constitution / bind-without-clock | YES | BR-SLA-*; BR-TL-001 |
| Timeline / audit | YES | BR-TL-* |
| Personas | YES | BR-GOV-004 |
| Not customer SoR / module boundary | YES | BR-GEN-006…007 |
| Config vs Hardcoded / ownership audit | YES | BR-GOV-002…003 |
| DEC-F4 detail | Reserved only | BR-ESC-003 |
| Receiving/Current Owning Org | Reserved only | BR-ORG-002 |
| UX Golden Rules detail | Indirect | via BP-015 / not duplicated as UI rules |
| Numeric SLA tables | Reference only | BR-SLA-005 (no invented numbers) |

---

# Appendix A — Validation Report

| Check | Result |
|---|---|
| No new constitutional requirements | **PASS** |
| No new workflow stages | **PASS** (references WS/DG only) |
| No glossary redefinitions | **PASS** (BC-003 citations) |
| No UI / API / database / implementation guidance | **PASS** |
| Every rule traceable to BC-000 / BC-001 / BC-003 / BW-000 / Decisions | **PASS** |
| BC-000/001/003/BW-000 unmodified | **PASS** |
| Deferred/Reserved classifications used where constituted | **PASS** |

---

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-05 | Initial Mode A Business Rules from BC-000 / BC-001 / BC-003 / BW-000 |

---

*End of BC-002.*
