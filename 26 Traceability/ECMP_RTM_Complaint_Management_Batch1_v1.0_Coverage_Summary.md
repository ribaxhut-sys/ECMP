# RTM Coverage Summary — Complaint Management Batch 1

| Field | Value |
|---|---|
| Document ID | GOV-COV-RTM-CM-B1-001 |
| Subject | RTM-CM-B1-001 v1.0 |
| Date | 2026-07-29 |
| Last execution sync | 2026-08-01 — TASK-006-01 @ tip `1608245` |
| Status | 🔒 Design-time RTM LOCKED · 🟢 Executed coverage synced (traceability only) |

---

## Coverage by dimension

| Dimension | In-scope | Covered | Coverage | Notes |
|---|---|---|---|---|
| **BR Coverage** | 11 consumed Batch 1 BRs | 11 | **100%** | 9 catalog BRs deferred (out of Batch 1) |
| **FR Coverage** | FR-001…FR-004 | 4 | **100%** | Full chain present |
| **UC Coverage** | UC-CM-001…009 | 9 | **100%** | |
| **API Coverage** | API-CM-B1-001…013 | 13 | **100%** | 6 Planned capabilities |
| **Domain Coverage** | DM-CM-001…008, 010…012 | 11 | **100%** | DM-CM-009 deferred Batch 2 |
| **Security Coverage** | SEC-CM-* | 33 | **100%** | Each cites originating FR |
| **Test Coverage (planned)** | 38 AC | 38 Planned TC | **100%** | Unchanged |
| **Test Coverage (executed)** | 38 AC | **35 Automated** | **~92%** | TASK-006-01 sync; **3 Pending** (no new tests) |

```text
BR (Batch 1 consumed)     ██████████ 100%
FR                        ██████████ 100%
UC                        ██████████ 100%
API (logical)             ██████████ 100%
Domain (in-scope)         ██████████ 100%
Security                  ██████████ 100%
AC → TC (planned)         ██████████ 100%
AC → TC (executed)        █████████░  ~92%   (was 0% — stale vs suite)
```

---

## Executed coverage sync (TASK-006-01)

Source catalog: `13 Test Strategy/ECMP_Test_Case_Catalog_CM_Batch1_v1.0.md` v1.0.1.

| FR | TC count | Automated | Pending | Manual |
|---|---|---|---|---|
| FR-001 | 12 | 11 | 1 | 0 |
| FR-002 | 9 | 9 | 0 | 0 |
| FR-003 | 8 | 8 | 0 | 0 |
| FR-004 | 9 | 9 | 0 | 0 |
| **Total** | **38** | **37** | **1** | **0** |

### Pending Must TCs (explicit — not Manual)

| TC ID | Reason (repository fact) |
|---|---|
| TC-CM-FR001-09 | Blocked, not a test gap — EVT-CM-005 (`NotificationOutboxEnqueued`) is catalogued **Planned**; no notification-enqueue call exists in the create-complaint path to test. Re-open once EVT-CM-005 ships. |

### Newly automated (this pass)

| TC ID | Test(s) |
|---|---|
| TC-CM-FR001-05 | `test_cm_batch1.py::test_tc_cm_fr001_05_unauthorized_create_rejected` + `test_tc_cm_fr001_05_unauthorized_create_writes_security_audit` (`@requires_postgres`) |
| TC-CM-FR001-08 | `test_cm_batch1.py::test_tc_cm_fr001_08_strict_master_unavailable_create_rejected` |

### Validation (TASK-006-01)

| Check | Result |
|---|---|
| Every TC-CM-* → existing automated node **or** Pending/Manual | **PASS** |
| Every mapped primary node exists in repository | **PASS** (verified against tip suite) |
| Broken references | **0** |
| New tests authored | **0** (out of scope) |
| Runtime / API / DB changes | **None** |

Companion evidence (not counted in 38-TC denominator): GOV-MODEA-M3C-001 §5 suite counts; API-513 `test_api_513_*`; confirm-lock TD-CM-001.

---

### Addendum — 2026-08-04 (Batch-1 Mode A finalization)

The TASK-006-01 validation above is a point-in-time record as of 2026-08-01 and is left unedited. Since that sync:

| Check | Result |
|---|---|
| New tests authored | **2** — `test_tc_cm_fr001_05_unauthorized_create_rejected`, `test_tc_cm_fr001_05_unauthorized_create_writes_security_audit`, `test_tc_cm_fr001_08_strict_master_unavailable_create_rejected` (3 test functions covering 2 TCs) |
| Business logic changed | **None** — both TCs covered existing, already-implemented reject paths (`require_permissions("complaints:create")` at the router; `self._customers.exists(...)` strict-mode check at `service.py` ~L723) |
| TC-CM-FR001-09 | Investigated and found **not implementable without new business logic** (EVT-CM-005 Planned, no notification integration exists) — reclassified from "Pending" to "Blocked, not a test gap"; not authored, per this batch's explicit no-new-features constraint |
| Suite run | `pytest tests/test_cm_batch1.py tests/test_cm_batch1_attachments.py tests/test_cm_batch1_foundation.py tests/test_cm_batch1_customer_provider.py tests/test_cm_batch1_ops_hygiene.py` — 89 passed, 1 skipped (`@requires_postgres`, no live Postgres in this environment) |

Do **not** equate this ~92% TC mapping with G2 case-service pack (103) — dual-tree / dual claim (see Mode A SIT SoT).

---

## Batch 1 FR spine (quick)

| FR | Primary BR | UC count | API count | AC / TC | Executed Automated |
|---|---|---|---|---|---|
| FR-001 Complaint Registration | BR-001 | 5 | 2 | 12 / 12 | 9 / 12 |
| FR-002 Customer Search | BR-002 | 2 | 3 | 9 / 9 | 9 / 9 |
| FR-003 Duplicate Detection | BR-014 | 3 | 2 | 8 / 8 | 8 / 8 |
| FR-004 Attachment Upload | BR-012 | 3 | 6 | 9 / 9 | 9 / 9 |

---

## Not Blocking / Future Decision

| OQ | Topic |
|---|---|
| OQ-CM-B1-012 | Request Id lifetime / TTL |
| OQ-CM-B1-013 | Request Id generation authority |
| OQ-CM-B1-014 | Attachment `TRANSFERRED` semantics |

---

## Gate

| Gate | Status |
|---|---|
| Design-time RTM completeness | **PASS** |
| RTM LOCKED (design) | **Yes (S0)** |
| Execution test coverage (mapped) | **Synced TASK-006-01 — 35/38 Automated; 3 Pending** |
| Execution test coverage (100% Must) | **Open** — remaining Pending need separate testing tasks |

---

## Related

- Master RTM: `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0.md` (§15)
- Validation Report: `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0_Validation_Report.md`
- Test Catalog: `13 Test Strategy/ECMP_Test_Case_Catalog_CM_Batch1_v1.0.md`
- Lab COMPLETE evidence: `18 Architecture Governance/ECMP_PROGRAM_MODE_A_M3C_Module_Lab_COMPLETE_Evidence_Pack_v1.0.md` §5

## Document History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-07-29 | Initial LOCKED design-time summary (executed 0% placeholder) |
| 1.0.1 | 2026-08-01 | TASK-006-01 — sync executed ~92% (35 Automated / 3 Pending); no design RTM unlock |

---

*End of GOV-COV-RTM-CM-B1-001.*
