# 26 Traceability


| Field | Value |
|---|---|
| ID | TRC-000 |
| Version | 0.2 |
| Owner | BA Lead / QA Lead |
| Reviewer | Compliance |
| Approver | Architecture Board |
| Status | 🟡 Draft |
| Last Review | 2026-07-22 |
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
BP → BR → FRD → API/Event → Test Case → UAT scenario (acceptance subset)
```

## Related
- `TRACEABILITY_MATRIX.md` — FR/API/Event/TC matrix (synced from `traceability.yaml`)
- `UAT_SCENARIO_TRACEABILITY.md` — UAT ↔ TC ↔ pytest (Sprint-09)
- `../13 Test Strategy/ECMP_UAT_Plan_v0.2.md` — UAT-001 v0.2
- `../02 Business Rules`
- `../03 Functional Requirements`
- `../07 API Catalog`
- `../13 Test Strategy`
