# ECMP Capability Register v0.1

| Field | Value |
|---|---|
| ID | BP-CAP-001 |
| Version | 0.1 |
| Owner | Business Analyst |
| Reviewer | Domain Product Owners / Solution Architect |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline) |
| Last Review | 2026-08-01 |
| Next Review | 2027-01-21 |

## Purpose
Register kapabilitas bisnis ECMP dengan ID stabil `CAP-0xx`, dipetakan ke capability statement Blueprint (`BP-0xx`), FR, dan status delivery. Status mengikuti `26 Traceability/traceability.yaml`; register ini tidak boleh menambah kapabilitas di luar Blueprint v2.1 (DEC-001).

## Capability Register

| CAP ID | Nama Kapabilitas | Domain | BP Ref | FR Ref | Status | Owner (PO) |
|---|---|---|---|---|---|---|
| CAP-001 | Case Registration & Retrieval (complaint/inquiry create + get, write-audit) | ECMF / Core Platform | BP-001 | FR-001, FR-001a/b/c, FR-002 | Implemented (Sprint-01 slice, Approved) | Domain PO ECMF |
| CAP-002 | Case Assignment (assign/reassign ke handler/unit) | ECMF | BP-002 | FR-003 | Planned (Sprint-02, menunggu G0 exit per DEC-002) | Domain PO ECMF |
| CAP-003 | Workflow Status Transition (transisi tervalidasi sesuai konfigurasi) | ECMF | BP-002 | FR-004 | Planned (Sprint-02, menunggu G0 exit per DEC-002) | Domain PO ECMF |
| CAP-004 | Customer 360 View (search/view profil read-only + masking) | CRM | BP-003 | FR-010 | Planned (Sprint-02, menunggu G0 exit per DEC-002) | Domain PO CRM |
| CAP-005 | Event-driven Notification (notifikasi assignee/supervisor atas event case) | Notification | BP-004 | FR-020 | Planned (Sprint-02) | Notification PO / Integration Lead |
| CAP-006 | SLA Measurement & Breach Detection (kalkulasi otomatis + EVT-004) | KPI | BP-005 | FR-030 | Planned (Sprint-03) | Performance Owner |
| CAP-007 | Operational Queue Dashboard (monitoring antrian oleh supervisor) | Dashboard | BP-006 | FR-040 | Planned (Sprint-03) | Dashboard PO |
| CAP-008 | Case Management (Batch-2 Mode A) — Create/Add/View/Update/Resolve/Close Case under Complaint Aggregate | ECMF | BP-001 / BR-004 (Batch-2) | FRD-CM-B2-001 (`ECMP_FRD_Case_Management_Batch2_v1.0.md`) Draft v1.0 | Planned (Batch-2 Mode A) — BCS LOCKED; Residual BQ ZERO; FRD Draft v1.0 | Domain PO ECMF |

## Catatan
- **Implemented** = FR ber-status Approved di traceability dan sudah ada di kode (`implementation/backend`). Saat ini hanya slice create/get + write-audit (TRC-L-001/002/009).
- **Planned** = FR ber-status Planned di traceability; implementasi menunggu gate per DEC-002.
- Kapabilitas Branch/HO escalation, Schedule Slot, Appointment, Work Order **tidak terdaftar** karena out of scope (DEC-001).
- **CAP-008** registered 2026-08-01 per DEC-MODEA-B2-001 / BQ-012. Former working ID `CAP-02` retired to avoid collision with **CAP-002** Case Assignment (unchanged). BCS: `../docs/product/CAP-008_Case_Management_Business_Capability_Specification_v1.0.md`. FRD: `../03 Functional Requirements/ECMP_FRD_Case_Management_Batch2_v1.0.md` (FRD-CM-B2-001 Draft v1.0).

## Related
- `ECMP_Business_Blueprint_v2.1_MD_Extract.md` (BP-EXT-001) §4 Capability Map
- `../26 Traceability/traceability.yaml`
- `../03 Functional Requirements/README.md`
