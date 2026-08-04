# UAT lab Mode A — 10 langkah (operator)

| Field | Value |
|---|---|
| Date | 2026-08-04 |
| Status | Siap dijalankan |
| Target modul | `https://pengaduan.layanankami.tech` |
| Pintu lab | `https://layanankami.tech` (landing saja — bukan SSO) |
| Mode B / SSO | **SKIP** — belum ada kunci EP |

Isi kolom **Hasil** dengan `PASS` / `FAIL` / `BLOCKED` + catatan singkat.
Username lab: `admin`, `agent1`, `supervisor1` — password di `/root/.ecmp-credentials` (VPS).

---

## Langkah

| # | Aksi | URL / tempat | Hasil | Catatan |
|---|---|---|---|---|
| 1 | Buka pintu lab → klik **Masuk ke Pengaduan** | `https://layanankami.tech` | | Harus land di `/login` modul |
| 2 | Login sebagai `admin` | `…/login` | | Masuk `/dashboard`, bukan stuck di login |
| 3 | Dashboard tampil tanpa error | `…/dashboard` | | Angka/overview boleh 0 |
| 4 | Buka daftar pengaduan | `…/complaints` | | List load |
| 5 | Buat pengaduan baru (isi wajib) | `…/complaints/new` | | Dapat nomor/ID; status awal (mis. NEW) |
| 6 | Buka detail pengaduan yang baru | `…/complaints/{id}` | | Data sesuai input |
| 7 | Logout (atau clear session) → login `supervisor1` | `…/login` | | Assign butuh SUPERVISOR |
| 8 | Assign pengaduan ke `agent1` (jika UI/API tersedia) | detail / aksi assign | | Status → ASSIGNED (atau setara) |
| 9 | Login `agent1` → lihat item yang di-assign | `…/complaints` / detail | | Terlihat oleh agent |
| 10 | Smoke teknis (opsional, dari VPS) | perintah di bawah | | |

### Perintah langkah 10 (VPS)

```bash
./deploy/smoke-lab.sh https://pengaduan.layanankami.tech
```

Harap: `health_http=200`, `login_page_http=200`, `docs_http=404`, `smoke_ok`.

---

## Dual-SoT (jangan bingung)

| Jalur | Kapan dipakai di UAT ini |
|---|---|
| Foundation UI `/complaints` (+ API `/api/v1/complaints`) | **Utama** untuk 10 langkah di atas |
| Aggregate CM `/complaints/cm/…` (+ `/api/v1/cm`) | Opsional / terpisah — jangan anggap menggantikan foundation |

Jangan force-merge atau “pindah semua ke CM” tanpa Retirement DEC.

---

## Jika gagal — klasifikasi cepat

| Gejala | Arah perbaikan |
|---|---|
| Landing apex error / bukan tombol Pengaduan | DNS/Caddy apex (Opsi A) |
| Login 401 | Password / user lab |
| Create gagal (customer/branch/SLA kosong) | Seed master data lab |
| Assign ditolak | Role `SUPERVISOR` + permission assign |
| Halaman CM vs complaints beda perilaku | Dual-SoT — laporkan jalur mana |

---

## Setelah 10 langkah

1. Kirim ringkas: nomor mana **FAIL** (mis. “5 dan 8 gagal …”).  
2. Kita perbaiki **gap itu saja** (Mode A).  
3. Jangan mulai SSO / Identity Adapter.

## Sign-off lab (U-5 — manusia)

| Peran | Nama | Tanggal | Setuju modul lab layak pakai? |
|---|---|---|---|
| Operator / BO | | | Ya / Tidak |
| Catatan sisa | | | |

*Checklist ini Mode A only. Sambungan Coretax-like = checklist Mode B terpisah.*
