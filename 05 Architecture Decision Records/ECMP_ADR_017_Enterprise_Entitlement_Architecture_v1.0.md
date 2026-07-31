# ECMP_ADR_017_Enterprise_Entitlement_Architecture_v1.0

| Field | Value |
|---|---|
| ID | ADR-017 |
| Version | 1.0 |
| Owner | Solution Architect / Security Architect |
| Reviewer | Architecture Board / Security Architect |
| Approver | Architecture Board |
| Status | 🟢 Approved (Accepted with Conditions — PROGRAM-BOARD-006) |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-30 |

- ADR Status: **Accepted with Conditions** (PROGRAM-BOARD-006 **BR-012**)
- Board Disposition: **Accepted with Conditions** — conditions **C-B6-1**…**C-B6-7** apply. Mode B / Batch-2 / Enterprise customer remain **CLOSED** (C-B6-1 / PROGRAM-BOARD-004 C-7). Resolution: `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`
- Prior dispositions (historical): Proposed; PROGRAM-BOARD-005 Ready for Resolution — superseded as *active* disposition by BR-012
- Date: 2026-07-30
- Program: **PROGRAM-ENTERPRISE-003** — Enterprise Entitlement ADR
- Decision Owners: Enterprise Authorization Architect, Security Architect, Solution Architect
- Related Domains: Core Platform, ECMF (Complaint Management), Administration
- Related ADRs: ADR-002, ADR-008, ADR-012, ADR-013, ADR-014, ADR-015, ADR-016
- Related decisions: DEC-020; PROGRAM-BOARD-004 (BR-009 / BR-010; C-7 gates); PROGRAM-BOARD-005; PROGRAM-BOARD-006 (BR-011 / BR-012 / BR-013)
- Baseline: ADR-014 v1.4 and ADR-015 v1.3 **Accepted with Conditions** (PROGRAM-BOARD-004); ADR-016 v1.0 **Accepted with Conditions** (BR-011); this ADR **Accepted with Conditions** (BR-012); Mode B / Batch-2 / Enterprise customer remain **CLOSED**

## Purpose of this ADR

Define the **Enterprise Entitlement Architecture** governing entitlements consumed by ECMP under Mode B.

This ADR defines **entitlement architecture** only:

- what an enterprise entitlement *is for*
- who owns it
- how it relates to identity, protocol binding, RBAC, and the complaint module
- where it is consumed
- lifecycle and fail-closed behavior
- governance

This ADR does **not** define:

- ECMP permissions (ADR-008)
- Complaint Roles or Complaint Roles mapping tables (ADR-014 ownership)
- Identity claim content (ADR-015)
- Protocol / binding / `iss` / `aud` mechanics (ADR-016)
- JWT claim schemas, OpenAPI, or implementation

---

## Terminology

Aligned with ADR-014 / ADR-015 / ADR-016 unless refined below.

| Term | Meaning |
|---|---|
| **Enterprise Entitlement** | An explicit enterprise-issued grant that a given enterprise subject is allowed to access a named enterprise business module (here: ECMP Complaint module). Entitlement answers “*may this authenticated subject enter this module at all?*” |
| **Enterprise Entitlement Gate** | The ECMP evaluation point (inside the Identity Adapter) that admits or denies module entry based on entitlement presence/validity after identity trust and identity-contract checks succeed (existence decided in ADR-014; architecture elaborated here). |
| **Identity (ADR-015)** | Who the subject is (canonical claims / bilateral identity contract). |
| **Presentation / Binding (ADR-016)** | How identity (and possibly related signals) are conveyed and cryptographically validated. |
| **Complaint Role** | ECMP module role used after the gate for complaint-domain authorization mapping (ECMP-owned per ADR-014). |
| **Permission** | Fine-grained authorization unit in the Role-Permission Matrix SoT (Core Platform, ADR-008). |

---

## 1. Context

ADR-014 decided:

- Under Mode B, Enterprise Platform owns Authentication and Enterprise Identity.
- Access to ECMP requires an **explicit enterprise entitlement** for the Complaint module.
- Enterprise authentication alone must never grant ECMP access.
- Absence of entitlement → deny; no default ECMP role from AuthN success alone.
- **How entitlement is represented and issued** was deferred.

ADR-015 requires denial when enterprise entitlement for the Complaint module is absent, without defining representation.

ADR-016 places Entitlement Gate evaluation at validation lifecycle step **L9**, after trust and ADR-015 mapping, and defers entitlement payload representation (D-04).

Without an Entitlement Architecture ADR:

- Teams may collapse entitlement into identity claims, OIDC roles, or ECMP permissions.
- The gate may be treated as optional.
- Complaint Roles mapping may run before module admission.
- Representation experiments may redefine ADR-015 or ADR-008.

PROGRAM-ENTERPRISE-003 closes the **architecture** gap. Exact on-the-wire representation remains a deferred decision under this ADR’s governance (see §12).

## 2. Problem Statement

If entitlement architecture is undefined:

1. “Authenticated enterprise user” may be treated as “ECMP user.”
2. Ownership of grant/revoke may drift between Enterprise Platform and ECMP.
3. Lifecycle (grant, revoke, suspend, restore) may be inconsistent with identity lifecycle.
4. Trust ordering vs ADR-015 / ADR-016 may be violated.
5. RBAC SoT or Complaint Roles may be overloaded to mean “module admission.”
6. Fail-open defaults may appear (“if entitlement signal missing, allow”).

## 3. Decision Drivers

- Preserve ADR-014 Entitlement Gate existence and AuthN ≠ AuthZ module admission.
- Preserve Identity SoT = ADR-015; Protocol SoT = ADR-016; Permission SoT = ADR-008; Complaint Role ownership = ADR-014.
- Keep entitlement **coarser** than permissions and **distinct** from complaint roles.
- Fail closed.
- Do not unlock Mode B / Batch-2 / enterprise customer (PROGRAM-BOARD-004 C-7).
- Do not redesign ADR-015 / ADR-016 bodies in this task.

## 4. Options Considered

### Option A — Treat successful AuthN + ADR-015 claims as sufficient module access

- Pros: simplest.
- Cons: contradicts ADR-014 gate; every enterprise user becomes an ECMP entrant.
- Verdict: **Rejected.**

### Option B — Encode module admission as ECMP permissions / Complaint Roles only

- Pros: reuses local AuthZ machinery.
- Cons: moves enterprise module-admission SoR into ECMP; blurs Enterprise Platform ownership; invites default role assignment from AuthN.
- Verdict: **Rejected** for the admission decision (permissions/roles remain post-gate).

### Option C — Enterprise-owned entitlement grant + ECMP Entitlement Gate consumption (chosen)

- Pros: matches ADR-014; separates “may enter module” from “what may be done inside”; keeps SoT layers clean.
- Cons: requires enterprise issuance process and a later representation profile.
- Verdict: **Accepted** as architecture.

---

## 5. Decision

ECMP adopts the following **Enterprise Entitlement Architecture** for Mode B.

### Decision Summary

1. **Purpose:** Entitlement is the enterprise module-admission grant for ECMP Complaint.
2. **Ownership:** Enterprise Platform owns entitlement as enterprise truth; ECMP consumes and evaluates it at the Entitlement Gate; ECMP must not invent entitlements as enterprise SoR.
3. **Ordering:** Trust (ADR-016) → Identity Contract (ADR-015) → **Entitlement Gate (this ADR / ADR-014)** → Complaint Roles mapping (ADR-014) → Permissions (ADR-008).
4. **Failure:** Missing, invalid, revoked, or non-applicable entitlement → **deny** (fail closed).
5. **Representation format** (claim name, token field, directory attribute, API check, etc.) is **deferred** but must obey this architecture.
6. This ADR does **not** unlock Mode B implementation.

---

## 6. Purpose of Enterprise Entitlement

Enterprise Entitlement exists to answer a single question:

> Has the Enterprise Platform explicitly granted this enterprise subject access to the **ECMP Complaint** business module?

It is **not** used to answer:

| Question | Answered by |
|---|---|
| Who is the subject? | ADR-015 Identity Contract |
| Is the presentation authentic? | ADR-016 Protocol & Binding |
| What complaint role applies? | ADR-014 Complaint Roles mapping (after gate) |
| What permissions does the role have? | ADR-008 Role-Permission Matrix |
| What complaint business action is allowed by domain rules? | ECMF / complaint FRDs & services |

### Normative purpose statements

1. Entitlement is a **module admission control**, not a permission catalog.
2. Entitlement prevents unintended ECMP access from enterprise-wide authentication alone.
3. Entitlement is **prerequisite** to Complaint Roles mapping and permission enforcement under Mode B.
4. Optional ADR-015 `enterprise_role_codes` (or similar labels) **do not** substitute for entitlement.

---

## 7. Ownership

| Concern | Owner | ECMP role |
|---|---|---|
| Entitlement SoR (who is entitled to which module) | **Enterprise Platform** | Consume only |
| Issuance / grant of entitlement | **Enterprise Platform** | Observe / consume |
| Revocation / suspension of entitlement | **Enterprise Platform** | Observe / consume; deactivate local access use |
| Entitlement Gate evaluation | **ECMP Identity Adapter** | Enforce deny/allow at boundary |
| Local cache / projection of entitlement state (if any) | ECMP (non-authoritative) | Projection only; enterprise truth wins on conflict |
| Complaint Roles mapping | **ECMP Business Module** (ADR-014) | Only **after** gate success |
| Role-Permission Matrix | **Core Platform** (ADR-008) | Enforce after mapping |
| Identity claims | **ADR-015 / Enterprise Platform** | Unchanged by this ADR |
| Protocol binding | **ADR-016** | Unchanged by this ADR |

### Hard rules

1. ECMP must not create enterprise entitlements as enterprise truth.
2. ECMP must not treat AuthN success as implicit entitlement.
3. ECMP must not assign a default Complaint Role solely because identity validated.
4. ECMP may retain local projections for performance/audit but must not promote them above enterprise entitlement state when they disagree.

---

## 8. Lifecycle

Entitlement lifecycle is enterprise-owned. ECMP reacts; it does not author the enterprise grant.

| Lifecycle state / event | Meaning | ECMP required reaction |
|---|---|---|
| **Grant** | Subject becomes entitled to ECMP Complaint module | Gate may allow (subject to identity + trust checks); local profile create/reactivate remains subordinate to gate + ADR-015 |
| **Active** | Entitlement currently valid | Gate allow (if all prior checks pass) |
| **Suspend** | Temporary enterprise denial of module access while identity may still exist | Gate deny; deactivate local ECMP access use |
| **Revoke** | Entitlement permanently removed | Gate deny; deactivate local ECMP access use |
| **Restore / Re-grant** | Entitlement returned after suspend/revoke per enterprise policy | Gate may allow again; local reactivate only for same `external_user_id` per ADR-014/015 |
| **Expiry** (if enterprise uses time-bounded grants) | Entitlement no longer valid after end time | Gate deny |

### Lifecycle coupling (normative)

1. Identity lifecycle (ADR-015 Suspend/Deactivate/Reactivate) and entitlement lifecycle are **related but not identical**.
2. A subject may have valid identity claims and still lack entitlement → **deny**.
3. A subject with revoked entitlement must not retain effective ECMP module admission via stale local projection.
4. Detailed reconciliation cadence (push event vs pull vs login-time only) is deferred (see §12); architecture requires that ECMP be able to deny on entitlement absence at gate evaluation time.

---

## 9. Trust Relationship

Entitlement evaluation trusts only signals that survive the Mode B trust pipeline:

```
Enterprise Platform AuthN
        ↓
Presentation validation (ADR-016: crypto, iss, aud, time, …)
        ↓
Wire → ADR-015 claim mapping + required-claim enforcement
        ↓
Enterprise Entitlement Gate (this ADR)
        ↓
Complaint Roles mapping (ADR-014)
        ↓
Permission resolution (ADR-008)
```

### Trust rules

1. Entitlement signals conveyed with the presentation must still pass ADR-016 trust validation if they travel in-band.
2. Entitlement signals obtained out-of-band (for example directory/entitlement service lookup) must use an Enterprise Platform–trusted channel and authenticated caller identity already bound to `external_user_id`.
3. ECMP must not accept “self-asserted entitlement” from the client.
4. Audience validation (ADR-016) proves the presentation was meant for ECMP; entitlement proves the subject is **allowed into the module**. Both are required under Mode B.

---

## 10. Consumption Boundary

| Boundary | Responsibility |
|---|---|
| **Enterprise Platform** | Issue and maintain entitlement SoR |
| **ECMP Identity Adapter** | Sole Mode B consumption point for Entitlement Gate evaluation |
| **ECMP Business Module services** | Must not re-implement alternate entitlement admission; must assume caller already passed the gate (defense-in-depth permission checks still apply) |
| **Frontend / browser** | Must not be treated as entitlement authority (OD-FE-002 remains downstream; not closed here) |

### Containment

- Protocol and entitlement divergence terminate at the Identity Adapter (ADR-014 Containment Principle).
- Complaint domain logic must not branch on “how entitlement was represented.”
- Mode A (Standalone) is outside enterprise entitlement runtime; Mode A must not contradict these ownership rules when Mode B is later enabled.

---

## 11. Relationship Matrix (Must Preserve)

### 11.1 Relationship with Identity Contract (ADR-015) — Identity SoT

| | Identity (ADR-015) | Entitlement (this ADR) |
|---|---|---|
| Question | Who is the subject? | May the subject enter ECMP Complaint? |
| SoT | ADR-015 bilateral contract | Enterprise Platform entitlement SoR (architecture here) |
| Required claims | `external_user_id`, org hierarchy, etc. | Not an ADR-015 claim-table redesign |
| Failure | Missing required identity claims → deny | Missing/invalid entitlement → deny |

**Normative:** This ADR must not add, remove, or redefine ADR-015 required/optional claims. If a future representation uses an identity-adjacent signal, it is a **binding/entitlement profile** decision subordinate to ADR-015, not a silent contract change.

### 11.2 Relationship with Protocol Binding (ADR-016) — Protocol SoT

| | Protocol (ADR-016) | Entitlement (this ADR) |
|---|---|---|
| Question | Is presentation authentic and correctly targeted? | Is module admission granted? |
| SoT | ADR-016 families + binding rules | Entitlement architecture (this ADR) |
| Pipeline slot | L1–L8 (trust + map + identity contract) | L9 Entitlement Gate |
| Deferred | IdP product; binding profile tables | On-the-wire entitlement representation (aligned with ADR-016 D-04) |

**Normative:** ADR-016 remains protocol SoT. This ADR does not select OIDC/SAML fields or unlock Mode B coding.

### 11.3 Relationship with RBAC SoT (ADR-008) — Permission SoT

| | Entitlement | Permission (ADR-008) |
|---|---|---|
| Granularity | Module admission (coarse) | Action/resource permission (fine) |
| SoT | Enterprise Platform | Core Platform |
| When evaluated | Before Complaint Roles mapping | After role mapping |

**Normative:** Entitlement must not become a second Role-Permission Matrix. Permissions are never “proven” by entitlement alone.

### 11.4 Relationship with Complaint Module (ADR-014) — Complaint Role ownership

| | Entitlement Gate | Complaint Roles mapping |
|---|---|---|
| Owner of decision | Enterprise grant + ECMP gate evaluation | ECMP Business Module |
| Order | First (admission) | After admission |
| Default on AuthN only | Deny | Must not assign default role |

**Normative:** Complaint Role ownership remains ADR-014. This ADR does not define role catalogs, mapping tables, or permission sets.

---

## 12. Failure Behavior (Fail Closed)

| Condition | Required behavior |
|---|---|
| Entitlement absent | Deny module access |
| Entitlement invalid / malformed relative to chosen representation profile | Deny |
| Entitlement revoked or suspended | Deny; deactivate local access use |
| Entitlement expired | Deny |
| Entitlement for a different module only | Deny for ECMP Complaint |
| Identity valid but entitlement missing | Deny |
| Presentation trusted (ADR-016) but entitlement missing | Deny |
| Entitlement present but ADR-015 required claims fail | Deny (identity fails first / independently) |
| Ambiguous entitlement signal | Deny (no fail-open interpretation) |
| Local projection says entitled but enterprise signal says not | Deny (enterprise wins) |

### Prohibited behaviors

1. Default-allow when entitlement signal is missing.
2. Inferring entitlement from email, display name, or org membership alone.
3. Inferring entitlement solely from optional `enterprise_role_codes`.
4. Collapsing entitlement into ADR-008 permissions.
5. Assigning Complaint Roles before gate success.

Semantic outcome alignment (high level): unauthenticated / untrusted presentation → unauthenticated denial; trusted identity without entitlement → access denial for module entry; entitled but unauthorized for action → forbidden at permission layer (ADR-008). Exact HTTP mapping remains an API-contract concern and is **not** changed by this ADR.

---

## 13. Governance

| Topic | Rule |
|---|---|
| Architecture changes to entitlement meaning/ownership/order | Require ADR revision + Architecture Board |
| Representation profile (wire/API shape) | Change-controlled Security/Architecture artifact subordinate to this ADR; must not rewrite ADR-015/008/014 role catalogs |
| Fail-closed subordination (ADR-016 §9.3) | Representation / reconciliation profiles **MUST NOT** loosen §12 fail-closed gate rules, invent default-allow, or treat ambiguous entitlement as allow. Any relaxation of fail-closed entitlement evaluation requires **Architecture Board** Resolution citing this ADR (same standard as ADR-016 §9.3). |
| Production enablement of Mode B entitlement checks | Requires Mode B unlock (PROGRAM-BOARD-004 C-7) **and** Accepted protocol/entitlement baselines as Board conditions dictate |
| Audit | Enterprise Platform audits entitlement grant/revoke SoR changes; ECMP audits gate denials/allows and subsequent AuthZ decisions |
| RACI | Security Architect R/A for access-affecting entitlement evaluation rules; Enterprise Platform owns issuance SoR; Architecture Board adjudicates material policy disputes |
| Relationship to PROGRAM-BOARD-004 | C-7 remains: Mode B / Batch-2 / Enterprise customer **CLOSED** |

---

## 14. Deferred Decisions

| ID | Deferred item | Notes |
|---|---|---|
| E-01 | Exact entitlement **representation** (claim/attribute/API) | Completes ADR-014 follow-up / ADR-016 D-04; must obey this architecture |
| E-02 | Issuance UX / enterprise admin workflow | Enterprise Platform concern |
| E-03 | Push vs pull vs login-time reconciliation of entitlement state | Must preserve fail-closed gate evaluation |
| E-04 | Time-bounded entitlement / TTL policy details | If used, expiry fails closed |
| E-05 | Multi-module entitlement model beyond ECMP Complaint | Out of scope except isolation principle |
| E-06 | Service-to-service / non-human entitlement profile | Separate from interactive user entitlement |
| E-07 | Break-glass entitlement path | Must be designed/audited; not Mode A password bypass |
| E-08 | Mode B implementation authorization & OpenAPI changes | Explicitly not granted here |
| E-09 | OD-FE-002 browser bridge | Downstream; not closed by this ADR |

---

## 15. Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | Entitlement collapsed into identity claims without gate | Every authenticated user enters ECMP | Hard separation §§6–11; fail closed §12 |
| R-02 | Entitlement collapsed into permissions (ADR-008) | SoT drift; coarse/fine confusion | Relationship matrix §11.3 |
| R-03 | Complaint Roles assigned pre-gate | Default privilege from AuthN | Ordering §5 / §11.4 |
| R-04 | Representation profile silently edits ADR-015 | Dual identity SoT | E-01 subordination rule |
| R-05 | Stale local entitlement projection | Access after revoke | Enterprise wins; deactivate on suspend/revoke |
| R-06 | Implementing Mode B on Proposed ADR | Governance breach | Status Proposed; non-authorization §17 |
| R-07 | Treating ADR-016 audience success as entitlement | Skips module admission | Trust relationship §9 |
| R-08 | Optional enterprise role labels treated as entitlement | Uncontrolled admission | Explicit prohibition §6 / §12 |

---

## 16. Consequences

### Positive

- Completes the architectural definition of the ADR-014 Entitlement Gate without touching permission or complaint-role catalogs.
- Clarifies ownership, lifecycle, consumption boundary, and SoT preservation across ADR-015 / ADR-016 / ADR-008 / ADR-014.
- Keeps fail-closed module admission independent of protocol product choice.

### Trade-offs

- On-the-wire representation (E-01) still required before implementation.
- Enterprise Platform must operate an entitlement issuance capability (process/system) before Mode B can work.

### Non-consequences

- No Mode B unlock
- No Batch-2 / enterprise customer unlock
- No OpenAPI / JWT / authorization code changes
- No redesign of ADR-015, ADR-016, ADR-008 matrices, or Complaint Roles

---

## 17. Explicit Non-Authorization

This ADR (even if later Accepted) does **not** by itself authorize:

1. Mode B runtime enablement
2. Authorization code or JWT claim implementation
3. OpenAPI `securitySchemes` or entitlement endpoint publication
4. Changes to Role-Permission Matrix data or Complaint Roles catalogs
5. Redesign of ADR-015 or ADR-016
6. OD-FE-002 implementation
7. Batch-2 or enterprise customer production
8. Cutover Mode A → Mode B

---

## 18. Follow-ups

- [x] Architecture Board review of **ADR-017** → Accepted with Conditions (PROGRAM-BOARD-006 **BR-012**)
- [x] After Accept: draft Entitlement Representation Profile (E-01) subordinate to this ADR — **Draft** `entitlement-rep-ecmp-complaint-v0.1` (`10 Security and Access Standards/ECMP_ENTITLEMENT_REPRESENTATION_PROFILE_v0.1.md`); EP bilateral confirm pending; still no Mode B unlock
- [ ] Keep ADR-016 Accept track independent but sequenced before Mode B AuthN coding (C-B6-5)
- [ ] After Mode B authorization (future): implement gate evaluation inside Identity Adapter only
- [ ] Service-to-service entitlement profile (E-06) when needed
- [ ] Break-glass design (E-07)
- [ ] Editorial sync to Solution Architecture / Security standards after Accept (no contract invention)
- [x] Do **not** treat Accept as Mode B unlock (PROGRAM-BOARD-006 C-B6-1 / PROGRAM-BOARD-004 C-7)

---

## 19. Document History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-30 | PROGRAM-ENTERPRISE-003 — initial Proposed Enterprise Entitlement Architecture; preserves ADR-015/016/008/014 SoT boundaries; Mode B remains CLOSED |
| 1.0a | 2026-07-30 | Audit **K-5** — §13 adds fail-closed subordination aligned to ADR-016 §9.3 (profiles cannot loosen gate rules without Board) |
| 1.0b | 2026-07-30 | PROGRAM-BOARD-006 **BR-012** — Accepted with Conditions (C-B6-1…C-B6-7); metadata only; Mode B CLOSED |

---

*End of ADR-017 v1.0. Architecture Accept With Conditions — no Mode B unlock; no OpenAPI enterprise securitySchemes authorization.*
