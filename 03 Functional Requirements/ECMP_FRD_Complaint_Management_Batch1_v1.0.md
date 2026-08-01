# ECMP Functional Requirements Document — Complaint Management Module Batch 1

| Field | Value |
|---|---|
| Document ID | FRD-CM-001 |
| Title | Complaint Management Module — FRD Batch 1 |
| Version | 1.0 |
| Status | Draft v1.0 |
| Owner | Business Analyst / Domain PO ECMF |
| Reviewer | Solution Architect, Operations Lead, Compliance |
| Approver | Business Owner / Architecture Board |
| Module | Complaint Management Module only |
| Last Review | 2026-07-29 |
| Next Review | 2026-10-29 |
| Related BR Catalog | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001) |
| Related ADRs | ADR-014 (Enterprise Business Module), ADR-015 (Enterprise Identity Contract), ADR-002 (Customer Master non-SoR) |

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

---

## 1. Document Control

### 1.1 Namespace Clarification

This FRD defines **Complaint Aggregate** functional requirements for the Complaint Management Module target model (BR-CM-CAT-001).

| Namespace | Document | Meaning of BR-001 / FR-001 |
|---|---|---|
| **This FRD (normative for Batch 1)** | FRD-CM-001 + BR-CM-CAT-001 | FR-001 = Complaint Registration; BR-001 = Create Complaint |
| Delivery Sprint SoT (separate) | FRD-001 / BR-DOC-001 | FR-001 = Create Case (case-centric slice); BR-001 = workflow transition rule |

Until a formal DEC remaps delivery SoT to the Complaint Aggregate model, **implementation of this Batch 1 FRD MUST NOT silently overwrite Sprint delivery IDs**. Traceability in this document uses **BR-CM-CAT-001 rule IDs** and **FRD-CM-001 FR IDs**.

### 1.2 Quality Rules Applied

- RFC-2119 keywords: **MUST**, **SHALL**, **SHOULD**, **MAY**
- No inventing Business Rules — all BR references are from BR-CM-CAT-001
- No Out-of-Scope capabilities
- API-first integration; Frontend → ECMP Backend → Enterprise APIs only
- ECMP is **not** Customer Master System of Record

---

## 2. Purpose and Scope

### 2.1 Purpose

Provide an **implementation-ready** Functional Requirements baseline for intake capabilities of the Complaint Management Module:

1. Register a Complaint Aggregate Root
2. Search and validate Customer via Master Customer
3. Detect potential duplicate Complaints
4. Upload supporting attachments

### 2.2 In Scope (Batch 1 only)

| FR ID | Title |
|---|---|
| FR-001 | Complaint Registration |
| FR-002 | Customer Search |
| FR-003 | Duplicate Complaint Detection |
| FR-004 | Attachment Upload |

### 2.3 Explicitly Out of Scope (this Batch)

Assignment, Working Day SLA calculation, Escalation, Resolution, Closure, Reopen, Customer 360 full view, Communication History, Comment Management, Complaint Search as a standalone FR, Dashboard KPI, Reporting, Case creation as a standalone FR (except where BR-001 optionally triggers Create Case per policy), UI visual design, OpenAPI payload design, database physical design, sequence diagrams, backend/frontend code.

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

---

## 4. External Dependencies

ECMP integrates with the following **external enterprise systems via APIs only**. ECMP MUST NOT assume direct database access.

| Dependency | Role in Batch 1 |
|---|---|
| Identity | Principal identity for actor attribution |
| Authentication | Prove actor identity before any FR |
| Authorization | ECMP module authorization for complaint/customer/attachment actions |
| Organization | Unit/branch context of registering actor |
| Master Customer | Customer lookup and profile read for FR-002 / FR-001 |
| Notification | Opt-in notifications after successful registration / critical attachment events |
| Calendar | Not required for Batch 1 create/search/duplicate/upload; required later for Case SLA (BR-006) |
| Audit Platform | Optional sink for audit copies; ECMP MUST still write mandatory module audit (BR-016) |

---

## 5. Actors

| Actor | Batch 1 Relevance |
|---|---|
| Agent / Petugas Frontline | Primary actor for FR-001…FR-004 |
| Supervisor Unit | May create Complaint; may override duplicate warning with justification (FR-003) |
| Case Handler | May upload attachments on existing Complaint/Case (FR-004) |
| Administrator | Configures categories, channels, attachment policy, duplicate thresholds |
| System | Generates Complaint Number, runs duplicate scoring, enforces validations, writes audit/timeline |
| Customer | Source of complaint; does not log into this module in Batch 1 scope |
| Master Customer (external) | Authoritative customer data source |

---

## 6. FR Catalog Summary

| FR ID | Title | Priority | Primary BR References |
|---|---|---|---|
| FR-001 | Complaint Registration | Must | BR-001, BR-002, BR-014, BR-016, BR-017 |
| FR-002 | Customer Search | Must | BR-002 |
| FR-003 | Duplicate Complaint Detection | Must | BR-014, BR-003, BR-016 |
| FR-004 | Attachment Upload | Must | BR-012, BR-016, BR-017 |

Supporting BR references used within flows (not separate Batch 1 FRs): BR-004 (optional initial Case), BR-010 (Customer 360 access during create), BR-011 / BR-013 (optional initial notes/communication), BR-018 (duplicate linkage history).

---

## 7. FR-001 Complaint Registration

### 1. Document ID

**FR-001**

### 2. Title

Complaint Registration

### 3. Description

The system SHALL enable an authorized actor to register a new **Complaint** as Aggregate Root after the customer has been identified via Master Customer. The Complaint SHALL store only `CustomerId` as the customer reference, generate a unique Complaint Number, set initial status `REGISTERED`, and persist mandatory audit and timeline records. Assignment and SLA MUST NOT be created at Complaint level.

### 4. Business Objective

Ensure every customer complaint enters ECMP as a valid, uniquely identified, fully auditable Complaint Aggregate that is ready for subsequent Case work — without duplicating Master Customer data and without losing intake evidence.

### 5. Business Rule Reference

| Rule ID | Rule Name | Usage in FR-001 |
|---|---|---|
| BR-001 | Create Complaint | Primary rule |
| BR-002 | Customer Validation | Mandatory prerequisite |
| BR-014 | Duplicate Complaint | Mandatory pre-confirm check |
| BR-016 | Audit Trail | Mandatory on successful create |
| BR-017 | Timeline | Mandatory “Complaint Created” entry |
| BR-010 | Customer 360 View | SHOULD be available before confirm |
| BR-004 | Create Case | MAY create initial Case if policy requires |
| BR-012 | Attachment Management | MAY attach evidence during create |
| BR-018 | Complaint History | Records possible-duplicate linkage / initial snapshot |

### 6. Actors

- Agent / Petugas Frontline (primary)
- Supervisor Unit
- System
- Administrator (configuration of category, channel, priority defaults, “initial Case required” policy)

### 7. Preconditions

1. Actor MUST be authenticated via Enterprise Authentication / Identity.
2. Actor MUST hold ECMP authorization to create Complaint for the relevant organizational unit.
3. Actor’s organization/unit context MUST be resolvable from Organization dependency.
4. Master Customer integration MUST be available, or an Administrator-configured degradation mode MUST be active (see Exception Flow).
5. Active reference data MUST exist for: intake channel, complaint category/type, and allowed priority values.
6. Customer MUST be validated per FR-002 / BR-002 before final confirmation (except configured UNVERIFIED emergency mode).

### 8. Trigger

Actor selects business action **Create New Complaint** after receiving a customer complaint through a configured intake channel (walk-in, phone, email, portal, integrated social, or other Administrator-configured channel).

### 9. Normal Flow

1. Actor opens Create Complaint.
2. Actor performs Customer Search (FR-002) using exactly one primary key type: Customer Number **or** Identity Number **or** Reference Number.
3. System displays Master Customer brief profile; actor confirms the correct customer.
4. System SHOULD present or link Customer 360 context (BR-010) for active complaints and history before continue.
5. System runs Duplicate Complaint Detection (FR-003 / BR-014) and presents warnings when candidates exist.
6. Actor completes mandatory Complaint attributes:
   - Intake channel
   - Category / complaint type
   - Subject
   - Description
   - Initial priority (or configured default)
   - Recording unit (default = actor unit)
   - Optional external reference (channel ticket number, letter number, etc.)
7. Actor MAY upload initial attachments (FR-004) and MAY add initial communication/notes (out of Batch 1 FR scope; governed by BR-011 / BR-013 if invoked).
8. Actor confirms creation.
9. System SHALL:
   - Generate a unique Complaint Number
   - Persist Complaint with status `REGISTERED`
   - Persist `CustomerId` only (no Master Customer SoR copy)
   - Persist registration timestamp, creating actor, and unit
   - Write Audit Trail (BR-016) and Timeline entry (BR-017)
   - Request Notification Platform delivery per opt-in configuration
10. If “initial Case required” policy is active, System SHALL invoke Create Case (BR-004) in the same business transaction.
11. System SHALL display confirmation including Complaint Number and status.

### 10. Alternative Flow

#### A1 — Multiple customer candidates

1. Master Customer returns multiple matches.
2. Actor selects exactly one candidate (FR-002 A1).
3. Flow resumes at customer confirmation.

#### A2 — Duplicate warning → open existing Complaint

1. FR-003 marks strong duplicate candidate(s).
2. Actor opens existing Complaint and does **not** create a new Aggregate.
3. Create Complaint is cancelled with no new Aggregate.
4. Actor MAY add a new Case on the existing Complaint (BR-004) outside this FR’s create path.

#### A3 — Duplicate warning overridden with justification

1. Authorized actor (Supervisor or policy-permitted role) continues create despite warning.
2. Justification MUST be provided when policy requires it.
3. New Complaint is created; “possible duplicate of” linkage MUST be recorded (BR-018 / BR-016).

#### A4 — Complaint created without initial Case

1. Administrator policy allows Complaint without Case at first second.
2. Complaint remains `REGISTERED` awaiting Create Case.
3. SLA MUST NOT start (SLA belongs to Case per locked decision / BR-006).

#### A5 — Integrated channel intake

1. Channel boundary supplies customer key and description payload.
2. Agent reviews and confirms before Aggregate creation, **or** System auto-registers when channel auto-register policy is active and validations pass.
3. Channel source MUST be recorded.

### 11. Exception Flow

| ID | Condition | System Behavior |
|---|---|---|
| E1 | Customer search key empty/incomplete | MUST reject continue; require at least one allowed key |
| E2 | Customer not found in Master Customer | MUST reject normal Create; MAY allow UNVERIFIED only if enterprise emergency policy is configured |
| E3 | Master Customer unavailable | Strict: MUST reject create. Degraded (if configured): MAY create with `customerVerificationPending=true` without inventing Master attributes |
| E4 | Actor unauthorized | MUST reject; MUST write security audit attempt |
| E5 | Mandatory attributes missing/invalid | MUST reject confirm; MUST mark violating fields |
| E6 | Mandatory Audit/Timeline write fails | MUST fail the business create; MUST NOT leave an operational Aggregate without required trail |
| E7 | Hard-block duplicate policy triggered | MUST reject create (FR-003); MUST NOT create Aggregate |

### 12. Validation Rules

| Validation | Rule |
|---|---|
| Customer key | At least one allowed key type MUST be supplied for lookup |
| CustomerId | MUST exist after successful validation, except configured UNVERIFIED mode |
| Subject | MUST be present; length MUST comply with configured policy (business guidance: 1–200 characters) |
| Description | MUST be present; length MUST comply with configured policy (business guidance: 1–5000 characters) |
| Category | MUST be an active configured category |
| Channel | MUST be an active configured channel |
| Priority | MUST be one of configured priority values |
| Duplicate | Warning MUST be shown when candidate score ≥ threshold; override MUST capture justification when required |
| Authorization | Actor MUST have create entitlement for the unit |
| Aggregate invariants | MUST NOT create Assignment or SLA on Complaint |

### 13. Input Data

| Data | Mandatory | Source | Notes |
|---|---|---|---|
| Customer search key + type | Yes (for normal path) | Actor | Customer Number / Identity Number / Reference Number |
| Confirmed CustomerId | Yes (normal path) | Master Customer via FR-002 | Stored on Complaint |
| Channel | Yes | Actor / channel payload | Active catalog value |
| Category / type | Yes | Actor | Active catalog value |
| Subject | Yes | Actor | |
| Description | Yes | Actor | |
| Priority | Yes | Actor or default policy | |
| Recording unit | Yes | Default actor unit; overridable if permitted | From Organization |
| External reference | No | Actor / channel | |
| Duplicate override justification | Conditional | Actor | Required when overriding warning under policy |
| Initial attachments | No | Actor via FR-004 | |
| Idempotency / channel message id | Conditional | Integrated channel | For auto-register channels |

### 14. Output Data

| Data | Mandatory | Notes |
|---|---|---|
| Complaint Number | Yes | Unique within module |
| Complaint internal ID | Yes | System identity |
| Status | Yes | Initial `REGISTERED` |
| CustomerId | Yes (or UNVERIFIED pending flag) | Reference only |
| CreatedAt / CreatedBy / Unit | Yes | |
| Duplicate check result summary | Yes | None / warned / overridden / blocked |
| Initial Case Number | Conditional | If BR-004 fired |
| Confirmation view model | Yes | For UI presentation |

### 15. Business Constraints

1. ECMP MUST NOT act as Customer Master SoR.
2. Complaint MUST be Aggregate Root; Complaint identity MUST NOT be reused.
3. Create Complaint MUST NOT create Cases outside the same Complaint Aggregate.
4. Assignment and SLA MUST NOT exist at Complaint level.
5. Complaint Number MUST be enterprise-unique within the module.
6. Physical deletion of Complaint MUST be prohibited; cancellation only via configured status/flow with audit.
7. Future classification config changes MUST NOT rewrite historical Complaint classification without effective-dated rules.
8. Successful create without mandatory audit MUST be impossible.

### 16. Security Requirements

1. Authentication and ECMP authorization MUST be enforced before create.
2. Customer fields displayed during create MUST follow need-to-know and masking policy.
3. Duplicate override justification MUST be treated as sensitive operational data with restricted read access.
4. Attachments during create MUST obey FR-004 / BR-012 controls.
5. Frontend MUST call only ECMP Backend APIs; ECMP Backend SHALL call Master Customer / Notification / Audit Platform APIs.

### 17. Audit Requirements

System MUST record at minimum (BR-016):

- Who (enterprise principal mapped to ECMP actor)
- What (Complaint Created)
- When (trusted timestamp)
- Where (organizational unit)
- Object (Complaint Number / internal ID)
- Key business attributes (category, priority, CustomerId, channel)
- Duplicate check outcome (none / warned / overridden / blocked)
- Correlation to initial Case if created

### 18. Notifications

Via Notification Platform, opt-in only:

- Supervisor of recording unit — new Complaint in queue (SHOULD)
- Creating Agent — confirmation with Complaint Number (MAY)
- Other recipients per Administrator notification matrix (MAY)

Notification delivery failure MUST NOT roll back a successfully committed Complaint; failure MUST be recorded in Notification delivery log.

### 19. Acceptance Criteria

1. Given an authorized Agent and a verified CustomerId, when valid Complaint attributes are submitted, then the system creates a Complaint with unique Complaint Number and status `REGISTERED`.
2. Given successful create, then Complaint stores `CustomerId` only and does not persist Master Customer attributes as SoR.
3. Given successful create, then an immutable audit record and a Timeline “Complaint Created” entry exist.
4. Given missing mandatory attributes, when confirm is attempted, then create is rejected with field-level validation errors.
5. Given unauthorized actor, when create is attempted, then create is rejected and a security audit attempt is recorded.
6. Given duplicate candidates at or above threshold, when Actor confirms without required justification, then create is rejected or blocked per policy; when authorized override with justification is supplied, then create succeeds and linkage is audited.
7. Given “initial Case required” policy ON, when create succeeds, then exactly one initial Case is created under the same Complaint Aggregate.
8. Given Master Customer unavailable in Strict mode, when create is attempted, then create is rejected.
9. Given create succeeds, when Notification Platform is down, then Complaint remains created and notification failure is logged.

### 20. Priority

**Must**

### 21. Future Enhancement

1. Auto-classification of category/priority under configuration-first assistive rules.
2. Full omnichannel intake with per-message-id idempotency.
3. Complaint draft persistence before final submit.
4. Administrator-calibrated duplicate score models per category.

---

## 8. FR-002 Customer Search

### 1. Document ID

**FR-002**

### 2. Title

Customer Search

### 3. Description

The system SHALL enable an authorized actor to search and identify a customer by submitting exactly one allowed key type — Customer Number, Identity Number, or Reference Number — and SHALL resolve the result to a Master Customer `CustomerId` via Master Customer API through the ECMP Backend. ECMP MUST NOT create local customer masters and MUST NOT write back to Master Customer.

### 4. Business Objective

Guarantee that every Complaint is linked only to a legitimate Master Customer identity, using a simple Agent search experience, while preserving Master Customer as the single source of truth for customer profile data.

### 5. Business Rule Reference

| Rule ID | Rule Name | Usage in FR-002 |
|---|---|---|
| BR-002 | Customer Validation | Primary rule |
| BR-001 | Create Complaint | Consumer of validated CustomerId |
| BR-010 | Customer 360 View | May be opened after successful identification |
| BR-016 | Audit Trail | Validation outcome audit |

### 6. Actors

- Agent / Case Handler / Supervisor (search and confirm)
- System (calls Master Customer, normalizes results, sets verification status)
- Administrator (allowed key types, timeout, degradation policy)
- Master Customer (external SoR)

### 7. Preconditions

1. Actor MUST be authenticated.
2. Actor MUST be authorized to view customer data appropriate to role (sensitive fields MAY be masked).
3. Master Customer read integration MUST be defined.
4. Allowed customer key types MUST be active in configuration.

### 8. Trigger

- Before Create Complaint confirmation (FR-001)
- Actor selects **Search Customer** from Customer 360 or intake workspace
- Reconciliation of a Complaint with pending verification
- Integrated channel supplies a customer key for validation

### 9. Normal Flow

1. Actor selects key type and enters key value.
2. System validates basic format (non-empty; pattern per key type when configured).
3. ECMP Backend SHALL call Master Customer search API (Frontend MUST NOT call Master Customer directly).
4. When exactly one definitive result is returned, System displays brief profile and sets candidate `CustomerId`.
5. Actor confirms match.
6. System marks `customerVerified=true` in transaction context and locks `CustomerId` for subsequent Complaint create/link.
7. System MAY refresh read-only Customer 360 cache for that `CustomerId`.

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
3. If allowed, a special flag MUST be recorded.

#### A4 — Enrichment after UNVERIFIED create

1. Previously UNVERIFIED Complaint is successfully validated later.
2. Final `CustomerId` is set.
3. History and audit MUST record the customer reference change.

### 11. Exception Flow

| ID | Condition | System Behavior |
|---|---|---|
| E1 | Not found | Validation fails; normal FR-001 create MUST be rejected unless emergency UNVERIFIED mode is configured |
| E2 | Master Customer timeout/unavailable | Follow Strict vs Degraded policy aligned with BR-001 E3; limited retries MAY occur; unbounded retry loops MUST NOT occur in Agent session |
| E3 | Ambiguous results without selection | MUST NOT auto-assign `CustomerId` |
| E4 | Attempt to edit Master Customer data from ECMP | MUST reject; changes only via Master Customer processes/systems |
| E5 | Conflicting multiple keys supplied | MUST force manual resolution; MUST NOT silently choose |

### 12. Validation Rules

| Validation | Rule |
|---|---|
| Key presence | At least one allowed key MUST be provided |
| Key consistency | Exactly one active `CustomerId` per confirmation |
| Read-only | No Master Customer write-back from ECMP |
| Masking | Sensitive contact/identity display MUST follow role policy |
| Verification state | Verified / Unverified MUST be explicit |
| Rate control | Bulk enumeration patterns SHOULD be prevented via enterprise security controls |

### 13. Input Data

| Data | Mandatory | Notes |
|---|---|---|
| Key type | Yes | Customer Number / Identity Number / Reference Number |
| Key value | Yes | Non-empty; format per config |
| Actor confirmation | Yes (for lock) | Required when one or many candidates |

### 14. Output Data

| Data | Mandatory | Notes |
|---|---|---|
| CustomerId | Yes on success | From Master Customer |
| Brief profile view model | Yes on success | Read-only projection; not SoR |
| Verification status | Yes | verified / not found / ambiguous / degraded / unverified |
| Candidate list | Conditional | When multiple matches |
| Masking indicators | Conditional | Per role |

### 15. Business Constraints

1. Complaint MUST store only `CustomerId` as authoritative ECMP customer reference.
2. Any customer attribute copy in ECMP MUST be read-model/cache and MAY become stale; refresh follows policy.
3. Creating a “local customer” as Master substitute is prohibited.
4. Re-validation MUST NOT erase Complaint History; it MAY update reference with full audit trail.
5. Frontend MUST NOT call Master Customer API directly.

### 16. Security Requirements

1. Identity numbers are sensitive; display and logs MUST be minimized (hash/mask in audit when policy requires).
2. Search results MUST be need-to-know restricted.
3. Enterprise anti-enumeration controls SHOULD apply.
4. Authorization failures MUST be reject-closed.

### 17. Audit Requirements

System MUST audit (BR-016):

- Key type used (not full identity number when forbidden — hash/mask allowed)
- Resulting CustomerId (when found)
- Verification status
- Actor, timestamp
- Outcome: found / not found / ambiguous / degraded

### 18. Notifications

Generally no customer notification. Optional internal notification to Supervisor when UNVERIFIED volume exceeds configured threshold (MAY).

### 19. Acceptance Criteria

1. Given a valid Customer Number that uniquely matches Master Customer, when Agent searches and confirms, then System locks that `CustomerId` with `customerVerified=true`.
2. Given multiple Master Customer matches, when Agent has not selected a candidate, then System MUST NOT lock a CustomerId.
3. Given no Master Customer match, when Agent attempts FR-001 normal create, then create is rejected (unless UNVERIFIED emergency policy is enabled and used).
4. Given an attempt to update Master Customer attributes from ECMP UI/API, then the operation is rejected.
5. Given Master Customer unavailable in Strict mode, when search is executed, then System returns a degradation/unavailable outcome and does not invent customer data.
6. Given Frontend requests, when customer search is performed, then only ECMP Backend is called; Master Customer is invoked only by Backend.

### 20. Priority

**Must**

### 21. Future Enhancement

1. Controlled fuzzy match with configurable score thresholds.
2. Consumption of digital identity / biometric verification results from external identity services.
3. Read-only watchlist / special-attention flags from Master Customer.

---

## 9. FR-003 Duplicate Complaint Detection

### 1. Document ID

**FR-003**

### 2. Title

Duplicate Complaint Detection

### 3. Description

The system SHALL detect potential duplicate Complaints before final Create Complaint confirmation by comparing the candidate intake (same `CustomerId` and/or similar attributes within a configured time window) against existing Complaints, present warnings with actionable options, and record all decisions. Default behavior is **warn + justify**, not silent reject, except where category policy defines hard block.

### 4. Business Objective

Prevent duplicate Complaint Aggregates for substantially the same customer issue, promote adding a Case to an existing Complaint (No Duplicate Work), and preserve full decision traceability.

### 5. Business Rule Reference

| Rule ID | Rule Name | Usage in FR-003 |
|---|---|---|
| BR-014 | Duplicate Complaint | Primary rule |
| BR-003 | Complaint Search | Underlying search/index capability for candidates |
| BR-001 | Create Complaint | Gate before confirm |
| BR-004 | Create Case | Preferred alternative to new Complaint |
| BR-010 | Customer 360 View | Context for active complaints |
| BR-016 | Audit Trail | Warn / override / link decisions |
| BR-018 | Complaint History | Possible-duplicate / related linkages |

### 6. Actors

- Agent (review candidates, choose action)
- Supervisor (override with justification when required)
- System (scoring and candidate retrieval)
- Administrator (thresholds, windows, hard-block category policies)

### 7. Preconditions

1. `CustomerId` is identified, or searchable customer key context exists.
2. Complaint search/index capability is available (BR-003), or degradation mode is defined.
3. Duplicate detection policy (threshold, time window, compared fields) is active.

### 8. Trigger

- Automatically before Create Complaint confirmation (FR-001)
- Manual “Check Duplicate” action by actor
- Periodic/recheck after UNVERIFIED Complaint becomes verified

### 9. Normal Flow

1. System searches candidates using `CustomerId` + configured time window + category/similarity attributes.
2. System computes candidate scores and filters by threshold.
3. System presents candidate list including status and open Case indicators (where authorized).
4. Actor selects one outcome:
   - Cancel create and open existing Complaint, **or**
   - Continue create with justification (when permitted), **or**
   - Add Case to existing Complaint (BR-004) instead of new Complaint.
5. System records decision in Audit and History.

### 10. Alternative Flow

#### A1 — False positive override

1. Authorized actor overrides with justification.
2. New Complaint is created and marked reviewed/possible-duplicate-linked as configured.
3. Override MUST be auditable.

#### A2 — Business relate / non-destructive link

1. Supervisor links related/duplicate relationship without hard-deleting either Aggregate.
2. Work continues on designated survivor Complaint.
3. History of both Aggregates MUST remain (No Information Lost).

#### A3 — Cross-unit duplicate candidate

1. Candidates outside actor unit are shown only if authorization allows.
2. Coordination/escalation follows BR-007 if needed (out of Batch 1 execution scope).

#### A4 — No candidates above threshold

1. System records “no duplicate warning”.
2. Create Complaint proceeds without override justification.

### 11. Exception Flow

| ID | Condition | System Behavior |
|---|---|---|
| E1 | Detection unavailable (index down) | Create MAY proceed with `duplicateCheckDegraded=true`; MUST require later review |
| E2 | Override without required justification | MUST reject continue |
| E3 | Hard-block policy for category | MUST prevent new Complaint create |
| E4 | Actor lacks scope to see a candidate | Candidate MUST NOT be leaked; uniform authorized-empty behavior SHOULD apply per security policy |

### 12. Validation Rules

| Validation | Rule |
|---|---|
| Threshold | Candidate score ≥ configured threshold MUST raise warning |
| Time window | MUST use configured window; inverted/invalid windows MUST be rejected at config level |
| Compared fields | Only configured fields MAY contribute to score |
| Justification | Minimum length/content MUST apply when override is required |
| Decision capture | Actor decision MUST be one of allowed actions |
| No silent drop | System MUST NOT discard intake without actor-visible outcome |

### 13. Input Data

| Data | Mandatory | Notes |
|---|---|---|
| CustomerId (or pending key context) | Yes | Primary correlation key |
| Candidate category / subject / channel | Conditional | From FR-001 draft attributes when available |
| Policy version / threshold | Yes (system) | Active duplicate policy |
| Actor decision | Yes when warned | open existing / override / add case |
| Override justification | Conditional | Required by policy |

### 14. Output Data

| Data | Mandatory | Notes |
|---|---|---|
| Candidate list | Yes (may be empty) | Scoped by authorization |
| Score per candidate | Yes when candidates exist | |
| Warning flag | Yes | true/false |
| Decision code | Yes when warned | |
| Linkage record | Conditional | possible-duplicate / related |
| Degraded flag | Conditional | When check could not run fully |

### 15. Business Constraints

1. System MUST NOT silently drop a Complaint intake.
2. System MUST NOT hard-delete a Complaint because it is considered duplicate.
3. Preferred resolution for same substantive issue: **new Case on existing Complaint**, not new Complaint.
4. All duplicate decisions MUST be traceable.
5. Duplicate search results remain authorization-scoped.

### 16. Security Requirements

1. Candidate visibility MUST enforce org/role scope.
2. Override justifications are sensitive and read-restricted.
3. Detection APIs are Backend-only for Frontend clients.

### 17. Audit Requirements

System MUST audit:

- DuplicateWarned
- DuplicateOverridden (with justification reference)
- DuplicateLinked / Related
- ResolvedAsCaseOnExisting
- DuplicateCheckDegraded

### 18. Notifications

- Supervisor MAY be notified on frequent overrides or hard-block attempts (configuration).
- No customer notification for detection itself.

### 19. Acceptance Criteria

1. Given same CustomerId and an open Complaint within the configured window matching category threshold, when Agent attempts create confirm, then a duplicate warning with candidates is shown.
2. Given a warning, when Agent chooses open existing, then no new Complaint Aggregate is created.
3. Given a warning requiring justification, when Agent continues without justification, then create is rejected.
4. Given authorized override with justification, when create proceeds, then Complaint is created and possible-duplicate linkage plus audit exist.
5. Given hard-block category policy, when duplicate threshold is met, then create is rejected.
6. Given search index unavailable, when create proceeds under degradation policy, then `duplicateCheckDegraded=true` is recorded for later review.
7. Given candidates outside actor authorization scope, when detection runs, then unauthorized candidates are not disclosed.

### 20. Priority

**Must**

### 21. Future Enhancement

1. Controlled text-similarity models with Administrator calibration.
2. Golden Complaint selection rules for related-link resolution.
3. Continuous post-create duplicate surveillance for UNVERIFIED→verified transitions beyond intake.

---

## 10. FR-004 Attachment Upload

### 1. Document ID

**FR-004**

### 2. Title

Attachment Upload

### 3. Description

The system SHALL allow authorized actors to upload supporting evidence (documents, photos, videos, and other allowlisted file types) and bind them to a Complaint and/or Case. The system SHALL persist attachment metadata and history, enforce type/size/security controls, prohibit physical user delete, and ensure attachments remain part of the Escalation Package (No Information Lost During Escalation).

### 4. Business Objective

Ensure evidence captured at intake and during handling remains complete, accessible, and auditable for the full Complaint lifecycle — including after escalation to Regional or Head Office.

### 5. Business Rule Reference

| Rule ID | Rule Name | Usage in FR-004 |
|---|---|---|
| BR-012 | Attachment Management | Primary rule |
| BR-001 | Create Complaint | Optional initial evidence at registration |
| BR-016 | Audit Trail | Upload / void / supersede / sensitive access |
| BR-017 | Timeline | Attachment uploaded events |
| BR-007 | Escalation | Attachments MUST be included in Escalation Package |
| BR-010 | Customer 360 View | Attachment History visibility |
| BR-008 | Resolution | Evidence completeness may be required later |

### 6. Actors

- Agent / Case Handler (upload)
- Supervisor (review)
- Regional / Head Office handlers (access after escalation)
- System (type/size validation; security scan orchestration)
- Administrator (allowlist, max size, classification catalog)
- Compliance (retention / legal hold)

### 7. Preconditions

1. Anchor object (Complaint and/or Case) MUST exist and MUST allow upload in its current status, **or** upload is performed as part of in-progress Create Complaint draft session per configured intake rules.
2. Actor MUST be authorized to upload for that anchor and classification.
3. File type/extension MUST be on allowlist; size MUST be within limit.
4. Security scanning dependency MUST be available when policy requires scan-before-ACTIVE.

### 8. Trigger

- Upload during Complaint Registration (FR-001)
- Upload during Case handling
- Evidence request prior to resolution
- Channel ingest of files
- Escalation package completeness check referencing attachments

### 9. Normal Flow

1. Actor selects file(s) and classification (customer evidence, internal evidence, official letter, etc.).
2. Actor selects anchor Complaint and optional Case.
3. System validates type, size, and filename policy.
4. System submits file to security scan when configured.
5. On success, System stores binary via enterprise storage dependency and persists metadata + storage reference with status `ACTIVE`.
6. System appends Attachment History and Timeline event.
7. System writes audit `AttachmentUploaded`.
8. Attachment appears in Complaint/Case detail and Customer 360 Attachment History (per authorization).

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

#### A4 — Upload during create before Complaint Number exists

1. System MAY accept staged uploads in create session.
2. On successful FR-001 commit, staged attachments MUST bind to the new Complaint.
3. If create is cancelled, staged uploads MUST be discarded or voided per policy without leaving orphan ACTIVE operational evidence.

### 11. Exception Flow

| ID | Condition | System Behavior |
|---|---|---|
| E1 | Illegal type/size/name | MUST reject upload |
| E2 | Malware / scan failure | MUST reject; MUST security-audit the event |
| E3 | User attempts physical delete | MUST reject; void-with-reason only |
| E4 | Unauthorized access/download | MUST reject; sensitive access MAY be audited |
| E5 | Anchor Complaint/Case not uploadable (e.g., CLOSED without reopen) | MUST reject operational upload per policy |
| E6 | Storage dependency failure | MUST fail upload; MUST NOT mark ACTIVE |

### 12. Validation Rules

| Validation | Rule |
|---|---|
| Allowlist | MIME/extension MUST be allowlisted |
| Max size | MUST not exceed configured maximum (per type if configured) |
| Classification | MUST be provided from configured catalog |
| Anchor | Complaint and/or Case reference MUST be valid (or valid create-session staging token) |
| Scan status | When policy requires scan, status MUST be clean before `ACTIVE` |
| Filename | MUST meet safety policy (path segments, reserved characters) |
| Count limits | Bulk count MUST respect configured maximum per action |

### 13. Input Data

| Data | Mandatory | Notes |
|---|---|---|
| File binary | Yes | |
| Classification | Yes | Configured catalog |
| Anchor ComplaintId | Conditional | Required unless staging in create session |
| Anchor CaseId | No | Optional more specific bind |
| Filename | Yes | Original name (sanitized for storage metadata) |
| Content type | Yes | Declared / detected |
| Actor | Yes | From authenticated principal |

### 14. Output Data

| Data | Mandatory | Notes |
|---|---|---|
| AttachmentId | Yes | |
| Status | Yes | ACTIVE / SUPERSEDED / VOID / REJECTED |
| Storage reference | Yes | Not a public unauthenticated URL |
| Integrity hash | SHOULD | For integrity/audit |
| History entry | Yes | |
| Timeline event | Yes | |
| Scan result summary | Conditional | When scan enabled |

### 15. Business Constraints

1. Attachments MUST NOT be lost during escalation; documents, photos, and videos are part of Escalation Package (BR-007).
2. Attachment History is append-only for business meaning; void/supersede — not silent erase.
3. Legal hold MUST prevent void/purge where applicable.
4. Complaint closure MUST NOT delete attachments.
5. ECMP owns business metadata and access rules; binary MAY reside in enterprise storage, but business attachment remains part of Complaint Management trail.
6. No direct Frontend access to enterprise storage APIs bypassing ECMP Backend authorization.

### 16. Security Requirements

1. Malware scanning MUST be enforced when configured.
2. DLP / sensitive-content controls SHOULD apply per enterprise policy.
3. Encryption at rest is owned by storage platform; ECMP MUST not expose unauthenticated public links.
4. Internal vs customer evidence classifications MUST enforce distinct access rights.
5. Download of sensitive attachments MAY require audited access.

### 17. Audit Requirements

System MUST audit:

- AttachmentUploaded
- AttachmentSuperseded
- AttachmentVoided
- AttachmentAccess (for sensitive classifications, when policy requires)

Audit MUST include actor, timestamp, attachment id, anchor ids, classification, and outcome.

### 18. Notifications

Optional notification to Supervisor when critical evidence is uploaded (configuration) (MAY). Notification failure MUST NOT void a successful upload.

### 19. Acceptance Criteria

1. Given authorized Agent and allowlisted file within size limit, when upload is bound to a Complaint, then attachment status is `ACTIVE` and history/timeline/audit exist.
2. Given disallowed file type or oversize file, when upload is attempted, then upload is rejected and no ACTIVE attachment is created.
3. Given malware scan failure (policy on), when upload is attempted, then upload is rejected and security audit is written.
4. Given user requests physical delete, when delete is attempted, then operation is rejected; void-with-reason remains the only business removal path.
5. Given superseding upload, when new version is ACTIVE, then prior version is `SUPERSEDED` and still retrievable for audit.
6. Given successful escalation later, when Head Office opens the Case, then previously uploaded branch attachments remain visible to authorized roles (No Information Lost).
7. Given Frontend client, when upload occurs, then only ECMP Backend attachment APIs are used.

### 20. Priority

**Must**

### 21. Future Enhancement

1. OCR / metadata extraction.
2. Auto-classification of document types.
3. Customer self-upload via integrated portal channel.

---

## 11. Use Case Mapping

| Use Case ID | Use Case Name | Functional Requirement |
|---|---|---|
| UC-CM-001 | Register Complaint for identified customer | FR-001 |
| UC-CM-002 | Search and confirm customer from Master Customer | FR-002 |
| UC-CM-003 | Detect and handle potential duplicate Complaint | FR-003 |
| UC-CM-004 | Upload evidence attachment to Complaint/Case | FR-004 |
| UC-CM-005 | Register Complaint with initial evidence | FR-001, FR-004 |
| UC-CM-006 | Register Complaint after duplicate warning override | FR-001, FR-003 |
| UC-CM-007 | Abandon create and continue on existing Complaint | FR-001, FR-003 |
| UC-CM-008 | Identify customer then open Customer 360 context | FR-002 (supports FR-001; BR-010) |

---

## 12. Screen Mapping

Logical screens only. **UI design is out of scope** for this FRD.

| Screen ID | Screen Name | Primary FR | Supporting FR | Notes |
|---|---|---|---|---|
| SCR-CM-001 | Create Complaint | FR-001 | FR-002, FR-003, FR-004 | Intake form + confirm |
| SCR-CM-002 | Customer Search / Candidate Select | FR-002 | — | Key entry + candidate list |
| SCR-CM-003 | Duplicate Warning Dialog / Panel | FR-003 | FR-001 | Open existing / override / add Case |
| SCR-CM-004 | Attachment Upload Panel | FR-004 | FR-001 | Usable standalone or embedded in create |
| SCR-CM-005 | Create Complaint Confirmation | FR-001 | — | Displays Complaint Number / status |
| SCR-CM-006 | Customer Brief Profile Card | FR-002 | FR-001 | Read-only Master projection |

Existing product screen UX-SCR-001 (Case Detail Workspace) is **not** redefined here; Batch 1 intake screens are additive logical inventory pending UI UX Spec.

---

## 13. API Mapping

Logical ECMP Backend API capabilities required by Batch 1. **Payload design and OpenAPI authorship are out of scope** for this FRD. Existing catalog IDs are referenced where aligned; gaps are marked **Planned**.

| FR | Logical API Capability | Existing / Planned Catalog Reference | Consumer | Downstream Enterprise API |
|---|---|---|---|---|
| FR-001 | Create Complaint | Existing alignment: `API-390` `POST /api/v1/complaints` (target model remapping pending DEC) | Frontend → ECMP Backend | Notification (opt-in); Audit Platform (optional copy) |
| FR-001 | Get Complaint confirmation/detail | Existing alignment: `API-392` | Frontend → ECMP Backend | — |
| FR-002 | Search Customer by key | **Planned** ECMP Backend customer-search facade over Master Customer (do not treat local cache as SoR). Related read list exists as `API-222` but is insufficient as Master Customer contract) | Frontend → ECMP Backend | Master Customer Search/Get |
| FR-002 | Confirm / lock CustomerId in session/context | **Planned** (may be embedded in create draft context) | Frontend → ECMP Backend | Master Customer Get-by-id |
| FR-003 | Check duplicate candidates | **Planned** (may be dedicated endpoint or create pre-check). May leverage complaint search `API-388` as technical substrate | Frontend → ECMP Backend | — |
| FR-003 | Record duplicate decision / linkage | **Planned** (or embedded in create command) | Frontend → ECMP Backend | — |
| FR-004 | Upload attachment | Existing: `API-323` `POST /api/v1/attachments` | Frontend → ECMP Backend | Enterprise Storage; optional malware scan service |
| FR-004 | List attachments for Complaint | Existing: `API-387` | Frontend → ECMP Backend | — |
| FR-004 | Get metadata / download | Existing: `API-324`, `API-325` | Frontend → ECMP Backend | Enterprise Storage |
| FR-004 | Logical void | Existing: `API-326` (logical delete semantics MUST match BR-012 void rules) | Frontend → ECMP Backend | — |

### Integration constraints (normative)

1. Frontend MUST call ECMP Backend only.
2. ECMP Backend SHALL call Master Customer, Notification, Storage, Calendar (later), and Audit Platform APIs.
3. No direct database access to any external enterprise system.

---

## 14. Database Mapping

Logical persistence mapping only. **Physical schema, SQL, and migration design are out of scope.**

| FR | Logical Entity / Store | Ownership | Notes |
|---|---|---|---|
| FR-001 | Complaint (Aggregate Root) | ECMP | Number, status, CustomerId, classification, channel, subject, description, priority, unit, timestamps, verification flags |
| FR-001 | Complaint History (initial snapshot / linkages) | ECMP | BR-018 |
| FR-001 | Timeline entry | ECMP | BR-017 |
| FR-001 | Audit record | ECMP (+ optional Audit Platform copy) | BR-016; mandatory with create |
| FR-001 | Initial Case (optional) | ECMP | Only if policy invokes BR-004 |
| FR-002 | Customer read-model / cache (optional) | ECMP projection | Non-SoR; refreshable from Master Customer |
| FR-002 | Customer validation audit | ECMP | Outcome of search/confirm |
| FR-003 | Duplicate candidate evaluation result | ECMP (transient or stored decision) | Score, threshold, policy version |
| FR-003 | Duplicate / related linkage | ECMP | Possible-duplicate relationships |
| FR-004 | Attachment metadata | ECMP | Classification, status, hash, anchors |
| FR-004 | Attachment binary | Enterprise Storage dependency | Referenced by storage key; not Master Customer DB |
| FR-004 | Attachment History | ECMP | Append-only business history |

---

## 15. Business Rule Mapping

| Functional Requirement | Business Rules (BR-CM-CAT-001) |
|---|---|
| FR-001 Complaint Registration | BR-001 (primary), BR-002, BR-014, BR-016, BR-017; supporting BR-004, BR-010, BR-012, BR-018 |
| FR-002 Customer Search | BR-002 (primary); supporting BR-001, BR-010, BR-016 |
| FR-003 Duplicate Complaint Detection | BR-014 (primary), BR-003, BR-016, BR-018; supporting BR-001, BR-004, BR-010 |
| FR-004 Attachment Upload | BR-012 (primary), BR-016, BR-017; supporting BR-001, BR-007, BR-008, BR-010 |

### Reverse mapping (BR → FR in Batch 1)

| Business Rule | Batch 1 FR Coverage |
|---|---|
| BR-001 Create Complaint | FR-001 |
| BR-002 Customer Validation | FR-002 (primary), FR-001 |
| BR-003 Complaint Search | FR-003 (substrate only; standalone Complaint Search FR not in Batch 1) |
| BR-012 Attachment Management | FR-004 |
| BR-014 Duplicate Complaint | FR-003 (primary), FR-001 |
| BR-016 Audit Trail | FR-001, FR-002, FR-003, FR-004 |
| BR-017 Timeline | FR-001, FR-004 |

---

## 16. Requirements Traceability Matrix (DM → BR → FR)

Domain Model (DM) IDs below are **logical Complaint Management Module domain entities** for Batch 1 traceability under the locked Aggregate model. They are not physical tables.

| DM ID | Domain Entity | Business Rules | Functional Requirements | Blueprint Capability Affinity |
|---|---|---|---|---|
| DM-CM-001 | Complaint (Aggregate Root) | BR-001, BR-016, BR-017, BR-018 | FR-001 | BP-001 (complaint registration & tracking) |
| DM-CM-002 | Customer Reference (`CustomerId`) | BR-002 | FR-002, FR-001 | BP-001 / BP-003 (customer context) |
| DM-CM-003 | Customer Read-Model Projection | BR-002, BR-010 | FR-002 | BP-003 |
| DM-CM-004 | Duplicate Candidate / Linkage | BR-014, BR-003, BR-018 | FR-003, FR-001 | BP-001 (data quality / no duplicate work) |
| DM-CM-005 | Attachment | BR-012, BR-007 | FR-004, FR-001 | BP-001 (evidence trail) |
| DM-CM-006 | Attachment History | BR-012, BR-016 | FR-004 | BP-001 |
| DM-CM-007 | Audit Trail Record | BR-016 | FR-001, FR-002, FR-003, FR-004 | Cross-cutting |
| DM-CM-008 | Timeline Entry | BR-017 | FR-001, FR-004 | Cross-cutting |
| DM-CM-009 | Case (initial, optional) | BR-004 | FR-001 (conditional only) | BP-001; full Case FRs deferred |

### Compact DM → BR → FR links (Batch 1)

```text
DM-CM-001 Complaint  →  BR-001  →  FR-001
DM-CM-002 CustomerId →  BR-002  →  FR-002 → FR-001
DM-CM-004 Duplicate  →  BR-014  →  FR-003 → FR-001
DM-CM-005 Attachment →  BR-012  →  FR-004 → FR-001
DM-CM-007 Audit      →  BR-016  →  FR-001 / FR-002 / FR-003 / FR-004
DM-CM-008 Timeline   →  BR-017  →  FR-001 / FR-004
```

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
| FR-005+ (Case create standalone, Assignment, SLA, Escalation, Resolution, Closure, Reopen, Customer 360 FR, Communication, Comments, KPI, Reporting) | Later FRD batches |
| Direct enterprise DB access | Forbidden by architecture |
| Customer Master write-back | Forbidden (ADR-002 / BR-002) |

---

## 18. Open Questions

| ID | Question | Impact | Suggested Owner |
|---|---|---|---|
| OQ-CM-B1-001 | DEC remapping date: when does BR-CM-CAT-001 replace Sprint delivery SoT for implementation? | ID namespace / implementation sequencing | Business Owner + Architecture Board |
| OQ-CM-B1-002 | Exact Master Customer search API fields and identity-number masking contract | FR-002 audit/display | Integration Lead + Security |
| OQ-CM-B1-003 | Default duplicate threshold, window (days), and hard-block category list | FR-003 behavior | Operations Lead + Administrator |
| OQ-CM-B1-004 | Is initial Case mandatory at Complaint create in production policy? | FR-001 A4 vs auto BR-004 | Domain PO ECMF |
| OQ-CM-B1-005 | Attachment max sizes per media type and mandatory malware scan environments | FR-004 validation | Security + Administrator |

---

## 19. Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-29 | Business Analyst (FRD Batch 1) | Initial Draft v1.0 — FR-001…FR-004 + mappings + RTM |

---

## Architecture Review Checklist

- [ ] Scope limited to Complaint Management Module Batch 1
- [ ] Locked Aggregate / CustomerId / Working Day / No Information Lost decisions respected
- [ ] All FR BR references exist in BR-CM-CAT-001 (no invented BRs)
- [ ] External systems treated as API dependencies only
- [ ] Frontend → ECMP Backend → Enterprise APIs path explicit
- [ ] Traceability DM → BR → FR complete for Batch 1
- [ ] Out-of-scope design artifacts not embedded (DB/OpenAPI/UI/code)

---

*End of FRD-CM-001 Draft v1.0 — ECMP Complaint Management Module FRD Batch 1.*
