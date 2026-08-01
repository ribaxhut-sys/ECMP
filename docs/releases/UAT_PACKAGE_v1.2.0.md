# ECMP v1.2.0 — User Acceptance Test Package

| Field | Value |
|---|---|
| ID | UAT-PKG-v1.2.0 |
| Version | 1.0 |
| Date | 2026-08-01 |
| Candidate | `v1.2.0-rc.1` @ `6890f50d8243ba30589a3d88f0c0efcef791ce01` |
| Scope | Mode A CAP-008 Case Management (+ Batch-1 prerequisite path) |
| Owner | Release Management / QA |
| Status | **PREPARED** — executable on lab Mode A; **not** shared/prod UAT authorization |
| SoT | Repository only — FRD/OpenAPI/Business Rules **not modified** by this pack |

> Shared/staging/production UAT entry remains gated by **REL-SEC-001**.  
> This package does **not** waive IdP / `ECMP_AUTH_MODE=jwt` requirements.

---

## 1. Entry criteria

| # | Criterion | Status @ pack date |
|---|---|---|
| E1 | Annotated RC `v1.2.0-rc.1` exists | **PASS** |
| E2 | REL-RC-001 CAP-008 lab assessment PASS | **PASS** — `deploy/evidence/REL_RC_001_CAP-008_Mode_A_Assessment_20260801.md` |
| E3 | Alembic ≥ `0046_cm_case_management` on lab | **PASS** |
| E4 | Lab CAP-008 lifecycle ≠ 404 | **PASS** (RC evidence) |
| E5 | REL-SEC-001 GO for shared/prod UAT host | **FAIL** — see Production Readiness / REL-SEC pack |

**Lab Mode A UAT** may proceed against E1–E4.  
**Shared/prod UAT** must not start until E5 = PASS.

---

## 2. Personas (Mode A)

| Persona | Role intent | Permissions (minimum) |
|---|---|---|
| Officer | Create / view / update / propose resolve | `complaints:create`, `complaints:read`, `complaints:update` |
| Supervisor | Accept resolve / close | same + operational oversight as seeded |
| Unauthenticated | Negative AuthN | (none) |
| Viewer | Negative AuthZ | `complaints:read` only |

Use lab/UAT accounts from `docs/releases/UAT_ACCOUNTS_v1.0.0.md` **only** on non-production hosts. Rotate before any shared public environment.

---

## 3. Test scenarios — CAP-008 (FR-001…FR-006)

| ID | FR | Scenario | Expected | Priority |
|---|---|---|---|---|
| UAT-008-01 | FR-001 | Create Case from eligible Batch-1 Complaint | 201; status `CREATED` or `ASSIGNED`; Case Number `CASE-YYYY-NNNNNN`; parent may move to `IN_PROGRESS` | Must |
| UAT-008-02 | FR-002 | Add second Case under same Complaint (N &lt; 5) | 201; distinct Case Number | Must |
| UAT-008-03 | FR-003 | View Case by id (+ membership context) | 200; fields match create | Must |
| UAT-008-04 | FR-004 | PATCH status → `IN_PROGRESS` | 200 | Must |
| UAT-008-05 | FR-004 | Attempt Mode A non-exposed status (`PENDING`) | Domain error (not 404) | Must |
| UAT-008-06 | FR-005 | Resolve ACCEPT with code + summary | 200; status `RESOLVED`; resolution history present | Must |
| UAT-008-07 | FR-006 | Close Case | 200; `CLOSED`; parent Complaint **not** auto-closed (BQ-007) | Must |
| UAT-008-08 | AuthN | POST `/api/v1/cm/cases` without token | **401** `UNAUTHENTICATED` (not 404) | Must |
| UAT-008-09 | AuthZ | POST create without `complaints:create` | **403** `FORBIDDEN` (not 404) | Must |
| UAT-008-10 | Side effects | After create/update — audit + complaint timeline entries exist | Audit entity `Case`; timeline on Complaint stream | Should |

### Out of scope for this UAT pack (Mode A)

- Assignment / SLA / Notification / Event engines  
- Mode B / OIDC login path  
- Complaint Aggregate closure as Case close side effect  
- Performance/load (k6) — backlog per Test Strategy  

---

## 4. Batch-1 prerequisite smoke (regression)

| ID | Check | Expected |
|---|---|---|
| UAT-B1-01 | Create/confirm Batch-1 complaint usable as CAP-008 parent | Complaint id usable in UAT-008-01 |
| UAT-B1-02 | Mode A credential routes present (lab) | Login / forgot / reset / change present |

---

## 5. Evidence capture (per run)

Record for each Must scenario: UTC time, environment URL, actor username (no passwords), request id if available, HTTP status, Case/Complaint ids, pass/fail.

Store completed run sheets **outside git** if they contain environment URLs tied to secrets. Summary may be linked from `deploy/evidence/`.

---

## 6. Exit criteria

| Class | Exit |
|---|---|
| Lab Mode A UAT | All **Must** scenarios PASS on `v1.2.0-rc.1` (or successor RC) |
| Shared/prod UAT | Lab exit **plus** REL-SEC-001 **GO** + REL-APR-001 sign-off |
| Release `v1.2.0` tag | Not authorized by this pack alone |

---

## 7. Related

- FRD Batch-2 SoT (read-only): `03 Functional Requirements/ECMP_FRD_Case_Management_Batch2_v1.0.md`
- OpenAPI SoT (read-only): `07 API Catalog/openapi/cm-case-management.v1.yaml`
- RC assessment: `deploy/evidence/REL_RC_001_CAP-008_Mode_A_Assessment_20260801.md`
- REL-SEC: `16 Release Management/ECMP_Release_Security_Gate_v1.0.md`
