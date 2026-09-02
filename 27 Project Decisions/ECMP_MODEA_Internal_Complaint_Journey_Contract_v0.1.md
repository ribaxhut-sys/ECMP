# Mode A Contract — Pengaduan Internal (Journey)

| Field | Value |
|---|---|
| ID | ECMP-MODEA-INT-001 |
| Version | 0.5 |
| Owner | Product Owner / Domain PO |
| Reviewer | Solution Architect |
| Approver | Business Owner (Mode A lab) |
| Status | 🟢 Accepted for Mode A UI (2026-08-17); v0.2 kelengkapan berkas; v0.3 visibilitas WITHDRAWN; v0.4 usulan dua pihak (2026-08-19); v0.5 snapshot PDF (2026-09-02) |
| Date | 2026-09-02 |
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
- API: `/api/v1/internal/complaints` (snapshot PDF: `.../{id}/export`, API-550). UI: `/internal/*` (flag `NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI`, default off).

## 2. Aktor (Mode A)

| Peran | Yang boleh |
|---|---|
| Petugas (Agent / CS / Handler / Branch Officer) | Buat; dari cabang langsung ke Pusat; batal sepihak sebelum Terima; minta batal setelah Terima; ajukan pindah (hanya tiket Pusat lokal, bukan pindah langsung); terima & kerjakan (hanya di unit penanganan); kembalikan ke cabang jika berkas kurang (sebelum atau sesudah Terima); kirim ulang ke Pusat setelah dilengkapi; usulkan penyelesaian |
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
| Terima / mulai kerja | `CREATED` atau `ASSIGNED` | `IN_PROGRESS` | Aktor di **unit penanganan** (cabang pembuat tidak melihat Terima). Diblokir saat menunggu kelengkapan (`completionRequestStatus=PENDING`) |
| Kembalikan ke cabang (berkas kurang) | `ASSIGNED` atau `IN_PROGRESS` | `ASSIGNED` di unit pemilik | Owner cabang, handling Pusat; aktor di unit penanganan; alasan wajib. **Bukan** Tolak/`WITHDRAWN`. Handling kembali ke cabang; tiket tetap hidup |
| Cabang kirim ulang ke Pusat | `ASSIGNED` + PENDING kelengkapan | `ASSIGNED` di Pusat | Aktor di unit pemilik; **catatan wajib**; lampiran boleh ditambah dulu. Pusat **Terima** lagi |
| Cabang batal sepihak | `ASSIGNED` (handling Pusat, belum Terima) **atau** menunggu kelengkapan | `WITHDRAWN` | Pembuat atau Supervisor unit pemilik; alasan wajib; **tanpa notifikasi ke Pusat**; tiket hilang dari antrean Terima |
| Cabang minta batal | `IN_PROGRESS` (owner cabang, handling Pusat) | tetap `IN_PROGRESS` + PENDING | Alasan wajib; satu PENDING; tiket tetap dikerjakan |
| Pusat setujui batal | `IN_PROGRESS` + PENDING | `WITHDRAWN` | Supervisor/Admin unit penanganan (Pusat) |
| Pusat tolak batal | `IN_PROGRESS` + PENDING | `IN_PROGRESS` | Alasan wajib; cabang boleh minta lagi |
| Usulkan penyelesaian | `IN_PROGRESS` | tetap `IN_PROGRESS` | Hanya **unit penanganan**. `PROPOSE` (komentar + ringkasan; kode mesin `IC_DONE`, tidak ditampilkan). Mengganti usulan PENDING sebelumnya |
| Terima usulan | `IN_PROGRESS` | `RESOLVED` | Hanya **unit pemilik**; wajib ada usulan `PENDING_APPROVAL`; pengusul **tidak** boleh menerima sendiri. Tidak ada pintasan ACCEPT tanpa usulan. Cap otomatis unit penanganan memakai pengusul; kode mesin `IC_DONE` bila klien tidak mengirim kode |
| Tolak usulan | `IN_PROGRESS` | `IN_PROGRESS` | Hanya **unit pemilik**; alasan wajib; pengusul tidak boleh menolak sendiri |
| Setuju penutup | `RESOLVED` | `CLOSED` | Kedua pihak setuju (lihat §4) |
| Tolak penutup | `RESOLVED` | `IN_PROGRESS` | Catatan wajib; cap setuju direset |

Tidak ada: `REGISTERED`, `CANCELLED` (katalog WP), `PENDING`, `ESCALATED`, `CLARIFICATION`, `REJECTED` sebagai status tiket. Status terminal tipis **`WITHDRAWN`** (label UI: Dibatalkan) — bukan `CANCELLED`. `RESOLVED`/`CLOSED` tidak bisa dibatalkan.

**Kelengkapan berkas (v0.2):** label UI **Kembalikan ke cabang**, bukan Tolak. Permintaan kelengkapan memakai `completionRequestStatus=PENDING` (bukan status tiket baru). Riwayat: `RETURNED_FOR_COMPLETION`, `RESENT_TO_PUSAT`. Permintaan batal PENDING dihapus saat dikembalikan.

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

### Visibilitas `WITHDRAWN` (daftar + GET + lampiran)

Cabang pemilik selalu melihat tiketnya yang dibatalkan.

Pusat melihat `WITHDRAWN` **hanya jika Pusat sudah menangani**: pernah Terima, pernah Kembalikan ke cabang, atau Pusat yang menyetujui permintaan batal. Batal sepihak sebelum ada penanganan Pusat **tidak** tampil di daftar/GET Pusat (handling masih PUSAT tidak cukup). Admin (visibilitas ALL) tetap melihat semua. Filter di API, bukan di UI.

## 6. Dilarang di slice ini

Menyalin alur WP (Case, intake HQ, BQ-007). Izin `internal:*` penuh. Laporan/KPI sungguhan. `CANCELLED` katalog WP. Mode B / SSO. Katalog resolusi bisnis (selain sentinel `IC_DONE`). Notifikasi ke Pusat saat cabang batal sepihak sebelum Terima.

## 7. Snapshot PDF (v0.5)

`GET /api/v1/internal/complaints/{id}/export` (**API-550**). Salinan PDF **satu tiket** pada saat diunduh — analog API-539 Case WP, bukan dump Case, bukan laporan agregat.

- Tombol **Unduh PDF** di detail tiket. **Cabang dan Pusat** yang sudah boleh `GET` tiket itu boleh mengunduh (visibilitas `WITHDRAWN` sama dengan GET).
- Tidak mengubah status. Byte lampiran tidak tertanam (hanya daftar nama). Bukan dokumen untuk WP.
- Bukan laporan/KPI (tetap dilarang §6).

## Follow-up

- Binding UI Mode A: `frontend/src/features/internal-complaints/` + `frontend/messages/{id,en}.json`
- Kode penyelesaian tidak ditampilkan ke petugas; UI mengirim `IC_DONE`. Tiket lama `IC-OK` tetap valid.
- Domain/API: ACCEPT tanpa usulan PENDING ditolak; Terima/Tolak usulan hanya unit pemilik (v0.4)
- Lampiran Internal: CAP-011 `aggregateType=InternalComplaint` (bukan `cm_batch1_attachments`). Gambar + ZIP; ZIP tidak diekstrak.
