# ECMP Complaint Management Batch 1 — S0 Contract Pack

| Field | Value |
|---|---|
| Document ID | GOV-S0-CM-B1-001 |
| Title | Batch 1 S0 — LOCK RTM + Publish API/Event/TC |
| Version | 1.0 |
| Date | 2026-07-29 |
| Status | 🟢 Complete |
| Scope | FR-001…FR-004 only |

---

## Objective

Close S0 so implementation (S1+) can start against frozen contracts without redesigning FRD.

## Completed

| # | Item | Artifact |
|---|---|---|
| 1 | RTM LOCKED | `26 Traceability/ECMP_RTM_Complaint_Management_Batch1_v1.0.md` |
| 2 | Validation / Coverage → LOCKED | companion RTM reports |
| 3 | Planned OpenAPI Batch 1 | `07 API Catalog/openapi/complaint-management-batch1.v1.yaml` |
| 4 | API inventory API-500…512 | `07 API Catalog/README.md` (Batch 1 section) |
| 5 | Events EVT-CM-001…034 Planned | `08 Event Catalog/events/events.yaml` |
| 6 | 38 TC Planned authored | `13 Test Strategy/ECMP_Test_Case_Catalog_CM_Batch1_v1.0.md` |

## API ID map (logical → catalog)

| Logical (RTM) | Catalog ID | Path |
|---|---|---|
| API-CM-B1-001 | API-500 | `POST /api/v1/cm/complaints` |
| API-CM-B1-002 | API-501 | `GET /api/v1/cm/complaints/{complaintId}` |
| API-CM-B1-003 | API-502 | `POST /api/v1/cm/customers/search` |
| API-CM-B1-004 | API-503 | `POST /api/v1/cm/customers/confirm` |
| API-CM-B1-005 | API-504 | `GET /api/v1/cm/customers/{customerId}/batch1-360` |
| API-CM-B1-006 | API-505 | `POST /api/v1/cm/duplicates/check` |
| API-CM-B1-007 | API-506 | `POST /api/v1/cm/duplicates/decisions` |
| API-CM-B1-008 | API-507 | `POST /api/v1/attachments` (align API-323) |
| API-CM-B1-009 | API-508 | `POST /api/v1/cm/attachments/transfer` |
| API-CM-B1-010 | API-509 | `GET /api/v1/complaints/{id}/attachments` (align API-387) |
| API-CM-B1-011 | API-510 | `GET /api/v1/attachments/{id}` (align API-324) |
| API-CM-B1-012 | API-511 | `GET /api/v1/attachments/{id}/download` (align API-325) |
| API-CM-B1-013 | API-512 | `DELETE /api/v1/attachments/{id}` void semantics (align API-326) |

## Collision note (API-390 / API-392)

| Current use | Disposition |
|---|---|
| Dashboard `GET .../dashboard/queue` + `.../notifications` | **Keep** API-390 / API-392 |
| complaint-domain `POST/GET /api/v1/complaints` | Keep runtime; **ID collision remains** — cite path+method; future DEC may remap domain to API-520+ |
| Batch 1 Aggregate | Uses **API-500+** and `/api/v1/cm/...` — **no collision** |

## Explicit non-changes

- FRD-CM-001 not modified
- Business Rules not modified
- ADR not modified
- Batch 1 scope not expanded
- No application code in S0
- OQ-012/013/014 remain Not Blocking

## Next (S1)

1. Implement FR-002 against API-502…504 + SEC enumeration  
2. Implement FR-001 against API-500/501 + idempotency (no Case)  
3. Execute TC-CM-FR002-* then TC-CM-FR001-*  

---

*End of GOV-S0-CM-B1-001.*
