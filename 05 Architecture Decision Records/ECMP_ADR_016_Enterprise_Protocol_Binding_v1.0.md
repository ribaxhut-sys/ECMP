# ECMP_ADR_016_Enterprise_Protocol_Binding_v1.0

| Field | Value |
|---|---|
| ID | ADR-016 |
| Version | 1.0 |
| Owner | Security Architect |
| Reviewer | Solution Architect / Architecture Board |
| Approver | Architecture Board |
| Status | 🟢 Approved (Accepted with Conditions — PROGRAM-BOARD-006) |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |

- ADR Status: **Accepted with Conditions** (PROGRAM-BOARD-006 **BR-011**)
- Board Disposition: **Accepted with Conditions** — conditions **C-B6-1**…**C-B6-7** apply. Mode B / Batch-2 / Enterprise customer remain **CLOSED** (C-B6-1 / PROGRAM-BOARD-004 C-7). Resolution: `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`
- Prior dispositions (historical): Proposed; PROGRAM-BOARD-005 Ready for Resolution — superseded as *active* disposition by BR-011
- Date: 2026-07-30
- Program: **PROGRAM-ENTERPRISE-002** — Enterprise Protocol & Binding ADR
- Decision Owners: Security Architect, Solution Architect
- Related Domains: Core Platform, ECMF (Complaint Management), Administration, Notification, Dashboard & Analytics, KPI & Performance
- Related ADRs: ADR-002, ADR-007, ADR-008, ADR-012, ADR-013, ADR-014, ADR-015
- Related decisions: DEC-020; PROGRAM-BOARD-004 (BR-009 / BR-010); PROGRAM-BOARD-005; PROGRAM-BOARD-006 (BR-011 / BR-012 / BR-013)
- Baseline (governance): ADR-014 v1.4 and ADR-015 v1.3 **Accepted with Conditions** (PROGRAM-BOARD-004); this ADR **Accepted with Conditions** (PROGRAM-BOARD-006); Mode B / Batch-2 / Enterprise customer remain **CLOSED** (C-7 / C-B6-1)

## Purpose

This ADR defines **HOW** enterprise identity is conveyed to and cryptographically validated by ECMP under Mode B.

It does **not** define **WHAT** identity contains. Claim ownership, required/optional claims, claim semantics, and bilateral contract rules remain the sole Source of Truth of **ADR-015** (Enterprise Identity Contract v1.0).

## Terminology

Terms are identical to ADR-014 / ADR-015 unless refined below.

| Term | Meaning |
|---|---|
| **Identity Contract (ADR-015)** | Bilateral contract of identity *content* between Enterprise Platform and ECMP. Canonical claim names and fail-closed claim rules. |
| **Protocol family** | A standards family capable of authenticating a subject and presenting verifiable assertions (for example OIDC, OAuth 2.0, SAML 2.0). |
| **Binding** | The governed mapping from a protocol family’s wire representation (token/assertion fields, headers, discovery metadata) onto ADR-015 canonical claims, plus the validation controls (`iss`, `aud`, signature, lifetime) that establish trust in that presentation. |
| **Presentation** | The concrete credential or assertion presented to ECMP on a request or session establishment (for example a bearer access token or SAML assertion). |
| **Identity Adapter** | ECMP boundary component (ADR-014) that terminates Mode A / Mode B divergence: consumes presentation, validates binding controls, maps wire → ADR-015 claims, applies Entitlement Gate, correlates local profile. |
| **Issuer (Mode B)** | The Enterprise Platform–owned authority that authenticates the subject and issues presentations intended for ECMP consumption. |
| **Audience (Mode B)** | The intended ECMP recipient(s) of a presentation. Audience isolation prevents “one login opens every module.” |

---

## 1. Context

ADR-014 establishes that under **Mode B (Enterprise)**:

- Enterprise Platform owns Authentication and Enterprise Identity.
- ECMP is a Business Module that consumes identity.
- Mode divergence terminates at the **Identity Adapter**.

ADR-015 establishes the **Bilateral Identity Contract** (PROGRAM-BOARD-004 C-3): what claims must be present, what they mean, and that missing required claims deny access.

ADR-014 / ADR-015 explicitly **deferred** protocol selection, credential format, transport, `aud` / `iss` validation, key management, and wire-name mapping to a protocol / binding ADR.

Without that ADR:

- Implementers may invent incompatible conveyance assumptions.
- Audience / issuer isolation may be omitted (“one token opens everything”).
- Wire fields from ADR-012-era models (`sub`, `roles[]`, `orgUnitId`) may silently redefine Mode B claim SoT.
- Mode B AuthN coding or OpenAPI `securitySchemes` may start before trust controls are decided.

PROGRAM-BOARD-004 (F-5) requires this protocol / binding ADR before Mode B AuthN implementation may be authorized. **Creating this ADR does not unlock Mode B** (C-7 remains in force).

## 2. Problem Statement

If conveyance and trust validation are undefined:

1. ECMP cannot know which protocol families are eligible for Mode B presentations.
2. Trust boundaries between Enterprise Platform AuthN and ECMP Identity Adapter remain ambiguous.
3. Issuer and audience responsibilities are unenforceable.
4. Token / assertion validation lifecycle (signature, expiry, clock skew, key rotation) is ad hoc.
5. Protocol evolution can break ECMP without a versioning rule.
6. Binding ownership (who maps wire → ADR-015) may duplicate or contradict the bilateral contract.
7. Failure modes may fail open.

## 3. Decision Drivers

- Preserve ADR-015 as claim SoT; this ADR is subordinate for conveyance only.
- Preserve ADR-014 Identity Adapter containment (business modules remain mode-independent).
- Enforce fail-closed trust and claim validation under Mode B.
- Remain **implementation-agnostic**: define protocol *families* and binding *rules*, not a product (no IdP vendor selection here).
- Preserve ADR-012 as Accepted Mode A / shared-environment target AuthN without silent supersession (relationship disposition remains Board-owned).
- Keep Mode B / Batch-2 / Enterprise customer **CLOSED** until separate Board unlock after this ADR is Accepted **and** implementation is separately authorized.
- Align with ADR-008: presentations must not embed ECMP permissions as SoT.

## 4. Options Considered

### Option A — Embed protocol inside ADR-015

- Pros: one document.
- Cons: couples durable identity content to replaceable conveyance; rejected by ADR-015 Alternative B.
- Verdict: **Rejected.**

### Option B — Select a single protocol product now (for example Keycloak-only Mode B)

- Pros: fastest path to a concrete build.
- Cons: premature vendor lock; conflates Mode A ADR-012 baseline with Mode B enterprise conveyance; violates “families without selecting implementation.”
- Verdict: **Rejected** for this ADR.

### Option C — Protocol-family architecture + binding rules; product deferred (chosen)

- Pros: decides trust, `iss`/`aud`, validation lifecycle, key ownership, versioning, and fail-closed behavior; allows OIDC/OAuth2/SAML (and future families) under one binding discipline; keeps ADR-015 untouched.
- Cons: one more ADR before coding; requires a later implementation-selection decision.
- Verdict: **Accepted** as the architecture approach of this ADR.

---

## 5. Decision

ECMP adopts an **Enterprise Protocol & Binding** architecture for Mode B identity conveyance as follows.

### Decision Summary

1. **Supported protocol families** are declared (standards families), **without** selecting an IdP product or runtime implementation.
2. A **Binding** maps any allowed family’s wire presentation onto **ADR-015** canonical claims.
3. **Trust** is established by cryptographic validation of the presentation plus mandatory **issuer** and **audience** checks.
4. Validation and claim acceptance are **fail-closed**.
5. **Binding ownership** sits at the ECMP **Identity Adapter** for consumption/mapping; **Issuer** ownership sits with the **Enterprise Platform**.
6. This ADR does **not** unlock Mode B, Batch-2, Enterprise customer, OpenAPI `securitySchemes`, JWT coding, or OD-FE-002 implementation.

### What this ADR decides vs does not decide

| Decides (HOW) | Does not decide (out of scope) |
|---|---|
| Eligible protocol families | Concrete IdP product / vendor |
| Trust boundary & validation lifecycle | ADR-015 claim set changes |
| Issuer / audience / key-management responsibilities | Entitlement payload representation (ADR-014 follow-up) |
| Protocol versioning & binding ownership | Mode A local auth redesign |
| Fail-closed failure behavior | OpenAPI securitySchemes text |
| Future compatibility rules | Mode B implementation authorization |

---

## 6. Architecture Principles

1. **Content vs conveyance separation** — ADR-015 owns *what*; this ADR owns *how*. Protocol ADRs must not redefine canonical claim semantics.
2. **Bilateral contract remains binding** — Enterprise Platform must issue presentations that can be mapped to ADR-015; ECMP must reject presentations that cannot (PROGRAM-BOARD-004 C-3).
3. **Standards over products** — Couple to protocol-family interfaces (discovery, keys, assertion validation), not to a vendor API.
4. **Audience isolation** — A presentation accepted for ECMP must be intended for ECMP (or an explicitly governed ECMP audience set). Cross-module token reuse without audience check is prohibited.
5. **Issuer authenticity** — Only configured Enterprise Platform issuer(s) are trusted.
6. **Fail closed** — Any trust, mapping, or required-claim failure denies access.
7. **Identity Adapter containment** — Protocol divergence terminates at the Identity Adapter; complaint domain services must not branch on protocol family.
8. **No permission SoT in presentations** — Wire may carry informational enterprise role labels; ECMP permissions remain Core Platform SoT (ADR-008) after ADR-014 Entitlement Gate + Complaint Roles mapping.
9. **Mode B remains gated** — Acceptance of this ADR (when Board Accepts) is necessary but not sufficient to unlock Mode B implementation.
10. **No silent supersession** — This ADR does not supersede ADR-007, ADR-012, or ADR-013.

---

## 7. Supported Protocol Families

The following **standards families** are eligible for Mode B identity presentation to ECMP, subject to a governed Binding that maps wire → ADR-015:

| Family | Typical presentation | Eligibility note |
|---|---|---|
| **OpenID Connect (OIDC)** | OIDC-derived access token / ID token used per binding profile | Preferred family for interactive user AuthN patterns |
| **OAuth 2.0** | Bearer access token (including `client_credentials` for services when separately profiled) | Eligible when token content can be mapped to ADR-015 (user) or to a future service-identity profile (deferred) |
| **SAML 2.0** | SAML Assertion | Eligible when assertion attributes map to ADR-015 under a governed Binding |
| **Future standards family** | As Board-approved | Only via additive revision of this ADR (or a superseding protocol ADR) — not by local invention |

### Family selection rules (normative)

1. ECMP **SHALL NOT** hard-require a single product implementation in application code architecture.
2. A deployment **MAY** choose one primary family for Mode B operation.
3. Multi-family support is an operational choice; each enabled family **MUST** have an explicit Binding profile (wire → ADR-015).
4. **Selecting Keycloak, Entra ID, Okta, or any other IdP product is deferred** (see Deferred Decisions). ADR-012’s Keycloak baseline remains a **Mode A / shared-environment target** decision and is **not** automatically the Mode B Enterprise Platform issuer.

### Explicit non-selection

This ADR does **not** choose:

- IdP vendor or distribution
- Token signing algorithm product defaults beyond “asymmetric, rotatable, publicly verifiable keys”
- Browser redirect UX / PKCE library
- Gateway vs in-process validation topology

---

## 8. Trust Model

### 8.1 Trust Boundary

```
[ Enterprise Platform ]
  AuthN + Identity SoR + Issuer of presentations
           |
           |  presentation (token / assertion)
           |  + discovery / JWKS or equivalent key material
           v
[ ECMP Trust Boundary — Identity Adapter ]
  1) Cryptographic validation of presentation
  2) Issuer (iss) allowlist check
  3) Audience (aud) isolation check
  4) Lifetime / replay controls per binding profile
  5) Wire → ADR-015 canonical claim mapping
  6) ADR-015 required-claim / fail-closed enforcement
  7) Entitlement Gate (ADR-014) — existence decided; representation deferred
  8) Local profile correlation (external_user_id)
           |
           v
[ Core Platform AuthZ SoT (ADR-008) + ECMP Complaint Roles mapping ]
  Business modules (mode-independent)
```

**Inside ECMP trust boundary:** Identity Adapter validation outcomes, local projections, module audit, Role-Permission enforcement.

**Outside ECMP trust boundary:** Enterprise password/MFA, enterprise user directory SoR, enterprise identity audit SoR, issuer key custody (Enterprise Platform–owned).

### 8.2 Trust anchors

| Anchor | Requirement |
|---|---|
| Issuer identity | Explicit configured issuer identifier(s); no “any JWT” acceptance |
| Key material | Retrieved from issuer-controlled key publication (for example JWKS URI for JWT families; SAML metadata/certs for SAML) |
| Audience | Explicit configured audience value(s) for ECMP |
| Time | Validated `exp` / `nbf` (or SAML `NotOnOrAfter` / `NotBefore`) with bounded clock skew |
| Mapping completeness | After trust validation, presentation must map to all ADR-015 **required** claims |

### 8.3 Security assumptions

1. Enterprise Platform issuer is operated under enterprise security controls commensurate with identity SoR risk.
2. ECMP runtime can reach issuer key publication endpoints (or a governed cache/replica of those keys) under Mode B.
3. Transport between client and ECMP APIs uses confidential channels in shared/production environments (TLS); this ADR does not redesign network architecture.
4. ECMP does not become an IdP under Mode B (ADR-014 Local Auth Prohibition).
5. Attackers may present arbitrary bearer tokens; ECMP must not trust unsigned or wrongly-keyed material.
6. Compromise of a single module audience must not automatically authorize other modules (audience isolation).
7. ADR-015 bilateral obligations hold independently of which protocol family is used.

---

## 9. Responsibilities

### 9.1 Issuer responsibilities (Enterprise Platform)

| Responsibility | Requirement |
|---|---|
| Authenticate subject | Perform AuthN before issuing Mode B presentations intended for ECMP |
| Issue for intended audience | Include ECMP audience value(s) required by the Binding profile |
| Identify issuer | Populate stable issuer identifier consistent with ECMP allowlist |
| Supply mappable identity | Ensure presentation content can be mapped to ADR-015 required claims (bilateral contract) |
| Publish keys / metadata | Provide rotatable verification material (JWKS / SAML metadata) |
| Lifecycle signals | Support revocation or short-lived credentials per chosen family profile (detailed profile deferred) |
| Contract versioning cooperation | When conveying `identity_contract_version` (optional in ADR-015), do not assert unsupported contract versions to ECMP |

### 9.2 Binding / consumer responsibilities (ECMP Identity Adapter)

| Responsibility | Requirement |
|---|---|
| Validate cryptography | Verify signature / assertion integrity using trusted keys |
| Enforce issuer allowlist | Reject unknown / mismatched issuer |
| Enforce audience | Reject missing/mismatched audience |
| Enforce lifetime | Reject expired / not-yet-valid presentations |
| Map wire → ADR-015 | Apply governed field mapping; do not treat wire names as claim SoT |
| Enforce ADR-015 | Deny on missing/invalid required claims; ignore unknown optional claims per ADR-015 |
| Deny unsafe mode combos | Fail-fast if Mode B enabled with local credential routes or `dev` auth (ADR-014 mode matrix) |
| Containment | Do not push protocol branching into complaint domain services |

### 9.3 Binding ownership

| Concern | Owner |
|---|---|
| ADR-015 claim semantics | ADR-015 (Bilateral Contract) — **not** this ADR |
| Protocol family eligibility & trust controls | **This ADR (ADR-016)** |
| Wire-name → ADR-015 mapping tables | **Binding profiles** owned under this ADR’s governance; maintained by Security Architect / Solution Architect; change-controlled |
| IdP product selection | **Deferred** Board/Security decision |
| Entitlement representation | **Deferred** (ADR-014 open question) |
| Role-Permission SoT | Core Platform (ADR-008) |
| Complaint Roles mapping after entitlement | ECMP Business Module (ADR-014) |

**Normative:** Binding profiles are subordinate artifacts. They may rename wire fields; they must not change ADR-015 cardinality, key rules (`external_user_id`), or fail-closed claim semantics.

**Subordination standard (normative — applies to all Mode B subordinate profiles):**  
Any **binding profile**, **entitlement representation profile**, or **organization sync integration profile** is subordinate to its parent ADR and to ADR-015/008/014 SoT boundaries. Subordinate profiles **MUST NOT**:

1. loosen or bypass fail-closed AuthN / claim / entitlement / org-resolvability rules;
2. introduce default-allow, silent unscoped AuthZ, or “degraded allow” without an explicit **Architecture Board** decision recorded in a Board Resolution that cites the parent ADR;
3. rewrite ADR-015 claim cardinality/semantics or ADR-008 permission catalogs.

This §9.3 standard is the cross-ADR reference for ADR-017 §13 and ADR-018 §15 (audit K-5).

---

## 10. Audience Validation

1. Every Mode B presentation accepted by ECMP **MUST** carry an audience identifier applicable to ECMP.
2. ECMP **MUST** configure an allowlist of accepted audience values (exact match unless a future profile defines an explicit multi-audience array rule).
3. Missing audience, empty audience, or audience outside the allowlist → **deny** (fail closed).
4. **Per-module isolation principle:** ECMP audience values must not be shared with unrelated enterprise modules unless Architecture Board explicitly approves a multi-audience profile and records the risk.
5. Successful AuthN at the Enterprise Platform **does not** imply ECMP authorization. Audience validation is necessary but not sufficient; Entitlement Gate (ADR-014) and ADR-008 permission checks still apply.

---

## 11. Issuer Validation

1. ECMP **MUST** configure an allowlist of trusted issuer identifiers.
2. Presentation issuer **MUST** match the allowlist (exact match to configured issuer string(s)).
3. Issuer mismatch / absence → **deny**.
4. Issuer configuration changes are security-sensitive and require change control (Security RACI).

---

## 12. Token / Assertion Validation Lifecycle

The following lifecycle is normative for JWT-like families and must be mirrored by equivalent steps for SAML (integrity → issuer → audience → time → map → contract).

| Step | Check | On failure |
|---|---|---|
| L1 | Presentation present in the agreed location (for example `Authorization: Bearer`) | Deny (unauthenticated) |
| L2 | Cryptographic integrity (signature / assertion signature) using current trusted keys | Deny |
| L3 | Issuer allowlist | Deny |
| L4 | Audience allowlist | Deny |
| L5 | Time validity (`exp`/`nbf` or SAML NotOnOrAfter/NotBefore) within skew budget | Deny |
| L6 | Algorithm / key type allowlist (reject `none`, reject unexpected alg) | Deny |
| L7 | Wire → ADR-015 mapping produces required claims | Deny |
| L8 | ADR-015 semantic / cardinality checks | Deny |
| L9 | Entitlement Gate (existence per ADR-014; representation deferred) | Deny if entitlement absent/invalid when Mode B requires it |
| L10 | Proceed to Core Platform permission resolution / Complaint Roles mapping | 403 if authenticated but unauthorized |

### Cached key material

- ECMP **MAY** cache issuer keys / metadata to survive transient issuer publication outages.
- Cache refresh and key rotation handling are mandatory design concerns for implementation profiles.
- **Degraded mode (normative intent):** existing locally accepted sessions/presentations that still pass L1–L8 may continue until natural expiry; **new** presentations that cannot be verified after key-cache exhaustion **fail closed**. This ADR does not authorize a signature-bypass break-glass.

### Replay

- Baseline assumes short-lived bearer presentations; mandatory server-side replay cache is **deferred** unless a binding profile for a specific family requires it (for example certain SAML profiles).
- Refresh-token handling, if any, is an Enterprise Platform / client concern; ECMP APIs consume access presentations only unless a future profile says otherwise.

---

## 13. Key Management Responsibilities

| Responsibility | Enterprise Platform (Issuer) | ECMP (Identity Adapter) |
|---|---|---|
| Generate signing keys | Own | Do not generate issuer keys |
| Publish verification keys / metadata | Own | Consume only |
| Rotate keys | Own; publish overlapping keys during rotation windows | Accept multiple concurrent keys from publication |
| Revoke compromised keys | Own | Stop trusting removed keys after refresh |
| Store private signing keys | Own (never ship to ECMP) | N/A |
| Pin / configure key source URI or metadata | Provide stable publication endpoint | Configure trusted publication source + issuer allowlist |
| Local `dev` keys | Not used for Mode B | Mode B + dev keys / local credential routes = invalid (ADR-014) |

---

## 14. Protocol Versioning

| Layer | Versioning rule |
|---|---|
| **Identity Contract** | Versioned by ADR-015 (`identity_contract_version` optional claim; contract v1.0 current). Protocol must not bump contract version silently. |
| **This ADR (protocol & binding architecture)** | Document version (this file). Breaking trust-rule changes require Board review. |
| **Binding profile** | Named, versioned mapping artifact (for example `binding-oidc-ecmp-v1`) subordinate to this ADR. |
| **Protocol family standards** | OIDC/OAuth/SAML standard versions as constrained by the binding profile. |

### Compatibility

1. Additive optional wire fields that map to ADR-015 optional claims are non-breaking for ECMP.
2. Removing a wire field required to populate an ADR-015 required claim is **breaking** and must fail closed until mapping/issuer is fixed.
3. Changing audience or issuer identifiers is a coordinated security change (both parties).
4. Introducing a new protocol family requires an update to §7 (or superseding ADR), plus a new binding profile — not a silent code path.

---

## 15. Failure Behavior (Fail Closed)

| Condition | Required behavior |
|---|---|
| Missing presentation | Deny (unauthenticated) |
| Invalid signature / integrity | Deny |
| Unknown issuer | Deny |
| Audience mismatch | Deny |
| Expired / not-yet-valid | Deny |
| Cannot map to ADR-015 required claims | Deny |
| ADR-015 required claim missing/invalid | Deny (per ADR-015) |
| Entitlement absent when required by Mode B gate | Deny (per ADR-014) |
| Mode B + local login / `dev` mode | Fail-fast configuration denial (ADR-014) |
| Unknown optional wire fields | Ignore after trust validation (do not deny solely for unknowns) |
| Issuer key publication temporarily unavailable | Use valid cache if present; otherwise deny new verifications (no signature bypass) |

ECMP **MUST NOT**:

- Invent default `external_user_id`, org hierarchy claims, or employment status
- Accept unsigned presentations in Mode B
- Treat email as identity key
- Collapse AuthN success into AuthZ success

---

## 16. Future Compatibility

1. **IdP swap / brokering** — Changing Enterprise Platform issuer product must preserve issuer/audience/key-publication contracts or be accompanied by coordinated ECMP config change.
2. **Additional protocol families** — Allowed only through governed ADR/profile updates.
3. **Service-to-service identity** — Recognized as required future profile; not authorized by this ADR’s user-identity baseline.
4. **Break-glass** — Must be a designed, audited, time-boxed path in a future Security decision; must not reuse residual Mode A password endpoints as Mode B bypass (ADR-014 / prior review posture).
5. **OD-FE-002** — Browser/auth bridge remains downstream; this ADR supplies protocol constraints but does **not** close OD-FE-002 or authorize FE Mode B AuthN UI.
6. **Shared audit correlation** — If the presentation carries a correlation identifier, binding profiles may map it; choice of correlation scheme remains deferred (ADR-015) unless Board assigns it here in a later revision.

---

## 17. Relationship to Existing ADRs

| ADR | Relationship |
|---|---|
| ADR-015 | **Constrains / Consumes** — claim SoT; this ADR maps conveyance onto it |
| ADR-014 | **Complementary** — Identity Adapter hosts binding validation; Entitlement Gate remains; Mode B unlock still gated |
| ADR-008 | **Constrains** — no permission SoT in tokens |
| ADR-002 | **Consistent** — ECMP not SoR for enterprise identity |
| ADR-013 | **Orthogonal** — remains active (BR-007) |
| ADR-007 | **Relationship Pending (Board)** — Mode A slice/target applicability proposals in ADR-014/015 unchanged by this ADR |
| ADR-012 | **Relationship Pending (Board)** — Accepted Mode A / shared-env target AuthN. Historical claim vocabulary is **not** Mode B SoT. Wire mapping from ADR-012-era fields to ADR-015 requires binding profile + Board relationship disposition. This ADR **does not** supersede ADR-012 |
| DEC-020 | **Unchanged** — dual complaint SoT; no Mode B/Batch-2/enterprise-customer unlock |
| PROGRAM-BOARD-004 | **Baseline** — Accept With Conditions for ADR-014/015; C-7 gates remain CLOSED |

---

## 18. Deferred Decisions

| ID | Deferred item | Why deferred | Unblocks when decided |
|---|---|---|---|
| D-01 | Concrete IdP product for Enterprise Platform Mode B issuer | Implementation selection ≠ architecture of families | Implementation design; still needs Mode B unlock |
| D-02 | Exact Binding profile tables (OIDC wire names → ADR-015) | Requires issuer claim catalog from Enterprise Platform | Identity Adapter detailed design |
| D-03 | Service-to-service Mode B identity profile | Distinct threat model | Machine authn |
| D-04 | Entitlement payload representation | Owned as ADR-014 follow-up | Entitlement Gate implementation |
| D-05 | Mandatory replay cache / denylist | Family-specific | High-assurance profiles |
| D-06 | Break-glass Mode B path | Security design package | Ops resilience |
| D-07 | Shared audit correlation identifier | ADR-015 deferral | Cross-platform audit join |
| D-08 | Board disposition of ADR-007 / ADR-012 vs Mode B | Explicitly Board-owned | Narrative closure; not required to keep ADR-015 as claim SoT |
| D-09 | Mode B implementation authorization & OpenAPI `securitySchemes` | PROGRAM-BOARD-004 C-7 | Coding / contract edits |
| D-10 | OD-FE-002 browser bridge | Downstream of protocol Accept + FE track | FE Mode B AuthN UX |

---

## 19. Risks

| ID | Risk | Impact | Likelihood without controls | Mitigation in this ADR |
|---|---|---|---|---|
| R-01 | Binding profile redefines ADR-015 claims | Dual SoT / insecure defaults | Medium | Subordination rule; ADR-015 remains claim SoT |
| R-02 | Audience not isolated | Lateral privilege across modules | High | Mandatory audience allowlist |
| R-03 | Treating ADR-012 claims as Mode B SoT | Wrong authorization inputs | High until D-08 | Explicit non-SoT statement; mapping required |
| R-04 | Signature bypass during IdP outage | AuthN compromise | Medium | Cached keys OK; bypass forbidden |
| R-05 | Mode B coding starts on Proposed ADR | Governance violation | Medium | Status Proposed; C-7 CLOSED; non-authorization section |
| R-06 | Local login remains under Mode B | Critical bypass | Medium | Inherit ADR-014 fail-fast matrix |
| R-07 | Entitlement confused with token roles | Permission SoT drift | Medium | ADR-008 + ADR-014 gate ordering |
| R-08 | Multi-family without profiles | Inconsistent validation | Medium | Family requires explicit binding profile |

---

## 20. Consequences

### Positive

- Closes the ADR-014/015 protocol deferral with a Board-reviewable architecture.
- Enables consistent `iss` / `aud` / key / lifecycle rules before any Mode B coding.
- Keeps ADR-015 bilateral contract intact.
- Allows OIDC, OAuth 2.0, and SAML without premature vendor lock.
- Preserves Identity Adapter containment and ADR-008 permission SoT.

### Trade-offs

- Another Accepted ADR (future) is required before Mode B AuthN implementation authorization.
- Binding profiles must still be authored once the Enterprise Platform issuer claim catalog is known.
- ADR-007 / ADR-012 relationship remains Board-pending (not solved silently here).

### Non-consequences (explicit)

- **Mode B remains CLOSED**
- **Batch-2 remains CLOSED**
- **Enterprise customer remains CLOSED**
- No OpenAPI edits
- No JWT / OIDC / SAML implementation
- No redesign of Enterprise Platform or ADR-015 claim tables

---

## 21. Explicit Non-Authorization

Acceptance of this ADR (when/if Board Accepts) **still does not** by itself authorize:

1. Mode B runtime enablement
2. OpenAPI enterprise `securitySchemes` changes
3. JWT/OIDC/SAML coding in `backend/` or `frontend/`
4. OD-FE-002 implementation
5. Batch-2 or enterprise customer production
6. Cutover Mode A → Mode B
7. Supersession of ADR-012 / ADR-007 / ADR-013
8. Entitlement payload final design

Those require separate Board / program authorization after conditions and deferred decisions are addressed.

---

## 22. Follow-ups

- [x] Architecture Board review of **ADR-016** → Accepted with Conditions (PROGRAM-BOARD-006 **BR-011**)
- [x] After Accept: author Binding Profile v1 for the chosen protocol family (D-02) — **Draft** `binding-oidc-ecmp-v0.1` (`10 Security and Access Standards/ECMP_BINDING_PROFILE_OIDC_ECMP_v0.1.md`); EP bilateral confirm pending; still no Mode B unlock
- [ ] After Accept: Board disposition track for ADR-007 / ADR-012 relationship (D-08)
- [ ] After Accept + Mode B authorization (future): OpenAPI `securitySchemes` via `07 API Catalog` only
- [ ] After Accept: OD-FE-002 may be *designed* against this ADR; implementation remains gated
- [ ] Service-to-service profile (D-03)
- [x] Entitlement representation decision (D-04) — **Draft** SEC-ENT-REP-001 published; bilateral confirm pending
- [ ] Break-glass design (D-06)
- [ ] Sync Solution Architecture / Security standards references (editorial mapping only)
- [x] Architecture Board Accept With Conditions (PROGRAM-BOARD-006 **BR-011**) — Mode B remains CLOSED (C-B6-1)

---

## 23. Document History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | PROGRAM-ENTERPRISE-002 — initial Proposed Enterprise Protocol & Binding ADR; families without product selection; Mode B remains CLOSED |
| 1.0a | 2026-07-30 | Audit **K-5** — expand §9.3 subordination standard: subordinate profiles must not loosen fail-closed rules; Board required for any relaxation; cross-ref ADR-017/018 |
| 1.0b | 2026-07-30 | PROGRAM-BOARD-006 **BR-011** — Accepted with Conditions (C-B6-1…C-B6-7); metadata only; Mode B CLOSED |

---

*End of ADR-016 v1.0. Architecture Accept With Conditions — no Mode B unlock; no OpenAPI enterprise securitySchemes authorization.*
