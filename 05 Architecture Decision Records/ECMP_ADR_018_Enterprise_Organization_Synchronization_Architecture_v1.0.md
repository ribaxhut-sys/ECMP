# ECMP_ADR_018_Enterprise_Organization_Synchronization_Architecture_v1.0

| Field | Value |
|---|---|
| ID | ADR-018 |
| Version | 1.0 |
| Owner | Solution Architect / Enterprise Integration Architect |
| Reviewer | Architecture Board / Security Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (Accepted with Conditions — PROGRAM-BOARD-006) |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |

- ADR Status: **Accepted with Conditions** (PROGRAM-BOARD-006 **BR-013**)
- Board Disposition: **Accepted with Conditions** — conditions **C-B6-1**…**C-B6-7** apply. Mode B / Batch-2 / Enterprise customer remain **CLOSED** (C-B6-1 / PROGRAM-BOARD-004 C-7). Org-model gap remains Mode B unlock prerequisite (C-B6-3). Resolution: `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`
- Prior dispositions (historical): Proposed; PROGRAM-BOARD-005 Ready for Resolution — superseded as *active* disposition by BR-013
- Date: 2026-07-30
- Program: **PROGRAM-ENTERPRISE-004** — Enterprise Organization Synchronization ADR
- Decision Owners: Enterprise Integration Architect, Solution Architect, Security Architect
- Related Domains: Core Platform, ECMF (Complaint Management), Administration
- Related ADRs: ADR-002, ADR-008, ADR-014, ADR-015, ADR-016, ADR-017
- Related decisions: DEC-020; PROGRAM-BOARD-004 (BR-009 / BR-010; C-7 gates); PROGRAM-BOARD-005; PROGRAM-BOARD-006 (BR-011 / BR-012 / BR-013)
- Baseline: ADR-014 v1.4 and ADR-015 v1.3 **Accepted with Conditions** (PROGRAM-BOARD-004); ADR-016/017 **Accepted with Conditions** (BR-011/BR-012); this ADR **Accepted with Conditions** (BR-013); Mode B / Batch-2 / Enterprise customer remain **CLOSED**

## Purpose of this ADR

Define the **Enterprise Organization Synchronization Architecture** between the Enterprise Platform and ECMP.

This ADR defines **governance and architecture** only:

- purpose of organization synchronization
- System of Record and ownership
- consumption boundary
- relationships to Identity, Entitlement, and Complaint Module
- consistency model and failure behavior
- governance, deferred decisions, risks, and future evolution

This ADR does **not** define:

- synchronization APIs
- webhook payloads
- database schema
- scheduling / cadence
- cache strategy (TTL, invalidation algorithms, storage layout)
- redesign of ADR-015 Identity Contract
- redesign of ADR-017 Entitlement Architecture
- redesign of ADR-014 Complaint Module ownership
- OpenAPI changes
- Mode B unlock

---

## Terminology

Aligned with ADR-014 / ADR-015 / ADR-016 / ADR-017 unless refined below.

| Term | Meaning |
|---|---|
| **Enterprise Organization Structure** | The enterprise-owned hierarchy of Organization, Branch, and Department (and any future levels decided by Enterprise Platform). |
| **Organization Reference** | Opaque enterprise identifier used by ECMP for scoping and correlation (`organization_id`, `branch_id`, `department_id` per ADR-015). |
| **Organization Synchronization** | The governed capability that keeps Organization References **resolvable** inside ECMP for authorization and operational use, without making ECMP the organizational SoR. |
| **Local Organizational Projection** | Non-authoritative ECMP-held representation of enterprise organization structure used for resolution, display, and AuthZ inputs. Projection ≠ SoR. |
| **Resolvability** | Ability to map an Organization Reference to enough enterprise organizational context for correct authorization scoping and safe operational use. |
| **Identity (ADR-015)** | Who the subject is, including required org reference claims. |
| **Entitlement (ADR-017)** | Whether the subject may enter the ECMP Complaint module. |
| **Complaint Roles / Permissions** | Post-admission AuthZ (ADR-014 mapping → ADR-008 permissions). |

---

## 1. Context

ADR-014 decided:

- Under Mode B, Enterprise Platform owns Organization, Branch, and Department.
- ECMP stores **references only** and must not become master of organizational hierarchy.
- Organization Synchronization is an **Architecture Dependency** (not an optional enhancement): authorization depends on organization hierarchy remaining available and correct.
- Protocol, frequency, and transport for Organization Synchronization were deferred to a follow-on ADR.

ADR-015 requires Mode B identities to carry exactly one `organization_id`, one `branch_id`, and one `department_id`, and states that hierarchy resolution semantics are an Enterprise Platform / Organization Synchronization concern.

ADR-016 / ADR-017 preserve trust and entitlement ordering and do not redefine organization ownership.

Architecture Board review of ADR-014 (REC-13) reclassified org synchronization as a **decision dependency** and recommended the ADR-002 pattern shape: local read-only consumption, defined refresh (deferred here), “as of” semantics, ECMP never authoritative.

Without this ADR:

- Teams may treat ECMP local branch models as enterprise org SoR.
- Stale or unresolved org refs may silently grant or deny access incorrectly.
- Org membership may be confused with entitlement or permissions.
- Sync API / schema work may start before ownership and consistency rules are accepted.

PROGRAM-ENTERPRISE-004 closes the **architecture** gap. Transport, schema, scheduling, and cache mechanics remain deferred under this ADR’s governance (see §11).

## 2. Problem Statement

If Organization Synchronization architecture is undefined:

1. ECMP may invent or mutate enterprise organization hierarchy as if it were SoR.
2. ADR-015 org claims may be present but unresolvable for AuthZ scoping.
3. Authorization correctness depends on undefined freshness and failure behavior.
4. Org structure changes upstream may orphan live complaint scopes without a governed reaction model.
5. Entitlement, identity, and org sync concerns may collapse into one ad hoc integration.
6. Implementation may unlock Mode B org wiring before Architecture Board acceptance.

## 3. Decision Drivers

- Preserve Organization SoR = Enterprise Platform (ADR-014).
- Preserve Identity SoT = ADR-015; Protocol SoT = ADR-016; Entitlement SoT = ADR-017; Permission SoT = ADR-008; Complaint ownership = ADR-014.
- Align with ADR-002 non-SoR pattern: consume / project; never become master.
- Keep AuthZ inputs honest: unresolved or contradicted org refs must not fail open.
- Remain **implementation-agnostic**: architecture without APIs, schema, schedule, or cache strategy.
- Do not unlock Mode B / Batch-2 / enterprise customer (PROGRAM-BOARD-004 C-7).

## 4. Options Considered

### Option A — ECMP owns local organization masters under Mode B

- Pros: simplest for local joins and UI.
- Cons: contradicts ADR-014 ownership; creates dual SoR; diverges from enterprise hierarchy.
- Verdict: **Rejected.**

### Option B — Real-time read-through to Enterprise Platform on every AuthZ decision; no local projection

- Pros: maximal freshness in theory.
- Cons: couples every authorization decision to enterprise availability; undefined offline/degraded posture; still requires contract for identifiers and failure behavior; encourages premature API design in this ADR.
- Verdict: **Rejected** as the sole architecture for this ADR (may remain a future *implementation* profile subordinate to this ADR).

### Option C — Enterprise SoR + ECMP non-authoritative local projection; sync architecture governed here (chosen)

- Pros: matches ADR-014 dependency and ADR-002 pattern; keeps SoR clear; allows deferred transport/cadence; supports resolvability for AuthZ inputs; fail-closed rules can be stated without designing APIs.
- Cons: eventual consistency / staleness risk must be governed explicitly.
- Verdict: **Accepted** as the architecture approach of this ADR.

---

## 5. Decision

ECMP adopts the following **Enterprise Organization Synchronization Architecture** for Mode B.

### Decision Summary

1. **Purpose:** Keep enterprise Organization References resolvable for authorization scoping and operational use under Mode B.
2. **System of Record:** Enterprise Platform owns Organization / Branch / Department hierarchy truth.
3. **ECMP role:** Consume and maintain **non-authoritative local projections** and store references only; never author enterprise hierarchy truth.
4. **Consistency:** Eventual consistency with explicit **“as of”** semantics; enterprise truth wins on conflict.
5. **Failure:** Unresolved required Organization References for AuthZ → **deny / fail closed** (no invented hierarchy).
6. Transport, APIs, schema, scheduling, and cache strategy are **deferred**.
7. This ADR does **not** unlock Mode B implementation.

---

## 6. Purpose of Organization Synchronization

Organization Synchronization exists to answer:

> Are the enterprise organization / branch / department references used by ECMP still resolvable and safe as **authorization and operational inputs**, without ECMP becoming organizational SoR?

It is **not** used to answer:

| Question | Answered by |
|---|---|
| Who is the subject? | ADR-015 Identity Contract |
| Is the presentation authentic? | ADR-016 Protocol & Binding |
| May the subject enter ECMP Complaint? | ADR-017 Entitlement Gate |
| What complaint role / permissions apply? | ADR-014 → ADR-008 |
| What complaint business action is allowed by domain rules? | ECMF / complaint FRDs & services |

### Normative purpose statements

1. Organization Synchronization is a **prerequisite for correct Mode B authorization inputs**, not an optional reporting enhancement.
2. Synchronization preserves **resolvability** of ADR-015 Organization References.
3. Synchronization must not redefine identity claims, entitlement grants, permissions, or complaint lifecycle rules.
4. Display / lookup convenience is secondary; **authorization correctness** is primary.

---

## 7. System of Record

| Data concern | System of Record | ECMP posture |
|---|---|---|
| Organization / Branch / Department hierarchy | **Enterprise Platform** | Reference + non-authoritative projection only |
| Organization Reference identifiers used in identity | **Enterprise Platform** (via ADR-015 contract) | Consume opaque refs; do not re-key enterprise IDs as ECMP-owned masters |
| Local complaint records scoped *by* org refs | **ECMP** (complaint SoR) | Owns complaint facts; org fields remain foreign references |
| Role-Permission Matrix | **Core Platform (ADR-008)** | Unchanged |
| Enterprise entitlement grants | **Enterprise Platform (ADR-017)** | Unchanged |

### Hard SoR rules

1. ECMP must not become master source for organizational hierarchy under Mode B.
2. Conflict between local projection and Enterprise Platform truth → **Enterprise Platform wins**.
3. Local projection may be incomplete or stale; it must never be promoted to enterprise SoR.
4. Mode A local organizational models (if any) do not become Mode B enterprise SoR by silence; Mode B cutover remains a separate DEC (ADR-014).

---

## 8. Organization Ownership

Enterprise Platform owns:

- Creation, update, restructure, merge, split, and retirement of Organization / Branch / Department
- Identifier stability policy for organization references
- Authoritative hierarchy semantics (parent/child, effective dating if any)

ECMP owns:

- Storage of Organization References on local profiles / complaint authorization context (as references)
- Non-authoritative local organizational projection lifecycle *as consumer*
- Complaint business data that *uses* those references for scope

ECMP must not own:

- Enterprise hierarchy authorship
- Cross-module enterprise org renames as local truth
- “Shadow” org masters that diverge intentionally from Enterprise Platform

### Organizational model gap (recorded — Mode B prerequisite)

ADR-014 records that current ECMP foundation may be branch-centric relative to the three-level ADR-015 reference set (`organization_id` + `branch_id` + `department_id`).

**Normative governance (audit K-7):** closing that implementation gap — first-class resolvable masters / projections for **organizations**, **branches**, and **departments** aligned to ADR-015 — is a **Mode B prerequisite**. Mode B runtime unlock (PROGRAM-BOARD-004 C-7) **MUST NOT** be granted while required Organization References remain systematically unresolvable under §14.

This ADR still does **not** authorize schema redesign by itself; gap closure is planned under subordinate integration/delivery work after Accept, but **Accept of this ADR does not waive the Mode B prerequisite**.

---

## 9. Consumption Boundary

| Boundary | Responsibility |
|---|---|
| **Enterprise Platform** | Authoritative organization structure SoR; publish / expose truth through enterprise-governed integration (mechanism deferred) |
| **ECMP Identity Adapter / platform boundary** | Terminate mode-dependent organization resolution inputs; correlate ADR-015 org claims to resolvable organizational context for AuthZ |
| **ECMP AuthZ / scope evaluation** | Consume resolved organizational context as **inputs**; do not call Enterprise Platform ad hoc from domain services as a second ownership path |
| **ECMP Business Module (Complaint)** | Remain mode-independent; consume already-resolved authorization context; must not branch on sync transport |
| **Frontend / browser** | Must not be treated as organization authority |

### Containment (ADR-014)

- Identity-mode and organization-resolution divergence terminate at the Identity Adapter / platform boundary.
- Complaint business rules and case state machines remain mode-independent.
- Organization Synchronization mechanics must not leak into complaint domain conditionals (`if sync_mode`, `if enterprise_org_api`, etc.).

---

## 10. Relationship with Identity Contract (ADR-015) — Identity SoT

| | Identity (ADR-015) | Organization Synchronization (this ADR) |
|---|---|---|
| Question | Which org refs belong to the subject? | Can those refs be resolved safely for AuthZ/ops? |
| SoT | ADR-015 bilateral claim contract | Enterprise Platform org structure + sync architecture here |
| Required claims | `organization_id`, `branch_id`, `department_id` (exactly one each in v1.0) | Does not add/remove/redefine those claims |
| Failure | Missing required org claims → deny | Present but unresolvable required refs for AuthZ → deny |

### Normative

1. This ADR must not redesign ADR-015 claim tables, cardinality, or hierarchy assumption.
2. ADR-015 identifiers remain opaque enterprise references; sync supplies resolvability, not a second identity vocabulary.
3. Hierarchy traversal / descendant scope semantics, if required beyond opaque refs, are an Organization Synchronization / Enterprise Platform concern and require explicit future decision (deferred) — they are not invented inside complaint services.

---

## 11. Relationship with Entitlement (ADR-017) — Entitlement SoT

| | Entitlement (ADR-017) | Organization Synchronization (this ADR) |
|---|---|---|
| Question | May the subject enter ECMP Complaint? | Are org refs usable as AuthZ inputs? |
| Granularity | Module admission (coarse) | Organizational structure resolvability |
| SoT | Enterprise Platform entitlement | Enterprise Platform organization structure |

### Normative

1. Organization membership / hierarchy presence **must not** substitute for entitlement.
2. Entitlement grant **must not** invent organization hierarchy.
3. Pipeline remains: Trust (ADR-016) → Identity (ADR-015) → Entitlement Gate (ADR-017) → Complaint Roles (ADR-014) → Permissions (ADR-008), with organization resolvability required wherever AuthZ consumes org scope inputs.
4. This ADR does not change Entitlement Gate ordering or representation deferrals (E-01 et al.).

---

## 12. Relationship with Complaint Module (ADR-014) — Complaint ownership

| | Complaint Module | Organization Synchronization |
|---|---|---|
| Owns complaint lifecycle / business rules | Yes (ECMP) | No |
| Owns enterprise org hierarchy | No | No (Enterprise Platform) |
| Uses org refs | As scope / correlation inputs | Ensures refs remain resolvable |

### Normative

1. Complaint ownership remains ADR-014.
2. Live complaints may retain historical Organization References after upstream restructure; business retention vs re-scope policy is a future governed decision (deferred), but ECMP must not silently rewrite enterprise SoR.
3. DEC-020 complaint namespace remapping remains orthogonal; this ADR does not alter `/api/v1/cm` vs `/api/v1/complaints` coexistence.
4. Permission SoT remains ADR-008; org sync must not embed permissions into organizational projections.

---

## 13. Consistency Model

Architecture consistency posture (implementation-agnostic):

1. **Eventual consistency** between Enterprise Platform SoR and ECMP local organizational projection is the default architectural model.
2. Consumers of organizational data MUST treat projections as **“as of”** a last-known synchronization point (exact timestamp/field mechanics deferred).
3. **Enterprise truth wins** on conflict; ECMP must not “heal” conflicts by writing back authoritative hierarchy.
4. Authorization decisions that depend on Organization References require **resolvability** at decision time per failure rules in §14.
5. Freshness targets, refresh intervals, push vs pull, and cache eviction are **deferred** (see §16). This ADR forbids equating “eventual consistency” with “fail open on missing org context.”

### Relationship to ADR-002

This ADR adopts the same **non-SoR consumption pattern** as ADR-002 (local non-authoritative consumption; ECMP never authoritative). It does **not** copy customer-master integration details and does **not** define a cache strategy.

---

## 14. Failure Behavior (Fail Closed for AuthZ inputs)

| Condition | Required behavior |
|---|---|
| Required ADR-015 org claims missing | Deny (ADR-015) — unchanged |
| Required Organization Reference present but **unresolvable** for AuthZ scoping | **Deny** AuthZ decision that depends on that scope (fail closed) |
| Local projection conflicts with enterprise-provided truth | Enterprise wins; do not prefer local invention |
| Upstream org unit retired / restructured while complaints still reference it | Do not invent replacement hierarchy; retain reference integrity for historical records; AuthZ for *new* decisions must follow fail-closed resolvability rules; remediation policy deferred |
| Sync channel unavailable | Must not fail open by fabricating org structure. **Last-known projection may be used only when all Organization References required for the AuthZ decision remain resolvable** under this §14 table. If any required reference is unresolvable, **deny** scope-dependent AuthZ. Subordinate sync profiles **MUST NOT** authorize a weaker posture. Any exception (time-boxed degraded allow, break-glass, etc.) requires an explicit **Architecture Board** Resolution citing this ADR — profiles alone cannot grant it (aligned to ADR-016 §9.3 / audit K-5). |
| Ambiguous hierarchy resolution | Deny / refuse unsafe expansion (no silent descendant expansion without an accepted scope-semantics decision) |
| Org membership observed without entitlement | Still deny module entry (ADR-017) |

### Prohibited behaviors

1. Creating enterprise organization masters inside ECMP under Mode B.
2. Treating unresolved org refs as “match all” or “unscoped allow.”
3. Inferring entitlement from organization membership.
4. Inferring permissions from organization hierarchy nodes.
5. Rewriting ADR-015 claim meanings to bypass sync dependency.
6. Embedding sync transport details into complaint domain logic.
7. Using a subordinate “governance / sync profile” to loosen fail-closed AuthZ resolvability without Architecture Board Resolution (ADR-016 §9.3).

---

## 15. Governance Responsibilities

| Topic | Rule |
|---|---|
| Architecture changes to org SoR / ownership / fail-closed rules | Require ADR revision + Architecture Board |
| Sync mechanism profile (API/event/schedule/cache) | Change-controlled Integration/Architecture artifact **subordinate** to this ADR; must not rewrite ADR-015/017/008/014 |
| Fail-closed subordination (ADR-016 §9.3) | Sync / cache / cadence profiles **MUST NOT** loosen §14 AuthZ fail-closed resolvability, invent default-allow, or authorize degraded-allow. Any relaxation requires **Architecture Board** Resolution citing this ADR. |
| Mode B org-model gap (audit K-7) | Three-level resolvable org masters/projections are a **Mode B prerequisite** — see §8 gap statement; C-7 unlock forbidden while gap remains |
| Identifier stability / breaking org-key changes | Enterprise Platform + bilateral impact analysis; may require ADR-015 contract revision if claim semantics change |
| Audit | Enterprise Platform audits authoritative org structure changes; ECMP audits AuthZ denials due to unresolvable org refs and projection reconciliation outcomes |
| RACI | Enterprise Integration Architect R/A for sync architecture boundaries; Security Architect R/A for AuthZ fail-closed impact; Enterprise Platform owns SoR; Architecture Board adjudicates material disputes |
| Relationship to PROGRAM-BOARD-004 | C-7 remains: Mode B / Batch-2 / Enterprise customer **CLOSED** |
| Relationship to DEC-020 | Orthogonal; no complaint SoT namespace change |

---

## 16. Deferred Implementation Decisions

| ID | Deferred item | Notes |
|---|---|---|
| O-01 | Synchronization **APIs** | Explicitly out of scope of this ADR |
| O-02 | Webhook / event **payloads** | May later align to Event Catalog only after Board-accepted need |
| O-03 | Database **schema** for projections / org-model gap closure | **Mode B prerequisite** (audit K-7) — delivery planning allowed; Mode B unlock forbidden while gap remains; schema not authorized solely by this ADR |
| O-04 | Scheduling / cadence / refresh triggers | Must preserve fail-closed AuthZ input rules |
| O-05 | Cache strategy (TTL, invalidation, storage) | Deferred; architecture only allows non-authoritative projection concept |
| O-06 | Hierarchy traversal / descendant scope semantics | Must be explicit before silent expansion in AuthZ |
| O-07 | Upstream delete/restructure remediation for live complaints | Retention vs re-scope policy |
| O-08 | Push vs pull vs login-time hydration profile | Subordinate integration profile |
| O-09 | Mode B implementation authorization & OpenAPI | Explicitly not granted here |
| O-10 | Multi-tenancy / multi-org packaging | Remains out of scope per ADR-014 single-tenant assumption unless Board decides otherwise |

---

## 17. Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | Stale org projection → incorrect grant/deny | High | Fail-closed resolvability; enterprise wins; “as of” semantics |
| R-02 | ECMP becomes de facto org SoR | High | Ownership §§7–8; prohibited behaviors §14 |
| R-03 | Org membership treated as entitlement | High | Relationship §11 / ADR-017 |
| R-04 | Unresolved refs silently unscoped | Critical | Failure table §14 |
| R-05 | Upstream restructure orphans complaint scopes | Medium–High | Deferred O-07; no invented hierarchy |
| R-06 | Implementing sync/OpenAPI on Proposed ADR | High | Status Proposed; non-authorization §19 |
| R-07 | Org-model gap closure mistaken for Mode B unlock | High | Gap recorded; C-7 preserved |
| R-08 | Descendant scope assumed without decision | High | O-06; ambiguous → deny unsafe expansion |
| R-09 | Sync logic leaks into complaint domain | Medium | Containment §9 |
| R-10 | Dual vocabulary (local branch ids vs enterprise refs) | High | ADR-015 refs remain canonical under Mode B; no silent remap |

---

## 18. Future Evolution

Permitted evolution paths **after** Architecture Board acceptance of this ADR (still subject to separate implementation authorization and C-7):

1. Integration profile(s) for transport (event / pull / hybrid) subordinate to this ADR.
2. Org-model gap closure delivery planning under Mode B authorization.
3. Explicit scope-semantics ADR/DEC if descendant/effective-dating rules are required.
4. Restructure/remediation playbooks for historical complaint references.
5. Alignment with future multi-module enterprise organization consumption (still Enterprise Platform SoR).

Non-evolution (not implied by this ADR):

- Mode B unlock
- Identity contract rewrite
- Entitlement redesign
- Permission SoT move out of ADR-008
- Complaint module ownership transfer

---

## 19. Explicit Non-Authorization

This ADR (even if later Accepted) does **not** by itself authorize:

1. Mode B runtime enablement
2. Synchronization API design or publication
3. Webhook payload contracts
4. Database schema changes / migrations
5. Scheduling jobs or cache implementations
6. OpenAPI changes
7. Redesign of ADR-015 / ADR-016 / ADR-017 / ADR-008 / ADR-014 normative bodies
8. OD-FE-002 / Mode B frontend AuthN bridge
9. Batch-2 or enterprise customer production
10. Mode A → Mode B cutover

---

## 20. Consequences

### Positive

- Closes ADR-014 Organization Synchronization architecture dependency without implementation invention.
- Clarifies SoR, ownership, consumption boundary, and fail-closed AuthZ input behavior.
- Preserves Identity / Protocol / Entitlement / Permission / Complaint SoT boundaries.
- Reuses ADR-002 non-SoR pattern at architecture level without prescribing cache mechanics.

### Trade-offs

- Eventual consistency / staleness remains a managed risk until subordinate integration profiles exist.
- Org-model gap and restructure remediation remain deferred delivery concerns.
- Mode B still blocked on broader Board unlock conditions (C-7) and sibling Proposed ADRs as applicable.

### Non-consequences

- No Mode B unlock
- No OpenAPI / schema / API / webhook / scheduler / cache delivery
- No redesign of ADR-015 claims or ADR-017 entitlement
- No Complaint Module ownership change

---

## 21. Follow-ups

- [x] Architecture Board review of **ADR-018** → Accepted with Conditions (PROGRAM-BOARD-006 **BR-013**)
- [x] Keep ADR-016 / ADR-017 Accept tracks coordinated as package (PROGRAM-BOARD-006); sequencing for Mode B coding per C-B6-5
- [x] After Accept: draft subordinate Organization Sync Integration Profile (O-01…O-05) — **Draft** `org-sync-integration-ecmp-v0.1` (`10 Security and Access Standards/ECMP_ORG_SYNC_INTEGRATION_PROFILE_v0.1.md`); schema delivery still not authorized; Mode B CLOSED
- [x] After Accept: plan org-model gap closure as delivery work — **Draft** `ECMP_PROGRAM_ORG_GAP_DELIVERY_PLAN_v0.1.md` (C-B6-3; Phase B+ not authorized here)
- [x] Decide hierarchy scope semantics (O-06) — **Proposed** DEC-021 (exact-ref interim; awaiting Accept)
- [x] Decide restructure/orphan remediation policy (O-07) — **Proposed** DEC-022 (retain + fail-closed interim; awaiting Accept)
- [ ] Editorial sync to Solution Architecture / Integration catalogs after Accept (no contract invention in this ADR)
- [x] Do **not** treat Accept as Mode B unlock (PROGRAM-BOARD-006 C-B6-1 / PROGRAM-BOARD-004 C-7)

---

## 22. ADR Relationship

| ADR | Relationship |
|---|---|
| ADR-002 | **Consistent** — non-SoR local consumption pattern for data ECMP does not own |
| ADR-008 | **Preserved** — Permission SoT unchanged; org sync must not become a permission catalog |
| ADR-014 | **Complements** — fulfills Organization Synchronization architecture dependency; Complaint ownership preserved |
| ADR-015 | **Preserved** — Identity SoT unchanged; sync supplies resolvability for org reference claims |
| ADR-016 | **Orthogonal / Preserved** — Protocol SoT unchanged |
| ADR-017 | **Complementary / Preserved** — Entitlement SoT unchanged; org ≠ entitlement |
| ADR-013 | **Orthogonal** — frontend stack remain active (BR-007) |

No supersession is declared by this ADR.

---

## 23. Document History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | PROGRAM-ENTERPRISE-004 — initial Proposed Enterprise Organization Synchronization Architecture; preserves ADR-015/016/017/008/014 SoT boundaries; Mode B remains CLOSED |
| 1.0a | 2026-07-30 | Audit **K-5** — remove profile-gated fail-open from §14; Board required for any degraded AuthZ; §15 aligned to ADR-016 §9.3. Audit **K-7** — org-model gap elevated to **Mode B prerequisite** |
| 1.0b | 2026-07-30 | PROGRAM-BOARD-006 **BR-013** — Accepted with Conditions (C-B6-1…C-B6-7); metadata only; Mode B CLOSED; org-gap prerequisite remains |

---

*End of ADR-018 v1.0. Architecture Accept With Conditions — no Mode B unlock; no schema / API / webhook delivery authorized.*

---

*End of ADR-018 v1.0. Architecture only — no implementation; no OpenAPI / schema / API / webhook / schedule / cache design; no modifications to ADR-014/015/016/017 normative bodies.*
