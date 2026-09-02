# Mode A Contract — Pengaduan Internal (Journey)

| Field | Value |
|---|---|
| ID | ECMP-MODEA-INT-001 |
| Version | 0.11 |
| Owner | Product Owner / Domain PO |
| Reviewer | Solution Architect |
| Approver | Business Owner (Mode A lab) |
| Status | 🟢 Accepted for Mode A UI (2026-08-17); v0.2 kelengkapan berkas; v0.3 visibilitas WITHDRAWN; v0.4 usulan dua pihak (2026-08-19); v0.5 snapshot PDF (2026-09-02); v0.6 handling kanonik PUSAT (2026-09-02); v0.7 klaim otomatis usulan (2026-09-02); v0.8 urutan riwayat klaim+usulan (2026-09-02); v0.9 tanpa tombol Ambil tiket (2026-09-02); v0.10 beku kerja saat minta batal + wewenang Pusat setara + Staff KaSatPel/KaSatPel tutup tiket sendiri (2026-09-02); v0.11 CRO Cabang/Pusat tidak menutup — wajib Staff KaSatPel/KaSatPel (2026-09-02) |
| Date | 2026-09-02 |
| Type | Mode A lab contract (non-ADR, non-DEC) |
| Related | DEC-025 §14.1 D (`/internal/*` bukan Dual-SoT WP); OpenAPI `internal-complaints.v1.yaml` |

**Bukan** ADR. **Bukan** unlock Mode B. **Tidak** mengubah BR-CM-CAT / Case Aggregate WP.

---

## 1. Identitas

- Satu tiket = satu aggregate. **Tidak ada Case child.**
- Nomor: `PI-{UNIT}-{YYMM}-{NNN}` (contoh `PI-TAB-2608-001`).
- **Unit pemilik** = unit pembuat, tidak pernah berubah.
- **Unit penanganan** mulai sama dengan unit pemilik; hanya berubah saat transfer Cabang ↔ Pusat. Tujuan Pusat selalu kode kanonik **`PUSAT`** — bukan sub-unit (`PUSAT-CRO` milik jadwal kedatangan WP, bukan pintu Pengaduan Internal).
- Tautan `relatedComplaintId` ke pengaduan WP bersifat opsional. Tutup Internal **tidak** menutup WP.
- API: `/api/v1/internal/complaints` (snapshot PDF: `.../{id}/export`, API-550). UI: `/internal/*` (flag `NEXT_PUBLIC_ECMP_INTERNAL_COMPLAINTS_UI`, default off).

## 2. Aktor (Mode A)

Wewenang dibedakan **unit keanggotaan** (cabang vs `PUSAT`), bukan nama role di Pusat. Kode IAM tetap DEC-027: CRO = `AGENT`, Staff KaSatPel = `SUPERVISOR`, KaSatPel = `MANAGER`.

| Peran | Yang boleh |
|---|---|
| CRO **login Cabang** | Buat; kirim ke Pusat (`PUSAT`); batal sepihak selama masih antrian; minta batal setelah usulan (`IN_PROGRESS`); ajukan pindah (tiket Pusat lokal); kirim ulang ke Pusat setelah dilengkapi. **Tidak menutup** — gerbang tutup wajib Staff KaSatPel/KaSatPel unit pemilik |
| Staff KaSatPel / KaSatPel **login Cabang** | Semua kerja CRO cabang + pindah Handling langsung; gerbang tutup unit pemilik **termasuk tiket buatannya sendiri** |
| CRO **login Pusat** | Kerja antrian Pusat setara Staff KaSatPel (kembalikan / usulkan / putuskan batal). **Tidak menutup** — gerbang tutup wajib Staff KaSatPel/KaSatPel |
| Staff KaSatPel / KaSatPel / Admin **login Pusat** | Kerja antrian Pusat **setara**: kembalikan ke cabang, usulkan penyelesaian, **putuskan permintaan batal**. Saat permintaan batal PENDING: kerja dibekukan — hanya **Setujui pembatalan** / **Tolak pembatalan**. Bukan tombol Kembalikan ke cabang atau Ajukan penyelesaian. Gerbang tutup unit penanganan: Staff KaSatPel/KaSatPel (boleh tiket sendiri); Admin tidak menutup tiket buatannya |
| Admin | Kerja antrian Pusat (sama di atas); putuskan pengajuan pindah lintas unit; gerbang tutup tanpa terikat unit; **tidak** menutup tiket buatannya sendiri |

CRO **Cabang dan Pusat** tidak merekam gerbang tutup (tiket sendiri maupun orang lain). `SUPERVISOR` di UPPPD ≠ `SUPERVISOR` di `PUSAT`.

## 3. Status dan transisi

`CREATED → ASSIGNED → IN_PROGRESS → RESOLVED → CLOSED`  
Cabang → Pusat, selama masih antrian: `ASSIGNED → WITHDRAWN` (batal sepihak).  
Setelah usulan (`IN_PROGRESS`) + permintaan PENDING; Setujui → `WITHDRAWN`; Tolak → tetap `IN_PROGRESS`.

| Langkah | Dari | Ke | Syarat |
|---|---|---|---|
| Buat (Pusat) | — | `CREATED` | Unit pemilik = unit penanganan = unit pembuat |
| Buat (Cabang) | — | `ASSIGNED` di Pusat | Semua peran cabang; Handling langsung Pusat; tanpa gerbang transfer-request |
| Pindah Handling | `CREATED` / `ASSIGNED` / `IN_PROGRESS` | `ASSIGNED` | Hanya Cabang ↔ Pusat; bukan `RESOLVED`/`CLOSED`/`WITHDRAWN` |
| Petugas Pusat ajukan pindah | `CREATED` (masih lokal Pusat) | tetap `CREATED` + permintaan PENDING | Alasan wajib; APPROVE = pindah ke cabang; REJECT = tetap lokal, boleh ajukan ulang |
| Klaim / mulai kerja | `CREATED` atau `ASSIGNED` | `IN_PROGRESS` | **Tidak ada tombol UI.** Terjadi otomatis saat **Usulkan penyelesaian**. `POST /receive` tetap di API (lab/tes), bukan langkah petugas. Diblokir saat `completionRequestStatus=PENDING` |
| Kembalikan ke cabang (berkas kurang) | `ASSIGNED` atau `IN_PROGRESS` | `ASSIGNED` di unit pemilik | Owner cabang, handling Pusat; aktor **login Pusat**; alasan wajib. **Tanpa klaim** — jangan menulis RECEIVED. **Diblokir** jika permintaan batal PENDING |
| Usulkan penyelesaian | `CREATED` / `ASSIGNED` / `IN_PROGRESS` | `IN_PROGRESS` | Hanya **unit penanganan**. Dari antrian (`CREATED`/`ASSIGNED`) **mengklaim otomatis** lalu usulan `PENDING_APPROVAL`. Mengganti usulan PENDING sebelumnya. Kode mesin `IC_DONE` tidak ditampilkan. **Diblokir** jika permintaan batal PENDING |
| Cabang kirim ulang ke Pusat | `ASSIGNED` + PENDING kelengkapan | `ASSIGNED` di Pusat | Aktor di unit pemilik; **catatan wajib**; lampiran boleh ditambah dulu. **Login Pusat:** kembalikan lagi atau usulkan |
| Cabang batal sepihak | `ASSIGNED` (handling Pusat, belum usulan) **atau** menunggu kelengkapan | `WITHDRAWN` | Pembuat atau Staff KaSatPel/KaSatPel unit pemilik; alasan wajib; **tanpa notifikasi ke Pusat**; tiket hilang dari antrian masuk |
| Cabang minta batal | `IN_PROGRESS` (owner cabang, handling Pusat) | tetap `IN_PROGRESS` + PENDING | Alasan wajib; satu PENDING; **kerja di Pusat dibekukan** sampai keputusan |
| Pusat setujui batal | `IN_PROGRESS` + PENDING | `WITHDRAWN` | Semua login Pusat (CRO / Staff KaSatPel / KaSatPel / Admin) di unit penanganan |
| Pusat tolak batal | `IN_PROGRESS` + PENDING | `IN_PROGRESS` | Alasan wajib; kerja Pusat dibuka lagi; cabang boleh minta lagi |
| Terima usulan | `IN_PROGRESS` | `RESOLVED` | Hanya **unit pemilik**; wajib ada usulan `PENDING_APPROVAL`; pengusul **tidak** boleh menerima sendiri. Tidak ada pintasan ACCEPT tanpa usulan. Cap otomatis unit penanganan memakai pengusul; kode mesin `IC_DONE` bila klien tidak mengirim kode |
| Tolak usulan | `IN_PROGRESS` | `IN_PROGRESS` | Hanya **unit pemilik**; alasan wajib; pengusul tidak boleh menolak sendiri |
| Setuju penutup | `RESOLVED` | `CLOSED` | Kedua pihak setuju (lihat §4) |
| Tolak penutup | `RESOLVED` | `IN_PROGRESS` | Catatan wajib; cap setuju direset |

Tidak ada: `REGISTERED`, `CANCELLED` (katalog WP), `PENDING`, `ESCALATED`, `CLARIFICATION`, `REJECTED` sebagai status tiket. Status terminal tipis **`WITHDRAWN`** (label UI: Dibatalkan) — bukan `CANCELLED`. `RESOLVED`/`CLOSED` tidak bisa dibatalkan.

**Kelengkapan berkas (v0.2):** label UI **Kembalikan ke cabang**, bukan Tolak. Permintaan kelengkapan memakai `completionRequestStatus=PENDING` (bukan status tiket baru). Riwayat: `RETURNED_FOR_COMPLETION`, `RESENT_TO_PUSAT`. **Tidak** menghapus permintaan batal PENDING — kembalikan/usulkan ditolak selama PENDING (v0.10).

## 4. Gerbang tutup (UI)

Jangan tampilkan `OWNER` / `HANDLING_UNIT` ke petugas.

**Jika sudah dipindah (unit pemilik ≠ unit penanganan):**  
“Unit penanganan menyelesaikan. Unit pemilik harus menyetujui sebelum ditutup.”  
Tombol (hanya Staff KaSatPel/KaSatPel/Admin, **bukan CRO**): **Setujui sebagai unit penanganan** · **Setujui sebagai unit pemilik** · **Kembalikan ke pengerjaan**. CRO yang membuat tiket melihat hint untuk minta Staff KaSatPel/KaSatPel.

**Jika tidak dipindah (masih di unit pembuat):**  
Cap unit penanganan sudah otomatis saat penyelesaian diterima. Sisa gerbang: Staff KaSatPel/KaSatPel unit pemilik, **termasuk pembuat tiket**. CRO tidak menutup gerbang ini. Admin tidak menutup tiket buatannya sendiri.  
“CRO menyelesaikan. Staff KaSatPel unit pemilik harus menyetujui sebelum ditutup.”  
Tombol: **Setujui penyelesaian** · **Kembalikan ke pengerjaan**.

Setelah syarat terpenuhi, status menjadi **Ditutup** otomatis. Endpoint close tidak boleh menembus gerbang ini.

## 5. Antrian UI

Assignments / Follow-up / Verification / Reports adalah **filter daftar tiket Internal**, bukan workspace Case WP. Copy halaman memakai bahasa Pengaduan Internal.

### Visibilitas `WITHDRAWN` (daftar + GET + lampiran)

Cabang pemilik selalu melihat tiketnya yang dibatalkan.

Pusat melihat `WITHDRAWN` **hanya jika Pusat sudah menangani**: pernah usulan (klaim otomatis), pernah `POST /receive` lab, pernah Kembalikan ke cabang, atau Pusat yang menyetujui permintaan batal. Batal sepihak sebelum ada penanganan Pusat **tidak** tampil di daftar/GET Pusat (handling masih PUSAT tidak cukup). Admin (visibilitas ALL) tetap melihat semua. Filter di API, bukan di UI.

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
- v0.6: tujuan handling Pusat selalu `PUSAT` (bukan `PUSAT-CRO`). **Login Pusat** (termasuk Admin lab tanpa cabang) boleh Terima antrian Pusat. Jadwal kedatangan WP tetap CRO.
- v0.7: **Ambil tiket** opsional (kunci batal sepihak). **Kembalikan ke cabang** dan **Usulkan penyelesaian** dari antrian tanpa klik Ambil tiket; usulan mengklaim otomatis.
- v0.8: usulan dari antrian menulis riwayat **RECEIVED → RESOLUTION** (tanpa REVIEW di tengah); `occurred_at` monotonik. UI detail tetap terbaru di atas.
- v0.9: UI **tanpa Ambil tiket**. **Login Pusat/Admin** di antrian: **Kembalikan ke cabang** (tanpa klaim) atau **Usulkan** (klaim otomatis). **Login Cabang** batal sepihak selama belum usulan. `POST /receive` lab-only. Bukan WP.
- v0.10: permintaan batal PENDING **membekukan** kerja Pusat (kembalikan / usulkan / pindah). Semua **login Pusat** (CRO / Staff KaSatPel / KaSatPel / Admin) memutus Setujui/Tolak. Staff KaSatPel/KaSatPel boleh menutup tiket buatannya di unit sendiri. Bukan WP.
- v0.11: **CRO Cabang dan CRO Pusat** tidak menutup pengaduan (termasuk yang mereka buat) — wajib persetujuan Staff KaSatPel atau KaSatPel. Kerja antrian Pusat tetap setara. Bukan WP.
