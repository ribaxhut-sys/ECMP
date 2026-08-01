# Hardening — 2026-07-31

## Priority execution
1. GitHub push — **BLOCKED** (no PAT / `gh auth` on VPS); local branch ahead of origin.
2. SSH — UFW `22/tcp` changed from `ALLOW` to **`LIMIT`** (rate-limit new connections).
3. Login — backend fixed-window limiter: **10 attempts / 60s / client IP** on `POST /api/v1/auth/login` → HTTP **429** `RATE_LIMITED`.

## Verification
- Live: 10× bad login → 11th returns 429 with `retryAfterSeconds`.
- Unit: `tests/test_rate_limit.py` PASS.
- Legitimate login after backend restart (clears in-memory counters): PASS.
