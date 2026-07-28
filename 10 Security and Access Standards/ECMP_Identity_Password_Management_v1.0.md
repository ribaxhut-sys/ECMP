# ECMP Identity & Password Management (v1.0)

| Field | Value |
|---|---|
| ID | SEC-PWD-001 |
| Version | 1.0 |
| Status | Implemented |
| Related | API-410…API-413, Alembic `0037_password_management` |
| Last Review | 2026-07-28 |

## Summary

ECMP supports self-service password change, forgot/reset password (tokenized),
admin/supervisor temporary reset with forced change on next login, and a
configurable password policy.

## APIs

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
| `PASSWORD_RESET_FRONTEND_BASE_URL` | `http://localhost:3000` |
| `EMAIL_PROVIDER` | `logging` |
