# Decision Record — CM sebagai Target Single Complaint SoT + Closure Mode A

| Field | Value |
|---|---|
| ID | DEC-025 |
| Version | 1.0 |
| Owner | Business Owner / Solution Architect |
| Reviewer | Architecture Board / Domain PO ECMF |
| Approver | Architecture Board + Business Owner |
| Status | 🟢 **Accepted** (Mode A — BO/Board session 2026-08-13) |
| Date | 2026-08-13 |
| Last Review | 2026-08-13 |
| Next Review | 2027-02-13 |
| Related | DEC-020 (Accepted, tetap binding sampai Retirement follow-up); BR-009; BQ-007; BQ-014; FRD-CM-001; FRD-CM-B2-001; CAP-008 CLOSED; DEC-MODEA-B2-001 |
| Type | Project Decision (non-ADR) — target SoT + aturan Closure/Status Aggregate Mode A |

- Decision Status: **Accepted**
- DEC-020 **tetap Accepted** — tidak retired / tidak superseded
- Tidak unlock Mode B, CAP-006, DEC-F4, atau reopen CAP-008
- Tidak mengotorisasi cutover / hapus `/api/v1/complaints` / merge tabel
- Implementasi kontrak/sync/FE = **M-025-1** (terpisah; belum dijalankan oleh Accept ini)

---

## 1. Context

DEC-020 (Accepted, 2026-07-30) mengunci **Dual SoT under controlled coexistence**:

| Concern | Canonical sekarang |
|---|---|
| Batch-1 intake (FR-001…004) | `/api/v1/cm` · `cm_batch1_*` |
| Foundation lifecycle (assign / escalate / resolve / close / search) | `/api/v1/complaints` · `complaints` |
| Case operasional CAP-008 | `/api/v1/cm/cases` · `cm_cases` (parent = `cm_batch1_complaints`) |

Cutover / retirement Foundation **hanya** via Retirement DEC terpisah. Alternatif wholesale remapping **ditolak** di DEC-020.

**Masalah operasional (Observed, bukan opini):**

1. UI create/list utama sudah CM (`/complaints`, `/complaints/new`); handling masih Foundation (`/complaints/[id]`, `/queue`, `/assignments`, `/resolutions`).
2. Search API-388 = Foundation only — intake Aggregate tidak masuk `/queue`.
3. Dashboard punya dua sumber KPI (`/dashboard/summary` vs `/dashboard/aggregate-kpis`); FE `complaintKpiSource`.
4. Tiga ruang identitas tanpa sync: `CMP-…` · `UNIT-YYMM-NNNN` · `CASE-YYYY-NNNNNN` (+ CA BC `complaint_cases*` terpisah).
5. Kata assign / escalate / close punya makna berbeda per stack.

Business Owner menyatakan Dual-SoT **membingungkan** dan menginginkan **satu arah**: CM menjadi target Single Complaint SoT, tanpa cutover prematur.

Niat Closure/Status induk (diskusi BO 2026-08-13) juga perlu dikunci agar tidak bertentangan diam-diam dengan CAP-008 AC-16 dan kontrak Batch-1.

---

## 2. Options

| Opsi | Isi | Disposisi |
|---|---|---|
| A | Pertahankan Dual-SoT sebagai tujuan jangka panjang | Ditolak BO — membingungkan petugas/developer |
| B | CM = **target** Single SoT; Dual-SoT **sementara** sampai prasyarat + Retirement follow-up Accepted | **Selected — Accepted 2026-08-13** |
| C | Cutover / retire Foundation sekarang | Ditolak — gap capability + konflik semantic belum selesai |

---

## 3. Decision (Accepted 2026-08-13 — kebijakan mengikat; implementasi ≠ Accept)

### 3.1 Arah SoT

1. **Target architecture:** satu domain Complaint, satu canonical SoT = **CM Aggregate** (`/api/v1/cm`) dengan Case sebagai unit kerja di bawahnya.
2. **Keadaan namespace (sampai Retirement follow-up Accepted):** DEC-020 **tetap Accepted dan binding**. Dual-SoT bukan dihapus oleh Accept DEC-025.
3. **Sejak Accept DEC-025:** Foundation `/api/v1/complaints` diperlakukan sebagai **legacy** (bukan competing SoT jangka panjang), tetap hidup sampai Retirement DEC follow-up Accepted.
4. Capability Complaint **baru** tidak boleh ditambahkan ke Foundation; defect-driven maintenance saja (selaras BMR EPIC-ECMF-LEGACY).
5. Cutover / hapus path / merge tabel **bukan** wewenang DEC-025. Itu Retirement DEC terpisah setelah prasyarat §8.

```text
ACCEPTED TARGET (cutover Foundation = follow-up DEC, belum)

Complaint (Aggregate Root)
        │
        ▼
CM Aggregate  (/api/v1/cm)     ← target Single SoT
        ├── Complaint-level (identity, intake, confirmation, status induk, closure induk)
        └── Case(s)            ← assignment, SLA bind, operational resolve, Case close
```

### 3.2 Model domain (tidak di-redesign)

- **Complaint** = Aggregate Root (nomor induk).
- **Case** = unit kerja operasional di bawah Complaint.
- Jangan menyamakan Case dengan Complaint.
- Close Case ≠ Close Complaint (BQ-007) — lihat §3.4 untuk evaluasi BR-009 terpisah.
- CAP-008 tetap **Program CLOSED**. DEC ini tidak reopen Create/Status/Resolve/Close Case sebagai program baru.

### 3.3 Status nomor induk (Complaint Aggregate)

```text
REGISTERED     →  belum ada Case
     ↓ Case pertama terbentuk
IN_PROGRESS    →  ada kerja Case
     ↓ tidak ada Case yang masih dikerjakan, dan ada Case CLOSED yang relevan
CLOSED         →  auto-close (BR-009 Mode A)
```

Binding:

- Setelah **Case pertama** terbentuk, induk **HARUS** `IN_PROGRESS`.
- `RESOLVED` pada Case **tidak** mengubah induk menjadi `CLOSED`.
- Kontrak Batch-1 yang hanya `REGISTERED | CLOSED` adalah **gap** (§7) — harus diselaraskan di milestone implementasi **setelah** Accept, bukan diam-diam sekarang.

### 3.4 Closure induk (BR-009 Mode A) — tidak meniadakan BQ-007

**BQ-007 tetap:** aksi Close **satu** Case hanya menutup Case itu. Tidak diartikan “tutup pengaduan”.

**BR-009 Mode A (Accepted):**

Induk **auto-close** (`CLOSED`) hanya jika **semua** syarat terpenuhi:

1. Tidak ada Case yang masih dikerjakan: status **bukan** `CREATED` / `ASSIGNED` / `IN_PROGRESS` / `RESOLVED`.
2. Ada penyelesaian kerja berupa Case `CLOSED` yang relevan (Case yang menutup sisa kerja = `CLOSED`).
3. Evaluasi ini adalah **Closure Aggregate (BR-009)**, bukan perluasan makna tombol Close Case.

**Case `CANCELLED`:**

- Tidak menutup induk.
- **Tidak menghalangi** auto-close (diabaikan dalam hitungan “selesai”).
- Tidak diedit / tidak di-un-cancel.

**Semua Case `CANCELLED` (tidak ada yang `CLOSED`):**

- Induk **tetap buka** (bukan auto-close).
- Alur “Tutup Pengaduan” / pengaduan batal = **out of scope** DEC ini (follow-up).

### 3.5 Cancel Case (BQ-014 — tidak diubah)

Tiga alasan tetap:

1. Duplicate
2. Wrong Input
3. Customer Cancellation

Lapisan Duplicate:

| Lapisan | Yang benar |
|---|---|
| Duplicate **pengaduan** (intake) | Tautkan (`link_existing` / FR-003 / API-506) — bukan Cancel |
| Duplicate **Case** (sudah terlanjur terbentuk) | Cancel Case alasan Duplicate |

Kesalahan murni:

- Status Case = **`CANCELLED`**, bukan `CLOSED`.
- Bukan Case baru, kecuali kerja pengganti memang masih perlu.
- Kerja pengganti = **Case baru** di nomor induk yang sama.

### 3.6 Pengurangan bingung petugas (ops policy)

Setelah Accept, kebijakan operasional Mode A (bukan retire API):

| Pintu | Peran |
|---|---|
| `/complaints`, `/complaints/new`, `/complaints/cm/[id]` | Utama — Complaint CM |
| `/complaints/cm/cases` | Utama — kerja Case |
| `/queue`, `/assignments`, `/resolutions`, `/complaints/[id]` Foundation | **Legacy** — bukan menu utama |
| KPI resmi lab/ops | Aggregate (`/dashboard/aggregate-kpis`) |
| API-201 `POST /api/v1/complaints` | Jangan dihapus oleh DEC ini |

Ini **consumer alignment** (DEC-020 Phase 1), bukan authorization menghapus Foundation.

---

## 4. Explicit non-goals (binding)

DEC-025 **tidak** mengotorisasi:

- Mengubah status DEC-020 menjadi retired / superseded (kecuali Board kelak memutuskan follow-up Retirement yang eksplisit)
- Hapus `/api/v1/complaints` atau tabel `complaints`
- Merge `complaints` + `cm_batch1_*` + `cm_cases`
- Reopen CAP-008
- Implementasi CAP-006 SLA engine (`CAP006-BLK-001` tetap)
- Implementasi DEC-F4 / FRD-CM-002 escalate-to-Pusat
- Mode B / SSO / Identity Adapter / enterprise `securitySchemes`
- Mount penuh `complaint_foundation_router` (CA BC)
- Menyamakan Sprint `/v1/cases` (`implementation/`) dengan CAP-008
- Silent cutover UI Foundation → Aggregate

---

## 5. Relationship ke DEC-020

| Item | Aturan |
|---|---|
| DEC-020 | Tetap **Accepted** dan binding untuk namespace sampai Retirement follow-up Accepted |
| DEC-025 Accept | Mengunci **target** Single SoT + aturan Closure/Status; **bukan** tanggal retirement Foundation |
| Retirement follow-up | DEC baru (belum dibuka) — prasyarat §8 wajib terpenuhi |
| CA BC `complaint_cases*` | Tetap ticket-nested only (DEC-020) — bukan CM Case |

DEC-025 **tidak** mengulang Alternatif A DEC-020 (wholesale remapping pada tanggal tetap). Ini menetapkan *arah* + aturan produk Mode A, dengan cutover tetap Board-gated.

---

## 6. Relationship ke BQ-007 / AC-16 / BR-009

| Artefak | Isi sekarang | Hubungan setelah Accept |
|---|---|---|
| BQ-007 | Close Case ≠ auto Close Complaint | **Tetap.** Close Case tidak *berarti* tutup induk |
| FRD-CM-B2-001 AC-16 | Close Case terakhir → induk **tetap terbuka** | **Konflik.** Niat BO: setelah tidak ada Case dikerjakan dan ada `CLOSED` relevan → evaluasi BR-009 auto-close induk |
| CAP-008 FR-006 | Complaint Closure BR-009 **OUT OF SCOPE** default | **Aktivasi sempit BR-009 Mode A** (auto-close), tanpa reopen program CAP-008 |
| BR-009 | Closure Aggregate; opsi system auto-close jika policy mengizinkan | **Sumber aturan** untuk §3.4 |
| BR catalog baris 222 | Close Case MUST NOT auto-close kecuali keputusan BR-009 terpisah | DEC-025 **adalah** keputusan BR-009 terpisah itu |

AC-16 Mode A di-**narrow**: Close Case terakhir *memicu evaluasi* BR-009; yang menutup induk adalah aturan §3.4, bukan semantik tombol Close Case. CAP-008 program tetap CLOSED; perubahan kontrak/tes = **M-025-1**.

---

## 7. Konflik Observed vs implementasi saat ini

**Jangan disembunyikan.** Selaraskan di **M-025-1** (bukan cutover Foundation).

| # | Observed | Evidence | Niat BO (§3) |
|---|---|---|---|
| K1 | Case menulis parent `IN_PROGRESS` saat Case pertama | `backend/app/modules/cm_case/infrastructure/repository.py` `mark_complaint_in_progress` | Selaras §3.3 |
| K2 | Kontrak Batch-1 hanya `REGISTERED \| CLOSED` | `cm_batch1/schemas.py` `ComplaintBatch1Response.status` | **Tidak selaras** — gap kontrak |
| K3 | `caseCreated: Literal[False]` di skema; Case set `case_created=True` | `schemas.py` vs `repository.py` | Gap kontrak |
| K4 | Sync menganggap terminal = `CLOSED` **dan** `CANCELLED`, lalu parent `CLOSED` | `sync_complaint_status_from_cases` `terminal = ("CLOSED", "CANCELLED")` | **Tidak selaras** §3.4 — `CANCELLED` harus diabaikan; semua-CANCELLED → induk tetap buka |
| K5 | CAP-008 AC-16: last Case close → induk tetap terbuka | FRD-CM-B2-001 §AC-16 | **Tidak selaras** §3.4 |
| K6 | Tidak ada sync Foundation ↔ CM ↔ CA BC | DEC-020; tidak ada FK `cm_cases` → `complaints` | Tetap sampai Retirement follow-up |

---

## 8. Prerequisites sebelum Retirement / cutover Foundation

DEC-025 Accept **tidak** memenuhi ini. Wajib sebelum Retirement DEC follow-up:

1. Kontrak Aggregate mengakui `REGISTERED | IN_PROGRESS | CLOSED` + `caseCreated` sesuai kenyataan Case.
2. Sync parent sesuai §3.4 (bukan K4).
3. Narrow AC-16 / BR-009 tercatat di FRD/tes yang relevan (tanpa reopen fitur CAP-008).
4. Konsumen Foundation (FE queue/assign/resolve/search + API-201) teridentifikasi; zero-consumer atau dual-read eksplisit.
5. KPI/search resmi satu SoT untuk petugas (ops policy §3.6 sudah jalan).
6. Strategi data historis `complaints` / `CMP-…` (bukan asumsi).
7. CA BC mount-or-retire diputuskan **eksplisit** (DEC terpisah).
8. OpenAPI + RTM + tes coexistence diubah **setelah** Retirement DEC, bukan sekarang.
9. CAP-006 / DEC-F4 tetap tidak diangkat sebagai syarat palsu “CM belum lengkap”.

---

## 9. Consequences / Risks

### Positive (setelah Accept)

- Satu arah untuk petugas dan implementasi baru: CM.
- Dual-SoT tidak lagi dibaca sebagai “dua SoT setara selamanya”.
- Aturan close/status induk tertulis; konflik AC-16 vs kode menjadi keputusan Board, bukan drift.

### Risks

- Accept tanpa disiplin follow-up → tim mengira Foundation sudah boleh dihapus.
- Menjalankan M-025-1 tanpa disiplin tes = kontrak/sync bisa menyimpang dari §3.4.
- Auto-close salah hitung `CANCELLED` (perilaku lab sekarang) menutup induk yang BO ingin tetap buka.
- Menyembunyikan menu Foundation terlalu awal memotong petugas yang masih butuh assign/SLA/escalate Foundation.

### Risks if Reject / remain Dual-SoT as goal

- Kebingungan list vs queue vs dua KPI berlanjut.
- Fitur baru rawan masuk Foundation “karena belum ada di CM”.

---

## 10. Acceptance Criteria (vote Board)

Board **Accept** DEC-025 hanya jika mengonfirmasi **semua**:

1. Target Single SoT = CM Aggregate + Case; Dual-SoT DEC-020 tetap berlaku sampai Retirement follow-up.
2. Foundation = legacy setelah Accept; bukan dihapus oleh Accept ini.
3. Status induk: `REGISTERED` → `IN_PROGRESS` (Case pertama) → `CLOSED` (BR-009 §3.4).
4. BQ-007 tetap; auto-close induk = evaluasi BR-009 Mode A, bukan “Close Case = Close Complaint”.
5. `CANCELLED` tidak menutup induk dan tidak menghalangi auto-close; semua-CANCELLED → induk tetap buka.
6. BQ-014 tiga alasan Cancel **tidak** diubah.
7. Non-goals §4 mengikat.
8. Implementasi kontrak/sync/FE nav = **milestone terpisah setelah Accept**, bukan bagian Accept itu sendiri.
9. Mode B, CAP-006, DEC-F4, reopen CAP-008 **tidak** di-unlock.

**Reject** berarti: DEC-020 Dual-SoT sebagai kebijakan penuh tetap; niat BO tidak mengikat implementasi; kode sync parent tidak boleh dianggap SoT.

### Sign-off record

| Role | Disposition | Date |
|---|---|---|
| Business Owner / Architecture Board (session) | **Accept** — kriteria §10.1–10.9 | 2026-08-13 |
| Record | Working session ECMP — perintah `Board Accept` | 2026-08-13 |

Accept mengunci **kebijakan** §3. Tidak menjalankan M-025-1, tidak mengubah OpenAPI/kode/test, tidak membuka Retirement DEC.

---

## 11. Follow-up yang **tidak** dijalankan oleh Accept DEC-025

**Satu** milestone berikutnya (diotorisasi sebagai *pekerjaan setelah Accept*, belum dieksekusi):

> **M-025-1 (setelah Accept):** Selaraskan kontrak + sync Aggregate  
> — OpenAPI/skema Batch-1: status `IN_PROGRESS`; `caseCreated` boolean nyata  
> — `sync_complaint_status_from_cases` sesuai §3.4 (`CANCELLED` diabaikan; semua-CANCELLED → induk buka)  
> — Tes yang mengunci perilaku baru  
> — **Bukan** retire Foundation, **bukan** ubah menu FE sebagai cutover, **bukan** merge tabel

Milestone UI “satu pintu / Foundation legacy di nav” = slice terpisah (consumer alignment), hanya setelah Accept + tidak menghapus rute Foundation.

**M-025-1 execution (2026-08-13):** kontrak Aggregate `REGISTERED|IN_PROGRESS|CLOSED`, `caseCreated` boolean nyata, sync parent §3.4, filter list `OPEN`, KPI open = bukan `CLOSED`. Foundation tidak di-retire.

**M-025-2 execution (2026-08-13):** consumer alignment §3.6 — Case inbox di sidebar utama (`/complaints/cm/cases`); `/queue` `/assignments` `/resolutions` `/complaints/[id]` tetap rute + banner legacy; DualSotNotice ke `/complaints`. Bukan retire API/rute.

**M-025-3 execution (2026-08-13):** CTA Aggregate/CM tidak lagi mengantar petugas ke Foundation `/queue` (dashboard kosong → daftar CM; antrean supervisor Batch-1 → `/complaints`; detail Foundation tidak lagi “kembali ke antrean”). Rute `/queue` tetap. Bukan retire API.

**M-025-4 execution (2026-08-13):** overlay FRD Mode A (§13) tanpa unlock FRD LOCKED; inventaris konsumen Foundation (§14); salinan DualSotNotice = target CM / Foundation legacy. Bukan retire API, bukan reopen CAP-008.

**M-025-5 execution (2026-08-13):** Tindak lanjut membuka CM Case / Aggregate detail; pintu API-513 supervisor queue di daftar Aggregate (bukan daftar Foundation). Rute `/complaints/cm/supervisor` tetap — M3b tidak di-retire. Bukan retire Foundation.

---

## 12. Impact (setelah Accepted)

| Artefak | Dampak |
|---|---|
| DEC-020 | Tetap Accepted; dibaca bersama DEC-025 (target vs keadaan namespace) |
| FRD-CM-001 | **LOCKED tetap.** Overlay §13: create tetap `REGISTERED`; `IN_PROGRESS` setelah Case pertama |
| FRD-CM-B2-001 AC-16 | **LOCKED tetap.** Overlay §13: BQ-007 tetap; BR-009 Mode A per §3.4 |
| OpenAPI `complaint-management-batch1.v1.yaml` | Enum status — M-025-1 |
| OWNERSHIP_MATRIX | Tetap dual-namespace sampai Retirement follow-up |
| CAP-008 | Tetap CLOSED |

Accept **tidak** mengubah OpenAPI/kode/test. Itu M-025-1, hanya jika diminta terpisah.

---

## 13. Overlay FRD Mode A (M-025-4) — **bukan** unlock dokumen LOCKED

FRD-CM-001, FRD-CM-B2-001, BR-CM-CAT-001, dan CAP-008 BCS **tetap LOCKED**. Overlay ini **mencatat** niat Board DEC-025 agar §8.3 terpenuhi tanpa merevisi tubuh FRD (itu butuh revision plan terpisah).

| Klaim LOCKED (tetap benar) | Overlay Mode A (DEC-025) |
|---|---|
| FR-001 create → status awal `REGISTERED` | Tidak berubah |
| First Case → parent `IN_PROGRESS` (FRD-B2 AC-02 / BR-004) | Kontrak Aggregate **mengakui** `REGISTERED \| IN_PROGRESS \| CLOSED` + `caseCreated` nyata (sudah M-025-1) |
| AC-16 / BQ-007: Close Case ≠ Close Complaint | **Tetap.** Tombol Close Case tidak *berarti* tutup induk |
| AC-16 huruf: last open Case close → induk tetap terbuka | **Narrow:** last working Case close *memicu evaluasi* BR-009; induk `CLOSED` hanya jika §3.4 terpenuhi (`CANCELLED` diabaikan; semua-CANCELLED → induk tetap buka) |
| CAP-008 FR-006 Complaint Closure default OUT OF SCOPE | Aktivasi **sempit** BR-009 Mode A (auto-close). Program CAP-008 **tetap CLOSED** — bukan reopen fitur |

Jika teks AC-16 di FRD-B2 dibaca tanpa overlay ini, itu **konflik Observed (K5)** — yang mengikat untuk runtime Mode A adalah §3.4 + tes M-025-1, bukan huruf AC-16 pra-DEC-025.

---

## 14. Inventaris konsumen Foundation (M-025-4 / §8.4)

Dual-read **eksplisit**. Bukan zero-consumer. Bukan izin hapus.

| Konsumen | Pintu / API | Peran setelah M-025-2…4 |
|---|---|---|
| Header search | `/complaints?keyword=` → `/api/v1/cm` | **Resmi** — CM |
| Daftar `/complaints` | `/api/v1/cm` | **Resmi** — CM |
| Case inbox | `/complaints/cm/cases` → `/api/v1/cm/cases` | **Resmi** — Case |
| KPI dasbor (lab/ops) | `/dashboard/aggregate-kpis` | **Resmi** — Aggregate |
| `/queue` list | API-388 `GET /api/v1/complaints/search` | **Legacy** dual-read + banner |
| `/assignments` | API-388 | **Legacy** dual-read + banner |
| `/resolutions` | API-388 | **Legacy** dual-read + banner |
| `/complaints/[id]` Foundation | API-201 GET + lifecycle | **Legacy** + banner |
| API-201 `POST /api/v1/complaints` | Foundation create | **Tetap hidup** — jangan dihapus DEC-025 |
| Shell B0 `/queue/*` | mock WF-001 | Di luar Mode A CM — jangan di-retarget |
| `/internal/*` | prototype flag | Bukan Dual-SoT WP — jangan dicampur |

Search petugas resmi = Header → daftar CM. API-388 tetap untuk permukaan Foundation.

---

## Links

- DEC-020: `DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md`
- BR-009 / BQ-007 / BQ-014: `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md`
- FRD-CM-B2-001 AC-16: `03 Functional Requirements/ECMP_FRD_Case_Management_Batch2_v1.0.md`
- CAP-008 close: `18 Architecture Governance/ECMP_PROGRAM_CAP008_010_Final_Closure_Decision_v1.0.md`
- Sync parent: `backend/app/modules/cm_case/infrastructure/repository.py`
- Kontrak Batch-1: `backend/app/modules/cm_batch1/schemas.py`
- Collision ID: `deploy/evidence/DEC_ID_Collision_Register_20260801.md` (DEC-025 **tidak** memakai ulang 020/021)

---

*End of DEC-025 v1.0 Accepted.*
