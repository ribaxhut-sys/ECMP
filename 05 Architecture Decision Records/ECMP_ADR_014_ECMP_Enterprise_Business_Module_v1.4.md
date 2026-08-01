# ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4

| Field | Value |
|---|---|
| ID | ADR-014 |
| Version | 1.4 |
| Owner | Solution Architect |
| Reviewer | Security Architect / Architecture Board |
| Approver | Architecture Board |
| Status | 🟢 Approved (Accepted with Conditions — PROGRAM-BOARD-004) |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |

- ADR Status: **Accepted with Conditions** (PROGRAM-BOARD-004 **BR-009**)
- Board Disposition: **Accepted with Conditions** — conditions **C-1**, **C-3**, **C-7** apply. Mode B / Batch-2 / Enterprise customer remain **CLOSED** (C-7). Resolution: `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`
- Prior dispositions (historical): PROGRAM-ADR-002 **BR-005** Needs Revision; PROGRAM-ADR-004 Revised — Pending Board Review — superseded as *active* disposition by BR-009
- Date: 2026-07-30
- Decision Owners: Solution Architect, Security Architect
- Related Domains: Core Platform, ECMF (Complaint Management), Notification, Dashboard & Analytics, KPI & Performance
- Related ADRs: ADR-002, ADR-007, ADR-008, ADR-012, ADR-015
- Package: Accepted with ADR-015 as coordinated package (PROGRAM-BOARD-004). Prior authoring: PROGRAM-ADR-004 / PROGRAM-ENTERPRISE-001
- Governance posture: **Accepted Architecture — Implementation Deferred** (Mode B Closed)

## Terminology

Authoritative terms for this ADR package (identical in ADR-015). These terms must not be used interchangeably.

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

## Context

ECMP was originally designed as a standalone application with its own authentication, user management, authorization, and complaint management.

The enterprise roadmap has changed.

ECMP will become one **Business Module** within a larger **Enterprise Platform**.

The Enterprise Platform will provide shared capabilities for multiple business modules including:

- Portal
- Authentication
- Single Sign-On (SSO)
- User Directory
- Organization Structure
- Navigation
- **Enterprise Global Notification** (platform cross-module notification capability)
- Session Management

ECMP will focus on Complaint Management and **ECMP Business Notification** (module-scoped / complaint-domain notification). Enterprise Global Notification and ECMP Business Notification are **not** interchangeable; see Terminology and Architecture Boundary.

## Problem Statement

If ECMP continues to own enterprise authentication, several issues arise:

- Multiple login pages
- Duplicate user databases
- Duplicate password management
- Separate password reset processes
- Inconsistent logout behavior
- Fragmented identity auditing
- Difficult enterprise integration

These issues increase operational complexity as additional enterprise modules are introduced.

## Decision Drivers

- Eliminate duplicate enterprise identity stores across business modules.
- Preserve clear separation of Authentication and Authorization concerns.
- Preserve Accepted Role-Permission Matrix SoT ownership (ADR-008 — Core Platform).
- Enable Enterprise Mode without making every authenticated enterprise user an ECMP user by default.
- Keep complaint business rules mode-independent.
- Remain protocol-agnostic at the module-boundary layer (protocol is a follow-up decision).
- Align with ADR-002 non-SoR principle for data ECMP does not own.

## Options Considered

### Option A — ECMP continues to own authentication (status quo)

- Pros: No external dependency; fastest short-term delivery for standalone deployments.
- Cons: Duplicate identity/password lifecycle; fragmented audit; blocks multi-module enterprise integration.
- Verdict: **Rejected** for Enterprise Mode. Remains the basis of Mode A (Standalone) only.

### Option B — Enterprise Platform owns Authentication and Enterprise Identity; ECMP is a Business Module (chosen)

- Pros: Single login experience; centralized identity; clear AuthN/AuthZ split; aligns with ADR-002; preserves ADR-008 SoT when AuthZ language is qualified.
- Cons: Dependency on Enterprise Identity availability; requires Entitlement Gate, identity contract (ADR-015), and organization synchronization.
- Verdict: **Accepted.**

### Option C — Federated identity with ECMP retaining a local IdP fallback under Enterprise Mode

- Pros: Operational hedge if Enterprise IdP is unavailable.
- Cons: Recreates dual credential surfaces; SSO-bypass risk; contradicts Enterprise Mode Local Auth Prohibition; dual audit and dual password paths.
- Verdict: **Rejected** for Mode B. Mode A remains the deliberate standalone hedge, not an Enterprise Mode fallback IdP.

## Decision

Authentication ownership shall be transferred to the Enterprise Platform under **Mode B (Enterprise)**.

ECMP shall no longer act as an Identity Provider under Mode B.

ECMP shall operate as an Enterprise **Business Module**.

Authentication and Authorization shall remain separate responsibilities.

### Decision Summary

- **Enterprise Platform** is the owner of Authentication and Enterprise Identity under Mode B.
- **ECMP** is the owner of Complaint Management.
- Authentication is external under Mode B.
- **Complaint Authorization** and **Complaint Roles mapping** remain inside ECMP **after** the Enterprise Entitlement Gate.
- **Role-Permission Matrix SoT = Core Platform (ADR-008).** Enterprise Platform does **not** own the Role-Permission Matrix SoT. ECMP must not replace Core Platform as SoT.
- Required identity claims and claim semantics are defined by **ADR-015** (Identity Contract SoT). This ADR does not redefine that claim list.

This boundary shall guide future architectural decisions.

### Assumptions

- One ECMP instance is treated as **single-tenant** relative to enterprise organization hierarchy references consumed by ECMP. Multi-tenant ECMP packaging / multi-org isolation productization is **out of scope** for this ADR (explicit non-decision).
- Mode A (Standalone) remains available as a deployment hedge; it is not an Enterprise Mode fallback IdP.
- ADR-013 (frontend technology stack) is **orthogonal** to this ADR and remains active per PROGRAM-ADR-002 BR-007. This ADR does not supersede ADR-013.
- Protocol, IdP product, frontend mount/topology, and frontend stack are non-goals of this ADR.

### Enterprise Mode Local Auth Prohibition

When Enterprise Mode (Mode B) is enabled:

- Local Login is disabled
- Forgot Password is disabled
- Reset Password is disabled
- Change Password is disabled
- Local Password Storage is prohibited

Local credential routes must not remain an authentication path under Mode B. Configuration that enables both Mode B and local login shall fail closed (fail-fast), consistent with the control posture already established for unsafe auth-mode combinations in ADR-012.

**Security cross-references** (impact / existing Mode A surface only — this ADR does not relocate or rewrite these standards):

- **SEC-PWD-001** — `10 Security and Access Standards/ECMP_Identity_Password_Management_v1.0.md` (local password change, forgot/reset, admin reset; API-410…API-413)
- **SEC-AUTH-001** — `10 Security and Access Standards/ECMP_Target_Authentication_Architecture_v1.0.md` (target AuthN design under ADR-012)
- **ADR-012** — fail-fast posture for invalid auth-mode combinations

## Architecture Boundary

| Owner | Owns | Does not own |
|---|---|---|
| **Enterprise Platform** | Authentication, SSO, User Directory, Password/MFA (enterprise), Session, Organization, Department, Branch, Enterprise Navigation, Identity Audit, **Enterprise Global Notification** | ECMP complaint lifecycle; **Core Platform Role-Permission SoT**; Complaint Roles SoT; **ECMP Business Notification** |
| **Core Platform** (ECMP domain) | Role, Permission, Role-Permission, User-Role **SoT** (ADR-008); platform audit; platform config surfaces per domain architecture | Complaint business rules; Enterprise Identity SoR (under Mode B) |
| **ECMP Business Module** | Complaint, Assignment, Escalation, Resolution, SLA, Timeline, Complaint KPI, Complaint-domain audit; **Complaint Roles / Complaint Authorization** mapping after entitlement; **ECMP Business Notification** (module-scoped) | Login UI / IdP; enterprise org/user SoR; enterprise nav shell; Role-Permission Matrix SoT; Enterprise Global Notification |

## Authentication Ownership

Authentication is performed only by the Enterprise Platform under Mode B.

User flow:

```
User
  ↓
Enterprise Login
  ↓
Enterprise SSO
  ↓
Access Token
  ↓
ECMP
  ↓
Token Validation
  ↓
Enterprise Entitlement Gate
  ↓
Complaint Module
```

ECMP never requests enterprise credentials.

Enterprise authentication alone must never grant ECMP access.

Identity claim completeness and semantics are governed by ADR-015. This ADR owns the module AuthN boundary and the Entitlement Gate; it does not own the claim contract SoT.

### Protocol / trust conveyance deferral (normative)

This ADR remains **protocol-agnostic**. Audience (`aud`), issuer (`iss`), credential format, token validation mechanics, and related conveyance controls are **not** decided here.

Those controls **SHALL** be defined in a future **protocol / binding ADR** that maps conveyance to the ADR-015 Identity Contract and preserves Mode B fail-closed posture. Until that ADR is Accepted, Mode B AuthN implementation and OpenAPI enterprise `securitySchemes` remain gated (no Mode B unlock by this document).

## Authorization Ownership

After a successful Enterprise Entitlement Gate:

- ECMP performs **Complaint Authorization** and **Complaint Roles mapping** for the complaint domain.
- Identity received from the Enterprise Platform is mapped into ECMP complaint roles only after the gate has been satisfied.
- **Role-Permission Matrix SoT = Core Platform (ADR-008).** ECMP consumes and maps; it does not become a second Role-Permission SoT.
- Enterprise roles shall not automatically become ECMP roles.
- Optional enterprise role labels in the identity payload (ADR-015) do not grant ECMP permissions.

### Complaint Roles mapping governance

The enterprise-identity → ECMP Complaint Roles mapping is an **ECMP-owned privilege-granting artifact** and is subject to the same governance discipline as the Role-Permission Matrix (ADR-008 / Security RACI):

| Concern | Owner / accountability |
|---|---|
| **Ownership** | ECMP Business Module (Complaint Authorization / Complaint Roles mapping) |
| **Approval** | Security Architect (R/A for access-affecting changes) with Architecture Board adjudication for material policy changes |
| **Audit** | ECMP module audit MUST record mapping changes and authorization decisions taken under a mapped role; Identity Audit of enterprise identity remains Enterprise Platform–owned |
| **Change control** | Mapping changes are change-controlled; they MUST NOT be performed by silent inference from optional `enterprise_role_codes` or any enterprise role label |

Mapping occurs only **after** the Enterprise Entitlement Gate. Mapping does not move Role-Permission Matrix SoT ownership away from Core Platform (ADR-008).

Example flow:

```
Enterprise Identity (ADR-015 contract)
  ↓
external_user_id
  ↓
Enterprise Entitlement Gate
  ↓
ECMP Complaint Role mapping
  ↓
Permission (Core Platform Role-Permission SoT — ADR-008)
  ↓
Complaint Business Rules
```

### Enterprise Entitlement Gate

Access to ECMP requires an explicit enterprise entitlement for the Complaint module.

Enterprise authentication alone must never grant ECMP access.

Absence of entitlement shall result in denial of access. No default ECMP role shall be assigned solely because authentication succeeded.

How entitlement is represented and issued remains a follow-up decision (see Open Questions / Follow-up). The **existence** of the gate is decided here.

## Enterprise Identity

The Enterprise Platform is the Source of Truth for enterprise identity under Mode B.

### Canonical identity contract

**ADR-015 is the Source of Truth** for the Enterprise Identity Contract consumed by ECMP under Mode B (required claims, optional claims, claim semantics including `external_user_id`, versioning, fail-closed claim rules, and compatibility rules).

This ADR retains only what is required to understand the **module boundary**:

- ownership of the AuthN / module boundary and the Entitlement Gate;
- the requirement that the ECMP Business Module correlates local module profiles to enterprise identity using the enterprise identity key defined in ADR-015 (`external_user_id`);
- the requirement to consume ADR-015 rather than redefine identity-claim semantics inline.

Normative identity-key and claim semantics are not duplicated here; see ADR-015.

## User Model

ECMP stores only module-specific information.

Example attributes:

- `external_user_id`
- notification preferences
- dashboard preferences
- favorite views
- last access
- local status

Passwords shall never be stored when Enterprise Mode is enabled (see also **SEC-PWD-001** for the Mode A local password surface that must not remain an AuthN path under Mode B).

Local copies of enterprise attributes are **projections**, not masters. When enterprise identity and local projection disagree, enterprise identity wins for enterprise-owned fields (ADR-015).

### Referential anchoring

- Local `users.id` remains the **referential anchor** for ECMP foreign keys and module relationships.
- `external_user_id` is a **unique alternate key** correlating the local profile to enterprise identity (claim semantics per ADR-015).
- ECMP must not re-key historical complaint relationships onto `external_user_id` as part of this decision.

### User Provisioning

Enterprise Mode uses Just-In-Time Provisioning.

Provisioning is subject to the Enterprise Entitlement Gate. Enterprise authentication alone must never create ECMP access.

Lifecycle (normative event set; transport and schedule out of scope):

```
Identity received (ADR-015)
  ↓
Lookup external_user_id
  ↓
Enterprise Entitlement Gate
  ↓
Create | Update | Deactivate | Reactivate
  ↓
Continue or Deny
```

Lifecycle operations:

- **Create** — create a local ECMP profile when an entitled identity is first seen (aligns with ADR-015 **Introduce**)
- **Update** — update local projections from enterprise identity (aligns with ADR-015 **Update**)
- **Deactivate** — deactivate the local ECMP profile when entitlement or employment status requires it (aligns with ADR-015 **Suspend / Deactivate**)
- **Reactivate** — reactivate a previously deactivated local profile when entitlement is restored (aligns with ADR-015 **Reactivate**)
- **Periodic Reconciliation** — reconcile local projections against enterprise identity (aligns with ADR-015 **Reconcile**)

ADR-015 additionally defines **Terminate key** (`external_user_id` never reused). That rule is consumed here; it is not redefined.

Future synchronization strategies may refine transport without changing this decision.

## Organization Ownership

Enterprise Platform owns:

- Organization
- Branch
- Department

ECMP stores references only.

ECMP shall not become the master source for organizational hierarchy.

### Organizational model implementation gap (recorded)

**Consequence / gap:** under Mode B this ADR requires organization, branch, and department **references** from the Enterprise Platform (ADR-015 required claims). The current ECMP foundation schema exposes a local `branches` model and does **not** yet provide first-class `organizations` / `departments` masters aligned to that three-level reference set.

**Mode B prerequisite (audit K-7 — binding):** closing that gap (resolvable three-level organizational masters / projections per ADR-018) is a **prerequisite for Mode B unlock**. PROGRAM-BOARD-004 **C-7** remains CLOSED until Architecture Board explicitly unlocks Mode B **and** this prerequisite is satisfied (or an explicit Board waiver Resolution cites this section). This ADR still does **not** authorize schema redesign by itself.

Normative cross-ref: `18 Architecture Governance/ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`; ADR-018 §8 / §15.

## Architecture Dependency

### Organization Synchronization

Organization Synchronization is an Architecture Dependency of this ADR.

ECMP authorization depends on organization hierarchy (organization, branch, department). ECMP stores references only; therefore organization structure must be available from the Enterprise Platform for authorization to function correctly under Enterprise Mode.

Protocol, frequency, and transport for Organization Synchronization remain outside the scope of this ADR and require a future decision. The dependency itself is recorded here and is **not** an open question as to whether synchronization is required.

## Deployment Modes

### Mode A — Standalone

- Authentication: Local (and/or Mode A target auth as disposed with ADR-007 / ADR-012)
- Recommended for customers deploying ECMP independently / development hedge.

### Mode B — Enterprise

- Authentication: Enterprise SSO (Enterprise Platform)
- Identity claims: ADR-015 contract
- Recommended for enterprise platform deployments.

When Enterprise Mode is enabled, the Enterprise Mode Local Auth Prohibition applies.

### Containment Principle

Identity-mode divergence (Mode A vs Mode B) **terminates at the Identity Adapter boundary**.

- The Identity Adapter owns AuthN consumption differences, ADR-015 claim validation (Mode B), Entitlement Gate application, and local profile correlation.
- **Business modules SHALL remain mode-independent.** Complaint lifecycle rules, case state machines, and domain services MUST NOT branch on deployment mode (`if Mode B` / `if enterprise_mode` in business logic).
- Organization resolution and scope **inputs** may differ by mode at the adapter / platform boundary; complaint **business rules** that consume already-resolved authorization context remain mode-independent.

Precise invariant: *Complaint business rules and the case state machine are mode-independent. Identity source, organization resolution, and scope derivation are mode-dependent and confined to the Identity Adapter / platform boundary.*

### Mode A → Mode B cutover stance (governance only)

This ADR does **not** define cutover implementation, tooling, or data-migration procedures.

**Governance position:**

- Enabling Mode B for an existing Mode A deployment requires an explicit future **Decision Record (DEC)** approved by Architecture Board (cutover / linking DEC).
- That DEC MUST define how existing local profiles are correlated to `external_user_id` **without** using email (or other non-key attributes) as the enterprise identity key (ADR-015).
- Local `users.id` remains the referential anchor; historical complaint relationships MUST NOT be re-keyed onto `external_user_id` as part of cutover (see Referential anchoring).
- This ADR, DEC-020, FRD LOCKED, and PROGRAM-IMPLEMENTATION-001 do **not** authorize Mode B cutover, Batch-2, or enterprise customer production.

Until that cutover DEC is Accepted, Mode A and Mode B remain separately governed deployment modes; coexistence of dual SoT complaint namespaces (DEC-020) is orthogonal and unchanged.

### Interaction with ADR-012 `ECMP_AUTH_MODE` (proposed matrix for Board)

| ADR-014 Mode | `ECMP_AUTH_MODE` (ADR-012) | Validity |
|---|---|---|
| Mode A | `dev` | Valid for development / Mode A hedge |
| Mode A | `jwt` | Valid for Mode A JWT / local IdP path per ADR-012, subject to Board disposition of ADR-012 |
| Mode B | enterprise presentation conforming to ADR-015 | Valid only when AuthN is Enterprise Platform–owned and claims conform to ADR-015 |
| Mode B | `dev` | **Invalid** — must fail-fast |
| Mode B + local credential routes enabled | any | **Invalid** — must fail-fast |

This matrix is an authoring proposal for Architecture Board confirmation. It does not supersede ADR-012 by itself.

## Multi-tenancy stance

**Out of scope / explicit assumption:** this ADR treats one ECMP instance as single-tenant relative to consumed enterprise organization references. Multi-tenant ECMP packaging, cross-tenant isolation productization, and multi-org tenancy models are not decided here and require a separate Board decision if required.

## Architecture Principles

- Authentication and Authorization are separate concerns.
- Enterprise Platform owns Authentication under Mode B.
- ECMP owns Complaint Authorization and Complaint Roles mapping after the Entitlement Gate.
- Role-Permission Matrix SoT = Core Platform (ADR-008).
- Enterprise Platform owns Enterprise Identity.
- ADR-015 is the SoT for the Enterprise Identity Contract.
- ECMP owns Complaint Business Rules.
- Business modules shall consume Enterprise Identity rather than implement Enterprise Authentication.
- Enterprise authentication alone must never grant ECMP access.
- **Containment Principle:** identity-mode divergence terminates at the Identity Adapter; business modules remain mode-independent.
- Enterprise Global Notification ≠ ECMP Business Notification.

## Non-goals

This ADR does not decide:

- Identity protocol (OIDC, OAuth2, SAML, internal token) or credential formats
- Audience (`aud`) / issuer (`iss`) validation mechanics (deferred to protocol / binding ADR — see Protocol / trust conveyance deferral)
- IdP product selection
- Frontend technology stack (ADR-013 remain active — BR-007; orthogonal)
- Frontend mount / deployment topology
- Enterprise Entitlement claim representation / issuance format
- Organization Synchronization protocol or cadence
- Mode A → Mode B cutover implementation (governance stance only; future cutover DEC required)

## Risks

| ID | Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|---|
| R-01 | Unreconciled AuthN designs (Mode A local, ADR-012 target, Mode B enterprise) confuse implementers | High | Medium until Board disposition | Relationship table + Mode matrix submitted for Board; no silent supersession |
| R-02 | Local credential routes remain live under Mode B | Critical | Medium if controls weak | Local Auth Prohibition + fail-fast; SEC follow-up after acceptance |
| R-03 | Entitlement Gate exists without representation decision | High | Medium | Gate normative here; representation listed as follow-up, not as “gate optional” |
| R-04 | Teams treat ADR-014 inline history as claim SoT instead of ADR-015 | High | Medium | Pointer-only Enterprise Identity section; package submit with ADR-015 |
| R-05 | Organization Synchronization delayed while AuthZ depends on org refs | High | Medium | Architecture Dependency recorded; follow-up ADR required |
| R-06 | Multi-tenancy discovered late | High | Low–Medium | Explicit single-tenant assumption / out-of-scope statement |
| R-07 | Mode conditionals leak into domain services | Medium | Medium without containment | Containment Principle — Identity Adapter boundary |
| R-08 | Mode A→B cutover links by email or re-keys history | High | Medium without cutover DEC | Cutover stance + future DEC required; ADR-015 key rules |

## Open Questions

The following topics remain outside the scope of this ADR and require future decisions. They are **not** questions about whether the gate or org sync dependency exists:

- Identity protocol / conveyance binding, including `aud` / `iss` isolation (downstream of ADR-015; OD-FE-002 remains open until Board accepts this package and a protocol ADR is decided)
- Token lifecycle, refresh strategy, Single Logout
- Enterprise Entitlement representation and issuance
- Identity caching / offline validation posture
- High availability for Identity Provider
- Organization Synchronization protocol and cadence
- Service-to-service identity under Mode B
- Break-glass administrative access under Mode B
- Mode A → Mode B cutover DEC (linking method; not email-as-key)

## ADR Relationship

| ADR | Relationship |
|---|---|
| ADR-002 | **Consistent** — ECMP is not SoR for data it does not own; identity and organization follow the same principle under Mode B. |
| ADR-008 | **Complementary / Constrains** — Role-Permission Matrix SoT remains Core Platform. This ADR does not move SoT to Enterprise Platform or to the ECMP Business Module. |
| ADR-015 | **Complementary** — ADR-015 is the Identity Contract SoT required by this module boundary. Submit as one package. |
| ADR-007 | **Proposed disposition for Board (not executed):** Mode A–scoped applicability. Slice/target auth model remains valid for Mode A; under Mode B, AuthN ownership follows this ADR and identity claims follow ADR-015. Status remains **Relationship Pending** until Board confirms. |
| ADR-012 | **Proposed disposition for Board (not executed):** Mode A baseline IdP / Mode B subsumption candidate. Status remains **Relationship Pending** until Board confirms. See **ADR-012 relationship disclosure** below. |
| ADR-013 | **Orthogonal** — frontend stack; remain active (BR-007). Not superseded by this ADR. |

No supersession is declared by this ADR.

### ADR-012 relationship disclosure (editorial — no preference)

Architecture Board disposition of ADR-012 relative to this package affects **authorization flow semantics**, not only claim vocabulary alignment.

Proposed disposition options and architectural consequences (disclosure only; this ADR does **not** recommend an option):

| Proposed Board option | Consequence for authorization flow semantics | Consequence for claim vocabulary |
|---|---|---|
| **Mode A–only** | Mode B authorization flow is governed by Enterprise Platform AuthN → ADR-015 identity contract → ADR-014 Entitlement Gate → Complaint Roles mapping → Core Platform Role-Permission SoT (ADR-008). ADR-012 target AuthN flow does not authorize Mode B ECMP access. | ADR-012 historical claims (for example `sub`, `roles[]`, `orgUnitId`) do not become Mode B identity/authorization vocabulary. |
| **Subsumed as Enterprise Platform IdP implementation detail** | An IdP chosen under ADR-012 may implement Enterprise Platform authentication, but Mode B authorization flow still requires the ADR-014 Entitlement Gate and ADR-008 Role-Permission enforcement after ADR-015 identity acceptance. Subsumption does not collapse AuthN success into ECMP authorization. | Wire/token fields from ADR-012-era models require governed mapping to ADR-015; they must not silently redefine Mode B authorization inputs. |
| **Other (Board-defined)** | Any other disposition must still state how Mode B authorization flow relates to the ADR-014 Entitlement Gate, ADR-015 identity acceptance, and ADR-008 Role-Permission SoT. | Claim reconciliation remains mandatory if historical vocabularies remain in use. |

This disclosure does not execute a relationship change and does not supersede ADR-012.

## Consequences

### Positive

- Single Login Experience under Mode B
- Centralized Identity Management
- Enterprise-ready Business Module boundary
- Reduced operational complexity
- Cleaner security boundary
- Explicit entitlement prevents unintended access from enterprise authentication alone
- Clear SoT split: AuthN/Identity (Enterprise Platform), Identity Contract (ADR-015), Role-Permission Matrix (ADR-008), Complaint AuthZ mapping (ECMP)

### Negative / Trade-offs

- Dependency on Enterprise Identity availability
- Need for token validation infrastructure (protocol / binding ADR follow-up — includes audience/issuer isolation)
- Role mapping layer required after entitlement (governed ECMP artifact)
- Additional integration testing
- Dependency on Organization Synchronization
- Dependency on Enterprise Entitlement Gate representation follow-up
- Concentration of AuthN availability risk in the Enterprise Platform
- **Organizational model implementation gap** — three-level enterprise org references required under Mode B while current foundation schema is branch-centric — now a **Mode B unlock prerequisite** (audit K-7; see PROGRAM-MODE-B-ORG-GAP-001)
- Dual-mode maintenance tax bounded only if Containment Principle is enforced
- Mode A → Mode B cutover requires a separate DEC before linking existing local users

### Document history

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-29 | Initial Proposed |
| 1.1 | 2026-07-29 | Entitlement Gate, local-auth prohibition, identity-key rules, lifecycle (pre–Board PHASE-0 metadata) |
| 1.2 | 2026-07-30 | PROGRAM-ENTERPRISE-001 PHASE-2 coordinated revision with ADR-015: ownership language, ADR-015 SoT pointer, anchoring, multi-tenancy stance, options/risks, relationship proposals |
| 1.3 | 2026-07-30 | PROGRAM-ENTERPRISE-001 FINAL EDITORIAL PACKAGE: ADR-012 disposition disclosure (AuthZ flow semantics), terminology table, Identity SoT de-duplication → ADR-015, SEC-PWD-001/SEC-AUTH-001 cross-refs, Board Resolution traceability |
| 1.4 | 2026-07-30 | PROGRAM-ADR-004 Board Readiness: notification ownership split, Containment Principle, Mode A→B cutover stance, org-model gap consequence, role-mapping governance, protocol deferral for aud/iss; disposition **Revised — Pending Board Review**; remains Proposed |
| 1.4a | 2026-07-30 | Audit **K-7** — elevate organizational model gap from “post-Accept delivery concern” to **Mode B prerequisite** (C-7 unlock gated); no Mode B unlock; no schema redesign authorized |

### Follow-up Actions

- [x] Architecture Board review of **ADR-014 + ADR-015 package (PROGRAM-ADR-004)** → Accepted with Conditions (PROGRAM-BOARD-004 BR-009/BR-010)
- [ ] Board disposition of ADR-007 / ADR-012 relationships (proposals above)
- [x] Define Organization Synchronization approach as a follow-on decision — ADR-018 Proposed; **org-model gap = Mode B prerequisite (K-7)**
- [x] Define Enterprise Entitlement representation as a follow-on decision — ADR-017 Proposed
- [x] Define protocol / binding ADR (`aud` / `iss` / conveyance) — ADR-016 Proposed; does not unlock Mode B until Accepted and gated work authorized
- [ ] Mode A → Mode B cutover DEC (when needed) — linking without email-as-key; no re-key of historical FKs; **blocked until org-gap prerequisite met**
- [ ] After Accepted: update Solution Architecture identity/module sections
- [ ] After Accepted: sync Security standards references as needed (no protocol invention in this ADR)
- [x] After Accepted: sync FE-ARCH LAP-01..03 / OD-FE-008 Pending Upstream exit criteria
- [ ] Communicate to impacted teams — Core Platform, ECMF, Security, Integration, Enterprise Platform owners
