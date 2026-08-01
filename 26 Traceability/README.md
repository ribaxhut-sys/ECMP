# 26 Traceability


| Field | Value |
|---|---|
| ID | TRC-000 |
| Version | 0.3 |
| Owner | BA Lead / QA Lead |
| Reviewer | Compliance |
| Approver | Architecture Board |
| Status | 🟡 Draft (YAML authoritative; matrix synced) |
| Last Review | 2026-08-01 |
| Next Review | 2027-01-21 |

## Purpose
Menelusuri hubungan Requirement → Business Rule → FRD → API/Event → Test Case untuk QA dan audit.

## Owner
- Document Owner: BA Lead / QA Lead
- Reviewers: Product Owners, Architecture, Compliance

## Status
Draft — authoritative machine SoT = `traceability.yaml` (v0.11). Human matrix = `TRACEABILITY_MATRIX.md` (regenerated via `python3 tools/sync_traceability_md.py`). B2-07 re-synced TRC-L-011…016 (CAP-008).

## Minimum Contents (v1)
- [x] Traceability matrix starter
- [x] Decision Traceability Matrix (DTM-001) — architecture decisions ↔ ADR/EA/HOST
- [ ] Coverage report process
- [x] ID conventions across artifacts (partial — dual BR namespace Sprint vs CM noted in B2-07)
- [x] Update rule on every approved change (`sync_traceability_md.py`)

## ID Conventions
- Blueprint capability/item: `BP-xxx`
- Business Rule: `BR-xxx`
- Functional Requirement: `FRD-xxx` / `FR-xxx`
- API operation: `API-xxx`
- Event: `EVT-xxx`
- Test Case: `TC-xxx`
- Architecture decision (DTM): `DTM-D-xxx` / HOST open item `H*` · `K*` · `F*` (see DTM-001)

## Chain
```text
BP → BR → FRD → API/Event → Test Case → UAT scenario (acceptance subset)
```

## Related
- `TRACEABILITY_MATRIX.md` — FR/API/Event/TC matrix (synced from `traceability.yaml`) — **Sprint delivery SoT namespace**
- [`ECMP_DTM_001_Decision_Traceability_Matrix_v0.1.md`](./ECMP_DTM_001_Decision_Traceability_Matrix_v0.1.md) — **DTM-001** Decision Traceability Matrix (ADR ↔ principle ↔ design ↔ HOST gate); companion BOARD-008; **bukan** RTM pengganti
- `ECMP_RTM_Complaint_Management_Batch1_v1.0.md` — **Complaint Aggregate Batch 1 RTM** (RTM-CM-B1-001; 🔒 LOCKED; namespace FRD-CM-001 / BR-CM-CAT-001)
- `ECMP_RTM_Complaint_Management_DEC_F4_v0.1.md` — Draft RTM for FRD-CM-002 / DEC-F4 (RTM-CM-F4-001)
- `ECMP_IMPACT_DEC_F4_v1.0.md` — **Authoritative** impact for DEC-F4 / CM BR-007·008 (EOS `impact --id BR-007` hits Sprint BR namespace — do not use for F4)
- `ECMP_RTM_Complaint_Management_Batch1_v1.0_Validation_Report.md` — RTM validation extract
- `ECMP_RTM_Complaint_Management_Batch1_v1.0_Coverage_Summary.md` — Coverage summary extract
- **CAP-008** Case Management Batch-2 Mode A BCS — `../docs/product/CAP-008_Case_Management_Business_Capability_Specification_v1.0.md` (Residual BQ ZERO; FRD Batch-2 prerequisite READY; DEC-MODEA-B2-001)
- **CAP-008 TRC links:** `TRC-L-011`…`TRC-L-016` in `traceability.yaml` / `TRACEABILITY_MATRIX.md` (FR-CM-B2-001…006 ↔ API-530…535; Approved; lab suite citation — formal TC-catalog IDs deferred)
- Decision pack: `../18 Architecture Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md`
- B2-07 alignment evidence: `../deploy/evidence/B2-07_Repository_Capability_Alignment_20260801.md`
- `UAT_SCENARIO_TRACEABILITY.md` — UAT ↔ TC ↔ pytest (Sprint-09)
- `../13 Test Strategy/ECMP_UAT_Plan_v0.2.md` — UAT-001 v0.2
- `../02 Business Rules`
- `../03 Functional Requirements`
- `../07 API Catalog`
- `../13 Test Strategy`
