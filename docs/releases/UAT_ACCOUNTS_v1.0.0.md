# ECMP UAT Accounts — v1.0.0 / v1.0.0-rc2

| Field | Value |
|---|---|
| ID | UAT-ACCTS-V1 |
| Applies to | Foundation stack UAT / RC smoke |
| Date | 2026-07-25 |
| Auth | `POST /api/v1/auth/login` + refresh cookie |

## Role mapping

| UAT persona | System role code | Purpose |
|---|---|---|
| **Admin** | `ADMIN` | Administration, user management, full ops (when permission matrix resolved) |
| **Supervisor** | `SUPERVISOR` | Assign, escalate, close, operational oversight |
| **Officer** | `AGENT` (alias `BRANCH_OFFICER`) | Front-line complaint handling |
| **Viewer** | `VIEWER` | Read-only dashboards / reports |

Roles are seeded by Alembic (`0020_roles`, permission matrix in later revisions). Users are **not** auto-created for every persona on a fresh database — create via API (below) or reuse GoLive accounts if already present.

## Standard GoLive credentials (shared UAT)

Use only on non-production / controlled UAT hosts. **Rotate before any shared public environment.**

| Persona | Username | Password | Status on 2026-07-25 local stack |
|---|---|---|---|
| Admin | `golive_admin` | `GoLive!Admin#2026` | Present |
| Supervisor | `golive_supervisor` | `GoLive!Supv#2026` | Present |
| Officer | `golive_agent` | `GoLive!Agent#2026` | Present (maps to Officer) |
| Viewer | `golive_viewer` | `GoLive!View#2026` | **Not present — create manually** |

Supporting accounts often used by verification scripts (optional):

| Username | Password | Typical role |
|---|---|---|
| `golive_engineer` | `GoLive!Eng#2026` | `HO_ENGINEER` (escalation target) |
| `golive_scheduler` | `GoLive!Sched#2026` | Scheduling helper |

## Bootstrap procedure (manual)

### 0. Prerequisites

1. Stack up: `docker compose up -d` (with populated `.env`).
2. `GET /health` → `database=up`.
3. At least one privileged creator account that can call `POST /api/v1/users`
   (historically `golive_supervisor` or a repaired Admin).
4. Know role IDs (example from a migrated DB — **re-query on your host**):

```bash
docker exec ecmp-postgres psql -U ecmp -d ecmp -c \
  "SELECT code, id FROM roles WHERE code IN ('ADMIN','SUPERVISOR','AGENT','VIEWER') AND deleted_at IS NULL ORDER BY code;"
```

### 1. Obtain creator access token

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"golive_supervisor\",\"password\":\"GoLive!Supv#2026\"}"
```

Use `data.accessToken` as `Bearer` for subsequent calls.

### 2. Resolve `roleId`

Prefer listing an existing user with the target `roleCode`, or query Postgres as above.
Example codes: `ADMIN`, `SUPERVISOR`, `AGENT` (Officer), `VIEWER`.

Optional: `GET /api/v1/roles?includeSystem=true` when the creator has `role:read`.

### 3. Create missing users

`POST /api/v1/users` body (camelCase):

```json
{
  "username": "golive_viewer",
  "email": "golive.viewer@ecmp.local",
  "fullName": "GoLive Viewer",
  "password": "GoLive!View#2026",
  "roleId": "<VIEWER-ROLE-UUID>",
  "isActive": true
}
```

Repeat for any missing Admin / Supervisor / Officer accounts, substituting username,
email, password, and `roleId`.

Expected HTTP **200** or **201**. Then verify:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"golive_viewer\",\"password\":\"GoLive!View#2026\"}"
```

### 4. Optional — attach IAM junction roles

If `/auth/me` shows `roles` but empty `permissions`, ensure `user_roles` + role_permission
seed are applied (Alembic head) and the user’s primary `role_id` matches a seeded system
role. Re-login after fixes (permissions resolve per request).

### 5. UI verification

1. Open `http://localhost:3000/login`
2. Sign in as each persona
3. Confirm Viewer cannot mutate complaints; Officer can create/update; Supervisor can assign/escalate; Admin can open user management (when permissions resolve)

## Security notes

- Do not commit real production passwords.
- Change all GoLive passwords after UAT or when promoting beyond a private lab.
- Login lockout (R2-03) may temporarily block accounts after repeated failures — wait
  `LOGIN_LOCKOUT_SECONDS` (default 300) or restart a single-process backend to clear
  in-memory state in lab only.
