# Provider Executor Architecture (TASK-059)

| Field | Value |
|---|---|
| ID | ARCH-PROVIDER-EXEC-001 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Tech Lead |
| Approver | Architecture Board (delegated via TASK-059) |
| Status | Approved |
| Last Review | 2026-07-24 |
| Next Review | 2026-10-24 |

## Purpose

Introduce a **generic Provider Executor Foundation** — the execution-contract
layer between `TransportSelector` and future ProviderAdapters.

The executor **validates and prepares** a `ProviderExecutionRequest`.
It must **never** invoke providers, call `send()` / `health()`, or perform
network I/O.

## Principles

1. Single Responsibility — prepare the execution contract only.
2. Open/Closed — future adapters plug in without changing the executor.
3. Preparation ≠ invocation.
4. Immutable execution requests.
5. Must not modify Complaint / Workflow / Execution* / Delivery* /
   Transport* / Notification / Dashboard / KPI.

## Pipeline

```text
DeliveryRequest + TransportAdapter
      │
      ▼
ProviderExecutor.prepare(...)
      ├─ ProviderExecutionValidator
      │     · DeliveryRequest exists
      │     · TransportAdapter exists (isinstance)
      │     · Adapter supports channel (supports() only)
      ├─ Build ProviderExecutionRequest (immutable)
      └─ Return ProviderExecutionResult
            │
            ▼
   Future provider send (TASK-060+) — NOT in scope
```

## Components

| Component | Responsibility |
|---|---|
| `ProviderExecutor` | Validate + build execution request / result |
| `ProviderExecutionRequest` | Immutable contract: execution_id, delivery_request, transport_adapter, context, metadata |
| `ProviderExecutionResult` | success / ready / provider_name / reason |
| `ProviderExecutionValidator` | Shape + adapter compatibility checks |
| `ProviderExecutionPolicy` | `SYNC_PREPARE` only (no async / retry / timeout) |

## Guarantees

- No `adapter.send()` / `health()`
- No HTTP / SMTP / WhatsApp / Firebase / Webhook / Queue
- No DB / scheduler / retry / timeout
- Reject unknown / unsupported adapters and channels
- Immutable requests; no mutable shared state in the contract

## Implementation

- `backend/app/modules/provider_executor/executor.py`
- `backend/app/modules/provider_executor/validator.py`
- `backend/app/modules/provider_executor/models.py`
- DI: `get_provider_executor()`

## Related

- `PROVIDER_EXECUTOR_GUIDE.md`
- `PROVIDER_EXECUTOR_DEVELOPER_GUIDE.md`
- `TRANSPORT_ARCHITECTURE.md`
- `DELIVERY_ENGINE_ARCHITECTURE.md`
- `../../04 Solution Architecture/ECMP_Solution_Architecture_v1.0.md`
