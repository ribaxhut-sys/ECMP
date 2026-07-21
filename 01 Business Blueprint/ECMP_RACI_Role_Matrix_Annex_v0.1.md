# ECMP RACI & Role Matrix Annex v0.1

| Field | Value |
|---|---|
| ID | BP-RACI-001 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | PMO / Security Officer |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Lampiran Blueprint yang merangkum (1) RACI lifecycle artefak enterprise dan (2) aktor bisnis ECMP. Permission teknis (permission string, enforcement point) **bukan** di dokumen ini — SoT-nya `10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md` (SEC-RAM-001).

## 1. RACI — Lifecycle Artefak

Legenda: R = Responsible, A = Accountable, C = Consulted, I = Informed.

| Artefak | BA Lead | Domain PO | Solution Architect | Business Owner | Architecture Board | PMO | Engineering |
|---|---|---|---|---|---|---|---|
| Business Blueprint (`01`) | R | C | C | A | C | I | I |
| Business Rules (`02`) | R | C | C | A | I | I | I |
| FRD (`03`) | R | C | C | A | I | I | C |
| ADR (`05`) | I | C | R | I | A | I | C |
| Project Decision / DEC (`27`) | C | C | C | A* | C | R | I |
| Rilis / Release (`16`) | I | C | C | A | I | C | R |

\* Approver DEC dapat didelegasikan sesuai jenis keputusan (lihat header masing-masing DEC; mis. DEC-001 di-approve Architecture Board).

## 2. Aktor Bisnis

| Aktor | Deskripsi | Fokus Utama | Catatan Permission |
|---|---|---|---|
| CS Agent | Petugas customer service garis depan | Membuat case, melihat case/customer 360, mencatat interaksi | `cases:create`, `cases:read` (lihat SEC-RAM-001) |
| Supervisor | Pengawas unit penanganan | Assignment/reassignment, review antrian & SLA unit, approve closure/reopen di unitnya | Planned — permission menyusul saat FR-003/FR-004 dibangun (Sprint-02) |
| Manager | Manajemen operasional lintas unit | Monitoring KPI/SLA, eskalasi, laporan | Planned (Sprint-03, dashboard/KPI) |
| Administrator | Pengelola konfigurasi platform | Workflow/SLA/role-permission config (dengan approval BR-ADM-01), override tercatat (BR-CP-02) | Planned; semua aksi diaudit (BR-ADM-02) |
| Executive | Pimpinan | Konsumsi dashboard eksekutif read-only | Planned (Sprint-03) |

Role teknis Sprint-01 yang benar-benar ada di kode hanya **CS Agent** dan **Viewer** (SEC-RAM-001). Aktor lain adalah aktor bisnis target dan tidak boleh diimplementasikan sebelum matriks di folder `10` direvisi.

## Related
- `ECMP_Business_Blueprint_v2.1_MD_Extract.md` §7 Governance
- `../10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md`
- `../27 Project Decisions/` (DEC-001..004)
