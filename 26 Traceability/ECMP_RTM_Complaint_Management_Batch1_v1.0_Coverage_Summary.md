# RTM Coverage Summary — Complaint Management Batch 1

| Field | Value |
|---|---|
| Document ID | GOV-COV-RTM-CM-B1-001 |
| Subject | RTM-CM-B1-001 v1.0 |
| Date | 2026-07-29 |
| Status | 🔒 LOCKED |

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
| **Test Coverage (planned)** | 38 AC | 38 Planned TC | **100%** | |
| **Test Coverage (executed)** | 38 AC | 0 | **0%** | Post-RTM QA authoring |

```text
BR (Batch 1 consumed)     ██████████ 100%
FR                        ██████████ 100%
UC                        ██████████ 100%
API (logical)             ██████████ 100%
Domain (in-scope)         ██████████ 100%
Security                  ██████████ 100%
AC → TC (planned)         ██████████ 100%
AC → TC (executed)        ░░░░░░░░░░   0%
```

---

## Batch 1 FR spine (quick)

| FR | Primary BR | UC count | API count | AC / TC |
|---|---|---|---|---|
| FR-001 Complaint Registration | BR-001 | 5 | 2 | 12 / 12 |
| FR-002 Customer Search | BR-002 | 2 | 3 | 9 / 9 |
| FR-003 Duplicate Detection | BR-014 | 3 | 2 | 8 / 8 |
| FR-004 Attachment Upload | BR-012 | 3 | 6 | 9 / 9 |

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
| RTM LOCKED | **Yes (S0)** |
| Execution test coverage | Pending QA (38 TC Planned authored) |

---

## Related

- Master RTM: `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0.md` (§15)
- Validation Report: `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0_Validation_Report.md`

---

*End of GOV-COV-RTM-CM-B1-001.*
