# ECMP Requirements Traceability Matrix — Complaint Management Module Batch 1

| Field | Value |
|---|---|
| Document ID | RTM-CM-B1-001 |
| Title | Complaint Management Module — Batch 1 Requirements Traceability Matrix |
| Version | 1.0 |
| Status | 🔒 LOCKED |
| Owner | BA Lead / QA Lead / Requirements Manager |
| Reviewer | Solution Architect, Security, Compliance, QA |
| Approver | CTO / Architecture Board |
| Module | Complaint Management Module — Batch 1 only |
| Source of Truth (FRD) | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (FRD-CM-001 **LOCKED**) |
| Source of Truth (BR) | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001) |
| Created | 2026-07-29 |
| Locked | 2026-07-29 |
| Related Delta Review | GOV-DELTA-FRD-CM-001 |
| Related Release Notes | GOV-RN-FRD-CM-001 |
| Related S0 Pack | `18 Architecture Governance/reviews/ECMP_CM_Batch1_S0_Contract_Pack_v1.0.md` |
| Related DEC | DEC-020 (Accepted — dual SoT / namespace ownership; closes OQ-CM-B1-001) |
| Namespace | FRD-CM-001 / BR-CM-CAT-001 Aggregate (`/api/v1/cm`) — coexistence with Sprint/foundation (`/api/v1/complaints`) per DEC-020 |

> This RTM does **not** modify the FRD, Business Rules, Architecture Decisions, or Batch 1 scope. It consolidates locked FRD mappings into the single Batch 1 traceability source for implementation planning and test design.

---

## Table of Contents

1. [Purpose and Scope](#1-purpose-and-scope)
2. [Traceability Chain](#2-traceability-chain)
3. [ID Conventions](#3-id-conventions)
4. [Master Traceability Matrix (FR spine)](#4-master-traceability-matrix-fr-spine)
5. [BR ↔ FR Matrix](#5-br--fr-matrix)
6. [FR ↔ UC ↔ Screen Matrix](#6-fr--uc--screen-matrix)
7. [API ↔ UC ↔ FR Matrix](#7-api--uc--fr-matrix)
8. [Domain Model ↔ FR ↔ DB Entity Matrix](#8-domain-model--fr--db-entity-matrix)
9. [Events ↔ FR Matrix](#9-events--fr-matrix)
10. [Security Controls ↔ FR Matrix](#10-security-controls--fr-matrix)
11. [Acceptance Criteria ↔ Test Cases](#11-acceptance-criteria--test-cases)
12. [Open Questions (Not Blocking / Future Decision)](#12-open-questions-not-blocking--future-decision)
13. [Orphan Items](#13-orphan-items)
14. [Duplicate Mappings](#14-duplicate-mappings)
15. [Coverage Summary](#15-coverage-summary)
16. [RTM Validation Report](#16-rtm-validation-report)
17. [Document History](#17-document-history)

---

## 1. Purpose and Scope

### 1.1 Purpose

Provide the **Batch 1 Requirements Traceability Matrix** that becomes the single traceability source for implementation, security design, and test authoring against FRD-CM-001 v1.1 LOCKED.

### 1.2 In Scope (Batch 1 only)

| FR ID | Title |
|---|---|
| FR-001 | Complaint Registration |
| FR-002 | Customer Search |
| FR-003 | Duplicate Complaint Detection |
| FR-004 | Attachment Upload |

### 1.3 Explicitly Out of Scope

Case creation (BR-004 / Batch 2), Assignment, SLA, Escalation execution, Resolution, Closure, Reopen, full Customer 360, Communication History, Comment Management, Dashboard KPI, Reporting, Sprint delivery SoT IDs (FRD-001 / BR-DOC-001), physical DB/OpenAPI authorship.

---

## 2. Traceability Chain

```text
Business Rule
  → Functional Requirement
    → Use Case
      → Screen
        → API Endpoint
          → Domain Model
            → Database Entity (logical)
              → Events
                → Security Controls
                  → Acceptance Criteria
                    → Test Cases
```

---

## 3. ID Conventions

| Layer | ID pattern | Notes |
|---|---|---|
| Business Rule | `BR-001`…`BR-020` | BR-CM-CAT-001 |
| Functional Requirement | `FR-001`…`FR-004` | FRD-CM-001 Batch 1 |
| Use Case | `UC-CM-001`…`UC-CM-009` | Logical |
| Screen | `SCR-CM-001`…`SCR-CM-006` | Logical (no UI design) |
| API (Batch 1 logical) | `API-CM-B1-xxx` | Logical capability; catalog refs where known |
| Domain Model | `DM-CM-001`…`DM-CM-012` | Logical Aggregate model |
| Database Entity | `DB-CM-xxx` | Logical persistence (not physical tables) |
| Event (Batch 1 logical) | `EVT-CM-xxx` | Audit/domain events from FRD; **Planned** catalog publish |
| Security Control | `SEC-CM-xxx` | Derived from FR §16 / §16.1 / §22 |
| Acceptance Criteria | `AC-CM-FR00n-mm` | Numbered from FR §19 |
| Test Case | `TC-CM-FR00n-mm` | **Planned** — authored against this RTM |
| Open Question | `OQ-CM-B1-xxx` | From FRD §18 |

---

## 4. Master Traceability Matrix (FR spine)

| FR | Primary BR | Supporting BR | UC | Screen | Logical API | DM | Events (logical) | Security (summary) | AC count | TC count (planned) |
|---|---|---|---|---|---|---|---|---|---|---|
| FR-001 | BR-001 | BR-002, BR-010†, BR-012, BR-014, BR-016, BR-017, BR-018 | UC-CM-001, 005, 006, 007, 009 | SCR-CM-001, 005 | API-CM-B1-001, 002 | DM-CM-001, 002, 010, 012 (+007,008) | EVT-CM-001…005 | SEC-CM-001-* | 12 | 12 |
| FR-002 | BR-002 | BR-001, BR-010†, BR-016, BR-018 | UC-CM-002, 008 | SCR-CM-002, 006 | API-CM-B1-003, 004, 005 | DM-CM-002, 003 (+007) | EVT-CM-010…012 | SEC-CM-002-* | 9 | 9 |
| FR-003 | BR-014 | BR-001, BR-003, BR-010†, BR-016, BR-018 | UC-CM-003, 006, 007 | SCR-CM-003 | API-CM-B1-006, 007 | DM-CM-004, 011 (+007) | EVT-CM-020…026 | SEC-CM-003-* | 8 | 8 |
| FR-004 | BR-012 | BR-001, BR-007‡, BR-008‡, BR-010†, BR-016, BR-017 | UC-CM-004, 005, 007 | SCR-CM-004 | API-CM-B1-008…013 | DM-CM-005, 006 (+007,008) | EVT-CM-030…034 | SEC-CM-004-* | 9 | 9 |

† Batch 1 Customer 360 **minimum subset** only (CTO D-05).  
‡ Forward constraints only (Escalation Package / Resolution evidence readiness) — **no Batch 1 Case/Escalation/Resolution FR**.

---

## 5. BR ↔ FR Matrix

### 5.1 Forward (BR → FR) — Batch 1 consumed rules

| BR | Rule Name | Batch 1 FR | Role | Status |
|---|---|---|---|---|
| BR-001 | Create Complaint | FR-001 | Primary | ✅ Covered (Case-create portions deferred Batch 2) |
| BR-002 | Customer Validation | FR-002, FR-001 | Primary / Prerequisite | ✅ Covered |
| BR-003 | Complaint Search | FR-003 | Substrate only (no standalone Search FR) | ✅ Covered (substrate) |
| BR-007 | Escalation | FR-004 | Forward constraint (Escalation Package) | ✅ Covered (constraint only) |
| BR-008 | Resolution | FR-004 | Forward constraint (evidence store) | ✅ Covered (constraint only) |
| BR-010 | Customer 360 View | FR-001, FR-002, FR-004 | Batch 1 minimum subset (D-05) | ✅ Covered (subset) |
| BR-012 | Attachment Management | FR-004, FR-001 | Primary / Supporting | ✅ Covered |
| BR-014 | Duplicate Complaint | FR-003, FR-001 | Primary / Pre-confirm | ✅ Covered (no Case create) |
| BR-016 | Audit Trail | FR-001, FR-002, FR-003, FR-004 | Cross-cutting | ✅ Covered |
| BR-017 | Timeline | FR-001, FR-004 | Cross-cutting | ✅ Covered |
| BR-018 | Complaint History | FR-001, FR-002, FR-003 | Linkage / before-after | ✅ Covered |

### 5.2 Catalog BRs outside Batch 1 (deferred — not Batch 1 orphans)

| BR | Rule Name | Batch 1 disposition |
|---|---|---|
| BR-004 | Create Case | **Out of Batch 1** (CTO D-02) → Batch 2 |
| BR-005 | Assignment | Later batch |
| BR-006 | Working Day SLA | Later batch |
| BR-009 | Complaint Closure | Later batch |
| BR-011 | Communication History | Later batch |
| BR-013 | Comment Management | Later batch |
| BR-015 | Complaint Reopen | Later batch |
| BR-019 | Dashboard KPI | Later batch |
| BR-020 | Reporting | Later batch |

### 5.3 Requirement checks

| Rule | Result |
|---|---|
| Every Batch 1 FR traces to ≥1 BR | ✅ PASS |
| Every BR consumed by Batch 1 FRs is reverse-mapped to ≥1 FR | ✅ PASS |
| Catalog BRs not in Batch 1 | Deferred (explicit) — not treated as Batch 1 orphans |

---

## 6. FR ↔ UC ↔ Screen Matrix

| UC ID | Use Case Name | FR | Primary Screen(s) |
|---|---|---|---|
| UC-CM-001 | Register Complaint for identified customer | FR-001 | SCR-CM-001, SCR-CM-005 |
| UC-CM-002 | Search and confirm customer from Master Customer | FR-002 | SCR-CM-002, SCR-CM-006 |
| UC-CM-003 | Detect and handle potential duplicate Complaint | FR-003 | SCR-CM-003 |
| UC-CM-004 | Upload evidence attachment to Complaint/Case | FR-004 | SCR-CM-004 |
| UC-CM-005 | Register Complaint with initial evidence | FR-001, FR-004 | SCR-CM-001, SCR-CM-004 |
| UC-CM-006 | Register Complaint after duplicate warning override | FR-001, FR-003 | SCR-CM-001, SCR-CM-003 |
| UC-CM-007 | Abandon create, link to existing, transfer staged evidence | FR-001, FR-003, FR-004 | SCR-CM-001, SCR-CM-003, SCR-CM-004 |
| UC-CM-008 | Identify customer then open Batch 1 Customer 360 minimum | FR-002 | SCR-CM-006 |
| UC-CM-009 | Idempotent replay of create (Request Id / Channel Message Id) | FR-001 | SCR-CM-001 (system/channel) |

| Screen ID | Screen Name | Primary FR | Supporting FR |
|---|---|---|---|
| SCR-CM-001 | Create Complaint | FR-001 | FR-002, FR-003, FR-004 |
| SCR-CM-002 | Customer Search / Candidate Select | FR-002 | — |
| SCR-CM-003 | Duplicate Warning Dialog / Panel | FR-003 | FR-001 |
| SCR-CM-004 | Attachment Upload Panel | FR-004 | FR-001 |
| SCR-CM-005 | Create Complaint Confirmation | FR-001 | — |
| SCR-CM-006 | Customer Brief Profile + Batch 1 360 Minimum | FR-002 | FR-001 |

---

## 7. API ↔ UC ↔ FR Matrix

> Logical Batch 1 APIs. Payload/OpenAPI authorship remains out of FRD scope. Catalog collisions `API-390` / `API-392` are highlighted in §14 — cite **path+method** (DEC-020). Aggregate intake is `/api/v1/cm` (API-500…512).

| API ID | Logical Capability | Path / Catalog Ref | FR | Mapped Use Case(s) | Status |
|---|---|---|---|---|---|
| API-CM-B1-001 | Create Complaint (idempotent) | `API-500` `POST /api/v1/cm/complaints` | FR-001 | UC-CM-001, UC-CM-005, UC-CM-006, UC-CM-009 | Implemented (lab) |
| API-CM-B1-002 | Get Complaint confirmation/detail | `API-501` `GET /api/v1/cm/complaints/{complaintId}` | FR-001 | UC-CM-001, UC-CM-009 | Implemented (lab) |
| API-CM-B1-003 | Search Customer by key | `API-502` `POST /api/v1/cm/customers/search` | FR-002 | UC-CM-002, UC-CM-008 | Implemented (lab) |
| API-CM-B1-004 | Confirm / lock CustomerId | `API-503` `POST /api/v1/cm/customers/confirm` | FR-002 | UC-CM-002 | Implemented (lab) |
| API-CM-B1-005 | Batch 1 Customer 360 minimum | `API-504` `GET /api/v1/cm/customers/{customerId}/batch1-360` | FR-002 | UC-CM-008 | Implemented (lab) |
| API-CM-B1-006 | Check duplicate candidates | `API-505` `POST /api/v1/cm/duplicates/check` | FR-003 | UC-CM-003, UC-CM-006, UC-CM-007 | **Implemented (lab)** |
| API-CM-B1-007 | Record duplicate decision / linkage | `API-506` `POST /api/v1/cm/duplicates/decisions` | FR-003 | UC-CM-003, UC-CM-006, UC-CM-007 | **Implemented (lab)** |
| API-CM-B1-008 | Upload attachment | `API-323` / `API-507` `POST /api/v1/attachments` | FR-004 | UC-CM-004, UC-CM-005, UC-CM-007 | **Implemented (lab; shared CAP)** |
| API-CM-B1-009 | Transfer staged attachments | `API-508` `POST /api/v1/cm/attachments/transfer` | FR-004 | UC-CM-007 | **Implemented (lab)** |
| API-CM-B1-010 | List attachments for Complaint | `API-387` / `API-509` `GET /api/v1/complaints/{id}/attachments` | FR-004 | UC-CM-004 | **Implemented (lab; shared listing)** |
| API-CM-B1-011 | Get attachment metadata | `API-324` / `API-510` `GET /api/v1/attachments/{id}` | FR-004 | UC-CM-004 | **Implemented (lab; shared)** |
| API-CM-B1-012 | Download attachment | `API-325` / `API-511` `GET /api/v1/attachments/{id}/download` | FR-004 | UC-CM-004 | **Implemented (lab; shared)** |
| API-CM-B1-013 | Logical void | `API-326` / `API-512` (semantics MUST match BR-012 void) | FR-004 | UC-CM-004 | **Implemented (lab; shared void)** |
| API-CM-B1-014 | Supervisor later-review / no-Case aging queue | `API-513` `GET /api/v1/cm/supervisor/queue` | FR-001 | UC-CM-001 (visibility) | **Implemented (lab; read-only)** |
| API-CM-B1-015 | List Aggregate Complaints | `API-514` `GET /api/v1/cm/complaints` | FR-001 | UC-CM-001 | **Implemented (lab; coexistence)** |
| API-CM-B1-016 | Intake escalation approve/reject | `API-515` `POST /api/v1/cm/complaints/{id}/intake-escalation/decision` | FR-001 | UC-CM-001 | **Implemented (lab; disposition only, no Case)** |

### 7.1 Requirement check

| Rule | Result |
|---|---|
| Every Batch 1 API maps to ≥1 Use Case | ✅ PASS |

---

## 8. Domain Model ↔ FR ↔ DB Entity Matrix

| DM ID | Domain Entity | BR | FR | Logical DB Entity | Notes |
|---|---|---|---|---|---|
| DM-CM-001 | Complaint (Aggregate Root) | BR-001, BR-016, BR-017, BR-018 | FR-001 | DB-CM-001 Complaint | Aggregate Root |
| DM-CM-002 | Customer Reference (`CustomerId`) | BR-002 | FR-002, FR-001 | DB-CM-001 (CustomerId field) | Not Customer SoR |
| DM-CM-003 | Customer Read-Model Projection | BR-002, BR-010 | FR-002 | DB-CM-002 Customer read-model/cache | Non-SoR; `asOf` |
| DM-CM-004 | Duplicate Candidate / Linkage | BR-014, BR-003, BR-018 | FR-003, FR-001 | DB-CM-003 Duplicate linkage; DB-CM-004 Eval result | |
| DM-CM-005 | Attachment | BR-012, BR-007 | FR-004, FR-001 | DB-CM-005 Attachment metadata; DB-CM-006 Binary (ext.) | |
| DM-CM-006 | Attachment History | BR-012, BR-016 | FR-004 | DB-CM-007 Attachment History | Append-only |
| DM-CM-007 | Audit Trail Record | BR-016 | FR-001…FR-004 | DB-CM-008 Audit record | |
| DM-CM-008 | Timeline Entry | BR-017 | FR-001, FR-004 | DB-CM-009 Timeline entry | |
| DM-CM-009 | Case | BR-004 | **Deferred Batch 2** | — | Not created in Batch 1 |
| DM-CM-010 | Idempotency Record | BR-001 (intake integrity) | FR-001 | DB-CM-010 Idempotency record | D-03; OQ-012/013 |
| DM-CM-011 | Complaint Search Index | BR-003 | FR-003 | DB-CM-011 Complaint search index | OQ-011 |
| DM-CM-012 | Notification Outbox | ADR-009 (no BR) | FR-001 | DB-CM-012 Notification outbox | Cross-cutting |

### 8.1 Additional logical stores (FR §14)

| DB ID | Logical Store | FR | DM affinity |
|---|---|---|---|
| DB-CM-013 | Pending key context (UNVERIFIED) | FR-002, FR-001 | DM-CM-002 |
| DB-CM-014 | Supervisor aging / later-review work item | FR-001, FR-003, FR-004 | DM-CM-001 / DM-CM-004 |
| DB-CM-015 | Staging token / transfer record | FR-004 | DM-CM-005; OQ-014 |

### 8.2 Requirement check

| Rule | Result |
|---|---|
| Every in-scope Domain Entity maps to ≥1 FR | ✅ PASS (DM-CM-009 explicitly deferred, not in Batch 1 create scope) |

---

## 9. Events ↔ FR Matrix

> Logical Batch 1 events derived from FRD audit/timeline requirements. Publishing into `08 Event Catalog` is a follow-on catalog change (not performed by this RTM).

| Event ID | Event Name | FR | Trigger | Catalog status |
|---|---|---|---|---|
| EVT-CM-001 | ComplaintCreated | FR-001 | Successful create | Planned |
| EVT-CM-002 | CreateReplayed | FR-001 | Idempotent Request Id / Channel Message Id replay | Planned |
| EVT-CM-003 | CreateRedirectedToExisting | FR-001 / FR-003 | Duplicate redirect (D-06) | Planned |
| EVT-CM-004 | DuplicateCheckOutcomeRecorded | FR-001 / FR-003 | none / warned / overridden / blocked / redirected | Planned |
| EVT-CM-005 | NotificationOutboxEnqueued | FR-001 | Opt-in notify after create | Planned |
| EVT-CM-010 | CustomerValidated | FR-002 | Successful search/confirm | Planned |
| EVT-CM-011 | CustomerValidationFailed | FR-002 | not found / ambiguous / degraded / blocked | Planned |
| EVT-CM-012 | CustomerReferenceEnriched | FR-002 | UNVERIFIED → verified enrichment | Planned |
| EVT-CM-020 | DuplicateWarned | FR-003 | Candidates ≥ threshold | Planned |
| EVT-CM-021 | DuplicateOverridden | FR-003 | Authorized override | Planned |
| EVT-CM-022 | DuplicateLinked | FR-003 | Link/related decision | Planned |
| EVT-CM-023 | DuplicateRedirectedToExisting | FR-003 | Redirect path | Planned |
| EVT-CM-024 | DuplicateRecommendedExisting | FR-003 | Recommend-only (no Case) | Planned |
| EVT-CM-025 | DuplicateCheckDegraded | FR-003 | Index/timeout degradation | Planned |
| EVT-CM-026 | DuplicateLaterReviewEnqueued | FR-003 | Later-review work item | Planned |
| EVT-CM-030 | AttachmentUploaded | FR-004 | ACTIVE bind | Planned |
| EVT-CM-031 | AttachmentSuperseded | FR-004 | Version replace | Planned |
| EVT-CM-032 | AttachmentVoided | FR-004 | Void-with-reason | Planned |
| EVT-CM-033 | AttachmentTransferred | FR-004 | Staged → surviving Complaint (D-06) | Planned; OQ-014 |
| EVT-CM-034 | AttachmentAccess | FR-004 | Sensitive download/access | Planned |

**Removed from Batch 1:** `ResolvedAsCaseOnExisting` (CTO D-02).

---

## 10. Security Controls ↔ FR Matrix

| Control ID | Control | Originating FR | Source in FRD | Owner |
|---|---|---|---|---|
| SEC-CM-001-01 | ECMP-internal authentication + authorization before create | FR-001 | §16.1, §22 | ECMP / ADR-008 |
| SEC-CM-001-02 | Request Id idempotency | FR-001 | §9.9, §12, §22 | ECMP Backend |
| SEC-CM-001-03 | Channel Message Id replay detection | FR-001 | E9, A6, §22 | ECMP Backend |
| SEC-CM-001-04 | Double-submit protection (human + channel) | FR-001 | A6 | ECMP Backend + client |
| SEC-CM-001-05 | Input validation (injection resistance) | FR-001 | §12, §22 | ECMP Backend |
| SEC-CM-001-06 | Need-to-know + masking on create display | FR-001 | §16.2 | ECMP Backend / UI |
| SEC-CM-001-07 | Sensitive override-justification ACL | FR-001 / FR-003 | FR-001 §16.3; FR-003 §16 | ECMP |
| SEC-CM-001-08 | Frontend → ECMP Backend only | FR-001 | §16.5 | Frontend / Backend |
| SEC-CM-001-09 | Security audit on authz failure and replay | FR-001 | §17, §22 | ECMP (BR-016) |
| SEC-CM-001-10 | Notification outbox (no rollback side-channel) | FR-001 | §18, DM-CM-012 | ECMP (ADR-009) |
| SEC-CM-002-01 | Rate limiting (enumeration) | FR-002 | §16.1 | Enterprise Security + ECMP |
| SEC-CM-002-02 | Progressive delay | FR-002 | §16.1 | Enterprise Security + ECMP |
| SEC-CM-002-03 | Abuse detection | FR-002 | §16.1 | Enterprise Security / SOC |
| SEC-CM-002-04 | Security audit for enumeration outcomes | FR-002 | §16.1, §17 | ECMP + SOC sink |
| SEC-CM-002-05 | Alerting on abuse thresholds | FR-002 | §16.1, §18 | Enterprise Security / SOC |
| SEC-CM-002-06 | Fail-closed if anti-enumeration unavailable | FR-002 | §16.1 | ECMP Backend |
| SEC-CM-002-07 | Unconditional audit masking (no cleartext ID) | FR-002 | §16.1, §17 | ECMP |
| SEC-CM-002-08 | Need-to-know search results + reject-closed authz | FR-002 | §16.2–16.4 | ECMP |
| SEC-CM-002-09 | Exactly-one key type enforcement | FR-002 | §3, E5, AC-7 | ECMP Backend |
| SEC-CM-003-01 | Authorization-scoped candidate visibility | FR-003 | §16.1 | ECMP |
| SEC-CM-003-02 | Anti-inference uniform-empty MUST | FR-003 | E4, §16.4 | ECMP |
| SEC-CM-003-03 | Override justification restricted read | FR-003 | §16.2 | ECMP |
| SEC-CM-003-04 | Backend-only duplicate APIs | FR-003 | §16.3 | Frontend / Backend |
| SEC-CM-003-05 | Candidate cap + timeout | FR-003 | §12 | ECMP |
| SEC-CM-003-06 | Degraded mode → mandatory later-review work item | FR-003 | E1, §22 | ECMP |
| SEC-CM-004-01 | MIME/extension allowlist + size + aggregate caps | FR-004 | §12, §22 | ECMP + Admin config |
| SEC-CM-004-02 | Malware scan when configured | FR-004 | §16.1, E2 | ECMP + Scan dependency |
| SEC-CM-004-03 | Integrity hash MUST for ACTIVE | FR-004 | §12, AC-1 | ECMP |
| SEC-CM-004-04 | Void/transfer — no physical user delete | FR-004 | E3, §15, D-06 | ECMP |
| SEC-CM-004-05 | Anchor membership invariant (Case ∈ Complaint) | FR-004 | §9.4, E7 | ECMP |
| SEC-CM-004-06 | Audited sensitive attachment access MUST | FR-004 | §16.5, EVT-CM-034 | ECMP |
| SEC-CM-004-07 | Backend-only storage access; no public unauth links | FR-004 | §16.3, AC-7 | ECMP + Storage |
| SEC-CM-004-08 | Classification-based access rights | FR-004 | §16.4 | ECMP |

### 10.1 Requirement check

| Rule | Result |
|---|---|
| Every Security Control references originating FR | ✅ PASS |

---

## 11. Acceptance Criteria ↔ Test Cases

> Test Cases are **Planned** IDs for Batch 1 implementation/QA. They are not yet in the Sprint delivery TC catalog (namespace collision caveat applies under **DEC-020** dual SoT — qualify as TC-CM-* / FRD-CM-001).

### 11.1 FR-001 — Complaint Registration

| AC ID | Acceptance Criteria (summary) | Test Case ID | Priority |
|---|---|---|---|
| AC-CM-FR001-01 | Authorized create → REGISTERED Complaint, unique number, **no Case** | TC-CM-FR001-01 | Must |
| AC-CM-FR001-02 | Stores CustomerId only (not Master attributes as SoR) | TC-CM-FR001-02 | Must |
| AC-CM-FR001-03 | Immutable audit + Timeline “Complaint Created” | TC-CM-FR001-03 | Must |
| AC-CM-FR001-04 | Missing mandatory attributes → reject with field errors | TC-CM-FR001-04 | Must |
| AC-CM-FR001-05 | Unauthorized → reject + security audit | TC-CM-FR001-05 | Must |
| AC-CM-FR001-06 | Duplicate override rules (reject without justification / succeed with audit) | TC-CM-FR001-06 | Must |
| AC-CM-FR001-07 | Duplicate redirect transfers staged evidence (no discard) | TC-CM-FR001-07 | Must |
| AC-CM-FR001-08 | Strict mode + Master Customer down → reject create | TC-CM-FR001-08 | Must |
| AC-CM-FR001-09 | Notification down → Complaint remains; ECMP outbox records failure | TC-CM-FR001-09 | Must |
| AC-CM-FR001-10 | Repeated Request Id → no new Aggregate; original outcome returned | TC-CM-FR001-10 | Must |
| AC-CM-FR001-11 | Repeated Channel Message Id → no new Aggregate | TC-CM-FR001-11 | Must |
| AC-CM-FR001-12 | Confirm presents Batch 1 Customer 360 minimum | TC-CM-FR001-12 | Must |

### 11.2 FR-002 — Customer Search

| AC ID | Acceptance Criteria (summary) | Test Case ID | Priority |
|---|---|---|---|
| AC-CM-FR002-01 | Unique Customer Number → lock CustomerId + 360 minimum | TC-CM-FR002-01 | Must |
| AC-CM-FR002-02 | Multiple matches → no lock until selection | TC-CM-FR002-02 | Must |
| AC-CM-FR002-03 | No match → normal FR-001 create rejected (unless UNVERIFIED policy) | TC-CM-FR002-03 | Must |
| AC-CM-FR002-04 | Master Customer write-back rejected | TC-CM-FR002-04 | Must |
| AC-CM-FR002-05 | Strict unavailable → degraded/unavailable; no invented customer | TC-CM-FR002-05 | Must |
| AC-CM-FR002-06 | Frontend calls Backend only | TC-CM-FR002-06 | Must |
| AC-CM-FR002-07 | Two key types in one request → reject | TC-CM-FR002-07 | Must |
| AC-CM-FR002-08 | Enumeration threshold → delay/block + audit + alert | TC-CM-FR002-08 | Must |
| AC-CM-FR002-09 | Profile/`asOf` freshness shown | TC-CM-FR002-09 | Must |

### 11.3 FR-003 — Duplicate Detection

| AC ID | Acceptance Criteria (summary) | Test Case ID | Priority |
|---|---|---|---|
| AC-CM-FR003-01 | Open candidate in window → warning with candidates | TC-CM-FR003-01 | Must |
| AC-CM-FR003-02 | Open/link existing → no new Aggregate, no Case | TC-CM-FR003-02 | Must |
| AC-CM-FR003-03 | Continue without required justification → reject | TC-CM-FR003-03 | Must |
| AC-CM-FR003-04 | Override with justification → create + linkage + audit | TC-CM-FR003-04 | Must |
| AC-CM-FR003-05 | Hard-block category → reject create | TC-CM-FR003-05 | Must |
| AC-CM-FR003-06 | Index unavailable → degraded flag + later-review work item | TC-CM-FR003-06 | Must |
| AC-CM-FR003-07 | Out-of-scope candidates → uniform empty (anti-inference) | TC-CM-FR003-07 | Must |
| AC-CM-FR003-08 | Any Batch 1 duplicate flow → no Case created | TC-CM-FR003-08 | Must |

### 11.4 FR-004 — Attachment Upload

| AC ID | Acceptance Criteria (summary) | Test Case ID | Priority |
|---|---|---|---|
| AC-CM-FR004-01 | Allowlisted upload → ACTIVE + hash + history/timeline/audit | TC-CM-FR004-01 | Must |
| AC-CM-FR004-02 | Illegal type/size → reject; no ACTIVE | TC-CM-FR004-02 | Must |
| AC-CM-FR004-03 | Malware failure → reject + security audit | TC-CM-FR004-03 | Must |
| AC-CM-FR004-04 | Physical delete rejected; void-with-reason only | TC-CM-FR004-04 | Must |
| AC-CM-FR004-05 | Supersede → prior SUPERSEDED and retrievable | TC-CM-FR004-05 | Must |
| AC-CM-FR004-06 | Escalation later → prior attachments still visible (No Information Lost) | TC-CM-FR004-06 | Must |
| AC-CM-FR004-07 | Frontend uses Backend attachment APIs only | TC-CM-FR004-07 | Must |
| AC-CM-FR004-08 | Duplicate redirect transfer → bound to survivor + audit; no discard | TC-CM-FR004-08 | Must |
| AC-CM-FR004-09 | CaseId not in Complaint → reject | TC-CM-FR004-09 | Must |

### 11.5 Requirement check

| Rule | Result |
|---|---|
| Every AC maps to ≥1 Test Case | ✅ PASS (38 AC → 38 Planned TC, 1:1) |

---

## 12. Open Questions (Not Blocking / Future Decision)

Per CTO D-08 and FRD §18.1 — these do **not** block RTM approval or Batch 1 FR LOCK. Resolve via ADR/DEC during detailed design.

| OQ ID | Topic | Impacted FR / DM | Blocking? | Disposition |
|---|---|---|---|---|
| OQ-CM-B1-001 | Dual SoT / DEC remapping | Namespace / implementation sequencing | **Closed** | **DEC-020** — Closed — remapped by dual SoT |
| OQ-CM-B1-012 | Request Id / Channel Message Id lifetime (TTL) | FR-001 / DM-CM-010 / SEC-CM-001-02 | **Not Blocking** | Future Architecture Decision |
| OQ-CM-B1-013 | Request Id generation authority (client / gateway / Backend) | FR-001 / SCR-CM-001 / SEC-CM-001-02 | **Not Blocking** | Future Architecture Decision |
| OQ-CM-B1-014 | Attachment `TRANSFERRED` status semantics | FR-004 / EVT-CM-033 / DB-CM-015 | **Not Blocking** | Future Architecture Decision |

Other FRD OQs (002–011, 007 v1.2) remain tracked in FRD §18; they are outside this RTM close-set but do not invalidate Batch 1 FR coverage.

---

## 13. Orphan Items

### 13.1 Blocking orphans (Batch 1)

| Item | Type | Finding |
|---|---|---|
| — | — | **None.** No in-scope Batch 1 FR/BR/UC/Screen/API/DM/SEC/AC lacks a required reverse link. |

### 13.2 Non-blocking / deferred (highlighted for awareness)

| Item | Type | Finding | Action |
|---|---|---|---|
| BR-004…BR-006, BR-009, BR-011, BR-013, BR-015, BR-019, BR-020 | BR | Not consumed by Batch 1 FR | Deferred by scope (expected) |
| DM-CM-009 Case | DM | Explicitly deferred Batch 2 | No Batch 1 create |
| DM-CM-012 Notification Outbox | DM | No BR (ADR-009) | Acceptable ADR-linked entity |
| EVT-CM-* | Event | Not yet published to Event Catalog | Catalog follow-on (implementation gate) |
| TC-CM-* | Test | Planned IDs only | Author under Test Strategy after CTO RTM approval |
| API-CM-B1-006…007, 009 | API | Planned Aggregate capabilities | OpenAPI catalog update before code |
| BR-018 | BR | Consumed by FR-001/002/003 but omitted from FRD §15 reverse-mapping table | **Documentation gap in FRD reverse table** — RTM corrects coverage here; do not treat as missing FR consumption |
| Sprint delivery FR/BR/API/TC IDs | Namespace | Parallel SoT under DEC-020 coexistence | **DEC-020** (OQ-CM-B1-001 Closed) |

---

## 14. Duplicate Mappings

### 14.1 Expected (non-defect) multi-maps

| Pattern | Example | Verdict |
|---|---|---|
| One FR → many UC | FR-001 → UC-CM-001/005/006/007/009 | Expected |
| One BR → many FR | BR-016 → FR-001…004 | Expected |
| One UC → many FR | UC-CM-007 → FR-001+003+004 | Expected composite flow |
| One Screen → many FR | SCR-CM-001 supports FR-002/003/004 | Expected |

### 14.2 Defect / collision highlights

| ID | Issue | Severity | Disposition |
|---|---|---|---|
| `API-390` | Catalog collision: complaint create **and** dashboard queue | High (automation) | Cite path+method (DEC-020); Aggregate create = `POST /api/v1/cm/complaints` (`API-500` / `API-CM-B1-001`) |
| `API-392` | Catalog collision: complaint get **and** dashboard notifications | High (automation) | Cite path+method; Aggregate get = `GET /api/v1/cm/complaints/{complaintId}` (`API-501` / `API-CM-B1-002`) |
| `FR-001` / `BR-001` | Namespace collision vs Sprint delivery SoT | High (implementation) | **DEC-020** dual SoT; RTM uses CM Aggregate meaning only + path+method |
| `API-326` vs BR-012 | Catalog “logical delete” vs BR void-with-reason wording | Medium | Semantics MUST align to BR-012 void (FRD §13 note) |

---

## 15. Coverage Summary

| Dimension | In-scope items | Covered | Coverage | Notes |
|---|---|---|---|---|
| **BR Coverage** | 11 consumed Batch 1 BRs | 11 / 11 | **100%** | 9 catalog BRs deferred out of Batch 1 |
| **FR Coverage** | FR-001…FR-004 | 4 / 4 | **100%** | Each has BR, UC, Screen, API, DM, SEC, AC, TC |
| **UC Coverage** | UC-CM-001…009 | 9 / 9 | **100%** | All map to ≥1 FR and ≥1 Screen |
| **API Coverage** | API-CM-B1-001…013 | 13 / 13 | **100%** | All map to ≥1 UC; path+method under DEC-020; FR-003/004 Planned |
| **Domain Coverage** | DM-CM-001…008, 010…012 | 11 / 11 in-scope | **100%** | DM-CM-009 deferred Batch 2 |
| **Security Coverage** | SEC-CM-001/002/003/004 controls | 33 / 33 | **100%** | Each cites originating FR |
| **Test Coverage** | AC-CM-* (38) | 38 / 38 Planned TC | **100% Planned** | Execution coverage = 0% until TC authored |

### 15.1 Visual summary

```text
BR (Batch 1 consumed)     ██████████ 100%
FR                        ██████████ 100%
UC                        ██████████ 100%
API (logical)             ██████████ 100%
Domain (in-scope)         ██████████ 100%
Security                  ██████████ 100%
AC → TC (planned)         ██████████ 100%
AC → TC (executed)        ░░░░░░░░░░   0%  (post-RTM QA work)
```

### 15.2 Gate recommendation

| Gate | Recommendation |
|---|---|
| RTM completeness (design-time) | **PASS** — Ready for CTO Review |
| Implementation start | Allowed against FRD-CM-001 LOCKED + this RTM |
| Catalog publish (Events / Planned APIs) | Required before coding those capabilities |
| Test execution coverage | Required before Batch 1 UAT exit |

---

## 16. RTM Validation Report

| Field | Value |
|---|---|
| Report ID | GOV-VAL-RTM-CM-B1-001 |
| Subject | RTM-CM-B1-001 v1.0 |
| Date | 2026-07-29 |
| Validator role | Requirements Manager / Solution Architect / QA Lead |
| Status | 🔒 LOCKED — CTO Approval applied (S0) |

### 16.1 Validation checklist

| # | Requirement | Result | Evidence |
|---|---|---|---|
| 1 | Every FR traces to ≥1 BR | ✅ PASS | §4, §5 |
| 2 | Every Batch 1–consumed BR maps to ≥1 FR | ✅ PASS | §5.1 |
| 3 | Every AC maps to ≥1 TC | ✅ PASS | §11 (Planned TC) |
| 4 | Every API maps to a UC | ✅ PASS | §7 |
| 5 | Every in-scope Domain Entity maps to ≥1 FR | ✅ PASS | §8 |
| 6 | Every Security Control references originating FR | ✅ PASS | §10 |
| 7 | OQ-CM-B1-012/013/014 recorded as Not Blocking / Future Decision | ✅ PASS | §12 |
| 8 | Orphans highlighted | ✅ PASS | §13 (none blocking) |
| 9 | Duplicate mappings highlighted | ✅ PASS | §14 |
| 10 | Coverage Summary produced | ✅ PASS | §15 |
| 11 | FRD / BR / ADR / Batch 1 scope unmodified by this artifact | ✅ PASS | Documentation-only |

### 16.2 Findings

| ID | Severity | Finding | Disposition |
|---|---|---|---|
| V-01 | Info | 38 Test Cases are Planned IDs — not yet authored in Test Strategy | Accept for RTM; QA follow-on |
| V-02 | Info | EVT-CM-* not yet in Event Catalog | Accept; catalog sync before emit |
| V-03 | Medium | Catalog ID collisions API-390 / API-392 | Tracked §14; path+method interim |
| V-04 | Info | BR-018 missing from FRD §15 reverse table | RTM §5 covers; FRD unchanged per instruction |
| V-05 | Info | OQ-012/013/014 remain open | Not Blocking per D-08 |

### 16.3 Verdict

**LOCKED (S0).**

Design-time Batch 1 traceability is complete against FRD-CM-001 v1.1 LOCKED. No blocking orphans. Planned API/Event/TC published in S0 Contract Pack — implementation may proceed against this RTM + FRD.

---

## 17. Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-29 | Requirements Manager / QA Lead | Initial Batch 1 RTM from FRD-CM-001 v1.1 LOCKED; Validation Report + Coverage Summary; Ready for CTO Review |
| 1.0 LOCKED | 2026-07-29 | Requirements Manager / CTO | Status → LOCKED (S0); API/Event/TC publication referenced |
| 1.0 LOCKED + DEC-020 sync | 2026-07-30 | Documentation Architect | PROGRAM-DOC-001: §7 path+method → `/api/v1/cm` (API-500…512); OQ-CM-B1-001 Closed via DEC-020; no FR/BR change |

---

## Related

- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (LOCKED SoT)
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md`
- `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Delta_Review_v1.1.md`
- `18 Architecture Governance/reviews/ECMP_FRD_CM_001_v1.1_LOCKED_Release_Notes.md`
- `18 Architecture Governance/reviews/ECMP_CM_Batch1_S0_Contract_Pack_v1.0.md`
- `07 API Catalog/openapi/complaint-management-batch1.v1.yaml`
- `27 Project Decisions/DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md`
- `13 Test Strategy/ECMP_Test_Case_Catalog_CM_Batch1_v1.0.md`
- `26 Traceability/TRACEABILITY_MATRIX.md` (Sprint delivery SoT — separate namespace; DEC-020 coexistence)

---

*End of RTM-CM-B1-001 v1.0 LOCKED — Source of Truth for Batch 1 traceability.*
