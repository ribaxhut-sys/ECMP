# ECMP Personas & Journeys v0.1

| Field | Value |
|---|---|
| ID | UX-001 |
| Version | 0.1 |
| Owner | UX Lead |
| Reviewer | BA Lead / Domain POs |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

> **Catatan UI: deferred.** Frontend produk adalah non-goal Sprint-0/G0 (DEC-002) dan belum di-ADR-kan. Dokumen ini mendefinisikan persona dan *service journey* (level layanan/API), bukan screen spec. Screen inventory menyusul setelah keputusan frontend.

## 1. Personas

### P-01 CS Agent
| Aspek | Deskripsi |
|---|---|
| Peran | Petugas customer service garis depan |
| Tujuan | Meregistrasi complaint/inquiry cepat & akurat; melihat konteks pelanggan saat menangani |
| Frustrasi | Input berulang, konteks pelanggan terpencar, tidak tahu status lanjutan case |
| Interaksi ECMP | Create case, get case, customer 360 (unmasked kontak — role CS per BR-CRM-02 baseline) |
| Permission (slice) | `cases:create`, `cases:read` (SEC-RAM-001) |

### P-02 Supervisor
| Aspek | Deskripsi |
|---|---|
| Peran | Pengawas unit penanganan |
| Tujuan | Distribusi beban adil, SLA unit terjaga, tidak ada case terlantar |
| Frustrasi | Tidak terlihat antrian real-time; eskalasi terlambat |
| Interaksi ECMP | Assign/reassign (FR-003), monitor antrian (FR-040), terima eskalasi notifikasi gagal (BR-NOTIF-04 baseline) |
| Permission | Planned — menunggu revisi Role Access Matrix (Sprint-02) |

### P-03 Administrator
| Aspek | Deskripsi |
|---|---|
| Peran | Pengelola konfigurasi platform |
| Tujuan | Mengubah proses via konfigurasi (configuration-first) tanpa rilis kode |
| Frustrasi | Perubahan config tidak teraudit/tidak versioned di sistem lama |
| Interaksi ECMP | Workflow/SLA/role-permission config dengan approval (BR-ADM-01 baseline); override otorisasi dengan justifikasi tercatat (BR-CP-02 baseline) |
| Permission | Planned |

### P-04 Handler
| Aspek | Deskripsi |
|---|---|
| Peran | Petugas penanganan case setelah assignment (bisa dirangkap CS Agent di unit kecil) |
| Tujuan | Menyelesaikan case sesuai SLA; mencatat hasil penanganan untuk review |
| Frustrasi | Konteks case/pelanggan tidak lengkap saat menerima assignment; bolak-balik review |
| Interaksi ECMP | Mulai penanganan & ajukan review (FR-004), lihat case & customer 360 (FR-002, FR-010) |
| Permission | Planned — menunggu revisi Role Access Matrix (Sprint-02) |

### P-05 Manager / Executive
| Aspek | Deskripsi |
|---|---|
| Peran | Manajemen yang memantau kinerja layanan lintas unit |
| Tujuan | Melihat tren antrian, SLA achievement, dan KPI tanpa menyentuh data transaksi |
| Frustrasi | Laporan manual, angka tidak reconcile dengan operasional |
| Interaksi ECMP | Dashboard read-only lintas unit (FR-040, BR-DASH-01/03), laporan KPI (FR-030) |
| Permission | Planned (Sprint-03) |

## 2. Journey J-01 — Sprint-01 (API-first, current)
Selaras FRD-001 (Approved) dan UC-DOC-001.

| Step | Aktor | Aksi | Sistem |
|---|---|---|---|
| 1 | CS Agent | Submit case baru (`POST /v1/cases`) | Validasi payload + AuthN/AuthZ (`cases:create`) |
| 2 | Sistem | — | Verifikasi customerId (stub: `customerVerified=false`); buat case `CASE-<10-hex>`, status `REGISTERED` |
| 3 | Sistem | — | Persist case + **write-audit** + outbox dalam 1 transaksi (FR-001c); emit **EVT-001 CaseCreated** |
| 4 | CS Agent | Cek detail case (`GET /v1/cases/{caseId}`) | Return 200 dengan field lengkap (`cases:read`) |

Jalur gagal utama: 400 validasi / 401 token / 403 permission — semuanya Error envelope `{code, message, details?}`.

## 3. Journey J-02 — Target G1 (assign → process → close)
Selaras state machine baseline (`20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md`) dan FRD-002 (Draft). **Belum boleh dibangun sebelum G0 exit (DEC-002).**

| Step | Aktor | Aksi | Status Case | Event |
|---|---|---|---|---|
| 1 | CS Agent | Registrasi case | `REGISTERED` | EVT-001 |
| 2 | Supervisor | Assign ke handler/unit (FR-003) | `ASSIGNED` | EVT-002 + EVT-003 |
| 3 | Handler | Mulai penanganan (FR-004) | `IN_PROGRESS` | EVT-003 |
| 4 | Handler | Ajukan hasil untuk review | `PENDING_REVIEW` | EVT-003 |
| 5 | Supervisor | Approve closure (resolusi + evidence bila COMPLAINT, BR-ECMF-06 baseline) | `CLOSED` | EVT-005 + EVT-003 |
| 6 | (opsional) Role berwenang | Reopen ≤ 30 hari (BR-ECMF-07 baseline) | `REOPENED` | EVT-007 + EVT-003 |

> EVT-003 StatusChanged menyertai **setiap** transisi status valid (DOM-ECMF-003), termasuk yang memicu event spesifik.

Sepanjang journey: Notification mengabari assignee/supervisor (FR-020), KPI menghitung SLA 24x7 baseline (FR-030), Dashboard menampilkan antrian (FR-040).

## Related
- `../03 Functional Requirements/` (FRD-001 Approved; FRD-002..006 Draft)
- `../10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md`
- `../27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`, `DEC-004_BR_Baseline_Defaults_v1.0.md`
