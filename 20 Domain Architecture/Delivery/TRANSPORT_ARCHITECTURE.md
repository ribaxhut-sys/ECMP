# Transport Adapter Architecture (TASK-058)

| Field | Value |
|---|---|
| ID | ARCH-TRANSPORT-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-058) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Introduce a **generic Transport Adapter Foundation** — the provider abstraction
layer for future delivery transports.

Adapters are **registered and selected** only. No provider implementation.
No network communication. `send()` must never be called by this foundation.

## Principles

1. Interface Segregation — `TransportAdapter` contract is minimal.
2. Open/Closed — new providers implement the same interface; registry grows.
3. Selection ≠ execution.
4. Must not implement SMTP / Twilio / Meta WhatsApp / Firebase / APNS /
   Slack / Teams / Webhook clients.
5. Must not modify Complaint / Workflow / Execution* / DeliveryEngine /
   DeliveryValidator / DeliveryRequest / Notification / Dashboard / KPI.

## Pipeline

```text
DeliveryRequest
      │
      ▼
TransportSelector
      ├─ map channel → TransportCapability
      ├─ TransportRegistry.lookup(channel)
      └─ return (TransportAdapter|None, TransportResult)
            │
            ▼
   ProviderExecutor.prepare (TASK-059) → future send (TASK-060+)
```

## Components

| Component | Responsibility |
|---|---|
| `TransportAdapter` | Abstract interface: `supports` / `send` / `health` |
| `TransportRegistry` | Register + lookup by channel (no execution) |
| `TransportSelector` | Choose adapter for `DeliveryRequest` |
| `TransportCapability` | EMAIL · WHATSAPP · SMS · PUSH · WEBHOOK |
| `TransportResult` | supported / adapter_found / adapter_name / reason |

## Guarantees

- No `adapter.send()` / `health()` from registry or selector
- No network I/O
- No DB / queue / retry
- No HTTP API
- Unknown / unmapped channels rejected

## Implementation

- `backend/app/modules/transport/adapter.py`
- `backend/app/modules/transport/registry.py`
- `backend/app/modules/transport/selector.py`
- `backend/app/modules/transport/models.py`
- DI: `get_transport_registry()`, `get_transport_selector()`

## Related

- `TRANSPORT_GUIDE.md`
- `TRANSPORT_DEVELOPER_GUIDE.md`
- `../Delivery/DELIVERY_ENGINE_ARCHITECTURE.md`
- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`
