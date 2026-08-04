# ECMP-EBS-001 — Organization Location + Complaint Module Authorization

| Field | Value |
|---|---|
| ID | ECMP-EBS-001 |
| Version | 1.0.0 |
| Date | 2026-08-04 |
| Mode | A (`ECMP_AUTH_MODE=dev`) — Mode B unaffected |
| Status | Commits 1–7 implemented; PR not yet opened |
| Governing documents | Readiness Assessment (NEARLY READY), EBS-001, IP-001, DG-001 (PASS) |
| Evidence | `deploy/evidence/EBS-001_Mode_A_Org_Location_Authorization_20260804.md` |

## 1. Decision

Close the second, previously-unenforced direction of organization-location validation for users (head-office scoped roles must not carry a `branchId`, mirroring the existing branch-required direction), and extend enforcement of the existing complaint-module permission model into two frontend surfaces that previously offered no visibility or access control at all: the sidebar navigation and the `/complaints` route itself.

This is an enforcement and UX-consistency change, not a redesign. It does not introduce a new authorization model, a new permission catalog, or a new role catalog — every role code and permission string referenced already existed before this batch (confirmed against the live `roles` table and `backend/app/core/rbac.py` respectively).

## 2. Role Classification (backend/app/modules/users/service.py)

| Class | Codes | `branchId` rule |
|---|---|---|
| Exception | `SUPER_ADMIN` | Optional, evaluated first; validated for existence if present |
| Branch-scoped | `AGENT`, `CS_AGENT`, `BRANCH_OFFICER`, `SUPERVISOR`, `BRANCH_SUPERVISOR` | Required (unchanged, predates this batch) |
| Head-office scoped | `ADMIN`, `ADMINISTRATOR`, `HO_SCHEDULER`, `HEAD_OFFICE_SCHEDULER`, `SCHEDULER`, `HO_ENGINEER`, `HEAD_OFFICE_ENGINEER` | Forbidden (new this batch) |
| Unclassified | e.g. `VIEWER`, `HANDLER` | Optional (unchanged) |

Pre-flight verification (DG-001): the lab database holds zero users under any head-office scoped code, so this rule has no existing record to retroactively reject.

## 3. Complaint Module Authorization (frontend)

Two enforcement points, one metadata source:

- **Navigation** (`frontend/src/shared/layouts/app-layout/nav.ts`, `Sidebar.tsx`) — the `complaints` `NavItem` carries `requiredPermissions`, the canonical set from `backend/app/core/rbac.py`'s complaint family (`complaints:read/create/update/assign/escalate/close`). Hidden unless the user holds at least one.
- **Layout** (`frontend/src/app/(app)/complaints/layout.tsx`) — reads the identical `NavItem` from the identical `APP_NAV_ITEMS` array and evaluates it with the identical `isNavItemVisible` function. Blocks direct URL access; renders the repository's existing `Empty`/"Access Denied" pattern instead of protected content.

Wildcard (`*`) handling exists in exactly one place, `AuthProvider.hasPermission`, and neither gate reimplements it.

## 4. Out of Scope

Mode B, Enterprise entitlement, OIDC, Identity Adapter, CAP-006, CAP-005, DEC-F4, M4, permission redesign, role redesign, database migration, router changes. None referenced or touched by this batch.

## 5. Traceability

No `traceability.yaml` / `TRACEABILITY_MATRIX.md` entry added. This batch enforces existing Mode A business rules and existing complaint-module permissions more consistently — it does not introduce a new FR, BR, or API contract. `TRACEABILITY_MATRIX.md` is auto-generated and was not hand-edited.

## 6. Reference

Full scope, file inventory, acceptance criteria, test results, risks, and rollback: see the evidence pack linked above. Per-commit implementation detail: Commits 1–7 reports (not persisted as repo files; available in the engineering session record).
