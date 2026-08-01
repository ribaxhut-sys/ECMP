# CLAUDE.md — Konstitusi kerja di repo ECMP

Bahasa jawaban: **Bahasa Indonesia**.

---

## 1. North Star — prioritas di atas saran apa pun

> "Menyelesaikan Complaint Management Module dengan arsitektur yang benar, sehingga
> ketika pintu Enterprise Application terbuka, yang berubah hanyalah mekanisme
> integrasinya — bukan domain bisnisnya."

Sebelum merekomendasikan apa pun, lewatkan **tiga filter**:

1. Apakah ini membuat Complaint Module lebih dekat ke COMPLETE? Bila tidak → tolak.
2. Apakah ini menjaga Domain Complaint tetap stabil? Bila tidak → tolak.
3. Apakah ini membuat integrasi Enterprise lebih mudah? Bila tidak → tolak.

Perubahan pada **mekanisme integrasi** (adapter identity, SSO, organization provider,
notification, shared service) selalu boleh. Perubahan pada **domain komplain** harus
dibuktikan dibutuhkan bisnis.

Ide bagus yang tidak membantu modul selesai ditulis satu baris saja:
*"Future Work — Di luar ruang lingkup Complaint Management Module."* lalu berhenti.
Jangan dibahas.

**Dilarang memperluas menjadi:** Enterprise Platform · Enterprise OS · generic SDK ·
framework multi-modul · marketplace · governance baru — kecuali diminta eksplisit.

Latar belakang: sepanjang audit Juli 2026 pembahasan sempat melebar dari "selesaikan
modul komplain" menjadi desain platform untuk belasan modul masa depan. Itu dihentikan
dan konstitusi ini ditetapkan.

---

## 2. ECMP adalah modul, bukan aplikasi standalone

ECMP adalah **satu modul komplain** di dalam Enterprise Application Platform yang lebih
besar. **Aplikasi utama itu sudah jadi dan beroperasi** — ECMP pihak konsumen yang
menyesuaikan diri, bukan yang menetapkan syarat. Ditetapkan ADR-014 dan ADR-015
(ditulis 2026-07-29, **setelah** rilis v1.0.0), sehingga sebagian besar kode yang ada
masih mencerminkan desain standalone.

| Enterprise Platform memiliki | ECMP memiliki |
|---|---|
| Authentication, SSO, User Directory | Complaint Management, Assignment |
| Password Management, MFA, Session | Escalation, Resolution, SLA, Timeline |
| Organization / Branch / Department | Complaint KPI |
| Portal & Navigation, Global Notification | **Authorization** (peran & permission internal) |
| Identity Audit | |

**Konsekuensi saat menilai pekerjaan:** fitur yang tampak benar untuk aplikasi standalone
bisa jadi utang yang harus dibongkar untuk sebuah modul — contohnya sprint yang menambah
password management UI dan admin reset. Selalu tanyakan *"apakah ini milik ECMP atau
milik Enterprise Platform?"* sebelum menilai kelengkapan sebuah fitur.

**Mode A dan Mode B bukan dua arsitektur.** Target architecture selalu satu; yang berbeda
hanya strategi implementasi. Perilaku domain wajib identik di kedua mode.
Di kode: `ECMP_AUTH_MODE=dev` (Mode A, auth lokal) atau `jwt` (Mode B, SSO).

**Peringatan kontrak identitas:** repo ini tidak memuat satu pun artefak dari aplikasi
utama — tidak ada issuer produksi, token nyata, spesifikasi entitlement/user directory/org,
maupun metode integrasi portal. Semua referensi IdP menunjuk realm `ecmp` di
`localhost:8180` yang di-provision ECMP sendiri. Artinya kontrak identitas yang
diimplementasikan adalah **karangan ECMP, belum diverifikasi** ke pemilik platform.
Sebelum menilai atau merencanakan pekerjaan identitas apa pun, tanyakan dulu apakah
kontrak nyata sudah diperoleh.

---

## 3. Struktur repo

Folder bernomor `00`–`27` adalah dokumentasi arsitektur (EAR). Yang sering dipakai:

- `02 Business Rules`, `03 Functional Requirements` — sumber kebenaran perilaku
- `04 Solution Architecture`, `05 Architecture Decision Records` — ADR-014 (Business Module v1.4), ADR-015 (Identity Contract v1.3); Mode B Closed (C-7)
- `13 Test Strategy`, `14 Deployment Standards`, `15 Operations Runbook`
- `16 Release Management`, `18 Architecture Governance`, `26 Traceability`

Kode:

- `backend/` — FastAPI + SQLAlchemy + Alembic (Python 3.13, ruff line-length 100)
- `frontend/` — Next.js + TypeScript
- `deploy/proxy/` — Caddy dan nginx (lab override + certs)
- `deploy/README.md` (+ evidence pack) — operasi lab/VPS / bootstrap & panduan Claude Code di server (folder `deploy/vps/` **BELUM ADA** sebagai tree terpisah)
- `scripts/validate-production-config.py` — validator konfigurasi fail-fast
- `scripts/release/` — helper rilis

---

## 4. Perintah

```bash
# Backend
cd backend && pytest                      # konfigurasi di pytest.ini
cd backend && ruff check app tests
cd backend && alembic upgrade head

# Frontend
cd frontend && npm run typecheck
cd frontend && npm run lint               # --max-warnings 0
cd frontend && npm test                   # vitest
cd frontend && npm run check:auth-routes  # guard Mode A credential routes

# Produksi
python scripts/validate-production-config.py --env-file .env --require-production
docker compose -f docker-compose.prod.yml up -d --build
```

---

## 5. Aturan rahasia dan konfigurasi

- **`.env` tidak pernah di-commit.** Sudah di-gitignore; jangan pernah dilonggarkan.
- Jangan menulis token API, password, atau kunci apa pun ke dalam file di repo ini —
  termasuk ke dalam dokumentasi atau contoh.
- `.env.production.example` / `.env.prod.example` hanya template; semua nilainya placeholder.
- Saat menampilkan isi `.env` untuk diagnosis, ambil hanya kunci non-rahasia
  (`ECMP_DOMAIN`, `ENVIRONMENT`, `ECMP_AUTH_MODE`, `IMAGE_TAG`, dsb).

**Gerbang konfigurasi yang menghentikan startup** (`backend/app/core/config.py`):

- `ENVIRONMENT=production|staging` **mewajibkan** `ECMP_AUTH_MODE=jwt` (baris ~436).
- `ECMP_AUTH_MODE=jwt` **mewajibkan** `OIDC_ISSUER`, `OIDC_AUDIENCE`, `OIDC_JWKS_URL`
  terisi (baris ~497–532).
- `ECMP_ENV=shared` menolak `ECMP_AUTH_MODE=dev`.

Artinya deploy produksi tidak mungkin tanpa IdP yang nyata. Bila belum ada, itu keputusan
bisnis — angkat ke pengguna, jangan diakali dengan menurunkan `ENVIRONMENT`.

---

## 6. Deployment

Stack produksi (`docker-compose.prod.yml`, project `ecmp-prod`): Caddy 2.8 (TLS otomatis) ·
PostgreSQL 16 · backend · frontend. Backend dan frontend **dibangun dari source**
(`build: context:`), jadi deployment memerlukan repo lengkap di host — tidak bisa lewat
API yang hanya mengirim isi compose.

VPS lab (contoh): Hostinger, `srv1869401.hstgr.cloud`. User aplikasi `ecmp` (grup `sudo` + `docker`) bila di-provision demikian.
ufw mengizinkan 80/443, SSH di-rate-limit. Firewall hPanel / panel host adalah lapisan terpisah —
keduanya harus mengizinkan. Panduan: `deploy/README.md`, `deploy/proxy/README.md` (bukan `deploy/vps/` — tree terpisah belum ada).

Ambil snapshot hPanel sebelum deploy produksi pertama.

---

## 7. Cara bekerja

- Jawab ringkas. Hilangkan kata yang bisa dihilangkan tanpa mengubah makna.
- Sebelum menyatakan sesuatu tentang kode, **baca berkasnya** — jangan menebak.
- Bila sebuah saran gagal salah satu dari tiga filter di bagian 1, katakan begitu dan
  berhenti. Jangan diteruskan dengan alasan "mumpung".
- Bila menemukan penghambat (seperti gerbang konfigurasi di bagian 5), sampaikan lebih
  dulu sebelum menyusun rencana panjang yang akan gagal di langkah pertama.
