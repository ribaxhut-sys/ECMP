# FRD-CM-001 Revision Plan v1.1

| Field | Value |
|---|---|
| Document ID | GOV-RP-FRD-CM-001 |
| Title | FRD-CM-001 Revision Plan — Batch 1 v1.1 |
| Version | 1.1 |
| Status | 🟢 Approved — FRD-CM-001 v1.1 LOCKED (D-08) |
| Subject | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.0.md` (FRD-CM-001 Draft v1.0) |
| Evidence Review | `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Architecture_Review_v1.0.md` (GOV-REV-FRD-CM-001) |
| Review Status | Complete |
| Owner | Requirements Manager / Domain PO ECMF |
| Reviewer | Principal Enterprise Solution Architect |
| Approver | CTO / Architecture Board |
| Created | 2026-07-29 |
| Target FRD Version | FRD-CM-001 v1.1 |
| Next Gate | Complete — FRD-CM-001 v1.1 LOCKED (D-08) |

---

## 0. Purpose and Constraints

### 0.1 Purpose

This document is the **implementation plan for FRD v1.1**. It analyzes every finding from GOV-REV-FRD-CM-001 and defines what must change in the FRD specification — **without rewriting the FRD itself**.

### 0.2 Explicit Non-Goals

- Do **not** revise FRD-CM-001 text in this artifact
- Do **not** implement code, OpenAPI payloads, UI, or physical schema
- Do **not** redesign the Complaint Aggregate model

### 0.3 Locked Architecture (MUST NOT CHANGE)

The following remain **LOCKED** across all revision actions:

| # | Locked Decision |
|---|---|
| 1 | Complaint Aggregate Root |
| 2 | Multi Case (1..n Cases under Complaint) |
| 3 | Assignment on Case |
| 4 | SLA on Case |
| 5 | Working Day SLA |
| 6 | CustomerId-only (ECMP not Customer Master SoR) |
| 7 | Customer 360 (capability retained; Batch 1 subset may be clarified) |
| 8 | API First |
| 9 | No Direct Database Access |
| 10 | No Information Lost During Escalation |

### 0.4 Verdict Premise (from GOV-REV-FRD-CM-001)

FRD-CM-001 is architecturally sound. Findings are **corrections and completions** within the existing structure. Six gating items (`C-01`…`C-06`) stand between Draft v1.0 and a safe v1.1 baseline. None require redesign.

---

## 1. Executive Summary for CTO

| Metric | Value |
|---|---|
| Critical findings | 6 |
| Major findings | 17 |
| Minor findings | 13 |
| Total actionable findings | 36 |
| Gating before FRD rewrite | `C-01`…`C-06` + Decision Matrix items marked **Need Business / Architecture / Security Decision** |
| Estimated FRD revision complexity | Medium (specification completion; no Aggregate redesign) |
| Recommended sprint split | 3 sprints of specification work (not code) |
| Residual risk if plan rejected | Implementation against unratified foundation; permanent duplicates; regulatory exposure on identity enumeration |

**CTO ask:** Approve this Revision Plan (Accept / Clarify / Move / Reject per Decision Matrix). Only then authorize FRD-CM-001 v1.1 authoring.

---

## 2. Finding-by-Finding Analysis

Legend for **Status** in this plan: `Open` until Revision Plan approved and FRD v1.1 lands.  
**Target Version** defaults to `FRD-CM-001 v1.1` unless Decision Matrix moves the item.

---

### 2.1 Critical Findings

#### C-01 — LOCKED decisions rest on unratified documents

| Field | Content |
|---|---|
| Finding ID | C-01 |
| Title | LOCKED decisions rest entirely on unratified documents, yet FRD claims implementation-readiness |
| Category | Governance / Foundation |
| Severity | Critical |
| Description | §3 declares thirteen decisions LOCKED while items 1–11 rest on BR-CM-CAT-001 (Draft), items 12–13 on ADR-014/015 (Proposed), and the DEC that would ratify the catalog is the FRD’s own open question OQ-CM-B1-001. §2.1 still calls the deliverable “implementation-ready”. |
| Current Situation | FRD presents LOCKED + implementation-ready language over Draft BR + Proposed ADRs + absent DEC. |
| Expected Situation | Either (a) obtain DEC + ADR-014/015 acceptance before claiming readiness, or (b) restate §2.1 as “specification baseline, pending DEC” and keep LOCKED as *intent-locked for Batch 1*, not *governance-frozen*. |
| Root Cause | Sequencing inversion: FRD authored as if foundation were already frozen; repository gate requires contract freeze before code. |
| Recommended Action | Decide Accept path: close OQ-CM-B1-001 with DEC date **or** downgrade readiness claim; track ADR-014/015 acceptance as dependency. Do not start implementation planning from FRD until one path is chosen. |
| Affected Sections | §2.1 Purpose; §3 Locked Architecture Decisions; §18 OQ-CM-B1-001; Document Control Status |
| Business Rules | BR-CM-CAT-001 status (Draft → Approved via DEC) |
| Functional Requirements | All FR-001…FR-004 (normative force of document) |
| Use Cases | UC-CM-001…008 (baseline authority) |
| API Mapping | §13 (implementation sequencing against Sprint SoT vs Aggregate SoT) |
| Database Mapping | §14 (same sequencing risk) |
| Traceability | §1.1 namespace; §16 RTM authority |
| Architecture Impact | None on Aggregate model; governance sequencing only. Depends on GOV-REV-014 / ADR-014 / ADR-015. |
| Risk if not fixed | Teams build against unratified model while Sprint delivery SoT still governs live code; ID/namespace collision and rework. |
| Priority | P0 — Gating |
| Owner | Business Owner + Architecture Board |
| Target Version | FRD-CM-001 v1.1 (status/wording) + DEC artifact (parallel) |
| Status | Open — Need Business Decision + Need Architecture Decision |
| Dependencies | OQ-CM-B1-001; ADR-014; ADR-015; GOV-REV-014 blocking items |
| Estimated Complexity | Low (wording) / High (DEC + ADR acceptance path) |

---

#### C-02 — Authorization listed as external enterprise dependency

| Field | Content |
|---|---|
| Finding ID | C-02 |
| Title | Authorization is listed as an external enterprise dependency, inverting ADR-014 boundary |
| Category | Architecture Boundary |
| Severity | Critical |
| Description | §4 table of “external enterprise systems via APIs only” includes Authorization for complaint/customer/attachment actions. ADR-014, ADR-008, and ADR-015 assign Complaint Authorization / Role-Permission SoT to ECMP / Core Platform internally. |
| Current Situation | Authorization appears as outbound API dependency alongside Identity, Authentication, Organization. |
| Expected Situation | Authorization removed from external dependency table; stated as ECMP-internal (Core Platform Role-Permission SoT per ADR-008). Identity, Authentication, Organization remain external. |
| Root Cause | Boundary conflation of Authentication/Identity (external) with Authorization (internal). |
| Recommended Action | Correct §4; add one normative sentence that complaint authorization is ECMP-internal. No ADR change required if wording aligns to ADR-014/008. |
| Affected Sections | §4 External Dependencies; FR-001 §7/§16; FR-002 §7/§16; FR-004 §7/§16; §13 Integration constraints |
| Business Rules | BR authorization assumptions; ADR-008 / ADR-014 / ADR-015 alignment |
| Functional Requirements | FR-001…FR-004 security/precondition language |
| Use Cases | All (actor authorization assumptions) |
| API Mapping | §13 — no outbound “Authorization API” for module decisions |
| Database Mapping | None |
| Traceability | Boundary mapping to ADR-014 |
| Architecture Impact | Restores locked boundary; prevents incorrect outbound authz coupling. |
| Risk if not fixed | Implementers build outbound authorization calls — reintroducing coupling ADR-014 removed. |
| Priority | P0 — Gating |
| Owner | Solution Architect |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept (specification correction) |
| Dependencies | ADR-008, ADR-014, ADR-015 (read alignment only) |
| Estimated Complexity | Low |

---

#### C-03 — FR-003 preferred outcome out of Batch 1 scope

| Field | Content |
|---|---|
| Finding ID | C-03 |
| Title | FR-003’s preferred business outcome (“Add Case to existing Complaint”) is out of Batch 1 scope |
| Category | Scope / Business Outcome |
| Severity | Critical |
| Description | BR-014 purpose steers duplicates to a new Case on existing Complaint. FR-003 Normal Flow, UC-CM-007 path language, and audit event `ResolvedAsCaseOnExisting` advertise that outcome, while §2.3 / §17 place Case creation (standalone) out of Batch 1. FR-001 A2 says add Case is “outside this FR’s create path”. |
| Current Situation | Warn/block/override paths exist; preferred remedy path is specified but not deliverable in Batch 1. |
| Expected Situation | **Decision required:** (Option A) bring minimal “add Case on existing Complaint” into Batch 1 as constrained FR/extension; **or** (Option B) remove/disable that option from FR-003 flow, UC mapping, screens, and audit event; document explicit limitation and deferred FR. |
| Root Cause | Scope cut left algorithmic detection in while removing the business remedy the rule exists to promote. |
| Recommended Action | CTO/Business choose Option A or B before FRD rewrite. Prefer Option A if `% Possible Duplicate Override` KPI must remain meaningful in Batch 1. |
| Affected Sections | §2.3; §9 FR-003 §4/§9/§17; §7 FR-001 A2; §11 UC-CM-007; §12 SCR-CM-003; §17 Out of Scope; §18 Open Questions |
| Business Rules | BR-014; BR-004 E1 |
| Functional Requirements | FR-003; FR-001 A2; possible new minimal Case-create-on-existing FR |
| Use Cases | UC-CM-007; possibly new UC |
| API Mapping | Planned Case-create-on-existing capability if Option A |
| Database Mapping | DM-CM-009 Case (conditional) if Option A |
| Traceability | BR-014 → FR-003 outcome path |
| Architecture Impact | Locked Multi Case / Assignment-on-Case unchanged. Option A is *minimal Case create under existing Aggregate*, not redesign. |
| Risk if not fixed | Override rate inflates; intake-quality KPI corrupted; audit event for impossible outcome. |
| Priority | P0 — Gating |
| Owner | Domain PO ECMF + Business Owner |
| Target Version | FRD-CM-001 v1.1 (scope decision) |
| Status | Open — Need Business Decision |
| Dependencies | BR-004; OQ-CM-B1-004 related; Batch 2 Case FRD if Option B |
| Estimated Complexity | Medium (Option A) / Low (Option B documentation) |

---

#### C-04 — Customer key cardinality contradiction

| Field | Content |
|---|---|
| Finding ID | C-04 |
| Title | Customer key cardinality: FRD contradicts BR-001 and itself |
| Category | Requirements Ambiguity / BR Compliance |
| Severity | Critical |
| Description | BR-001 requires exactly one primary key type for lookup. FR-001 Normal Flow says “exactly one”; Validation tables and E1 say “at least one”; FR-002 validation says “at least one”; FR-002 E5 (conflicting multiple keys) only fits “at least one”. |
| Current Situation | Two defensible implementations; validation tables contradict BR and flow. |
| Expected Situation | All statements aligned to BR-001 **exactly one** key type; FR-002 E5 re-derived (reject multi-key request as invalid input, not “manual resolution of conflicting keys”). |
| Root Cause | Validation table authored with looser cardinality than BR imperative. |
| Recommended Action | Normative alignment pass on FR-001 §9/§11/§12 and FR-002 §12/§11 E5; add acceptance criterion for exactly-one enforcement. |
| Affected Sections | FR-001 §9 step 2, §11 E1, §12; FR-002 §3, §12, §11 E5; §19 ACs |
| Business Rules | BR-001 Business Validation; BR-002 |
| Functional Requirements | FR-001; FR-002 |
| Use Cases | UC-CM-001; UC-CM-002 |
| API Mapping | Customer search request contract (single key type) |
| Database Mapping | None |
| Traceability | BR-001 → FR-002 → FR-001 |
| Architecture Impact | None (CustomerId-only preserved). |
| Risk if not fixed | Divergent UI/API/tests; silent BR deviation. |
| Priority | P0 — Gating |
| Owner | Business Analyst / Domain PO ECMF |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | BR-CM-CAT-001 BR-001 text (authoritative) |
| Estimated Complexity | Low |

---

#### C-05 — Channel auto-register without idempotency control

| Field | Content |
|---|---|
| Finding ID | C-05 |
| Title | Channel auto-register is in scope while its idempotency control is deferred |
| Category | Intake Integrity / Reliability |
| Severity | Critical |
| Description | FR-001 A5 allows system auto-register when policy active. Idempotency/channel message id is Conditional with no rule; no replay exception; Future Enhancement #2 defers per-message-id idempotency. Human path also lacks create-level idempotency key. |
| Current Situation | Unattended create in Batch 1 without mandatory idempotency; permanent Aggregates cannot be physically deleted (§15.6). |
| Expected Situation | **Decision:** (Option A) promote per-message-id idempotency + human idempotency key into FR-001 with replay exception; **or** (Option B) move channel auto-register (A5 unattended path) out of Batch 1, keep agent-confirmed channel intake only. |
| Root Cause | Capability included without its controlling invariant; control parked in Future Enhancement. |
| Recommended Action | Prefer Option A for production channel readiness; Option B if Batch 1 is human-intake-only. Document chosen option in §2.3 / A5 / Future Enhancement. |
| Affected Sections | FR-001 A5, §11, §13 Input, §21 FE#2; §17; possibly new OQ |
| Business Rules | BR-001; permanence rules; BR-014 interaction |
| Functional Requirements | FR-001 |
| Use Cases | Channel intake UC (may need new UC-CM-00x) |
| API Mapping | Create Complaint idempotency key / channel message id |
| Database Mapping | Idempotency store / unique constraint on message id |
| Traceability | Intake → Audit → no silent duplicate Aggregates |
| Architecture Impact | No Aggregate redesign; adds intake control. Interacts with M-02 index timing. |
| Risk if not fixed | Permanent duplicate Aggregates from retries/double-submit; cumulative silent data quality failure. |
| Priority | P0 — Gating |
| Owner | Domain PO ECMF + Integration Lead |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Need Business Decision + Need Architecture Decision |
| Dependencies | M-02; C-03 (duplicate remediation capacity) |
| Estimated Complexity | Medium |

---

#### C-06 — Enumeration prevention weakened and undeclared

| Field | Content |
|---|---|
| Finding ID | C-06 |
| Title | Enumeration prevention is a SHOULD delegated to an undeclared dependency |
| Category | Security / Compliance |
| Severity | Critical |
| Description | FR-002 Identity Number lookup uses SHOULD for rate/anti-enumeration controls, delegated to “enterprise security controls” not listed in §4. Audit masking rule is circular (“not full identity number when forbidden”). |
| Current Situation | Confirm-or-deny oracle over national identity numbers with advisory rate limiting and self-referential masking. |
| Expected Situation | Controls raised to MUST; rate-limiting / anti-enumeration dependency declared in §4 with owner; audit rule unconditional prohibition on cleartext identity numbers in audit records. |
| Root Cause | Security controls softened to SHOULD; dependency ownership omitted. |
| Recommended Action | Security decision to mandate MUST; declare dependency; rewrite audit masking as unconditional. Align with OQ-CM-B1-002. |
| Affected Sections | §4; FR-002 §12, §16.3, §17; related FR-001 security display |
| Business Rules | BR-002; BR-016 (PII in audit) |
| Functional Requirements | FR-002 |
| Use Cases | UC-CM-002 |
| API Mapping | Customer search rate-limit / abuse signals |
| Database Mapping | Audit field storage (hashed/masked identity) |
| Traceability | Security → FR-002 → Audit |
| Architecture Impact | Dependency table expansion only; API First preserved. |
| Risk if not fixed | Direct regulatory exposure; identity enumeration by authenticated agents. |
| Priority | P0 — Gating |
| Owner | Security + Integration Lead |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Need Security Decision |
| Dependencies | OQ-CM-B1-002; enterprise security platform owner |
| Estimated Complexity | Medium |

---

### 2.2 Major Findings

#### M-01 — UNVERIFIED / degraded mode closure gap

| Field | Content |
|---|---|
| Finding ID | M-01 |
| Title | UNVERIFIED / degraded mode has no closure obligation; may permit Complaint with no CustomerId |
| Category | Data Quality / CustomerId-only integrity |
| Severity | Major |
| Description | BR-001 E3 requires reconcile when Master recovers; FR-001 E3 drops mandatory reconciliation. Output allows CustomerId “or UNVERIFIED pending flag”. FR-003 “pending key context” undefined. No aging queue / max pending / supervisor visibility required. |
| Current Situation | Possible persistent Complaint without CustomerId; invisible to duplicate detection and Customer 360. |
| Expected Situation | Restore mandatory reconciliation; define pending key context; aging queue + max pending duration; explicit rule whether Complaint may persist without CustomerId (prefer: no permanent CustomerId-less Aggregate, or hard time-bound exception). |
| Root Cause | Degraded-mode convenience overrode BR closure obligation. |
| Recommended Action | Align FR-001 E3/§14 and FR-003 §13 to BR-001 E3; add supervisor aging obligation (ties to M-16). |
| Affected Sections | FR-001 E3, §14; FR-002 A4/§18; FR-003 §8/§13; §14 DB; §16 RTM |
| Business Rules | BR-001 E3; BR-002; BR-014 correlation |
| Functional Requirements | FR-001; FR-002; FR-003 |
| Use Cases | Reconciliation UC (may need new) |
| API Mapping | Pending verification list / enrich APIs (planned) |
| Database Mapping | Verification flags; pending key context store |
| Traceability | DM-CM-002 → BR-002 → FR-002 |
| Architecture Impact | CustomerId-only principle strengthened, not changed. |
| Risk if not fixed | Silent exit from duplicate detection and 360; data-quality holes. |
| Priority | P1 |
| Owner | Domain PO ECMF |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | M-03 (orphan enrichment/recheck); M-16 (supervisor queue) |
| Estimated Complexity | Medium |

---

#### M-02 — Complaint search index missing from DB mapping

| Field | Content |
|---|---|
| Finding ID | M-02 |
| Title | Complaint search index absent from Database Mapping; update semantics unspecified |
| Category | Data / Consistency |
| Severity | Major |
| Description | BR-001 Data Affected includes search index (BR-003). §14 omits it. Sync vs async indexing on create unspecified; FR-003 E1 only covers index down. |
| Current Situation | Duplicate detection substrate undefined in mapping; race window for dual creates possible if async. |
| Expected Situation | Index entity in §14; normative statement of sync vs async indexing and lag/degradation behavior. |
| Root Cause | Substrate treated as invisible technical detail. |
| Recommended Action | Add DM/DB mapping; decide sync requirement for Batch 1 create path (architecture decision). |
| Affected Sections | §14; FR-003 §7/E1; §16 DM possibly DM-CM-004 |
| Business Rules | BR-003; BR-014; BR-001 |
| Functional Requirements | FR-003; FR-001 |
| Use Cases | UC-CM-003 |
| API Mapping | Search substrate (API-388 related) |
| Database Mapping | Complaint search index |
| Traceability | BR-003 → FR-003 |
| Architecture Impact | Need Architecture Decision on sync vs async. |
| Risk if not fixed | Permanent duplicates via indexing lag (compounded by C-05). |
| Priority | P1 |
| Owner | Solution Architect |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Need Architecture Decision |
| Dependencies | C-05; M-13 |
| Estimated Complexity | Medium |

---

#### M-03 — Orphan mandatory obligations

| Field | Content |
|---|---|
| Finding ID | M-03 |
| Title | Three obligations created with no owning requirement |
| Category | Requirements Completeness |
| Severity | Major |
| Description | (1) later review after `duplicateCheckDegraded=true`; (2) enrichment of UNVERIFIED Complaint; (3) periodic/recheck after UNVERIFIED→verified. No FR/actor/queue/schedule; third implies background process not in architecture. |
| Current Situation | Mandatory downstream work with no owner. |
| Expected Situation | Each obligation assigned to an FR (Batch 1 or deferred with explicit Out-of-Scope + OQ), with actor and trigger. |
| Root Cause | Exception/trigger text invented obligations without FR ownership. |
| Recommended Action | Map (1)(2) into FR-001/FR-002/FR-003 extensions or defer explicitly; (3) either Batch 1 recheck trigger on verify event or Future Enhancement with owner. |
| Affected Sections | FR-003 E1/§8; FR-002 A4; §17; §18 |
| Business Rules | BR-001 E3; BR-014 |
| Functional Requirements | FR-001/002/003 ownership assignment |
| Use Cases | New or extended UCs |
| API Mapping | Review queue / recheck endpoints if in scope |
| Database Mapping | Degraded/pending work items |
| Traceability | Obligation → FR → Test |
| Architecture Impact | May introduce Batch 1 queue concept (logical), not Aggregate redesign. |
| Risk if not fixed | Unowned “MUST” language; untestable compliance. |
| Priority | P1 |
| Owner | Business Analyst |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept / Clarify |
| Dependencies | M-01; M-16 |
| Estimated Complexity | Medium |

---

#### M-04 — ADR-002 staleness indicator and cache PII retention omitted

| Field | Content |
|---|---|
| Finding ID | M-04 |
| Title | ADR-002 staleness indicator and cache retention/PII policy not carried forward |
| Category | Architecture Compliance (Accepted ADR) |
| Severity | Major |
| Description | ADR-002 Accepted consequences require “data as of [timestamp]” UI and local cache retention/PII policy. FRD establishes customer read-model but requires neither. |
| Current Situation | Stale cache acknowledged (MAY) without user-visible freshness or retention policy. |
| Expected Situation | FR-002 requirements for staleness indicator and retention/PII policy reference. |
| Root Cause | Accepted ADR consequences not translated into FR language. |
| Recommended Action | Add FR-002 constraints/ACs; reference ADR-002 explicitly. |
| Affected Sections | FR-002 §15.2/§14/§19; §14 DB customer read-model |
| Business Rules | BR-002; BR-010 read-model |
| Functional Requirements | FR-002 |
| Use Cases | UC-CM-002; UC-CM-008 |
| API Mapping | Brief profile view model fields (`asOf`) |
| Database Mapping | Cache metadata (as-of, expiry) |
| Traceability | ADR-002 → FR-002 |
| Architecture Impact | Aligns FRD to Accepted ADR-002; CustomerId-only unchanged. |
| Risk if not fixed | Agents act on stale customer data without awareness; PII retention gap. |
| Priority | P1 |
| Owner | Solution Architect + BA |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | ADR-002 |
| Estimated Complexity | Low–Medium |

---

#### M-05 — Staged attachment discard vs No Information Lost

| Field | Content |
|---|---|
| Finding ID | M-05 |
| Title | Staged attachment “discard” permits physical destruction of customer-supplied evidence |
| Category | Evidence Integrity / Escalation Principle |
| Severity | Major |
| Description | FR-004 A4 allows “discarded or voided”. Discard conflicts with BR-012 and §15.2 void/supersede. Cancel-after-duplicate path risks losing evidence that should move to surviving Complaint; abandoned session undefined. |
| Current Situation | Physical discard permitted pre-commit; abandoned session unspecified. |
| Expected Situation | Void-with-reason only (no discard); define abandoned-session policy; decide whether staged evidence transfers to surviving Complaint under FR-003 A2 / FR-001 A2. |
| Root Cause | Orphan-prevention language overshot into physical erase. |
| Recommended Action | Rewrite A4; add transfer/retain decision; align to No Information Lost. |
| Affected Sections | FR-004 A4, §15, §11 E3; FR-001 A2; FR-003 A2 |
| Business Rules | BR-012 E3; Escalation package principle |
| Functional Requirements | FR-004; FR-001; FR-003 |
| Use Cases | UC-CM-005; UC-CM-007 |
| API Mapping | Staged void / rebind APIs |
| Database Mapping | Attachment status VOID; staging token lifecycle |
| Traceability | BR-012 → FR-004; Locked escalation principle |
| Architecture Impact | Strengthens No Information Lost; Aggregate boundary unchanged. |
| Risk if not fixed | Evidence loss at cancel-after-duplicate — worst intake failure mode. |
| Priority | P1 |
| Owner | Domain PO ECMF + Compliance |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Need Business Decision (transfer vs void-only) |
| Dependencies | C-03 (add Case path); locked escalation principle |
| Estimated Complexity | Medium |

---

#### M-06 — Attachment anchor invariant missing

| Field | Content |
|---|---|
| Finding ID | M-06 |
| Title | Attachment anchor invariant missing (Case must belong to Complaint) |
| Category | Aggregate Integrity |
| Severity | Major |
| Description | FR-004 requires “valid” anchors but not that Case belongs to Complaint — allowing cross-Aggregate bind. |
| Current Situation | Aggregate boundary can be breached via attachment anchors. |
| Expected Situation | Normative invariant: if CaseId present, Case MUST belong to ComplaintId. |
| Root Cause | Validity ≠ Aggregate membership. |
| Recommended Action | Add validation rule + AC + DB constraint note (logical). |
| Affected Sections | FR-004 §12, §13, §19 |
| Business Rules | BR-012; Aggregate Root rules |
| Functional Requirements | FR-004 |
| Use Cases | UC-CM-004 |
| API Mapping | Upload validation |
| Database Mapping | Anchor FK/membership invariant |
| Traceability | DM-CM-005 → BR-012 → FR-004 |
| Architecture Impact | Defends locked Aggregate Root; no redesign. |
| Risk if not fixed | Cross-Aggregate evidence binding; audit/escalation package corruption. |
| Priority | P1 |
| Owner | Solution Architect |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | None |
| Estimated Complexity | Low |

---

#### M-07 — Add Case / open existing without CLOSED qualification

| Field | Content |
|---|---|
| Finding ID | M-07 |
| Title | “Add Case / open existing” offered without status qualification; conflicts with BR-004 E1 |
| Category | Business Rule Conflict |
| Severity | Major |
| Description | BR-004 E1 blocks Case creation on CLOSED Complaint. FR flows offer open/add without status precondition; candidates include “recent” (may be closed). |
| Current Situation | UI can offer action that will be refused. |
| Expected Situation | Qualify candidate actions by Complaint status; closed candidates: open/view only or reopen path (out of Batch 1) — not add Case. |
| Root Cause | Candidate presentation not filtered by BR-004 E1. |
| Recommended Action | Update FR-003 Normal Flow and FR-001 A2; screen notes on SCR-CM-003. |
| Affected Sections | FR-003 §9; FR-001 A2; §12 SCR-CM-003 |
| Business Rules | BR-004 E1; BR-014 |
| Functional Requirements | FR-003; FR-001 |
| Use Cases | UC-CM-007 |
| API Mapping | Candidate payload includes status + allowed actions |
| Database Mapping | None |
| Traceability | BR-004 → FR-003 |
| Architecture Impact | None beyond status-gated Case create. |
| Risk if not fixed | Agent dead-ends; override pressure increases. |
| Priority | P1 |
| Owner | Business Analyst |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | C-03 |
| Estimated Complexity | Low |

---

#### M-08 — Customer 360 downgraded to SHOULD / out of scope conflict

| Field | Content |
|---|---|
| Finding ID | M-08 |
| Title | Customer 360 downgraded to SHOULD; depends on out-of-scope full view |
| Category | Scope / BR Compliance |
| Severity | Major |
| Description | BR-001 step 5 / BR-010 A3 imperative for 360 context (active-complaint highlight). FR-001 uses SHOULD; §2.3 excludes full Customer 360 view. |
| Current Situation | Algorithmic duplicate check kept; human complement weakened/deferred. |
| Expected Situation | Define **minimum Batch 1 Customer 360 subset** (at least active-complaint highlight per BR-010 A3) as MUST during create; keep full 360 view out of scope. |
| Root Cause | Binary in/out scope cut instead of subsetting. |
| Recommended Action | Clarify §2.3; restore MUST for minimum subset; leave full view deferred. Locked Customer 360 capability unchanged. |
| Affected Sections | §2.3; FR-001 §9 step 4; FR-002; UC-CM-008; SCR mapping |
| Business Rules | BR-010 A3; BR-001; BR-014 complement |
| Functional Requirements | FR-001; FR-002; partial BR-010 |
| Use Cases | UC-CM-008 |
| API Mapping | Minimal active-complaint context API (planned) |
| Database Mapping | Read of active Complaints by CustomerId |
| Traceability | BR-010 → FR-001 subset |
| Architecture Impact | Locked Customer 360 retained; Batch 1 delivers subset only. |
| Risk if not fixed | Duplicate prevention loses human judgement layer. |
| Priority | P1 |
| Owner | Domain PO ECMF |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Need Business Decision (subset contents) |
| Dependencies | C-03; FRD-003 CRM 360 (later full view) |
| Estimated Complexity | Medium |

---

#### M-09 — Evidence integrity controls weakened

| Field | Content |
|---|---|
| Finding ID | M-09 |
| Title | Sensitive-access audit and integrity hash downgraded vs BR-012 |
| Category | Security / Audit |
| Severity | Major |
| Description | BR-012 requires Accessed (sensitive) and hash/integrity; FRD uses MAY/SHOULD. |
| Current Situation | Optional hash and optional sensitive-access audit. |
| Expected Situation | Both MUST. |
| Root Cause | Softening of BR imperatives in FR security/output tables. |
| Recommended Action | Raise to MUST in FR-004 §14/§16/§17 and ACs. |
| Affected Sections | FR-004 §14, §16.5, §17 |
| Business Rules | BR-012 |
| Functional Requirements | FR-004 |
| Use Cases | UC-CM-004 |
| API Mapping | Metadata includes hash; access audit events |
| Database Mapping | Integrity hash mandatory field |
| Traceability | BR-012 → FR-004 |
| Architecture Impact | Strengthens No Information Lost / evidence chain. |
| Risk if not fixed | Unprovable evidence in escalated/compliance reads. |
| Priority | P1 |
| Owner | Compliance + Security |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | M-05 |
| Estimated Complexity | Low |

---

#### M-10 — Anti-inference control is SHOULD

| Field | Content |
|---|---|
| Finding ID | M-10 |
| Title | Anti-inference uniform-empty behavior on duplicate detection is SHOULD |
| Category | Security |
| Severity | Major |
| Description | FR-003 E4 MUST not leak candidate payload but SHOULD apply uniform authorized-empty behavior — creating a side channel via result shape/scores. |
| Current Situation | Partial anti-inference control. |
| Expected Situation | Uniform authorized-empty behavior MUST. |
| Root Cause | Control split incorrectly across MUST/SHOULD. |
| Recommended Action | Raise E4 uniformity to MUST; add AC. |
| Affected Sections | FR-003 E4, §16, §19 |
| Business Rules | BR-014 authorization scoping |
| Functional Requirements | FR-003 |
| Use Cases | UC-CM-003 |
| API Mapping | Duplicate check response uniformity |
| Database Mapping | None |
| Traceability | Security → FR-003 |
| Architecture Impact | None beyond response policy. |
| Risk if not fixed | Cross-unit complaint existence inference. |
| Priority | P1 |
| Owner | Security |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | C-06 (security hardening theme) |
| Estimated Complexity | Low |

---

#### M-11 — Transaction boundary undefined / oversized

| Field | Content |
|---|---|
| Finding ID | M-11 |
| Title | Transaction boundary undefined and implied very large |
| Category | Architecture / Reliability |
| Severity | Major |
| Description | FR-001 E6 + initial Case same transaction + FR-004 staged bind on commit imply huge unit of work spanning Aggregate, audit, timeline, linkage, attachments, index — with binary already in external storage. No saga/compensation; post-commit bind failure undefined. |
| Current Situation | Atomicity demanded for audit but boundary unbounded. |
| Expected Situation | Explicit transaction boundary diagram in FR terms; compensation/saga notes for storage-vs-metadata; defined behavior for post-commit attachment binding failure. |
| Root Cause | Multiple MUST-atomic statements composed without a stated boundary. |
| Recommended Action | Architecture Decision in FRD § Business Constraints / new subsection; keep audit atomicity; bound other steps. |
| Affected Sections | FR-001 §9/§11 E6; FR-004 A4; §14 |
| Business Rules | BR-016 E6-style; BR-001; BR-012 |
| Functional Requirements | FR-001; FR-004 |
| Use Cases | UC-CM-001; UC-CM-005 |
| API Mapping | Create command semantics |
| Database Mapping | Outbox / binding state if needed |
| Traceability | Create → Audit → Attachment bind |
| Architecture Impact | Need Architecture Decision; ADR-009 may apply for outbox. |
| Risk if not fixed | Partial commits; orphan binaries; inconsistent Aggregates. |
| Priority | P1 |
| Owner | Solution Architect |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Need Architecture Decision |
| Dependencies | M-05; M-12; ADR-009 |
| Estimated Complexity | High |

---

#### M-12 — Notification failure logged in externally owned log

| Field | Content |
|---|---|
| Finding ID | M-12 |
| Title | Notification failure must be recorded in a log ECMP does not own |
| Category | Integration / Reliability |
| Severity | Major |
| Description | FR-001 §18 requires failure recorded in Notification delivery log; Notification Platform is external. When platform is down, mandatory record cannot be written. ADR-009 already establishes outbox pattern. |
| Current Situation | Mandatory write to unavailable external log. |
| Expected Situation | ECMP-side outbox / delivery-status projection required; external log optional copy. |
| Root Cause | Ownership mismatch. |
| Recommended Action | Rewrite §18; reference ADR-009. |
| Affected Sections | FR-001 §18; §4 Notification; §14 |
| Business Rules | Notification scope table; BR-016 optional |
| Functional Requirements | FR-001 |
| Use Cases | UC-CM-001 notification side effect |
| API Mapping | Outbox / notification request API |
| Database Mapping | ECMP notification outbox / delivery status |
| Traceability | ADR-009 → FR-001 |
| Architecture Impact | Align to ADR-009; API First preserved. |
| Risk if not fixed | Unmet MUST on the common failure path. |
| Priority | P1 |
| Owner | Solution Architect |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | ADR-009; M-11 |
| Estimated Complexity | Medium |

---

#### M-13 — No NFR linkage for pre-commit duplicate check

| Field | Content |
|---|---|
| Finding ID | M-13 |
| Title | No NFR linkage for synchronous unbounded pre-commit duplicate check |
| Category | Performance / Scalability |
| Severity | Major |
| Description | FR-003 runs sync before confirm over configurable window with scores; no latency budget, candidate cap, timeout, or slow-degradation (only unavailable). NFR spec unreferenced. |
| Current Situation | Unbounded critical-path check. |
| Expected Situation | Reference NFR spec; add latency budget, candidate cap, timeout, degradation-on-slowness. |
| Root Cause | Functional FR without non-functional bounds. |
| Recommended Action | Add FR-003 NFR subsection; cite `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md`. |
| Affected Sections | FR-003 §11/§12/§14/§19; document references |
| Business Rules | BR-014; BR-003 |
| Functional Requirements | FR-003 |
| Use Cases | UC-CM-003 |
| API Mapping | Duplicate check timeout/cap contract |
| Database Mapping | Index query bounds |
| Traceability | NFR → FR-003 |
| Architecture Impact | Complements M-02 sync/async decision. |
| Risk if not fixed | Intake latency failures at volume; undefined degradation. |
| Priority | P1 |
| Owner | Solution Architect + Performance |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | M-02; OQ-CM-B1-003 |
| Estimated Complexity | Medium |

---

#### M-14 — Audit retention unspecified; Compliance unreferenced

| Field | Content |
|---|---|
| Finding ID | M-14 |
| Title | Audit retention unspecified; `17 Compliance` unreferenced |
| Category | Compliance / Audit |
| Severity | Major |
| Description | BR-016 requires long retention; FRD mandates content but not retention period, immutability enforcement, or audit legal-hold interaction. |
| Current Situation | Strong audit content, weak retention/legal-hold story. |
| Expected Situation | Retention + immutability + legal-hold for audit; reference `17 Compliance`. |
| Root Cause | Content specified; lifecycle omitted. |
| Recommended Action | Add cross-cutting audit constraints section; new OQ if retention period needs legal input. |
| Affected Sections | Cross-cutting (§17 Audit across FRs); new Compliance refs; §18 |
| Business Rules | BR-016 |
| Functional Requirements | All FRs audit sections |
| Use Cases | All |
| API Mapping | None mandatory |
| Database Mapping | Audit store retention attributes |
| Traceability | BR-016 → Compliance |
| Architecture Impact | May need Compliance/Security decision on period. |
| Risk if not fixed | Audit content without defensible retention. |
| Priority | P1 |
| Owner | Compliance |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Need Security Decision / Compliance Decision |
| Dependencies | `17 Compliance`; m-06 |
| Estimated Complexity | Medium |

---

#### M-15 — API catalog ID collisions for cited anchors

| Field | Content |
|---|---|
| Finding ID | M-15 |
| Title | Cited API catalog IDs API-390 / API-392 are ambiguous |
| Category | Traceability / Catalog Defect |
| Severity | Major |
| Description | Generated catalog assigns API-390 and API-392 twice (complaints vs dashboard). FRD cites them as stable anchors. |
| Current Situation | Ambiguous traceability IDs. |
| Expected Situation | Catalog collision resolved; FRD cites unambiguous IDs (or path+method until remapped). |
| Root Cause | Inherited catalog defect. |
| Recommended Action | Fix catalog first; then update §13 citations. Parallel workstream to FRD text. |
| Affected Sections | §13 API Mapping |
| Business Rules | None |
| Functional Requirements | FR-001 mapping |
| Use Cases | None directly |
| API Mapping | API-390, API-392 (and dashboard duplicates) |
| Database Mapping | None |
| Traceability | FR → API broken until fixed |
| Architecture Impact | Catalog hygiene; API First unchanged. |
| Risk if not fixed | Automated RTM resolves wrong endpoints. |
| Priority | P1 |
| Owner | API Catalog Owner / Integration Lead |
| Target Version | Catalog fix + FRD-CM-001 v1.1 citation update |
| Status | Open — Accept (catalog + FRD) |
| Dependencies | `07 API Catalog` remediation |
| Estimated Complexity | Medium (catalog); Low (FRD citation) |

---

#### M-16 — KPI Impact and supervisor-queue obligation dropped

| Field | Content |
|---|---|
| Finding ID | M-16 |
| Title | KPI Impact and supervisor-queue obligation dropped in translation |
| Category | Completeness / Operations |
| Severity | Major |
| Description | BR catalog KPI Impact lost (no KPI section in FR template). BR-001 A4 supervisor queue for Complaint without Case omitted from FR-001 A4. |
| Current Situation | Batch success measures and no-Case aging control absent. |
| Expected Situation | KPI Impact section in FR template (or Batch summary); restore supervisor-queue flagging for no-Case path. |
| Root Cause | Template gap + alternate flow truncation. |
| Recommended Action | Extend FR template; restore A4 step; link to M-01/M-03 aging. |
| Affected Sections | FR template; FR-001 A4; possibly §6 summary |
| Business Rules | BR-001 A4; KPI definitions in BR-CM-CAT-001 |
| Functional Requirements | FR-001; Batch KPI notes |
| Use Cases | Supervisor queue UC (may be new/deferred with owner) |
| API Mapping | Queue item projection |
| Database Mapping | Aging / queue flags |
| Traceability | BR KPI → FR → Test |
| Architecture Impact | Operations visibility; Dashboard KPI full FR remains out of scope — subset flagging only. |
| Risk if not fixed | No objective Batch 1 success measures; no-Case aging invisible. |
| Priority | P1 |
| Owner | Domain PO ECMF + Operations Lead |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | M-01; M-03; OQ-CM-B1-004 |
| Estimated Complexity | Medium |

---

#### M-17 — Customer merge / retirement not addressed

| Field | Content |
|---|---|
| Finding ID | M-17 |
| Title | Upstream customer merge / retirement not addressed |
| Category | Integration Edge Case |
| Severity | Major |
| Description | Master Customer merge/retire leaves Complaints on retired CustomerId; breaks 360, duplicate correlation, reporting. FR-002 A3 handles inactive only. ADR-002: ECMP cannot write back. |
| Current Situation | No reaction model for merged/superseded. |
| Expected Situation | Define reaction (consume merge event / mapping table / re-link policy) **or** explicit OQ with owner and target version (v1.2 acceptable if Batch 1 volume risk accepted). |
| Root Cause | Happy-path Master states only. |
| Recommended Action | Prefer new OQ-CM-B1-00x with Architecture/Integration owner; minimal Batch 1 note if full handling deferred to v1.2. |
| Affected Sections | FR-002 A3/§15; §18 Open Questions; §17 |
| Business Rules | BR-002; ADR-002 |
| Functional Requirements | FR-002; possibly later FR |
| Use Cases | Future |
| API Mapping | Merge event consumption (enterprise) |
| Database Mapping | CustomerId alias/redirect if adopted |
| Traceability | ADR-002 → FR-002 |
| Architecture Impact | Need Architecture Decision if in v1.1; else Move to v1.2 with OQ. |
| Risk if not fixed | Silent correlation break after Master merges. |
| Priority | P2 (or P1 if merge volume high) |
| Owner | Integration Lead |
| Target Version | FRD-CM-001 v1.1 (OQ) or v1.2 (full handling) |
| Status | Open — Need Architecture Decision / Move to v1.2 candidate |
| Dependencies | ADR-002; Master Customer event contract |
| Estimated Complexity | High (full); Low (OQ deferral) |

---

### 2.3 Minor Findings

#### m-01 — Draft vs normative status conflict

| Field | Content |
|---|---|
| Finding ID | m-01 |
| Title | Document Status “Draft v1.0” vs §1.1 “normative for Batch 1” |
| Category | Governance / Document Control |
| Severity | Minor |
| Description | Draft and normative are incompatible under Architecture Governance lifecycle. |
| Current Situation | Conflicting authority signals. |
| Expected Situation | Status = Draft until CTO/Board approval of v1.1; §1.1 says “intended normative after approval” or Status raised when locked. |
| Root Cause | Premature normative claim. |
| Recommended Action | Align Document Control with C-01 readiness language. |
| Affected Sections | Header Status; §1.1 |
| Business Rules | — |
| Functional Requirements | — |
| Use Cases | — |
| API Mapping | — |
| Database Mapping | — |
| Traceability | Document authority |
| Architecture Impact | None |
| Risk if not fixed | Implementers treat Draft as frozen. |
| Priority | P2 |
| Owner | BA / Architecture Board Chair |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | C-01 |
| Estimated Complexity | Low |

---

#### m-02 — Recording unit override underspecified

| Field | Content |
|---|---|
| Finding ID | m-02 |
| Title | Recording unit “overridable if permitted” without who/audit/multi-unit rules |
| Category | Authorization / Org Context |
| Severity | Minor |
| Description | Override of recording unit lacks role rule, audit requirement, multi-unit actor behaviour. |
| Current Situation | Conditional override without policy. |
| Expected Situation | Define permitted roles, mandatory audit, multi-unit selection rule — or OQ. |
| Root Cause | Incomplete org-context rule. |
| Recommended Action | Add validation/audit or OQ-CM-B1-00x. |
| Affected Sections | FR-001 §13 Recording unit; §17 Audit |
| Business Rules | Org dependency; BR-016 |
| Functional Requirements | FR-001 |
| Use Cases | UC-CM-001 |
| API Mapping | Create payload unit override |
| Database Mapping | Unit on Complaint |
| Traceability | Org → FR-001 |
| Architecture Impact | None |
| Risk if not fixed | Inconsistent unit attribution. |
| Priority | P2 |
| Owner | Operations Lead |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Clarify / Need Business Decision |
| Dependencies | Organization dependency |
| Estimated Complexity | Low |

---

#### m-03 — Complaint Number policy incomplete

| Field | Content |
|---|---|
| Finding ID | m-03 |
| Title | Complaint Number uniqueness required but format/sequencing/gapless/reset/failure unspecified |
| Category | Identifier Policy |
| Severity | Minor |
| Description | Uniqueness only; audit-sensitive number policy missing. |
| Current Situation | Underspecified generator. |
| Expected Situation | New OQ with owner for format, gapless, reset, failure behaviour — do not invent values in FRD. |
| Root Cause | Identity rule stopped at uniqueness. |
| Recommended Action | Add OQ; minimal MUST uniqueness retained. |
| Affected Sections | FR-001 §15.5; §18 |
| Business Rules | BR-001 |
| Functional Requirements | FR-001 |
| Use Cases | UC-CM-001 |
| API Mapping | — |
| Database Mapping | Number generator |
| Traceability | — |
| Architecture Impact | None |
| Risk if not fixed | Later audit/format rework. |
| Priority | P2 |
| Owner | Operations Lead + Administrator |
| Target Version | FRD-CM-001 v1.1 (OQ) |
| Status | Open — Clarify (new OQ) |
| Dependencies | None |
| Estimated Complexity | Low |

---

#### m-04 — Inactive customer flag unnamed

| Field | Content |
|---|---|
| Finding ID | m-04 |
| Title | Inactive customer “special flag” unnamed and unmapped |
| Category | Ambiguity |
| Severity | Minor |
| Description | FR-002 A3 requires special flag; absent from FR-001 output and §14. |
| Current Situation | Unnamed mandatory flag. |
| Expected Situation | Named field in Output + DB mapping (e.g., `customerInactiveAtCreate=true`). |
| Root Cause | Alternate flow without data dictionary update. |
| Recommended Action | Name and map the flag. |
| Affected Sections | FR-002 A3; FR-001 §14; §14 DB |
| Business Rules | BR-002 |
| Functional Requirements | FR-002; FR-001 |
| Use Cases | UC-CM-002 |
| API Mapping | Flag on create/context |
| Database Mapping | Complaint verification attributes |
| Traceability | BR-002 → FR-002 |
| Architecture Impact | None |
| Risk if not fixed | Untestable AC; divergent implementations. |
| Priority | P2 |
| Owner | BA |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | M-17 (related Master states) |
| Estimated Complexity | Low |

---

#### m-05 — Override justification minimum unspecified

| Field | Content |
|---|---|
| Finding ID | m-05 |
| Title | Override justification minimum length/content MUST apply with no value |
| Category | Ambiguity |
| Severity | Minor |
| Description | MUST without configured value or OQ (unlike threshold/window). |
| Current Situation | Unenforceable MUST. |
| Expected Situation | OQ or config default placeholder with owner (Operations). |
| Root Cause | Incomplete policy binding. |
| Recommended Action | Add OQ parallel to OQ-CM-B1-003. |
| Affected Sections | FR-003 §12; §18 |
| Business Rules | BR-014 |
| Functional Requirements | FR-003 |
| Use Cases | UC-CM-006 |
| API Mapping | Validation rule |
| Database Mapping | — |
| Traceability | — |
| Architecture Impact | None |
| Risk if not fixed | Weak/variable override quality. |
| Priority | P2 |
| Owner | Operations Lead |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Clarify (new OQ) |
| Dependencies | OQ-CM-B1-003 |
| Estimated Complexity | Low |

---

#### m-06 — BR-016 clock-skew and no-secrets not carried

| Field | Content |
|---|---|
| Finding ID | m-06 |
| Title | BR-016 clock-skew detection and no-auth-secrets constraints not carried into any FR |
| Category | Audit Completeness |
| Severity | Minor |
| Description | E3 clock-skew and no authentication secrets in audit missing from FRD. |
| Current Situation | Partial BR-016 coverage. |
| Expected Situation | Cross-cutting audit constraints in all FR audit sections or shared § Audit. |
| Root Cause | Incomplete BR carry-forward. |
| Recommended Action | Add to cross-cutting audit (with M-14). |
| Affected Sections | Audit sections FR-001…004; possibly new shared section |
| Business Rules | BR-016 |
| Functional Requirements | All |
| Use Cases | All |
| API Mapping | — |
| Database Mapping | Audit |
| Traceability | BR-016 → FR |
| Architecture Impact | None |
| Risk if not fixed | Silent timestamp normalization; secret leakage into audit. |
| Priority | P2 |
| Owner | Compliance + Security |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | M-14 |
| Estimated Complexity | Low |

---

#### m-07 — Bulk upload aggregate payload size missing

| Field | Content |
|---|---|
| Finding ID | m-07 |
| Title | Bulk upload has per-file and per-count limits but no aggregate payload size |
| Category | Validation Completeness |
| Severity | Minor |
| Description | Missing total payload cap for multi-file action. |
| Current Situation | Partial bulk limits. |
| Expected Situation | Aggregate max payload validation (config) or OQ under OQ-CM-B1-005 family. |
| Root Cause | Incomplete bulk policy. |
| Recommended Action | Extend FR-004 §12 / OQ-CM-B1-005. |
| Affected Sections | FR-004 §12 A3; §18 |
| Business Rules | BR-012 |
| Functional Requirements | FR-004 |
| Use Cases | UC-CM-004 |
| API Mapping | Upload validation |
| Database Mapping | — |
| Traceability | — |
| Architecture Impact | None |
| Risk if not fixed | Resource exhaustion on bulk action. |
| Priority | P2 |
| Owner | Security + Administrator |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | OQ-CM-B1-005 |
| Estimated Complexity | Low |

---

#### m-08 — Effective-dated config not extended to attachment/duplicate policies

| Field | Content |
|---|---|
| Finding ID | m-08 |
| Title | Effective-dated classification protected; attachment allowlists/size/duplicate hard-block lists not |
| Category | Configuration Governance |
| Severity | Minor |
| Description | Historical explainability incomplete for non-classification configs. |
| Current Situation | Asymmetric effective-dating. |
| Expected Situation | Extend effective-dated requirement to attachment allowlists, size limits, duplicate hard-block category lists. |
| Root Cause | Narrow application of config versioning. |
| Recommended Action | Broaden FR-001 §15.7-style constraint to FR-003/FR-004 config. |
| Affected Sections | FR-001 §15; FR-003; FR-004 Business Constraints |
| Business Rules | Config governance |
| Functional Requirements | FR-003; FR-004 |
| Use Cases | — |
| API Mapping | — |
| Database Mapping | Config version / effective dates |
| Traceability | — |
| Architecture Impact | None |
| Risk if not fixed | Cannot explain past allow/block decisions. |
| Priority | P2 |
| Owner | Administrator + BA |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | None |
| Estimated Complexity | Low–Medium |

---

#### m-09 — No linkage to Test Strategy or Traceability folder

| Field | Content |
|---|---|
| Finding ID | m-09 |
| Title | No linkage to `13 Test Strategy` or `26 Traceability` |
| Category | Traceability Hygiene |
| Severity | Minor |
| Description | Full ACs and RTM exist but consumers unreferenced. |
| Current Situation | Isolated FRD RTM. |
| Expected Situation | Explicit references and update plan for Test Strategy / Traceability packs. |
| Root Cause | Document silo. |
| Recommended Action | Add Related Documents; include in Traceability Update Plan (this document §9). |
| Affected Sections | Document Control / Related; §16 |
| Business Rules | — |
| Functional Requirements | All ACs |
| Use Cases | All |
| API Mapping | — |
| Database Mapping | — |
| Traceability | FR → TC |
| Architecture Impact | None |
| Risk if not fixed | Test design drifts from ACs. |
| Priority | P2 |
| Owner | QA Lead |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | Traceability Update Plan |
| Estimated Complexity | Low |

---

#### m-10 — Customer reference update missing before/after History capture

| Field | Content |
|---|---|
| Finding ID | m-10 |
| Title | FR-002 §15.4 customer reference update lacks before/after History capture |
| Category | History Semantics |
| Severity | Minor |
| Description | BR-018 distinguishes History by before/after; FR says “full audit trail” only. |
| Current Situation | Audit without mandated History before/after. |
| Expected Situation | Require before/after CustomerId capture in History on enrichment. |
| Root Cause | Audit conflated with History. |
| Recommended Action | Align FR-002 A4/§15.4 with BR-018. |
| Affected Sections | FR-002 A4, §15.4 |
| Business Rules | BR-018; BR-016 |
| Functional Requirements | FR-002 |
| Use Cases | Enrichment |
| API Mapping | — |
| Database Mapping | History entries |
| Traceability | BR-018 → FR-002 |
| Architecture Impact | None |
| Risk if not fixed | Non-reconstructable CustomerId changes. |
| Priority | P2 |
| Owner | BA |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Accept |
| Dependencies | M-01 |
| Estimated Complexity | Low |

---

#### m-11 — Concurrent create for same customer not addressed

| Field | Content |
|---|---|
| Finding ID | m-11 |
| Title | Concurrent create by two agents for same customer not addressed |
| Category | Concurrency |
| Severity | Minor |
| Description | No alternate/exception for simultaneous creates; interacts with M-02/C-05. |
| Current Situation | Race undefined. |
| Expected Situation | Exception/alternative: both may warn, or optimistic create + linkage, or lock — pick via Architecture Decision note. |
| Root Cause | Single-actor flow assumption. |
| Recommended Action | Add concurrency note under FR-001/FR-003; tie to index semantics. |
| Affected Sections | FR-001; FR-003 Exception/Alternative |
| Business Rules | BR-014 |
| Functional Requirements | FR-001; FR-003 |
| Use Cases | — |
| API Mapping | Create concurrency semantics |
| Database Mapping | Unique/idempotency aids |
| Traceability | — |
| Architecture Impact | Need Architecture Decision (light). |
| Risk if not fixed | Duplicate Aggregates under concurrency. |
| Priority | P2 |
| Owner | Solution Architect |
| Target Version | FRD-CM-001 v1.1 |
| Status | Open — Need Architecture Decision |
| Dependencies | M-02; C-05 |
| Estimated Complexity | Medium |

---

#### m-12 — Deceased / dormant / merged Master states incomplete

| Field | Content |
|---|---|
| Finding ID | m-12 |
| Title | Deceased, dormant, merged customer states not addressed (only inactive) |
| Category | Master Customer Edge Cases |
| Severity | Minor |
| Description | Broader Master lifecycle states missing beyond inactive. |
| Current Situation | Incomplete state matrix. |
| Expected Situation | State matrix in FR-002 or OQ covering deceased/dormant/merged (merged overlaps M-17). |
| Root Cause | Narrow Master status modeling. |
| Recommended Action | Extend A3 or OQ; align with M-17 decision. |
| Affected Sections | FR-002 A3; §18 |
| Business Rules | BR-002 |
| Functional Requirements | FR-002 |
| Use Cases | UC-CM-002 |
| API Mapping | Master status mapping |
| Database Mapping | Flags |
| Traceability | — |
| Architecture Impact | None if deferred via OQ |
| Risk if not fixed | Inconsistent create policy across Master states. |
| Priority | P2 |
| Owner | Integration Lead |
| Target Version | FRD-CM-001 v1.1 (matrix/OQ) |
| Status | Open — Clarify |
| Dependencies | M-17; m-04 |
| Estimated Complexity | Low–Medium |

---

#### m-13 — Durable FR-001 / BR-001 ID namespace collision hazard

| Field | Content |
|---|---|
| Finding ID | m-13 |
| Title | Two live documents define FR-001/BR-001 differently — tooling hazard |
| Category | Namespace / Tooling |
| Severity | Minor |
| Description | §1.1 warns humans; automation/indexes/commit messages remain exposed. |
| Current Situation | Dual namespaces in one repo. |
| Expected Situation | Tooling-safe IDs (FRD-CM-001 / FR-CM-001 style) **or** DEC remapping date that retires collision; update indexes/generators. |
| Root Cause | Parallel SoTs during transition. |
| Recommended Action | Prefer qualified IDs in v1.1 headings + generator rules; close via C-01 DEC. |
| Affected Sections | §1.1; FR headings; catalogs; tools |
| Business Rules | BR-CM-CAT-001 vs BR-DOC-001 |
| Functional Requirements | ID scheme |
| Use Cases | UC-CM-* already qualified (good) |
| API Mapping | — |
| Database Mapping | — |
| Traceability | All ID-based tooling |
| Architecture Impact | Governance/tooling; depends on C-01. |
| Risk if not fixed | Wrong FR/BR resolved by automation. |
| Priority | P2 |
| Owner | Architecture Board Chair + Tooling |
| Target Version | FRD-CM-001 v1.1 + tooling follow-up |
| Status | Open — Need Architecture Decision (ID scheme) |
| Dependencies | C-01; OQ-CM-B1-001 |
| Estimated Complexity | Medium |

---

## 3. Revision Roadmap

Specification work only (no application implementation).

### Sprint 1 — Foundation & Gating (P0)

**Goal:** Make FRD safe to revise and remove critical contradictions/boundary errors.

| Item | Finding | Outcome |
|---|---|---|
| DEC / readiness path | C-01, m-01 | CTO/Board decision recorded; §2.1/status language path selected |
| Authorization boundary fix plan | C-02 | Accepted correction for §4 |
| Scope decision: Add Case in Batch 1? | C-03 | Option A or B locked |
| Key cardinality alignment plan | C-04 | Accept — exactly one |
| Auto-register vs idempotency | C-05 | Option A or B locked |
| Enumeration MUST + dependency | C-06 | Security decision recorded |
| API ID collision remediation start | M-15 | Catalog fix kickoff (parallel) |
| Decision Matrix freeze | — | All P0 decisions Closed or deferred with date |

**Sprint 1 exit:** All Critical findings have an approved Decision Matrix disposition.

### Sprint 2 — Integrity, Security & BR Alignment (P1 core)

**Goal:** Close major integrity/security/BR-compliance gaps that affect Aggregate safety and regulatory posture.

| Item | Finding |
|---|---|
| UNVERIFIED closure + pending key context | M-01, M-03, m-10 |
| Search index mapping + sync/async decision | M-02, M-13, m-11 |
| ADR-002 staleness + cache PII | M-04 |
| Staged attachment void/transfer | M-05 |
| Anchor invariant | M-06 |
| CLOSED status qualification | M-07 |
| Customer 360 Batch 1 subset | M-08 |
| Evidence hash + sensitive access MUST | M-09 |
| Anti-inference MUST | M-10 |
| Notification outbox | M-12 |
| KPI + supervisor queue | M-16 |

**Sprint 2 exit:** All P1 Accept items specified in Revision Plan dispositions; Architecture Decision notes drafted for M-02/M-11/M-13.

### Sprint 3 — Completeness, Housekeeping & Lock Prep (P1 residual + P2)

**Goal:** Complete template/traceability/compliance housekeeping; prepare FRD v1.1 authoring package.

| Item | Finding |
|---|---|
| Transaction boundary statement | M-11 |
| Audit retention + Compliance refs | M-14, m-06 |
| Merge/retirement OQ or v1.2 move | M-17, m-12 |
| Catalog citation update | M-15 (complete) |
| Minors batch | m-02…m-09, m-13 |
| Traceability Update Plan execution checklist | §9 |
| FRD v1.1 authoring authorization package | DoD gate |

**Sprint 3 exit:** Revision Plan marked Ready for FRD Update; Claude Delta Review can begin after FR text lands.

---

## 4. Dependency Graph

```text
C-01 (Foundation / DEC / readiness)
 ├── m-01 (Draft vs normative)
 ├── m-13 (Namespace tooling)
 └── gates authority of all FR text changes
        │
        ▼
C-02 (Authorization boundary)
        │
        ▼
C-04 (Exact-one key cardinality)
        │
        ▼
C-06 (Enumeration MUST + §4 dependency)
        │
        ▼
C-03 (Add Case in Batch 1? — scope)
 ├── M-07 (CLOSED qualification)
 ├── M-08 (360 subset complements remedy path)
 └── M-05 (evidence transfer on abandon-create)
        │
        ▼
C-05 (Idempotency vs auto-register)
 ├── M-02 (Index sync/async)
 ├── M-13 (NFR bounds)
 └── m-11 (Concurrency)
        │
        ▼
M-01 (UNVERIFIED closure)
 ├── M-03 (Orphan obligations ownership)
 ├── M-16 (Supervisor queue / KPI)
 └── m-10 (History before/after)
        │
        ▼
M-11 (Transaction boundary)
 ├── M-05 (staged bind/void)
 └── M-12 (Notification outbox / ADR-009)
        │
        ▼
M-04  M-06  M-09  M-10  M-14  M-15  M-17
 (parallelizable after gating decisions)
        │
        ▼
m-02 m-03 m-04 m-05 m-06 m-07 m-08 m-09 m-12
 (housekeeping)
```

Critical path (compressed):

```text
C-01 → C-02 → C-04 → C-06 → C-03 → C-05 → M-01 → M-02 → M-05 → M-11 → M-15
```

---

## 5. Risk Matrix

| Risk ID | Risk | Related Findings | Probability | Impact | Mitigation | Owner |
|---|---|---|---|---|---|---|
| RSK-01 | Implementation starts on unratified foundation | C-01, m-01 | High | High | Block code planning until DEC/readiness path approved | Architecture Board Chair |
| RSK-02 | Outbound Authorization coupling reintroduced | C-02 | Medium | High | §4 correction mandatory in v1.1; design review checklist | Solution Architect |
| RSK-03 | Permanent duplicate Aggregates | C-05, M-02, m-11 | High | High | Idempotency decision + index semantics + concurrency note | Domain PO + Architect |
| RSK-04 | Identity enumeration / regulatory exposure | C-06 | Medium | Critical | MUST controls + declared dependency + cleartext ban | Security |
| RSK-05 | Override KPI corruption / no remedy path | C-03, M-07, M-08 | High | High | Scope decision Option A/B before FR rewrite | Business Owner |
| RSK-06 | Evidence loss on cancel-after-duplicate | M-05 | Medium | High | Void-only + transfer decision | Compliance + PO |
| RSK-07 | Cross-Aggregate attachment bind | M-06 | Low | High | Anchor membership invariant | Solution Architect |
| RSK-08 | Partial create / orphan storage objects | M-11, M-12 | Medium | High | Explicit transaction/saga + ECMP outbox | Solution Architect |
| RSK-09 | CustomerId-less Complaints evade detection | M-01, M-03 | Medium | High | Mandatory reconcile + aging queue | Domain PO |
| RSK-10 | Ambiguous API traceability | M-15 | High | Medium | Fix catalog before FRD citation freeze | API Catalog Owner |
| RSK-11 | Stale Master data acted on blindly | M-04 | Medium | Medium | as-of indicator + retention policy | Architect + BA |
| RSK-12 | Post-merge correlation break | M-17, m-12 | Low–Medium | High | OQ with owner or v1.2 handling | Integration Lead |
| RSK-13 | Unbounded intake latency | M-13 | Medium | Medium | NFR budget/cap/timeout | Performance + Architect |
| RSK-14 | Dual FR-001 tooling misfires | m-13, C-01 | Medium | Medium | Qualified IDs + DEC remapping | Architecture Board Chair |

---

## 6. Decision Matrix

| Finding | Disposition | Rationale | Decision Needed From |
|---|---|---|---|
| C-01 | **Need Business Decision** + **Need Architecture Decision** | DEC date vs downgrade “implementation-ready” | CTO, Business Owner, Architecture Board |
| C-02 | **Accept** | Clear ADR conflict; specification correction only | Architecture Board (ratify) |
| C-03 | **Need Business Decision** | Option A (minimal add-Case in Batch 1) vs Option B (remove outcome from Batch 1) | Business Owner + Domain PO |
| C-04 | **Accept** | Align to BR-001 exactly one | BA (execute after plan approval) |
| C-05 | **Need Business Decision** + **Need Architecture Decision** | Idempotency in vs auto-register out | Domain PO + Architect + Integration |
| C-06 | **Need Security Decision** | MUST + dependency owner + cleartext ban | Security |
| M-01 | **Accept** | Restore BR-001 E3 closure | Domain PO |
| M-02 | **Need Architecture Decision** | Sync vs async index on create | Solution Architect |
| M-03 | **Accept** / **Clarify** | Own or explicitly defer each obligation | BA |
| M-04 | **Accept** | Carry ADR-002 consequences | Architect + BA |
| M-05 | **Need Business Decision** | Transfer staged evidence vs void-only on A2 | Domain PO + Compliance |
| M-06 | **Accept** | Anchor membership invariant | Architect |
| M-07 | **Accept** | Status-qualify actions | BA |
| M-08 | **Need Business Decision** | Define Batch 1 360 subset contents | Domain PO |
| M-09 | **Accept** | Raise to MUST | Compliance + Security |
| M-10 | **Accept** | Raise uniformity to MUST | Security |
| M-11 | **Need Architecture Decision** | Transaction/saga boundary | Solution Architect |
| M-12 | **Accept** | ECMP outbox per ADR-009 | Architect |
| M-13 | **Accept** | NFR bounds | Architect + Performance |
| M-14 | **Need Security Decision** | Retention period / legal-hold for audit | Compliance / Security |
| M-15 | **Accept** | Fix catalog then FRD citations | API Catalog Owner |
| M-16 | **Accept** | KPI section + supervisor queue | Domain PO + Ops |
| M-17 | **Move to v1.2** *or* **Need Architecture Decision** | Full merge handling vs OQ in v1.1 | Integration Lead + Architect |
| m-01 | **Accept** | Align status language with C-01 | BA |
| m-02 | **Clarify** / **Need Business Decision** | Override policy or OQ | Ops Lead |
| m-03 | **Clarify** | New OQ — do not invent format | Ops + Admin |
| m-04 | **Accept** | Name and map flag | BA |
| m-05 | **Clarify** | New OQ for min justification | Ops Lead |
| m-06 | **Accept** | Carry BR-016 provisions | Compliance |
| m-07 | **Accept** | Aggregate payload cap | Security + Admin |
| m-08 | **Accept** | Extend effective-dating | Admin + BA |
| m-09 | **Accept** | Link Test Strategy / Traceability | QA |
| m-10 | **Accept** | Before/after History | BA |
| m-11 | **Need Architecture Decision** | Concurrency semantics | Architect |
| m-12 | **Clarify** | State matrix / OQ (with M-17) | Integration |
| m-13 | **Need Architecture Decision** | Qualified ID scheme vs DEC-only | Architecture Board |

**Disposition counts (proposed):**

| Disposition | Count |
|---|---|
| Accept | 20 |
| Clarify (incl. new OQ) | 6 |
| Need Business Decision | 5 (C-01, C-03, C-05, M-05, M-08; m-02 shared) |
| Need Architecture Decision | 7 (C-01, C-05, M-02, M-11, M-17, m-11, m-13) |
| Need Security Decision | 3 (C-06, M-14, + Security share on M-09/M-10 as Accept) |
| Move to v1.2 (candidate) | 1 (M-17 full handling) |
| Reject | 0 |
| Backlog | 0 (minors stay in v1.1 housekeeping unless CTO moves) |

---

## 7. Implementation Order (FRD Revision Sequencing)

Step-by-step order for **authoring FRD-CM-001 v1.1** after this plan is approved. Most critical first. No application code.

1. **Record CTO Decision Matrix outcomes** (especially C-01, C-03, C-05, C-06, M-08, M-05, M-17).
2. **Update Document Control / §2.1 / §1.1** per C-01 + m-01 (authority language).
3. **Correct §4 External Dependencies** (C-02; add anti-enumeration dependency from C-06).
4. **Align customer key cardinality** across FR-001/FR-002 (C-04).
5. **Apply Batch 1 scope resolution** for add-Case outcome (C-03) → update FR-003, FR-001 A2, UC, screens, audit events, §17.
6. **Apply auto-register / idempotency resolution** (C-05) → FR-001 A5/exceptions/FE list.
7. **Harden FR-002 security/audit** (C-06) + raise FR-003 E4 (M-10).
8. **UNVERIFIED / pending / orphan obligations** (M-01, M-03, m-04, m-10, M-16).
9. **Duplicate substrate & NFR** (M-02, M-13, m-11) + CLOSED qualification (M-07).
10. **Customer 360 Batch 1 subset** (M-08) + ADR-002 staleness (M-04).
11. **Attachment integrity package** (M-05, M-06, M-09, m-07, m-08 attachment side).
12. **Transaction boundary + notification outbox** (M-11, M-12).
13. **Audit retention / BR-016 gaps / Compliance refs** (M-14, m-06).
14. **API catalog collision fix + §13 re-cite** (M-15).
15. **Open Questions pack** (m-03, m-05, m-02 if needed, M-17/m-12).
16. **Namespace / tooling note** (m-13) and Related Documents (m-09).
17. **Refresh §15 BR mapping, §16 RTM, AC lists** for all touched FRs.
18. **Run Claude Delta Review → CTO Approval → LOCKED** (see §10).

---

## 8. Architecture Impact Summary

### 8.1 What changes (specification only)

| Area | Change Type |
|---|---|
| Document authority language | Readiness/status aligned to governance gates |
| §4 dependency boundary | Authorization removed from external API deps; anti-enumeration dependency added |
| Batch 1 scope edges | Add-Case outcome and/or auto-register/idempotency explicitly resolved |
| Validation cardinality | Exactly-one customer key type |
| Security RFC-2119 levels | Enumeration, anti-inference, evidence hash/access raised to MUST |
| UNVERIFIED lifecycle | Mandatory reconcile, aging, pending key context |
| Attachment staging | Discard removed; void/transfer rules; anchor invariant |
| Duplicate substrate | Index mapped; sync/async + NFR bounds stated |
| Integration reliability | ECMP notification outbox; transaction boundary stated |
| Traceability anchors | Unambiguous API IDs after catalog fix |
| Template completeness | KPI Impact; Compliance/NFR/Test Strategy links; new OQs |

### 8.2 What remains unchanged (LOCKED)

- Complaint Aggregate Root  
- Multi Case  
- Assignment on Case  
- SLA on Case  
- Working Day SLA  
- CustomerId-only / non-SoR Master Customer  
- Customer 360 as enterprise capability (Batch 1 may define **subset** only)  
- API First  
- No Direct Database Access  
- No Information Lost During Escalation  

### 8.3 Documents that need updates (after plan approval)

| Document | Update Trigger |
|---|---|
| `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.0.md` → v1.1 | Primary subject rewrite (post-approval) |
| `03 Functional Requirements/README.md` | Status/version pointer |
| `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` | Only if DEC path requires status/SoT note (C-01) — not content redesign |
| `07 API Catalog/` (generated + sources) | M-15 ID collision |
| `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md` | Cross-link / possibly FR-003 budgets recorded |
| `13 Test Strategy` | Consume updated ACs (m-09) |
| `26 Traceability` | RTM extension DM→…→Test |
| `17 Compliance` | Audit retention reference targets |
| This Revision Plan | Status → Approved after CTO decision |

### 8.4 ADRs affected

| ADR | Impact |
|---|---|
| ADR-002 (Accepted) | **Carry-forward into FR** (M-04); no ADR rewrite expected |
| ADR-008 | **Cited** to justify C-02 correction |
| ADR-009 | **Cited** for notification outbox (M-12); confirm applicability |
| ADR-014 (Proposed) | **Dependency** of C-01; FRD must not contradict; acceptance still required for foundation freeze |
| ADR-015 (Proposed) | **Dependency** of C-01 / identity contract; C-06 may reference masking expectations |
| New ADR? | **Only if** M-11 transaction/saga or M-02 sync-index decision exceeds FRD-local note — CTO may require thin ADR; otherwise FRD Architecture Constraints subsection suffices |

**No ADR is opened to change Locked Architecture listed in §0.3.**

---

## 9. Traceability Update Plan

When FRD v1.1 is authored, update the chain end-to-end:

```text
DM  →  BR  →  FR  →  UC  →  API  →  DB  →  UI  →  Test
```

| Layer | Action in v1.1 cycle |
|---|---|
| **DM** | Keep DM-CM-001…009; add logical entities if needed (search index, notification outbox, pending verification work item, idempotency key). |
| **BR** | No invented BRs; restore downgraded imperatives to match BR-CM-CAT-001; note DEC status for catalog authority (C-01). |
| **FR** | Apply accepted/clarified findings; RFC-2119 corrections; new OQs; KPI section. |
| **UC** | Adjust UC-CM-007 per C-03; add/extend UCs for reconcile, idempotent channel intake, supervisor aging if in scope. |
| **API** | Fix catalog collisions (M-15); re-cite; mark Planned capabilities for idempotency, duplicate check caps, outbox. |
| **DB** | Extend §14 logical mapping (index, outbox, pending context, hash mandatory, flags). |
| **UI** | Logical screens only: SCR-CM-003 actions per C-03/M-07; SCR-CM-006 as-of (M-04); 360 subset entry (M-08). No visual design. |
| **Test** | Map each AC to TC IDs in `13 Test Strategy` / `26 Traceability`; add negatives for C-04, C-05, C-06, M-06, M-10. |

Compact ownership:

```text
DM (Architect) → BR (Business Owner/BA) → FR (BA) → UC (BA)
    → API (Integration) → DB logical (Architect) → UI logical (BA/UX later)
    → Test (QA)
```

---

## 10. Definition of Done

```text
Revision Plan Approved (CTO / Architecture Board)
        ↓
FR Updated (FRD-CM-001 v1.1 authored per this plan only)
        ↓
Claude Delta Review (diff vs Draft v1.0 against Accept/Clarify decisions)
        ↓
CTO Approval (FRD-CM-001 v1.1)
        ↓
LOCKED (Batch 1 FR baseline frozen for implementation planning)
```

### 10.1 DoD checklist

| Gate | Criteria |
|---|---|
| Revision Plan Approved | This document Status = Approved; Decision Matrix dispositions recorded for all Critical findings |
| FR Updated | All Accept items reflected; Clarify items have OQ IDs; Move-to-v1.2 items listed in §17/§18; Locked Architecture untouched |
| Claude Delta Review | No new Critical introduced; no Locked Architecture drift; BR downgrades reversed where planned |
| CTO Approval | Sign-off on FRD-CM-001 v1.1 header |
| LOCKED | README + governance status updated; implementation planning may begin against v1.1 **only if** C-01 DEC/readiness path satisfied |

### 10.2 Explicit hold line

**No FRD rewrite and no implementation work** proceeds until **Revision Plan Approved**.

---

## 11. Open Decisions Summary (CTO Pack)

Must be decided in Sprint 1 before FRD authoring:

| ID | Question | Options |
|---|---|---|
| D-01 | Foundation readiness | (1) Obtain DEC + ADR-014/015 acceptance first; (2) Downgrade FRD to “specification baseline, pending DEC” |
| D-02 | Add Case on existing Complaint in Batch 1 | (A) Include minimal path; (B) Remove from Batch 1 flows/audit/UC |
| D-03 | Channel auto-register | (A) Idempotency in Batch 1; (B) Auto-register out of Batch 1 |
| D-04 | Enumeration controls | Approve MUST + §4 dependency owner (recommended) |
| D-05 | Customer 360 Batch 1 subset | Approve minimum active-complaint highlight as MUST |
| D-06 | Staged evidence on create-cancel after duplicate | Transfer to surviving Complaint vs void-with-reason only |
| D-07 | Customer merge handling | OQ in v1.1 vs full design in v1.2 |

---

## 12. Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.1 | 2026-07-29 | Principal Enterprise Solution Architect / Requirements Manager | Initial Revision Plan from GOV-REV-FRD-CM-001 Complete review — analysis only, no FRD rewrite |
| 1.1 | 2026-07-29 | Requirements Manager / CTO | Status → Approved; FRD-CM-001 v1.1 LOCKED under D-08 after GOV-DELTA-FRD-CM-001 |

---

## Related

- Subject (LOCKED SoT): `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md`
- Baseline Draft: `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.0.md`
- Review: `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Architecture_Review_v1.0.md` (GOV-REV-FRD-CM-001)
- Delta Review: `18 Architecture Governance/reviews/ECMP_FRD_CM_001_Delta_Review_v1.1.md` (GOV-DELTA-FRD-CM-001)
- Release Notes: `18 Architecture Governance/reviews/ECMP_FRD_CM_001_v1.1_LOCKED_Release_Notes.md`
- BR Catalog: `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md`
- ADRs: ADR-002, ADR-008, ADR-009, ADR-014, ADR-015
- API Catalog: `07 API Catalog/API_CATALOG.generated.md`
- NFR: `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md`
- Compliance: `17 Compliance`
- Test / Traceability: `13 Test Strategy`, `26 Traceability`

---

*End of GOV-RP-FRD-CM-001 — FRD-CM-001 Revision Plan v1.1. Approved. FRD-CM-001 v1.1 LOCKED (D-08).*
