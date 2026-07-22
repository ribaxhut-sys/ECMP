# UAT Scenario Traceability (Sprint-09)

| Field | Value |
|---|---|
| ID | TRC-UAT-001 |
| Version | 0.1 |
| Owner | QA Lead |
| Reviewer | BA Lead |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-22 |
| Related | UAT-001 v0.2, TC-CAT-001, TRC-DATA-001 |

Acceptance-layer mapping between **UAT scenarios** and **automated test cases**.
Does **not** invent new TC ids — UAT scenarios are a subset of TC-CAT-001.
Normative scenario text lives in `../13 Test Strategy/ECMP_UAT_Plan_v0.2.md` §3 / §3.1.

| UAT | TC | TRC link | Automated evidence |
|---|---|---|---|
| UAT-S1 | TC-001 | TRC-L-001 | `implementation/backend/tests/test_cases.py` (create) |
| UAT-S2 | TC-002 | TRC-L-002 | `implementation/backend/tests/test_cases.py` (get) |
| UAT-S3 | TC-005 | TRC-L-009 | `test_create_persists_audit_and_outbox_in_one_transaction` |
| UAT-S4 | TC-003 | TRC-L-003 | `tests/test_lifecycle.py::test_tc003_*` |
| UAT-S5 | TC-004 | TRC-L-004 | `tests/test_lifecycle.py::test_tc004_invalid_transition_rejected_state_unchanged` |
| UAT-S6 | TC-010 | TRC-L-005 | Deferred (ACR-002) |
| UAT-S7 Close | TC-004 | TRC-L-004 | `test_tc004_close_emits_evt005`, `test_tc004_closed_requires_resolution_code_400`; UI `canApproveClose` |
| UAT-S8 Reject | TC-004 | TRC-L-004 | Workflow `PENDING_REVIEW→IN_PROGRESS`; UI `canReject`; TC-004 status suite |

## Maintenance

1. Update UAT Plan scenario table first (`ECMP_UAT_Plan_v0.2.md`).
2. Keep this file and UAT Plan §3.1 identical for the mapping columns.
3. FR/API/Event SoT remains `traceability.yaml` (synced to `TRACEABILITY_MATRIX.md`).
