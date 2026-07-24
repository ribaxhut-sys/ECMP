# Transport Adapter — Developer Guide (TASK-058)

| Field | Value |
|---|---|
| ID | ARCH-TRANSPORT-DEV-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-058) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Package

| Module | Role |
|---|---|
| `adapter.py` | `TransportAdapter` ABC |
| `models.py` | `TransportCapability`, `TransportResult` |
| `registry.py` | `TransportRegistry` |
| `selector.py` | `TransportSelector` |

Do **not** modify DeliveryEngine, DeliveryValidator, DeliveryRequest,
Execution*, Complaint, Workflow, Notification, Dashboard, or KPI.

## DI

```text
from app.dependencies.events import get_transport_registry, get_transport_selector
```

Not auto-invoked from the event path. No adapters are pre-registered.

## Typical flow

1. DeliveryEngine prepares `DeliveryRequest` (TASK-057).
2. `TransportSelector.select(request)` → `(adapter|None, TransportResult)`.
3. ProviderExecutor prepares the execution contract (TASK-059). Future send is TASK-060+.

## Implementing a future provider

Subclass `TransportAdapter`, implement `name`, `supports`, `send`, `health`,
then `registry.register(adapter)`. Do not call `send()` from TASK-058 code.

## Hard rules

- Never call `adapter.send()` or `health()` from registry/selector
- Reject unknown / unmapped channels
- Keep `DeliveryRequest` immutable
- No network / DB / queue / retry / HTTP

## Tests

```bash
cd backend
pytest tests/test_transport_adapter.py tests/test_delivery_engine.py -q
```

Docker:

```bash
docker compose exec -T backend pytest tests/test_transport_adapter.py tests/test_delivery_engine.py -q
```
