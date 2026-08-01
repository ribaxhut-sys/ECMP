# ECMP Audit Investigation Guide

| Field | Value |
|---|---|
| ID | OPS-SEC-AUD-001 |
| Version | 1.0.0 |
| Date | 2026-07-30 |
| Owner | Security Architect / Operations Lead |
| Status | 🟢 Active (foundation stack) |
| Task | TASK-PLATFORM-SECMIG-P6-002 |
| Scope | Platform `audit_logs` security events + request correlation |
| Out of scope | Redesign of audit writers; SIEM product; Complaint timeline |

## 1. Purpose

How to investigate security-relevant activity on the **foundation** backend after SECMIG-P5-004 (taxonomy) and P5-005 (ops defaults).

Runtime audit behavior is unchanged: synchronous, append-only, **fail-open** on write error (missing rows possible under DB distress).

## 2. Security event taxonomy

Source: `backend/app/modules/audit/security_events.py` → `SecurityEventType`.

| `event_type` (stored) | Meaning | Typical HTTP |
|---|---|---|
| `security.login_failed` | Failed login attempt | 401 |
| `security.token_rejected` | Bearer/JWT rejected | 401 |
| `security.permission_denied` | Authenticated but not authorized | 403 |
| `security.lockout` | Login lockout triggered | 429 (with retry hint) |

`entity_type` for these rows is `Security`. Actions map via `SECURITY_EVENT_ACTIONS` (login/update).

Do not invent new `event_type` strings in tickets; use the table above.

## 3. Trace identifiers

| Id | Where | Notes |
|---|---|---|
| `requestId` | Audit `metadata` JSON; HTTP response / access log | Foundation middleware sets/echoes `X-Request-ID` |
| `correlationId` | Audit `metadata` JSON | From `X-Correlation-ID` / `X-Correlation-Id` when present; else equals `requestId` |
| Access log `request_id` | Backend stdout (text formatter) | Same id as `X-Request-ID` when middleware ran |

> **Historical:** OPS-LOG-001 originally documented JSON logs for `implementation/backend` (`ecmp-case-service`). Foundation logs are **text lines** including `request_id=…`. Prefer this guide + current OPS-LOG-001 for foundation; treat implementation JSON examples as historical unless that pack is running.

### Capture from HTTP

```powershell
curl.exe -sD - -o NUL https://$env:ECMP_DOMAIN/ready
# Record X-Request-ID from response headers
```

Ask reporters for the **response** `X-Request-ID` from the failing call.

## 4. Audit log store

| Item | Detail |
|---|---|
| Table | `audit_logs` (platform; append-only) |
| Useful columns | `event_type`, `entity_type`, `actor_id`, `ip_address`, `user_agent`, `metadata`, `created_at` |
| Metadata keys | `requestId`, `correlationId`, often `path` |
| API | Authorized list endpoint under audit module (use with least privilege) |

Legacy `audit_logs_legacy` is out of scope for this security taxonomy.

## 5. Investigation workflow

1. **Scope the window** — UTC start/end (±15 minutes around report unless storm).
2. **Collect ids** — `X-Request-ID`; optional correlation; user id / username if known (no passwords).
3. **Query by event_type** (DB example):

```sql
SELECT created_at, event_type, actor_id, ip_address,
       metadata->>'requestId' AS request_id,
       metadata->>'correlationId' AS correlation_id,
       metadata->>'path' AS path
FROM audit_logs
WHERE event_type LIKE 'security.%'
  AND created_at >= :window_start
  AND created_at < :window_end
ORDER BY created_at DESC
LIMIT 500;
```

4. **Pivot on requestId**

```sql
SELECT created_at, event_type, ip_address, metadata
FROM audit_logs
WHERE metadata->>'requestId' = :request_id
ORDER BY created_at;
```

5. **Pivot on correlationId** (multi-call journeys when client sent `X-Correlation-ID`):

```sql
SELECT created_at, event_type, metadata->>'requestId' AS request_id, metadata
FROM audit_logs
WHERE metadata->>'correlationId' = :correlation_id
ORDER BY created_at;
```

6. **Correlate logs** — search backend container logs for the same `request_id=` (foundation text logs).
7. **Classify** — single user error vs lockout storm (SEC-P2) vs systemic AuthN (SEC-P1) vs compromise (SEC-P3).
8. **Escalate** per OPS-SEC-RB-001; do not paste secrets or raw tokens into tickets.

### Histogram (storm triage)

```sql
SELECT event_type, count(*) AS n
FROM audit_logs
WHERE event_type LIKE 'security.%'
  AND created_at >= :window_start
  AND created_at < :window_end
GROUP BY event_type
ORDER BY n DESC;
```

## 6. Evidence collection

- [ ] Ticket / incident id
- [ ] Time window (UTC)
- [ ] List of `requestId` / `correlationId` values
- [ ] `event_type` counts
- [ ] Sample row ids (UUID pk) — not full PII
- [ ] IP set (if abuse)
- [ ] App `ENVIRONMENT`, `ECMP_AUTH_MODE`, image tag
- [ ] Whether audit write failures appeared in logs (`failed to persist security audit event`)

**Integrity note:** Fail-open means absence of a row is **not** proof the event never occurred. Cross-check access logs.

**PII:** Prefer ids; avoid exporting user agents wholesale to public channels; follow TS-OBS / security standards.

## 7. Related

- [`./ECMP_Security_Operations_Runbook_v1.0.md`](./ECMP_Security_Operations_Runbook_v1.0.md)
- [`./ECMP_Log_Inspection_Procedure_v0.1.md`](./ECMP_Log_Inspection_Procedure_v0.1.md) (OPS-LOG-001)
- [`../docs/deployment/OPERATIONAL_SECURITY.md`](../docs/deployment/OPERATIONAL_SECURITY.md)
- Code (read-only reference): `backend/app/modules/audit/security_events.py`
