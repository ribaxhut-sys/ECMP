# Provider Executor Guide — Execution Model (TASK-059)

| Field | Value |
|---|---|
| ID | ARCH-PROVIDER-EXEC-GUIDE-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-059) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## What Provider Executor does

Coordinates **provider execution preparation**: given a `DeliveryRequest`
and a selected `TransportAdapter`, it validates compatibility and builds an
immutable `ProviderExecutionRequest`.

It does **not** send. It does **not** invoke providers.

## Execution model

| Aspect | Foundation behavior |
|---|---|
| Policy | `SYNC_PREPARE` only |
| Async | Not supported |
| Retry | Not supported |
| Timeout | Not supported |
| Persistence | None |
| Scheduler | None |
| Network | Forbidden |

## Outcomes

| Situation | ProviderExecutionResult |
|---|---|
| Valid request + compatible adapter | `success=True`, `ready=True`, `EXECUTION_READY` |
| Missing DeliveryRequest | `success=False`, `ready=False`, `MISSING_DELIVERY_REQUEST` |
| Missing adapter | `success=False`, `ready=False`, `MISSING_TRANSPORT_ADAPTER` |
| Not a TransportAdapter | `success=False`, `ready=False`, `UNKNOWN_ADAPTER` |
| Unmapped channel (e.g. WEBSOCKET) | `success=False`, `ready=False`, `UNSUPPORTED_CHANNEL` |
| Adapter does not support channel | `success=False`, `ready=False`, `ADAPTER_CHANNEL_MISMATCH` |

## Out of scope

Calling `send()` / `health()`, SMTP, HTTP, WhatsApp, Firebase, Webhook,
queue, DB, retry, timeout, async, TASK-060+.
