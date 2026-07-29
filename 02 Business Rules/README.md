# 02 Business Rules


| Field | Value |
|---|---|
| ID | BR-000 |
| Version | 0.2 |
| Owner | Business Analyst |
| Reviewer | Domain PO |
| Approver | Business Owner |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Mendefinisikan aturan bisnis yang mengikat proses ECMP (workflow, SLA, akses, validasi, closure, reopen).

## Owner
- Document Owner: BA Lead
- Reviewers: Product Owners (ECMF/CRM/KPI), Operations, Compliance

## Status
Approved — katalog enterprise v1.2 baseline (seluruh `[TBD]` ditutup per DEC-004); katalog delivery Sprint-01 Approved (SoT implementasi per DEC-003).

## Documents
- [`ECMP_Business_Rules_Sprint01_v0.1.md`](./ECMP_Business_Rules_Sprint01_v0.1.md) — **SoT delivery** (`BR-0xx`) untuk implementasi/tes/traceability (DEC-003); BR-002/005/006 reserved untuk sprint berikut
- [`ECMP_Business_Rules_v1.0.md`](./ECMP_Business_Rules_v1.0.md) — katalog enterprise referensi (BR-CAT-001, konten v1.2) per domain (Core Platform, CRM, ECMF, KPI, Dashboard, Notification, Administration); nama file mempertahankan baseline mayor v1.0, versi konten lihat header dokumen
- [`ECMP_Business_Rules_Complaint_Management_Module_v1.0.md`](./ECMP_Business_Rules_Complaint_Management_Module_v1.0.md) — **Draft v1.1** katalog modul Complaint (BR-CM-CAT-001): model **Complaint Aggregate → multi Case**, Working Day SLA, eskalasi *No Information Lost* (BR-001…BR-020); **DEC-F4** mengunci jalur Cabang→Pusat, Return (kode+catatan), dan `result_visibility`; menunggu DEC remapping sebelum menggantikan SoT implementasi
- DEC terkait: [`../18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`](../18%20Architecture%20Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md)

## Minimum Contents (v1)
- [x] Rule catalog by domain
- [x] Workflow transition rules (BR-ECMF-03)
- [x] SLA calculation rules (BR-ECMF-05 — formula detail menyusul di `11`)
- [x] Approval / escalation rules (BR-ADM-01, BR-NOTIF-04)
- [ ] Data validation rules (menunggu FRD per domain)
- [x] Exception handling rules (kolom Exception per rule; seluruh `[TBD]` ditutup dengan baseline per DEC-004)

## Template Sections
1. Rule ID & Name
2. Domain / Module
3. Trigger Condition
4. Rule Statement
5. Exception
6. Owner
7. Priority / Severity
8. Configuration vs Hardcoded

## Naming
`ECMP_Business_Rules_<Domain>_vX.Y.xlsx|md|docx`

## Related
- `../01 Business Blueprint`
- `../03 Functional Requirements`
- `../11 SLA and KPI Matrix`
