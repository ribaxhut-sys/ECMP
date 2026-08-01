# ECMP Functional Requirements Document — Complaint Management Escalation & Resolution

| Field | Value |
|---|---|
| Document ID | FRD-CM-002 |
| Title | Complaint Management Module — Escalation & Resolution (DEC-F4) |
| Version | 0.1 |
| Status | 🟡 Draft |
| Owner | Business Analyst / Domain PO ECMF |
| Reviewer | Solution Architect, Operations Lead, Security |
| Approver | Business Owner / Architecture Board (pending countersign DEC-F4) |
| Module | Complaint Management Module only |
| Last Review | 2026-07-29 |
| Next Review | 2026-10-29 |
| Related DEC | GOV-DEC-F4 |
| Related BR | BR-CM-CAT-001 v1.1 — BR-007, BR-008 |
| Related ADRs | ADR-014, ADR-015, ADR-002, ADR-008, ADR-009 |
| Related Impact | GOV-IMPACT-DEC-F4 |
| Related UAT | TC-CAT-CM-F4-001 |
| Related OpenAPI | `07 API Catalog/openapi/complaint-management-esc-res.v1.yaml` |
| Does not modify | FRD-CM-001 v1.1 LOCKED |

---

## 1. Document Control

### 1.1 Purpose

Define Draft functional requirements for:

1. Escalating a **Case** from Cabang to Pusat (No Information Lost)
2. Returning an incomplete escalation to the originating branch
3. Pusat work-queue visibility (model B)
4. Resolving a Case at Pusat with `result_visibility`
5. Changing `result_visibility` after Resolve
6. Enforcing read scope for other branches

### 1.2 Dependencies

| Dependency | Requirement |
|---|---|
| Case exists under Complaint Aggregate | Case create/assignment MUST exist (Batch 2+ / foundation Case path). This FRD does **not** redefine Case create. |
| DEC-F4 | Normative business decisions F4…F4.5 + F4-OQ-01/02 |
| BR-007 / BR-008 | Normative business rules (Draft catalog) |
| Identity / org claims | `branch_id` (and related) available for authorization |

### 1.3 Quality rules

- RFC-2119: **MUST**, **SHALL**, **SHOULD**, **MAY**
- No Customer Master write-back
- Frontend → ECMP Backend only
- No Regional escalate target under DEC-F4
- Batch 1 FR-001…FR-004 unchanged

### 1.4 OQ closures applied

| ID | Closure |
|---|---|
| F4-OQ-01 | `return_note` minimum length **10** (trim, then count) |
| F4-OQ-02 | Originating branch **read-only** while Case owned by Pusat; write restored after Return |

---

## 2. Scope

### In scope

- FR-CM-010…FR-CM-015 (this document)
- Planned API-520…526 / API-CM-F4-001…007
- Planned EVT-CM-040…044
- UAT-F4-01…11

### Out of scope

- Regional escalation path
- Complaint Closure aggregate rules beyond Case resolve side-effects (BR-009 detail remains separate)
- SSO protocol selection
- Batch 1 intake redesign
- Implementation against foundation complaint escalate APIs (API-207/301…) — separate namespace under DEC-020 coexistence (not interchangeable with Aggregate `/api/v1/cm`)

---

## 3. Actors

| Actor | Capabilities in this FRD |
|---|---|
| Branch Agent / Supervisor (origin) | Escalate to Pusat; read while at Pusat; write after Return; always read after Pusat Resolve |
| Branch Agent (other) | Read resolved Case only if `result_visibility = ALL_BRANCHES` |
| Pusat Handler | Work escalated queue; Return; Resolve + set visibility; change visibility later |
| Pusat Analyst | KPI/monitoring per F4; detail access only with explicit permission |
| System | Validate package; emit events; enforce authZ |

---

## 4. FR Catalog Summary

| FR ID | Name | Primary BR | DEC |
|---|---|---|---|
| FR-CM-010 | Escalate Case to Pusat | BR-007 | F4.1 |
| FR-CM-011 | Return Escalation | BR-007 A4/E6 | F4.4, F4.5, OQ-01/02 |
| FR-CM-012 | Pusat Escalated Work Queue | BR-007 | F4 |
| FR-CM-013 | Resolve Case with Result Visibility | BR-008 | F4.2, F4.3 |
| FR-CM-014 | Change Result Visibility | BR-008 A4 | F4.3a |
| FR-CM-015 | Visibility-Enforced Case Read | BR-007/008 | F4…F4.3 |

---

## 5. FR-CM-010 — Escalate Case to Pusat

### Statement

The system SHALL allow an authorized originating-branch actor to escalate an active Case to **Pusat**, transferring a complete Escalation Package without creating a new Case or Complaint identity.

### Acceptance criteria

1. Target MUST be Pusat only (Regional MUST NOT be offered/accepted under DEC-F4).
2. Escalation reason MUST be present.
3. System MUST assemble Escalation Package per BR-007 / Lampiran B.
4. Incomplete package MUST block successful escalate (or hold per E1) — empty Case transfer forbidden.
5. Escalation History append-only entry MUST record from/to/reason/actor/time.
6. Assignment MUST move to Pusat queue/handler (BR-005 semantics).
7. Originating branch MUST become **read-only** on the Case (F4-OQ-02).
8. Pusat handlers MUST see full prior branch history (No Information Lost).
9. Unauthorized escalate MUST fail with security audit.
10. EVT-CM-040 MUST be emitted on success.

### Security

Org-scope: only actors of owning branch (or permitted roles) may escalate. Privilege escalation across branches forbidden.

### API / Event

- API-520 / API-CM-F4-001  
- EVT-CM-040 CaseEscalatedToPusat  

---

## 6. FR-CM-011 — Return Escalation

### Statement

The system SHALL allow an authorized Pusat actor to return an escalated Case to the **originating branch** when information is incomplete, requiring a controlled reason code and free-text note.

### Acceptance criteria

1. Return allowed only while Case owned by Pusat.
2. Target MUST be originating branch only.
3. `return_reason_code` MUST be from catalog (baseline codes in DEC-F4).
4. `return_note` MUST be present with length ≥ **10** after trim (F4-OQ-01).
5. Missing code or note → reject (BR-007 E6).
6. History MUST retain Pusat work + return fields (append-only).
7. Ownership MUST return to originating branch; write restored (F4-OQ-02).
8. Case MUST leave Pusat handler work queue until re-escalated.
9. `result_visibility` MUST NOT be set by Return.
10. Notification to originating branch SHOULD be attempted; failure MUST NOT roll back committed return (retry via Notification Platform).
11. EVT-CM-041 MUST be emitted on success.
12. Re-escalate after completion MUST be allowed; package cumulative.

### API / Event

- API-521 / API-CM-F4-002  
- EVT-CM-041 CaseEscalationReturned  

---

## 7. FR-CM-012 — Pusat Escalated Work Queue

### Statement

The system SHALL present Pusat handlers a work queue limited to Cases escalated/assigned to Pusat (visibility model B).

### Acceptance criteria

1. Queue MUST exclude non-escalated Cases from branches.
2. Analyst/viewer roles MUST NOT gain handler write access solely via queue APIs.
3. Cross-branch KPI endpoints (if any) MUST remain separate from handler queue.
4. AuthZ failure → 403 + audit.

### API

- API-522 / API-CM-F4-003  

---

## 8. FR-CM-013 — Resolve Case with Result Visibility

### Statement

When a Pusat actor resolves an escalated Case, the system SHALL require (or default) `result_visibility` and SHALL always allow the originating branch to read the result.

### Acceptance criteria

1. Resolve MUST record resolution fields per BR-008.
2. For Pusat-owned escalated Case, `result_visibility` MUST be `ORIGIN_BRANCH` or `ALL_BRANCHES`.
3. If omitted, system MUST default to `ORIGIN_BRANCH`.
4. Originating branch MUST be able to read result after Resolve (F4.2).
5. Other branches MUST NOT read when `ORIGIN_BRANCH`.
6. Other branches MAY read-only when `ALL_BRANCHES`.
7. Return path MUST NOT be used to resolve.
8. EVT-CM-042 MUST be emitted (includes visibility).

### API / Event

- API-523 / API-CM-F4-004  
- EVT-CM-042 CaseResolvedWithVisibility  

---

## 9. FR-CM-014 — Change Result Visibility

### Statement

After Resolve, authorized Pusat actors MAY change `result_visibility`; every change MUST be audited and immediately enforced.

### Acceptance criteria

1. Allowed transitions: `ORIGIN_BRANCH` ↔ `ALL_BRANCHES`.
2. Audit MUST store from, to, actor, timestamp, optional change_note.
3. Enforcement on search/list/get/export MUST update immediately.
4. Unauthorized change → 403.
5. EVT-CM-043 MUST be emitted.

### API / Event

- API-524 / API-CM-F4-005  
- EVT-CM-043 ResultVisibilityChanged  

---

## 10. FR-CM-015 — Visibility-Enforced Case Read

### Statement

All Case read surfaces (get, list, search, export) MUST enforce org scope and `result_visibility`.

### Acceptance criteria

1. Non-escalated Case: visible only within owning branch scope (plus permitted Pusat analyst permissions if explicitly granted — default deny for handlers).
2. Escalated (owned by Pusat): Pusat handlers read/write per role; origin branch read-only.
3. After Resolve + `ORIGIN_BRANCH`: origin + Pusat read; other branches denied.
4. After Resolve + `ALL_BRANCHES`: other branches read-only; writes denied.
5. Direct-ID access MUST NOT bypass list filters (no IDOR).
6. Denials SHOULD be uniform (403 or empty per security policy) without leaking existence beyond policy.

### API

- API-525 Get Case (API-CM-F4-006)  
- API-526 Search/List Cases with visibility (API-CM-F4-007)  
- EVT-CM-044 CaseAccessDenied (optional/security) when denial is audited  

---

## 11. Mapping tables

### 11.1 API mapping

| Logical ID | Catalog ID | Method & path | FR |
|---|---|---|---|
| API-CM-F4-001 | API-520 | POST /api/v1/cm/cases/{caseId}/escalate-to-pusat | FR-CM-010 |
| API-CM-F4-002 | API-521 | POST /api/v1/cm/cases/{caseId}/return-escalation | FR-CM-011 |
| API-CM-F4-003 | API-522 | GET /api/v1/cm/pusat/escalated-queue | FR-CM-012 |
| API-CM-F4-004 | API-523 | POST /api/v1/cm/cases/{caseId}/resolve | FR-CM-013 |
| API-CM-F4-005 | API-524 | PATCH /api/v1/cm/cases/{caseId}/result-visibility | FR-CM-014 |
| API-CM-F4-006 | API-525 | GET /api/v1/cm/cases/{caseId} | FR-CM-015 |
| API-CM-F4-007 | API-526 | GET /api/v1/cm/cases | FR-CM-015 |

### 11.2 Event mapping

| Event ID | Name | FR |
|---|---|---|
| EVT-CM-040 | CaseEscalatedToPusat | FR-CM-010 |
| EVT-CM-041 | CaseEscalationReturned | FR-CM-011 |
| EVT-CM-042 | CaseResolvedWithVisibility | FR-CM-013 |
| EVT-CM-043 | ResultVisibilityChanged | FR-CM-014 |
| EVT-CM-044 | CaseAccessDenied | FR-CM-015 |

### 11.3 UAT mapping

See `13 Test Strategy/ECMP_UAT_Catalog_DEC_F4_v1.0.md` (UAT-F4-01…11).

### 11.4 BR mapping

| FR | BR |
|---|---|
| FR-CM-010 | BR-007 |
| FR-CM-011 | BR-007 |
| FR-CM-012 | BR-007 |
| FR-CM-013 | BR-008 |
| FR-CM-014 | BR-008 |
| FR-CM-015 | BR-007, BR-008 |

---

## 12. Open Questions

| ID | Topic | Owner | Status |
|---|---|---|---|
| OQ-CM-F4-001 | Convergence with foundation escalate APIs (API-207/301) vs Aggregate `/cm/` namespace | Solution Architect | Open (DEC remapping) |
| OQ-CM-F4-002 | Exact Case state machine labels for return (`ESCALATED` → `IN_PROGRESS` at branch) | BA | Open |
| OQ-CM-F4-003 | Whether denial responses use 404 vs 403 for other-branch probes | Security | Open (default recommend 403 + audit) |

F4-OQ-01 and F4-OQ-02 are **Closed** (see §1.4).

---

## 13. Document History

| Version | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-29 | Draft from DEC-F4 + outline; OQ-01/02 closed |

---

## Related

- `18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`
- `18 Architecture Governance/reviews/ECMP_DEC_F4_Architecture_Board_Countersign_Pack_v1.0.md`
- `03 Functional Requirements/ECMP_FRD_Complaint_Management_Escalation_Resolution_Outline_v0.1.md` (superseded as outline by this Draft for FR content)
- `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md`
