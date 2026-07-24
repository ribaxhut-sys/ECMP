# Provider Executor — Developer Guide (TASK-059)

| Field | Value |
|---|---|
| ID | ARCH-PROVIDER-EXEC-DEV-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-059) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Package

| Module | Role |
|---|---|
| `executor.py` | `ProviderExecutor` |
| `validator.py` | `ProviderExecutionValidator` |
| `models.py` | Request / Result / Policy |

Do **not** modify Delivery*, Transport*, Execution*, Complaint, Workflow,
Notification, Dashboard, or KPI.

## DI

```text
from app.dependencies.events import get_provider_executor
```

Not auto-invoked from the event path.

## Typical flow

1. DeliveryEngine prepares `DeliveryRequest` (TASK-057).
2. TransportSelector selects `TransportAdapter` (TASK-058).
3. `ProviderExecutor.prepare(delivery_request, adapter)` →
   `(ProviderExecutionRequest|None, ProviderExecutionResult)`.
4. Future layer may call `adapter.send(...)` (TASK-060+) — **not here**.

## Hard rules

- Never call `adapter.send()` or `health()`
- Never perform HTTP / SMTP / WhatsApp / Firebase / Webhook / Queue I/O
- Reject unknown / unsupported adapters
- Keep `ProviderExecutionRequest` immutable
- Policy is `SYNC_PREPARE` only
- No DB / scheduler / retry / timeout

## Tests

```bash
cd backend
pytest tests/test_provider_executor.py tests/test_transport_adapter.py tests/test_delivery_engine.py -q
```

Docker:

```bash
docker compose exec -T backend pytest tests/test_provider_executor.py tests/test_transport_adapter.py tests/test_delivery_engine.py -q
```
