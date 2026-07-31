# ECMP Entitlement Representation Profile v0.1 (Draft)

| Field | Value |
|---|---|
| Document ID | SEC-ENT-REP-001 |
| Profile ID | `entitlement-rep-ecmp-complaint-v0.1` |
| Version | 0.1 |
| Date | 2026-07-30 |
| Owner | Security Architect / Enterprise Authorization Architect |
| Reviewer | Solution Architect / Enterprise Platform (bilateral) |
| Approver | Architecture Board (profile acceptance — separate from Mode B unlock) |
| Status | 🟡 **Draft** |
| Parent ADR | ADR-017 v1.0 (Accepted with Conditions — PROGRAM-BOARD-006 **BR-012**) |
| Closes (partial) | ADR-017 **E-01** / ADR-016 **D-04** (representation — working draft pending EP bilateral confirm) |
| Mode B coding | **Not authorized** (C-B6-1 / C-7 CLOSED) |

---

## 1. Purpose

Define **how** Enterprise Platform communicates that a subject is entitled to the **ECMP Complaint** module, so the Identity Adapter Entitlement Gate can evaluate admit/deny under Mode B **when** Mode B is later unlocked.

Entitlement answers only:

> Has the Enterprise Platform explicitly granted this subject access to ECMP Complaint?

It does **not** assign Complaint Roles (ADR-014) or permissions (ADR-008).

---

## 2. Subordination (normative)

Subordinate to ADR-017 §13, ADR-016 §9.3, ADR-015, ADR-014, ADR-008, and PROGRAM-BOARD-006 **C-B6-2**.

**MUST NOT:**

1. Treat AuthN success or audience match as entitlement
2. Auto-map `enterprise_role_codes` (or any ADR-015 optional labels) to entitlement or permissions
3. Invent default-allow / “everyone in org is entitled”
4. Loosen fail-closed gate rules without Board Resolution
5. Edit ADR-015 required claim tables

---

## 3. Options considered

| Option | Description | Verdict |
|---|---|---|
| **A — Dedicated boolean claim** | e.g. `ecmp_complaint_entitled: true` | Viable; simple |
| **B — Module entitlement array** | e.g. `module_entitlements` contains `ecmp.complaint` | Viable; multi-module ready |
| **C — Directory group / role name as entitlement** | Infer from enterprise group membership | **Rejected** as sole signal — conflates labels with module admission; hard to fail closed consistently |
| **D — ECMP-side default grant after SSO** | Any authenticated user entitled | **Rejected** — violates ADR-014/017 |

---

## 4. Working draft recommendation (E-01)

**Chosen for Draft v0.1 (pending bilateral confirm):** **Option B — module entitlement array**, with Option A accepted as an equivalent alternate if EP prefers a boolean.

### 4.1 Primary representation (array)

| Field | Rule |
|---|---|
| Wire name (provisional) | `module_entitlements` |
| Type | Array of strings |
| ECMP Complaint token | Exact string `ecmp.complaint` |
| Admit | Array present **and** contains exact token `ecmp.complaint` |
| Deny | Array missing, not an array, empty, or token absent |
| Case / whitespace | Exact match; no case-folding; trim not applied |

### 4.2 Alternate representation (boolean)

| Field | Rule |
|---|---|
| Wire name (provisional) | `ecmp_complaint_entitled` |
| Type | JSON boolean |
| Admit | Exactly `true` |
| Deny | Missing, `false`, string `"true"`, or any non-boolean |

### 4.3 Coexistence rule

If **both** signals appear:

1. Prefer **deny on conflict** (array lacks token but boolean true, or vice versa) → **deny**
2. Admit only if **at least one** valid admit signal and **no** conflict

Enterprise Platform SHOULD emit exactly one representation style per environment.

---

## 5. Conveyance channel

| Channel | Profile rule |
|---|---|
| In access-token claims | **Preferred** for interactive user Mode B (same presentation as Binding Profile) |
| Separate entitlement API | Allowed as future reconciliation path (E-03); gate must still deny if live check fails |
| Login-time only cache | Local projection allowed; stale “entitled” must not outrank enterprise revoke (ADR-017 §8) |

Reconciliation cadence (push vs pull vs login-time) remains **E-03** — this profile requires only that gate evaluation can deny on absence/invalid at decision time.

---

## 6. Gate evaluation (design only)

Order relative to Binding Profile:

1. Presentation trust + ADR-015 required claims satisfied
2. **Entitlement Gate** per §4 → deny if not entitled
3. Org resolvability (ADR-018) for scope-dependent AuthZ
4. Complaint Roles mapping (ADR-014)
5. ADR-008 permissions

`employment_status` denying access (per ADR-015) remains independent of entitlement.

---

## 7. Lifecycle mapping (consume-only)

| Enterprise signal | Gate |
|---|---|
| Grant / active with valid representation | May admit |
| Suspend / revoke / expiry / missing token | **Deny** |
| Ambiguous / malformed representation | **Deny** |

---

## 8. Out of scope (remain deferred)

| ID | Item |
|---|---|
| E-02 | Issuance UX / enterprise admin workflow |
| E-03 | Push vs pull reconciliation details |
| E-04 | TTL policy details (if used → expiry fails closed) |
| E-05 | Multi-module model beyond `ecmp.complaint` (array shape allows future tokens) |
| E-06 | Service-to-service entitlement |
| E-07 | Break-glass entitlement |
| E-08 / E-09 | Mode B coding / OD-FE-002 |

---

## 9. Explicit Non-Authorization

- Does **not** unlock Mode B
- Does **not** authorize OpenAPI / Identity Adapter coding
- Does **not** grant Complaint Roles or permissions
- Wire names remain **provisional** until Enterprise Platform countersigns this profile or a successor revision

---

## 10. Related

- Parent: `05 Architecture Decision Records/ECMP_ADR_017_Enterprise_Entitlement_Architecture_v1.0.md`
- Binding: `ECMP_BINDING_PROFILE_OIDC_ECMP_v0.1.md`
- Pack: `18 Architecture Governance/ECMP_PROGRAM_ENTERPRISE_PROFILES_001_Subordinate_Profiles_Draft_Pack_v0.1.md`

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-30 | Initial Draft — array `module_entitlements` + boolean alternate; Mode B CLOSED |

---

*End of SEC-ENT-REP-001. Draft subordinate profile — no Mode B coding.*
