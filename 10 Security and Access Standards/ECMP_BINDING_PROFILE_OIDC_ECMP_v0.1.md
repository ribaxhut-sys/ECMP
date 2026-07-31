# ECMP Binding Profile — OIDC / ECMP v0.1 (Draft)

| Field | Value |
|---|---|
| Document ID | SEC-BIND-OIDC-001 |
| Profile ID | `binding-oidc-ecmp-v0.1` |
| Version | 0.1 |
| Date | 2026-07-30 |
| Owner | Security Architect |
| Reviewer | Solution Architect / Enterprise Platform (bilateral) |
| Approver | Architecture Board (profile acceptance — separate from Mode B unlock) |
| Status | 🟡 **Draft** |
| Parent ADR | ADR-016 v1.0 (Accepted with Conditions — PROGRAM-BOARD-006 **BR-011**) |
| Claim SoT | ADR-015 v1.3 / Identity Contract **v1.0** |
| Closes (partial) | ADR-016 **D-02** (profile tables — provisional until EP issuer catalog confirmed) |
| Mode B coding | **Not authorized** (C-B6-1 / C-7 CLOSED) |

---

## 1. Purpose

Define a **subordinate Binding Profile** for the **OpenID Connect (OIDC)** protocol family: how an OIDC-derived presentation maps to ADR-015 canonical claims and which trust controls (`iss`, `aud`, signature, lifetime) ECMP must enforce under Mode B **when** Mode B is later unlocked.

This profile does **not** select an IdP product (ADR-016 **D-01** remains open).

---

## 2. Subordination (normative)

This profile is subordinate to ADR-016 §9.3, ADR-015, ADR-014, ADR-008, and PROGRAM-BOARD-006 **C-B6-2**.

**MUST NOT:**

1. Loosen fail-closed claim / AuthN rules
2. Introduce default-allow or degraded-allow without Board Resolution
3. Change ADR-015 claim cardinality, key rules (`external_user_id`), or fail-closed semantics
4. Treat ADR-012 historical claim vocabulary as Mode B SoT

---

## 3. Protocol family & presentation

| Item | Profile rule |
|---|---|
| Family | **OIDC** (preferred for interactive user AuthN per ADR-016 §7) |
| Presentation to ECMP APIs | Bearer **access token** (JWT profile assumed unless EP specifies opaque + introspection — TBC) |
| ID token | May be used at browser/session establishment **only if** a future Mode B UI bridge profile cites it; API Resource Server baseline = access token |
| Product IdP | **Deferred (D-01)** — Keycloak / Entra / Okta / other not selected here |

---

## 4. Trust controls (fail-closed)

| Control | Rule |
|---|---|
| Signature | Validate JWT signature against issuer JWKS (or equivalent). Invalid → **deny** |
| `iss` | Exact match to configured issuer allowlist. Missing/mismatch → **deny** |
| `aud` | Exact match to configured ECMP audience allowlist (ADR-016 §10). Missing/mismatch → **deny** |
| Lifetime | Reject if `exp` missing, expired, or `nbf` in future (clock skew ≤ 60s configurable; default deny on ambiguity) |
| Algorithm | Deny `none` and weak algs; allowlist algorithms in deployment config (not default-allow) |
| Replay | Mandatory server-side replay cache **not** required by this v0.1 (ADR-016 D-05); short-lived tokens assumed |

**Provisional placeholders (TBC with Enterprise Platform):**

| Config key (logical) | Example shape | Status |
|---|---|---|
| `mode_b.oidc.issuer` | `https://idp.example/realms/enterprise` | TBC |
| `mode_b.oidc.audience` | `ecmp-complaint` or `api://ecmp` | TBC — must be ECMP-isolated (ADR-016 §10.4) |
| `mode_b.oidc.jwks_uri` | issuer discovery / static JWKS URL | TBC |

---

## 5. Wire → ADR-015 claim mapping (provisional)

Canonical names are **ADR-015**. Wire names below are **working drafts** until Enterprise Platform confirms its issuer claim catalog (D-02).

| ADR-015 claim | Cardinality | Provisional OIDC wire source | Mapping notes |
|---|---|---|---|
| `external_user_id` | Exactly one | Prefer dedicated claim `enterprise_user_id` **or** EP-guaranteed opaque `sub` | Must be opaque, immutable, non-reassignable. **Never** map from `email` / `preferred_username` |
| `display_name` | Exactly one | `name` or `preferred_username` (display only) | If both absent → deny |
| `email` | Exactly one | `email` | Contact attribute only — **not** join key |
| `organization_id` | Exactly one | `organization_id` (custom) | Exact one; no partial hierarchy |
| `branch_id` | Exactly one | `branch_id` (custom) | Exact one |
| `department_id` | Exactly one | `department_id` (custom) | Exact one |
| `employment_status` | Exactly one | `employment_status` (custom) | Values interpreted per ADR-015 semantics; unknown/missing → deny |

### Optional claims (non-exhaustive)

| ADR-015 optional | Provisional wire | Notes |
|---|---|---|
| `preferred_language` | `locale` / `preferred_language` | Absence OK |
| `job_title` | `job_title` / `title` | Absence OK |
| `enterprise_role_codes` | `enterprise_role_codes` (array) | **Informational only** — never auto-map to ADR-008 permissions |
| `manager_external_user_id` | `manager_external_user_id` | Absence OK |
| `identity_contract_version` | `identity_contract_version` | Prefer explicit `1.0` when present |

### Explicit non-mappings

| Wire / historical field | Must not become |
|---|---|
| `roles[]` (ADR-012-era) | ECMP permissions or Complaint Roles |
| `orgUnitId` (ADR-012-era) | Substitute for three-level org claims |
| `email` | `external_user_id` |
| Missing required claim | Default / invented value |

---

## 6. Evaluation order (Identity Adapter — design only)

When Mode B is authorized later, evaluation SHALL follow ADR-016 pipeline order. Profile-specific notes:

1. Trust controls (§4) before claim mapping
2. Map wire → ADR-015; missing required → **deny**
3. Entitlement Gate (see Entitlement Representation Profile) — AuthN success ≠ entitlement
4. Org reference resolvability (ADR-018) — unresolvable → **deny** scope-dependent AuthZ
5. Local profile correlation by `external_user_id` only
6. Complaint Roles mapping (ADR-014) only after gate success
7. ADR-008 permission checks

---

## 7. Open / bilateral items

| ID | Item | Blocks |
|---|---|---|
| BP-O-01 | Confirm issuer claim catalog & wire names | Finalizing D-02 tables |
| BP-O-02 | Confirm `aud` / `iss` production values | Deployment binding |
| BP-O-03 | JWT access token vs opaque+introspection | Adapter detailed design |
| BP-O-04 | IdP product (D-01) | Ops runbooks — not this profile’s job |
| BP-O-05 | ADR-007 / ADR-012 Board disposition (D-08) | Narrative closure only |

---

## 8. Explicit Non-Authorization

- Does **not** unlock Mode B / Batch-2 / enterprise customer
- Does **not** authorize OpenAPI enterprise `securitySchemes` edits
- Does **not** authorize Identity Adapter coding
- Does **not** close OD-FE-002
- Does **not** waive org-model gap prerequisite (C-B6-3)

---

## 9. Related

- Parent: `05 Architecture Decision Records/ECMP_ADR_016_Enterprise_Protocol_Binding_v1.0.md`
- Claims: `05 Architecture Decision Records/ECMP_ADR_015_Enterprise_Identity_Contract_v1.3.md`
- Pack: `18 Architecture Governance/ECMP_PROGRAM_ENTERPRISE_PROFILES_001_Subordinate_Profiles_Draft_Pack_v0.1.md`
- Sibling: Entitlement Representation Profile; Org Sync Integration Profile

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-30 | Initial Draft — OIDC family provisional mapping; Mode B CLOSED |

---

*End of SEC-BIND-OIDC-001. Draft subordinate profile — no Mode B coding.*
