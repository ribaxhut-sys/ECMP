# ECMP ADR-014 — Independent Architecture Review

| Field | Value |
|---|---|
| ID | GOV-REV-014 |
| Version | 1.0 |
| Subject | `05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.0.md` |
| Subject Status at Review | 🟡 Proposed |
| Review Type | Independent architecture review (Principal Enterprise Architect) |
| Reviewer Role | Principal Enterprise Architect |
| Owner | Architecture Board Chair |
| Approver | Architecture Board |
| Status | 🟢 Complete |
| Review Date | 2026-07-29 |
| Next Review | On ADR-014 v1.1 resubmission |

## Scope and Method

This review assesses the **architecture only**. No implementation, no ADR rewrite, no code.

Evidence base:

- `05 Architecture Decision Records/` — ADR-002, ADR-007, ADR-008, ADR-012, ADR-014
- `10 Security and Access Standards/` — SEC-AUTH-001, SEC-RBAC-FLOW-001, SEC-IAM-CACHE-001, SEC-PWD-001
- `18 Architecture Governance/README.md` — RACI, ADR lifecycle, quality gates
- `24 Templates/ADR_TEMPLATE.md` — canonical ADR structure
- Implemented state: `backend/app/models/__init__.py`, `backend/app/modules/iam/`, `backend/app/modules/audit/models.py`

Findings are identified as `S-nn` (strength), `W-nn` (weakness), `M-nn` (missing consideration), `RISK-nn`, `REC-nn`.

---

## 1. Executive Position

The **core decision is correct and should be endorsed**. Transferring enterprise identity ownership to the Enterprise Platform and reducing ECMP to a business module is the right boundary, is internally consistent with the precedent already set by ADR-002 (ECMP is not a system of record for data it does not own), and preserves the Role-Permission SoT established in ADR-008.

The ADR is, however, **incomplete relative to the repository's own ADR standard** and leaves three decisions unstated that are blocking rather than deferrable:

1. No entitlement gate — "assign default ECMP role" makes every authenticated enterprise user an ECMP user by default (§4, `W-07`).
2. No disposition for the **already-implemented** local credential surface (SEC-PWD-001) under Enterprise Mode — an SSO-bypass exposure (§5, `W-05`).
3. Just-In-Time Provisioning covers *create* only — no leaver, no attribute drift, no reactivation, no cutover linking (§2, `W-09`).

None of these require redesign. All three are completions of the decision ADR-014 already makes.

---

## 2. Enterprise Architecture

### Strengths

- `S-01` — The boundary statement ("Enterprise Platform owns Enterprise Identity; ECMP owns Complaint Management") is crisp, testable, and durable. It is the kind of statement that can actually arbitrate future disputes, which is the purpose of an ADR.
- `S-02` — Architecturally consistent with ADR-002. ECMP already declines ownership of customer master data; declining ownership of identity and organization applies the same principle to a second domain rather than inventing a new one.
- `S-03` — Correctly identifies the failure mode being avoided (duplicate identity stores across N modules) rather than justifying the change on technology preference.
- `S-04` — Explicit statement that "this boundary shall guide future architectural decisions" gives the ADR standing as a principle, not just a point decision.

### Weaknesses

- `W-01` — **Does not conform to the repository ADR template.** `24 Templates/ADR_TEMPLATE.md` and the ADR lifecycle in `18 Architecture Governance/README.md` step 1 require options **with trade-offs**. "Alternatives Considered" contains two alternatives with one-line verdicts and no pros/cons. The alternatives are also not genuinely distinct — Alternative 1 is the status quo and Alternative 2 is the decision, so no real option space was explored. At minimum a third option (federated identity with ECMP retaining a local IdP for fallback) was available and should be recorded as considered and rejected, with reasons.
- `W-02` — **Governance defect in ownership.** Owner is recorded as CTO. The RACI in `18 Architecture Governance` assigns ADRs **R** = Solution Architect / Tech Lead, **A** = Architecture Board, with **Security consulted whenever auth or data is touched**. This ADR touches both and lists no Security Architect reviewer. Compare ADR-007 and ADR-012, both Security-Architect-owned. A CTO-authored ADR is legitimate as a strategic directive, but it must still route through the defined review path or the governance model is undermined by its own leadership.
- `W-03` — **Supersession relationship to ADR-007 / ADR-012 is unstated.** ADR-012 (still 🟡 Proposed) decides Keycloak as ECMP's baseline IdP with a full token model. ADR-014 decides authentication moves out of ECMP entirely. These are not obviously compatible, and the ADR lifecycle requires a superseding ADR to explicitly reference what it replaces. As written, the repository now contains **three concurrent authentication designs**: the implemented local login (SEC-PWD-001), the proposed Keycloak target (ADR-012), and the enterprise SSO direction (ADR-014). Follow-up action "reconcile implications" is too weak for this — reconciliation is a precondition of acceptance, not a downstream task.
- `W-04` — The **Risks section duplicates Negative/Trade-offs verbatim**. Four identical bullets appear twice. No likelihood, impact, owner, or mitigation. This is not a risk register; it is a restatement.

### Missing Considerations

- `M-01` — **Multi-tenancy is entirely absent.** If the Enterprise Platform serves multiple organizations, does one ECMP instance serve all of them, or one per tenant? This changes data scoping, audit isolation, and the meaning of `organization_id` fundamentally. Silence here is the most likely source of an expensive late discovery.
- `M-02` — No statement of which side owns the **identity contract** as a versioned artifact, or how it is governed. "Additional claims may be introduced without changing ECMP business logic" is an aspiration with no owner.
- `M-03` — No commercial/packaging owner for the Standalone vs Enterprise distinction. Deployment modes are also a product-licensing decision; no accountable party is named.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-01` | Three unreconciled authentication designs coexist; teams implement against different ones | High | High if ADR accepted as-is |
| `RISK-02` | Multi-tenancy discovered as a requirement after scoping and audit models are built | High | Medium |
| `RISK-03` | ADR accepted without Security review sets precedent that leadership-authored ADRs bypass governance | Medium | Medium |

### Recommendations

- `REC-01` — Before acceptance, state explicitly whether ADR-014 **supersedes ADR-012 in whole, in part, or subsumes it** (e.g. "Keycloak becomes the Enterprise Platform IdP" vs "ADR-012 applies to Mode A only"). Record the outcome in both ADRs. *Why: the ADR lifecycle mandates it, and without it two teams can build to contradictory targets while both believe they are compliant.*
- `REC-02` — Add Decision Drivers and a genuine Options Considered section per the canonical template, and add Security Architect as reviewer. *Why: conformance to the repo's own governance is what makes the ADR enforceable against others later.*
- `REC-03` — Answer the multi-tenancy question in this ADR, even if the answer is "single-tenant per ECMP instance; multi-tenant explicitly out of scope." *Why: a recorded "no" is architecture; silence is a latent assumption.*
- `REC-04` — Replace the duplicated Risks section with a risk register carrying impact, likelihood, owner, and mitigation.

---

## 3. Identity & Access Management

### Strengths

- `S-05` — Correct refusal to make ECMP an Identity Provider. Stated unambiguously, twice.
- `S-06` — **"Enterprise roles shall not automatically become ECMP roles"** is the single best line in the document. It prevents the most common enterprise IAM failure — implicit privilege inheritance across a trust boundary — and it preserves ADR-008's Role-Permission SoT without needing to restate it.
- `S-07` — The minimum identity payload is a sensible, small, stable set. Requiring `employment_status` shows lifecycle awareness.
- `S-08` — "Passwords shall never be stored when Enterprise Mode is enabled" is the right absolute.

### Weaknesses

- `W-05` — **The already-implemented local credential surface has no disposition.** SEC-PWD-001 is marked **Implemented**: `API-410`…`API-413`, `users.password_hash`, `password_reset_tokens`, `force_password_change`, admin temporary-password reset. ADR-014 assigns Password Management and MFA to the Enterprise Platform but never says what becomes of those endpoints in Enterprise Mode. If they remain routable, they are an **authentication bypass**: a path to obtain an ECMP session without traversing enterprise SSO, MFA, or identity audit. "Passwords shall never be stored" constrains the data; it does not constrain the code path.
- `W-06` — **`external_user_id` is listed but not specified.** Nothing states that it must be opaque, immutable, non-reassignable, and the sole join key — nor that `email` must **not** be used as an identity join key. Email is reassigned in real directories; joining on it silently grants a new employee a predecessor's history.
- `W-07` — **"Assign default ECMP role" is default-allow.** Combined with enterprise SSO, the ECMP access boundary collapses to "holds any enterprise account." Every authenticated user of *any* module on the platform becomes a provisioned ECMP user with a working role. This is a privilege-escalation surface created by default, and it is the most consequential unstated decision in the ADR.
- `W-08` — Identity **audit is split** (Enterprise Platform owns Identity Audit; ECMP owns complaint audit) with no correlation mechanism defined. Answering "who did what, end to end" now requires joining two audit stores with no shared correlation key and no stated clock discipline.

### Missing Considerations

- `M-04` — **Referential anchoring is not decided.** The implemented schema uses local `users.id` (UUID) as the FK target for roughly sixteen relationships — complaints, assignments, escalations, resolutions, appointments, timelines, attachments — several with `ondelete="RESTRICT"`. `audit_logs.actor_id` is an unconstrained UUID. The ADR must state that **local `users.id` remains the referential anchor and `external_user_id` is a unique alternate key**. The alternative — re-keying on the enterprise identifier — is a destructive migration across the entire complaint history and must be ruled out explicitly, now, in writing.
- `M-05` — Existing `users` constraints conflict with naive JIT: `email` UNIQUE, `username` UNIQUE, and `role_id` **NOT NULL** FK to `roles`. JIT cannot create a profile without selecting a role (which is why `W-07` exists), and uniqueness collides on directory re-creation or email reuse.
- `M-06` — No **access recertification / attestation** position. Enterprise deployments are normally subject to periodic entitlement review; ADR-014 creates locally-owned entitlements (ECMP roles) mapped from external identities, which is precisely the structure auditors ask about.
- `M-07` — No **service-to-service identity**. ADR-012 covered `client_credentials`; ADR-014 is silent. Batch jobs, KPI consumers, notification workers, and event consumers still require identity under Enterprise Mode.
- `M-08` — No **PII position on the cached profile**. `display_name` and `email` held locally constitute a PII copy under ECMP retention. ADR-002 raised exactly this for the customer cache; ADR-014 does not inherit the concern.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-04` | Local password endpoints remain live in Enterprise Mode → SSO/MFA bypass, unattributed identity | Critical | High if unaddressed |
| `RISK-05` | Any enterprise user self-provisions into ECMP with a working role | High | Certain, as specified |
| `RISK-06` | Identity join performed on `email`; history mis-attributed on address reuse | High | Medium |
| `RISK-07` | Re-keying to `external_user_id` proposed at implementation time; full-history migration | High | Medium |

### Recommendations

- `REC-05` — Decide and record: in Enterprise Mode, local credential endpoints are **disabled at routing level**, with a **fail-fast startup assertion** if both Enterprise Mode and local login are enabled. Reuse the pattern ADR-012 §5 already established for dev-mode refusal. *Why: consistency with an existing accepted control, and because a disabled-by-configuration authentication path is not a control — an absent route is.*
- `REC-06` — Add an **entitlement gate** to the provisioning flow. Two acceptable forms: (a) the Enterprise Platform asserts module entitlement via an application-assignment claim, and ECMP denies access absent that claim; or (b) the JIT default role is a **zero-permission `PENDING` role** requiring administrative activation. State which. *Why: default-deny is the required posture at a trust boundary; the ADR currently specifies default-allow, and this is the difference between a controlled module and an open one.*
- `REC-07` — Specify `external_user_id` as **opaque, immutable, non-reassignable, and the only identity join key**, and prohibit `email` as a join key. State that local `users.id` remains the referential anchor. *Why: closes `RISK-06` and `RISK-07` at design time for the cost of three sentences.*
- `REC-08` — State that ECMP audit records **denormalize actor name at write time** (the implemented `audit_logs.actor_name` already does this — endorse it) and that a shared correlation identifier spans enterprise and module audit. *Why: once identity is external, the directory may not be queryable at read time, and audit must remain readable without it.*

---

## 4. Authentication Boundary

### Strengths

- `S-09` — "ECMP never requests enterprise credentials" is exactly the right invariant, stated in the strongest possible form.
- `S-10` — The flow diagram terminates ECMP's involvement at token validation. Correct.
- `S-11` — Deferring protocol choice (OIDC/OAuth2/SAML) is legitimate for a directional ADR; the boundary does not depend on the protocol.

### Weaknesses

- `W-09` — Deferring the protocol **and** trust establishment **and** token lifecycle **and** SLO simultaneously means the boundary is *declared* but not *verifiable*. Nothing in the ADR can currently be tested or implemented against. This is acceptable only if the ADR is explicitly labelled directional and gated accordingly — it is not.
- `W-10` — **Two independent mode switches now exist.** ADR-012 defines `ECMP_AUTH_MODE=dev|jwt`; ADR-014 defines Standalone vs Enterprise. Their interaction is undefined — a four-cell matrix with at least one nonsensical and one dangerous cell.

### Missing Considerations

- `M-09` — No **fail-closed rule** for missing or unrecognised claims. If `organization_id` is absent, does ECMP deny, or grant unscoped access? The correct answer is deny; it must be written down.
- `M-10` — No **JWKS caching / offline validation** posture, despite ADR-012 having already solved this. Cached signing keys let ECMP continue validating tokens through an IdP outage; without it, `RISK-08` is far worse than it needs to be.
- `M-11` — No **break-glass administrative access** for Enterprise Mode.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-08` | Enterprise IdP outage → total ECMP unavailability, including administrative access | High | Medium |
| `RISK-09` | Auth-mode matrix produces a deployment authenticating locally while believing it is enterprise-federated | High | Medium |

### Recommendations

- `REC-09` — Collapse to **one** mode concept, or define the full matrix and mark invalid combinations as fail-fast at startup. *Why: two orthogonal switches governing the same security property is how misconfiguration becomes invisible.*
- `REC-10` — Adopt ADR-012's cached-JWKS validation explicitly so token validation survives IdP unavailability, and state the degraded-mode expectation (existing sessions continue; new logins fail). *Why: it converts a total outage into a partial one at no design cost, and the mechanism is already designed.*
- `REC-11` — Define a **designed, audited, time-boxed break-glass path** for Enterprise Mode — and note explicitly that it is **not** the residual password endpoints from `REC-05`. *Why: `REC-05` and `M-11` are in tension; resolving them separately is what prevents the bypass from being reintroduced as an operational necessity.*
- `REC-12` — Add a **gating clause**: no Enterprise Mode implementation may begin until the identity contract ADR (protocol, claims, trust, lifecycle) is Accepted. *Why: consistent with the G0/G1 principle already in `18 Architecture Governance` — contract frozen before code.*

---

## 5. Authorization Boundary

### Strengths

- `S-12` — "Authorization remains internal" is correct and defensible. Complaint authorization depends on complaint semantics; externalising it would couple the Enterprise Platform to ECMP's domain model.
- `S-13` — The mapping chain (`Enterprise Identity → external_user_id → ECMP Role → Permission → Business Rules`) is the right shape and aligns with the implemented resolver pipeline in SEC-RBAC-FLOW-001.
- `S-14` — Consistent with ADR-008: role→permission resolution stays in Core Platform, permissions are not carried in the token.

### Weaknesses

- `W-11` — **One genuine boundary leak.** ADR-014 assigns Organization / Branch / Department to the Enterprise Platform, but ECMP's data scopes are *defined in terms of those identifiers* — SEC-RBAC-FLOW-001 implements `ORGANIZATION` and `BRANCH` scope types. An authorization decision made inside ECMP therefore depends on a hierarchy owned externally with undefined freshness. The claim "Authorization remains internal" is true for the *decision* but not for its *inputs*, and the ADR does not acknowledge the difference.
- `W-12` — Consequently, **"Organization synchronization" is misfiled under Open Questions.** It is not an optional enhancement; it is a prerequisite for correct authorization. Stale org data does not degrade a report — it grants or denies access incorrectly.
- `W-13` — Role mapping is asserted ("Identity received from Enterprise Platform shall be mapped into ECMP-specific roles") but its ownership, storage, and change-control are unstated. A mapping table is itself a privilege-granting artifact and needs the same governance as the role matrix.

### Missing Considerations

- `M-12` — No position on **hierarchy semantics**: does a `BRANCH` scope imply descendants? The implemented `branches` table is self-referential (`parent_branch_id`), so hierarchy exists locally today; under external ownership, traversal depth and its source must be defined.
- `M-13` — Nothing on what happens when an org unit is **deleted or restructured upstream** while ECMP holds complaints scoped to it.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-10` | Stale org references → incorrect authorization grant or denial | High | High without a sync contract |
| `RISK-11` | Upstream org restructure orphans scope references on live complaints | Medium | Medium |

### Recommendations

- `REC-13` — Reclassify org synchronization from Open Question to **decision dependency**, and adopt the ADR-002 pattern explicitly: local read-only cache, defined refresh, "as of" semantics, ECMP never authoritative. *Why: the pattern is already accepted in this repository for exactly this problem shape; reusing it costs nothing and inherits a reviewed design.*
- `REC-14` — State that the enterprise-role → ECMP-role mapping is an **ECMP-owned, audited, change-controlled artifact** under the same governance as the role matrix (`10 Security and Access Standards`, Security = R/A per RACI). *Why: without this, the mapping becomes an ungoverned side channel into the permission model that ADR-008 deliberately centralised.*

---

## 6. Security

### Strengths

- `S-15` — Eliminating duplicate credential stores is a material, real reduction in attack surface — the strongest security argument for the decision, and it is correctly made.
- `S-16` — Centralised MFA and password policy at the Enterprise Platform is the correct placement.
- `S-17` — Not embedding permissions in the token (inherited from ADR-008 / ADR-012) is preserved.

### Weaknesses

- `W-14` — See `W-05` / `RISK-04`. This is the most serious security finding in the review: an implemented local authentication path with no stated disposition under a new external-authentication regime.
- `W-15` — No threat-model delta. `ECMP_Threat_Model_v0.1.md` exists and predates this boundary change. Moving authentication across a trust boundary invalidates parts of it — token replay, IdP compromise blast radius, claim injection, and confused-deputy scenarios between modules are all newly relevant.
- `W-16` — No statement on **token audience isolation**. If the Enterprise Platform issues tokens for N modules, a token minted for another module must not be accepted by ECMP. `aud` validation is the control; ADR-012 had it, ADR-014 does not restate it.

### Missing Considerations

- `M-14` — Session termination semantics at enterprise scope. ADR-012 accepted a 15-minute post-logout validity window; under SSO across N modules the blast radius of that window is larger and the trade-off deserves re-affirmation rather than silent inheritance.
- `M-15` — No mention of **step-up authentication** for high-impact complaint actions, where the enterprise IdP is the natural place to enforce it.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-12` | Token issued for another platform module accepted by ECMP | High | Medium without `aud` enforcement |
| `RISK-13` | IdP compromise grants access to every module simultaneously | Critical | Low, but concentrated by this decision |

### Recommendations

- `REC-15` — Require **strict `aud` / `iss` validation and per-module audience isolation** as a normative statement in this ADR, not a downstream detail. *Why: it is the control that keeps "one login" from becoming "one token opens everything."*
- `REC-16` — Commission a **threat-model delta** against `ECMP_Threat_Model_v0.1.md` as an acceptance condition. *Why: the trust boundary moved; a threat model that assumes ECMP authenticates its own users is no longer describing the system.*
- `REC-17` — Record explicitly that centralising identity **concentrates** risk (`RISK-13`) as well as reducing it. The Consequences section currently lists only benefits. *Why: an ADR that records only upside is not a decision record, and this trade-off is real and acceptable — it just needs to be stated.*

---

## 7. Scalability

### Strengths

- `S-18` — Removing authentication load from ECMP is a genuine scaling benefit; login/session/password traffic moves to a purpose-built component.
- `S-19` — Stateless token validation scales horizontally.

### Weaknesses

- `W-17` — The **IAM cache is process-local**. SEC-IAM-CACHE-001 documents an in-memory singleton, 5-minute TTL, `invalidate_iam_all()` on role-permission writes, and explicitly non-goals Redis. Under Enterprise Mode with multiple replicas this yields (a) divergent authorization decisions across instances for up to 5 minutes and (b) no cross-instance invalidation. What was a reasonable deferral at single-instance scale becomes a correctness constraint at enterprise scale.
- `W-18` — JIT provisioning executes on the **request path**. First-login write amplification during a mass enterprise rollout — an org-wide cutover — is a foreseeable load spike, and a write on the authentication path is a contention point.

### Missing Considerations

- `M-16` — No expected scale figures: user population, concurrent sessions, token validation rate, modules sharing the IdP. Scalability cannot be assessed against unstated targets, and `04 Solution Architecture/ECMP_NFR_Specification_v0.1.md` predates this decision.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-14` | Authorization inconsistency across replicas up to cache TTL after entitlement change | Medium | High at multi-instance scale |
| `RISK-15` | JIT write storm at enterprise cutover | Medium | Medium |

### Recommendations

- `REC-18` — Record that Enterprise Mode **reclassifies the distributed-cache non-goal** in SEC-IAM-CACHE-001 from deferral to constraint, and register it as a follow-up decision. *Why: the ADR should not solve it, but it should not silently invalidate an existing accepted design without saying so.*
- `REC-19` — Require NFR targets for identity operations before implementation gating. *Why: `M-16` makes every scalability statement in this section provisional.*

---

## 8. Maintainability

### Strengths

- `S-20` — Narrowing ECMP to complaint management reduces long-term surface. Directionally the decision *improves* maintainability.
- `S-21` — Preserving one authorization model across both modes avoids forking the domain.

### Weaknesses

- `W-19` — **Dual-mode is a permanent maintenance tax and the ADR under-weights it.** "Additional integration testing" is one bullet; the reality is a doubled test matrix, two identity paths, two provisioning paths, and two session models — maintained indefinitely, since Mode A is a supported product configuration and not a transitional state. ADR-012 already flagged the two-mode hazard as its risk R-1 at a smaller scope.
- `W-20` — No **containment principle** for mode divergence. Without one, `if enterprise_mode` conditionals leak into domain services and the boundary erodes from inside.
- `W-21` — "Complaint domain behavior shall remain identical across both modes" is **not achievable as literally written**. Data-scope resolution differs by construction: in Standalone, branch is ECMP-owned (`branches` table, self-referential hierarchy); in Enterprise, it is an external reference with different freshness and lifecycle. The intent is right; the wording overreaches and will be cited later as license to ignore real differences.

### Missing Considerations

- `M-17` — No **deprecation position on Mode A**. Is Standalone permanent, or sunset after enterprise adoption? The maintenance cost calculus differs entirely.
- `M-18` — Documentation debt: SEC-PWD-001, SEC-AUTH-001, SEC-RBAC-FLOW-001, `ECMP_AuthN_Limitations_Register`, and the Solution Architecture §8 all become partially inaccurate on acceptance. Follow-up actions cover only Solution Architecture.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-16` | Mode conditionals proliferate into domain code; boundary erodes | Medium | High without `REC-20` |
| `RISK-17` | Security documentation set drifts out of sync with the accepted architecture | Medium | High |

### Recommendations

- `REC-20` — State a **containment principle**: mode differences are confined to an identity adapter boundary; **domain code must never branch on deployment mode.** *Why: this single sentence is what makes the dual-mode cost bounded and reviewable rather than diffuse — it converts a policy into something a code reviewer can enforce.*
- `REC-21` — Restate the invariant precisely: *"Complaint business rules and the case state machine are mode-independent. Identity source, organization resolution, and scope derivation are mode-dependent."* *Why: the current wording is not defensible and an imprecise invariant is worse than none, because it will be quoted.*
- `REC-22` — Expand follow-up actions to name every affected security document (`M-18`).

---

## 9. Integration Readiness

### Strengths

- `S-22` — Reference-only organization data is the correct integration posture and matches ADR-002.
- `S-23` — The minimum-payload approach keeps the contract small and gives the ADR a defensible integration surface even before protocol selection.
- `S-24` — The Open Questions list is honest and reasonably complete. Naming unknowns is better practice than the false precision of pretending them resolved.

### Weaknesses

- `W-22` — **No integration contract artifact.** The repository operates catalog-first (`07 API Catalog`, `08 Event Catalog`, `09 Integration Catalog`, and the G2 gate principle). ADR-014 introduces the most significant external integration in the system's history and produces no catalog entry, no contract identifier, and no owner.
- `W-23` — **Target org model does not exist locally.** The payload specifies `organization_id`, `branch_id`, `department_id`. The implemented schema has `branches` only — **no `organizations` table, no `departments` table** — while `DataScope` already supports an `ORGANIZATION` scope type resolved from string `scope_value`. The ADR describes a three-level hierarchy that is currently one level, and does not record the gap.
- `W-24` — No **claim contract versioning**. What ECMP does on an unknown claim, a missing required claim, or a payload version bump is undefined.

### Missing Considerations

- `M-19` — No integration test strategy against a contract that does not yet exist; `13 Test Strategy` is unreferenced.
- `M-20` — No position on whether identity propagates into ECMP's **event payloads** (ADR-001 domain events) and, if so, in what form.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-18` | Implementation proceeds against an undocumented, unversioned identity contract | High | High without `REC-12` |
| `RISK-19` | Org hierarchy depth mismatch discovered mid-implementation | Medium | High |

### Recommendations

- `REC-23` — Register the enterprise identity integration in `09 Integration Catalog` with an ID and owner as a condition of acceptance. *Why: catalog-first is an existing repository rule; exempting the largest integration from it sets the wrong precedent.*
- `REC-24` — Record the org-model gap (`W-23`) in the ADR's consequences so it is discovered now rather than during implementation.
- `REC-25` — Require the identity contract to be **explicitly versioned** with a stated fail-closed rule for missing required claims.

---

## 10. Operational Risk

### Strengths

- `S-25` — Dependency on Enterprise Identity availability is named rather than hidden.
- `S-26` — HA for the Identity Provider appears in Open Questions — the right concern, flagged early.

### Weaknesses

- `W-25` — Naming the availability dependency is not managing it. There is no RTO/RPO expectation, no degraded-mode definition, no incident ownership across the two systems.
- `W-26` — **No break-glass access** (`M-11`). An IdP outage in Enterprise Mode means no administrative access to ECMP — including the access needed to manage the consequences of the outage.
- `W-27` — **Cutover from Standalone to Enterprise is the highest-risk transition in this decision and is not designed.** Existing local users have no `external_user_id`. Linking them (claim-by-email once? admin-approved mapping? pre-seeded correlation?) determines whether historical complaint attribution survives. "Future migration path" is asserted; it is the item most likely to fail.
- `W-28` — No operational ownership boundary. When login fails, which team owns the incident? Cross-boundary triage without a defined split is a reliable source of prolonged outages.

### Missing Considerations

- `M-21` — `15 Operations Runbook` is unreferenced despite this decision materially changing operations.
- `M-22` — No monitoring position on the identity dependency (validation failure rate, JIT provisioning rate, claim anomalies) — the last of which is a security signal, not merely an operational one.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-20` | IdP outage → complete ECMP unavailability with no administrative recourse | Critical | Medium |
| `RISK-21` | Standalone→Enterprise cutover breaks historical actor attribution | High | High without a designed linking strategy |
| `RISK-22` | Cross-boundary incidents with undefined ownership | Medium | High |

### Recommendations

- `REC-26` — Require a **cutover / identity-linking strategy** as a named follow-up ADR before any Enterprise Mode implementation. *Why: this is the highest-likelihood high-impact item in the entire review, and it is currently a single unelaborated sentence.*
- `REC-27` — Define degraded-mode behaviour and the operational ownership split, and require a runbook update in `15 Operations Runbook`.
- `REC-28` — Require monitoring of token validation failures, JIT provisioning rate, and claim anomalies.

---

## 11. Long-term Enterprise Evolution

### Strengths

- `S-27` — The decision is **strategically correct and will age well.** Consuming enterprise identity rather than implementing it is the posture that lets ECMP survive as one of N modules.
- `S-28` — Protocol-agnostic framing means the ADR does not expire when the protocol choice is made.
- `S-29` — "Business modules shall consume Enterprise Identity rather than implement Enterprise Authentication" is reusable as a platform-wide principle beyond ECMP — arguably its most valuable sentence for the wider platform.
- `S-30` — Retaining authorization internally keeps complaint domain evolution independent of the platform's release cadence. This is the correct long-term coupling choice and is easy to get wrong in the other direction.

### Weaknesses

- `W-29` — The ADR is scoped as an ECMP decision but states **platform-wide principles**. If it genuinely governs all business modules, ECMP's ADR set is the wrong home and the wrong authority; a platform-level architecture principle is needed, with ADR-014 referencing it.
- `W-30` — No **reverse-migration** consideration. If the Enterprise Platform is cancelled, descoped, or delayed, what is ECMP's position? Mode A provides the technical answer; the ADR does not state it as a deliberate hedge, which is a missed opportunity since it is a genuine strength of the dual-mode design.

### Missing Considerations

- `M-23` — No stated **evolution path for the identity contract** as the platform adds modules with richer claim needs.
- `M-24` — No position on whether ECMP's own complaint roles eventually federate upward (enterprise-managed role assignment) — a natural pressure once several modules each own their own mapping tables.

### Risks

| ID | Risk | Impact | Likelihood |
|---|---|---|---|
| `RISK-23` | Enterprise Platform delayed/cancelled; ECMP roadmap stranded | High | Low–Medium |
| `RISK-24` | Platform-wide principles set unilaterally in a module-level ADR | Medium | Medium |

### Recommendations

- `REC-29` — Either narrow the ADR to ECMP's own boundary, or **promote the platform-wide principles to a platform architecture principle document** that ADR-014 references. *Why: a module cannot bind its peers, and principles asserted from the wrong altitude are ignored by the modules they are meant to govern.*
- `REC-30` — State Mode A explicitly as the **strategic hedge** against `RISK-23`. *Why: it reframes the dual-mode maintenance cost (`W-19`) as a deliberately purchased option rather than an accident, which is both more honest and more defensible at Board level.*

---

## 12. Findings on Areas of Special Attention

| Topic | Assessment | Verdict |
|---|---|---|
| **Separation of AuthN vs AuthZ** | Correct and well-stated. Boundary leaks only via org hierarchy as an authorization input (`W-11`). | ✅ Correct, one gap |
| **Enterprise Platform ownership** | Correct scope. Password/MFA/session/directory/org placement is right. | ✅ Correct |
| **ECMP ownership** | Correct. Complaint domain plus its own authorization is the right retained scope. | ✅ Correct |
| **User Profile model** | Right shape (thin, module-specific), but `external_user_id` unspecified, referential anchoring undecided, conflicts with implemented `users` constraints. | ⚠️ Incomplete |
| **Organization ownership** | Correct in principle. Understated as reference data when it is an authorization input; local org model gap unrecorded. | ⚠️ Understated |
| **Just-In-Time Provisioning** | **Insufficient.** Covers create only. No leaver, no attribute drift, no reactivation, no cutover linking, no entitlement gate. | ❌ Insufficient |
| **Standalone vs Enterprise mode** | Sound product decision. Under-weights maintenance cost; overreaching behavioural-equivalence claim; interacts unclearly with `ECMP_AUTH_MODE`. | ⚠️ Needs tightening |
| **Future migration path** | Asserted, not designed. Highest-risk unaddressed item. | ❌ Not designed |

### Just-In-Time Provisioning — expanded finding

JIT as specified is a **create-only** flow. Four lifecycle events are unaddressed:

1. **Leaver / deprovisioning.** `employment_status` is collected but never used. A departed user retains an ECMP profile and role indefinitely; ECMP is never notified. This is a standard access-recertification audit finding.
2. **Attribute drift.** Branch or department transfer changes data-scope entitlement. If the profile is written only on first sight, the user silently retains access to their former unit's complaints — a *live authorization defect*, not a data-staleness annoyance.
3. **Reactivation / rehire** and identifier reuse.
4. **Orphan and merge.** Existing local users have no `external_user_id`; cutover linking is undesigned (`W-27`).

The correction is small and does not constitute a redesign:

- `REC-31` — Keep JIT as the **create** path; add **idempotent refresh of mutable claims on every authentication** (branch, department, display name, employment status). *Why: closes attribute drift at effectively zero cost, since the claims are already present in the token on every request.*
- `REC-32` — Define an **explicit deactivation trigger**: `employment_status ≠ active` → local status inactive and ECMP role revoked at next authentication, with audit. *Why: `employment_status` is already in the required payload; not acting on it means collecting the data and ignoring it.*
- `REC-33` — Register **periodic reconciliation** against the enterprise directory as a follow-up decision, to catch users who simply stop appearing (the leaver case that login-time refresh cannot detect). *Why: login-time refresh is necessary but structurally cannot observe absence.*

---

## 13. Consolidated Blocking Items

The following must be resolved before Status moves to Accepted:

| # | Item | Reference |
|---|---|---|
| B-1 | Entitlement gate — remove default-allow provisioning | `REC-06` |
| B-2 | Disposition of implemented local credential surface under Enterprise Mode | `REC-05` |
| B-3 | JIT lifecycle beyond create (refresh, deactivate, reconcile) | `REC-31`–`REC-33` |
| B-4 | Explicit supersession relationship to ADR-007 / ADR-012 | `REC-01` |
| B-5 | `external_user_id` semantics and referential anchoring | `REC-07` |
| B-6 | Org synchronization reclassified as authorization dependency | `REC-13` |
| B-7 | Cutover / identity-linking strategy as named follow-up ADR | `REC-26` |
| B-8 | ADR template conformance and Security Architect review | `REC-02` |

Non-blocking recommendations (`REC-03`, `REC-04`, `REC-08`–`REC-12`, `REC-14`–`REC-25`, `REC-27`–`REC-30`) should be incorporated into v1.1 or registered as follow-up decisions.

---

## 14. Reviewer Statement

ADR-014 makes the right call. The boundary between Enterprise Platform and ECMP is drawn in the correct place, the authentication/authorization split is appropriate, and the refusal to let enterprise roles become ECMP roles demonstrates real IAM judgement. The document's weaknesses are weaknesses of **completeness and conformance**, not of direction — which is the better failure mode for an ADR at this stage.

The eight blocking items are all completions of decisions ADR-014 already implies. None requires reopening the boundary question.

---

## Verdict

**APPROVED WITH CHANGES**

---

## Related

- `05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.0.md` (subject)
- `05 Architecture Decision Records/` — ADR-002, ADR-007, ADR-008, ADR-012
- `10 Security and Access Standards/` — SEC-AUTH-001, SEC-RBAC-FLOW-001, SEC-IAM-CACHE-001, SEC-PWD-001, `ECMP_Threat_Model_v0.1.md`
- `18 Architecture Governance/README.md` — RACI, ADR lifecycle, quality gates
- `18 Architecture Governance/reviews/REVIEW_CHECKLIST.md`, `ARCHITECTURE_REVIEW_FORM.md`
- `24 Templates/ADR_TEMPLATE.md`
