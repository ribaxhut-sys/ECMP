# 11 SLA and KPI Matrix


| Field | Value |
|---|---|
| ID | SLA-000 |
| Version | 0.1 |
| Owner | Operations Lead |
| Reviewer | Business Owner |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Definisi SLA dan KPI ECMP: formula, target, owner, sumber data, dan cara pengukuran.

## Owner
- Document Owner: Operations Lead / Performance Owner
- Reviewers: Business Owner, BA Lead, Domain POs

## Status
Approved (baseline) — target numerik SLA ditutup per DEC-005; target KPI dictionary sebagian masih `[TBD]`

## Documents
- [`ECMP_KPI_Dictionary_v1.0.md`](./ECMP_KPI_Dictionary_v1.0.md) — 26 KPI/SLA lintas 7 domain dengan formula dan data source
- [`ECMP_SLA_Matrix_v0.1.md`](./ECMP_SLA_Matrix_v0.1.md) — SLA-MTX-001, matriks SLA case type × priority dengan target numerik baseline DEC-005

## Minimum Contents (v1)
- [x] SLA matrix by category/priority (nilai baseline per DEC-005 — lihat `ECMP_SLA_Matrix_v0.1.md`)
- [ ] Business calendar / working hours rules — baseline 24x7 (DEC-004/BR-ECMF-05); kalender kerja = konfigurasi SLA fase berikut
- [x] KPI dictionary (definition + formula)
- [x] Target per period/unit (SLA: baseline per DEC-005; target KPI dictionary sebagian masih `[TBD]`)
- [x] Breach & escalation thresholds (baseline per DEC-005: breach = melewati due → EVT-004; warning 80%)
- [x] Data source mapping to ECMF events

## Template Fields
- Metric ID
- Metric Name
- Type (SLA / KPI)
- Definition
- Formula
- Target
- Unit
- Measurement Window
- Data Source
- Owner
- Dashboard Consumer

## Naming
`ECMP_SLA_Matrix_vX.Y.xlsx`  
`ECMP_KPI_Dictionary_vX.Y.xlsx`

## Related
- `../02 Business Rules`
- `../03 Functional Requirements`
- `../08 Event Catalog`
