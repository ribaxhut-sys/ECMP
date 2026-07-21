# ECMP Business Rules (Katalog Enterprise)

> Nama file `..._v1.0.md` menandai **baseline mayor v1.0** dan sengaja dipertahankan agar tautan lintas-dokumen stabil; **versi konten otoritatif = field `Version` di header** (saat ini 1.2, per DEC-004).

| Field | Value |
|---|---|
| ID | BR-CAT-001 |
| Version | 1.2 |
| Owner | BA Lead |
| Reviewer | Domain Product Owners, Operations, Compliance |
| Approver | Business Owner |
| Status | 🟢 Approved (baseline — nilai default [TBD] ditutup per DEC-004, 2026-07-21) |
| Last Review | 2026-07-21 |
| Next Review | 2027-01-21 |

## Purpose
Memformalkan aturan bisnis yang sebelumnya tersirat di `01 Business Blueprint` menjadi rule eksplisit yang dapat dirujuk oleh FRD (`03`), Solution Architecture (`04`), dan Test Strategy (`13`). Setiap rule mengikuti template di `../24 Templates` dan wajib punya status konfigurasi (Configuration vs Hardcoded) agar sejalan dengan prinsip *configuration-first*.

## Cara Membaca
Rule ID mengikuti pola `BR-<Domain>-<NN>`. **Per DEC-003 (2026-07-21): skema ini adalah katalog referensi kebijakan — SoT untuk implementasi/tes/traceability adalah skema delivery `BR-0xx`** di `ECMP_Business_Rules_Sprint01_v0.1.md`. Kode, PR, dan tes hanya boleh mengutip `BR-0xx`.

## Pemetaan ke ID Delivery (DEC-003)
| Delivery (SoT implementasi) | Enterprise (katalog ini) |
|---|---|
| BR-001 | BR-ECMF-03 |
| BR-002 | BR-ECMF-02 |
| BR-003 | BR-CRM-01 / BR-CRM-04 |
| BR-004 | BR-NOTIF-01 |
| BR-005 | BR-ECMF-05 |
| BR-006 | BR-DASH-01 / BR-DASH-04 |
| BR-007 | BR-CP-01 / BR-CP-02 |
| BR-008 | BR-CP-03 / BR-ECMF-01 |

---

## 1. Core Platform

| Rule ID | Trigger Condition | Rule Statement | Exception | Owner | Priority | Config/Hardcoded |
|---|---|---|---|---|---|---|
| BR-CP-01 | Setiap request ke modul apapun | Akses wajib melalui autentikasi yang valid sebelum request diproses | Tidak ada (mandatory) | Security Officer | Critical | Hardcoded |
| BR-CP-02 | User sudah terautentikasi mengakses fungsi/data | Otorisasi mengikuti kombinasi role dan organisasi unit user | Override hanya oleh Administrator dengan justifikasi tercatat + audit trail (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Security Officer | Critical | Configuration |
| BR-CP-03 | Setiap aktivitas signifikan (create/update/delete/approve) | Audit trail dicatat dan tidak dapat dihapus atau diedit oleh siapapun termasuk Administrator | Tidak ada | Security Officer | Critical | Hardcoded |
| BR-CP-04 | Perubahan konfigurasi sistem (role, parameter, workflow) | Setiap perubahan konfigurasi wajib tercatat di audit trail dengan identitas pelaku dan waktu | Tidak ada | Administrator | High | Hardcoded |

## 2. CRM

| Rule ID | Trigger Condition | Rule Statement | Exception | Owner | Priority | Config/Hardcoded |
|---|---|---|---|---|---|---|
| BR-CRM-01 | Semua operasi terhadap data pelanggan | ECMP tidak boleh menjadi/berfungsi sebagai system of record master pelanggan; data master tetap bersumber dari sistem eksternal | Cache read-only untuk performa diperbolehkan, tidak untuk write-back | Domain PO CRM | Critical | Hardcoded |
| BR-CRM-02 | User membuka profil/riwayat pelanggan | Akses data pelanggan mengikuti role dan prinsip need-to-know | Field yang dibatasi: kontak pelanggan (phone/email) dimask untuk role non-CS (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Domain PO CRM | High | Configuration |
| BR-CRM-03 | Interaksi dengan pelanggan dianggap "penting" (mis. terkait case) | Interaksi wajib dicatat dan ditautkan ke Customer ID | Ambang "penting" = interaksi yang tertaut ke case; interaksi ringan tanpa case tidak wajib dicatat (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Domain PO CRM | Medium | Configuration |
| BR-CRM-04 | Ada kebutuhan perubahan data master pelanggan | Perubahan hanya boleh melalui integrasi resmi ke sistem master, bila dan hanya bila diizinkan oleh sistem tsb | Tidak ada | Domain PO CRM | Critical | Hardcoded |

## 3. ECMF (Complaint/Inquiry Management)

| Rule ID | Trigger Condition | Rule Statement | Exception | Owner | Priority | Config/Hardcoded |
|---|---|---|---|---|---|---|
| BR-ECMF-01 | Setiap transaksi case (create/assign/status change/close/reopen) | Wajib memiliki audit trail lengkap | Tidak ada | Domain PO ECMF | Critical | Hardcoded |
| BR-ECMF-02 | User melakukan aksi terhadap case | Hak akses mengikuti peran organisasi (mis. hanya assignee/supervisor unit terkait) | Akses lintas unit: aksi tulis hanya oleh supervisor unit induk; unit lain read-only (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Domain PO ECMF | High | Configuration |
| BR-ECMF-03 | Perubahan status case | Status hanya dapat berubah sesuai transisi yang didefinisikan pada workflow configuration | Override oleh Administrator dengan justifikasi tercatat | Domain PO ECMF | Critical | Configuration |
| BR-ECMF-04 | Perubahan penting pada case (status, assignment, prioritas) | Dicatat pada activity log yang dapat dilihat semua pihak berwenang | Tidak ada | Domain PO ECMF | High | Hardcoded |
| BR-ECMF-05 | Case memasuki suatu status/tahapan yang memiliki SLA | SLA dihitung otomatis berdasarkan konfigurasi kategori dan prioritas case | Kalender: 24x7 dulu; kalender kerja/jam operasional = konfigurasi SLA fase berikut, lihat `11 SLA and KPI Matrix` (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Operations Lead | Critical | Configuration |
| BR-ECMF-06 | User menutup case | Case tertutup wajib memiliki resolusi, dan evidence sesuai tipe kasus (bila dipersyaratkan kategori) | Evidence wajib untuk `COMPLAINT`, opsional untuk `INQUIRY` (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Domain PO ECMF | High | Configuration |
| BR-ECMF-07 | User meminta reopen case closed | Reopen hanya dapat dilakukan oleh role yang diizinkan, dalam jangka waktu 30 hari kalender sejak closure (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Tidak ada | Domain PO ECMF | High | Configuration |

## 4. KPI & Performance

| Rule ID | Trigger Condition | Rule Statement | Exception | Owner | Priority | Config/Hardcoded |
|---|---|---|---|---|---|---|
| BR-KPI-01 | Definisi metrik baru dibuat | Setiap KPI wajib memiliki formula, owner, dan periode pengukuran sebelum dipublikasikan | Tidak ada | Performance Analyst | High | Configuration |
| BR-KPI-02 | Perubahan target atau definisi metrik | Hanya boleh dilakukan melalui proses governance konfigurasi, bukan perubahan langsung | Tidak ada | Performance Analyst | High | Hardcoded (proses), Configuration (nilai) |
| BR-KPI-03 | Perhitungan KPI dijalankan | Data KPI wajib bersumber dari event operasional; input manual hanya untuk kasus terdokumentasi/dikecualikan | Tidak ada KPI berinput manual di fase awal — daftar kosong (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Performance Analyst | Medium | Hardcoded |
| BR-KPI-04 | Hasil KPI ditampilkan/dilaporkan | Setiap angka KPI harus dapat ditelusuri (traceable) ke transaksi sumber | Tidak ada | Performance Analyst | High | Hardcoded |

## 5. Dashboard & Analytics

| Rule ID | Trigger Condition | Rule Statement | Exception | Owner | Priority | Config/Hardcoded |
|---|---|---|---|---|---|---|
| BR-DASH-01 | User membuka dashboard | Tampilan (widget, data) mengikuti role dan organisasi pengguna yang login | Tidak ada | Domain PO Dashboard | High | Configuration |
| BR-DASH-02 | Data agregat ditampilkan | Angka dashboard harus reconcile dengan data sumber operasional (tidak boleh menyimpang tanpa penjelasan) | Perbedaan akibat lag data harus ditandai dengan timestamp "as of" | Domain PO Dashboard | High | Hardcoded |
| BR-DASH-03 | User berinteraksi dengan dashboard | Dashboard bersifat read-only dan tidak boleh mengubah data transaksi | Tidak ada | Domain PO Dashboard | Critical | Hardcoded |
| BR-DASH-04 | Dashboard menampilkan data sensitif pelanggan/case | Akses tetap mengikuti otorisasi Core Platform (BR-CP-02) | Tidak ada | Security Officer | Critical | Hardcoded |

## 6. Notification

| Rule ID | Trigger Condition | Rule Statement | Exception | Owner | Priority | Config/Hardcoded |
|---|---|---|---|---|---|---|
| BR-NOTIF-01 | Domain event terjadi | Notifikasi hanya dikirim untuk event yang secara eksplisit dikonfigurasi (opt-in, bukan default kirim semua) | Tidak ada | Integration Lead | Medium | Configuration |
| BR-NOTIF-02 | Notifikasi akan dikirim | Penerima ditentukan oleh kombinasi role, assignment, atau organisasi — bukan daftar statis | Tidak ada | Integration Lead | Medium | Configuration |
| BR-NOTIF-03 | Notifikasi dikirim (berhasil/gagal) | Riwayat pengiriman wajib disimpan untuk audit dan troubleshooting | Tidak ada | Integration Lead | High | Hardcoded |
| BR-NOTIF-04 | Pengiriman notifikasi gagal | Kegagalan dicatat dan dapat di-retry sesuai kebijakan retry: maksimal 3x dengan interval 5 menit (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Setelah max retry, eskalasi via email ke supervisor terkait (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Integration Lead | High | Configuration |

## 7. Administration

| Rule ID | Trigger Condition | Rule Statement | Exception | Owner | Priority | Config/Hardcoded |
|---|---|---|---|---|---|---|
| BR-ADM-01 | Permintaan perubahan konfigurasi yang diklasifikasikan kritikal | Wajib melalui approval sebelum diterapkan | Konfigurasi kritikal: workflow config, SLA config, role-permission (baseline ARB 2026-07-21 — dapat direvisi BO via DEC) | Administrator | Critical | Configuration |
| BR-ADM-02 | Setiap perubahan konfigurasi (kritikal maupun tidak) | Tercatat lengkap dalam audit trail (siapa, apa, kapan, nilai lama/baru) | Tidak ada | Administrator | Critical | Hardcoded |
| BR-ADM-03 | Konfigurasi baru diaktifkan | Wajib versioned atau memiliki effective date agar histori dapat direkonstruksi | Tidak ada | Administrator | High | Hardcoded |
| BR-ADM-04 | Konfigurasi diubah/dinonaktifkan | Tidak boleh menghapus jejak transaksi historis yang sudah menggunakan konfigurasi lama | Tidak ada | Administrator | Critical | Hardcoded |

## Open Items untuk FRD & Solution Architecture
- ~~Semua kolom bertanda `[TBD]`~~ **Selesai** — seluruh [TBD] ditutup dengan nilai baseline ARB 2026-07-21 (dicatat di `27 Project Decisions/DEC-004_BR_Baseline_Defaults_v1.0.md`; Business Owner berwenang merevisi via DEC baru).
- BR-ECMF-05 (kalender 24x7 baseline) dan BR-NOTIF-04 (retry 3x/5 menit) berdampak ke `11 SLA and KPI Matrix` — sinkronkan saat matriks SLA dirinci.
- ~~Role-Permission Matrix belum ada~~ **Selesai** — kini tersedia di `10 Security and Access Standards/ECMP_Role_Access_Matrix_v0.1.md` (SEC-RAM-001, scope Sprint-01 slice); BR-CP-02, BR-CRM-02, BR-ECMF-02 merujuk ke sana untuk permission teknis.

## Related
- `../01 Business Blueprint`
- `../03 Functional Requirements`
- `../11 SLA and KPI Matrix`
- `../10 Security and Access Standards`
