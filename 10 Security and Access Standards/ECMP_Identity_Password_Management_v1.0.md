# ECMP Identity & Password Management (v1.0)

| Field | Value |
|---|---|
| ID | SEC-PWD-001 |
| Version | 1.0 |
| Status | Implemented |
| Applies to | **Mode A (Lab / Standalone) behavior only** |
| Related | API-410…API-413, Alembic `0037_password_management` |
| Last Review | 2026-07-28 |

> **Scope note:** This document describes **Mode A (Lab / Standalone)** behavior
> only. It records how the local operational surface behaves; it does **not**
> assert ECMP product ownership of authentication, identity, password, or MFA.
> See **Scope & Ownership** below.

## Scope & Ownership

**Enterprise owns** (as product capabilities):

- Authentication
- Identity
- Password
- MFA

**ECMP does NOT own:**

- Password
- Temporary Password
- Reset Password

The password-related capabilities described here (self-service change,
forgot/reset, admin/supervisor temporary reset, password policy) exist **only as
a Mode A operational surface** so the standalone lab can function without the
Enterprise identity provider. They are **not** ECMP product ownership of
identity or password domains. When Enterprise integration is enabled (Mode B),
these responsibilities are served by the Enterprise Platform.

## Summary

**Mode A operational behavior.** In Mode A (Lab / Standalone), ECMP provides a
local operational surface for self-service password change, forgot/reset password
(tokenized), admin/supervisor temporary reset with forced change on next login,
and a configurable password policy.

This is an operational surface for standalone lab/ops use only and is **not**
Enterprise product ownership of authentication, identity, password, or MFA —
those remain owned by the Enterprise Platform (see **Scope & Ownership**).

## APIs

> These endpoints are the **Mode A operational surface** only. They implement
> local password/reset behavior for standalone lab/ops use and do not represent
> ECMP ownership of the identity/password domain (Enterprise-owned).

| ID | Method | Path |
|---|---|---|
| API-412 | POST | `/api/v1/users/me/change-password` |
| API-410 | POST | `/api/v1/auth/forgot-password` |
| API-411 | POST | `/api/v1/auth/reset-password` |
| API-413 | POST | `/api/v1/users/{id}/reset-password` |

## Security decisions

1. **Opaque forgot-password response** — always returns
   “If the account exists, a reset link has been sent.”
2. **Hash-only reset tokens** — `secrets.token_urlsafe` raw token; store
   SHA-256 hash in `password_reset_tokens`; never log raw token or passwords.
3. **Single-use + 15-minute TTL** — expired/reused tokens audited and rejected.
4. **Session invalidation** — password change/reset/admin-reset revokes all
   refresh tokens; access JWTs expire naturally (15 min).
5. **Force password change** — `users.force_password_change`; backend allows
   only `/auth/me`, `/auth/logout`, and change-password until cleared
   (`PASSWORD_CHANGE_REQUIRED`).
6. **Permission** — admin reset requires `users:reset_password` (seeded to
   Admin + Supervisor role codes; Admin `*` also covers it).
7. **Email abstraction** — `EmailService` ABC with `logging` / `noop`
   providers; SMTP/SendGrid/SES/Mailgun are future swaps via `EMAIL_PROVIDER`.
8. **Password policy** — composable rules (`PASSWORD_MIN_LENGTH` default 8);
   reject blank, too short, and same-as-current; extensible for complexity later.
   *(Mode A operational surface only; password policy ownership is Enterprise's.)*
9. **Cookie CSRF posture unchanged** — refresh cookie remains HttpOnly +
   SameSite=Lax; password endpoints use Bearer JSON (not cookie auth) except
   login/refresh/logout.

## Audit events (platform `audit_logs`)

| Event type | When |
|---|---|
| `password.changed` | Successful self-service change |
| `password.change_failed` | Failed self-service change |
| `password.reset_requested` | Reset token issued |
| `password.reset_completed` | Reset succeeded |
| `password.reset_token_expired` | Expired token presented |
| `password.reset_token_reused` | Used token presented |
| `password.admin_reset` | Admin/supervisor reset |

## Schema

### `users.force_password_change`

Boolean, default `false`.

### `password_reset_tokens`

| Column | Notes |
|---|---|
| id | UUID PK |
| user_id | FK → users |
| token_hash | SHA-256 hex (64) |
| expires_at | timestamptz |
| used_at | nullable |
| created_at | timestamptz |

## Configuration

| Env | Default |
|---|---|
| `PASSWORD_MIN_LENGTH` | 8 |
| `PASSWORD_RESET_TOKEN_EXPIRE_MINUTES` | 15 |
| `PASSWORD_RESET_FRONTEND_BASE_URL` | `http://localhost:3000` (dev only) |
| `EMAIL_PROVIDER` | `logging` (dev only) |

Outside `ENVIRONMENT=development`, runtime fail-fast rejects:

- `PASSWORD_RESET_FRONTEND_BASE_URL` containing `localhost` / `127.0.0.1` (or empty)
- `EMAIL_PROVIDER=logging` (use a real provider, or `noop` until SMTP is wired)

## Frontend routes (R6-02B / R6-02C)

| Route | Auth | Purpose |
|---|---|---|
| `/forgot-password` | Public | Request reset email (opaque success) |
| `/reset-password?token=` | Public | Set new password from email link |
| `/change-password` | Authenticated | Self-service / forced change |
| `/users` | Authenticated + `users:read` | User list; Reset password requires `users:reset_password` (API-413) |

When `/auth/me` reports `forcePasswordChange: true`, the UI redirects to
`/change-password` and blocks other app routes until the password is changed.

Admin reset (API-413) returns a **temporary password once** in the API response.
The Users UI shows it in a single dialog (copy / print); closing the dialog
discards it from UI state. Audit event: `password.admin_reset`.

> **Ownership clarification:** Temporary Password and Reset Password described
> above are **Mode A operational behavior** only. ECMP does not own Temporary
> Password or Reset Password as product capabilities — these belong to the
> Enterprise Platform (see **Scope & Ownership**). The description above is
> retained as an implementation reference for the standalone lab surface.
