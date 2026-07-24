# Delivery Guide (TASK-057)

| Field | Value |
|---|---|
| ID | ARCH-DELIVERY-GUIDE-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-057) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## What Delivery Engine does

Converts `DispatchRequest` → `DeliveryRequest` + `DeliveryResult`.

It prepares a delivery plan. It does **not** deliver.

## Policy

| Policy | Supported (TASK-057) |
|---|---|
| `DIRECT` | Yes (default) |
| Batching | No |
| Retry | No |

## Known channels

`EMAIL` · `WHATSAPP` · `PUSH` · `SMS` · `WEBSOCKET`

Unknown channels are rejected (`INVALID_CHANNEL`).

## DispatchRequest → DeliveryRequest mapping

| Delivery field | Source |
|---|---|
| `request_id` | New UUID |
| `dispatch_request_id` | `DispatchRequest.task_id` |
| `channel` | `configuration.channel` or parse `target` (`channel:email`) |
| `recipient` | `configuration.recipient` |
| `template_id` | `configuration.template_id` / `templateId` / `template` |
| `payload` | `configuration.payload` (must be a mapping) |
| `context` | Mapped from `DispatchRequest.context` → `DeliveryContext` |
| `metadata` | Diagnostic (`runId`, `taskType`, `target`, `policy`) |

## Validation failures

| Reason prefix | Meaning |
|---|---|
| `INVALID_RECIPIENT` | Missing / empty recipient |
| `INVALID_CHANNEL` | Missing or unknown channel |
| `INVALID_TEMPLATE` | Missing / empty template id |
| `INVALID_PAYLOAD` | Missing payload or not a mapping |

## Out of scope

SMTP, WhatsApp, FCM, APNS, SMS gateway, Webhook, AI, DB, queue, retry, scheduler, HTTP API.
