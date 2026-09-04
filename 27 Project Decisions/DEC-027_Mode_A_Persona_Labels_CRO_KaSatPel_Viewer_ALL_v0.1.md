# Decision Record — Label persona Mode A (CRO / Staff KaSatPel / KaSatPel) dan Viewer baca-semua

| Field | Value |
|---|---|
| ID | DEC-027 |
| Version | 0.1 |
| Owner | Business Owner / Solution Architect |
| Status | 🟢 Accepted (lab Mode A) — implementasi diotorisasi |
| Date | 2026-08-20 |
| Related | DEC-024 (visibility); ADR-008 (Role-Permission SoT); BC-8 / BG-018 (persona operasional) |
| Type | Project Decision (label + visibilitas lab) — **bukan** Mode B unlock · **bukan** merge peran · **bukan** rewrite BR/FRD/ADR |

---

## 1. Intent

Operator lab memakai sebutan organisasi, bukan label generik Petugas / Supervisor / Manager. Jenjang wewenang **tetap tiga persona operasional** plus Admin dan Viewer. Kode peran IAM **tidak diganti**.

## 2. Decision

### 2.1 Label tampilan (kode tetap)

| Kode lab | Tampilan ID | Tampilan EN | Kepanjangan |
|---|---|---|---|
| `AGENT` (+ alias `CS_AGENT`, `HANDLER`, `BRANCH_OFFICER`) | CRO | CRO | Customer Relationship Officer |
| `SUPERVISOR` (+ alias `BRANCH_SUPERVISOR`) | Staff KaSatPel | Staff KaSatPel | staf Kepala Satuan Pelaksana |
| `MANAGER` | KaSatPel | KaSatPel | Kepala Satuan Pelaksana |
| `ADMIN` (+ alias `ADMINISTRATOR`, `SUPER_ADMIN` di UI) | Admin | Admin | — |
| `VIEWER` | Viewer / Peninjau | Viewer | baca saja |

Picker create/edit user Mode A: kelima kode di atas. Alias sistem lain tetap tersembunyi.

`SUPERVISOR` **tidak dihapus** dan **tidak dinonaktifkan**. Bukan alias `MANAGER`.

### 2.2 Viewer — baca semua, tanpa aksi

Perluasan DEC-024: `VIEWER` memakai visibility class **`ALL`** untuk daftar pengaduan/case (lintas unit), setara jangkauan baca Admin.

- Mutasi domain ditolak di API (tidak ada `complaints:create` / update / assign / escalate / close / attachment tulis). UI tanpa tombol mutasi.
- Kontak pelanggan tetap masked (bukan CRO).
- Bukan Admin: tidak mengelola konfigurasi / peran / keanggotaan.
- Baca IAM yang sudah ada (`role:read`, dll.) tidak dicabut di slice ini; form ubah tetap tertutup karena tidak ada permission tulis.

### 2.3 Di luar keputusan ini

| Topik | Status |
|---|---|
| Ganti role code (`AGENT`→`CRO`, …) | Tidak |
| Hapus / merge `SUPERVISOR` ke `MANAGER` | Tidak |
| Rewrite BC-8.4 / FRD / ADR | Tidak — SoT dokumen menyusul bila BO meminta |
| Mode B / SSO / Identity Adapter | CLOSED |
| Marker riwayat intake `Catatan Supervisor` | Tetap (parser kompatibilitas) |

## 3. Acceptance

1. Picker menampilkan CRO, Staff KaSatPel, KaSatPel, Admin, Viewer.
2. Viewer melihat baris pengaduan lintas unit; POST create ditolak.
3. Role code di database tidak berubah.
