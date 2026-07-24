# Transport Guide (TASK-058)

| Field | Value |
|---|---|
| ID | ARCH-TRANSPORT-GUIDE-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-058) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## What Transport Foundation does

Provides a **provider abstraction**: register adapters, select by channel
from a `DeliveryRequest`.

It does **not** send. It does **not** implement providers.

## Capabilities

| Capability | Notes |
|---|---|
| `EMAIL` | Mapped from DeliveryChannel.EMAIL |
| `WHATSAPP` | Mapped from DeliveryChannel.WHATSAPP |
| `SMS` | Mapped from DeliveryChannel.SMS |
| `PUSH` | Mapped from DeliveryChannel.PUSH |
| `WEBHOOK` | Capability reserved; no DeliveryChannel mapping yet |

`DeliveryChannel.WEBSOCKET` has **no** capability mapping → `UNKNOWN_CHANNEL`.

## Selection outcomes

| Situation | TransportResult |
|---|---|
| Unmapped delivery channel | `supported=False`, `adapter_found=False`, `UNKNOWN_CHANNEL` |
| Mapped but no adapter registered | `supported=True`, `adapter_found=False`, `ADAPTER_NOT_FOUND` |
| Adapter found | `supported=True`, `adapter_found=True`, `ADAPTER_SELECTED` |

## Out of scope

SMTP, Twilio, Meta WhatsApp, Firebase, APNS, Slack, Teams, Webhook clients,
network I/O, DB, queue, retry, HTTP API, calling `send()`.
Provider execution prepare is TASK-059; actual send is TASK-060+.
