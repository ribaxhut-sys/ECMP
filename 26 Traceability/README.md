# 26 Traceability


| Field | Value |
|---|---|
| ID | TRC-000 |
| Version | 0.1 |
| Owner | BA Lead / QA Lead |
| Reviewer | Compliance |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Menelusuri hubungan Requirement → Business Rule → FRD → API/Event → Test Case untuk QA dan audit.

## Owner
- Document Owner: BA Lead / QA Lead
- Reviewers: Product Owners, Architecture, Compliance

## Status
Draft

## Minimum Contents (v1)
- [x] Traceability matrix starter
- [ ] Coverage report process
- [ ] ID conventions across artifacts
- [ ] Update rule on every approved change

## ID Conventions
- Blueprint capability/item: `BP-xxx`
- Business Rule: `BR-xxx`
- Functional Requirement: `FRD-xxx` / `FR-xxx`
- API operation: `API-xxx`
- Event: `EVT-xxx`
- Test Case: `TC-xxx`

## Chain
```text
BP → BR → FRD → API/Event → Test Case
```

## Related
- `TRACEABILITY_MATRIX.md`
- `../02 Business Rules`
- `../03 Functional Requirements`
- `../07 API Catalog`
- `../13 Test Strategy`
