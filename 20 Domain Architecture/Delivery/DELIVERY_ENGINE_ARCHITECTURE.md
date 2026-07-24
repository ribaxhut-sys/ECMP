# Delivery Engine Architecture (TASK-057)

| Field | Value |
|---|---|
| ID | ARCH-DELIVERY-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-057) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Introduce a **generic Delivery Engine Foundation** that converts an immutable
`DispatchRequest` into an immutable `DeliveryRequest`.

The engine **prepares** delivery operations only. It must **not** send messages,
call providers, or execute transports.

## Principles

1. Delivery planning ≠ delivery execution.
2. Immutable models; Open/Closed for future policies / providers.
3. Dependency Injection for `DeliveryEngine` / `DeliveryValidator`.
4. Must not call SMTP / WhatsApp / FCM / APNS / SMS / Webhook / AI.
5. Must not modify Complaint / Workflow / Execution* / Notification /
   Dashboard / KPI modules.
6. No persistence, queue, retry, or scheduler.

## Pipeline

```text
DispatchRequest (from ExecutionDispatcher)
                │
                ▼
        DeliveryValidator
          ├─ recipient exists?
          ├─ channel known?
          ├─ template exists?
          └─ payload exists?
                │
                ▼
          DeliveryEngine
          ├─ build DeliveryRequest
          └─ return DeliveryResult
                │
                ▼
     Future transport / provider (TASK-058+) — NOT in scope
```

## Components

| Component | Responsibility |
|---|---|
| `DeliveryRequest` | Immutable prepared delivery unit |
| `DeliveryResult` | success / reason / provider_selected |
| `DeliveryContext` | trace / correlation / tenant / user / metadata |
| `DeliveryPolicy` | **DIRECT** only (no batch, no retry) |
| `DeliveryValidator` | Shape / catalog checks (no provider call) |
| `DeliveryEngine` | Validate + build request |

## Guarantees

- No send / transport / provider invocation
- `provider_selected` remains `None` in foundation
- No DB / queue / scheduler / retry
- No HTTP API
- Rejects unknown channels

## Implementation

- `backend/app/modules/delivery/models.py`
- `backend/app/modules/delivery/validator.py`
- `backend/app/modules/delivery/engine.py`
- DI: `get_delivery_engine()`

## Related

- `DELIVERY_GUIDE.md`
- `DELIVERY_DEVELOPER_GUIDE.md`
- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`
- Execution Dispatcher (`../Execution/EXECUTION_DISPATCHER_ARCHITECTURE.md`)
