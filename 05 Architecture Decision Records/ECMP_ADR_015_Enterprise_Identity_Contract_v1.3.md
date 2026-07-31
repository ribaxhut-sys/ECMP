# ECMP_ADR_015_Enterprise_Identity_Contract_v1.3

| Field | Value |
|---|---|
| ID | ADR-015 |
| Version | 1.3 |
| Owner | Solution Architect |
| Reviewer | Security Architect / Architecture Board |
| Approver | Architecture Board |
| Status | 🟢 Approved (Accepted with Conditions — PROGRAM-BOARD-004) |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |

- ADR Status: **Accepted with Conditions** (PROGRAM-BOARD-004 **BR-010**)
- Board Disposition: **Accepted with Conditions** — conditions **C-1**, **C-3**, **C-7** apply. Under **C-3**, ADR-015 is a **Bilateral Contract**. Mode B / Batch-2 / Enterprise customer remain **CLOSED** (C-7). Resolution: `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`
- Prior dispositions (historical): PROGRAM-ADR-002 **BR-006** Needs Revision; PROGRAM-ADR-004 Revised — Pending Board Review — superseded as *active* disposition by BR-010
- Date: 2026-07-30
- Decision Owners: Solution Architect, Security Architect
- Related Domains: Core Platform, ECMF (Complaint Management), Administration, Notification, Dashboard & Analytics, KPI & Performance
- Related ADRs: ADR-002, ADR-007, ADR-008, ADR-012, ADR-014
- Package: Accepted with ADR-014 as coordinated package (PROGRAM-BOARD-004). Prior authoring: PROGRAM-ADR-004 / PROGRAM-ENTERPRISE-001
- Identity Contract Version: **1.0** (document revision 1.3 does not change contract major/minor claim set)
- Governance posture: **Accepted Architecture — Implementation Deferred** (Mode B Closed)

## Terminology

Authoritative terms for this ADR package (identical in ADR-014). These terms must not be used interchangeably.

| Term | Meaning |
|---|---|
| **Enterprise Platform** | The larger enterprise application platform that hosts multiple business modules and provides shared enterprise capabilities (Portal, Authentication, SSO, User Directory, Organization structure, Enterprise Navigation, Session, Identity Audit, **Enterprise Global Notification**). Under Mode B, it owns Authentication and Enterprise Identity. |
| **Core Platform** | The ECMP domain that provides shared platform capabilities inside the ECMP system boundary. It owns the Role-Permission Matrix SoT (ADR-008). It is not the Enterprise Platform. |
| **ECMP Business Module** | The Complaint Management business module that operates within the Enterprise Platform under Mode B (or as a standalone application under Mode A). Owns complaint lifecycle capabilities and Complaint Authorization / Complaint Roles mapping after the Enterprise Entitlement Gate. |
| **ECMP Solution** | The end-to-end ECMP solution design spanning business domains, solution architecture, and related ADRs for delivering Complaint Management. Distinct from the Enterprise Platform as a whole. |
| **ECMP Application** | The runnable ECMP software system (services and operator UI) that implements the ECMP Business Module. May be deployed in Mode A (Standalone) or Mode B (Enterprise). |
| **Enterprise Global Notification** | Cross-module, platform-owned notification/delivery capability of the Enterprise Platform (for example platform-wide alerts or shared notification shell). Not the ECMP complaint-domain notification surface. |
| **ECMP Business Notification** | Notification capabilities owned by the ECMP Business Module / Notification domain for complaint- and module-scoped events, preferences, and delivery within ECMP. Distinct from Enterprise Global Notification. |
| **Identity Adapter** | The ECMP boundary component that terminates Mode A / Mode B identity-mode divergence (AuthN consumption, claim validation against ADR-015, Entitlement Gate application, local profile correlation). Business modules must not branch on deployment mode. |

## 1. Context

ADR-014 establishes that ECMP operates as an Enterprise **Business Module** and that the **Enterprise Platform** owns Enterprise Identity under **Mode B (Enterprise)**. ECMP consumes identity; it does not provide it.

That boundary is necessary but incomplete. Without a versioned **identity contract**, each team may assume different required attributes, different key semantics, and different failure behavior when identity is incomplete or evolves.

An independent architecture review of ADR-014 recorded this gap explicitly: ownership of the identity contract as a versioned artifact, and how that contract is governed, was not stated.

This ADR defines that contract.

This ADR defines the **identity interface only**. It does not define authentication protocols, credential formats, transport mechanisms, or implementation technology.

## 2. Problem Statement

If the identity interface between the Enterprise Platform and ECMP is not contracted:

- Required identity attributes may be assumed inconsistently across modules and environments.
- ECMP may incorrectly treat mutable or non-unique attributes (for example email) as identity keys.
- Unknown or newly introduced attributes may be treated as breaking changes, or silently required without governance.
- Missing attributes may be handled inconsistently — sometimes defaulted, sometimes ignored — producing insecure or non-deterministic access outcomes.
- Identity evolution may become coupled to ECMP implementation releases, slowing enterprise platform change and ECMP change alike.
- Local ECMP profiles may drift from enterprise truth if ECMP is permitted to modify enterprise identity attributes.

These failures undermine the Enterprise Mode boundary decided in ADR-014 and the non-SoR principle established in ADR-002.

## 3. Decision

ECMP adopts a canonical **Enterprise Identity Contract** between the Enterprise Platform and ECMP.

### Decision Summary

- **Enterprise Platform owns identity.**
- **ECMP consumes identity.**
- **ECMP must never modify enterprise identity.**
- The contract defines required claims, optional claims, claim semantics, versioning, lifecycle expectations, fail-closed rules, compatibility rules, and the trust boundary.
- **Unknown claims are ignored unless explicitly marked as required.**
- **Missing required claims cause access denial.**
- **The identity contract is versioned independently from implementation.**

This ADR is the **Source of Truth** for the Enterprise Identity Contract consumed by ECMP under Mode B. ADR-014 shall point here for claim SoT and shall not maintain a competing required-claim list.

Protocol selection, credential binding, and runtime transport remain out of scope and require separate decisions.

### Assumptions

- Runtime enforcement of this contract applies to **Mode B (Enterprise)**. Mode A (Standalone) is outside runtime enforcement but must not contradict these ownership rules when Mode B is later enabled (see §11).
- ADR-013 (frontend technology stack) is **orthogonal** and remains active per PROGRAM-ADR-002 BR-007. This ADR does not supersede ADR-013.
- Claim names here are canonical for ECMP; wire-name mapping belongs to a future protocol/binding ADR.
- **Organization hierarchy assumption (project):** Mode B identities consumed by ECMP are assumed to carry **exactly one** `organization_id`, **exactly one** `branch_id`, and **exactly one** `department_id`. Partial hierarchy (missing level) is **not** supported under contract v1.0 — absence of any required org claim is fail-closed denial (§5 / §10). Changing this assumption is a **breaking** contract change.

## 4. Identity Ownership

| Concern | Owner | ECMP Role |
|---|---|---|
| Enterprise person / subject identity | Enterprise Platform | Consume only |
| Enterprise identity key (`external_user_id`) | Enterprise Platform | Reference only |
| Display and contact attributes supplied as claims | Enterprise Platform | Consume / cache locally as non-authoritative **projections** |
| Organization / branch / department identity references | Enterprise Platform | Reference only |
| Employment / entitlement-relevant status signals in the identity payload | Enterprise Platform | Consume for access and lifecycle decisions |
| ECMP local profile (preferences, last access, local module status) | ECMP Business Module | Own |
| Role-Permission Matrix SoT (Role, Permission, Role-Permission, User-Role) | **Core Platform (ADR-008)** | Consume / enforce via Core Platform — **not** a second SoT |
| Complaint Roles / Complaint Authorization mapping after entitlement | ECMP Business Module | Own mapping after ADR-014 Entitlement Gate |
| Complaint business authorization decisions | ECMP Business Module | Own |

### Hard rules

1. Enterprise Platform is the Source of Truth for enterprise identity.
2. **Role-Permission Matrix SoT = Core Platform (ADR-008).** Enterprise Platform does **not** own the Role-Permission Matrix SoT. ECMP must not replace Core Platform as SoT.
3. ECMP stores only what it needs for module operation and audit correlation.
4. ECMP must never create, update, delete, merge, or reassign enterprise identity as enterprise truth.
5. ECMP must never promote a local attribute (including email) to an enterprise identity key.
6. Local copies of enterprise attributes are **projections**, not masters. When enterprise identity and local projection disagree, enterprise identity wins for enterprise-owned fields.
7. Referential anchoring for ECMP relationships remains local `users.id`; `external_user_id` is the unique alternate key (ADR-014).

### PII projection statement

Local copies of enterprise-supplied attributes such as `display_name` and `email` are **PII projections**, not ECMP-owned master data.

- Retention, minimization, and deletion/correction of projected PII MUST follow enterprise privacy policy and MUST NOT invent a competing identity SoR (ADR-002 principle applied to identity attributes).
- ECMP may retain projections only as needed for module operation, readable audit trails, and correspondence within complaint workflows.
- When enterprise identity and local projection disagree, enterprise identity wins for enterprise-owned fields (Hard rule 6).
- Detailed retention schedules and lawful-basis mapping remain a follow-up Security / Privacy documentation task after Board Accept; this ADR establishes the ownership and projection posture only.

## 5. Required Identity Claims

The following claims are **required** for ECMP to accept an identity under Mode B:

| Claim | Cardinality | Purpose |
|---|---|---|
| `external_user_id` | Exactly one | Canonical enterprise identity key |
| `display_name` | Exactly one | Human-readable display for UI and audit readability |
| `email` | Exactly one | Contact / correspondence attribute (not an identity key) |
| `organization_id` | Exactly one | Enterprise organization reference used for scoping |
| `branch_id` | Exactly one | Enterprise branch reference used for scoping |
| `department_id` | Exactly one | Enterprise department reference used for scoping |
| `employment_status` | Exactly one | Employment / active-status signal used for access and lifecycle |

Absence of any required claim is a contract failure and must result in access denial (see §10).

**Hierarchy assumption restated:** contract v1.0 requires the full three-level reference set (`organization_id`, `branch_id`, `department_id`) with cardinality Exactly one each. There is **no** partial-hierarchy / N/A substitution rule in v1.0.

No additional claim is required by this ADR unless a later version of this contract marks it required.

Note: ADR-012 uses a different historical claim vocabulary (for example `sub`, `roles[]`, `orgUnitId`). That vocabulary is not the SoT for Mode B enterprise identity claims. Any conveyance mapping from ADR-012-era models to this contract requires Board-disposed relationship reconciliation and a follow-up binding decision — it must not silently redefine this table.

## 6. Optional Claims

Optional claims may be supplied by the Enterprise Platform to improve UX, audit richness, or future authorization inputs.

Examples of optional claims (non-exhaustive):

| Claim | Purpose |
|---|---|
| `preferred_language` | Localization preference |
| `job_title` | Display / reporting context |
| `phone` | Contact enrichment |
| `enterprise_role_codes` | Informational enterprise role labels (never auto-mapped to ECMP permissions) |
| `manager_external_user_id` | Organizational context |
| `identity_contract_version` | Explicit contract version assertion when conveyed with the identity |

### Rules for optional claims

- Optional claims may be present or absent without denying access, provided all required claims are present and valid.
- **Unknown claims are ignored unless explicitly marked as required** in the active contract version.
- Optional claims must not be treated as identity keys.
- Optional enterprise role labels do not grant ECMP permissions. After entitlement (ADR-014), authorization remains governed by Complaint Roles mapping under **Role-Permission Matrix SoT = Core Platform (ADR-008)**.

## 7. Claim Semantics

### `external_user_id`

- The **only** enterprise identity key used by ECMP.
- Must be immutable for the lifetime of the subject.
- Must be opaque to ECMP business logic (no parsing of internal structure).
- Must be unique within the enterprise identity domain consumed by ECMP.
- Must be enterprise-owned.
- Must be non-reassignable to a different person.
- Email, username, employee number, or display name must never substitute for `external_user_id`.

### `display_name`

- Human-readable name for presentation and readable audit trails.
- May change over time.
- Must not be used as a join key, unique constraint for identity, or authorization key.

### `email`

- Contact attribute only.
- May change over time.
- Must never be used as an identity key.
- Uniqueness of email, if enforced anywhere, is an Enterprise Platform concern — not an ECMP identity-key rule.

### `organization_id`, `branch_id`, `department_id`

- Opaque enterprise references to organization structure owned by the Enterprise Platform.
- ECMP stores references only and must not become master of organizational hierarchy (ADR-014).
- Semantics of hierarchy resolution remain an Enterprise Platform / Organization Synchronization concern; this contract only requires the identifiers to be present and stable enough for reference.
- **Project assumption:** all three claims are required together (Exactly one each). Partial hierarchy is out of scope for contract v1.0 (see Assumptions).

### `employment_status`

- Enterprise-supplied status signal used by ECMP for fail-closed access and local profile lifecycle.
- At minimum, ECMP must be able to distinguish states that mean **allowed to hold an active ECMP profile** versus **must not hold active ECMP access**.
- Exact enumerated value set may be refined by a follow-up ADR without changing the claim name, provided compatibility rules in §11 are respected.

### General semantic rules

- Claim names in this ADR are the canonical contract names for ECMP.
- Conveyance mechanisms may use different wire names only if a governed mapping to these canonical names is defined in a later protocol/binding ADR.
- Claims express **identity facts**, not ECMP permissions.
- Claims do not by themselves grant module access; Enterprise Entitlement Gate rules from ADR-014 remain in force.

## 8. Identity Versioning

1. The Enterprise Identity Contract has its own version identity. The active contract version governed by this document revision is **1.0**.
2. **The identity contract is versioned independently from implementation** — application release versions, deployment modes, and protocol bindings must not silently redefine the contract.
3. Document revision of this ADR (for example 1.3) may clarify ownership/relationship language without changing contract version **1.0**, provided required claims, key rules, and fail-closed behavior are unchanged.
4. Contract changes are classified as:
   - **Compatible** — add optional claims; clarify semantics without changing required meaning; add non-breaking enumerated values with documented defaults/ignore behavior.
   - **Breaking** — add/remove/rename required claims; change required claim meaning; change identity-key rules; change fail-closed behavior.
5. Breaking changes require a new contract major version and an explicit Architecture Board decision.
6. ECMP must know which contract version it implements and must reject identities that cannot be interpreted under a supported contract version when version negotiation is introduced by a follow-up ADR.
7. Until explicit version negotiation exists, ECMP treats contract **v1.0** as the sole supported Enterprise Identity Contract for Mode B.

## 9. Identity Lifecycle

The contract defines the identity lifecycle events ECMP must be prepared to honor when consuming enterprise identity. Transport and scheduling are out of scope.

| Lifecycle event | Meaning for ECMP | ADR-014 alignment |
|---|---|---|
| **Introduce** | An entitled enterprise identity is first presented to ECMP; ECMP may create a local module profile keyed by `external_user_id`. | Create |
| **Update** | Enterprise-owned attributes change; ECMP updates local projections of those attributes. ECMP does not invent competing values. | Update |
| **Suspend / Deactivate** | Enterprise status or entitlement indicates the subject must not have active ECMP access; ECMP deactivates local access/profile use. | Deactivate |
| **Reactivate** | Enterprise status and entitlement again permit access; ECMP may reactivate a previously deactivated local profile for the same `external_user_id`. | Reactivate |
| **Reconcile** | ECMP compares local projections to enterprise identity and corrects drift for enterprise-owned fields. | Periodic Reconciliation |
| **Terminate key** | `external_user_id` is never reused for a different person. Historical audit references remain valid; new access for a new person requires a new `external_user_id`. | Consumed by ADR-014; not redefined there |

### Lifecycle hard rules

- Lifecycle operations never authorize ECMP to modify enterprise identity at the source.
- Create/update of local profiles is always subordinate to enterprise identity + entitlement checks (ADR-014).
- Enterprise authentication success alone is never sufficient for ECMP access (ADR-014 Entitlement Gate).

## 10. Fail-Closed Rules

ECMP shall deny access under Mode B when any of the following is true:

1. Required claim is missing.
2. Required claim is present but empty / null where a value is required.
3. `external_user_id` is missing, empty, or not usable as the identity key.
4. `employment_status` indicates the subject is not permitted active access.
5. Enterprise entitlement for the Complaint module is absent (ADR-014 Entitlement Gate).
6. Identity cannot be interpreted under a supported identity contract version (when version enforcement is active).

### Explicit non-behaviors

- ECMP must not invent default values for missing required claims.
- ECMP must not infer `external_user_id` from email or other attributes.
- ECMP must not grant a default ECMP role solely because identity was partially present.
- **Unknown claims are ignored** — they do not cause denial by themselves, and they do not become implicitly required.

Fail closed means: **no access**, not “best effort with incomplete identity.”

Entitlement **representation** remains a follow-up decision complementary to ADR-014; this ADR does not redefine the gate, only requires denial when entitlement is absent.

## 11. Compatibility Rules

1. Adding a new **optional** claim is backward compatible.
2. Promoting an optional claim to **required** is a breaking contract change.
3. Removing a required claim is a breaking contract change.
4. Renaming a claim is a breaking contract change unless a dual-read compatibility window is explicitly approved and time-bounded by Architecture Board.
5. Changing the meaning of `external_user_id` (mutability, reassignment, key substitution) is always breaking and strongly discouraged.
6. ECMP implementations consuming contract v1.0 must ignore unknown claims.
7. ECMP must not require claims that are not listed as required in the active contract version.
8. Local profile schema may store additional ECMP-owned fields; those fields are outside this contract and must not be presented as enterprise identity claims.
9. Mode A (Standalone) per ADR-014 is outside the runtime enforcement of this enterprise contract, but must not contradict these ownership rules when Mode B is later enabled.
10. Mode B combined with local credential authentication paths is invalid (ADR-014 Local Auth Prohibition / Mode matrix).

## 12. Trust Boundary

```
Enterprise Platform Trust Domain
  - Owns identity source of truth
  - Issues / presents identity claims to modules
  - Owns organization structure referenced by identity
        |
        |  Identity Contract boundary (this ADR)
        v
ECMP Trust Domain
  - Authenticates trust in the enterprise presentation mechanism (protocol ADR — out of scope here)
  - Validates contract completeness (required claims, fail-closed rules)
  - Applies Enterprise Entitlement Gate (ADR-014)
  - Maps accepted identity to Complaint Roles / Complaint Authorization after the gate
  - Consumes Role-Permission Matrix SoT from Core Platform (ADR-008)
  - Owns complaint domain decisions and local profile data
```

### Trust statements

- ECMP trusts the Enterprise Platform as the authority for enterprise identity claims at the contract boundary.
- ECMP does not trust clients, browsers, or downstream modules to assert enterprise identity independently of the Enterprise Platform.
- Crossing the trust boundary does not transfer identity ownership to ECMP.
- Audit of enterprise identity changes remains an Enterprise Platform responsibility; ECMP audits module actions taken under a consumed identity.

### Shared audit correlation (deferred)

End-to-end “who did what” across Enterprise Identity Audit and ECMP module audit requires a **shared correlation identifier** (and clock discipline).

This ADR **explicitly defers** the choice of correlation identifier, propagation mechanism, and operational join procedure to a follow-up Security / Operations decision (or protocol / binding ADR where conveyance already carries a suitable correlation claim).

Until that decision exists:

- ECMP MUST continue to denormalize actor display information at write time for readable module audit (existing `actor_name`-style practice is compatible).
- ECMP MUST retain `external_user_id` (and local `users.id`) on module audit records where subject correlation is required.
- Teams MUST NOT invent an informal second identity key for cross-system joins.

## 13. Responsibilities

| Party | Responsibilities |
|---|---|
| **Enterprise Platform** | Own and supply identity; preserve `external_user_id` immutability and non-reassignment; supply required claims; version enterprise identity capabilities; notify or otherwise enable lifecycle/reconciliation signals as decided in follow-up ADRs. |
| **ECMP Business Module** | Consume identity only; enforce required-claim presence; ignore unknown non-required claims; deny on contract failure; maintain local profiles as projections + module-owned data; never modify enterprise identity source data; perform Complaint Roles mapping only after ADR-014 Entitlement Gate. |
| **Core Platform** | Own and enforce Role-Permission Matrix SoT (ADR-008). |
| **Architecture Board** | Approve contract versions; adjudicate breaking changes; resolve conflicts with ADR-007 / ADR-012 / ADR-014. |
| **Security Architect** | Review contract changes that affect access denial, identity-key rules, or trust boundary; ensure fail-closed posture is preserved. |
| **Solution Architect** | Keep Solution Architecture and dependent ADRs aligned to the active contract version; keep ADR-014 pointer to this SoT current. |
| **Domain teams (ECMF and others)** | Use `external_user_id` for correlation; do not introduce competing identity keys; do not treat optional claims as authorization. |

## 14. Consequences

### Positive

- Clear, testable interface between Enterprise Platform and ECMP for identity.
- Prevents email-as-key and other unsafe identity shortcuts.
- Enables enterprise identity evolution without forcing silent ECMP business-logic churn.
- Makes fail-closed behavior explicit and reviewable.
- Closes the ADR-014 governance gap on identity-contract ownership and versioning.
- Separates identity interface decisions from protocol/implementation decisions.
- Aligns ownership language with ADR-008 and ADR-014 (no duplicated Role-Permission SoT).

### Negative / Trade-offs

- Enterprise Platform must reliably supply the required claim set.
- ECMP access availability depends on enterprise identity completeness and correctness.
- Organization reference claims create a hard dependency on enterprise org identifiers (and on Organization Synchronization as recorded in ADR-014); contract v1.0 assumes full three-level hierarchy with no partial-org rule.
- Teams must resist embedding protocol assumptions into this contract.
- Existing claim models in earlier auth ADRs must be reconciled (see §17 and ADR Relationship).
- Shared audit correlation across Enterprise and ECMP audit stores remains deferred.
- Local `display_name` / `email` projections are PII and require retention discipline after Accept.

## 15. Risks

| ID | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| R-01 | Producers omit required claims in some environments | High — widespread access denial or unsafe bypass pressure | Medium | Fail closed; contract conformance checks in architecture review and integration verification |
| R-02 | Teams continue using email as a de-facto key | High — identity collisions / wrong-subject access | Medium | Explicit prohibition in §7; review of data models and join paths |
| R-03 | Protocol ADRs redefine claims without updating this contract | High — dual sources of truth | Medium | This ADR is SoT for claim contract; protocol ADRs must map to it |
| R-04 | Optional claims silently become treated as required in code | Medium — brittle integrations | Medium | Compatibility rules + code review against required claim list |
| R-05 | Unreconciled overlap with ADR-007 / ADR-012 claim models | High — conflicting implementation targets | High until Board disposition | Identical Relationship proposals in ADR-014 + this ADR; follow-up binding ADR |
| R-06 | Local projection drift if reconciliation is never implemented | Medium — stale org/status decisions | Medium | Lifecycle §9 requires reconcile capability; scheduling left to follow-up |
| R-07 | ADR-014 retains a competing claim list | High — dual SoT | Low after PHASE-2 package | ADR-014 points to this ADR as claim SoT |

## 16. Alternatives Considered

### Alternative A — Leave identity attributes informal under ADR-014 only

- Pros: fewer documents; faster short-term progress.
- Cons: no versioned contract; unknown-claim behavior undefined; ownership of the interface remains ambiguous (the gap already found in ADR-014 review).
- Verdict: **Rejected.**

### Alternative B — Define identity contract inside a protocol/binding ADR

- Pros: one document for interface + conveyance.
- Cons: couples durable business identity rules to replaceable conveyance technology; forces premature protocol choice into the identity SoT.
- Verdict: **Rejected** for the identity SoT. Protocol binding may reference this contract later.

### Alternative C — ECMP defines and owns the identity schema, Enterprise Platform adapts

- Pros: optimizes for ECMP delivery speed.
- Cons: inverts enterprise ownership; recreates module-specific identity fragmentation across future business modules.
- Verdict: **Rejected.**

### Alternative D — Canonical Enterprise Identity Contract owned at the platform boundary (this ADR)

- Pros: durable ownership split; protocol-agnostic; versioned independently; fail-closed and compatibility rules explicit.
- Cons: requires discipline to keep protocol ADRs subordinate; requires claim reconciliation with earlier auth ADRs.
- Verdict: **Accepted.**

## 17. Follow-up ADRs

The following topics are explicitly **out of scope** for ADR-015 and require follow-up decisions:

1. **Identity conveyance / protocol binding** — how identity claims are presented to ECMP (without changing claim ownership or semantics defined here), including audience/issuer isolation. OD-FE-002 remains downstream and is **not** closed by this ADR.
2. **Enterprise Entitlement representation** — how module entitlement is expressed and evaluated relative to identity (complements ADR-014 gate; does not redefine the gate).
3. **Organization Synchronization** — how organization/branch/department references remain resolvable for authorization (dependency already recorded in ADR-014); includes foundation org-model gap closure planning.
4. **Identity reconciliation schedule and authority path** — operational cadence for §9 Reconcile.
5. **`employment_status` enumeration normative set** — exact allowed values and mapping to activate/deactivate.
6. **ADR relationship reconciliation** — Architecture Board disposition of ADR-007 and ADR-012 relative to Mode B / ADR-014 / this contract (see Relationship table proposals; no self-supersession).
7. **Contract version negotiation** — optional runtime assertion of `identity_contract_version` and multi-version support windows.
8. **Shared audit correlation identifier** — deferred per Trust Boundary section; do not invent informal join keys.
9. **PII projection retention schedule** — detailed privacy retention mapping after Board Accept.

### Non-goals (restated)

This ADR does not define authentication protocols, credential formats, validation mechanics, directory products, API endpoint design, frontend stack, or deployment topology.

## ADR Relationship

| ADR | Relationship |
|---|---|
| ADR-002 | **Consistent** — ECMP is not SoR for data it does not own; identity follows the same principle. |
| ADR-008 | **Complementary / Constrains** — enterprise identity ≠ Role-Permission Matrix SoT. Role-Permission Matrix SoT remains Core Platform. |
| ADR-014 | **Complementary** — ADR-014 decides AuthN ownership, Business Module boundary, and Entitlement Gate; this ADR is the Identity Contract SoT those decisions require. Submit as one package. |
| ADR-007 | **Proposed disposition for Board (not executed):** Mode A–scoped applicability. Slice/target auth model remains valid for Mode A; under Mode B, AuthN ownership follows ADR-014 and identity claims follow this ADR. Status remains **Relationship Pending** until Board confirms. |
| ADR-012 | **Proposed disposition for Board (not executed):** Mode A baseline IdP / Mode B subsumption candidate. Status remains **Relationship Pending** until Board confirms. See **ADR-012 relationship disclosure** below. |
| ADR-013 | **Orthogonal** — frontend stack; remain active (BR-007). Not superseded by this ADR. |

No supersession is declared by this ADR.

### ADR-012 relationship disclosure (editorial — no preference)

Architecture Board disposition of ADR-012 relative to this package affects **authorization flow semantics**, not only claim vocabulary alignment.

Proposed disposition options and architectural consequences (disclosure only; this ADR does **not** recommend an option):

| Proposed Board option | Consequence for authorization flow semantics | Consequence for claim vocabulary |
|---|---|---|
| **Mode A–only** | Mode B authorization flow is governed by Enterprise Platform AuthN → this Identity Contract (ADR-015) → ADR-014 Entitlement Gate → Complaint Roles mapping → Core Platform Role-Permission SoT (ADR-008). ADR-012 target AuthN flow does not authorize Mode B ECMP access. | ADR-012 historical claims (for example `sub`, `roles[]`, `orgUnitId`) do not become Mode B identity/authorization vocabulary. This contract remains the Mode B claim SoT. |
| **Subsumed as Enterprise Platform IdP implementation detail** | An IdP chosen under ADR-012 may implement Enterprise Platform authentication, but Mode B authorization flow still requires the ADR-014 Entitlement Gate and ADR-008 Role-Permission enforcement after identity acceptance under this contract. Subsumption does not collapse AuthN success into ECMP authorization. | Wire/token fields from ADR-012-era models require governed mapping to this contract; they must not silently redefine Mode B authorization inputs. |
| **Other (Board-defined)** | Any other disposition must still state how Mode B authorization flow relates to the ADR-014 Entitlement Gate, this Identity Contract, and ADR-008 Role-Permission SoT. | Claim reconciliation remains mandatory if historical vocabularies remain in use. |

This disclosure does not execute a relationship change and does not supersede ADR-012.

## Compliance / Follow-up Actions

- [ ] Architecture Board review of **ADR-014 + ADR-015 package (PROGRAM-ADR-004)** → move Status to Accepted only by Board decision
- [ ] Confirm ADR-014 references this ADR as the canonical Enterprise Identity Contract SoT (preserve after acceptance)
- [ ] Board disposition of ADR-007 / ADR-012 relationships (proposals above — identical to ADR-014)
- [ ] After Accepted: update Solution Architecture identity section to cite ADR-015
- [ ] After Accepted: sync Security standards references as needed (mapping only; no protocol invention here)
- [ ] After Accepted: sync FE-ARCH LAP-01..03 / OD-FE-008 Pending Upstream exit criteria
- [ ] Communicate to impacted teams — Core Platform, ECMF, Security, Integration, Enterprise Platform owners

### Document history

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-29 | Initial Proposed — Identity Contract SoT |
| 1.1 | 2026-07-30 | PROGRAM-ENTERPRISE-001 PHASE-2 coordinated revision with ADR-014: ownership language (ADR-008), lifecycle alignment, claim conflict note vs ADR-012, identical relationship proposals; contract version remains 1.0 |
| 1.2 | 2026-07-30 | PROGRAM-ENTERPRISE-001 FINAL EDITORIAL PACKAGE: ADR-012 disposition disclosure (AuthZ flow semantics), terminology table (identical to ADR-014), Board Resolution traceability; contract version remains 1.0 |
| 1.3 | 2026-07-30 | PROGRAM-ADR-004 Board Readiness: three-level org hierarchy assumption explicit, PII projection statement, shared audit correlation deferred, terminology aligned with ADR-014 v1.4; disposition **Revised — Pending Board Review**; remains Proposed; contract version remains 1.0 |
