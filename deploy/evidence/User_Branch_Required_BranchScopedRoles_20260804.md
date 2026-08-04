# Evidence — Branch required for branch-scoped user roles

| Field | Value |
|---|---|
| Date | 2026-08-04 |
| Status | **DONE** (Mode A) |
| Scope | Create/update user API |

## Rule

`branchId` **required** when effective role is:

- `AGENT`, `CS_AGENT`, `BRANCH_OFFICER`
- `SUPERVISOR`, `BRANCH_SUPERVISOR` (supervisor / manager cabang)

Optional for `SUPER_ADMIN` / head-office roles.

## Artefacts

- `backend/app/modules/users/service.py` — `BRANCH_SCOPED_ROLE_CODES` + `_ensure_branch_for_role`
- Message `user.branch_required_for_role`
- OpenAPI `UserCreateRequest` / `UserUpdateRequest` descriptions
- Tests: `backend/tests/test_users.py` (19 passed)

## Lab

Orphan `agent_*` test users assigned to `JKT-01`.

## Out of scope

- FE create-user form (still directory-only)
- Mode B / enterprise org sync
