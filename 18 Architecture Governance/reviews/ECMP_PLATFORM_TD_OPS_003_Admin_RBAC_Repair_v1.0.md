# ECMP Platform — TD-OPS-003 ADMIN role_permissions Repair

| Field | Value |
|---|---|
| Document ID | GOV-PLATFORM-OPS-SEED-001 |
| Date | 2026-07-29 |
| Status | 🟢 Complete (ADMIN matrix only) |
| Epic | EPIC-PLATFORM |
| Task | TASK-PLATFORM-OPS-SEED-001 (narrow scope) |

## Objective

Close **TD-OPS-003**: `golive_admin` (role `ADMIN`) could login but received empty permissions → CM APIs 403.

Out of scope this task: TD-OPS-002 (agent/viewer password drift).

## Root cause

| Role | Grants before `0044` |
|---|---|
| `ADMIN` | **0** |
| `ADMINISTRATOR` | 46 |
| `SUPER_ADMIN` | 46 |

`golive_admin.role_id` → `ADMIN`. Migration `0039_admin_rbac_repair` had seeded aliases but live `ADMIN` row had no `role_permissions` (likely post-0039 role recreate / missed insert). Permission catalog for `complaints:read`/`create`/`*` was present.

## Fix

- New Alembic revision `0044_admin_rbac_repair` (revises `0043`)
- Idempotent insert of canonical ADMIN matrix for `ADMIN`, `ADMINISTRATOR`, `SUPER_ADMIN`
- Downgrade is intentionally non-destructive (no revoke)

## Verification

| Check | Result |
|---|---|
| `alembic upgrade head` | `0044_admin_rbac_repair` |
| ADMIN grants | **46** including `complaints:read` + `complaints:create` |
| `golive_admin` `/me` perm_count | 46 |
| CM search / confirm / create | 200 / 200 / 201 (`CM-00000003`) |
| Head-assertion unit tests | 6 passed |

## Debt status

| ID | After this task |
|---|---|
| TD-OPS-003 | **Closed** |
| TD-OPS-002 | Still open (agent/viewer 401) |

---

*End of GOV-PLATFORM-OPS-SEED-001.*
