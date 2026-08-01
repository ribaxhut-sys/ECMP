# ECMP Log Inspection Procedure

| Field | Value |
|---|---|
| ID | OPS-LOG-001 |
| Version | 0.2 |
| Owner | Operations Lead |
| Reviewer | DevOps / Tech Lead Backend / Support Lead |
| Approver | Operations Lead |
| Status | 🟡 Draft |
| Last Review | 2026-07-30 |
| Next Review | 2027-01-21 |
| Related | TS-OBS-001, OPS-RB-001, OPS-SEC-AUD-001, DEP-CHK-001 |

Procedure for inspecting **foundation backend** access/application logs and correlating with `X-Request-ID`. For platform **security audit** rows (`security.*`), prefer [`ECMP_Audit_Investigation_Guide_v1.0.md`](./ECMP_Audit_Investigation_Guide_v1.0.md).

## 1. Foundation log format (canonical)

Root `backend/` uses a text formatter (`backend/app/core/logging.py`), for example:

```text
2026-07-30T10:00:00+0000 | INFO     | app.http | request method=GET path=/ready status=200 duration_ms=1.2 request_id=<uuid>
```

| Signal | Where |
|---|---|
| `request_id` | Substring `request_id=` in the message; also response header `X-Request-ID` |
| Level / logger | `INFO` / `ERROR`, logger name e.g. `app.http`, `app.main` |
| Secrets | Scrubbed via `SecretRedactingFilter` — do not expect raw JWT/DB passwords |

**PII ban:** do not search for or paste case subject/description, tokens, or passwords (TS-OBS-001 §3).

### Historical (slice pack)

Sprint-08 JSON contract for `ecmp-case-service` under **`implementation/backend`** (fields `correlation_id`, `extra.request_id`) remains valid **only** when that pack is running. Marked historical — not the production foundation path.

## 2. Where logs live

| Environment | Source | How to view |
|---|---|---|
| DEV (foundation) | uvicorn / Compose `backend` stdout | `docker compose logs -f backend` |
| CI | GitHub Actions job log | Workflow run |
| SIT/UAT/PROD | Compose / host logging | `docker compose -f docker-compose.prod.yml logs backend`; aggregation TBD (ADR-010) |

## 3. Capture IDs from a response

Foundation middleware echoes **`X-Request-ID`**. Audit metadata may also store `correlationId` (from `X-Correlation-ID` if the client sent it; else equals request id) — see OPS-SEC-AUD-001.

```powershell
curl.exe -sD - -o NUL http://127.0.0.1:8000/ready
# Production:
# curl.exe -sD - -o NUL https://$env:ECMP_DOMAIN/ready
```

Record `X-Request-ID` in the incident ticket.

## 4. Lookup by `request_id` (foundation)

```powershell
$requestId = "<paste-uuid>"
docker compose logs backend 2>&1 | Select-String -SimpleMatch "request_id=$requestId"
```

```bash
rg -F "request_id=<REQUEST_ID>" <<< "$(docker compose logs backend)"
```

## 5. Correlation across calls

If the client propagated `X-Correlation-ID`, query **audit** `metadata.correlationId` (OPS-SEC-AUD-001). Foundation access logs may not print a separate correlation field — use audit for multi-call journeys.

## 6. Diagnosis workflow (support)

1. Obtain response `X-Request-ID` (and AuthN symptom if any).
2. Narrow time window (±5–15 minutes).
3. Search foundation logs for `request_id=…`.
4. For 401/403/429 security patterns → OPS-SEC-RB-001 + audit guide.
5. For 5xx / boot failures → OPS-RB-001 P1/P2.
6. Never paste secrets or raw case free-text into tickets.

## 7. Verification checklist

| # | Check | Pass |
|---|---|---|
| 1 | Can capture `X-Request-ID` from a probe response | Header present |
| 2 | Log line contains matching `request_id=` | Hit in `docker compose logs backend` |
| 3 | No secret material in matched lines | Redacted / absent |
| 4 | Security follow-up uses audit guide when needed | OPS-SEC-AUD-001 |

## Related

- `../21 Technical Standards/ECMP_Observability_Standard_v0.1.md` (TS-OBS-001)
- `./ECMP_Runbook_Slice_v0.1.md` (OPS-RB-001)
- `./ECMP_Audit_Investigation_Guide_v1.0.md` (OPS-SEC-AUD-001)
- Foundation code (reference): `backend/app/core/middleware.py`, `backend/app/core/logging.py`
- **Historical:** `implementation/backend/app/logging_config.py` (JSON slice pack)
