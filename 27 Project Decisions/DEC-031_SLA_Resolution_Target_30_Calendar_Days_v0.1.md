# DEC-031 — Target penyelesaian pengaduan 30 hari kalender

| Field | Value |
|---|---|
| ID | DEC-031 |
| Version | 0.1 |
| Owner | Business Owner |
| Reviewer | Operations Lead · BA Lead · Domain PO ECMF · Architecture Review Board |
| Approver | Business Owner (§7a) · ARB untuk Fase 2 (§7b) |
| Status | 🟢 **Accepted — Fase 1** (§7a) · **Fase 2 pola Accepted with Conditions** (§7b) · **Implementation Gate PASS** (IG-20260823-01) — eng authorized with scope; mesin belum dibangun |
| Date | 2026-08-23 |
| Type | Project Decision (Complaint Management Module — SLA) |
| Supersedes | DEC-005 §(a) kolom *Resolution Target* · SLA-MTX-001 §1 kolom *Resolution Target* |
| Related | DEC-004 (kalender 24×7) · BR-ECMF-05 · BR-006 Working Day SLA · FRD-005 🔒 LOCKED · CAP006-BLK-001 (B2-24) |

---

## 1. Intent

Target penyelesaian yang berlaku hari ini berasal dari DEC-005 (baseline ARB 2026-07-21): 4 jam untuk CRITICAL, 8 jam HIGH, 2 hari MEDIUM, 5 hari LOW. Angka-angka itu **tidak pernah aktif di runtime** — Mode A mengikat versi SLA Policy tanpa hitung mundur, `sla_countdown_active` permanen `false`, dan penyedia SLA di dasbor selalu mengembalikan nol. Akibatnya modul berjalan tanpa ukuran waktu sama sekali: tidak ada cara melihat pengaduan mana yang menua, dan tidak ada angka yang bisa dijanjikan ke nasabah.

Business Owner menetapkan **satu target tunggal yang sederhana, seragam, dan bisa dijelaskan**: pengaduan wajib selesai dalam **30 hari kalender**. Target tunggal dipilih di atas matriks empat prioritas karena diferensiasi prioritas belum pernah divalidasi data operasional (DEC-005 sendiri menandainya sebagai kandidat revisi), dan karena satu angka jauh lebih mudah ditegakkan dan diaudit daripada empat angka yang tak satu pun berjalan.

DEC ini menutup **nilai targetnya**. DEC ini **tidak** membuka pembekuan mesin deteksi breach (CAP006-BLK-001) — lihat §4.

## 2. Decision

1. **Target penyelesaian pengaduan = 30 hari kalender**, seragam untuk seluruh prioritas (CRITICAL/HIGH/MEDIUM/LOW), seluruh kategori, dan seluruh unit. Menggantikan kolom *Resolution Target* pada DEC-005 §(a) dan SLA-MTX-001 §1.

2. **Kalender 24×7 — hari kalender, bukan hari kerja.** Sabtu, Minggu, dan hari libur resmi **ikut dihitung**. Menegaskan baseline BR-ECMF-05 / DEC-004. BR-006 (Working Day SLA) tetap **Deferred** dan tidak diaktifkan oleh DEC ini; bila kelak kalender kerja diaktifkan, itu DEC tersendiri yang harus menyatakan ulang angka 30 dalam satuan hari kerja.

3. **SLA diukur pada Pengaduan (Complaint), bukan pada Case.** Ini **deviasi tercatat** dari BR-006 yang menyatakan *"SLA melekat pada Case, bukan Complaint"*. Alasan: yang dijanjikan kepada nasabah adalah selesainya **pengaduan** yang ia sampaikan, bukan selesainya unit kerja internal; dan di Mode A satu pengaduan lazimnya ditangani satu Case, sehingga pengukuran per-Case tidak menambah informasi tetapi menambah kerumitan. BR-006 tetap berlaku sebagai katalog target untuk fase saat Case majemuk benar-benar dipakai.

4. **Titik mulai jam** = `cm_batch1_complaints.created_at` (saat pengaduan terdaftar). **Titik henti** = saat pengaduan berstatus `CLOSED`. Eskalasi ke Pusat, penggantian unit penangan, maupun penjadwalan kedatangan **tidak me-reset dan tidak menghentikan** jam — konsisten dengan BR-006 §A4 (*"petugas pusat melanjutkan, bukan mengulang"*).

5. **Tidak ada pause.** Baseline ini tidak mengenal status yang menghentikan sementara jam (mis. menunggu dokumen nasabah). Pause = kandidat revisi BO via DEC saat ada data yang membenarkannya.

6. **Empat status SLA turunan**, dihitung dari `created_at`, target 30 hari, dan waktu penutupan:

   | Status | Kondisi | Label UI (id-ID) |
   |---|---|---|
   | `ON_TRACK` | belum tutup, umur ≤ 30 hari | Berjalan |
   | `OVERDUE` | belum tutup, umur > 30 hari | Lewat batas |
   | `MET` | sudah tutup, durasi ≤ 30 hari | Tepat waktu |
   | `MISSED` | sudah tutup, durasi > 30 hari | Terlambat |

7. **Ambang peringatan 80% = hari ke-24** (dibulatkan ke bawah dari 24,0 hari). Dipertahankan dari DEC-005 §(b) sebagai ambang **tampilan** saja pada Fase 1 — tidak memicu notifikasi sampai Fase 2.

8. **Nilai 30 wajib konfigurasi, bukan hardcode.** Kunci `COMPLAINT_RESOLUTION_TARGET_DAYS`, default `30`, dibaca lewat `Settings`. Mengubah target bisnis tidak boleh menuntut deploy kode. Nilai yang dipakai suatu pengaduan dievaluasi saat pembacaan, sehingga perubahan konfigurasi berlaku serentak — versioning per-pengaduan (BR-006 §A1) baru relevan pada Fase 2.

9. **Server yang menghitung, bukan klien.** Status dan sisa hari disajikan API sebagai field turunan; frontend tidak pernah menghitung ulang dari jam browser. Sejalan dengan pola yang sudah dipakai DEC-030 (`editable`/`editableUntil`).

## 3. Fase pelaksanaan

DEC ini dibagi dua fase karena keduanya tunduk pada gerbang governance yang berbeda.

### Fase 1 — Pengukuran & tampilan (tidak memerlukan mesin)

Seluruh isi §2 dapat dipenuhi **tanpa scheduler, tanpa job, tanpa event baru**, karena status SLA adalah fungsi murni dari `created_at`, waktu penutupan, dan jam saat ini — dihitung ketika data dibaca. Yang dihasilkan: umur pengaduan, status empat-nilai, penanda lewat batas di daftar dan Case, serta angka kepatuhan di dasbor yang selama ini nol.

Fase 1 **tidak melanggar** CAP006-BLK-001, karena blocker itu membekukan *mekanisme deteksi lewatnya `dueAt`* (scheduler/job/poller) dan emisi EVT-004 — bukan penyajian ukuran waktu yang dihitung saat pembacaan. Fase 1 juga tidak menyentuh `sla_countdown_active`, yang tetap `false`.

### Fase 2 — Notifikasi proaktif & EVT-004 (TERBLOKIR)

Yang **tidak** bisa dilakukan tanpa mesin hanyalah: memberi tahu petugas **pada saat** batas terlampaui tanpa ada orang membuka halaman, dan menerbitkan `EVT-004 SLABreached`. Keduanya masuk CAP-006 / FR-030 dan tetap **Stay Deferred** di bawah **CAP006-BLK-001** (B2-24, 2026-08-04) sampai ARB menerima pola pemenuhan Time Source.

**DEC ini tidak membuka blocker tersebut.** Menyetujui DEC-031 berarti menyetujui angka 30 hari dan Fase 1 — bukan mengotorisasi pembangunan mesin.

## 4. Conditions

- **Tidak ada waktu penutupan yang tersimpan.** `cm_batch1_complaints` tidak punya kolom `closed_at`; `updated_at` berubah oleh sunting apa pun sehingga tidak sah dipakai mengukur durasi. Waktu penutupan saat ini hanya bisa diturunkan dari `timeline_entries` (peristiwa `CaseClosed` / `HqCompleted` / `IntakeDispositionRecorded` dengan disposisi `BRANCH_CLOSED`/`HQ_CLOSED`). Verifikasi 2026-08-23 pada basis data lab: **21 dari 21** pengaduan `CLOSED` memiliki peristiwa penutupan tersebut, sehingga penurunan ini layak. Namun menyimpan `closed_at` di Aggregate adalah jalur yang benar untuk `MET`/`MISSED` yang stabil dan murah; ini prasyarat teknis Fase 1, bukan perluasan lingkup.
- **Rujukan menggantung.** Kode mematikan SLA dengan alasan **"BQ-005"** ([`cm_case/domain/aggregate.py:94`](../backend/app/modules/cm_case/domain/aggregate.py), [`dashboard/providers/sla_provider.py:11`](../backend/app/modules/dashboard/providers/sla_provider.py)), tetapi kode keputusan itu **tidak memiliki dokumen di repo** — hanya muncul di dua baris komentar. Perlu ditelusuri atau diterbitkan sebagai keputusan yang sah; DEC ini tidak mengarang isinya.
- **Tidak ada breach retroaktif saat adopsi.** Verifikasi 2026-08-23: umur pengaduan pada basis data lab berkisar 1,0–6,0 hari; **nol** baris melewati 30 hari. Mengaktifkan target ini tidak menghasilkan tumpukan pelanggaran mendadak.
- **Tabel SLA Foundation tidak relevan.** `sla_records` / `complaints` tidak ada di basis data (pensiun per DEC-026). `complaint_sla_policies` berisi satu baris *"Default 24h Resolution"* (1440 menit) milik CAPABILITY-008, tetapi `complaint_cases` kosong dan modul itu tidak melayani lalu lintas. Tidak satu pun dari ketiganya menjadi jalur pelaksanaan DEC ini.
- North Star: perubahan ini murni domain komplain, tidak menyentuh mekanisme integrasi Enterprise.

## 5. Acceptance

1. Target penyelesaian yang berlaku di seluruh modul = 30 hari kalender, terbaca dari konfigurasi, seragam lintas prioritas.
2. Setiap pengaduan menampilkan umur dan salah satu dari empat status (§2.6) yang dihitung server.
3. Pengaduan belum tutup berumur > 30 hari ditandai **Lewat batas** di daftar pengaduan, halaman Case, dan dasbor.
4. Dasbor menyajikan kepatuhan SLA sebagai angka nyata, bukan nol tetap.
5. Sabtu/Minggu/libur terhitung — pengaduan terdaftar 1 Januari jatuh tempo 31 Januari, tanpa penyesuaian kalender kerja.
6. Eskalasi ke Pusat tidak me-reset umur pengaduan.
7. Mengubah `COMPLAINT_RESOLUTION_TARGET_DAYS` mengubah perilaku tanpa deploy kode.
8. `sla_countdown_active` tetap `false`; tidak ada scheduler, job, atau `EVT-004` yang ditambahkan oleh Fase 1.
9. SLA-MTX-001 dan DEC-005 disinkronkan dengan penanda bahwa kolom *Resolution Target* disupersede oleh DEC-031.

## 6. Dampak artefak

| Artefak | Aksi |
|---|---|
| `11 SLA and KPI Matrix/ECMP_SLA_Matrix_v0.1.md` | Kolom *Resolution Target* disupersede; naik versi + catatan rujuk DEC-031 |
| `27 Project Decisions/DEC-005_...md` | Catatan supersede pada §(a); nilai NFR §(c) **tidak** tersentuh |
| `02 Business Rules/...Complaint_Management_Module_v1.0.md` | BR-006: catatan deviasi level pengukuran (Complaint, bukan Case) |
| `03 Functional Requirements/ECMP_FRD_KPI_SLA_v0.1.md` (🔒 LOCKED) | **Tidak diubah** — FRD-005 mengatur mesin CAP-006 (Fase 2), bukan target numerik |
| Kode backend / frontend / OpenAPI | Fase 1 **sudah dilaksanakan** sebelum tanda tangan formal — lihat §7 catatan; berjalan di baliknya konfigurasi `COMPLAINT_RESOLUTION_TARGET_DAYS` (§8 rollback) |

## 7. Kewenangan & tanda tangan

DEC-005 §*Kewenangan Revisi* menyatakan Business Owner berwenang merevisi nilai baseline melalui DEC baru — bukan lewat sunting langsung matriks. DEC-031 memakai jalur itu.

**(a) Business Owner** — menyetujui angka 30 hari kalender, level pengukuran Complaint, dan pelaksanaan Fase 1.

> Nama: **rbxhut**  Tanggal: **2026-08-23**  Tanda tangan: **rbxhut** (disetujui via sesi kerja tercatat; git identity `rbxhut` / `hutbeon@gmail.com`)

**(b) Architecture Review Board** — *hanya diperlukan bila kelak Fase 2 dijalankan.* Tanda tangan (a) **tidak** membuka CAP006-BLK-001; pembukaan blocker menuntut ARB menerima pola pemenuhan Time Source dari bukti repo yang tidak dikarang, atau otorisasi-invent eksplisit di luar konstitusi default.

> Nama: **rbxhut**  Tanggal: **2026-08-23**  Tanda tangan: **rbxhut**
>
> Outcome: **Accepted with Conditions** (AR-20260823-01 / B2-25). Pola Time Source = Scheduled Command Invocation. **CAP006-BLK-001 diangkat.**
>
> **Batas jangkauan (C-2).** Accept memberi **pemicu**, bukan kanal. CAP-005 tetap stub. Lingkup Fase 2 yang boleh dirancang: deteksi + catatan durabel + peringatan **dalam-aplikasi** saja.
>
> **C-3 (2026-08-23):** jeda deteksi **1 jam** → cadence awal jam-jaman.
>
> **C-4 (2026-08-23):** `EVT-004` **wajib dikuras** lewat perintah terjadwal pola yang sama (bukan write-only).
>
> **C-6 (2026-08-23):** peringatan dalam-aplikasi sekali per ambang pada sisa **7 / 3 / 1** hari kalender sebelum `due_at`, plus breach saat `due_at`. Bukan surel/SMS/push. Ambang tampilan Fase 1 80% (badge baca-saat-diminta) **belum** diganti oleh DEC ini.
>
> **C-1 masih terbuka** — pemilik + mekanisme heartbeat wajib sebelum kode FR-030. Kode mesin **tidak** diotorisasi oleh tanda tangan ini.

**Status §7b per 2026-08-23: DITANDATANGANI (Accepted with Conditions). C-3/C-4/C-6 tertutup. Mesin FR-030 menunggu Implementation Gate 1–4 (termasuk C-1).**

Artefak yang memenuhi syarat B2-24 adalah
[`ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md`](../05%20Architecture%20Decision%20Records/ADR-CAP006-002_Time_Source_Fulfillment_Pattern.md)
(v0.3.1, status 🟢 **Accepted with Conditions**, AR-20260823-01 / B2-25). Pola **Scheduled Command Invocation**. **CAP006-BLK-001 diangkat.** C-3 = 1 jam; C-4 = outbox dikuras; C-6 = H-7/H-3/H-1 dalam aplikasi. FR-030 tetap **tidak terotorisasi** sampai Implementation Gate 1–4 (C-1 heartbeat owner/mechanism masih terbuka).

**Batas jangkauan (C-2) — tetap berlaku setelah §7b:**

1. **Kanal pengiriman belum ada.** CAP-005 masih stub. H-7/H-3/H-1 = permukaan **dalam-aplikasi** saja.
2. **C-4 mengikat penguras outbox** sebagai jalur publikasi `EVT-004`, tetapi penguras itu **belum dibangun** — 262 baris `UNPUBLISHED` tetap utang operasi sampai Gate 4 + coding.

Konsekuensi lingkup Fase 2 yang boleh dikerjakan setelah gerbang: **deteksi terjadwal + catatan durabel + peringatan dalam-aplikasi (H-7/H-3/H-1 + breach) + penguras outbox**, bukan surel/SMS/push.

## 8. Rollback

Fase 1 reversibel penuh: setel `COMPLAINT_RESOLUTION_TARGET_DAYS` kosong untuk menyembunyikan status SLA, atau revert commit dokumentasi + kode. Tidak ada data yang hilang karena status SLA tidak dipersistensi — selalu dihitung ulang saat pembacaan.

## 9. Risiko

**RENDAH** untuk Fase 1 — perhitungan baca-saat-diminta, tanpa proses latar, tanpa migrasi destruktif, tanpa breach retroaktif.
**Coding mesin DIOTORISASI BERSYARAT** — Implementation Gate PASS (B2-26); lingkup = H-7/H-3/H-1 dalam aplikasi + breach + penguras outbox + heartbeat; tanpa CAP-005. Kode belum ada sampai sprint implementasi.

## 10. Catatan Persetujuan

Fase 1 (§3) diimplementasikan pada sesi kerja 2026-08-23 — migrasi `closed_at`, kolom SLA di API pengaduan, rollup SLA dasbor, dan panel peringatan dalam-aplikasi — **sebelum** dokumen ini ditandatangani formal di §7a, atas instruksi eksplisit pemilik repo untuk membangun fitur tersebut. Tanda tangan §7a pada 2026-08-23 mengesahkan pekerjaan yang sudah berjalan itu secara retroaktif sebagai keputusan bisnis yang sah, bukan mengesahkan pekerjaan yang baru akan dimulai. Urutan ini dicatat di sini demi transparansi audit trail — bukan pola yang direkomendasikan untuk DEC berikutnya.

---

*Akhir DEC-031 v0.1 — Accepted (Fase 1) + §7b Accepted with Conditions (pola saja), 2026-08-23.*
