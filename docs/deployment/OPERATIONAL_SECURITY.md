# Operational Security (SECMIG-P5-005)

| Field | Value |
|---|---|
| ID | OPS-SEC-001 |
| Version | 1.1.0 |
| Date | 2026-07-30 |
| Related | TASK-PLATFORM-SECMIG-P5-005, TASK-PLATFORM-SECMIG-P6-002, `backend/app/core/operational_security.py` |

## Scope

Improve operational security **without** changing authentication architecture,
API envelopes, authorization semantics, audit taxonomy, or Complaint domain
behavior.

## Operations runbooks (P6-002)

| Doc | ID | Use |
|---|---|---|
| [Security Operations Runbook](../../15%20Operations%20Runbook/ECMP_Security_Operations_Runbook_v1.0.md) | OPS-SEC-RB-001 | Auth / lockout / secret / config / deploy incidents |
| [Secret Operations Guide](../../15%20Operations%20Runbook/ECMP_Secret_Operations_Guide_v1.0.md) | OPS-SEC-SEC-001 | Rotate / emergency replace / rollback |
| [Audit Investigation Guide](../../15%20Operations%20Runbook/ECMP_Audit_Investigation_Guide_v1.0.md) | OPS-SEC-AUD-001 | Investigate `security.*` rows |

## Audit flood policy

Source of truth: `AUDIT_FLOOD_POLICY` in `backend/app/core/operational_security.py`.

| Rule | Value |
|---|---|
| Sampling | **No** |
| Async audit workers | **No** |
| Write mode | Synchronous, best-effort (fail-open on write error) |
| Semantics | Unchanged (P5-004 taxonomy / `AuditService`) |
| Mitigation | Edge / reverse-proxy / WAF rate limits |

Abuse storms may amplify durable security-audit writes; auth still fail-closes.

## Retry-After

When an `ApiError` already exposes `details.retryAfterSeconds` (login lockout /
rate-limit), the HTTP response includes `Retry-After` with the same integer
seconds. The JSON body is unchanged.

## Client IP trust boundary

| Layer | Knob | Role |
|---|---|---|
| Uvicorn | `FORWARDED_ALLOW_IPS` | Trust immediate hop for `X-Forwarded-*` → rewrite `request.client` |
| Application | `TRUST_FORWARDED_CLIENT_IP` (default `false`) | Opt-in app-level `X-Forwarded-For` parse |

Login lockout keys and audit `ip_address` use `app.core.client_ip.resolve_client_ip`.

## Runtime security defaults

Documented in `RUNTIME_SECURITY_DEFAULTS` (mirrors Settings defaults):

- `LOGIN_RATE_LIMIT_ENABLED=true`
- `LOGIN_MAX_FAILED_ATTEMPTS=5`
- `LOGIN_LOCKOUT_SECONDS=300`
- `TRUST_FORWARDED_CLIENT_IP=false`
- `FORWARDED_ALLOW_IPS=127.0.0.1` (prod compose typically `*`)
