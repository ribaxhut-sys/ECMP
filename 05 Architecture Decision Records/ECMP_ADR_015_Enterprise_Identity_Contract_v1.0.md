# ECMP_ADR_015_Enterprise_Identity_Contract_v1.0

| Field | Value |
|---|---|
| ID | ADR-015 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Security Architect / Architecture Board |
| Approver | Architecture Board |
| Status | 🟡 Proposed |
| Last Review | 2026-07-29 |
| Next Review | 2027-01-29 |

- ADR Status: Proposed
- Date: 2026-07-29
- Decision Owners: Solution Architect, Security Architect
- Related Domains: Core Platform, ECMF (Complaint Management), Administration, Notification, Dashboard & Analytics, KPI & Performance
- Related ADRs: ADR-002, ADR-007, ADR-008, ADR-012, ADR-014

## 1. Context

ADR-014 establishes that ECMP operates as an Enterprise Business Module and that the Enterprise Platform owns Enterprise Identity. ECMP consumes identity; it does not provide it.

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

This ADR is the Source of Truth for the Enterprise Identity Contract consumed by ECMP under Enterprise Mode. Protocol selection, credential binding, and runtime transport remain out of scope and require separate decisions.

## 4. Identity Ownership

| Concern | Owner | ECMP Role |
|---|---|---|
| Enterprise person / subject identity | Enterprise Platform | Consume only |
| Enterprise identity key (`external_user_id`) | Enterprise Platform | Reference only |
| Display and contact attributes supplied as claims | Enterprise Platform | Consume / cache locally as non-authoritative copies |
| Organization / branch / department identity references | Enterprise Platform | Reference only |
| Employment / entitlement-relevant status signals in the identity payload | Enterprise Platform | Consume for access and lifecycle decisions |
| ECMP local profile (preferences, last access, local module status) | ECMP | Own |
| ECMP roles and permissions | ECMP (per ADR-008) | Own |
| Complaint business authorization | ECMP | Own |

### Hard rules

1. Enterprise Platform is the Source of Truth for enterprise identity.
2. ECMP stores only what it needs for module operation and audit correlation.
3. ECMP must never create, update, delete, merge, or reassign enterprise identity as enterprise truth.
4. ECMP must never promote a local attribute (including email) to an enterprise identity key.
5. Local copies of enterprise attributes are **projections**, not masters. When enterprise identity and local projection disagree, enterprise identity wins for enterprise-owned fields.

## 5. Required Identity Claims

The following claims are **required** for ECMP to accept an identity under Enterprise Mode:

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

No additional claim is required by this ADR unless a later version of this contract marks it required.

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
- Optional enterprise role labels do not grant ECMP permissions. ECMP authorization remains governed by ADR-008 after entitlement and identity acceptance.

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

1. The Enterprise Identity Contract has its own version identity (this ADR starts at contract version **1.0**, aligned with ADR version 1.0).
2. **The identity contract is versioned independently from implementation** — application release versions, deployment modes, and protocol bindings must not silently redefine the contract.
3. Contract changes are classified as:
   - **Compatible** — add optional claims; clarify semantics without changing required meaning; add non-breaking enumerated values with documented defaults/ignore behavior.
   - **Breaking** — add/remove/rename required claims; change required claim meaning; change identity-key rules; change fail-closed behavior.
4. Breaking changes require a new contract major version and an explicit Architecture Board decision.
5. ECMP must know which contract version it implements and must reject identities that cannot be interpreted under a supported contract version when version negotiation is introduced by a follow-up ADR.
6. Until explicit version negotiation exists, ECMP treats this ADR v1.0 as the sole supported Enterprise Identity Contract for Enterprise Mode.

## 9. Identity Lifecycle

The contract defines the identity lifecycle events ECMP must be prepared to honor when consuming enterprise identity. Transport and scheduling are out of scope.

| Lifecycle event | Meaning for ECMP |
|---|---|
| **Introduce** | An entitled enterprise identity is first presented to ECMP; ECMP may create a local module profile keyed by `external_user_id`. |
| **Update** | Enterprise-owned attributes change; ECMP updates local projections of those attributes. ECMP does not invent competing values. |
| **Suspend / Deactivate** | Enterprise status or entitlement indicates the subject must not have active ECMP access; ECMP deactivates local access/profile use. |
| **Reactivate** | Enterprise status and entitlement again permit access; ECMP may reactivate a previously deactivated local profile for the same `external_user_id`. |
| **Reconcile** | ECMP compares local projections to enterprise identity and corrects drift for enterprise-owned fields. |
| **Terminate key** | `external_user_id` is never reused for a different person. Historical audit references remain valid; new access for a new person requires a new `external_user_id`. |

### Lifecycle hard rules

- Lifecycle operations never authorize ECMP to modify enterprise identity at the source.
- Create/update of local profiles is always subordinate to enterprise identity + entitlement checks (ADR-014).
- Enterprise authentication success alone is never sufficient for ECMP access (ADR-014 Entitlement Gate).

## 10. Fail-Closed Rules

ECMP shall deny access under Enterprise Mode when any of the following is true:

1. Required claim is missing.
2. Required claim is present but empty / null where a value is required.
3. `external_user_id` is missing, empty, or not usable as the identity key.
4. `employment_status` indicates the subject is not permitted active access.
5. Enterprise entitlement for the Complaint module is absent (ADR-014).
6. Identity cannot be interpreted under a supported identity contract version (when version enforcement is active).

### Explicit non-behaviors

- ECMP must not invent default values for missing required claims.
- ECMP must not infer `external_user_id` from email or other attributes.
- ECMP must not grant a default ECMP role solely because identity was partially present.
- **Unknown claims are ignored** — they do not cause denial by themselves, and they do not become implicitly required.

Fail closed means: **no access**, not “best effort with incomplete identity.”

## 11. Compatibility Rules

1. Adding a new **optional** claim is backward compatible.
2. Promoting an optional claim to **required** is a breaking contract change.
3. Removing a required claim is a breaking contract change.
4. Renaming a claim is a breaking contract change unless a dual-read compatibility window is explicitly approved and time-bounded by Architecture Board.
5. Changing the meaning of `external_user_id` (mutability, reassignment, key substitution) is always breaking and strongly discouraged.
6. ECMP implementations consuming contract v1.0 must ignore unknown claims.
7. ECMP must not require claims that are not listed as required in the active contract version.
8. Local profile schema may store additional ECMP-owned fields; those fields are outside this contract and must not be presented as enterprise identity claims.
9. Standalone Mode (ADR-014 Mode A) is outside the runtime enforcement of this enterprise contract, but must not contradict these ownership rules when Enterprise Mode is later enabled.

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
  - Applies Enterprise Entitlement Gate
  - Maps accepted identity to ECMP authorization (ADR-008)
  - Owns complaint domain decisions and local profile data
```

### Trust statements

- ECMP trusts the Enterprise Platform as the authority for enterprise identity claims at the contract boundary.
- ECMP does not trust clients, browsers, or downstream modules to assert enterprise identity independently of the Enterprise Platform.
- Crossing the trust boundary does not transfer identity ownership to ECMP.
- Audit of enterprise identity changes remains an Enterprise Platform responsibility; ECMP audits module actions taken under a consumed identity.

## 13. Responsibilities

| Party | Responsibilities |
|---|---|
| **Enterprise Platform** | Own and supply identity; preserve `external_user_id` immutability and non-reassignment; supply required claims; version enterprise identity capabilities; notify or otherwise enable lifecycle/reconciliation signals as decided in follow-up ADRs. |
| **ECMP** | Consume identity only; enforce required-claim presence; ignore unknown non-required claims; deny on contract failure; maintain local profiles as projections + module-owned data; never modify enterprise identity source data. |
| **Architecture Board** | Approve contract versions; adjudicate breaking changes; resolve conflicts with ADR-007 / ADR-012 / ADR-014. |
| **Security Architect** | Review contract changes that affect access denial, identity-key rules, or trust boundary; ensure fail-closed posture is preserved. |
| **Solution Architect** | Keep Solution Architecture and dependent ADRs aligned to the active contract version. |
| **Domain teams (ECMF and others)** | Use `external_user_id` for correlation; do not introduce competing identity keys; do not treat optional claims as authorization. |

## 14. Consequences

### Positive

- Clear, testable interface between Enterprise Platform and ECMP for identity.
- Prevents email-as-key and other unsafe identity shortcuts.
- Enables enterprise identity evolution without forcing silent ECMP business-logic churn.
- Makes fail-closed behavior explicit and reviewable.
- Closes the ADR-014 governance gap on identity-contract ownership and versioning.
- Separates identity interface decisions from protocol/implementation decisions.

### Negative / Trade-offs

- Enterprise Platform must reliably supply the required claim set.
- ECMP access availability depends on enterprise identity completeness and correctness.
- Organization reference claims create a hard dependency on enterprise org identifiers (and on Organization Synchronization as recorded in ADR-014).
- Teams must resist embedding protocol assumptions into this contract.
- Existing claim models in earlier auth ADRs must be reconciled (see §17 and Conflicts in the delivery note).

## 15. Risks

| ID | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| R-01 | Producers omit required claims in some environments | High — widespread access denial or unsafe bypass pressure | Medium | Fail closed; contract conformance checks in architecture review and integration verification |
| R-02 | Teams continue using email as a de-facto key | High — identity collisions / wrong-subject access | Medium | Explicit prohibition in §7; review of data models and join paths |
| R-03 | Protocol ADRs redefine claims without updating this contract | High — dual sources of truth | Medium | This ADR is SoT for claim contract; protocol ADRs must map to it |
| R-04 | Optional claims silently become treated as required in code | Medium — brittle integrations | Medium | Compatibility rules + code review against required claim list |
| R-05 | Unreconciled overlap with ADR-007 / ADR-012 claim models | High — conflicting implementation targets | High until follow-up ADR | Architecture Board reconciliation (follow-up ADR) |
| R-06 | Local projection drift if reconciliation is never implemented | Medium — stale org/status decisions | Medium | Lifecycle §9 requires reconcile capability; scheduling left to follow-up |

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

1. **Identity conveyance / protocol binding** — how identity claims are presented to ECMP (without changing claim ownership or semantics defined here).
2. **Enterprise Entitlement representation** — how module entitlement is expressed and evaluated relative to identity (complements ADR-014 gate).
3. **Organization Synchronization** — how organization/branch/department references remain resolvable for authorization (dependency already recorded in ADR-014).
4. **Identity reconciliation schedule and authority path** — operational cadence for §9 Reconcile.
5. **`employment_status` enumeration normative set** — exact allowed values and mapping to activate/deactivate.
6. **ADR relationship reconciliation** — explicit Architecture Board disposition of ADR-007 and ADR-012 relative to Enterprise Mode / ADR-014 / this contract (supersede, subsume, or Mode A–only applicability).
7. **Contract version negotiation** — optional runtime assertion of `identity_contract_version` and multi-version support windows.

### Non-goals (restated)

This ADR does not define authentication protocols, credential formats, validation mechanics, directory products, or API endpoint design.

## ADR Relationship

| ADR | Relationship |
|---|---|
| ADR-002 | Consistent — ECMP is not SoR for data it does not own; identity follows the same principle. |
| ADR-008 | Complementary — enterprise identity ≠ ECMP Role-Permission SoT. |
| ADR-014 | Complementary / specializing — ADR-014 decides ownership and module boundary; this ADR defines the identity interface contract those decisions require. |
| ADR-007 | Relationship Pending — slice/target auth model predates Enterprise Identity Contract; must be reconciled for Enterprise Mode. |
| ADR-012 | Relationship Pending — target authentication architecture predates Enterprise Mode identity ownership; must be reconciled so it does not redefine this contract. |

No supersession is declared by this ADR.

## Compliance / Follow-up Actions

- [ ] Architecture Board review → move Status to Accepted
- [ ] On acceptance, update ADR-014 to reference ADR-015 as the canonical Enterprise Identity Contract (replace inline “Minimum Identity Payload” as SoT pointer)
- [ ] Resolve Relationship Pending for ADR-007 and ADR-012 under Enterprise Mode
- [ ] Update Solution Architecture identity section to cite ADR-015
- [ ] Communicate to impacted teams — Core Platform, ECMF, Security, Integration, Enterprise Platform owners
