# ECMP Personas & Journeys v0.2

| Field | Value |
|---|---|
| ID | UX-001 |
| Version | 0.2 |
| Owner | UX Lead |
| Reviewer | BA Lead / Domain POs |
| Approver | Business Owner |
| Status | 🟡 Draft |
| Last Review | 2026-08-05 |
| Next Review | 2027-02-05 |
| Revision note | UX-001 Documentation Update: persona **P-01 CS Agent** dan **P-04 Handler** digabung menjadi **P-01 Complaint Officer**, mengikuti keputusan UX Review bahwa memisahkan Front Office/Customer Service dari Complaint Officer menciptakan kompleksitas UX yang tidak perlu. Perbedaan otoritas (mis. siapa yang boleh assign/close case) ditangani Role & Permission, bukan persona terpisah. Untuk model persona/JTBD/responsibility yang lebih rinci di level Complaint Workspace, lih. `docs/ux/PDS-001-Persona-Design-Specification.md` (rujukan yang menggantikan bagian "siapa & tujuan" dokumen ini). |

> **Catatan UI: deferred.** Frontend produk adalah non-goal Sprint-0/G0 (DEC-002) dan belum di-ADR-kan. Dokumen ini mendefinisikan persona dan *service journey* (level layanan/API), bukan screen spec. Screen inventory menyusul setelah keputusan frontend.

## 1. Personas

Lima persona sebelumnya (CS Agent, Supervisor, Administrator, Handler, Manager/Executive) menjadi **empat** setelah merge P-01 + P-04.

### P-01 Complaint Officer *(gabungan CS Agent + Handler)*
| Aspek | Deskripsi |
|---|---|
| Peran | Petugas garis depan yang meregistrasi complaint/inquiry **dan** menangani case setelah assignment — satu persona, dua mode kerja situasional (intake / penanganan aktif) |
| Tujuan | Meregistrasi complaint/inquiry cepat & akurat sejak kontak pertama; melihat konteks pelanggan saat menangani; menyelesaikan case sesuai SLA; mencatat hasil penanganan untuk review |
| Frustrasi | Input berulang, konteks pelanggan terpencar, tidak tahu status lanjutan case; konteks case/pelanggan tidak lengkap saat menerima assignment; bolak-balik review |
| Interaksi ECMP | Create case, get case, customer 360 (unmasked kontak per BR-CRM-02 baseline); mulai penanganan & ajukan review (FR-004) |
| Permission (slice) | `cases:create`, `cases:read` (SEC-RAM-001) — menunggu revisi Role Access Matrix (Sprint-02) untuk slice penanganan (mulai/ajukan review) |

*Catatan penggabungan: sebelum revisi ini, P-04 Handler mencatat "bisa dirangkap CS Agent di unit kecil" — merge ini mengangkat pengakuan tersebut menjadi satu persona formal, bukan lagi rangkap dua persona berbeda.*

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

### P-04 Manager / Executive
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
| 1 | Complaint Officer | Submit case baru (`POST /v1/cases`) | Validasi payload + AuthN/AuthZ (`cases:create`) |
| 2 | Sistem | — | Verifikasi customerId (stub: `customerVerified=false`); buat case `CASE-<10-hex>`, status `REGISTERED` |
| 3 | Sistem | — | Persist case + **write-audit** + outbox dalam 1 transaksi (FR-001c); emit **EVT-001 CaseCreated** |
| 4 | Complaint Officer | Cek detail case (`GET /v1/cases/{caseId}`) | Return 200 dengan field lengkap (`cases:read`) |

Jalur gagal utama: 400 validasi / 401 token / 403 permission — semuanya Error envelope `{code, message, details?}`.

## 3. Journey J-02 — Target G1 (assign → process → close)
Selaras state machine baseline (`20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md`) dan FRD-002 (Draft). **Belum boleh dibangun sebelum G0 exit (DEC-002).**

| Step | Aktor | Aksi | Status Case | Event |
|---|---|---|---|---|
| 1 | Complaint Officer | Registrasi case | `REGISTERED` | EVT-001 |
| 2 | Supervisor | Assign ke Complaint Officer/unit (FR-003) | `ASSIGNED` | EVT-002 + EVT-003 |
| 3 | Complaint Officer | Mulai penanganan (FR-004) | `IN_PROGRESS` | EVT-003 |
| 4 | Complaint Officer | Ajukan hasil untuk review | `PENDING_REVIEW` | EVT-003 |
| 5 | Supervisor | Approve closure (resolusi + evidence bila COMPLAINT, BR-ECMF-06 baseline) | `CLOSED` | EVT-005 + EVT-003 |
| 6 | (opsional) Role berwenang | Reopen ≤ 30 hari (BR-ECMF-07 baseline) | `REOPENED` | EVT-007 + EVT-003 |

> EVT-003 StatusChanged menyertai **setiap** transisi status valid (DOM-ECMF-003), termasuk yang memicu event spesifik.

Sepanjang journey: Notification mengabari assignee/supervisor (FR-020), KPI menghitung SLA 24x7 baseline (FR-030), Dashboard menampilkan antrian (FR-040).

## Related
- `../03 Functional Requirements/` (FRD-001 Approved; FRD-002..006 Draft)
- `../10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md`
- `../27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`, `DEC-004_BR_Baseline_Defaults_v1.0.md`
- `../docs/ux/PDS-001-Persona-Design-Specification.md` — model persona/JTBD/responsibility rinci di level Complaint Workspace, menggantikan bagian "siapa & tujuan" dokumen ini
