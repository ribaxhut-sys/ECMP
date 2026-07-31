# ECMP Organization Sync Integration Profile v0.1 (Draft)

| Field | Value |
|---|---|
| Document ID | SEC-ORG-SYNC-001 |
| Profile ID | `org-sync-integration-ecmp-v0.1` |
| Version | 0.1 |
| Date | 2026-07-30 |
| Owner | Solution Architect / Enterprise Integration Architect |
| Reviewer | Security Architect / Enterprise Platform (bilateral) |
| Approver | Architecture Board (profile acceptance — separate from Mode B unlock / schema delivery) |
| Status | 🟡 **Draft** |
| Parent ADR | ADR-018 v1.0 (Accepted with Conditions — PROGRAM-BOARD-006 **BR-013**) |
| Addresses | ADR-018 **O-01…O-05**, **O-08** (architecture profile — not schema migration authorization) |
| Mode B coding / unlock | **Not authorized** (C-B6-1 / C-7 CLOSED; **C-B6-3** org-gap prerequisite remains) |

---

## 1. Purpose

Define a **subordinate Organization Synchronization Integration Profile**: how ECMP intends to obtain **non-authoritative** organization projections so ADR-015 Organization References (`organization_id`, `branch_id`, `department_id`) are **resolvable** for Mode B AuthZ — without making ECMP the organization SoR.

This profile **plans** gap closure (O-03) but does **not** by itself authorize Alembic migrations, OpenAPI, or Mode B unlock.

---

## 2. Subordination (normative)

Subordinate to ADR-018 §14–§15, ADR-016 §9.3, ADR-015, ADR-017, ADR-014, ADR-008, PROGRAM-BOARD-006 **C-B6-2** / **C-B6-3**, and `ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`.

**MUST NOT:**

1. Fail open on unresolvable Organization References
2. Authorize degraded-allow via this profile alone
3. Invent hierarchy when upstream sync is unavailable
4. Treat local projections as enterprise SoR
5. Expand descendant AuthZ scope without an explicit O-06 decision

---

## 3. Current gap (as-is)

| Level | ADR-015 claim | Foundation today |
|---|---|---|
| Organization | `organization_id` | **No** first-class `organizations` master/projection |
| Branch | `branch_id` | Local `branches` table exists (Mode A); **not** proven as enterprise projection keyed by ADR-015 ids |
| Department | `department_id` | **No** first-class `departments` master/projection |

Until three-level resolvability exists, Mode B unlock remains forbidden (C-B6-3).

---

## 4. Target projection model (conceptual — O-03)

Working draft entities (names provisional):

| Projection | Key | Minimum attributes | Notes |
|---|---|---|---|
| `organizations` | `organization_id` (enterprise opaque id) | `display_name`, `is_active`, `as_of` | Non-authoritative |
| `branches` (enterprise-aligned) | `branch_id` | `organization_id`, `display_name`, `is_active`, `as_of` | May evolve from/coexist with Mode A `branches` under a future delivery DEC — **not decided here** |
| `departments` | `department_id` | `organization_id`, `branch_id`, `display_name`, `is_active`, `as_of` | Non-authoritative |

**Resolvability rule:** for AuthZ that depends on org scope, all three referenced ids on the identity **MUST** resolve to active (or policy-allowed historical) projection rows at decision time; else **deny**.

Schema DDL, migrations, and dual-write with Mode A `branches` are **out of scope of this Draft** — require a future delivery authorization that still does not unlock Mode B until Board opens C-7/C-B6-1 **after** gap closure evidence.

---

## 5. Transport & cadence (O-01, O-02, O-04, O-08)

| Option | Description | Draft verdict |
|---|---|---|
| Push webhooks / events | EP pushes org change events | Allowed later; payloads not invented in Event Catalog here (O-02) |
| Pull / reconciliation API | ECMP pulls org graph or deltas | **Preferred baseline** for v0.1 |
| Login-time hydration | Resolve/refresh refs seen on subject at AuthN | **Required complement** for cold start |
| Hybrid | Periodic pull + login-time ensure | **Working draft recommendation** |

### Working draft recommendation

1. **Login-time:** on Mode B identity accept, ensure referenced org/branch/department rows exist or refresh; if unresolvable → **deny**
2. **Periodic pull:** background reconciliation against EP org API (contract TBC) to update projections and mark inactive
3. **Push events:** optional later enhancement — must not weaken fail-closed rules

API paths, webhook payloads, and Event Catalog entries are **not** published by this profile (O-01/O-02 remain open for a future Board-accepted need).

---

## 6. Cache strategy (O-05)

| Rule | Profile |
|---|---|
| Cache role | Performance only; never authority above EP |
| Stale entitled org | Last-known projection usable **only if** required refs still resolve (ADR-018 §14) |
| Sync channel down | Do **not** fabricate structure; deny when refs unresolvable |
| TTL | Exact TTL deferred; must not imply fail-open |

---

## 7. Explicitly still open (not decided by this Draft)

| ID | Item | Why open |
|---|---|---|
| O-06 | Hierarchy traversal / descendant scope | High risk if assumed; ambiguous → deny unsafe expansion |
| O-07 | Upstream delete/restructure vs live complaints | Retention vs re-scope needs Board/business policy |
| O-09 | Mode B implementation & OpenAPI | C-B6-1 CLOSED |
| Mode A `branches` coexistence | Mapping/cutover | Needs delivery DEC when schema work is authorized |

---

## 8. Acceptance criteria for “org-gap prerequisite met” (evidence bar)

Before any Mode B **unlock** Resolution may cite C-B6-3 as satisfied, evidence SHOULD include:

1. Resolvable projections (or masters) for **organization**, **branch**, and **department** keyed to ADR-015 ids
2. Fail-closed AuthZ tests: missing/unresolvable ref → deny
3. Sync-unavailable test: no fabricated hierarchy; deny when unresolvable
4. Written bilateral confirmation of EP org SoR feed (API or approved channel)
5. Explicit Board unlock of Mode B **still required** separately (C-B6-1)

This Draft alone does **not** satisfy the prerequisite.

---

## 9. Explicit Non-Authorization

- No Mode B unlock
- No Alembic / schema migration authorization
- No OpenAPI / webhook / Event Catalog invention
- No descendant AuthZ expansion (O-06 open)
- No waiver of C-B6-3

---

## 10. Related

- Parent: `05 Architecture Decision Records/ECMP_ADR_018_Enterprise_Organization_Synchronization_Architecture_v1.0.md`
- Prerequisite: `18 Architecture Governance/ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`
- Binding / Entitlement sibling profiles under `10 Security and Access Standards/`
- Pack: `18 Architecture Governance/ECMP_PROGRAM_ENTERPRISE_PROFILES_001_Subordinate_Profiles_Draft_Pack_v0.1.md`

| Rev | Date | Notes |
|---|---|---|
| 0.1 | 2026-07-30 | Initial Draft — hybrid pull + login-time; conceptual three-level projections; Mode B CLOSED |

---

*End of SEC-ORG-SYNC-001. Draft subordinate profile — no Mode B coding / no schema delivery.*
