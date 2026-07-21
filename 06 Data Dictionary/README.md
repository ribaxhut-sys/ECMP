# 06 Data Dictionary


| Field | Value |
|---|---|
| ID | DD-000 |
| Version | 0.1 |
| Owner | Data Architect |
| Reviewer | Security / Compliance |
| Approver | Architecture Board |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Kamus data ECMP: entitas, atribut, tipe, source of truth, retention, dan ownership.

## Owner
- Document Owner: Data Architect / BA Lead
- Reviewers: Solution Architect, Domain POs, Compliance

## Status
Approved (baseline) — v1.0 diselaraskan dengan skema fisik Sprint-01 + FRD-001 v0.2; ERD Sprint-01 tersedia.

## Documents
- [`ECMP_Data_Dictionary_v1.0.md`](./ECMP_Data_Dictionary_v1.0.md) — entity list 35 entity lintas 7 domain, plus detail atribut (Case Header, Customer Reference, Audit Log, Outbox, sketsa Config Version), standar kolom audit, dan naming standard
- [`ECMP_ERD_Sprint01_v0.1.md`](./ECMP_ERD_Sprint01_v0.1.md) — DD-ERD-001, ERD fisik Sprint-01 (cases, audit_log, outbox) + diagram konseptual entitas inti

## Minimum Contents (v1)
- [x] Entity list by domain
- [ ] Attribute definitions (Case Header, Audit Log, Outbox selaras skema fisik Sprint-01; entity lain menyusul saat FRD)
- [x] Source of truth mapping (especially Customer Master)
- [x] PII classification (indikatif, perlu review Compliance)
- [ ] Retention policy reference
- [x] Relationship diagram / ERD link — [`ECMP_ERD_Sprint01_v0.1.md`](./ECMP_ERD_Sprint01_v0.1.md)

## Template Fields (per attribute)
- Entity
- Attribute
- Description
- Data Type
- Mandatory
- Source System
- Owner
- PII/Sensitive (Y/N)
- Sample Value
- Notes

## Naming
`ECMP_Data_Dictionary_vX.Y.xlsx`

## Related
- `../01 Business Blueprint`
- `../03 Functional Requirements`
- `../09 Integration Catalog`
- `../10 Security and Access Standards`
