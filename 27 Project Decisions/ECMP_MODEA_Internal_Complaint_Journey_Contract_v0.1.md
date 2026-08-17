# Mode A Contract — Pengaduan Internal (Journey)

| Field | Value |
|---|---|
| ID | ECMP-MODEA-INT-001 |
| Version | 0.1 |
| Owner | Product Owner / Domain PO |
| Reviewer | Solution Architect |
| Approver | Business Owner (Mode A lab) |
| Status | 🟢 Accepted for Mode A UI (2026-08-17) |
| Date | 2026-08-17 |
| Type | Mode A lab contract (non-ADR, non-DEC) |
| Related | DEC-025 §14.1 D (`/internal/*` bukan Dual-SoT WP); OpenAPI `internal-complaints.v1.yaml` |

**Bukan** ADR. **Bukan** unlock Mode B. **Tidak** mengubah BR-CM-CAT / Case Aggregate WP.

---

## 1. Identitas

- Satu tiket = satu aggregate. **Tidak ada Case child.**
- Nomor: `PI-{UNIT}-{YYMM}-{NNN}` (contoh `PI-TAB-2608-001`).
- **Unit pemilik** = unit pembuat, tidak pernah berubah.
- **Unit penanganan** mulai sama dengan unit pemilik; hanya berubah saat transfer Cabang ↔ Pusat.
- Tautan `relatedComplaintId` ke pengaduan WP bersifat opsional. Tutup Internal **tidak** menutup WP.
- API: `/api/v1/internal/complaints`. UI: `/internal/*` (flag `NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI`, default off).

## 2. Aktor (Mode A)

| Peran | Yang boleh |
|---|---|
| Petugas (Agent / CS / Handler / Branch Officer) | Buat; dari cabang langsung ke Pusat; batal sepihak sebelum Terima; minta batal setelah Terima; ajukan pindah (hanya tiket Pusat lokal, bukan pindah langsung); terima & kerjakan (hanya di unit penanganan); usulkan penyelesaian |
| Supervisor / Manager | Semua di atas + pindah Handling langsung; putuskan pengajuan pindah Agent; putuskan permintaan batal (unit penanganan); setujui/tolak gerbang tutup |
| Admin | Putuskan pengajuan pindah lintas unit; putuskan permintaan batal; gerbang tutup tanpa terikat unit |

Pemisahan tugas: Supervisor/Manager/Admin **tidak** boleh menjadi pihak persetujuan penutup jika dia yang membuat tiket.

## 3. Status dan transisi

`CREATED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED`  
Cabang → Pusat, sebelum Terima: `ASSIGNED → WITHDRAWN` (batal sepihak).  
Setelah Terima: `IN_PROGRESS` + permintaan PENDING; Setujui → `WITHDRAWN`; Tolak → tetap `IN_PROGRESS`.

| Langkah | Dari | Ke | Syarat |
|---|---|---|---|
| Buat (Pusat) | — | `CREATED` | Unit pemilik = unit penanganan = unit pembuat |
| Buat (Cabang) | — | `ASSIGNED` di Pusat | Semua peran cabang; Handling langsung Pusat; tanpa gerbang transfer-request |
| Pindah Handling | `CREATED` / `ASSIGNED` / `IN_PROGRESS` | `ASSIGNED` | Hanya Cabang ↔ Pusat; bukan `RESOLVED`/`CLOSED`/`WITHDRAWN` |
| Petugas Pusat ajukan pindah | `CREATED` (masih lokal Pusat) | tetap `CREATED` + permintaan PENDING | Alasan wajib; APPROVE = pindah ke cabang; REJECT = tetap lokal, boleh ajukan ulang |
| Terima / mulai kerja | `CREATED` atau `ASSIGNED` | `IN_PROGRESS` | Aktor di **unit penanganan** (cabang pembuat tidak melihat Terima) |
| Cabang batal sepihak | `ASSIGNED` (handling Pusat, belum Terima) | `WITHDRAWN` | Pembuat atau Supervisor unit pemilik; alasan wajib; **tanpa notifikasi ke Pusat**; tiket hilang dari antrean Terima |
| Cabang minta batal | `IN_PROGRESS` (owner cabang, handling Pusat) | tetap `IN_PROGRESS` + PENDING | Alasan wajib; satu PENDING; tiket tetap dikerjakan |
| Pusat setujui batal | `IN_PROGRESS` + PENDING | `WITHDRAWN` | Supervisor/Admin unit penanganan (Pusat) |
| Pusat tolak batal | `IN_PROGRESS` + PENDING | `IN_PROGRESS` | Alasan wajib; cabang boleh minta lagi |
| Usulkan penyelesaian | `IN_PROGRESS` | tetap `IN_PROGRESS` | `PROPOSE` (komentar + ringkasan; kode mesin `IC_DONE`, tidak ditampilkan) |
| Terima penyelesaian | `IN_PROGRESS` | `RESOLVED` | `ACCEPT` → cap otomatis unit penanganan sudah setuju; kode mesin `IC_DONE` bila klien tidak mengirim kode |
| Tolak usulan | `IN_PROGRESS` | `IN_PROGRESS` | Alasan wajib |
| Setuju penutup | `RESOLVED` | `CLOSED` | Kedua pihak setuju (lihat §4) |
| Tolak penutup | `RESOLVED` | `IN_PROGRESS` | Catatan wajib; cap setuju direset |

Tidak ada: `REGISTERED`, `CANCELLED` (katalog WP), `PENDING`, `ESCALATED` sebagai status tiket. Status terminal tipis **`WITHDRAWN`** (label UI: Dibatalkan) — bukan `CANCELLED`. `RESOLVED`/`CLOSED` tidak bisa dibatalkan.

## 4. Gerbang tutup (UI)

Jangan tampilkan `OWNER` / `HANDLING_UNIT` ke petugas.

**Jika sudah dipindah (unit pemilik ≠ unit penanganan):**  
“Unit penanganan menyelesaikan. Unit pemilik harus menyetujui sebelum ditutup.”  
Tombol: **Setujui sebagai unit penanganan** · **Setujui sebagai unit pemilik** · **Kembalikan ke pengerjaan**.

**Jika tidak dipindah (masih di unit pembuat):**  
Cap unit penanganan sudah otomatis saat penyelesaian diterima. Sisa gerbang: Supervisor unit pemilik.  
“Petugas menyelesaikan. Supervisor unit pemilik harus menyetujui sebelum ditutup.”  
Tombol: **Setujui penyelesaian** · **Kembalikan ke pengerjaan**.

Setelah syarat terpenuhi, status menjadi **Ditutup** otomatis. Endpoint close tidak boleh menembus gerbang ini.

## 5. Antrian UI

Assignments / Follow-up / Verification / Reports adalah **filter daftar tiket Internal**, bukan workspace Case WP. Copy halaman memakai bahasa Pengaduan Internal.

## 6. Dilarang di slice ini

Menyalin alur WP (Case, intake HQ, BQ-007). Izin `internal:*` penuh. Laporan/KPI sungguhan. `CANCELLED` katalog WP. Mode B / SSO. Katalog resolusi bisnis (selain sentinel `IC_DONE`). Notifikasi ke Pusat saat cabang batal sepihak sebelum Terima.

## Follow-up

- Binding UI Mode A: `frontend/src/features/internal-complaints/` + `frontend/messages/{id,en}.json`
- Kode penyelesaian tidak ditampilkan ke petugas; UI mengirim `IC_DONE`. Tiket lama `IC-OK` tetap valid.
- Domain/API tidak diubah oleh Accept kontrak ini (kecuali default sentinel kosong → `IC_DONE`)
- Lampiran Internal: CAP-011 `aggregateType=InternalComplaint` (bukan `cm_batch1_attachments`). Gambar + ZIP; ZIP tidak diekstrak.
