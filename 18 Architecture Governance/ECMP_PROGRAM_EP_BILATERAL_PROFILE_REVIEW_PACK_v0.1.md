# PROGRAM — Enterprise Platform Bilateral Profile Review Pack v0.1

| Field | Value |
|---|---|
| Document ID | GOV-EP-BILAT-001 |
| Program | PROGRAM-EP-BILATERAL-001 |
| Version | 0.1 |
| Date | 2026-07-31 |
| Prepared by | Security Architect / Solution Architect (ECMP side) |
| Audience | Enterprise Platform Identity / Integration owners |
| Status | 🟡 **Issued for bilateral review — awaiting EP countersign** |
| Related profiles | SEC-BIND-OIDC-001, SEC-ENT-REP-001, SEC-ORG-SYNC-001 |
| Mode B | **CLOSED** on ECMP side — review does not unlock |

---

## 1. Request

Enterprise Platform is requested to **review and countersign** (or propose redlines to) the provisional wire names and trust values in the Draft subordinate profiles, per PROGRAM-BOARD-004 **C-3** Bilateral Contract and PROGRAM-BOARD-006 **C-B6-4**.

---

## 2. Documents under review

| ID | Path |
|---|---|
| Binding | `10 Security and Access Standards/ECMP_BINDING_PROFILE_OIDC_ECMP_v0.1.md` |
| Entitlement | `10 Security and Access Standards/ECMP_ENTITLEMENT_REPRESENTATION_PROFILE_v0.1.md` |
| Org sync | `10 Security and Access Standards/ECMP_ORG_SYNC_INTEGRATION_PROFILE_v0.1.md` |
| Claim SoT | `05 Architecture Decision Records/ECMP_ADR_015_Enterprise_Identity_Contract_v1.3.md` (Contract v1.0) |

---

## 3. Checklist for EP (please mark)

### 3.1 Identity / Binding

| # | Item | EP response (Agree / Redline / N/A) | Notes |
|---|---|---|---|
| B1 | OIDC family acceptable for interactive user Mode B | | |
| B2 | Access-token JWT presentation to ECMP APIs | | |
| B3 | Provisional `iss` allowlist shape | | Provide production/non-prod issuer URLs when ready |
| B4 | Provisional `aud` = ECMP-isolated audience | | Propose exact string |
| B5 | `external_user_id` wire = dedicated claim **or** opaque `sub` with non-reuse guarantee | | Must not be email |
| B6 | Wire names for `organization_id` / `branch_id` / `department_id` / `employment_status` | | |
| B7 | `display_name` / `email` mapping | | |

### 3.2 Entitlement

| # | Item | EP response | Notes |
|---|---|---|---|
| E1 | Prefer array `module_entitlements` containing `ecmp.complaint` | | |
| E2 | Alternate boolean `ecmp_complaint_entitled` | | Pick one primary |
| E3 | Entitlement in access-token claims vs separate API | | |
| E4 | Confirm AuthN ≠ entitlement (no default grant) | | |

### 3.3 Organization feed

| # | Item | EP response | Notes |
|---|---|---|---|
| O1 | EP is SoR for org hierarchy | | |
| O2 | Pull API availability (or approved channel) for org/branch/department | | Contract TBD — do not invent in ECMP Event Catalog here |
| O3 | Id opacity / stability of org/branch/department ids | | |
| O4 | Inactive / restructure signalling | | Informs DEC-022 |

---

## 4. ECMP commitments (reaffirmed)

1. Fail-closed on missing required claims / entitlement / unresolvable org refs
2. Will not treat EP countersign as Mode B unlock (C-B6-1)
3. Will not loosen fail-closed via profiles (C-B6-2)
4. Org-gap remains Mode B prerequisite (C-B6-3)

---

## 5. Countersign block (EP)

| Role | Name | Date | Decision |
|---|---|---|---|
| Enterprise Platform Identity Owner | | | ☐ Agree / ☐ Agree with redlines / ☐ Reject |
| Enterprise Platform Integration Owner | | | ☐ Agree / ☐ Agree with redlines / ☐ Reject |
| ECMP Security Architect (receive) | | | ☐ Recorded |

Redlines attach as appendix or revised profile rev 0.2.

---

## 6. Explicit Non-Authority

- Does not unlock Mode B on either side
- Does not authorize ECMP schema/OpenAPI coding
- Empty signature rows are intentional until EP responds

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-31 | Pack issued for bilateral review |

---

*End of GOV-EP-BILAT-001.*
