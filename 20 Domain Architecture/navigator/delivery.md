# Domain Navigator — Delivery

| Field | Value |
|---|---|
| ID | EOS-NAV-DELIVERY |
| Version | 0.3 |
| Owner | Architecture |
| Reviewer | PMO / Enterprise Architecture |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-24 |
| Next Review | auto |

> Command concept: _Masuk ke domain Delivery_

## Quick Pack

- Domain: `20 Domain Architecture/Delivery/README.md`
- Architecture: `DELIVERY_ENGINE_ARCHITECTURE.md` / `TRANSPORT_ARCHITECTURE.md` / `PROVIDER_EXECUTOR_ARCHITECTURE.md` / `PROVIDER_CONTRACT_ARCHITECTURE.md`
- Guide: `PROVIDER_RESPONSE_GUIDE.md` / developer guides (TASK-057…060)

## API

- — (no HTTP in TASK-057…060)

## Tests

- `backend/tests/test_delivery_engine.py`
- `backend/tests/test_transport_adapter.py`
- `backend/tests/test_provider_executor.py`
- `backend/tests/test_provider_contract.py`

## Active / Related Sprints

- Sprint-16/17 (TASK-057…060 Delivery → Transport → Executor → Contract)

## Notes

Foundations prepare contracts only — never send, never call providers.
