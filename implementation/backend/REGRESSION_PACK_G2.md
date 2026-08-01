# G2 Regression Pack (Mode A) — Case Service

| Field | Value |
|---|---|
| ID | G2-REG-001 |
| Status | Adopted (DEC-021) |
| Tree | `implementation/backend` |
| Date | 2026-08-01 |

## Purpose

Named regression pack for G2-S4 exit — authz, illegal transitions (409), list filters, notification stub / outbox drain, contract conformance. Not a full UAT.

## Suite mapping

| Area | Tests |
|---|---|
| Lifecycle assign/status (TC-003/004 analogs) | `tests/test_lifecycle.py` |
| Workflow unit / no CLOSED→REOPENED | `tests/test_workflow_unit.py` |
| Case list API-005 | `tests/test_case_list.py` |
| Notification stub FR-020 | `tests/test_notification_unit.py` |
| Outbox / create path | `tests/test_cases.py` |
| Error envelope | `tests/test_error_envelope.py` |
| Contract vs OpenAPI | `tests/test_contract_conformance.py` |
| Response body contract | `tests/test_response_body_contract.py` |
| Obs / readiness | `tests/test_prod_readiness.py` |
| Settings guards | `tests/test_settings_guard.py` |

## How to run

```bash
cd implementation/backend
./scripts/run_g2_regression.sh
# or: pytest -q tests/
```

## Pass criteria

- Exit code 0  
- No skipped “will fix later” for assign/status/409  
- Contract conformance green against `07 API Catalog/openapi/case-service.v1.yaml`

## Explicitly out of pack

API-010 Customer 360 · Mode B JWT · physical broker · FR-030 event SLA clock · FR-040 dashboard queues (unless separately frozen)
