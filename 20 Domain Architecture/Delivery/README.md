# Domain Architecture — Delivery

| Field | Value |
|---|---|
| ID | DOM-DELIVERY-001 |
| Version | 1.1 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-057…059) |
| Status | 🟢 Approved (TASK-057…060 delivery / transport / executor / contract foundations) |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Objective

Shared **Delivery + Transport + Provider Executor foundations**: prepare
`DeliveryRequest` from `DispatchRequest`, select a `TransportAdapter` by
channel, then prepare a `ProviderExecutionRequest` contract.

No send. No provider implementations. No network.

## Bounded Context

| Concept | Role |
|---|---|
| Delivery Engine (TASK-057) | Validate + build `DeliveryRequest` |
| Transport Adapter (TASK-058) | Provider abstraction + registry + selector |
| Provider Executor (TASK-059) | Validate + build execution contract |
| Provider Contract (TASK-060) | Standard response / error / metadata models |
| Future provider send | Execute delivery (TASK-061+) |

## In Scope (TASK-060)

- `ProviderResponse`, `ProviderStatus`, `ProviderError`, `ProviderMetadata`
- Abstract `ProviderException`
- Contracts only

## Out of Scope (STOP)

- SMTP / Twilio / Meta WhatsApp / Firebase / APNS / Slack / Teams / Webhook
- Calling `adapter.send()` / `health()` / network I/O
- Persistence / queue / retry / timeout / async
- Changes to Delivery* / Transport* / ProviderExecutor / Execution* /
  Complaint* / Workflow* / Notification* / Dashboard* / KPI*
- TASK-061+

## Key Flow

```text
DispatchRequest → DeliveryEngine → DeliveryRequest
                                        │
                                        ▼
                              TransportSelector + Registry
                                        │
                                        ▼
                         TransportAdapter (selected)
                                        │
                                        ▼
                              ProviderExecutor.prepare
                                        │
                                        ▼
              ProviderExecutionRequest + ProviderExecutionResult
                                        │
                                        ▼
                    Provider Contract (ProviderResponse …)
                                        │
                                        ▼
                         Future provider adapters (TASK-061+)
```

## Related

- `DELIVERY_ENGINE_ARCHITECTURE.md`
- `DELIVERY_GUIDE.md`
- `DELIVERY_DEVELOPER_GUIDE.md`
- `TRANSPORT_ARCHITECTURE.md`
- `TRANSPORT_GUIDE.md`
- `TRANSPORT_DEVELOPER_GUIDE.md`
- `PROVIDER_EXECUTOR_ARCHITECTURE.md`
- `PROVIDER_EXECUTOR_GUIDE.md`
- `PROVIDER_EXECUTOR_DEVELOPER_GUIDE.md`
- `PROVIDER_CONTRACT_ARCHITECTURE.md`
- `PROVIDER_RESPONSE_GUIDE.md`
- `PROVIDER_CONTRACT_DEVELOPER_GUIDE.md`
- `../Execution/EXECUTION_DISPATCHER_ARCHITECTURE.md`
