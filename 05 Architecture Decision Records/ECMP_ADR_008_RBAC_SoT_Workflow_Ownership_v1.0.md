# ECMP_ADR_008_RBAC_SoT_Workflow_Ownership_v1.0

| Field | Value |
|---|---|
| ID | ADR-008 |
| Version | 1.0 |
| Owner | Solution Architect |
| Reviewer | Security Architect / Domain PO ECMF / Administrator |
| Approver | Architecture Board |
| Status | 🟢 Approved |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

- ADR Status: Accepted
- Date: 2026-07-21
- Decision Owners: Solution Architect
- Related Domains: Core Platform, Administration, ECMF

## Context
Dua ambiguitas ownership tercatat di Data Dictionary dan SA §10:
1. Role-Permission Matrix terdaftar di **dua** domain (Core Platform dan Administration).
2. Workflow Config (transisi status Case) belum jelas dimiliki Administration atau Core.

## Decision
1. **Role-Permission Matrix — SoT = Core Platform.** Entitas Role, Permission, Role-Permission, User-Role dimiliki dan ditegakkan Core Platform. **Administration hanya konfigurator** (UI/proses perubahan + approval BR-ADM-01), menulis melalui API Core Platform; tidak menyimpan salinan otoritatif.
2. **Workflow Config — SoT = Administration.** Definisi status & transisi per kategori adalah konfigurasi bisnis (BR-001/BR-ECMF-03), diversion sesuai BR-ADM-03, dipublikasikan via EVT-006 `ConfigChanged`. **ECMF adalah enforcer**: memuat config aktif dan menolak transisi invalid; tidak mendefinisikan transisi sendiri.
3. Audit kedua jenis perubahan wajib (BR-008 / BR-ADM-02) di Core Platform.

## Consequences
- Data Dictionary: tandai Role-Permission di Administration sebagai "config view, non-SoT".
- State machine ECMF (lihat `20 Domain Architecture/ECMF/`) merujuk Workflow Config Administration sebagai sumber transisi.
