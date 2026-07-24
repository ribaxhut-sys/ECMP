# Provider Contract — Developer Guide (TASK-060)

| Field | Value |
|---|---|
| ID | ARCH-PROVIDER-CONTRACT-DEV-001 |
| Version | 1.0 |
| Owner | Tech Lead |
| Reviewer | Solution Architect |
| Approver | Architecture Board (delegated via TASK-060) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Package

| Module | Role |
|---|---|
| `models.py` | `ProviderResponse`, `ProviderStatus`, `ProviderError`, `ProviderMetadata` |
| `exceptions.py` | `ProviderException` (abstract) |

Do **not** modify Delivery*, Transport*, ProviderExecutor, Execution*,
Complaint, Workflow, Notification, Dashboard, or KPI.

## Usage (future providers)

```text
from app.modules.provider_contract import (
    ProviderResponse,
    ProviderStatus,
    ProviderError,
    ProviderMetadata,
    ProviderException,
)
```

Return `ProviderResponse` from every provider `send()` implementation (TASK-061+).
Subclass `ProviderException` for provider failures — do not invent parallel envelopes.

## Hard rules

- Immutable contracts; never mutate `tags` / metadata in place
- No HTTP / SMTP / WhatsApp / Firebase / Twilio / Webhook in this package
- No DB / scheduler / queue / side effects
- Do not instantiate `ProviderException` directly

## Tests

```bash
cd backend
pytest tests/test_provider_contract.py tests/test_provider_executor.py -q
```

Docker:

```bash
docker compose exec -T backend pytest tests/test_provider_contract.py tests/test_provider_executor.py -q
```
