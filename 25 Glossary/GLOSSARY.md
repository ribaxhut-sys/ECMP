# ECMP Official Glossary (Language Freeze)

| Field | Value |
|---|---|
| ID | GLS-001 |
| Version | 1.0 (L10-04 Freeze) |
| Owner | Language Review Board / Business Analyst |
| Reviewer | UX Writer / Terminology Manager / Architecture |
| Approver | Business Owner |
| Status | 🟢 Frozen |
| Last Review | 2026-08-01 |
| Next Review | 2027-02-01 |
| Sprint | L10-04 Official Terminology & Glossary Freeze |

## Purpose

Satu istilah bisnis/UI = satu padanan Bahasa Indonesia resmi, diambil **hanya** dari bukti yang sudah ada di repositori (`frontend/messages/id.json`, `backend/app/core/user_messages.py`, glosarium bisnis sebelumnya). Tidak menambah konsep bisnis baru.

## Scope

- User-facing UI, validasi, notifikasi, pesan API ke pengguna, dokumentasi yang ditampilkan ke operator.
- Di luar freeze: nama kode/permission (`complaints:read`), enum status teknis (`IN_PROGRESS`), event ID (`EVT-001`), komentar developer, log internal.

## Official Terminology Table

| English | Official Indonesian | Definition | Repository Evidence | Status |
|---|---|---|---|---|
| ECMP | ECMP | Enterprise Complaint Management Platform — modul pengaduan enterprise | `common.appName`; Blueprint / DEC-001 | FROZEN |
| Enterprise Complaint Management Platform | Platform Manajemen Pengaduan Enterprise | Nama lengkap produk untuk UI | `common.appFullName` | FROZEN |
| Complaint | Pengaduan | Ketidakpuasan/masalah pelanggan yang ditangani modul komplain | `nav.complaints`, `complaints.title`, pesan `complaint.*` | FROZEN |
| Case | Case | Unit kerja penanganan (inquiry/complaint); istilah produk dipinjam, **bukan** “Kasus” | `cases.title` = “Case”; GLOSS-001 historis | FROZEN |
| Inquiry | Inquiry | Case permintaan informasi (subtype); token domain tetap Inquiry bila muncul sebagai tipe | GLOSS-001; FRD Case Type | FROZEN |
| Queue | Antrian | Antrian kerja pengaduan | `nav.queue`, `queue.title` | FROZEN |
| Assignment | Penugasan | Penunjukan pengaduan/Case ke petugas/unit | `nav.assignments`, `assignments` | FROZEN |
| Escalation | Eskalasi | Kenaikan penanganan ke level/peran lebih tinggi | `complaints.escalationCard`, pesan `escalation.*` | FROZEN |
| Resolution | Resolusi | Hasil penanganan / penyelesaian | `nav.resolutions`, `resolutions` | FROZEN |
| Attachment | Lampiran | Bukti/berkas terlampir pada pengaduan/Case | `nav.attachments`, `attachments.title` | FROZEN |
| User | Pengguna | Akun orang yang memakai ECMP | `common.user`, `nav.users`, `users.title` | FROZEN |
| Username | Nama pengguna | Identitas login pengguna | `users.username`, `auth.usernameOrEmail` | FROZEN |
| Role | Peran | Peran otorisasi internal modul | `users.role`, `validation.roleRequired` | FROZEN |
| Permission | Izin | Hak melakukan tindakan (bukan frasa “Hak Akses”) | `errors.forbidden`, hampir semua `*Permission*` di `id.json` | FROZEN |
| Settings | Pengaturan | Administrasi & konfigurasi sistem | `nav.settings`, `settings.title` | FROZEN |
| Dashboard | Dasbor | Ringkasan operasional | `nav.dashboard` | FROZEN |
| Reports | Laporan | Halaman/laporan KPI operasional | `nav.reports` | FROZEN |
| Customer | Pelanggan | Referensi pelanggan (bukan SoR ECMP) | `validation.customerRequired`, GLOSS-001 / BR-003 | FROZEN |
| Branch | Cabang | Unit cabang organisasi | `users.branch`, `validation.branchRequired` | FROZEN |
| Head Office | Kantor Pusat | Level organisasi pusat (dalam salinan UI) | `complaints.notClosedPermissionHint` | FROZEN |
| Channel | Kanal | Media masuk pengaduan | `validation.channelRequired` | FROZEN |
| Priority | Prioritas | Tingkat urgensi | `common.priority`, `priority.*` | FROZEN |
| Status | Status | Keadaan siklus hidup (label UI boleh diterjemahkan; kode enum tetap EN) | `common.status`, `status.*` | FROZEN |
| SLA | SLA | Batas waktu layanan (singkatan dipertahankan) | `settings.slaPolicies`, `table.allSla` | FROZEN |
| KPI | KPI | Indikator kinerja (singkatan dipertahankan) | GLOSS-001 | FROZEN |
| Appointment | Janji temu | Janji pertemuan penanganan (UI) | `complaints.appointmentCard`, `stageAppointment` | FROZEN |
| Password | Kata sandi | Kredensial rahasia pengguna | `auth.password`, `users.password` | FROZEN |
| Email | Email | Alamat surel (dipertahankan) | `auth.email` | FROZEN |
| Subject | Subjek | Judul singkat pengaduan/Case | `validation.subjectRequired` | FROZEN |
| Description | Deskripsi | Uraian narasi | `validation.descriptionRequired` | FROZEN |
| Category | Kategori | Klasifikasi isi | `cases.category` | FROZEN |
| Root Cause | Akar masalah | Penyebab utama | `complaints.rootCauseRequired` | FROZEN |
| Comment | Komentar | Catatan komentar pada aksi | `cases.comment` | FROZEN |
| Timeline | Linimasa / Timeline | Jejak aktivitas (ikut label UI setempat bila ada) | konteks modul timeline | FROZEN |
| Audit Trail | Jejak audit | Rekaman aktivitas tidak terhapus | GLOSS-001 | FROZEN |
| Save | Simpan | Menyimpan data | `common.save` | FROZEN |
| Save changes | Simpan perubahan | Menyimpan perubahan form | `complaints.saveChanges` | FROZEN |
| Cancel | Batal | Membatalkan aksi UI | `common.cancel` | FROZEN |
| Delete | Hapus | Menghapus entitas (bukan clear filter) | `common.delete` | FROZEN |
| Edit | Ubah | Mengubah data | `common.edit` | FROZEN |
| Create | Buat | Membuat entitas baru | `common.create` | FROZEN |
| Update | Perbarui | Memperbarui data | `common.update` | FROZEN |
| Search | Cari | Pencarian | `common.search` | FROZEN |
| Filter | Filter | Penyaringan (dipertahankan) | `common.filter` | FROZEN |
| Reset | Atur ulang | Mengembalikan kontrol/filter/kata sandi sesuai konteks | `common.reset`, `auth.resetPassword*` | FROZEN |
| Refresh | Muat ulang | Memuat ulang data | `common.refresh` | FROZEN |
| Retry | Coba lagi | Mengulang percobaan | `common.retry` | FROZEN |
| Close | Tutup | Menutup dialog atau menutup Case/pengaduan sesuai konteks | `common.close`, `cases.close` | FROZEN |
| Confirm | Konfirmasi | Mengonfirmasi aksi | `common.confirm` | FROZEN |
| Submit | Kirim | Mengirim formulir/aksi | `common.submit` | FROZEN |
| View | Lihat | Melihat detail | `common.view` | FROZEN |
| Back | Kembali | Navigasi kembali | `common.back` | FROZEN |
| Home | Beranda | Halaman awal | `common.home` | FROZEN |
| Sign in / Login | Masuk | Autentikasi masuk | `auth.signIn`, `nav` terkait | FROZEN |
| Log out / Sign out | Keluar | Mengakhiri sesi | `auth.logout`, `auth.signOut` | FROZEN |
| Required (field) | Wajib diisi | Validasi field wajib | `validation.required`, `framework.field_required` | FROZEN |
| Loading | Memuat | Indikator muat | `common.loading` | FROZEN |
| Actions | Tindakan | Kolom/aksi tersedia | `common.actions` | FROZEN |
| Yes / No | Ya / Tidak | Boolean UI | `common.yes`, `common.no` | FROZEN |
| Active / Inactive | Aktif / Nonaktif | Status aktifitas | `common.active`, `users.deactivate` | FROZEN |
| Severity | Severity | Dampak teknis/bisnis; **jangan** disamakan otomatis dengan Prioritas | GLOSS-001 | FROZEN |
| Reopen | Buka kembali | Membuka Case/pengaduan yang sudah ditutup (sesuai aturan) | GLOSS-001 | FROZEN |

## Explicit Rejected Synonyms (UI)

| Jangan dipakai (UI) | Pakai |
|---|---|
| Komplain | Pengaduan |
| Kasus (sebagai label Case) | Case |
| Queue (label UI) | Antrian |
| Attachment (label UI) | Lampiran |
| User (label UI) | Pengguna |
| Role (label UI) | Peran |
| Permission / Hak Akses (label UI) | Izin |
| Settings (label UI) | Pengaturan |
| Logout (label UI) | Keluar |
| Harus diisi (untuk required field) | Wajib diisi |
| Appointment (label UI) | Janji temu |

## Status Enum Tokens (keep English in data/API)

`NEW`, `ASSIGNED`, `IN_PROGRESS`, `PENDING`, `ESCALATED`, `RESOLVED`, `CLOSED`, `REQUESTED`, `APPROVED`, `REJECTED`, `BOOKED`, `CHECKED_IN`, `COMPLETED`, `ON_TIME`, `BREACHED`, dll. — kode tetap Inggris; label tampilan mengikuti namespace `status.*` di `messages/id.json`.

## Governance Rules

1. Satu konsep bisnis = satu istilah Indonesia resmi (tabel di atas).
2. Dilarang menciptakan sinonim UI baru di luar tabel freeze.
3. Kode teknis (permission string, enum, event ID, path API) tetap Inggris.
4. Perubahan istilah resmi membutuhkan review LRB + dampak ke `messages/id.json` / `user_messages.py` / dokumentasi pengguna.
5. `docs/business/glossary.md` adalah mirror; SoT = berkas ini.

## Known Alignment Debt

Ditutup pada Sprint L10-06 (Language Freeze Closure): salinan “kasus”, pesan “Appointment”, dan `common.clear` vs `common.delete` telah diselaraskan ke GLS-001.
