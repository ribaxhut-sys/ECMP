# Delivery Engine — Developer Guide (TASK-057)

| Field | Value |
|---|---|
| ID | ARCH-DELIVERY-DEV-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-057) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Package

| Module | Role |
|---|---|
| `models.py` | `DeliveryRequest`, `DeliveryResult`, `DeliveryContext`, `DeliveryPolicy`, `DeliveryChannel` |
| `validator.py` | `DeliveryValidator` |
| `engine.py` | `DeliveryEngine` |

Do **not** modify Complaint, Workflow, Execution*, Notification, Dashboard, or KPI for this task.

## DI

```text
from app.dependencies.events import get_delivery_engine
```

Not auto-invoked from the event path.

## Typical flow

1. `ExecutionDispatcher.dispatch(...)` → `DispatchRequest`.
2. `DeliveryEngine.prepare(dispatch)` → `(DeliveryRequest|None, DeliveryResult)`.
3. Future transport / provider consumes `DeliveryRequest` (TASK-058+) — **not here**.

## Hard rules

- Never send mail / push / SMS / WhatsApp / webhook
- Never select or call a provider (`provider_selected` stays `None`)
- Keep `DeliveryRequest` frozen
- Reject unknown channels
- No HTTP / DB / queue / scheduler / retry
- Policy must be `DIRECT`

## Tests

```bash
cd backend
pytest tests/test_delivery_engine.py tests/test_execution_dispatcher.py -q
```

Docker:

```bash
docker compose exec -T backend pytest tests/test_delivery_engine.py tests/test_execution_dispatcher.py -q
```
