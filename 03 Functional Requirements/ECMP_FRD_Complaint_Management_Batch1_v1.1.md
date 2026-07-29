# ECMP Functional Requirements Document — Complaint Management Module Batch 1

| Field | Value |
|---|---|
| Document ID | FRD-CM-001 |
| Title | Complaint Management Module — FRD Batch 1 |
| Version | 1.1 |
| Status | 🔒 LOCKED |
| Owner | Business Analyst / Domain PO ECMF |
| Reviewer | Solution Architect, Operations Lead, Compliance, Security |
| Approver | Business Owner / Architecture Board / CTO |
| Module | Complaint Management Module only |
| Last Review | 2026-07-29 |
| Next Review | 2026-10-29 |
| Related BR Catalog | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001) |
| Related ADRs | ADR-014 (Enterprise Business Module), ADR-015 (Enterprise Identity Contract), ADR-002 (Customer Master non-SoR), ADR-008 (Role-Permission), ADR-009 (Outbox) |
| Related Revision Plan | `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Revision_Plan_v1.1.md` (GOV-RP-FRD-CM-001) |
| Related Architecture Review | `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Architecture_Review_v1.0.md` (GOV-REV-FRD-CM-001) |
| Related Delta Review | `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Delta_Review_v1.1.md` (GOV-DELTA-FRD-CM-001) — Completed |
| Related Release Notes | `18 Architecture Governance/reviews/ECMP_FRD_CM_001_v1.1_LOCKED_Release_Notes.md` |
| Supersedes | FRD-CM-001 Draft v1.0; closes FRD-CM-001 Draft v1.1 |

---

## Table of Contents

1. [Document Control](#1-document-control)
2. [Purpose and Scope](#2-purpose-and-scope)
3. [Locked Architecture Decisions](#3-locked-architecture-decisions)
4. [External Dependencies](#4-external-dependencies)
5. [Actors](#5-actors)
6. [FR Catalog Summary](#6-fr-catalog-summary)
7. [FR-001 Complaint Registration](#7-fr-001-complaint-registration)
8. [FR-002 Customer Search](#8-fr-002-customer-search)
9. [FR-003 Duplicate Complaint Detection](#9-fr-003-duplicate-complaint-detection)
10. [FR-004 Attachment Upload](#10-fr-004-attachment-upload)
11. [Use Case Mapping](#11-use-case-mapping)
12. [Screen Mapping](#12-screen-mapping)
13. [API Mapping](#13-api-mapping)
14. [Database Mapping](#14-database-mapping)
15. [Business Rule Mapping](#15-business-rule-mapping)
16. [Requirements Traceability Matrix (DM → BR → FR)](#16-requirements-traceability-matrix-dm--br--fr)
17. [Out of Scope](#17-out-of-scope)
18. [Open Questions](#18-open-questions)
19. [Document History](#19-document-history)
20. [Revision Summary (v1.1)](#20-revision-summary-v11)

---

## 1. Document Control

### 1.1 Namespace Clarification

This FRD defines **Complaint Aggregate** functional requirements for the Complaint Management Module target model (BR-CM-CAT-001).

| Namespace | Document | Meaning of BR-001 / FR-001 |
|---|---|---|
| **This FRD (normative LOCKED Batch 1 SoT)** | FRD-CM-001 + BR-CM-CAT-001 | FR-001 = Complaint Registration; BR-001 = Create Complaint |
| Delivery Sprint SoT (separate) | FRD-001 / BR-DOC-001 | FR-001 = Create Case (case-centric slice); BR-001 = workflow transition rule |

Until a formal DEC remaps delivery SoT to the Complaint Aggregate model, **implementation of this Batch 1 FRD MUST NOT silently overwrite Sprint delivery IDs**. Traceability in this document uses **BR-CM-CAT-001 rule IDs** and **FRD-CM-001 FR IDs**.

Document status is **LOCKED** (CTO Decision D-08). This FRD is the **Source of Truth for Batch 1 implementation** (FR-001…FR-004). Claude Delta Review and CTO Approval are complete. Per D-01, foundation readiness of BR-CM-CAT-001 / ADR-014 / ADR-015 / DEC remapping remains tracked under OQ-CM-B1-001 — this LOCK does not upgrade those artifacts' statuses.

### 1.2 Quality Rules Applied

- RFC-2119 keywords: **MUST**, **SHALL**, **SHOULD**, **MAY**
- No inventing Business Rules — all BR references are from BR-CM-CAT-001
- No Out-of-Scope capabilities
- API-first integration; Frontend → ECMP Backend → Enterprise APIs only
- ECMP is **not** Customer Master System of Record
- Threat modeling is mandatory: every FR includes **Security Considerations**

### 1.3 CTO Decisions Applied in v1.1

| ID | Decision | Application |
|---|---|---|
| D-01 | Readiness language | “Architecture Baseline Pending Governance Approval” — no technical redesign |
| D-02 | No Case create in Batch 1 | Duplicate Detection may detect / warn / recommend / link only; Case creation → Batch 2 |
| D-03 | Batch 1 idempotency | Request Id + Channel Message Id + Replay Detection + Double Submit Protection (human + channel) |
| D-04 | Enumeration Protection MUST | Rate limiting, progressive delay, abuse detection, security audit, alerting; ownership declared |
| D-05 | Customer 360 Batch 1 minimum | Customer Profile + Active Complaints + Complaint Count; no full Customer 360 dependency |
| D-06 | Staged evidence transfer | On redirect to existing Complaint, staged evidence MUST transfer; never discard; full audit history |
| D-07 | Customer Merge | Not designed in Batch 1; Open Question for v1.2 |
| D-08 | LOCK FRD-CM-001 v1.1 | Approve Claude Delta Review; Status = LOCKED as Batch 1 SoT; park Request Id TTL, Request Id generation authority, and attachment TRANSFERRED semantics as Open Questions / Architecture Decision candidates — no FR redesign, no Batch 1 scope change |

---

## 2. Purpose and Scope

### 2.1 Purpose

Provide the **LOCKED Batch 1 Source of Truth** for intake capabilities of the Complaint Management Module:

1. Register a Complaint Aggregate Root
2. Search and validate Customer via Master Customer
3. Detect potential duplicate Complaints
4. Upload supporting attachments

Technical content of the Aggregate model is unchanged from Draft v1.0 locked decisions; v1.1 corrects specification gaps and applies approved CTO decisions.

### 2.2 In Scope (Batch 1 only)

| FR ID | Title |
|---|---|
| FR-001 | Complaint Registration |
| FR-002 | Customer Search |
| FR-003 | Duplicate Complaint Detection |
| FR-004 | Attachment Upload |

### 2.3 Explicitly Out of Scope (this Batch)

Assignment, Working Day SLA calculation, Escalation, Resolution, Closure, Reopen, **Case creation (any path — including initial Case at register and “Add Case on existing Complaint”)**, full Customer 360 view beyond the Batch 1 minimum subset (D-05), Communication History, Comment Management, Complaint Search as a standalone FR, Dashboard KPI, Reporting, Customer Merge/retirement handling (D-07 → v1.2), UI visual design, OpenAPI payload design, database physical design, sequence diagrams, backend/frontend code.

---

## 3. Locked Architecture Decisions

The following decisions are **LOCKED** and MUST NOT be changed by this FRD:

| # | Decision |
|---|---|
| 1 | Complaint is Aggregate Root |
| 2 | Complaint contains one or many Cases |
| 3 | Assignment belongs to Case |
| 4 | SLA belongs to Case |
| 5 | SLA uses Working Days only |
| 6 | Saturday is excluded from Working Days |
| 7 | Sunday is excluded from Working Days |
| 8 | Holidays are excluded from Working Days (Calendar Platform) |
| 9 | Complaint stores only `CustomerId` |
| 10 | Customer data comes from Master Customer API; customer data is not duplicated as SoR |
| 11 | Escalation principle: **No Information Lost During Escalation** |
| 12 | API First; no direct database access to enterprise systems |
| 13 | Frontend MUST NOT call Enterprise APIs directly; Frontend → ECMP Backend → Enterprise APIs |

> Note: Multi-Case capability remains locked architecturally. **Creating Cases is out of Batch 1 scope** (CTO D-02); Case create FRs belong to Batch 2.

---

## 4. External Dependencies

ECMP integrates with the following **external enterprise systems via APIs only**. ECMP MUST NOT assume direct database access.

| Dependency | Role in Batch 1 | Owner |
|---|---|---|
| Identity | Principal identity for actor attribution | Enterprise Identity |
| Authentication | Prove actor identity before any FR | Enterprise Authentication |
| Organization | Unit/branch context of registering actor | Enterprise Organization |
| Master Customer | Customer lookup and profile read for FR-002 / FR-001 | Master Customer Platform |
| Notification | Opt-in notifications after successful registration / critical attachment events | Notification Platform |
| Enterprise Security Controls (Anti-Enumeration) | Rate limiting, progressive delay, abuse detection, security audit, alerting for customer-key search (FR-002) | Enterprise Security / SOC (contracted via ECMP Backend) |
| Calendar | Not required for Batch 1 create/search/duplicate/upload; required later for Case SLA (BR-006) | Calendar Platform |
| Audit Platform | Optional sink for audit copies; ECMP MUST still write mandatory module audit (BR-016) | Audit Platform |
| Enterprise Storage | Attachment binary storage | Storage Platform |

### 4.1 Internal authorization boundary (normative)

**Authorization is ECMP-internal** (Core Platform Role-Permission SoT per ADR-008; Complaint Authorization per ADR-014 / ADR-015). Authorization MUST NOT be listed or implemented as an outbound “external enterprise Authorization API” for module complaint/customer/attachment decisions.

---

## 5. Actors

| Actor | Batch 1 Relevance |
|---|---|
| Agent / Petugas Frontline | Primary actor for FR-001…FR-004 |
| Supervisor Unit | May create Complaint; may override duplicate warning with justification (FR-003); receives aging / abuse alerts per policy |
| Case Handler | May upload attachments on existing Complaint (FR-004). Case create is out of Batch 1 |
| Administrator | Configures categories, channels, attachment policy, duplicate thresholds, idempotency and enumeration policies |
| System | Generates Complaint Number, enforces idempotency, runs duplicate scoring, enforces validations, writes audit/timeline, transfers staged evidence |
| Customer | Source of complaint; does not log into this module in Batch 1 scope |
| Master Customer (external) | Authoritative customer data source |
| Enterprise Security / SOC | Owns anti-enumeration control plane consumed by ECMP Backend (D-04) |

---

## 6. FR Catalog Summary

| FR ID | Title | Priority | Primary BR References |
|---|---|---|---|
| FR-001 | Complaint Registration | Must | BR-001, BR-002, BR-014, BR-016, BR-017 |
| FR-002 | Customer Search | Must | BR-002 |
| FR-003 | Duplicate Complaint Detection | Must | BR-014, BR-003, BR-016 |
| FR-004 | Attachment Upload | Must | BR-012, BR-016, BR-017 |

Supporting BR references used within flows (not separate Batch 1 FRs): BR-010 (Customer 360 **Batch 1 minimum subset** during create — D-05), BR-011 / BR-013 (optional initial notes/communication — out of Batch 1 FR scope if invoked), BR-018 (duplicate linkage history).

**BR-004 Create Case** is referenced only as deferred Batch 2 capability. Batch 1 MUST NOT invoke Case creation.

### 6.1 KPI Impact (Batch 1)

| KPI / Measure | Source BR affinity | Batch 1 observation |
|---|---|---|
| Time to Register | BR-001 | Intake duration to `REGISTERED` |
| % Possible Duplicate Override | BR-014 | Override rate among warned creates |
| Complaint without Case (aging) | BR-001 A4 | All Batch 1 Complaints start without Case (D-02); supervisor queue MUST flag aging items awaiting Batch 2 Case create |
| Idempotent replay rate | D-03 | Replays detected vs new Aggregates |
| Enumeration / abuse events | D-04 | Security audit + alert volume on FR-002 |

---

## 7. FR-001 Complaint Registration

### 1. Document ID

**FR-001**

### 2. Title

Complaint Registration

### 3. Description

The system SHALL enable an authorized actor to register a new **Complaint** as Aggregate Root after the customer has been identified via Master Customer. The Complaint SHALL store only `CustomerId` as the customer reference, generate a unique Complaint Number, set initial status `REGISTERED`, and persist mandatory audit and timeline records. Assignment and SLA MUST NOT be created at Complaint level. **Case creation MUST NOT occur in Batch 1** (CTO D-02). Create paths MUST enforce idempotency (CTO D-03).

### 4. Business Objective

Ensure every customer complaint enters ECMP as a valid, uniquely identified, fully auditable Complaint Aggregate that is ready for subsequent Case work in Batch 2 — without duplicating Master Customer data and without losing intake evidence.

### 5. Business Rule Reference

| Rule ID | Rule Name | Usage in FR-001 |
|---|---|---|
| BR-001 | Create Complaint | Primary rule |
| BR-002 | Customer Validation | Mandatory prerequisite |
| BR-014 | Duplicate Complaint | Mandatory pre-confirm check |
| BR-016 | Audit Trail | Mandatory on successful create |
| BR-017 | Timeline | Mandatory “Complaint Created” entry |
| BR-010 | Customer 360 View | Batch 1 minimum subset MUST be available before confirm (D-05) |
| BR-012 | Attachment Management | MAY attach evidence during create |
| BR-018 | Complaint History | Records possible-duplicate linkage / initial snapshot |

### 6. Actors

- Agent / Petugas Frontline (primary)
- Supervisor Unit
- System
- Administrator (configuration of category, channel, priority defaults, idempotency policy)
- Integrated channel System (auto-register when policy active)

### 7. Preconditions

1. Actor MUST be authenticated via Enterprise Authentication / Identity (human path), or channel identity MUST be established per integration contract (channel path).
2. Actor MUST hold ECMP authorization to create Complaint for the relevant organizational unit (ECMP-internal authorization).
3. Actor’s organization/unit context MUST be resolvable from Organization dependency.
4. Master Customer integration MUST be available, or an Administrator-configured degradation mode MUST be active (see Exception Flow).
5. Active reference data MUST exist for: intake channel, complaint category/type, and allowed priority values.
6. Customer MUST be validated per FR-002 / BR-002 before final confirmation (except configured UNVERIFIED emergency mode).
7. Idempotency inputs MUST be present per §12 / D-03.

### 8. Trigger

Actor selects business action **Create New Complaint** after receiving a customer complaint through a configured intake channel (walk-in, phone, email, portal, integrated social, or other Administrator-configured channel), **or** an integrated channel submits an auto-register payload when policy is active.

### 9. Normal Flow

1. Actor opens Create Complaint (or channel starts auto-register session).
2. Actor / channel performs Customer Search (FR-002) using **exactly one** primary key type: Customer Number **or** Identity Number **or** Reference Number.
3. System displays Master Customer brief profile; actor confirms the correct customer (human path) or channel confirmation rules apply.
4. System MUST present Batch 1 Customer 360 minimum context (D-05): Customer Profile, Active Complaints, Complaint Count.
5. System runs Duplicate Complaint Detection (FR-003 / BR-014) and presents warnings when candidates exist.
6. Actor completes mandatory Complaint attributes:
   - Intake channel
   - Category / complaint type
   - Subject
   - Description
   - Initial priority (or configured default)
   - Recording unit (default = actor unit)
   - Optional external reference (channel ticket number, letter number, etc.)
7. Actor MAY upload initial attachments (FR-004) as staged evidence.
8. Actor confirms creation (human) or System confirms auto-register when policy and validations pass (channel).
9. System SHALL enforce idempotency (D-03) before persist:
   - Honor **Request Id** (human and channel)
   - Honor **Channel Message Id** when channel-sourced
   - Detect **Replay** and **Double Submit**
10. System SHALL:
   - Generate a unique Complaint Number (on first successful accept of an idempotency key)
   - Persist Complaint with status `REGISTERED`
   - Persist `CustomerId` only (no Master Customer SoR copy)
   - Persist registration timestamp, creating actor/channel principal, and unit
   - Write Audit Trail (BR-016) and Timeline entry (BR-017)
   - Bind any staged attachments to the new Complaint (FR-004)
   - Request Notification Platform delivery per opt-in configuration (ECMP-side outbox / delivery-status projection MUST record attempt outcome; see §18)
11. System SHALL display confirmation including Complaint Number and status (human path) or return equivalent channel acknowledgement.

### 10. Alternative Flow

#### A1 — Multiple customer candidates

1. Master Customer returns multiple matches.
2. Actor selects exactly one candidate (FR-002 A1).
3. Flow resumes at customer confirmation.

#### A2 — Duplicate warning → open / continue on existing Complaint (no new Aggregate; no Case create)

1. FR-003 marks strong duplicate candidate(s).
2. Actor opens / continues on existing Complaint and does **not** create a new Aggregate.
3. Create Complaint is cancelled with no new Aggregate.
4. Any staged evidence from the abandoned create session MUST **transfer** to the surviving Complaint (CTO D-06; FR-004 A4). Physical discard is prohibited.
5. System MUST record linkage / redirect decision in Audit and History (BR-016 / BR-018).
6. System MUST NOT create a Case (Batch 2). System MAY recommend that a Case be created later under the existing Complaint.

#### A3 — Duplicate warning overridden with justification

1. Authorized actor (Supervisor or policy-permitted role) continues create despite warning.
2. Justification MUST be provided when policy requires it.
3. New Complaint is created; “possible duplicate of” linkage MUST be recorded (BR-018 / BR-016).

#### A4 — Complaint created without Case (Batch 1 normative path)

1. Batch 1 ALWAYS registers Complaint without Case (CTO D-02).
2. Complaint remains `REGISTERED` awaiting Batch 2 Create Case.
3. SLA MUST NOT start (SLA belongs to Case per locked decision / BR-006).
4. Supervisor queue MUST flag Complaint without Case as an aging item requiring follow-up (Batch 2).

#### A5 — Integrated channel intake

1. Channel boundary supplies customer key, description payload, **Channel Message Id**, and **Request Id**.
2. Agent reviews and confirms before Aggregate creation, **or** System auto-registers when channel auto-register policy is active and validations pass.
3. Channel source MUST be recorded.
4. Idempotency MUST apply (D-03): replay of the same Channel Message Id / Request Id MUST NOT create a second Aggregate.

#### A6 — Idempotent replay / double submit

1. System receives a create with a Request Id and/or Channel Message Id already successfully accepted.
2. System MUST treat as replay: return the original Complaint outcome (same Complaint Number / id) without creating a new Aggregate.
3. System MUST write a security/operational audit of the replay detection.
4. Double submit of an in-flight Request Id MUST be protected (single winner; loser receives in-progress or original result per policy — never a second Aggregate).

### 11. Exception Flow

| ID | Condition | System Behavior |
|---|---|---|
| E1 | Customer search key empty/incomplete | MUST reject continue; require **exactly one** allowed key type with value |
| E2 | Customer not found in Master Customer | MUST reject normal Create; MAY allow UNVERIFIED only if enterprise emergency policy is configured |
| E3 | Master Customer unavailable | Strict: MUST reject create. Degraded (if configured): MAY create with `customerVerificationPending=true` without inventing Master attributes; MUST require later reconciliation when Master recovers (aging queue + maximum pending duration per policy) |
| E4 | Actor unauthorized | MUST reject; MUST write security audit attempt |
| E5 | Mandatory attributes missing/invalid | MUST reject confirm; MUST mark violating fields |
| E6 | Mandatory Audit/Timeline write fails | MUST fail the business create; MUST NOT leave an operational Aggregate without required trail |
| E7 | Hard-block duplicate policy triggered | MUST reject create (FR-003); MUST NOT create Aggregate |
| E8 | Missing Request Id (human or channel) | MUST reject create |
| E9 | Missing Channel Message Id on channel auto-register / channel-sourced create | MUST reject create |
| E10 | Replay / double-submit detected | MUST NOT create new Aggregate; follow A6 |

### 12. Validation Rules

| Validation | Rule |
|---|---|
| Customer key | **Exactly one** allowed key type MUST be supplied for lookup (BR-001) |
| CustomerId | MUST exist after successful validation, except configured UNVERIFIED mode with pending reconciliation obligation |
| Subject | MUST be present; length MUST comply with configured policy (business guidance: 1–200 characters) |
| Description | MUST be present; length MUST comply with configured policy (business guidance: 1–5000 characters) |
| Category | MUST be an active configured category |
| Channel | MUST be an active configured channel |
| Priority | MUST be one of configured priority values |
| Duplicate | Warning MUST be shown when candidate score ≥ threshold; override MUST capture justification when required |
| Authorization | Actor MUST have create entitlement for the unit (ECMP-internal) |
| Aggregate invariants | MUST NOT create Assignment or SLA on Complaint; MUST NOT create Case in Batch 1 |
| Request Id | MUST be present; MUST be unique per successful create semantics (idempotency key) |
| Channel Message Id | MUST be present for channel-sourced creates; MUST participate in idempotency |
| Recording unit override | If permitted, override MUST be role-restricted and audited (see OQ-CM-B1-006) |

### 13. Input Data

| Data | Mandatory | Source | Notes |
|---|---|---|---|
| Customer search key + type | Yes (for normal path) | Actor / channel | Exactly one of: Customer Number / Identity Number / Reference Number |
| Confirmed CustomerId | Yes (normal path) | Master Customer via FR-002 | Stored on Complaint |
| Channel | Yes | Actor / channel payload | Active catalog value |
| Category / type | Yes | Actor | Active catalog value |
| Subject | Yes | Actor | |
| Description | Yes | Actor | |
| Priority | Yes | Actor or default policy | |
| Recording unit | Yes | Default actor unit; overridable if permitted | From Organization |
| External reference | No | Actor / channel | |
| Duplicate override justification | Conditional | Actor | Required when overriding warning under policy |
| Initial attachments | No | Actor via FR-004 | Staged until commit or transfer (D-06) |
| Request Id | Yes | Client / channel | Idempotency (D-03) |
| Channel Message Id | Conditional | Integrated channel | Mandatory for channel-sourced creates (D-03) |

### 14. Output Data

| Data | Mandatory | Notes |
|---|---|---|
| Complaint Number | Yes | Unique within module |
| Complaint internal ID | Yes | System identity |
| Status | Yes | Initial `REGISTERED` |
| CustomerId | Yes (or UNVERIFIED pending flag with reconciliation obligation) | Reference only; permanent CustomerId-less state without aging is prohibited |
| `customerInactiveAtCreate` | Conditional | When Master marks inactive and create still allowed |
| CreatedAt / CreatedBy / Unit | Yes | |
| Duplicate check result summary | Yes | None / warned / overridden / blocked / redirected-to-existing |
| Idempotency outcome | Yes | accepted / replayed / rejected |
| Confirmation view model | Yes | For UI presentation |

### 15. Business Constraints

1. ECMP MUST NOT act as Customer Master SoR.
2. Complaint MUST be Aggregate Root; Complaint identity MUST NOT be reused.
3. Batch 1 Create Complaint MUST NOT create Cases (CTO D-02).
4. Assignment and SLA MUST NOT exist at Complaint level.
5. Complaint Number MUST be enterprise-unique within the module.
6. Physical deletion of Complaint MUST be prohibited; cancellation only via configured status/flow with audit.
7. Future classification config changes MUST NOT rewrite historical Complaint classification without effective-dated rules. The same effective-dated protection MUST apply to attachment allowlists, size limits, and duplicate hard-block category lists.
8. Successful create without mandatory audit MUST be impossible.
9. Idempotent replay MUST NOT create a second Aggregate (D-03).
10. UNVERIFIED creates MUST enter reconciliation aging; maximum pending duration MUST be configured; supervisor visibility MUST exist.

### 16. Security Requirements

1. Authentication and ECMP-internal authorization MUST be enforced before create.
2. Customer fields displayed during create MUST follow need-to-know and masking policy.
3. Duplicate override justification MUST be treated as sensitive operational data with restricted read access.
4. Attachments during create MUST obey FR-004 / BR-012 controls.
5. Frontend MUST call only ECMP Backend APIs; ECMP Backend SHALL call Master Customer / Notification / Audit Platform / Security control APIs.
6. Request Id / Channel Message Id MUST be treated as security-relevant operational identifiers (replay audit).

### 17. Audit Requirements

System MUST record at minimum (BR-016):

- Who (enterprise principal mapped to ECMP actor / channel principal)
- What (Complaint Created / Create Replayed / Create Redirected To Existing)
- When (trusted timestamp; clock-skew MUST be marked, not silently normalized)
- Where (organizational unit)
- Object (Complaint Number / internal ID)
- Key business attributes (category, priority, CustomerId, channel)
- Duplicate check outcome (none / warned / overridden / blocked / redirected)
- Request Id; Channel Message Id when applicable
- Evidence transfer events when A2/D-06 applies

Audit records MUST NOT contain authentication secrets. Cleartext national identity numbers MUST NOT appear in audit records (hash/mask only).

### 18. Notifications

Via Notification Platform, opt-in only:

- Supervisor of recording unit — new Complaint in queue (SHOULD)
- Creating Agent — confirmation with Complaint Number (MAY)
- Other recipients per Administrator notification matrix (MAY)

Notification delivery failure MUST NOT roll back a successfully committed Complaint. Failure MUST be recorded in an **ECMP-side notification outbox / delivery-status projection** (ADR-009 pattern). Recording solely in an externally owned Notification Platform log is insufficient when that platform is unavailable.

### 19. Acceptance Criteria

1. Given an authorized Agent and a verified CustomerId, when valid Complaint attributes and Request Id are submitted, then the system creates a Complaint with unique Complaint Number and status `REGISTERED` and does **not** create a Case.
2. Given successful create, then Complaint stores `CustomerId` only and does not persist Master Customer attributes as SoR.
3. Given successful create, then an immutable audit record and a Timeline “Complaint Created” entry exist.
4. Given missing mandatory attributes, when confirm is attempted, then create is rejected with field-level validation errors.
5. Given unauthorized actor, when create is attempted, then create is rejected and a security audit attempt is recorded.
6. Given duplicate candidates at or above threshold, when Actor confirms without required justification, then create is rejected or blocked per policy; when authorized override with justification is supplied, then create succeeds and linkage is audited.
7. Given duplicate redirect to existing Complaint with staged attachments, when create is cancelled, then staged evidence is transferred to the surviving Complaint with audit history and is not discarded.
8. Given Master Customer unavailable in Strict mode, when create is attempted, then create is rejected.
9. Given create succeeds, when Notification Platform is down, then Complaint remains created and failure is recorded in ECMP outbox/delivery-status.
10. Given a repeated Request Id after successful create, when create is retried, then no new Aggregate is created and the original Complaint outcome is returned.
11. Given channel auto-register with a repeated Channel Message Id, when replayed, then no new Aggregate is created.
12. Given Batch 1 Customer 360 minimum, when actor reaches confirm, then Customer Profile, Active Complaints, and Complaint Count are presented.

### 20. Priority

**Must**

### 21. Future Enhancement

1. Auto-classification of category/priority under configuration-first assistive rules.
2. Complaint draft persistence before final submit.
3. Administrator-calibrated duplicate score models per category.
4. Case creation paths (initial Case / add Case on existing) — **FR Batch 2**.

### 22. Security Considerations

| Area | Content |
|---|---|
| **Threats** | Unauthorized create; privilege escalation across units; duplicate Aggregate spam via retry; channel replay forgery; injection via subject/description; sensitive customer data leakage on create screen; notification side-channel on failure |
| **Mitigations** | ECMP-internal authz; Request Id + Channel Message Id idempotency with replay audit; input validation; masking; Frontend→Backend only; security audit on authz failure and replay; ECMP notification outbox |
| **Residual Risk** | Compromised channel credentials could submit valid first-seen Message Ids; residual depends on channel credential hygiene (enterprise-owned). UNVERIFIED emergency mode widens create window — constrained by aging/reconciliation MUST |

---

## 8. FR-002 Customer Search

### 1. Document ID

**FR-002**

### 2. Title

Customer Search

### 3. Description

The system SHALL enable an authorized actor to search and identify a customer by submitting **exactly one** allowed key type — Customer Number, Identity Number, or Reference Number — and SHALL resolve the result to a Master Customer `CustomerId` via Master Customer API through the ECMP Backend. ECMP MUST NOT create local customer masters and MUST NOT write back to Master Customer. Enumeration protection controls MUST apply (CTO D-04).

### 4. Business Objective

Guarantee that every Complaint is linked only to a legitimate Master Customer identity, using a simple Agent search experience, while preserving Master Customer as the single source of truth for customer profile data.

### 5. Business Rule Reference

| Rule ID | Rule Name | Usage in FR-002 |
|---|---|---|
| BR-002 | Customer Validation | Primary rule |
| BR-001 | Create Complaint | Consumer of validated CustomerId |
| BR-010 | Customer 360 View | Batch 1 minimum subset after successful identification (D-05) |
| BR-016 | Audit Trail | Validation outcome audit |
| BR-018 | Complaint History | Before/after capture on enrichment of UNVERIFIED Complaint |

### 6. Actors

- Agent / Case Handler / Supervisor (search and confirm)
- System (calls Master Customer, normalizes results, sets verification status, enforces anti-enumeration)
- Administrator (allowed key types, timeout, degradation policy)
- Enterprise Security / SOC (anti-enumeration control plane owner — D-04)
- Master Customer (external SoR)

### 7. Preconditions

1. Actor MUST be authenticated.
2. Actor MUST be authorized (ECMP-internal) to view customer data appropriate to role (sensitive fields MAY be masked).
3. Master Customer read integration MUST be defined.
4. Allowed customer key types MUST be active in configuration.
5. Anti-enumeration controls MUST be available or search MUST fail closed per security policy.

### 8. Trigger

- Before Create Complaint confirmation (FR-001)
- Actor selects **Search Customer** from intake workspace / Batch 1 Customer 360 minimum panel
- Reconciliation of a Complaint with pending verification
- Integrated channel supplies a customer key for validation

### 9. Normal Flow

1. Actor selects **exactly one** key type and enters key value.
2. System validates basic format (non-empty; pattern per key type when configured).
3. System MUST enforce Enumeration Protection (D-04) before and during search.
4. ECMP Backend SHALL call Master Customer search API (Frontend MUST NOT call Master Customer directly).
5. When exactly one definitive result is returned, System displays brief profile (including **data as of [timestamp]** freshness indicator per ADR-002) and sets candidate `CustomerId`.
6. Actor confirms match.
7. System marks `customerVerified=true` in transaction context and locks `CustomerId` for subsequent Complaint create/link.
8. System MUST present Batch 1 Customer 360 minimum (D-05): Customer Profile, Active Complaints, Complaint Count.
9. System MAY refresh read-only customer projection cache for that `CustomerId` subject to retention/PII policy (ADR-002).

### 10. Alternative Flow

#### A1 — Multiple candidates

1. System displays candidate list with minimum identity fields allowed by security policy.
2. Actor MUST select exactly one candidate.
3. Confirmation is mandatory before `CustomerId` is locked.

#### A2 — Search again

1. Actor changes key.
2. Previous confirmation context MUST be discarded.
3. System MUST NOT silently mix old and new `CustomerId` without explicit re-confirmation.

#### A3 — Inactive customer in Master Customer

1. System displays inactive status.
2. Policy determines whether Complaint create is still allowed.
3. If allowed, flag `customerInactiveAtCreate=true` MUST be recorded on the subsequent Complaint.

#### A4 — Enrichment after UNVERIFIED create

1. Previously UNVERIFIED Complaint is successfully validated later.
2. Final `CustomerId` is set.
3. History MUST record before/after customer reference (BR-018); Audit MUST record the change (BR-016).
4. System MUST trigger duplicate recheck obligation ownership under FR-003 (event-driven on verify; not an undeclared batch job inventing scope).

### 11. Exception Flow

| ID | Condition | System Behavior |
|---|---|---|
| E1 | Not found | Validation fails; normal FR-001 create MUST be rejected unless emergency UNVERIFIED mode is configured |
| E2 | Master Customer timeout/unavailable | Follow Strict vs Degraded policy aligned with BR-001 E3; limited retries MAY occur; unbounded retry loops MUST NOT occur in Agent session |
| E3 | Ambiguous results without selection | MUST NOT auto-assign `CustomerId` |
| E4 | Attempt to edit Master Customer data from ECMP | MUST reject; changes only via Master Customer processes/systems |
| E5 | More than one key type supplied | MUST reject as invalid input; MUST NOT silently choose |
| E6 | Enumeration / abuse threshold breached | MUST reject or delay per D-04 controls; MUST security-audit; MUST alert per policy |

### 12. Validation Rules

| Validation | Rule |
|---|---|
| Key presence | **Exactly one** allowed key type MUST be provided with a value |
| Key consistency | Exactly one active `CustomerId` per confirmation |
| Read-only | No Master Customer write-back from ECMP |
| Masking | Sensitive contact/identity display MUST follow role policy |
| Verification state | Verified / Unverified MUST be explicit |
| Enumeration Protection | Bulk enumeration patterns MUST be prevented (D-04) |

### 13. Input Data

| Data | Mandatory | Notes |
|---|---|---|
| Key type | Yes | Exactly one of: Customer Number / Identity Number / Reference Number |
| Key value | Yes | Non-empty; format per config |
| Actor confirmation | Yes (for lock) | Required when one or many candidates |

### 14. Output Data

| Data | Mandatory | Notes |
|---|---|---|
| CustomerId | Yes on success | From Master Customer |
| Brief profile view model | Yes on success | Read-only projection; not SoR; includes `asOf` timestamp |
| Verification status | Yes | verified / not found / ambiguous / degraded / unverified |
| Candidate list | Conditional | When multiple matches |
| Masking indicators | Conditional | Per role |
| Batch 1 Customer 360 minimum | Yes on success | Profile + Active Complaints + Complaint Count |

### 15. Business Constraints

1. Complaint MUST store only `CustomerId` as authoritative ECMP customer reference.
2. Any customer attribute copy in ECMP MUST be read-model/cache, MUST expose freshness (`asOf`), and MAY become stale; refresh and retention/PII follow ADR-002 policy.
3. Creating a “local customer” as Master substitute is prohibited.
4. Re-validation MUST NOT erase Complaint History; it MUST update reference with audit + before/after History.
5. Frontend MUST NOT call Master Customer API directly.
6. Full Customer 360 beyond D-05 minimum is out of Batch 1 scope.
7. Customer merge/retirement handling is out of Batch 1 design (D-07 / OQ-CM-B1-007).

### 16. Security Requirements

1. Identity numbers are sensitive; display MUST be minimized; audit MUST NOT store cleartext identity numbers (hash/mask only — unconditional).
2. Search results MUST be need-to-know restricted.
3. Enumeration Protection MUST apply (D-04) — see §22.
4. Authorization failures MUST be reject-closed (ECMP-internal authz).

### 16.1 Enumeration Protection (CTO D-04) — normative

The following controls MUST be enforced on FR-002 search (especially Identity Number):

| Control | Requirement | Owner |
|---|---|---|
| Rate limiting | MUST limit search attempts per principal / unit / time window | Enterprise Security (policy) + ECMP Backend (enforcement) |
| Progressive delay | MUST apply increasing delay on repeated failures / suspicious patterns | Enterprise Security + ECMP Backend |
| Abuse detection | MUST detect bulk/sequential enumeration patterns | Enterprise Security / SOC |
| Security audit | MUST write security audit for threshold breaches and blocked attempts | ECMP (BR-016 security events) + SOC sink if configured |
| Alerting | MUST alert SOC / security operations per policy when abuse thresholds are exceeded | Enterprise Security / SOC |

If the anti-enumeration dependency is unavailable, customer search MUST fail closed (no unprotected Identity Number oracle).

### 17. Audit Requirements

System MUST audit (BR-016):

- Key type used
- Key value representation: hash/mask only — **cleartext identity numbers MUST NOT be stored in audit**
- Resulting CustomerId (when found)
- Verification status
- Actor, timestamp
- Outcome: found / not found / ambiguous / degraded
- Enumeration protection outcomes: allowed / delayed / blocked / alerted

### 18. Notifications

Generally no customer notification. Internal notification to Supervisor when UNVERIFIED volume exceeds configured threshold (SHOULD). Security alerting per D-04 is mandatory for abuse thresholds.

### 19. Acceptance Criteria

1. Given a valid Customer Number that uniquely matches Master Customer, when Agent searches and confirms, then System locks that `CustomerId` with `customerVerified=true` and shows Batch 1 Customer 360 minimum.
2. Given multiple Master Customer matches, when Agent has not selected a candidate, then System MUST NOT lock a CustomerId.
3. Given no Master Customer match, when Agent attempts FR-001 normal create, then create is rejected (unless UNVERIFIED emergency policy is enabled and used).
4. Given an attempt to update Master Customer attributes from ECMP UI/API, then the operation is rejected.
5. Given Master Customer unavailable in Strict mode, when search is executed, then System returns a degradation/unavailable outcome and does not invent customer data.
6. Given Frontend requests, when customer search is performed, then only ECMP Backend is called; Master Customer is invoked only by Backend.
7. Given two key types in one request, when search is attempted, then request is rejected.
8. Given enumeration threshold breach, when search continues, then System MUST delay or block, security-audit, and alert per policy.
9. Given brief profile display, when data is from cache/projection, then `asOf` freshness is shown.

### 20. Priority

**Must**

### 21. Future Enhancement

1. Controlled fuzzy match with configurable score thresholds.
2. Consumption of digital identity / biometric verification results from external identity services.
3. Read-only watchlist / special-attention flags from Master Customer.
4. Customer merge/retirement reaction (v1.2 — OQ-CM-B1-007).

### 22. Security Considerations

| Area | Content |
|---|---|
| **Threats** | National-ID confirm-or-deny oracle; credential stuffing / bulk enumeration by authenticated agents; cache/PII leakage; inference via timing; cleartext ID in logs/audit |
| **Mitigations** | D-04 MUST controls (rate limit, progressive delay, abuse detection, security audit, alerting) with declared owners; fail closed if controls unavailable; unconditional audit masking; need-to-know result fields; ECMP-internal authz |
| **Residual Risk** | Determined attacker with many distinct authorized principals may still distribute attempts below per-principal thresholds — residual accepted only with SOC alerting and enterprise identity lifecycle controls |

---

## 9. FR-003 Duplicate Complaint Detection

### 1. Document ID

**FR-003**

### 2. Title

Duplicate Complaint Detection

### 3. Description

The system SHALL detect potential duplicate Complaints before final Create Complaint confirmation by comparing the candidate intake (same `CustomerId` and/or similar attributes within a configured time window) against existing Complaints, present warnings with actionable options limited to Batch 1, and record all decisions. Default behavior is **warn + justify**, not silent reject, except where category policy defines hard block.

Per CTO D-02, Batch 1 outcomes are limited to: **detect, warn, recommend, and link to existing Complaint**. The system MUST NOT create a Case from this FR.

### 4. Business Objective

Prevent duplicate Complaint Aggregates for substantially the same customer issue, recommend continuing on an existing Complaint (No Duplicate Work), preserve full decision traceability, and defer Case creation to Batch 2.

### 5. Business Rule Reference

| Rule ID | Rule Name | Usage in FR-003 |
|---|---|---|
| BR-014 | Duplicate Complaint | Primary rule |
| BR-003 | Complaint Search | Underlying search/index capability for candidates |
| BR-001 | Create Complaint | Gate before confirm |
| BR-010 | Customer 360 View | Batch 1 minimum context (Active Complaints / counts) |
| BR-016 | Audit Trail | Warn / override / link / redirect decisions |
| BR-018 | Complaint History | Possible-duplicate / related linkages |

### 6. Actors

- Agent (review candidates, choose action)
- Supervisor (override with justification when required)
- System (scoring and candidate retrieval)
- Administrator (thresholds, windows, hard-block category policies)

### 7. Preconditions

1. `CustomerId` is identified, or searchable pending key context exists (defined as the exactly-one key type + value used for UNVERIFIED pending correlation, retained for reconciliation).
2. Complaint search/index capability is available (BR-003), or degradation mode is defined.
3. Duplicate detection policy (threshold, time window, compared fields) is active.

### 8. Trigger

- Automatically before Create Complaint confirmation (FR-001)
- Manual “Check Duplicate” action by actor
- Recheck when an UNVERIFIED Complaint becomes verified (event-driven obligation owned with FR-002 A4; MUST enqueue review work item)

### 9. Normal Flow

1. System searches candidates using `CustomerId` + configured time window + category/similarity attributes (index semantics: Batch 1 create path SHOULD treat index update as part of create visibility rules — see §14; degradation on unavailability or NFR timeout applies).
2. System computes candidate scores, applies candidate result cap and timeout per NFR budget, and filters by threshold.
3. System presents candidate list including status and open indicators (where authorized). For CLOSED candidates, System MUST NOT offer actions that imply Case create; actor MAY open/view existing Complaint and link/recommend only.
4. Actor selects one Batch 1 outcome:
   - Cancel create and open / continue on existing Complaint (link/redirect), **or**
   - Continue create with justification (when permitted), **or**
   - Acknowledge recommendation to handle under existing Complaint without creating Case (recommend-only).
5. System records decision in Audit and History.
6. System MUST NOT create a Case.

### 10. Alternative Flow

#### A1 — False positive override

1. Authorized actor overrides with justification.
2. New Complaint is created and marked reviewed/possible-duplicate-linked as configured.
3. Override MUST be auditable.

#### A2 — Business relate / non-destructive link

1. Supervisor links related/duplicate relationship without hard-deleting either Aggregate.
2. Work continues on designated survivor Complaint.
3. History of both Aggregates MUST remain (No Information Lost).
4. If redirect cancels an in-progress create with staged evidence, evidence MUST transfer to surviving Complaint (D-06).

#### A3 — Cross-unit duplicate candidate

1. Candidates outside actor unit are shown only if authorization allows.
2. Coordination/escalation follows BR-007 if needed (out of Batch 1 execution scope).
3. Uniform authorized-empty behavior MUST apply when candidates are not visible (anti-inference).

#### A4 — No candidates above threshold

1. System records “no duplicate warning”.
2. Create Complaint proceeds without override justification.

### 11. Exception Flow

| ID | Condition | System Behavior |
|---|---|---|
| E1 | Detection unavailable (index down) or NFR timeout | Create MAY proceed with `duplicateCheckDegraded=true`; MUST create a later-review work item owned by Supervisor queue |
| E2 | Override without required justification | MUST reject continue |
| E3 | Hard-block policy for category | MUST prevent new Complaint create |
| E4 | Actor lacks scope to see a candidate | Candidate MUST NOT be leaked; uniform authorized-empty behavior MUST apply |
| E5 | Actor attempts “Add Case” / Case create action | MUST reject in Batch 1; MAY show recommendation only |

### 12. Validation Rules

| Validation | Rule |
|---|---|
| Threshold | Candidate score ≥ configured threshold MUST raise warning |
| Time window | MUST use configured window; inverted/invalid windows MUST be rejected at config level |
| Compared fields | Only configured fields MAY contribute to score |
| Justification | Minimum length/content MUST apply when override is required (configured value — OQ-CM-B1-008) |
| Decision capture | Actor decision MUST be one of allowed Batch 1 actions (detect/warn/recommend/link — no Case create) |
| No silent drop | System MUST NOT discard intake without actor-visible outcome |
| Candidate cap / timeout | MUST respect configured NFR candidate cap and timeout |
| CLOSED Complaint | MUST NOT offer Case create; link/open/recommend only |

### 13. Input Data

| Data | Mandatory | Notes |
|---|---|---|
| CustomerId (or pending key context) | Yes | Primary correlation key; pending key context = exactly-one key type + value retained for UNVERIFIED |
| Candidate category / subject / channel | Conditional | From FR-001 draft attributes when available |
| Policy version / threshold | Yes (system) | Active duplicate policy |
| Actor decision | Yes when warned | open/link existing / override / recommend-only |
| Override justification | Conditional | Required by policy |

### 14. Output Data

| Data | Mandatory | Notes |
|---|---|---|
| Candidate list | Yes (may be empty) | Scoped by authorization; uniform empty when denied |
| Score per candidate | Yes when candidates exist | |
| Warning flag | Yes | true/false |
| Decision code | Yes when warned | link_existing / override / recommend_only / blocked |
| Recommendation | Conditional | e.g., “Create Case under existing Complaint in Batch 2” |
| Linkage record | Conditional | possible-duplicate / related |
| Degraded flag | Conditional | When check could not run fully |
| Later-review work item id | Conditional | When degraded |

### 15. Business Constraints

1. System MUST NOT silently drop a Complaint intake.
2. System MUST NOT hard-delete a Complaint because it is considered duplicate.
3. Preferred business outcome remains new Case on existing Complaint — **recommended only in Batch 1**; Case create is Batch 2 (D-02).
4. All duplicate decisions MUST be traceable.
5. Duplicate search results remain authorization-scoped with MUST-level anti-inference uniformity.
6. Complaint search index MUST be represented in logical persistence mapping; create-path visibility rules MUST be stated (synchronous visibility for Batch 1 preferred; if asynchronous, lag MUST be covered by concurrency/idempotency controls).

### 16. Security Requirements

1. Candidate visibility MUST enforce org/role scope.
2. Override justifications are sensitive and read-restricted.
3. Detection APIs are Backend-only for Frontend clients.
4. Anti-inference uniform-empty behavior MUST apply (E4).

### 17. Audit Requirements

System MUST audit:

- DuplicateWarned
- DuplicateOverridden (with justification reference)
- DuplicateLinked / Related
- DuplicateRedirectedToExisting
- DuplicateRecommendedExisting
- DuplicateCheckDegraded
- DuplicateLaterReviewEnqueued

Audit event `ResolvedAsCaseOnExisting` is **removed from Batch 1** (D-02).

### 18. Notifications

- Supervisor MAY be notified on frequent overrides or hard-block attempts (configuration).
- Supervisor MUST be notifiable for later-review work items from degraded checks.
- No customer notification for detection itself.

### 19. Acceptance Criteria

1. Given same CustomerId and an open Complaint within the configured window matching category threshold, when Agent attempts create confirm, then a duplicate warning with candidates is shown.
2. Given a warning, when Agent chooses open/link existing, then no new Complaint Aggregate is created and no Case is created.
3. Given a warning requiring justification, when Agent continues without justification, then create is rejected.
4. Given authorized override with justification, when create proceeds, then Complaint is created and possible-duplicate linkage plus audit exist.
5. Given hard-block category policy, when duplicate threshold is met, then create is rejected.
6. Given search index unavailable, when create proceeds under degradation policy, then `duplicateCheckDegraded=true` is recorded and a later-review work item exists.
7. Given candidates outside actor authorization scope, when detection runs, then unauthorized candidates are not disclosed and response shape is uniform.
8. Given any Batch 1 duplicate flow, when completed, then no Case has been created by FR-003.

### 20. Priority

**Must**

### 21. Future Enhancement

1. Controlled text-similarity models with Administrator calibration.
2. Golden Complaint selection rules for related-link resolution.
3. Continuous post-create duplicate surveillance beyond verify-event recheck.
4. **Add Case on existing Complaint** as executable outcome — Batch 2.

### 22. Security Considerations

| Area | Content |
|---|---|
| **Threats** | Cross-unit inference via score/result-shape side channels; override justification leakage; degraded-mode bypass used to spam duplicates; unauthorized candidate enumeration |
| **Mitigations** | MUST uniform authorized-empty; authorization-scoped candidates; sensitive justification ACL; degraded mode creates mandatory later-review work item; Backend-only APIs; candidate cap/timeout |
| **Residual Risk** | Timing side channels under load may remain partially observable — accepted with uniform payloads and monitoring; full elimination out of Batch 1 |

---

## 10. FR-004 Attachment Upload

### 1. Document ID

**FR-004**

### 2. Title

Attachment Upload

### 3. Description

The system SHALL allow authorized actors to upload supporting evidence (documents, photos, videos, and other allowlisted file types) and bind them to a Complaint and/or Case. The system SHALL persist attachment metadata and history, enforce type/size/security controls, prohibit physical user delete, require integrity hash, and ensure attachments remain part of the Escalation Package (No Information Lost During Escalation). Staged evidence on redirected duplicate create MUST transfer to the surviving Complaint (CTO D-06).

### 4. Business Objective

Ensure evidence captured at intake and during handling remains complete, accessible, and auditable for the full Complaint lifecycle — including after escalation to Regional or Head Office.

### 5. Business Rule Reference

| Rule ID | Rule Name | Usage in FR-004 |
|---|---|---|
| BR-012 | Attachment Management | Primary rule |
| BR-001 | Create Complaint | Optional initial evidence at registration |
| BR-016 | Audit Trail | Upload / void / supersede / sensitive access / transfer |
| BR-017 | Timeline | Attachment uploaded / transferred events |
| BR-007 | Escalation | Attachments MUST be included in Escalation Package |
| BR-010 | Customer 360 View | Attachment History visibility (full 360 out of Batch 1; history still on Complaint) |
| BR-008 | Resolution | Evidence completeness may be required later |

### 6. Actors

- Agent / Case Handler (upload)
- Supervisor (review)
- Regional / Head Office handlers (access after escalation)
- System (type/size validation; security scan orchestration; staged transfer)
- Administrator (allowlist, max size, classification catalog)
- Compliance (retention / legal hold)

### 7. Preconditions

1. Anchor object (Complaint and/or Case) MUST exist and MUST allow upload in its current status, **or** upload is performed as part of in-progress Create Complaint draft session per configured intake rules.
2. Actor MUST be authorized to upload for that anchor and classification (ECMP-internal authz).
3. File type/extension MUST be on allowlist; size MUST be within limit; bulk aggregate payload size MUST respect configured maximum.
4. Security scanning dependency MUST be available when policy requires scan-before-ACTIVE.

### 8. Trigger

- Upload during Complaint Registration (FR-001)
- Upload during handling on existing Complaint/Case
- Evidence request prior to resolution
- Channel ingest of files
- Escalation package completeness check referencing attachments
- Transfer of staged evidence on duplicate redirect (D-06)

### 9. Normal Flow

1. Actor selects file(s) and classification (customer evidence, internal evidence, official letter, etc.).
2. Actor selects anchor Complaint and optional Case.
3. System validates type, size, aggregate payload size, and filename policy.
4. System validates anchor invariant: if CaseId is present, Case MUST belong to the same Complaint Aggregate as ComplaintId.
5. System submits file to security scan when configured.
6. On success, System stores binary via enterprise storage dependency and persists metadata + storage reference + **integrity hash** with status `ACTIVE`.
7. System appends Attachment History and Timeline event.
8. System writes audit `AttachmentUploaded`.
9. Attachment appears in Complaint/Case detail (per authorization).

### 10. Alternative Flow

#### A1 — New version supersedes prior file

1. Actor uploads replacement for an existing attachment.
2. Prior version status becomes `SUPERSEDED`.
3. Prior version MUST remain accessible for audit.

#### A2 — Mandatory evidence before resolution

1. Later BR-008 checks category evidence completeness.
2. Missing required attachment blocks resolution (out of Batch 1 execution, but FR-004 MUST support the evidence store).

#### A3 — Limited bulk upload

1. Actor uploads multiple files in one action.
2. Each file MUST produce its own history/audit entry.
3. Aggregate payload size MUST not exceed configured maximum.

#### A4 — Upload during create / staged evidence / duplicate redirect (CTO D-06)

1. System MAY accept staged uploads in create session.
2. On successful FR-001 commit, staged attachments MUST bind to the new Complaint.
3. If create is cancelled because actor redirects to an existing Complaint (FR-001 A2 / FR-003), staged uploads MUST **transfer** to the surviving Complaint:
   - MUST NOT physically discard
   - MUST void-or-rebind with full audit history (void of staging token + bind/transfer events)
   - Attachment History MUST remain complete and reconstructable
4. If create is cancelled for other reasons, staged uploads MUST be **voided with reason** (not physically discarded) per policy without leaving orphan ACTIVE operational evidence.
5. Abandoned session (timeout / browser close): staged uploads MUST auto-void-with-reason after configured TTL; binaries retained per retention/legal-hold policy; MUST NOT silent erase.

### 11. Exception Flow

| ID | Condition | System Behavior |
|---|---|---|
| E1 | Illegal type/size/name/aggregate payload | MUST reject upload |
| E2 | Malware / scan failure | MUST reject; MUST security-audit the event |
| E3 | User attempts physical delete | MUST reject; void-with-reason only |
| E4 | Unauthorized access/download | MUST reject; sensitive access MUST be audited |
| E5 | Anchor Complaint/Case not uploadable (e.g., CLOSED without reopen) | MUST reject operational upload per policy |
| E6 | Storage dependency failure | MUST fail upload; MUST NOT mark ACTIVE |
| E7 | CaseId does not belong to ComplaintId | MUST reject (Aggregate boundary) |
| E8 | Post-commit bind failure after successful Complaint create | MUST leave Complaint created; MUST record failed-bind work item; MUST NOT mark orphan binary ACTIVE without metadata; compensation/retry per transaction boundary policy |

### 12. Validation Rules

| Validation | Rule |
|---|---|
| Allowlist | MIME/extension MUST be allowlisted |
| Max size | MUST not exceed configured maximum (per type if configured) |
| Aggregate payload | Bulk action total size MUST not exceed configured maximum |
| Classification | MUST be provided from configured catalog |
| Anchor | Complaint and/or Case reference MUST be valid (or valid create-session staging token) |
| Anchor membership | If CaseId present, Case MUST belong to ComplaintId |
| Scan status | When policy requires scan, status MUST be clean before `ACTIVE` |
| Filename | MUST meet safety policy (path segments, reserved characters) |
| Count limits | Bulk count MUST respect configured maximum per action |
| Integrity hash | MUST be computed and stored for ACTIVE attachments |

### 13. Input Data

| Data | Mandatory | Notes |
|---|---|---|
| File binary | Yes | |
| Classification | Yes | Configured catalog |
| Anchor ComplaintId | Conditional | Required unless staging in create session |
| Anchor CaseId | No | Optional more specific bind; membership invariant applies |
| Filename | Yes | Original name (sanitized for storage metadata) |
| Content type | Yes | Declared / detected |
| Actor | Yes | From authenticated principal |

### 14. Output Data

| Data | Mandatory | Notes |
|---|---|---|
| AttachmentId | Yes | |
| Status | Yes | ACTIVE / SUPERSEDED / VOID / REJECTED / TRANSFERRED |
| Storage reference | Yes | Not a public unauthenticated URL |
| Integrity hash | Yes | MUST |
| History entry | Yes | Including transfer/void reasons |
| Timeline event | Yes | |
| Scan result summary | Conditional | When scan enabled |

### 15. Business Constraints

1. Attachments MUST NOT be lost during escalation; documents, photos, and videos are part of Escalation Package (BR-007).
2. Attachment History is append-only for business meaning; void/supersede/transfer — not silent erase.
3. Legal hold MUST prevent void/purge where applicable.
4. Complaint closure MUST NOT delete attachments.
5. ECMP owns business metadata and access rules; binary MAY reside in enterprise storage, but business attachment remains part of Complaint Management trail.
6. No direct Frontend access to enterprise storage APIs bypassing ECMP Backend authorization.
7. Staged evidence on duplicate redirect MUST transfer to surviving Complaint (D-06).

### 16. Security Requirements

1. Malware scanning MUST be enforced when configured.
2. DLP / sensitive-content controls SHOULD apply per enterprise policy.
3. Encryption at rest is owned by storage platform; ECMP MUST not expose unauthenticated public links.
4. Internal vs customer evidence classifications MUST enforce distinct access rights.
5. Download of sensitive attachments MUST require audited access.

### 17. Audit Requirements

System MUST audit:

- AttachmentUploaded
- AttachmentSuperseded
- AttachmentVoided
- AttachmentTransferred (staging → surviving Complaint)
- AttachmentAccess (for sensitive classifications — MUST)

Audit MUST include actor, timestamp, attachment id, anchor ids, classification, integrity hash reference, and outcome.

### 18. Notifications

Optional notification to Supervisor when critical evidence is uploaded (configuration) (MAY). Notification failure MUST NOT void a successful upload. Delivery failure recording follows ECMP outbox pattern when notifications are used.

### 19. Acceptance Criteria

1. Given authorized Agent and allowlisted file within size limit, when upload is bound to a Complaint, then attachment status is `ACTIVE`, integrity hash exists, and history/timeline/audit exist.
2. Given disallowed file type or oversize file, when upload is attempted, then upload is rejected and no ACTIVE attachment is created.
3. Given malware scan failure (policy on), when upload is attempted, then upload is rejected and security audit is written.
4. Given user requests physical delete, when delete is attempted, then operation is rejected; void-with-reason remains the only business removal path.
5. Given superseding upload, when new version is ACTIVE, then prior version is `SUPERSEDED` and still retrievable for audit.
6. Given successful escalation later, when Head Office opens the Case, then previously uploaded branch attachments remain visible to authorized roles (No Information Lost).
7. Given Frontend client, when upload occurs, then only ECMP Backend attachment APIs are used.
8. Given create cancelled due to duplicate redirect with staged files, when redirect completes, then files are bound to surviving Complaint with transfer audit and are not discarded.
9. Given CaseId not belonging to ComplaintId, when upload is attempted, then upload is rejected.

### 20. Priority

**Must**

### 21. Future Enhancement

1. OCR / metadata extraction.
2. Auto-classification of document types.
3. Customer self-upload via integrated portal channel.

### 22. Security Considerations

| Area | Content |
|---|---|
| **Threats** | Malware upload; evidence tampering; unauthorized download of sensitive evidence; orphan binaries after failed bind; evidence destruction on cancel; path traversal in filenames |
| **Mitigations** | Allowlist + size + aggregate caps; malware scan; integrity hash MUST; void/transfer not delete; D-06 transfer on redirect; anchor membership invariant; audited sensitive access MUST; Backend-only storage access |
| **Residual Risk** | Storage platform compromise is outside ECMP control — residual accepted via enterprise storage controls and hash verification on read |

---

## 11. Use Case Mapping

| Use Case ID | Use Case Name | Functional Requirement |
|---|---|---|
| UC-CM-001 | Register Complaint for identified customer | FR-001 |
| UC-CM-002 | Search and confirm customer from Master Customer | FR-002 |
| UC-CM-003 | Detect and handle potential duplicate Complaint (warn / link / recommend / override) | FR-003 |
| UC-CM-004 | Upload evidence attachment to Complaint/Case | FR-004 |
| UC-CM-005 | Register Complaint with initial evidence | FR-001, FR-004 |
| UC-CM-006 | Register Complaint after duplicate warning override | FR-001, FR-003 |
| UC-CM-007 | Abandon create, link to existing Complaint, transfer staged evidence | FR-001, FR-003, FR-004 |
| UC-CM-008 | Identify customer then open Batch 1 Customer 360 minimum | FR-002 (supports FR-001; BR-010 subset D-05) |
| UC-CM-009 | Idempotent replay of create (Request Id / Channel Message Id) | FR-001 |

---

## 12. Screen Mapping

Logical screens only. **UI design is out of scope** for this FRD.

| Screen ID | Screen Name | Primary FR | Supporting FR | Notes |
|---|---|---|---|---|
| SCR-CM-001 | Create Complaint | FR-001 | FR-002, FR-003, FR-004 | Intake form + confirm; Request Id handled by client/gateway |
| SCR-CM-002 | Customer Search / Candidate Select | FR-002 | — | Exactly one key type; enumeration protections invisible but enforced |
| SCR-CM-003 | Duplicate Warning Dialog / Panel | FR-003 | FR-001 | Open/link existing / override / recommend only — **no Add Case** |
| SCR-CM-004 | Attachment Upload Panel | FR-004 | FR-001 | Usable standalone or embedded in create |
| SCR-CM-005 | Create Complaint Confirmation | FR-001 | — | Displays Complaint Number / status; no Case Number in Batch 1 |
| SCR-CM-006 | Customer Brief Profile + Batch 1 360 Minimum | FR-002 | FR-001 | Profile + Active Complaints + Complaint Count; `asOf` indicator |

Existing product screen UX-SCR-001 (Case Detail Workspace) is **not** redefined here; Batch 1 intake screens are additive logical inventory pending UI UX Spec.

---

## 13. API Mapping

Logical ECMP Backend API capabilities required by Batch 1. **Payload design and OpenAPI authorship are out of scope** for this FRD. Existing catalog IDs are referenced where aligned; gaps are marked **Planned**. Catalog ID collisions for `API-390` / `API-392` MUST be resolved in `07 API Catalog` before treating those IDs as stable automation anchors (cite path+method until remapped).

| FR | Logical API Capability | Existing / Planned Catalog Reference | Consumer | Downstream Enterprise API |
|---|---|---|---|---|
| FR-001 | Create Complaint (idempotent) | Existing alignment: `POST /api/v1/complaints` (catalog ID remap pending); requires Request Id; Channel Message Id when channel-sourced | Frontend → ECMP Backend | Notification (opt-in); Audit Platform (optional copy) |
| FR-001 | Get Complaint confirmation/detail | Existing alignment: `GET /api/v1/complaints/{complaintId}` (catalog ID remap pending) | Frontend → ECMP Backend | — |
| FR-002 | Search Customer by key | **Planned** ECMP Backend customer-search facade over Master Customer | Frontend → ECMP Backend | Master Customer Search/Get; Enterprise Security anti-enumeration |
| FR-002 | Confirm / lock CustomerId in session/context | **Planned** (may be embedded in create draft context) | Frontend → ECMP Backend | Master Customer Get-by-id |
| FR-002 | Batch 1 Customer 360 minimum | **Planned** (profile + active complaints + count) | Frontend → ECMP Backend | Master Customer profile read; ECMP Complaint reads |
| FR-003 | Check duplicate candidates | **Planned** (dedicated or create pre-check). May leverage complaint search substrate | Frontend → ECMP Backend | — |
| FR-003 | Record duplicate decision / linkage | **Planned** (or embedded in create command) | Frontend → ECMP Backend | — |
| FR-004 | Upload attachment | Existing: `API-323` `POST /api/v1/attachments` | Frontend → ECMP Backend | Enterprise Storage; optional malware scan service |
| FR-004 | Transfer staged attachments to surviving Complaint | **Planned** | ECMP Backend internal / Frontend-triggered redirect flow | Enterprise Storage (rebind metadata) |
| FR-004 | List attachments for Complaint | Existing: `API-387` | Frontend → ECMP Backend | — |
| FR-004 | Get metadata / download | Existing: `API-324`, `API-325` | Frontend → ECMP Backend | Enterprise Storage |
| FR-004 | Logical void | Existing: `API-326` (logical delete semantics MUST match BR-012 void rules) | Frontend → ECMP Backend | — |

### Integration constraints (normative)

1. Frontend MUST call ECMP Backend only.
2. ECMP Backend SHALL call Master Customer, Notification, Storage, Calendar (later), Audit Platform, and Enterprise Security anti-enumeration APIs as applicable.
3. No direct database access to any external enterprise system.
4. Authorization decisions remain ECMP-internal (ADR-008 / ADR-014).

---

## 14. Database Mapping

Logical persistence mapping only. **Physical schema, SQL, and migration design are out of scope.**

| FR | Logical Entity / Store | Ownership | Notes |
|---|---|---|---|
| FR-001 | Complaint (Aggregate Root) | ECMP | Number, status, CustomerId, classification, channel, subject, description, priority, unit, timestamps, verification flags, `customerInactiveAtCreate` |
| FR-001 | Idempotency record | ECMP | Request Id; Channel Message Id; outcome Complaint id; status |
| FR-001 | Complaint History (initial snapshot / linkages) | ECMP | BR-018 |
| FR-001 | Timeline entry | ECMP | BR-017 |
| FR-001 | Audit record | ECMP (+ optional Audit Platform copy) | BR-016; mandatory with create; retention per Compliance (OQ-CM-B1-009) |
| FR-001 | Notification outbox / delivery-status | ECMP | ADR-009 pattern |
| FR-001 | Supervisor aging / later-review work item | ECMP | No-Case aging; degraded duplicate review; failed attachment bind |
| FR-002 | Customer read-model / cache (optional) | ECMP projection | Non-SoR; `asOf`; retention/PII policy |
| FR-002 | Customer validation audit | ECMP | Outcome of search/confirm; hashed keys |
| FR-002 | Pending key context | ECMP | Exactly-one key type + value for UNVERIFIED reconciliation |
| FR-003 | Complaint search index | ECMP | BR-003 substrate; create visibility rules |
| FR-003 | Duplicate candidate evaluation result | ECMP (transient or stored decision) | Score, threshold, policy version |
| FR-003 | Duplicate / related linkage | ECMP | Possible-duplicate relationships |
| FR-004 | Attachment metadata | ECMP | Classification, status, **integrity hash**, anchors |
| FR-004 | Attachment binary | Enterprise Storage dependency | Referenced by storage key |
| FR-004 | Attachment History | ECMP | Append-only including transfer/void |
| FR-004 | Staging token / transfer record | ECMP | D-06 |

### Transaction boundary (logical, Batch 1)

- **MUST be atomic with create:** Complaint persist + mandatory Audit + Timeline + idempotency commit.
- **MUST bind on success path:** staged attachment metadata bind/transfer; failures after Complaint commit MUST create compensable work items (E8) — MUST NOT silently lose evidence.
- **MUST NOT require:** Notification Platform success inside the create transaction (outbox instead).

---

## 15. Business Rule Mapping

| Functional Requirement | Business Rules (BR-CM-CAT-001) |
|---|---|
| FR-001 Complaint Registration | BR-001 (primary), BR-002, BR-014, BR-016, BR-017; supporting BR-010 (subset), BR-012, BR-018 |
| FR-002 Customer Search | BR-002 (primary); supporting BR-001, BR-010 (subset), BR-016, BR-018 |
| FR-003 Duplicate Complaint Detection | BR-014 (primary), BR-003, BR-016, BR-018; supporting BR-001, BR-010 (subset) |
| FR-004 Attachment Upload | BR-012 (primary), BR-016, BR-017; supporting BR-001, BR-007, BR-008, BR-010 |

### Reverse mapping (BR → FR in Batch 1)

| Business Rule | Batch 1 FR Coverage |
|---|---|
| BR-001 Create Complaint | FR-001 (Case-create portions deferred to Batch 2) |
| BR-002 Customer Validation | FR-002 (primary), FR-001 |
| BR-003 Complaint Search | FR-003 (substrate only; standalone Complaint Search FR not in Batch 1) |
| BR-004 Create Case | **Out of Batch 1** (D-02) — Batch 2 |
| BR-012 Attachment Management | FR-004 |
| BR-014 Duplicate Complaint | FR-003 (primary), FR-001 (detect/warn/recommend/link only) |
| BR-016 Audit Trail | FR-001, FR-002, FR-003, FR-004 |
| BR-017 Timeline | FR-001, FR-004 |

---

## 16. Requirements Traceability Matrix (DM → BR → FR)

Domain Model (DM) IDs below are **logical Complaint Management Module domain entities** for Batch 1 traceability under the locked Aggregate model. They are not physical tables.

| DM ID | Domain Entity | Business Rules | Functional Requirements | Blueprint Capability Affinity |
|---|---|---|---|---|
| DM-CM-001 | Complaint (Aggregate Root) | BR-001, BR-016, BR-017, BR-018 | FR-001 | BP-001 (complaint registration & tracking) |
| DM-CM-002 | Customer Reference (`CustomerId`) | BR-002 | FR-002, FR-001 | BP-001 / BP-003 (customer context) |
| DM-CM-003 | Customer Read-Model Projection | BR-002, BR-010 | FR-002 | BP-003 (Batch 1 minimum) |
| DM-CM-004 | Duplicate Candidate / Linkage | BR-014, BR-003, BR-018 | FR-003, FR-001 | BP-001 (data quality / no duplicate work) |
| DM-CM-005 | Attachment | BR-012, BR-007 | FR-004, FR-001 | BP-001 (evidence trail) |
| DM-CM-006 | Attachment History | BR-012, BR-016 | FR-004 | BP-001 |
| DM-CM-007 | Audit Trail Record | BR-016 | FR-001, FR-002, FR-003, FR-004 | Cross-cutting |
| DM-CM-008 | Timeline Entry | BR-017 | FR-001, FR-004 | Cross-cutting |
| DM-CM-009 | Case | BR-004 | **Deferred — Batch 2** (not created in Batch 1) | BP-001 |
| DM-CM-010 | Idempotency Record | BR-001 (intake integrity) | FR-001 | BP-001 |
| DM-CM-011 | Complaint Search Index | BR-003 | FR-003 | BP-001 |
| DM-CM-012 | Notification Outbox | — (ADR-009) | FR-001 | Cross-cutting |

### Compact DM → BR → FR links (Batch 1)

```text
DM-CM-001 Complaint  →  BR-001  →  FR-001
DM-CM-002 CustomerId →  BR-002  →  FR-002 → FR-001
DM-CM-004 Duplicate  →  BR-014  →  FR-003 → FR-001
DM-CM-005 Attachment →  BR-012  →  FR-004 → FR-001
DM-CM-007 Audit      →  BR-016  →  FR-001 / FR-002 / FR-003 / FR-004
DM-CM-008 Timeline   →  BR-017  →  FR-001 / FR-004
DM-CM-010 Idempotency→  BR-001  →  FR-001
DM-CM-011 Search Idx →  BR-003  →  FR-003
```

Related consumers: `13 Test Strategy`, `26 Traceability` MUST be updated when this FRD is approved.

---

## 17. Out of Scope

This FRD Batch 1 does **not** include:

| Area | Status |
|---|---|
| Database physical design / SQL / migrations | Separate document |
| API payload / OpenAPI contract authorship | Separate catalog change |
| Sequence diagrams | Separate design artifact |
| UI visual design / wireframes | `12 UI UX Spec` |
| Backend / Frontend code | Implementation stream |
| **Case creation (initial Case, Add Case on existing, any Case FR)** | **FR Batch 2 (CTO D-02)** |
| Assignment, SLA, Escalation, Resolution, Closure, Reopen | Later FRD batches |
| Full Customer 360 beyond D-05 minimum | Later FRD / CRM FRD |
| Customer merge / retirement reaction design | **v1.2 (CTO D-07 / OQ-CM-B1-007)** |
| Direct enterprise DB access | Forbidden by architecture |
| Customer Master write-back | Forbidden (ADR-002 / BR-002) |

---

## 18. Open Questions

| ID | Question | Impact | Suggested Owner | Target |
|---|---|---|---|---|
| OQ-CM-B1-001 | DEC remapping date: when does BR-CM-CAT-001 replace Sprint delivery SoT for implementation? | ID namespace / implementation sequencing | Business Owner + Architecture Board | Parallel to v1.1 approval |
| OQ-CM-B1-002 | Exact Master Customer search API fields and identity-number masking contract | FR-002 audit/display | Integration Lead + Security | v1.1 close |
| OQ-CM-B1-003 | Default duplicate threshold, window (days), and hard-block category list | FR-003 behavior | Operations Lead + Administrator | v1.1 close |
| OQ-CM-B1-004 | Production policy for when Batch 2 Case create becomes mandatory after REGISTERED | Aging KPI / supervisor queue SLAs | Domain PO ECMF | Batch 2 |
| OQ-CM-B1-005 | Attachment max sizes per media type, aggregate payload max, and mandatory malware scan environments | FR-004 validation | Security + Administrator | v1.1 close |
| OQ-CM-B1-006 | Who may override recording unit; multi-unit actor behaviour; mandatory audit fields | FR-001 validation | Operations Lead | v1.1 |
| OQ-CM-B1-007 | How should ECMP react to upstream Customer merge / retirement / superseded CustomerId? | 360, duplicate correlation, history | Integration Lead + Architect | **v1.2 (CTO D-07)** — do not design in Batch 1 |
| OQ-CM-B1-008 | Minimum override justification length/content | FR-003 validation | Operations Lead | v1.1 |
| OQ-CM-B1-009 | Audit retention period, immutability enforcement, legal-hold interaction for audit records | BR-016 / Compliance | Compliance + Security | v1.1 |
| OQ-CM-B1-010 | Complaint Number format, sequencing, gapless policy, reset rules, generator-failure behaviour | FR-001 | Operations Lead + Administrator | v1.1 |
| OQ-CM-B1-011 | Create-path search index: synchronous visibility vs asynchronous with explicit lag SLA | FR-003 / M-02 | Solution Architect | v1.1 |
| OQ-CM-B1-012 | What is the Request Id / Channel Message Id lifetime (TTL / retention window) for idempotency replay semantics after successful create? | FR-001 / DM-CM-010 — **Architecture Decision candidate** | Solution Architect + Security | Implementation design (no Batch 1 FR scope change) |
| OQ-CM-B1-013 | Who is the Request Id generation authority (client, gateway, or ECMP Backend) for human and channel paths? | FR-001 / SCR-CM-001 — **Architecture Decision candidate** | Solution Architect + Security | Implementation design (no Batch 1 FR scope change) |
| OQ-CM-B1-014 | What are the normative semantics of attachment status `TRANSFERRED` (terminal on source vs transient; relationship to `ACTIVE` on surviving Complaint)? | FR-004 §14 / A4.3 — **Architecture Decision candidate** | Solution Architect | Implementation design (no Batch 1 FR scope change) |

### 18.1 Architecture Decision Candidates (from D-08 / Delta Review)

The following are **implementation-level** decisions parked at LOCK. They MUST NOT expand Batch 1 functional scope and MUST NOT redesign FR-001…FR-004. Resolve via ADR / DEC before or during detailed design:

| Candidate | Linked OQ | Topic |
|---|---|---|
| ADR/DEC — Idempotency key lifetime | OQ-CM-B1-012 | Request Id / Channel Message Id TTL and post-expiry replay outcome |
| ADR/DEC — Idempotency key provenance | OQ-CM-B1-013 | Request Id generation authority and trust model |
| ADR/DEC — Attachment transfer state | OQ-CM-B1-014 | `TRANSFERRED` status semantics vs void/bind events and `ACTIVE` on target |

---

## 19. Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-29 | Business Analyst (FRD Batch 1) | Initial Draft v1.0 — FR-001…FR-004 + mappings + RTM |
| 1.1 | 2026-07-29 | Requirements Manager / Solution Architect | Draft v1.1 per GOV-RP-FRD-CM-001 + CTO Decisions D-01…D-07; Security Considerations added to all FRs; Case create removed from Batch 1; idempotency + enumeration MUST + 360 minimum + evidence transfer |
| 1.1 LOCKED | 2026-07-29 | Requirements Manager / CTO | CTO Decision D-08: LOCK after GOV-DELTA-FRD-CM-001; OQ-CM-B1-012…014 + ADR candidates; no FR redesign; no Batch 1 scope change |

---

## Architecture Review Checklist

- [x] Scope limited to Complaint Management Module Batch 1
- [x] Locked Aggregate / CustomerId / Working Day / No Information Lost decisions respected
- [x] All FR BR references exist in BR-CM-CAT-001 (no invented BRs)
- [x] External systems treated as API dependencies only; Authorization is ECMP-internal
- [x] Frontend → ECMP Backend → Enterprise APIs path explicit
- [x] Traceability DM → BR → FR complete for Batch 1
- [x] Out-of-scope design artifacts not embedded (DB/OpenAPI/UI/code)
- [x] CTO Decisions D-01…D-08 applied
- [x] Security Considerations present on FR-001…FR-004
- [x] Claude Delta Review (GOV-DELTA-FRD-CM-001) — Completed
- [x] CTO Approval → LOCKED (D-08)

---

## 20. Revision Summary (v1.1)

### 20.1 Findings Resolved

| Finding | Resolution in v1.1 |
|---|---|
| C-01 | D-01: replaced “implementation-ready” with **Architecture Baseline Pending Governance Approval**; Draft status retained |
| C-02 | Authorization removed from external dependency table; §4.1 declares ECMP-internal authz |
| C-03 / D-02 | All Case-create outcomes removed from Batch 1; FR-003 limited to detect/warn/recommend/link; audit `ResolvedAsCaseOnExisting` removed |
| C-04 | Customer key cardinality aligned to **exactly one** across flows, validations, and exceptions |
| C-05 / D-03 | Idempotency in Batch 1: Request Id, Channel Message Id, Replay Detection, Double Submit Protection (human + channel) |
| C-06 / D-04 | Enumeration Protection raised to **MUST** with rate limiting, progressive delay, abuse detection, security audit, alerting; owners declared |
| M-01 | Reconciliation obligation restored; pending key context defined; aging/supervisor visibility required |
| M-02 | Complaint search index added to §14; OQ-CM-B1-011 for sync vs async |
| M-03 | Later-review / enrichment / verify-recheck ownership assigned via work items / FR-002 A4 / FR-003 triggers |
| M-04 | `asOf` freshness + ADR-002 retention/PII acknowledgment in FR-002 |
| M-05 / D-06 | Discard removed; staged evidence MUST transfer on redirect; void-with-reason otherwise; abandoned TTL void |
| M-06 | Anchor membership invariant: Case MUST belong to Complaint |
| M-07 | CLOSED candidates: no Case-implying actions; open/link/recommend only |
| M-08 / D-05 | Batch 1 Customer 360 minimum: Profile + Active Complaints + Complaint Count; full 360 out of scope |
| M-09 | Integrity hash MUST; sensitive access audit MUST |
| M-10 | Anti-inference uniform-empty MUST |
| M-11 | Logical transaction boundary stated in §14 |
| M-12 | ECMP notification outbox / delivery-status required (ADR-009) |
| M-13 | Candidate cap + timeout + NFR degradation path referenced |
| M-15 | Catalog collision called out; cite path+method until remap |
| M-16 | KPI Impact section + supervisor no-Case aging restored |
| m-01 | Draft v1.1 + non-normative-until-approval language |
| m-04 | Named flag `customerInactiveAtCreate` |
| m-06 | Clock-skew mark + no auth secrets in audit |
| m-07 | Aggregate payload size validation |
| m-08 | Effective-dated protection extended to attachment/duplicate config |
| m-09 | Explicit link to Test Strategy / Traceability |
| m-10 | Before/after History on enrichment |

### 20.2 Findings Deferred

| Finding | Disposition |
|---|---|
| M-17 / D-07 / m-12 (merge/deceased/dormant full matrix) | **Deferred to v1.2** via OQ-CM-B1-007 (no design in Batch 1). Inactive-only remains |
| M-14 | Retention period values → OQ-CM-B1-009 (Compliance decision); structure referenced |
| m-02 | Recording unit override policy → OQ-CM-B1-006 |
| m-03 | Complaint Number format policy → OQ-CM-B1-010 |
| m-05 | Justification minimum value → OQ-CM-B1-008 |
| m-11 | Concurrency deep design → covered partially by idempotency + OQ-CM-B1-011 |
| m-13 | Durable ID tooling rename → remains governed by OQ-CM-B1-001 / namespace note (no FR renumber) |

### 20.3 Open Questions

See §18: OQ-CM-B1-001 … OQ-CM-B1-014. **Customer Merge is explicitly OQ-CM-B1-007 for v1.2 (D-07).** **D-08 parks OQ-CM-B1-012…014 as Architecture Decision candidates** (Request Id TTL, Request Id generation authority, TRANSFERRED semantics) without expanding Batch 1 scope.

### 20.4 Sections Changed

| Section | Change type |
|---|---|
| Header / Document Control | Version 1.1; Draft v1.1; D-01 language; CTO decision table |
| §2 Purpose and Scope | Readiness wording; Case create and full 360 out of scope |
| §3 Locked Decisions | Clarifying note: Multi-Case locked; Case create deferred Batch 2 |
| §4 External Dependencies | Authorization removed; anti-enumeration dependency + owners; §4.1 internal authz |
| §5 Actors | Security/SOC; Case Handler Batch 1 limit |
| §6 FR Catalog + KPI | Case create removed from supporting BR-004; KPI Impact added |
| §7 FR-001 | Idempotency; no Case create; 360 minimum; evidence transfer A2; Security Considerations; ACs |
| §8 FR-002 | Exactly one key; D-04 enumeration MUST; 360 minimum; asOf; Security Considerations |
| §9 FR-003 | D-02 outcomes only; anti-inference MUST; no Case audit event; Security Considerations |
| §10 FR-004 | D-06 transfer; no discard; hash MUST; anchor invariant; Security Considerations |
| §11–§16 | UC/Screen/API/DB/BR/RTM updated for Batch 1 constraints + new DM entities |
| §17–§18 | Out of scope + new OQs including merge v1.2 |
| §19–§20 | History + this Revision Summary |
| All FRs | New **§22 Security Considerations** (Threats / Mitigations / Residual Risk) |
| LOCK close (D-08) | Status → LOCKED; OQ-CM-B1-012…014 + §18.1 ADR candidates; checklist gates closed; no FR body redesign |

### 20.5 LOCK Gate Closure (D-08)

| Check | Status |
|---|---|
| Status | **LOCKED** |
| Claude Delta Review (GOV-DELTA-FRD-CM-001) | **Completed** |
| CTO Approval | **Completed (D-08)** |
| CTO Decisions D-01…D-08 applied | Yes |
| Locked Architecture unchanged | Yes |
| FR numbering unchanged (FR-001…FR-004) | Yes |
| No new Business Rules invented | Yes |
| No Batch 1 scope expansion (Case create removed, not added) | Yes |
| No locked ADR modification | Yes |
| No FR redesign at LOCK | Yes |
| Delta Review minor ambiguities parked as OQ-CM-B1-012…014 / ADR candidates | Yes |
| Security Considerations on every FR | Yes |
| Source of Truth for Batch 1 implementation | **Yes** |

---

*End of FRD-CM-001 v1.1 LOCKED — ECMP Complaint Management Module FRD Batch 1. Source of Truth for implementation.*
