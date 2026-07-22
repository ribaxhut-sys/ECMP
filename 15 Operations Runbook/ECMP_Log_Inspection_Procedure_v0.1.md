# ECMP Structured Log Inspection Procedure

| Field | Value |
|---|---|
| ID | OPS-LOG-001 |
| Version | 0.1 |
| Owner | Operations Lead |
| Reviewer | DevOps / Tech Lead Backend / Support Lead |
| Approver | Operations Lead |
| Status | 🟡 Draft |
| Last Review | 2026-07-22 |
| Next Review | 2027-01-21 |
| Related | TS-OBS-001, OPS-RB-001, DEP-CHK-001 |

Dedicated procedure for inspecting **structured JSON logs** from `ecmp-case-service` (Sprint-08 logging). Aligns with `21 Technical Standards/ECMP_Observability_Standard_v0.1.md` (TS-OBS-001) and runtime middleware (`X-Request-ID`, `X-Correlation-ID`).

## 1. Log format (contract)

Each application/access line is **one JSON object** on stdout (no multi-line free text).

| Field | Location | Notes |
|---|---|---|
| `timestamp` | top-level | UTC ISO-8601 with `Z` |
| `level` | top-level | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `service` | top-level | `ecmp-case-service` |
| `correlation_id` | top-level | From `X-Correlation-ID`, or equals `request_id` if header absent |
| `message` | top-level | Short, **no PII** |
| `extra.request_id` | under `extra` | From `X-Request-ID` (generated UUID if client omitted it) |
| `extra.method` / `path` / `status_code` / `duration_ms` | under `extra` | Access log (`request completed`) |

Example (illustrative):

```json
{"timestamp":"2026-07-22T10:00:00.000Z","level":"INFO","service":"ecmp-case-service","correlation_id":"corr-abc","message":"request completed","extra":{"request_id":"req-abc","method":"POST","path":"/v1/cases","status_code":201,"duration_ms":12.5}}
```

**PII ban (always):** do not expect or search for `subject`, `description`, customer name/contact, or bearer tokens in logs (TS-OBS-001 §3).

## 2. Where logs live (today)

| Environment | Source | How to view |
|---|---|---|
| DEV | uvicorn stdout in the terminal | Scroll / redirect to file when reproducing |
| CI | GitHub Actions job log | Open workflow run → pytest/uvicorn steps |
| SIT/UAT/PROD | Planned (ADR-010) | Same JSON contract; aggregation tool TBD at activation |

## 3. Capture IDs from a response

Every successful middleware path echoes:

- Response header `X-Request-ID`
- Response header `X-Correlation-ID` (defaults to request id when client did not send correlation)

```powershell
# Example — capture headers from health (no auth)
curl.exe -sD - -o NUL http://127.0.0.1:8000/health
```

Record both values in the incident ticket before diving into logs.

## 4. Lookup by `request_id`

`request_id` is stored as `extra.request_id` in JSON lines.

**PowerShell (local file or redirected stdout):**

```powershell
# $logFile = path to captured stdout (one JSON object per line)
$requestId = "req-sprint09-example"
Get-Content $logFile | ForEach-Object {
  try { $_ | ConvertFrom-Json } catch { $null }
} | Where-Object {
  $_.extra.request_id -eq $requestId -or $_.extra.request_id -eq $requestId
}
```

**ripgrep (any OS with `rg`):**

```bash
rg -F '"request_id":"<REQUEST_ID>"' /path/to/logfile.jsonl
```

Expect at least the `request completed` access line for that HTTP call; ERROR lines for the same request share the same ids when emitted inside the request context.

## 5. Lookup by `correlation_id`

`correlation_id` is a **top-level** JSON field. Use it to group related calls when the client propagates `X-Correlation-ID` across retries or portal→API hops (propagation to other services is Planned until ADR-009 consumers exist).

```powershell
$correlationId = "corr-sprint09-example"
Get-Content $logFile | ForEach-Object {
  try { $_ | ConvertFrom-Json } catch { $null }
} | Where-Object { $_.correlation_id -eq $correlationId }
```

```bash
rg -F '"correlation_id":"<CORRELATION_ID>"' /path/to/logfile.jsonl
```

**Rule of thumb:** if the client sent only `X-Request-ID`, `correlation_id == request_id` for that call — searching either id finds the same access line.

## 6. Diagnosis workflow (support)

1. Obtain failing `caseId` (if any) and response headers `X-Request-ID` / `X-Correlation-ID` from the client or API collection.
2. Narrow time window (±5 minutes around the failure).
3. Lookup by `request_id` first (single call); escalate to `correlation_id` if the journey spans multiple calls.
4. Confirm `extra.path`, `extra.status_code`, and `level` — map 4xx/5xx to OPS-RB-001 playbooks (auth → check token/permissions; 5xx → P1/P2).
5. If no matching line: verify the process writing logs is the same instance that served the request; confirm the client copied headers from the **same** response.
6. **Never** paste raw case `subject`/`description` into tickets from DB dumps when correlating — use ids only.

## 7. Verification checklist

| # | Check | Pass |
|---|---|---|
| 1 | Log line parses as JSON | `ConvertFrom-Json` / `jq` succeeds |
| 2 | Required fields present | `timestamp`, `level`, `service`, `message` |
| 3 | Id lookup works | Hit on `correlation_id` and/or `extra.request_id` |
| 4 | No PII in matched lines | No subject/description/token values |

## Related

- `../21 Technical Standards/ECMP_Observability_Standard_v0.1.md` (TS-OBS-001)
- `./ECMP_Runbook_Slice_v0.1.md` (OPS-RB-001) — incident playbooks
- `../14 Deployment Standards/ECMP_Production_Deployment_Checklist_v0.1.md` (DEP-CHK-001 §3)
- Implementation: `implementation/backend/app/logging_config.py`, `implementation/backend/app/middleware.py`
