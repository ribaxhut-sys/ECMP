# ECMP Local Stack — PC Lab (Mode A)

Jalankan di PC **fitur yang sama** dengan VPS lab Mode A, tanpa domain/Caddy/TLS.

| Di VPS lab | Di PC lokal |
|---|---|
| `https://pengaduan.layanankami.tech` | `http://localhost:3000` |
| Caddy + DNS + 443 | Tidak perlu |
| Docker Compose | Docker Compose (sama) |
| Mode A credential login | Mode A credential login (sama) |
| Postgres + seed pelanggan | Postgres + seed (opsional, disarankan) |

Mode B / SSO **tetap CLOSED** — tidak diganti oleh setup lokal ini.

## Prasyarat (Windows)

1. **Git for Windows** — https://git-scm.com/download/win  
2. **Docker Desktop for Windows** — https://www.docker.com/products/docker-desktop/  
   - Aktifkan **WSL2** backend (Settings → General → Use WSL 2)  
   - Pastikan Docker running (ikon whale di tray)  
3. RAM disarankan ≥ 8 GB  
4. Port bebas: `3000`, `8000`, `5433`

Cek di **PowerShell**:

```powershell
git --version
docker version
docker compose version
```

## 1. Ambil kode (`main`)

PowerShell:

```powershell
cd $HOME\Projects   # atau folder kerja Anda
git clone https://github.com/ribaxhut-sys/ECMP.git
cd ECMP
git checkout main
git pull
```

## 2. Environment

```powershell
Copy-Item .env.example .env
notepad .env
```

Pastikan nilai ini (paritas VPS lab):

| Kunci | Nilai lokal |
|---|---|
| `ENVIRONMENT` | `development` |
| `ECMP_AUTH_MODE` | `dev` |
| `ECMP_LOCAL_CREDENTIAL_AUTH` | `true` |
| `ECMP_ENTERPRISE_MODE` | `false` |
| `NEXT_PUBLIC_API_BASE_URL` | `http://localhost:8000` |
| `ALLOWED_ORIGINS` | `http://localhost:3000` |
| `CUSTOMER_PROVIDER` | `local` |

Jangan commit file `.env`.

## 3. Jalankan stack

Dari folder repo (`ECMP`):

```powershell
docker compose up -d --build
```

Build pertama bisa 5–15 menit. Cek:

```powershell
docker compose ps
curl.exe -fsS http://localhost:8000/live
curl.exe -fsS http://localhost:8000/ready
```

| Layanan | URL |
|---|---|
| Frontend / login | http://localhost:3000/login |
| Backend API | http://localhost:8000 |
| OpenAPI (dev) | http://localhost:8000/docs |
| Postgres (host) | `localhost:5433` |

Buka browser: **http://localhost:3000/login**

## 4. Seed data lab (paritas VPS)

Tanpa seed, pencarian pelanggan sering kosong.

```powershell
Get-Content .\deploy\seed-lab-customers-500.sql -Raw |
  docker compose exec -T postgres psql -U ecmp -d ecmp

# Opsional user kandidat modul
Get-Content .\deploy\seed-lab-module-users-200.sql -Raw |
  docker compose exec -T postgres psql -U ecmp -d ecmp

docker compose restart backend
```

Buat user lab lewat UI **Users** (perlu akun admin dulu). Password sementara create-user lab: `LabTemp!2026` (hanya Mode A lab).

> DB lokal baru belum otomatis berisi user VPS (`admin` / NIK lab). Buat admin/agent/supervisor di lokal lewat UI, atau salin seed user secara terpisah — **jangan** commit password ke git.

## 5. Alur uji singkat (sama VPS, host beda)

1. Login → http://localhost:3000/login  
2. Buat pengaduan → `/complaints/new`  
3. Daftar Aggregate → `/complaints/cm`  
4. Detail / Setujui eskalasi (supervisor) → `/complaints/cm/{id}`  

Checklist: `deploy/UAT_LAB_BATCH1_AGENT_10_MIN.md` (ganti URL domain → `localhost:3000`).

## 6. Perintah sehari-hari (PowerShell)

```powershell
docker compose logs -f backend frontend
docker compose restart backend frontend
docker compose down          # stop; data volume tetap
docker compose down -v       # HATI-HATI: hapus DB + lampiran
```

Update kode dari GitHub:

```powershell
git pull origin main
docker compose up -d --build
```

## Tanpa Docker penuh (opsional, advanced)

Hanya Postgres di Docker; API/UI di host (butuh Python 3.13 + Node 20+).

```powershell
docker compose up -d postgres

# Terminal 1 — backend
cd backend
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
# POSTGRES_HOST=localhost POSTGRES_PORT=5433 di environment / .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

## Bukan bagian lokal (milik VPS / Mode B)

- Caddy, Let’s Encrypt, DNS `pengaduan.layanankami.tech`
- Firewall ufw / hPanel
- SSO / OIDC / Identity Adapter Mode B

## Troubleshooting Windows

| Gejala | Cek |
|---|---|
| `docker` tidak dikenali | Install/start Docker Desktop; restart PowerShell |
| WSL error | Settings Docker → Use WSL 2; `wsl --update` |
| Port bentrok | Ubah `FRONTEND_PORT` / `BACKEND_PORT` / `POSTGRES_PORT` di `.env` |
| `curl` gagal | Pakai `curl.exe` (bukan alias `Invoke-WebRequest`) |
| Frontend build gagal | `NEXT_PUBLIC_API_BASE_URL` wajib di `.env` |
| Cari pelanggan kosong | `CUSTOMER_PROVIDER=local` + jalankan seed customers |
| Login gagal berkali-kali | Rate-limit; `docker compose restart backend` |
| File SQL pipe gagal | Pastikan path `.\deploy\...` dari root repo; encoding UTF-8 |

## Referensi

- Compose: `docker-compose.yml`
- Produksi/TLS VPS: `deploy/README.md` + `docker-compose.prod.yml`
- Validasi env: `python scripts/validate-production-config.py --env-file .env`
