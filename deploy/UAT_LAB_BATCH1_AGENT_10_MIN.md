# UAT lab Batch-1 — checklist agent (~10 menit)

| Field | Value |
|---|---|
| Date | 2026-08-06 |
| Target | `https://pengaduan.layanankami.tech` |
| Scope | Mode A Batch-1 intake + Case (DEC-020 dual-SoT) |
| Bukan scope | Mode B / SSO · force-merge 1 SoT · Retirement DEC |

Isi **Hasil** dengan `PASS` / `FAIL` / `BLOCKED` + catatan singkat.

Password lab bersama (jika masih berlaku): lihat kredensial VPS lab — jangan commit rahasia.

---

## Peta dua daftar (baca dulu — 30 detik)

| URL | Arti untuk agent |
|---|---|
| `/complaints` | Daftar **fondasi** (SoT lama). Create Batch-1 **tidak** wajib muncul di sini. |
| `/complaints/cm` | **Daftar pengaduan** Batch-1 — hasil form buat yang Anda pakai sekarang. |
| `/complaints/cm/supervisor` | **Perlu tinjauan** (later-review / aging) — **bukan** daftar semua pengaduan. |

Selesai bisnis = **Case CLOSED**, bukan hilangnya baris dari `/complaints/cm`.

---

## Checklist (~10 menit)

| # | Aksi | Tempat | Hasil | Catatan |
|---|---|---|---|---|
| 1 | Login agent (contoh `3100000000000001` / user lab agent) | `/login` | | Masuk dashboard |
| 2 | Buat pengaduan baru (pelanggan + subjek + deskripsi). Lampiran **opsional**. | `/complaints/new` | | Dapat `CM-…` / confirmation |
| 3 | Pastikan pengaduan terlihat di daftar Batch-1 | `/complaints/cm` | | **Jangan** cek hanya di `/complaints` |
| 4 | Buka detail → cek subjek / customer | `/complaints/cm/{id}` | | Data sesuai input |
| 5a | *(Jika ada lampiran bermasalah)* lihat tinjauan Terbuka | `/complaints/cm/supervisor` | | Alasan mis. bind lampiran |
| 5b | *(Jika 5a)* upload ulang di detail → tinjauan tidak lagi Terbuka | detail + supervisor | | Later-review CLOSED ≠ Case closed |
| 6 | Kelola Case → buat Case (jika belum ada) | `/complaints/cm/{id}/cases` | | Case muncul |
| 6b | Lihat **Daftar Case** sesuai peran (agent: milik sendiri) | `/complaints/cm/cases` | | API-536 / DEC-024 |
| 7 | **Skenario selesai di tempat:** Resolve Case lalu Close Case | detail Case | | Butuh syarat resolve + approval lab |
| 8 | **Skenario lanjut:** biarkan Case open (jangan close) | detail Case | | Aggregate tetap di `/complaints/cm` |
| 9 | Pastikan `/complaints` fondasi **tidak** dipakai sebagai bukti “pengaduan hilang” | `/complaints` | | Dual-SoT — PASS jika Anda sadar bedanya |
| 10 | Logout | | | Sesi bersih |

Lewati 5a/5b jika tidak ada later-review.

---

## Lulus cepat (DoD lab agent)

- [ ] Create → terlihat di `/complaints/cm`
- [ ] Detail + (opsional) lampiran bisa dibuka
- [ ] Case bisa dibuat  
- [ ] Daftar Case (`/complaints/cm/cases`) menampilkan Case sesuai peran  
- [ ] Satu jalur: Resolve→Close **atau** Case tetap open untuk lanjut  
- [ ] Tidak mengira supervisor = daftar pengaduan
- [ ] Tidak force-merge ke satu URL tanpa Board

---

## Jika gagal — klasifikasi

| Gejala | Bukan berarti | Arah |
|---|---|---|
| `/complaints` kosong setelah create | Bug hilang data | Cek `/complaints/cm` (DEC-020) |
| Masih di daftar setelah lampiran OK | Gagal close | Normal — arsip Aggregate |
| Later-review CLOSED | Pengaduan selesai | Lanjut Case Resolve/Close |
| Tidak bisa Close Case | UI rusak total | Cek syarat RESOLVED + approval |

---

## Setelah checklist

1. Laporkan nomor langkah **FAIL** saja.  
2. Perbaiki gap Mode A itu — jangan mulai SSO / 1 SoT.  
3. Usulan “satu daftar saja” = proposal Retirement DEC (Board), paralel.  
4. Visibility daftar Case per peran: draft `27 Project Decisions/DEC-024_Case_List_Visibility_Matrix_Mode_A_v0.1.md` (sign-off BO sebelum coding list API).

*Dokumen ini melengkapi `UAT_LAB_MODE_A_10_STEPS_20260804.md` (fondasi). Untuk uji form Batch-1 saat ini, pakai checklist ini.*
