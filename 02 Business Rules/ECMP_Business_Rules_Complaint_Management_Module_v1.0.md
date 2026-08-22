# ECMP Business Rules — Complaint Management Module

| Field | Value |
|---|---|
| ID | BR-CM-CAT-001 |
| Version | 1.3.1 |
| Owner | Business Analyst / Domain PO ECMF |
| Reviewer | Solution Architect, Operations Lead, Compliance |
| Approver | Business Owner / Architecture Board |
| Status | 🟢 Locked |
| Last Review | 2026-08-05 |
| Next Review | 2026-10-29 |
| Related DEC | [DEC-F4](../18%20Architecture%20Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md) (**detail Reserved** for Mode A force until Board countersign / DL-012 — see BR-007 note; path Branch↔HO remains binding); [DEC-BQ001](../18%20Architecture%20Governance/reviews/ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md) (Case Aggregate SoT / Option O3 APPROVED); [DEC-MODEA-B2-001](../18%20Architecture%20Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md) (Mode A Delivery Baseline BQ lock — CAP-008); [DEC-028](../27%20Project%20Decisions/DEC-028_Case_Number_Unit_Month_and_HQ_Destination_v0.1.md) (BQ-004 format + HQ destination) |
| Related Governance Baseline | `docs/governance/BC-000-Business-Constitution.md`; `docs/governance/BC-001-Business-Principles.md`; `docs/governance/BC-002-Business-Rules.md`; `docs/governance/BC-003-Business-Glossary.md`; `docs/business/BW-000-Business-Workflow-Constitution.md` |
| Precedence | If this catalog conflicts with the approved Mode A governance baseline (BC-000…BC-003, BW-000), **the baseline prevails**. This document remains the Complaint Aggregate domain catalog under dual-SoT (DEC-BQ001 O3 / DEC-020). |

## Mode A Delivery Baseline (Batch-2) — Policy Notes

> Binding Product Owner decisions for **CAP-008** / Batch-2 Mode A. **Case Aggregate Transition Matrix above remains SoT and is not rewritten by these notes.** Full record: DEC-MODEA-B2-001.

| BQ | Mode A policy (LOCKED) |
|---|---|
| BQ-002 | Complaint MAY register without Case; MUST have ≥1 Case within **1 working day** after `REGISTERED` (BC-5.4 timing threshold; **not** activation of Working Day SLA calendar); Supervisor Queue MUST show exceedances |
| BQ-003 | Default max Cases per Complaint = **5**; future override outside Mode A |
| BQ-004 | Case Number independent of Complaint Number; format **`UNIT-YYMM-NNNN`** (complaint **`CM{UNIT}-YYMM-NNNN`**) — DEC-028 |
| BQ-005 | Case SHALL bind SLA Policy Version; SLA countdown **NOT** activated in Mode A |
| BQ-006 | Assignment at **Unit level only**; Assigned User outside Mode A |
| BQ-007 | Close Case ≠ auto Close Complaint |
| BQ-008 | Mode A flow: `IN_PROGRESS` → `RESOLVED` → Supervisor Approval → `CLOSED` |
| BQ-009 | `PENDING` / `ESCALATED` remain in Aggregate matrix; Mode A Delivery **does not expose** them |
| BQ-010 | Resolve requires Comment; Attachment optional; Complaint Attachment may be reused |
| BQ-011 | D-02 retained (no Case-at-intake); timing after REGISTERED = BQ-002 |
| BQ-012 | Capability ID **CAP-008** (not CAP-002) |
| BQ-014 | `CANCELLED` included in Mode A; reasons include Duplicate, Wrong Input, Customer Cancellation |

## Dokumen Ini

Dokumen ini menetapkan **Business Rules Enterprise** untuk **Complaint Management Module** pada Enterprise Complaint Management Platform (ECMP), dengan model domain yang dikunci sebagai berikut:

1. **Complaint** adalah Aggregate Root.
2. Satu Complaint dapat memiliki satu atau lebih **Case**.
3. **Case** adalah unit kerja operasional.
4. **Assignment** berada pada level Case.
5. **SLA** berada pada level Case. Mode A: Case **SHALL bind** SLA Policy Version; countdown **NOT** activated (BQ-005 / BC-9.10). Baseline kalender Mode A = **24×7** (BC-6.5 / BR-SLA-003). **Working Day** calendars, pause/resume, and case-type differentiation remain **Deferred** (BR-SLA-004) — not Mode A force.
6. Complaint hanya menyimpan **CustomerId**; data pelanggan bersumber dari Master Customer eksternal.
7. Prinsip eskalasi: **NO INFORMATION LOST DURING ESCALATION**.

### Batas Lingkup

| Termasuk | Tidak Termasuk |
|---|---|
| Lifecycle Complaint & Case | ERP |
| Assignment, SLA, Eskalasi, Resolusi, Closure, Reopen | CRM sebagai SoR pelanggan |
| Customer 360 View (read-enriched) | Enterprise Platform Identity/SSO |
| Communication, Attachment, Comment, Timeline, History | User Directory ownership |
| Duplicate detection, Audit Trail, KPI, Reporting | Notification Platform ownership |
| | Calendar Platform ownership |
| | Audit Platform ownership (ECMP mencatat jejak bisnis; platform audit eksternal boleh menerima salinan) |

### Dependency Eksternal (bukan milik modul ini)

Identity · Authentication · Organization · User Directory · Notification Platform · Calendar Platform · Audit Platform · Master Customer

### Hubungan dengan Katalog BR Lain

| Katalog | Peran |
|---|---|
| `ECMP_Business_Rules_Sprint01_v0.1.md` (BR-DOC-001) | SoT delivery implementasi slice Sprint-01 (case-centric) per DEC-003 |
| `ECMP_Business_Rules_v1.0.md` (BR-CAT-001) | Katalog kebijakan enterprise lintas domain |
| **Dokumen ini (BR-CM-CAT-001)** | Katalog Business Rules modul Complaint dengan model **Complaint → Case**; menunggu DEC formal sebelum menggantikan SoT implementasi |

> Hingga DEC remapping disetujui Business Owner, implementasi aktif tetap merujuk delivery SoT. Dokumen ini adalah spesifikasi bisnis target untuk model Aggregate Complaint.

### Prinsip Arsitektur Bisnis

Single Source of Truth · No Duplicate Work · Full Traceability · Auditability · Configurable · Scalable · Maintainable

### Aktor Bisnis (referensi lintas rule)

> **Persona alignment (BC-8 / BG-018):** Operational closed set = **Complaint Officer**, **Supervisor**, **Manager**. Legacy labels Agent / Petugas Frontline / Case Handler map to **Complaint Officer** (situational modes: intake | active handling). **Manager** remains a valid business persona; Manager Workspace/Dashboard **MAY** remain deferred (DL-068).

| Aktor | Peran Ringkas |
|---|---|
| Complaint Officer *(legacy: Agent / Petugas Frontline — intake mode)* | Menerima keluhan, membuat Complaint, mencari pelanggan, mencatat komunikasi |
| Complaint Officer *(legacy: Case Handler — active handling mode)* | Menangani Case yang di-assign, menambah catatan, attachment, usulan resolusi |
| Supervisor Unit | Assignment, reassignment, review, eskalasi unit, approval operasional |
| Manager | Persona bisnis sah (BC-8.4); workspace/dashboard **MAY** deferred — bukan syarat validitas persona |
| Petugas Regional | **Out of Scope for Mode A.** Not an actor on the Branch ↔ Head Office escalation path (BC-7.1 / BR-ESC-002 / BR-ORG-001). Listed only so readers do not invent Regional as Mode A delivery. |
| Petugas Kantor Pusat / Head Office | Menerima Case yang dieskalasikan ke Head Office; return / `result_visibility` detail = **DEC-F4 provisional** (not Mode A BR force until countersign — BR-ESC-003) |
| Administrator | Mengelola SLA Policy, parameter workflow, kategori, prioritas (di luar closed set operasional) |
| System | Otomasi (Mode A: bind SLA tanpa countdown); deteksi duplicate; pembentukan timeline; audit emit |
| Customer | Pihak yang menyampaikan keluhan (tidak login ke modul ini secara langsung dalam scope ini) |

### Glosarium Domain

| Istilah | Definisi |
|---|---|
| Complaint | Aggregate Root yang merepresentasikan keluhan/permintaan pelanggan sebagai satu kesatuan bisnis |
| Case | Unit kerja operasional di bawah Complaint; memiliki assignment dan SLA sendiri |
| CustomerId | Identitas pelanggan dari Master Customer; satu-satunya referensi pelanggan yang disimpan Complaint |
| Working Day | **Deferred** for Mode A SLA enforcement (BR-SLA-004). Historical catalog meaning: Senin–Jumat excluding Sabtu, Minggu, and official holidays (Calendar Platform). **Not** Mode A calendar baseline — baseline is 24×7 (BR-SLA-003). Do not confuse with the BC-5.4 “1 working day” Case-establishment **timing** threshold. |
| SLA Policy | Konfigurasi Administrator untuk target SLA per kategori/prioritas/tipe Case; Mode A = bind Policy Version without countdown (BQ-005) |
| Escalation Package | Seluruh konteks operasional Case/Complaint yang berpindah utuh saat eskalasi |
| Return / De-escalation | Pengembalian Case dari Head Office ke cabang asal; `return_reason_code` + `return_note` = **DEC-F4 detail** (Reserved for Mode A BR force until countersign) |
| `result_visibility` | Audience hasil setelah Resolve oleh Head Office: `ORIGIN_BRANCH` \| `ALL_BRANCHES` — **DEC-F4 detail** (Reserved for Mode A BR force until countersign) |
| Customer 360 View | Pandangan terpadu profil + riwayat interaksi Complaint/Case yang dimiliki ECMP, diperkaya data Master Customer |

### Complaint State Machine (ringkas — tidak diubah oleh DEC-BQ001)

**Complaint:** `REGISTERED` → `IN_PROGRESS` → `RESOLVED` → `CLOSED` · cabang: `REOPENED` → `IN_PROGRESS`

### Case Aggregate Transition Matrix

| Field | Value |
|---|---|
| SoT scope | **Case under Complaint Aggregate** — Batch-2 Mode A / CAP-02 (Definition B) |
| Governing decision | [`ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md`](../18%20Architecture%20Governance/reviews/ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md) (**DEC-BQ001**, Option **O3**, Status **APPROVED**) |
| Dual SoT | Sprint / case-centric Case SoT tetap **DOM-ECMF-003** — **bukan** matriks ini; keduanya tidak interchangeable |
| Aggregate | Complaint = Aggregate Root; Case = child |
| Explicit non-equivalence | Complaint `REGISTERED` ≠ Case `REGISTERED` (DOM-ECMF-003) |

> Matriks ini adalah **Source of Truth** status dan transisi Case Aggregate. Tidak memakai enum DOM-ECMF-003 (`REGISTERED`, `PENDING_REVIEW`, Case `REOPENED`) pada Case Aggregate.

#### 1. Case states

| State | Purpose | Entry Criteria | Exit Criteria | Terminal |
|---|---|---|---|---|
| `CREATED` | Case terbentuk di bawah Complaint; belum ada assignee aktif | Create Case / Add Case sukses (BR-004); Complaint induk mengizinkan; Case Number terbentuk | Assign pertama → `ASSIGNED`; atau Cancel → `CANCELLED` | No |
| `ASSIGNED` | Ada kepemilikan assignee dan/atau queue unit aktif (BR-005) | Assign/reassign/claim dari state yang mengizinkan; atau Create+Assign sekaligus (BR-004 A1) | Mulai kerja → `IN_PROGRESS`; reassign tetap/`ASSIGNED`; tunggu pihak → `PENDING`; eskalasi → `ESCALATED`; cancel → `CANCELLED` | No |
| `IN_PROGRESS` | Sedang dikerjakan petugas berwenang | Dari `ASSIGNED` (mulai penanganan); dari `PENDING` (lanjut); dari `ESCALATED` setelah Return ke cabang; reassign dapat kembali ke `ASSIGNED` | Pending / Escalate / Resolve / Cancel / Reassign | No |
| `PENDING` | Menunggu pihak eksternal/pelanggan/dokumen; kerja Case ditahan (BR-006 pause) | Dari `ASSIGNED` atau `IN_PROGRESS` dengan alasan tunggu wajib | Lanjut kerja → `IN_PROGRESS`; reassign → `ASSIGNED`; eskalasi → `ESCALATED`; resolve bila “PENDING selesai” (BR-008); cancel | No |
| `ESCALATED` | Ownership operasional di jenjang eskalasi (Pusat per DEC-F4); package lengkap (BR-007) | Eskalasi dari state aktif non-terminal dengan alasan + package valid | Assign di tujuan → `ASSIGNED`; Return ke cabang → `IN_PROGRESS`; Resolve → `RESOLVED`; Cancel hanya jika masih sebelum resolusi final & policy izinkan | No |
| `RESOLVED` | Resolution final **Accepted**; kerja Case selesai secara substansi (BR-008) | Resolve Accepted dari `IN_PROGRESS` / `ESCALATED` / `PENDING` (selesai) | Close Case → `CLOSED` | No |
| `CLOSED` | Siklus Case ditutup secara resmi | Dari `RESOLVED` setelah close berwenang | Tidak ada exit Case-level; pekerjaan ulang lewat **Complaint Reopen (BR-015)** + Case baru (default), bukan reopen status Case ini | **Yes** |
| `CANCELLED` | Case dibatalkan sebelum resolusi final + justifikasi (BR-004); bukan hard-delete | Dari `CREATED`/`ASSIGNED`/`IN_PROGRESS`/`PENDING`/`ESCALATED` dengan alasan wajib | Tidak ada | **Yes** |

**Bukan Case state:** `PENDING_APPROVAL` = status **usulan Resolution** (BR-008), bukan status Case.  
**Bukan Case state:** `REOPENED` = status **Complaint** (BR-015), bukan Case Aggregate.

**Catatan SoT (Return):** BR-007 A4 tidak menamai next status; matriks Aggregate menetapkan `ESCALATED` → `IN_PROGRESS` (cabang lanjut kerja / write restored). BR-008 menuliskan `RESOLVED`/`CLOSED`; urutan Definition B menetapkan `RESOLVED` → `CLOSED` sebagai Close Case terpisah.

#### 2. Allowed transitions

| Current State | Allowed Next State | Business Guard | Triggered By | Notes |
|---|---|---|---|---|
| *(none)* | `CREATED` | Complaint valid, tidak `CLOSED` tanpa reopen; aktor berwenang; tipe/prioritas valid; di bawah max Case/Complaint | Agent / Supervisor / System (Create Case, BR-004) | Status awal default |
| *(none)* | `ASSIGNED` | Sama Create + assignee/queue valid (BR-005) | Create Case + Assignment sekaligus (BR-004 A1) | Melewati persistensi lama di `CREATED` dalam satu aksi bisnis |
| `CREATED` | `ASSIGNED` | Assignee/queue valid; aktor punya hak assign | Supervisor / System (assign/claim) | Assign pertama |
| `CREATED` | `CANCELLED` | Alasan wajib; sebelum resolusi final | Supervisor (utama) / aktor berwenang | Bukan delete fisik |
| `ASSIGNED` | `IN_PROGRESS` | Aktor = assignee atau Supervisor unit terkait | Case Handler / Supervisor | Mulai penanganan |
| `ASSIGNED` | `ASSIGNED` | Target assignee/queue valid; history append-only | Reassign / claim / unassign-to-queue per BR-005 | Tetap status, ganti ownership |
| `ASSIGNED` | `PENDING` | Alasan tunggu wajib | Handler / Supervisor | Menunggu pihak lain |
| `ASSIGNED` | `ESCALATED` | Case belum `CLOSED`; alasan eskalasi; package No Information Lost; target Pusat (DEC-F4) | Supervisor / Handler berwenang / System auto-rule | Identitas Case tidak berubah |
| `ASSIGNED` | `CANCELLED` | Alasan wajib; belum ada Resolution Accepted | Supervisor / berwenang | |
| `IN_PROGRESS` | `PENDING` | Alasan tunggu wajib | Handler / Supervisor | |
| `IN_PROGRESS` | `ASSIGNED` | Reassign valid (BR-005) | Supervisor / claim policy | Ownership berubah |
| `IN_PROGRESS` | `ESCALATED` | Guard eskalasi BR-007 | Supervisor / Handler / System | |
| `IN_PROGRESS` | `RESOLVED` | Resolution lengkap; evidence wajib kategori terpenuhi; approval Accepted bila policy wajib; aktor assignee atau Supervisor | Handler (ajukan) + Supervisor (approve bila wajib) | `PENDING_APPROVAL` hanya pada Resolution History |
| `IN_PROGRESS` | `CANCELLED` | Alasan wajib; belum Resolution Accepted | Supervisor / berwenang | |
| `PENDING` | `IN_PROGRESS` | Alasan tunggu selesai / dokumen ada | Handler / Supervisor | Resume kerja |
| `PENDING` | `ASSIGNED` | Assign/reassign valid | Supervisor | BR-005 mengizinkan assign dari `PENDING` |
| `PENDING` | `ESCALATED` | Guard eskalasi BR-007 | Supervisor / System | |
| `PENDING` | `RESOLVED` | “PENDING selesai” + Resolution Accepted (BR-008) | Handler / Supervisor | Tidak resolve sambil masih menunggu item wajib |
| `PENDING` | `CANCELLED` | Alasan wajib; belum Resolution Accepted | Supervisor / berwenang | |
| `ESCALATED` | `ASSIGNED` | Assign di unit tujuan (Pusat) valid | Supervisor Pusat / claim Pusat | BR-005 + BR-007 |
| `ESCALATED` | `IN_PROGRESS` | **Return:** `return_reason_code` + `return_note` ≥ 10 trim; target = cabang asal; Case owned by Pusat | Petugas/Supervisor Pusat (BR-007 A4) | next = `IN_PROGRESS`; write cabang restored |
| `ESCALATED` | `RESOLVED` | Resolution Accepted; untuk Resolve Pusat: `result_visibility` set/default `ORIGIN_BRANCH` (DEC-F4) | Petugas Pusat / Supervisor | Return ≠ Resolve |
| `ESCALATED` | `CANCELLED` | Alasan wajib; belum Resolution Accepted; role berwenang | Supervisor berwenang | Hanya sebelum resolusi final |
| `RESOLVED` | `CLOSED` | Resolution Accepted masih berlaku; aktor berwenang close Case; checklist Case terpenuhi | Supervisor (utama) / Handler bila dikonfigurasi | Close Case ≠ auto Close Complaint (BR-009 terpisah) |

#### 3. Forbidden transitions

| Forbidden | Why (SoT) |
|---|---|
| Any → hard-delete / hilang tanpa status | BR-004: hapus fisik dilarang |
| `CLOSED` → any Case status | Definition B tidak punya Case `REOPENED`; BR-015 = reopen **Complaint** + Case baru (default) |
| `CANCELLED` → any | Terminal; kerja baru = Case baru di bawah Complaint yang mengizinkan |
| `RESOLVED` → `CANCELLED` | Cancel hanya sebelum resolusi final |
| `CLOSED` → `CANCELLED` | Sudah terminal close-with-resolution path |
| `CREATED` → `IN_PROGRESS` | Urutan Definition B: melalui `ASSIGNED` (kepemilikan jelas) |
| `CREATED` → `PENDING` / `ESCALATED` / `RESOLVED` / `CLOSED` | Belum ada basis kerja/assignment/package/resolusi |
| `CREATED` → `CLOSED` | Resolution wajib sebelum close (BR-008) |
| `ASSIGNED` → `RESOLVED` / `CLOSED` | BR-008: resolve dari kerja (`IN_PROGRESS` / `ESCALATED` / `PENDING` selesai), bukan langsung dari assign tanpa penanganan |
| `IN_PROGRESS` → `CREATED` | Tidak mundur ke status awal |
| `PENDING` → `CREATED` | Tidak mundur |
| `ESCALATED` → `CREATED` | Tidak mundur; identitas/history eskalasi tetap |
| `RESOLVED` → `IN_PROGRESS` / `ASSIGNED` / `PENDING` / `ESCALATED` | Setelah Accepted, ubah kerja = Case baru atau jalur Complaint reopen — bukan mundur status Case lama |
| `RESOLVED` → `ESCALATED` | Eskalasi hanya sebelum resolve final |
| Any → `ESCALATED` dari `RESOLVED`/`CLOSED`/`CANCELLED` | BR-007: aktif & belum CLOSED; terminal/cancel excluded |
| `CLOSED` → Create mutation pada Case yang sama | Write terbatas; Case baru via BR-015/BR-004 |
| Eskalasi tanpa package lengkap | BR-007 E1 / No Information Lost |
| Return tanpa kode/note | BR-007 E6 |
| Resolve tanpa evidence wajib kategori | BR-008 E1 |
| Resolve milik Case orang lain tanpa hak Supervisor | BR-008 E3 |
| Transisi yang mengubah status **Complaint** sebagai efek samping tak terkendali selain yang sudah disebut BR-004 (Complaint `REGISTERED`→`IN_PROGRESS` saat Case pertama) | Batas Aggregate vs Case |
| Memakai enum DOM-ECMF-003 (`REGISTERED`, `PENDING_REVIEW`, Case `REOPENED`) pada Case Aggregate | DEC-BQ001 O3: SoT terpisah |

#### 4. Entry criteria

Ringkas per state — lihat kolom **Entry Criteria** pada tabel §1 Case states. Setiap masuk state MUST memenuhi kriteria tersebut plus Business Guard pada baris allowed transition terkait.

#### 5. Exit criteria

Ringkas per state — lihat kolom **Exit Criteria** pada tabel §1 Case states. Keluar state hanya melalui **Allowed transitions** (§2); selain itu MUST ditolak.

#### 6. Terminal states

| Terminal state | Meaning |
|---|---|
| `CLOSED` | Siklus Case ditutup setelah Resolution Accepted; tidak ada exit Case-level |
| `CANCELLED` | Case dibatalkan sebelum resolusi final; tidak ada un-cancel; kerja baru = Case baru |

#### 7. Business guards

1. Setiap transisi MUST ada di §2 Allowed transitions; selain itu MUST ditolak.  
2. Case MUST memiliki Complaint induk yang sama sepanjang hidupnya.  
3. Create Case MUST ditolak jika Complaint `CLOSED` tanpa reopen (BR-004 E1).  
4. Assign MUST ditolak pada `RESOLVED` / `CLOSED` / `CANCELLED` (BR-005 E3).  
5. Escalate MUST ditolak dari `CLOSED` / `CANCELLED` / `RESOLVED`; MUST menolak package tidak lengkap.  
6. Return MUST hanya dari `ESCALATED` owned by Pusat; MUST punya `return_reason_code` + `return_note` (min 10 trim); MUST NOT set `result_visibility`.  
7. Resolve MUST menolak evidence wajib hilang; MUST menghasilkan Resolution History append-only; Case MUST menjadi `RESOLVED` hanya setelah Accepted.  
8. Close Case MUST hanya dari `RESOLVED`; MUST NOT otomatis menutup Complaint kecuali keputusan BR-009 terpisah.  
9. Cancel MUST punya alasan; MUST ONLY sebelum Resolution Accepted; MUST NOT hard-delete.  
10. Tidak boleh memakai status DOM-ECMF-003 pada Case Aggregate (DEC-BQ001 O3).  
11. Tidak boleh reopen dengan mengubah Case `CLOSED` → status kerja; gunakan BR-015 pada Complaint.  
12. Setiap transisi sukses MUST tercatat Timeline + Audit (BR-016 / BR-017).

**Invariant lintas state:** Case selalu punya Complaint induk; CustomerId tetap di Complaint; Timeline+Audit pada setiap transisi sukses.

#### 8. Transition business events

| Transition | Business Event | Business Meaning |
|---|---|---|
| → `CREATED` | CaseCreated | Unit kerja operasional baru di bawah Complaint |
| → `ASSIGNED` (create+assign atau assign) | CaseAssigned | Kepemilikan kerja ditetapkan/dialihkan |
| `ASSIGNED` → `IN_PROGRESS` | CaseWorkStarted | Penanganan aktif dimulai |
| `*` → `PENDING` | CasePending | Kerja ditahan menunggu pihak/dokumen |
| `PENDING` → `IN_PROGRESS` | CaseResumed | Penanganan dilanjutkan |
| `*` → `ESCALATED` | CaseEscalated | Ownership + package pindah ke jenjang lebih tinggi (Pusat) |
| `ESCALATED` → `IN_PROGRESS` (Return) | CaseEscalationReturned | Dikembalikan ke cabang asal; bukan resolve |
| `*` → `RESOLVED` | CaseResolved | Resolusi final Accepted; substansi kerja selesai |
| `RESOLVED` → `CLOSED` | CaseClosed | Siklus Case ditutup resmi |
| `*` → `CANCELLED` | CaseCancelled | Case dibatalkan sebelum resolusi final |
| Reassign (`ASSIGNED`↔ / `IN_PROGRESS`→`ASSIGNED`) | CaseReassigned | Ownership berubah; history lama tidak dihapus |

> Nama event di atas = **business event names** untuk matriks Aggregate; **bukan** spesifikasi katalog EVT / OpenAPI.

#### 9. Governing decision reference

| Item | Value |
|---|---|
| Decision | DEC-BQ001 — Case State Machine Option O3 |
| File | `18 Architecture Governance/reviews/ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md` |
| Countersign | `18 Architecture Governance/reviews/ECMP_DEC_BQ001_Architecture_Board_Countersign_Pack_v1.0.md` |
| Status | **APPROVED** (2026-08-01) |
| Effect | Matriks ini adalah SoT Case Aggregate; DOM-ECMF-003 tetap SoT Sprint / case-centric |

---

# Katalog Business Rules

| Rule ID | Nama |
|---|---|
| BR-001 | Create Complaint |
| BR-002 | Customer Validation |
| BR-003 | Complaint Search |
| BR-004 | Create Case |
| BR-005 | Assignment |
| BR-006 | Working Day SLA |
| BR-007 | Escalation |
| BR-008 | Resolution |
| BR-009 | Complaint Closure |
| BR-010 | Customer 360 View |
| BR-011 | Communication History |
| BR-012 | Attachment Management |
| BR-013 | Comment Management |
| BR-014 | Duplicate Complaint |
| BR-015 | Complaint Reopen |
| BR-016 | Audit Trail |
| BR-017 | Timeline |
| BR-018 | Complaint History |
| BR-019 | Dashboard KPI |
| BR-020 | Reporting |

---

# BR-001 — Create Complaint

## Nama Rule

Create Complaint

## Purpose

Menjamin setiap keluhan pelanggan masuk ke ECMP sebagai **Complaint Aggregate Root** yang sah, teridentifikasi, dapat dilacak, dan siap dilanjutkan menjadi satu atau lebih Case operasional — tanpa menggandakan data pelanggan dan tanpa kehilangan jejak intake.

## Business Description

Create Complaint adalah pintu masuk utama Complaint Management Module. Aktor yang berwenang mendaftarkan Complaint setelah pelanggan teridentifikasi melalui Master Customer (lihat BR-002). Sistem membentuk identitas Complaint unik, menautkan `CustomerId`, merekam atribut klasifikasi awal, kanal intake, ringkasan keluhan, serta metadata organisasi unit pencatat.

Complaint **bukan** Case. Pada saat pembuatan, Complaint menjadi wadah bisnis; Case operasional dapat dibuat bersamaan (minimal satu Case awal) atau segera setelahnya sesuai BR-004. Tanpa Complaint yang valid, tidak boleh ada Case, Assignment, SLA, Resolusi, atau Closure.

Prinsip yang ditegakkan:

- Single Source of Truth untuk identitas Complaint.
- Complaint hanya menyimpan `CustomerId`, bukan salinan master pelanggan yang dijadikan SoR.
- Agent memasukkan Nomor Pelanggan **atau** Nomor Identitas **atau** Nomor Referensi; sistem mengambil data pelanggan dari Master Customer.
- Setiap pembuatan menghasilkan jejak Audit (BR-016) dan entri Timeline (BR-017).
- Deteksi potensi duplikasi dijalankan sesuai BR-014 sebelum konfirmasi final (peringatan, bukan otomatis menolak kecuali aturan keras terpenuhi).

## Actors

| Aktor | Tanggung Jawab pada Rule Ini |
|---|---|
| Agent / Petugas Frontline | Memulai pembuatan, memilih kunci pencarian pelanggan, mengisi atribut Complaint |
| Supervisor Unit | Dapat membuat Complaint atas nama unit; mengoverride peringatan duplikat dengan justifikasi (bila diizinkan kebijakan) |
| System | Generate nomor Complaint, set status awal, tautkan CustomerId, tulis audit/timeline, panggil validasi pelanggan |
| Administrator | Mengonfigurasi kategori, kanal, prioritas default, kebijakan “wajib Case awal” |

## Preconditions

1. Aktor telah terautentikasi melalui dependency Authentication/Identity eksternal.
2. Aktor memiliki otorisasi Complaint Module untuk membuat Complaint (authorization internal ECMP).
3. Organisasi/unit aktor tersedia dari dependency Organization.
4. Master Customer dapat diakses untuk resolusi pelanggan, atau mode degradasi yang diizinkan kebijakan (lihat Exception Flow) telah dikonfigurasi.
5. Parameter referensi aktif: kategori Complaint, kanal intake, prioritas default, dan (opsional) template subjek.
6. Calendar Platform tidak wajib untuk Create Complaint, tetapi wajib tersedia sebelum SLA Case diaktifkan (BR-006).

## Trigger

Aktor memilih aksi bisnis **“Buat Complaint Baru”** setelah menerima keluhan dari pelanggan melalui kanal yang diakui (walk-in, telepon, email, portal, media sosial yang terintegrasi, atau kanal lain yang dikonfigurasi Administrator).

## Normal Flow

1. Aktor membuka formulir Create Complaint.
2. Aktor memasukkan **salah satu** kunci pencarian pelanggan:
   - Nomor Pelanggan, atau
   - Nomor Identitas, atau
   - Nomor Referensi.
3. Sistem menjalankan **Customer Validation** (BR-002) dan menampilkan hasil profil ringkas dari Master Customer.
4. Aktor mengonfirmasi bahwa pelanggan yang ditampilkan adalah pihak yang benar.
5. Sistem menampilkan/menyediakan akses ke **Customer 360 View** (BR-010) agar aktor melihat Complaint aktif dan riwayat terkait sebelum melanjutkan.
6. Sistem menjalankan pemeriksaan **Duplicate Complaint** (BR-014) dan menampilkan peringatan bila ada kandidat duplikat.
7. Aktor mengisi atribut wajib Complaint:
   - Kanal intake
   - Kategori / tipe keluhan
   - Subjek
   - Deskripsi
   - Prioritas awal (atau menerima default dari kebijakan)
   - Unit pencatat (default = unit aktor)
   - Referensi eksternal opsional (nomor tiket kanal, nomor surat, dsb.)
8. Aktor dapat melampirkan bukti awal (BR-012) dan catatan komunikasi awal (BR-011 / BR-013).
9. Aktor mengonfirmasi pembuatan.
10. Sistem menghasilkan **Complaint Number** unik, menetapkan status awal `REGISTERED`, menyimpan `CustomerId`, mencatat waktu registrasi, dan menautkan identitas aktor serta unit.
11. Bila kebijakan “Case awal wajib” aktif, sistem memicu **Create Case** (BR-004) untuk Case pertama dalam transaksi bisnis yang sama.
12. Sistem menulis Audit Trail (BR-016), entri Timeline (BR-017), dan meminta Notification Platform mengirim notifikasi sesuai konfigurasi opt-in.
13. Sistem menampilkan konfirmasi berisi nomor Complaint dan status.

## Alternative Flow

### A1 — Pelanggan ditemukan lebih dari satu kandidat

1. Master Customer mengembalikan beberapa kandidat yang cocok dengan kunci pencarian.
2. Sistem menampilkan daftar kandidat (identifikasi minimum yang diizinkan keamanan).
3. Aktor memilih satu pelanggan.
4. Alur kembali ke langkah konfirmasi Normal Flow.

### A2 — Peringatan duplikat ditindaklanjuti dengan tautan ke Complaint existing

1. BR-014 menandai kandidat duplikat kuat.
2. Aktor memilih membuka Complaint existing dan **tidak** membuat Complaint baru.
3. Create Complaint dibatalkan tanpa membentuk Aggregate baru.
4. Aktor dapat menambahkan Case baru pada Complaint existing (BR-004) bila keluhan adalah aspek baru dari keluhan yang sama.

### A3 — Peringatan duplikat diabaikan dengan justifikasi

1. Aktor (dengan wewenang Supervisor atau sesuai kebijakan) melanjutkan pembuatan meski ada peringatan.
2. Justifikasi wajib diisi.
3. Complaint baru tetap dibuat; hubungan “possible duplicate of” dicatat pada History (BR-018) dan Audit.

### A4 — Complaint dibuat tanpa Case awal

1. Kebijakan Administrator mengizinkan Complaint tanpa Case pada detik pertama.
2. Complaint berstatus `REGISTERED` menunggu Create Case.
3. SLA belum berjalan karena SLA melekat pada Case (BR-006).
4. Supervisor queue menandai Complaint tanpa Case sebagai item yang perlu ditindaklanjuti.

### A5 — Intake dari kanal terintegrasi

1. Channel boundary menyerahkan payload intake yang sudah memuat kunci pelanggan dan deskripsi.
2. Agent mereview dan mengonfirmasi sebelum Aggregate terbentuk, atau sistem membentuk Complaint otomatis bila kebijakan auto-register kanal tersebut aktif dan validasi lulus.
3. Jejak “sumber kanal” wajib tercatat.

## Exception Flow

### E1 — Kunci pencarian pelanggan kosong / tidak lengkap

Sistem menolak lanjut. Pesan bisnis: minimal satu dari Nomor Pelanggan, Nomor Identitas, atau Nomor Referensi wajib diisi.

### E2 — Pelanggan tidak ditemukan di Master Customer

Sistem menolak Create Complaint. Agent tidak boleh mengarang data pelanggan. Pengecualian hanya jika kebijakan enterprise mengizinkan “Complaint dengan pelanggan belum terverifikasi” untuk situasi darurat — status pelanggan ditandai `UNVERIFIED`, dan wajib ditindaklanjuti validasi ulang (lihat BR-002 Exception).

### E3 — Master Customer tidak tersedia

Sesuai kebijakan degradasi:

- **Strict:** Create ditolak; keluhan dicatat di prosedur offline operasional di luar sistem (bukan invent data).
- **Degraded (jika dikonfigurasi):** Complaint boleh dibuat dengan flag `customerVerificationPending=true` dan `CustomerId` sementara/kandidat yang diizinkan kebijakan; wajib reconcile saat Master pulih. Data atribut pelanggan tidak diisi manual sebagai SoR.

### E4 — Aktor tidak berwenang

Pembuatan ditolak. Percobaan dicatat pada Audit keamanan.

### E5 — Atribut wajib tidak lengkap / tidak valid

Sistem menolak konfirmasi dan menandai field yang melanggar (panjang subjek/deskripsi, kategori tidak aktif, kanal tidak dikenal, dsb.).

### E6 — Kegagalan penulisan jejak wajib (Audit/Timeline)

Create Complaint dianggap gagal secara bisnis. Tidak boleh terbentuk Complaint tanpa Audit Trail wajib. Konsistensi Single Source of Truth dijaga (tidak ada Aggregate “setengah jadi” yang terlihat operasional tanpa jejak).

## Business Validation

| Validasi | Aturan |
|---|---|
| Kunci pelanggan | Tepat satu jenis kunci primer digunakan untuk lookup; tidak boleh mengisi saling bertentangan tanpa resolusi |
| CustomerId | Wajib ada setelah validasi berhasil (kecuali mode UNVERIFIED yang dikonfigurasi) |
| Subjek | Wajib, panjang sesuai kebijakan (disarankan 1–200 karakter bisnis) |
| Deskripsi | Wajib, panjang sesuai kebijakan (disarankan 1–5000 karakter bisnis) |
| Kategori | Harus aktif pada katalog konfigurasi |
| Kanal | Harus aktif pada katalog konfigurasi |
| Prioritas | Harus salah satu nilai yang dikonfigurasi |
| Duplikat | Peringatan wajib ditampilkan bila skor kandidat ≥ ambang; override butuh justifikasi bila kebijakan mensyaratkan |
| Otorisasi | Aktor harus punya hak create Complaint pada unit terkait |

## Business Constraints

1. ECMP **bukan** System of Record Master Customer.
2. Complaint adalah Aggregate Root; identitas Complaint tidak boleh didaur ulang.
3. Satu Complaint dapat memiliki banyak Case, tetapi Create Complaint tidak boleh menciptakan Case di luar Aggregate Complaint yang sama.
4. Tidak ada Assignment atau SLA pada level Complaint.
5. Nomor Complaint bersifat unik enterprise dalam modul.
6. Setelah terbentuk, penghapusan fisik Complaint dilarang; pembatalan hanya melalui status/alur yang dikonfigurasi dengan audit.
7. Perubahan aturan klasifikasi di masa depan tidak mengubah histori Complaint yang sudah tercatat (konfigurasi ber-effective date).

## Data Affected

- Complaint (baru): nomor, status, CustomerId, kategori, kanal, subjek, deskripsi, prioritas, unit, waktu registrasi, aktor pembuat, flag verifikasi pelanggan, tautan possible-duplicate (opsional)
- Case awal (opsional/wajib sesuai kebijakan) — dampak mengikuti BR-004
- Timeline entry “Complaint Created”
- Audit Trail “ComplaintCreated”
- Complaint History snapshot awal
- Communication / Attachment awal bila diunggah
- Indeks pencarian Complaint (BR-003)

## Notifications

Melalui Notification Platform (opt-in konfigurasi), contoh penerima:

- Supervisor unit pencatat — Complaint baru masuk antrian
- Agent pembuat — konfirmasi nomor Complaint
- Pihak lain sesuai matriks notifikasi Administrator

Kegagalan notifikasi **tidak** membatalkan Create Complaint yang sudah sukses, tetapi wajib tercatat pada delivery log dependency Notification.

## Audit Trail

Wajib mencatat minimal:

- Siapa (identitas aktor eksternal yang dipetakan ke principal ECMP)
- Apa (Create Complaint)
- Kapan (timestamp tepercaya)
- Di mana (unit organisasi)
- Objek (Complaint Number / ID internal)
- Nilai atribut bisnis penting (kategori, prioritas, CustomerId, kanal)
- Hasil pemeriksaan duplikat (ada/tidak, override atau tidak)
- Correlation ke Case awal bila dibuat

## Security Considerations

1. Data pelanggan yang ditampilkan saat create mengikuti need-to-know dan masking sesuai kebijakan akses.
2. Percobaan create tanpa entitlement modul ditolak.
3. Justifikasi override duplikat termasuk data sensitif operasional; akses baca dibatasi role.
4. Lampiran pada create mengikuti kontrol BR-012 (tipe, ukuran, malware scan oleh dependency terkait bila ada).

## KPI Impact

| KPI / Metrik | Dampak |
|---|---|
| Volume Complaint Baru | Bertambah per periode |
| Time to Register | Diukur dari intake hingga Complaint REGISTERED |
| % Complaint dengan pelanggan terverifikasi | Dipengaruhi keberhasilan BR-002 |
| % Possible Duplicate Override | Indikator kualitas intake |
| Complaint tanpa Case (aging) | Indikator kepatuhan kebijakan Case awal |

## Future Enhancement

1. Auto-classification kategori/prioritas berbasis aturan lanjutan atau asistensi terukur (tetap configuration-first; tidak mengubah Aggregate model).
2. Intake omnichannel penuh dengan idempotensi per message-id kanal.
3. Kebijakan “Complaint draft” tersimpan sementara sebelum submit final.
4. Score duplikat yang dapat dikalibrasi Administrator per kategori.

---

# BR-002 — Customer Validation

## Nama Rule

Customer Validation

## Purpose

Memastikan setiap Complaint hanya tertaut pada pelanggan yang sah menurut Master Customer, dengan cara input yang sederhana bagi Agent, tanpa menjadikan ECMP sebagai penyimpan otoritatif data pelanggan.

## Business Description

Customer Validation adalah aturan yang mengatur cara Agent mengidentifikasi pelanggan dan cara sistem menyelesaikan identitas menjadi `CustomerId`.

Agent **hanya** memasukkan salah satu dari:

1. Nomor Pelanggan, atau
2. Nomor Identitas, atau
3. Nomor Referensi.

Sistem kemudian mengambil seluruh data pelanggan yang diperlukan dari Master Customer. ECMP menyimpan `CustomerId` pada Complaint dan boleh menampilkan salinan baca (cache read-only) untuk keperluan operasional, tetapi **tidak** boleh menerima edit master dari Agent sebagai SoR.

Validasi ini menjadi prasyarat Create Complaint (BR-001), Create Case yang mensyaratkan konteks pelanggan, Customer 360 (BR-010), dan sebagian besar komunikasi eksternal yang menyebut identitas pelanggan.

## Actors

| Aktor | Tanggung Jawab |
|---|---|
| Agent / Case Handler / Supervisor | Memasukkan kunci pencarian, memilih kandidat, mengonfirmasi kecocokan |
| System | Memanggil Master Customer, menormalisasi hasil, menetapkan status verifikasi |
| Administrator | Mengonfigurasi jenis kunci yang diterima, timeout, kebijakan degradasi |
| Master Customer (eksternal) | Sumber kebenaran data pelanggan |

## Preconditions

1. Aktor berwenang melihat data pelanggan sesuai role (field sensitif dapat dimask).
2. Integrasi baca ke Master Customer terdefinisi sebagai dependency.
3. Jenis kunci pencarian yang diizinkan aktif pada konfigurasi.

## Trigger

- Sebelum Create Complaint dikonfirmasi
- Saat aktor memicu “Cari Pelanggan” dari Customer 360
- Saat reconcile Complaint berstatus verifikasi tertunda
- Saat kanal terintegrasi mengirim kunci pelanggan untuk divalidasi

## Normal Flow

1. Aktor memilih jenis kunci dan memasukkan nilai.
2. Sistem memvalidasi format dasar (tidak kosong; pola sesuai jenis kunci bila dikonfigurasi).
3. Sistem meminta Master Customer melakukan pencarian.
4. Bila tepat satu hasil definitif, sistem menampilkan profil ringkas dan menetapkan kandidat `CustomerId`.
5. Aktor mengonfirmasi.
6. Sistem menandai `customerVerified=true` pada konteks transaksi dan mengunci `CustomerId` untuk Complaint yang akan dibuat/ditautkan.
7. Sistem dapat menyegarkan cache read-only Customer 360 untuk `CustomerId` tersebut.

## Alternative Flow

### A1 — Banyak kandidat

Sistem menampilkan daftar; aktor memilih satu; konfirmasi wajib.

### A2 — Pencarian ulang

Aktor mengubah kunci; hasil sebelumnya dibuang dari konteks konfirmasi; tidak boleh mencampur `CustomerId` lama dan baru tanpa konfirmasi eksplisit.

### A3 — Pelanggan non-aktif di Master

Ditampilkan dengan status non-aktif. Kebijakan menentukan apakah Complaint tetap boleh dibuat (misalnya untuk sengketa pelanggan non-aktif). Bila diizinkan, flag khusus dicatat.

### A4 — Enrichment setelah create

Complaint UNVERIFIED kemudian divalidasi sukses; `CustomerId` final ditetapkan; History mencatat perubahan referensi pelanggan dengan audit lengkap.

## Exception Flow

### E1 — Tidak ditemukan

Validasi gagal; Create Complaint normal ditolak kecuali mode darurat dikonfigurasi.

### E2 — Master timeout / unavailable

Ikuti kebijakan Strict vs Degraded (selaras BR-001 E3). Retry terbatas boleh dilakukan; looping tanpa batas dilarang pada sesi Agent.

### E3 — Hasil ambigu tanpa pemilihan

Sistem menolak menetapkan `CustomerId` otomatis.

### E4 — Upaya mengubah data master dari ECMP

Ditolak. Pesan bisnis: perubahan master hanya melalui proses/sistem Master Customer.

### E5 — Ketidakcocokan kunci

Jika aktor mengisi lebih dari satu kunci dan hasilnya saling bertentangan, sistem memaksa resolusi manual; tidak memilih diam-diam.

## Business Validation

| Validasi | Aturan |
|---|---|
| Keberadaan kunci | Minimal satu kunci wajib |
| Konsistensi | Satu `CustomerId` aktif per konfirmasi |
| Read-only | Tidak ada write-back master dari ECMP |
| Masking | Kontak sensitif mengikuti kebijakan role |
| Verifikasi | Status verified/unverified wajib eksplisit |

## Business Constraints

1. Complaint hanya menyimpan `CustomerId` sebagai referensi pelanggan otoritatif di sisi ECMP.
2. Salinan atribut pelanggan di ECMP bersifat read-model / cache dan dapat kedaluwarsa; penyegaran mengikuti kebijakan.
3. Dilarang membuat “pelanggan lokal” sebagai pengganti Master.
4. Validasi ulang tidak boleh menghapus History Complaint; hanya memperbarui referensi dengan jejak.

## Data Affected

- Konteks sesi validasi (sementara)
- Complaint.CustomerId dan flag verifikasi
- Cache/read-model Customer 360
- Audit “CustomerValidated” / “CustomerVerificationPending”

## Notifications

Umumnya tidak notifikasi pelanggan. Notifikasi internal opsional ke Supervisor bila volume UNVERIFIED melebihi ambang.

## Audit Trail

Wajib: jenis kunci yang digunakan (bukan menyimpan nomor identitas penuh bila kebijakan melarang — boleh hash/mask pada audit), `CustomerId` hasil, status verifikasi, aktor, waktu, hasil (found/not found/ambiguous/degraded).

## Security Considerations

1. Nomor identitas adalah data sensitif; tampilan dan log harus diminimalkan.
2. Akses hasil pencarian dibatasi need-to-know.
3. Cegah enumerasi massal (rate limit bisnis / pantauan anomali melalui kontrol keamanan enterprise).

## KPI Impact

- % Complaint terverifikasi saat create
- Lama waktu validasi rata-rata
- % transaksi degraded/UNVERIFIED
- % reconcile sukses dalam SLA operasional internal

## Future Enhancement

1. Validasi biometrik/kanal digital identity (di luar modul; hanya konsumsi hasil).
2. Fuzzy match terkendali dengan skor dan threshold yang dikonfigurasi.
3. Watchlist / perhatian khusus pelanggan (flag read-only dari master).

---

# BR-003 — Complaint Search

## Nama Rule

Complaint Search

## Purpose

Memungkinkan aktor menemukan Complaint yang tepat dengan cepat dan akurat sebagai fondasi operasional No Duplicate Work, penanganan lanjutan, dan Customer 360 — tanpa membocorkan data di luar hak akses.

## Business Description

Complaint Search adalah kemampuan mencari Aggregate Complaint berdasarkan atribut bisnis dan konteks pelanggan/organisasi. Hasil pencarian adalah daftar ringkas yang dapat dibuka ke detail Complaint, Case terkait, Timeline, dan Customer 360.

Pencarian bersifat **read-only** terhadap data transaksi; tidak mengubah status. Filter dan kewenangan mengikuti organisasi serta role ECMP. Karena Assignment dan SLA ada di Case, hasil pencarian dapat menampilkan agregat status Case (misalnya jumlah Case terbuka, SLA terburuk) sebagai informasi bantu, dengan Single Source of Truth tetap pada Case masing-masing.

## Actors

Agent, Case Handler, Supervisor, Petugas Regional, Petugas Kantor Pusat, Administrator (dukungan), System (eksekusi query bisnis / indeks)

## Preconditions

1. Aktor terautentikasi dan berwenang `complaint:search` / setara.
2. Indeks atau view pencarian tersedia untuk atribut yang diizinkan.
3. Scope organisasi aktor diketahui dari dependency Organization.

## Trigger

Aktor membuka fungsi cari Complaint, atau sistem memicu pencarian sebagai bagian deteksi duplikat (BR-014) maupun konteks Customer 360.

## Normal Flow

1. Aktor memasukkan kriteria: nomor Complaint, CustomerId / nomor pelanggan, subjek kata kunci, kategori, status, rentang tanggal, unit, kanal, prioritas, flag SLA berisiko (dari Case), dsb.
2. Sistem menerapkan filter otorisasi (hanya data dalam lingkup yang diizinkan, kecuali role lintas-unit yang sah).
3. Sistem mengembalikan daftar terurut (default: terbaru dulu, atau sesuai konfigurasi).
4. Aktor memilih satu baris untuk membuka detail.
5. Setiap pembukaan detail menghasilkan jejak akses sesuai kebijakan audit baca (bila diwajibkan untuk data sensitif).

## Alternative Flow

### A1 — Pencarian oleh pelanggan (Customer-centric)

Dari Customer 360, sistem menampilkan semua Complaint terkait `CustomerId` dalam lingkup hak akses.

### A2 — Pencarian Case-centric yang naik ke Complaint

Aktor mencari nomor Case; sistem menampilkan Case dan Complaint induknya (navigasi Aggregate).

### A3 — Tidak ada hasil

Sistem menampilkan kosong dengan opsi buat Complaint baru (jika berwenang).

### A4 — Hasil terlalu banyak

Sistem membatasi page size; mewajibkan kriteria lebih spesifik setelah ambang.

## Exception Flow

### E1 — Kriteria kosong total

Ditolak atau diganti default terbatas (mis. hanya Complaint unit sendiri 7 hari terakhir) sesuai kebijakan.

### E2 — Mencoba akses di luar lingkup

Data tidak ditampilkan (bukan error teknis yang membocorkan keberadaan bila kebijakan mengharuskan responses seragam). Percobaan dapat diaudit.

### E3 — Indeks pencarian stale

Hasil dapat diberi penanda “as of”; aktor dapat memicu refresh terbatas. Angka operasional kritis harus reconcile ke sumber transaksi (prinsip Dashboard/Reporting).

## Business Validation

- Panjang kata kunci minimum/maksimum
- Rentang tanggal tidak terbalik dan tidak melebihi jendela maksimum yang dikonfigurasi
- Operator filter hanya dari daftar yang diizinkan
- Sort field hanya field yang diizinkan

## Business Constraints

1. Search tidak mengubah data.
2. Tidak menampilkan field tersembunyi bagi role yang tidak berhak.
3. Nomor identitas penuh tidak menjadi kriteria bebas-teks tanpa kontrol.
4. Hasil pencarian bukan sumber otoritatif status SLA; SLA SoT di Case (BR-006).

## Data Affected

Tidak mengubah data master transaksi. Dapat menulis audit akses dan telemetri pencarian (kriteria tersanitasi).

## Notifications

Tidak ada, kecuali alert keamanan atas pola pencarian anomali (di luar modul inti; opsional).

## Audit Trail

Minimal untuk pencarian sensitif: siapa, kapan, kriteria (disanitasi), jumlah hasil, Complaint yang dibuka.

## Security Considerations

Cegah data scraping; enforce scope org; masking; pantau bulk export dari hasil search (terkait BR-020).

## KPI Impact

- Average Time to Find Complaint
- % Zero-result yang dilanjutkan create baru
- Digunakan sebagai input efisiensi operasional frontline

## Future Enhancement

Saved filters per role; full-text terkendali pada deskripsi; pencarian lintas periode arsip dengan tiering.

---

# BR-004 — Create Case

## Nama Rule

Create Case

## Purpose

Membentuk unit kerja operasional di bawah Complaint agar pekerjaan dapat di-assign, diukur SLA-nya, dieskalasikan, dan diselesaikan tanpa memecah Single Source of Truth Aggregate Complaint.

## Business Description

Case adalah **anak operasional** dari Complaint. Setiap Case merepresentasikan satu potongan kerja yang dapat ditangani secara independen (misalnya isu tagihan vs isu layanan teknis dalam satu keluhan pelanggan yang sama), namun tetap berada dalam batas Aggregate Complaint.

Aturan kunci yang dikunci domain:

- Assignment berada pada Case.
- SLA berada pada Case.
- Eskalasi memindahkan konteks Case (dan informasi terkait) secara utuh.
- Membuat Case baru tidak boleh menggandakan Complaint untuk pekerjaan yang masih dalam konteks keluhan yang sama (No Duplicate Work) — kecuali BR-014 menyatakan perlu Complaint terpisah.

## Actors

Agent, Case Handler, Supervisor, System, Administrator (konfigurasi tipe Case / template)

## Preconditions

1. Complaint induk ada dan tidak dalam status yang melarang Case baru (mis. `CLOSED` tanpa reopen — lihat BR-015).
2. Aktor berwenang menambah Case pada Complaint tersebut (unit/role).
3. Tipe Case, kategori turunan, dan SLA Policy terkait aktif.
4. CustomerId Complaint sudah ada (terverifikasi atau UNVERIFIED sesuai kebijakan).

## Trigger

- Otomatis saat Create Complaint bila kebijakan Case awal wajib
- Manual oleh aktor pada Complaint aktif
- Sebagai hasil pecah isu (split) yang disetujui Supervisor
- Saat reopen Complaint yang membutuhkan Case penanganan baru (BR-015)

## Normal Flow

1. Aktor memilih Complaint induk.
2. Aktor menentukan tipe/kategori Case, subjek Case, deskripsi kerja, prioritas Case, unit tujuan awal.
3. Sistem membentuk Case Number unik dalam korelasi ke Complaint.
4. Status Case = `CREATED` (atau langsung `ASSIGNED` bila assignment sekalian — BR-005).
5. Sistem mengikat SLA Policy yang berlaku dan **belum** atau **sudah** memulai jam SLA sesuai kebijakan trigger SLA (umum: mulai saat ASSIGNED atau saat CREATED — harus konsisten pada SLA Policy; lihat BR-006).
6. Timeline Complaint & Case mencatat “Case Created”.
7. Audit mencatat atribut dan relasi ke Complaint.
8. Notifikasi ke Supervisor/unit tujuan sesuai konfigurasi.
9. Status Complaint menjadi `IN_PROGRESS` bila sebelumnya `REGISTERED` dan belum berstatus lebih lanjut.

## Alternative Flow

### A1 — Create Case + Assignment sekaligus

Setelah Case terbentuk, alur BR-005 dijalankan dalam satu aksi bisnis.

### A2 — Multiple Case paralel

Complaint dapat memiliki Case A, B, C aktif bersamaan; masing-masing SLA dan assignment sendiri.

### A3 — Case informational / follow-up

Tipe Case tertentu mungkin memiliki SLA berbeda atau SLA “monitoring”; tetap Case formal agar traceable.

## Exception Flow

### E1 — Complaint CLOSED

Ditolak; arahkan ke Reopen (BR-015) bila memenuhi syarat.

### E2 — Tipe Case tidak kompatibel dengan kategori Complaint

Ditolak atau minta konfirmasi Supervisor sesuai konfigurasi.

### E3 — Batas maksimum Case per Complaint tercapai

Ditolak sampai kebijakan menaikkan batas atau Case lama ditutup.

### E4 — Aktor luar unit tanpa wewenang

Ditolak dan diaudit.

## Business Validation

| Field | Aturan |
|---|---|
| Complaint induk | Wajib, status mengizinkan |
| Tipe Case | Aktif |
| Subjek/Deskripsi | Wajib sesuai kebijakan |
| Prioritas | Valid |
| Unit tujuan | Valid pada Organization dependency |

## Business Constraints

1. Case tidak dapat berdiri tanpa Complaint.
2. Case tidak memindahkan kepemilikan CustomerId (tetap di Complaint).
3. Menghapus Case fisik dilarang; batalkan dengan status `CANCELLED` + alasan.
4. Semua artefak operasional Case (note, attachment, komunikasi) tetap milik jejak Complaint Aggregate untuk keperluan 360 dan eskalasi.

## Data Affected

Case baru; relasi Complaint–Case; Timeline; Audit; indeks search; possibly SLA instance (BR-006); queue assignment.

## Notifications

Unit tujuan / Supervisor / Assignee (jika langsung di-assign).

## Audit Trail

CaseCreated dengan referensi Complaint, atribut klasifikasi, aktor, unit, kebijakan SLA yang terikat (versi policy).

## Security Considerations

Hak create Case dapat lebih ketat daripada create Complaint; Case berisi konteks operasional sensitif.

## KPI Impact

- Case volume & Case per Complaint
- Time from Complaint registration to first Case
- Parallel open Case count (beban operasional)

## Future Enhancement

Template Case by kategori; auto-split rule berbasis struktur keluhan; linked Case lintas Complaint (hanya referensial, bukan merge Aggregate tanpa aturan khusus).

---

# BR-005 — Assignment

## Nama Rule

Assignment

## Purpose

Menetapkan kepemilikan kerja operasional pada level Case agar setiap Case memiliki penanggung jawab yang jelas, dapat dialihkan secara terkendali, dan seluruh sejarah penugasan tersimpan untuk audit serta eskalasi tanpa kehilangan informasi.

## Business Description

Assignment **hanya** terjadi pada Case, bukan pada Complaint. Satu Case pada satu waktu memiliki assignee aktif (individu dan/atau queue unit) sesuai model yang dikonfigurasi. Riwayat assignment bersifat append-only: setiap perubahan menghasilkan Assignment History yang ikut dibawa saat eskalasi (BR-007).

Prinsip No Duplicate Work: jangan meng-assign Case yang sama ke dua handler aktif bertentangan; transfer harus eksplisit. Supervisor mengatur beban kerja unit. Petugas Regional/Pusat menerima assignment setelah eskalasi.

## Actors

Supervisor Unit, Case Handler (menerima/menolak sesuai kebijakan), Petugas Regional, Petugas Kantor Pusat, System (auto-route bila dikonfigurasi), Administrator (matriks skill/unit)

## Preconditions

1. Case ada dan status mengizinkan assignment (`CREATED`, `ASSIGNED`, `IN_PROGRESS`, `PENDING`, `ESCALATED` sesuai konfigurasi).
2. Aktor punya hak assign/reassign pada lingkup unit.
3. Assignee target aktif di User Directory dependency dan memiliki role ECMP yang relevan.
4. Organization unit target valid.

## Trigger

Assign pertama, reassignment, claim dari queue, auto-routing, atau assignment sebagai bagian eskalasi.

## Normal Flow

1. Aktor memilih Case.
2. Aktor memilih assignee (user) dan/atau queue unit.
3. Sistem memvalidasi kelayakan role & unit.
4. Sistem menutup assignment aktif sebelumnya (jika ada) dengan timestamp akhir.
5. Sistem membuka assignment baru dengan timestamp mulai, status `ACTIVE`.
6. Status Case menjadi `ASSIGNED` atau tetap `IN_PROGRESS` sesuai state machine.
7. SLA clock mengikuti aturan BR-006 (mis. start on first assign).
8. Timeline + Audit + Assignment History ditulis.
9. Notifikasi ke assignee baru dan (opsional) assignee lama.

## Alternative Flow

### A1 — Claim dari queue

Handler mengambil Case dari antrian unit; sistem meng-assign ke dirinya jika kebijakan claim mengizinkan.

### A2 — Bulk reassignment terbatas

Supervisor memindahkan sejumlah Case antar handler dalam unit yang sama; setiap Case tetap punya jejak sendiri.

### A3 — Assignment saat eskalasi

Assignee berpindah ke petugas/queue Regional atau Pusat; Assignment History mencatat sebab `ESCALATION`.

### A4 — Unassign ke queue

Case kembali ke antrian tanpa assignee individu; tetap tercatat.

## Exception Flow

### E1 — Assign ke user tidak berwenang / non-aktif

Ditolak.

### E2 — Assign lintas unit tanpa hak

Ditolak; arahkan ke jalur eskalasi formal (BR-007) bila dimaksudkan sebagai eskalasi.

### E3 — Case sudah RESOLVED/CLOSED

Ditolak kecuali reopen alur terkait.

### E4 — Double-claim race

Hanya satu claim yang menang; yang lain mendapat pesan bisnis “sudah diambil”.

## Business Validation

Assignee wajib dapat diidentifikasi melalui identity eksternal yang dipetakan; unit wajib ada; alasan reassignment wajib pada kebijakan tertentu (mis. reassign > N kali).

## Business Constraints

1. Tidak ada assignment level Complaint.
2. Assignment History tidak boleh dihapus atau diedit isinya.
3. Eskalasi tidak boleh “menghilangkan” siapa sebelumnya mengerjakan Case.
4. Auto-route harus configuration-first dan diaudit setara assignment manual.

## Data Affected

Assignment aktif & history; Case status; possibly SLA start; Timeline; Audit; queue membership.

## Notifications

Assignee baru, Supervisor, Assignee sebelumnya (konfigurasi).

## Audit Trail

Assign / Reassign / Claim / Unassign dengan from-to, alasan, aktor, waktu.

## Security Considerations

Cegah privilege escalation melalui assignment ke unit lebih tinggi tanpa BR-007; pantau self-assign massal.

## KPI Impact

- Time to First Assignment
- Reassignment rate
- Workload per handler/unit
- % Case unassigned aging

## Future Enhancement

Skill-based routing; capacity-aware distribution; sticky assignment rules per kategori.

---


# BR-006 — Working Day SLA

## Nama Rule

Working Day SLA

## Purpose

Mengukur dan menegakkan target penyelesaian Case berdasarkan **hari kerja (Working Day)** yang dapat dikonfigurasi melalui SLA Policy, sehingga kinerja operasional adil terhadap kalender kerja organisasi dan tetap auditabel.

> **Mode A / governance baseline (alignment):** This rule body is **target catalog** content. Mode A **SHALL NOT** treat Working Day countdown/enforcement as active. Mode A = bind SLA Policy Version **without** countdown (BQ-005 / BR-SLA-002). Baseline calendar = **24×7** (BR-SLA-003 / BC-6.5). Working Day / pause / case-type differentiation = **Deferred** (BR-SLA-004). No countdown logic is introduced or activated by this alignment note.

## Business Description

SLA melekat pada **Case**, bukan Complaint. Satu Complaint dengan beberapa Case memiliki jam SLA independen per Case. Perhitungan Working Day mengikuti keputusan domain yang dikunci:

- Sabtu **tidak** dihitung.
- Minggu **tidak** dihitung.
- Hari Libur resmi **tidak** dihitung (sumber: Calendar Platform eksternal).
- Senin–Jumat dihitung sebagai Working Day, kecuali tanggal tersebut adalah hari libur.

Administrator mengubah nilai target melalui **SLA Policy** (configuration-first), lengkap dengan versioning dan effective date agar histori Case lama tetap dapat dijelaskan dengan policy yang berlaku saat SLA instance dibuat.

SLA History mencatat start, pause, resume, breach, dan stop. Seluruh SLA History ikut dalam Escalation Package (BR-007) — No Information Lost.

## Actors

Administrator (kebijakan), System (kalkulasi), Supervisor/Handler (melihat status), Operations Lead (governance target), Calendar Platform (sumber hari libur)

## Preconditions

1. Case telah dibuat dan terikat ke versi SLA Policy yang aktif untuk kombinasi tipe/kategori/prioritas/unit (sesuai matriks kebijakan).
2. Calendar Platform tersedia untuk resolusi hari libur pada zona kalender yang dikonfigurasi.
3. Trigger mulai SLA telah didefinisikan pada policy (contoh: on Case Created, on First Assignment, on In Progress).
4. Jam operasional harian (bila policy memakai working hours selain full working day) tersedia pada konfigurasi; bila policy “full working day”, satu hari kerja dihitung utuh menurut aturan hari.

## Trigger

- Event bisnis yang dikonfigurasi sebagai SLA start
- Perubahan status yang mem-pause/resume (mis. PENDING menunggu pelanggan)
- Job penandaan mendekati breach / breach
- Perubahan assignment/eskalasi yang mempengaruhi ownership tetapi **tidak** menghapus jam yang sudah berjalan kecuali policy menyatakan reset (default: tidak reset pada eskalasi — petugas pusat melanjutkan, bukan mengulang)

## Normal Flow

1. Saat trigger start terpenuhi, sistem membuat **SLA Instance** pada Case dengan: policyId, policyVersion, targetWorkingDays, startTimestamp, status `RUNNING`.
2. Sistem menghitung **due datetime** dengan menambahkan N Working Day dari Calendar Platform, mengabaikan Sabtu, Minggu, dan hari libur.
3. Sepanjang Case berjalan, sistem memelihara sisa Working Day / indikator on-track.
4. Bila Case masuk status pause yang dikonfigurasi (mis. menunggu dokumen pelanggan), SLA status `PAUSED`; waktu pause tidak memakan Working Day.
5. Saat resume, status kembali `RUNNING`; due date digeser sesuai sisa.
6. Saat Case `RESOLVED`/`CLOSED` sesuai aturan stop, SLA `COMPLETED` dengan hasil `MET` atau `BREACHED`.
7. Setiap perubahan signifikan menulis SLA History + Timeline + Audit.
8. Bila mendekati ambang peringatan (mis. 80% waktu), Notification Platform diberi permintaan notifikasi.

## Alternative Flow

### A1 — Administrator mengubah SLA Policy

Policy baru berlaku untuk Case **baru** atau Case yang belum start, sesuai effective date. Case berjalan tetap memakai versi yang terikat saat start (Maintainable + Auditability), kecuali ada aksi khusus “rebind policy” berjustifikasi yang jarang dan diaudit ketat.

### A2 — Hari libur ditambahkan setelah SLA start

Calendar Platform menambahkan libur; kalkulasi sisa/due mengikuti kalender terkini untuk hari yang belum berlalu; hari yang sudah terhitung di masa lalu tidak ditulis ulang secara destruktif tanpa jejak. Rekalkulasi wajib meninggalkan SLA History event `RECALCULATED`.

### A3 — Multi-SLA pada satu Case

Beberapa milestone (first response vs resolution) bila dikonfigurasi; masing-masing instance terpisah, tetap pada level Case.

### A4 — Eskalasi

SLA tetap berjalan (default) agar pusat melihat sisa waktu yang sama; Assignment berubah; SLA History mencatat `ESCALATED_CONTEXT` tanpa menghapus pengukuran sebelumnya.

## Exception Flow

### E1 — Calendar Platform down

Sistem tidak boleh mengarang hari libur. Opsi: tahan start SLA dengan flag, atau pakai cache kalender terakhir yang disetujui operasi, dengan penanda degraded. Breach decision yang ragu wajib ditandai untuk review Operations.

### E2 — Tidak ada SLA Policy cocok

Case boleh dibuat tetapi ditandai `SLA_UNBOUND`; Supervisor wajib menindak; KPI memisahkan Case unbound.

### E3 — Upaya mengedit manual due date tanpa wewenang

Ditolak. Adjustment hanya lewat aksi “SLA Adjustment” berwewenang + alasan + audit.

### E4 — Stop SLA pada status tidak sah

Ditolak; mencegah manipulasi MET/BREACHED.

## Business Validation

| Validasi | Aturan |
|---|---|
| Target | Working Day > 0 menurut policy |
| Kalender | Sabtu/Minggu/libur excluded |
| Binding | policyVersion wajib tersimpan |
| Pause reason | Wajib saat pause |
| Adjustment | Wajib alasan dan role khusus |

## Business Constraints

1. SLA tidak dihitung di level Complaint Aggregate.
2. Default eskalasi **tidak** mereset SLA (No Duplicate Work / tidak mengulang pekerjaan cabang dari sisi waktu).
3. Hasil MET/BREACHED immutable setelah close Case, kecuali koreksi formal beraudit.
4. Working Day enforcement is **Deferred** for Mode A (BR-SLA-004). Baseline calendar for Mode A interpretation is **24×7** (BR-SLA-003). Catalog text below that describes Working Day exclusion of weekends/holidays is **not** Mode A mandatory force until a Business Owner DEC activates Working Day calendars. Mode A delivery remains bind-without-clock (BQ-005).

## Data Affected

SLA Instance, SLA History, Case indicators, Timeline, Audit, feed KPI (BR-019), Reporting (BR-020)

## Notifications

Peringatan mendekati due; notifikasi breach ke Supervisor/assignee; notifikasi adjustment.

## Audit Trail

Start/pause/resume/breach/complete/recalculate/adjust dengan before-after due, policy version, aktor (system atau human).

## Security Considerations

Hanya role berwenang yang boleh adjust; cegah backdating due date untuk menutup breach.

## KPI Impact

Langsung ke: % SLA Met, Average Remaining WD, Breach count by unit/category, Pause ratio, Escalated-but-still-MET.

## Future Enhancement

Working hours intra-day; multi-calendar per region; customer-promised date terpisah dari SLA internal.

---

# BR-007 — Escalation

## Nama Rule

Escalation

## Purpose

Memindahkan Case ke tingkat penanganan yang lebih tinggi (**Kantor Pusat / Head Office** pada jalur Branch ↔ Head Office) **beserta seluruh informasi terkait**, sehingga petugas penerima melanjutkan pekerjaan cabang — bukan mengulang dari nol — sesuai prinsip **NO INFORMATION LOST DURING ESCALATION**.

> **DEC-F4 qualification (alignment; BC-7.3 / BR-ESC-003):** Detailed visibility, return (`return_reason_code` / `return_note`), and result-audience (`result_visibility`) rules from DEC-F4 are **workshop/catalog content**. They are **not** elevated to Mode A Business Rules force until Architecture Board countersign is complete (DL-012 PENDING). **Path scope** Branch ↔ Head Office remains binding (BR-ESC-002). Mode A delivery surface does **not** expose `PENDING`/`ESCALATED` (BQ-009). Do not read the F4 subsections below as mandatory Mode A delivery obligations.

## Business Description

Escalation adalah perpindahan tanggung jawab operasional Case ke jenjang organisasi yang lebih tinggi atau unit eskalasi yang dikonfigurasi. Yang berpindah bukan sekadar “tiket kosong”, melainkan **Escalation Package** lengkap:

- Timeline
- Assignment History
- Escalation History
- Internal Note
- External Note
- Communication History
- Attachment
- Dokumen
- Foto
- Video
- Resolution History
- SLA History
- Audit Trail

Tidak boleh ada informasi yang hilang, tersembunyi tanpa alasan keamanan yang sah, atau diarsipkan terpisah sehingga petugas pusat tidak melihatnya. Masking field sensitif tetap boleh diterapkan menurut role, tetapi artefak tetap ada dan dapat diakses oleh role yang berhak di jenjang tujuan.

Complaint Aggregate tetap sama; Case tetap identitas yang sama (tidak membuat Case baru hanya karena eskalasi, kecuali kebijakan split eksplisit). Ini menjaga Full Traceability dan Single Source of Truth.

### Jalur eskalasi yang dikunci (DEC-F4 / F4.1) — provisional detail

Untuk penerapan yang mengikuti DEC-F4 **after** formal countersign (until then: path Branch↔HO binds; F4 detail Reserved):

- Jalur operasional = **Cabang → Pusat** saja.
- **Regional tidak** menjadi target eskalasi pada jalur ini (UI/API tidak menawarkan Regional).
- Model visibilitas kerja Pusat = **F4 opsi B**: handler Pusat hanya mengerjakan Case yang dieskalasikan/di-assign ke Pusat; role analyst/viewer Pusat boleh melihat KPI/monitoring lintas cabang tanpa akses detail default ke Case cabang yang belum dieskalasikan.

Enterprise Platform tetap boleh memiliki unit Regional untuk modul lain; kebijakan ini hanya mengikat **jalur eskalasi Complaint** per DEC-F4.

## Actors

Supervisor Unit / Cabang (asal), Petugas/Supervisor Kantor Pusat, System, Administrator (matriks jalur eskalasi; katalog `return_reason_code`)

## Preconditions

1. Case aktif dan belum CLOSED.
2. Alasan eskalasi termasuk katalog alasan yang dikonfigurasi atau free-text wajib.
3. Jalur eskalasi aktif: **Cabang → Pusat** (DEC-F4). Jalur bertahap melibatkan Regional hanya jika konfigurasi di luar DEC-F4 diaktifkan secara eksplisit (lihat A1).
4. Aktor asal berwenang mengeskalasikan; atau auto-escalation rule terpenuhi (SLA breach, idle time, kategori kritikal).
5. Unit tujuan (Pusat) siap menerima (queue aktif).

## Trigger

Manual oleh Supervisor/Handler berwenang; otomatis oleh System berdasarkan rule (breach, aging, kategori); permintaan naik dari pelanggan yang disetujui kebijakan.

## Normal Flow

1. Aktor memilih Case dan aksi Eskalasi.
2. Aktor memilih target **Pusat** (DEC-F4) dan mengisi alasan + ringkasan konteks (wajib).
3. Sistem menyusun Escalation Package dari seluruh artefak Case dan konteks Complaint yang relevan.
4. Sistem memvalidasi kelengkapan package (checklist No Information Lost).
5. Sistem menulis Escalation History (from, to, reason, timestamp, aktor).
6. Sistem menjalankan Assignment ke queue/handler tujuan (BR-005) dengan sebab ESCALATION.
7. Status Case menjadi `ESCALATED` (dan/atau `ASSIGNED` di unit baru sesuai state machine).
8. SLA History mencatat peristiwa eskalasi; jam SLA default berlanjut (BR-006).
9. Timeline menampilkan peristiwa eskalasi secara menonjol.
10. Audit Trail mencatat eskalasi dan checksum/manifest package (daftar artefak yang ikut).
11. Notification Platform memberitahu pihak asal dan tujuan.
12. Petugas Pusat membuka Case dan melihat **seluruh** history; melanjutkan pekerjaan.
13. Cabang asal menjadi **read-only** pada Case selama ownership di Pusat (F4-OQ-02).

## Alternative Flow

### A1 — Eskalasi bertahap Unit → Regional → Pusat *(di luar jalur DEC-F4)*

Hanya berlaku jika konfigurasi enterprise di luar DEC-F4 mengaktifkan Regional. Setiap tahap menambah Escalation History; package tetap kumulatif. **Default DEC-F4: tidak digunakan.**

### A2 — Auto-escalation karena SLA Breach

System memicu tanpa menunggu Supervisor; alasan sistem tercatat; Supervisor asal tetap dinotifikasi.

### A3 — Eskalasi dengan permintaan guidance (bukan transfer penuh)

Jika kebijakan mendukung “consult”, Case tetap di unit asal tetapi catatan konsultasi tercatat; ini **bukan** pengganti transfer package. Transfer penuh tetap memakai rule ini.

### A4 — De-escalation / pengembalian (DEC-F4 / F4.4 / F4.5)

Pusat **wajib dapat mengembalikan** Case ke **cabang asal** jika kelengkapan/informasi kurang.

Aturan:

1. Hanya untuk Case yang sedang dimiliki Pusat (setelah eskalasi ke Pusat).
2. Target return = cabang asal yang mengeskalasikan (`returned_to_branch_id`); bukan cabang lain; bukan Regional.
3. Field wajib:
   - `return_reason_code` — enum terkendali (katalog Administrator; baseline DEC-F4: `MISSING_ATTACHMENT`, `INCOMPLETE_CHRONOLOGY`, `UNCLEAR_CUSTOMER_DATA`, `WRONG_CATEGORY_OR_ROUTING`, `ADDITIONAL_EVIDENCE_REQUIRED`, `OTHER`)
   - `return_note` — catatan bebas wajib; **minimum 10 karakter setelah trim** (F4-OQ-01 Closed)
4. Escalation History append-only: kerja Pusat + alasan return tetap terlihat; tidak menghapus artefak.
5. Ownership kembali ke cabang asal; Case keluar dari work queue handler Pusat sampai dieskalasikan lagi.
6. Selama Case dimiliki Pusat, cabang asal **read-only**; setelah Return, write dikembalikan (F4-OQ-02 Closed).
7. Return **bukan** Resolve: **tidak** meng-set `result_visibility` (lihat BR-008 / DEC-F4).
8. Notifikasi ke cabang asal dan assignee terkait.
9. Cabang boleh melengkapi lalu escalate ulang; package kumulatif (No Information Lost).

## Exception Flow

### E1 — Package tidak lengkap (deteksi selisih artefak)

Eskalasi ditolak atau ditahan sampai konsistensi dipulihkan. Dilarang mengirim Case “kosong”. Setelah Case sudah di Pusat, ketidaklengkapan yang ditemukan petugas ditangani lewat **A4 Return**, bukan dengan menghapus history.

### E2 — Target tidak valid / tidak berwenang menerima kategori

Ditolak. Termasuk upaya memilih Regional pada konfigurasi DEC-F4.

### E3 — Eskalasi dari Case CLOSED

Ditolak; gunakan reopen bila perlu.

### E4 — Upaya membuat Complaint/Case baru sebagai ganti eskalasi

Melanggar No Duplicate Work; sistem mengarahkan ke eskalasi formal.

### E5 — Kegagalan notifikasi

Tidak membatalkan eskalasi yang sudah commit; wajib retry di Notification Platform.

### E6 — Return tanpa `return_reason_code` atau tanpa `return_note`

Ditolak (DEC-F4 / F4.5).

## Business Validation

Alasan eskalasi wajib; target wajib (Pusat pada DEC-F4); konfirmasi checklist package; hak aktor; Case status valid. Untuk Return: `return_reason_code` + `return_note` wajib.

## Business Constraints

1. **NO INFORMATION LOST DURING ESCALATION** — constraint keras.
2. Identitas Case dan Complaint tidak berubah karena eskalasi atau return.
3. Escalation History append-only.
4. Petugas pusat wajib dapat melihat kerja cabang sebelumnya.
5. Attachment media (foto/video/dokumen) termasuk package, bukan hanya metadata kosong.
6. Internal notes tetap terlihat oleh role internal yang berhak di tujuan; external notes tetap dalam jejak komunikasi.
7. **DEC-F4:** jalur Cabang → Pusat; handler Pusat scoped ke Case escalated; Return ke cabang asal dengan kode alasan + catatan bebas.

## Data Affected

Escalation History; Assignment; Case status/unit; Timeline; Audit; manifest package; possibly KPI escalation counters; field return (`return_reason_code`, `return_note`, `returned_to_branch_id`).

## Notifications

Unit asal, unit tujuan, assignee terkait, opsional Management untuk kategori kritikal; pada Return — cabang asal dan assignee terkait.

## Audit Trail

EscalationRequested/Completed/Rejected/Returned + manifest artefak + alasan + jalur; untuk Returned: `return_reason_code`, `return_note`, aktor, timestamp.

## Security Considerations

Hak akses di unit tujuan harus cukup untuk membaca package; data sensitif tetap dimask untuk role yang tidak perlu; transfer lintas jenjang tidak boleh melemahkan audit. Visibilitas lintas cabang setelah Resolve diatur BR-008 (`result_visibility`), bukan oleh Return.

## KPI Impact

Escalation rate; time-in-tier; % escalated after breach; resolution after escalation; repeat escalation; return rate; reason-code distribution.

## Future Enhancement

Warm transfer dengan joint session; escalation playbook per kategori; quality score kelengkapan package; aktivasi jalur Regional hanya melalui keputusan konfigurasi/DEC terpisah.

---

# BR-008 — Resolution

## Nama Rule

Resolution

## Purpose

Menetapkan cara resmi menutup siklus kerja Case melalui resolusi yang lengkap, dapat dibuktikan, tertelusur, dan siap menjadi dasar penutupan Complaint — tanpa menghilangkan riwayat upaya sebelumnya.

## Business Description

Resolution adalah pernyataan hasil penanganan pada level **Case**: akar masalah (bila wajib), tindakan yang dilakukan, hasil bagi pelanggan, evidence, dan kode resolusi dari katalog. Satu Case dapat memiliki Resolution History (usulan, revisi, rejection, acceptance). Resolution final yang diterima menjadi prasyarat Case `RESOLVED`/`CLOSED` dan berkontribusi pada keputusan Complaint Closure (BR-009).

Prinsip: No Duplicate Work — resolusi memanfaatkan Timeline, komunikasi, dan work notes yang sudah ada; bukan memaksa petugas menulis ulang seluruh kronologi (cukup ringkasan resolusi + referensi).

### Visibilitas hasil setelah Resolve oleh Pusat (DEC-F4 / F4.2 / F4.3 / F4.3a)

> **Reserved for Mode A BR force** until DEC-F4 countersign (BR-ESC-003). Catalog retention only.

Jika Case diselesaikan oleh **Kantor Pusat** (setelah eskalasi):

1. **Cabang asal selalu** boleh membaca hasil resolusi dan history yang diizinkan role (**F4.2**).
2. Pada aksi Resolve, Pusat menetapkan `result_visibility`:
   - `ORIGIN_BRANCH` — hanya cabang asal (+ Pusat) yang boleh melihat hasil; cabang lain tidak menemukan Case di search/list/detail.
   - `ALL_BRANCHES` — semua cabang (role complaint yang berwenang) boleh **read-only** melihat hasil dan history yang diizinkan.
3. Default sistem jika tidak dipilih eksplisit: **`ORIGIN_BRANCH`**. UI Pusat sebaiknya meminta pemilihan eksplisit.
4. Setelah Resolve, Pusat **boleh mengubah** `result_visibility` kemudian (**F4.3a**); setiap perubahan wajib Audit Trail (`from`, `to`, `changed_by`, `changed_at`, opsional `change_note`).
5. Return/de-escalation (BR-007 A4) **tidak** meng-set `result_visibility`.

## Actors

Case Handler (menyusun), Supervisor (review/approve bila wajib), Petugas Pusat, System (validasi kelengkapan), Administrator (katalog kode resolusi)

## Preconditions

Case dalam status yang mengizinkan resolusi (`IN_PROGRESS`, `ESCALATED`, `PENDING` selesai, dsb.); aktor adalah assignee atau Supervisor berwenang; katalog resolusi aktif; evidence policy untuk kategori diketahui. Untuk Resolve oleh Pusat setelah eskalasi: aktor berwenang set `result_visibility`.

## Trigger

Aktor memilih “Ajukan Resolusi” / “Selesaikan Case”.

## Normal Flow

1. Aktor mengisi kode resolusi, ringkasan, detail tindakan, dampak pelanggan, evidence (jika wajib).
2. Jika Resolve dilakukan oleh Pusat pada Case hasil eskalasi: aktor menetapkan `result_visibility` (`ORIGIN_BRANCH` \| `ALL_BRANCHES`) — DEC-F4.
3. Sistem memvalidasi kelengkapan menurut kategori/tipe Case.
4. Bila approval wajib, status usulan `PENDING_APPROVAL`; Supervisor mereview.
5. Jika disetujui, Resolution menjadi `ACCEPTED`; Case → `RESOLVED`; SLA stop (BR-006); `result_visibility` tersimpan (bila berlaku).
6. Resolution History, Timeline, Audit ditulis.
7. Notifikasi sesuai konfigurasi (termasuk cabang asal bahwa hasil tersedia).
8. Sistem mengevaluasi apakah semua Case pada Complaint sudah resolved untuk usulan closure (BR-009).

## Alternative Flow

### A1 — Resolusi ditolak Supervisor

Kembali ke pengerjaan; alasan rejection wajib; history tersimpan.

### A2 — Resolusi parsial / workaround

Kode khusus; Case mungkin `RESOLVED` dengan flag follow-up Case baru pada Complaint yang sama.

### A3 — Multi-attempt

Beberapa entri Resolution History sebelum yang final; tidak menimpa entri lama.

### A4 — Ubah `result_visibility` setelah Resolve (DEC-F4 / F4.3a)

Aktor Pusat berwenang mengubah `ORIGIN_BRANCH` ↔ `ALL_BRANCHES`. Efek segera pada otorisasi search/list/detail cabang lain. Audit wajib. Tidak mengubah isi Resolution History.

## Exception Flow

### E1 — Evidence wajib hilang

Ditolak.

### E2 — Case belum punya assignment history yang memadai menurut kebijakan

Peringatan atau tolakan (cegah “resolve tanpa kerja”).

### E3 — Menyelesaikan Case orang lain tanpa hak

Ditolak.

### E4 — Resolve Pusat tanpa `result_visibility` dan tanpa default

Ditolak, atau sistem menerapkan default `ORIGIN_BRANCH` sesuai konfigurasi (DEC-F4 merekomendasikan pemilihan eksplisit di UI + default aman).

## Business Validation

Kode resolusi valid; ringkasan wajib; evidence sesuai tipe; approval bila policy mengharuskan; untuk Resolve Pusat: `result_visibility` valid.

## Business Constraints

Resolution History tidak dihapus; resolusi final terikat Case; eskalasi membawa Resolution History; Complaint tidak “resolved” hanya karena satu Case selesai jika Case lain masih terbuka (kecuali kebijakan partial closure yang eksplisit — default: belum). Setelah Resolve Pusat, cabang asal selalu read-capable terhadap hasil; perluasan ke semua cabang hanya via `ALL_BRANCHES`.

## Data Affected

Resolution + history; Case status; SLA; Timeline; Audit; feed closure; KPI; `result_visibility` (+ history perubahan visibility).

## Notifications

Assignee, Supervisor, Agent pencatat Complaint / cabang asal, opsional pelanggan via kanal (melalui Notification Platform).

## Audit Trail

ResolutionProposed/Approved/Rejected/Finalized; ResultVisibilitySet/Changed (`from`, `to`, aktor, timestamp).

## Security Considerations

Evidence dapat berisi data sensitif; akses terbatas; retensi mengikuti kebijakan compliance. Enforcement `result_visibility` wajib di search, list, detail, dan export.

## KPI Impact

First Time Resolution; rework after reject; resolution codes distribution; time to resolve; distribution `ORIGIN_BRANCH` vs `ALL_BRANCHES`.

## Future Enhancement

Structured root-cause taxonomy; customer confirmation step sebelum finalize.

---

# BR-009 — Complaint Closure

## Nama Rule

Complaint Closure

## Purpose

Menutup Aggregate Complaint secara sah hanya ketika kewajiban operasional terhadap pelanggan pada seluruh Case terkait telah selesai, dengan jejak lengkap untuk audit dan pelaporan.

## Business Description

Closure adalah status akhir bisnis Complaint (`CLOSED`). Karena Complaint dapat berisi banyak Case, penutupan Complaint adalah keputusan Aggregate: umumnya seluruh Case harus `CLOSED`/`RESOLVED` sesuai kebijakan, resolusi tersedia, komunikasi penutup tercatat bila wajib, dan tidak ada item wajib yang outstanding (attachment wajib, approval, dsb.).

Closure bukan penghapusan. Seluruh history tetap ada untuk Customer 360, Audit, Reporting.

## Actors

Supervisor (utama), Agent (bila dikonfigurasi untuk closure sederhana), System (auto-close bila semua Case closed dan policy mengizinkan), Compliance (review sampel)

## Preconditions

1. Complaint tidak sedang `CLOSED`.
2. Semua Case aktif memenuhi kondisi penutupan (default: tidak ada Case open).
3. Minimal satu Resolution final pada Case yang relevan, atau pengecualian beralasan (Complaint dibatalkan sebelum Case — jarang).
4. Aktor berwenang close.
5. Cek duplicate linkage selesai (tidak meninggalkan possible-duplicate menggantung tanpa keputusan, bila policy mewajibkan).

## Trigger

Aksi “Tutup Complaint”, atau auto-close rule.

## Normal Flow

1. Sistem mengevaluasi checklist closure Aggregate.
2. Aktor mengisi ringkasan penutupan dan kode closure.
3. Sistem menetapkan Complaint `CLOSED`, timestamp, closedBy.
4. Menulis Timeline, History, Audit.
5. Menonaktifkan create Case baru kecuali reopen.
6. Notifikasi pihak terkait.
7. Feed KPI/Reporting.

## Alternative Flow

### A1 — Close dengan Case cancelled

Jika Case dibatalkan sebelum kerja, policy menentukan apakah Complaint boleh closed sebagai `CANCELLED_COMPLAINT` atau setara.

### A2 — Soft close menunggu konfirmasi pelanggan

Status antara `RESOLVED` di Aggregate menunggu window konfirmasi; setelah timeout tanpa sanggahan → `CLOSED`.

## Exception Flow

### E1 — Masih ada Case open

Ditolak dengan daftar Case penghambat.

### E2 — Evidence/resolusi kurang

Ditolak.

### E3 — Close tanpa wewenang

Ditolak + audit keamanan.

## Business Validation

Checklist Aggregate; kode closure valid; alasan wajib pada exception path.

## Business Constraints

Tidak hard-delete; reopen hanya lewat BR-015; closure tidak menghapus SLA History/Audit; CustomerId tetap.

## Data Affected

Complaint status; History; Timeline; Audit; search index; dashboard open count.

## Notifications

Agent, Supervisor, opsional pelanggan.

## Audit Trail

ComplaintClosed dengan checklist snapshot.

## Security Considerations

Setelah closed, write terbatas; read tetap role-based.

## KPI Impact

Cycle time Complaint; open backlog; reopen rate (terkait BR-015); closure quality.

## Future Enhancement

Customer satisfaction capture at closure; multi-level closure approval untuk kategori kritikal.

---

# BR-010 — Customer 360 View

## Nama Rule

Customer 360 View

## Purpose

Memberikan pandangan terpadu dan read-oriented tentang pelanggan dalam konteks Complaint Management agar petugas mengambil keputusan tanpa menggandakan data master dan tanpa kehilangan konteks interaksi.

## Business Description

Setiap Complaint memiliki akses ke **Customer 360 View** untuk `CustomerId` terkait. Tampilan menggabungkan:

1. Profil Customer (dari Master Customer, read-only)
2. Complaint Aktif
3. Riwayat Complaint
4. Riwayat Case
5. Riwayat Resolusi
6. Riwayat Eskalasi
7. Attachment History
8. Statistik Complaint

ECMP memperkaya 360 dengan data operasional miliknya; Master tetap SoR profil. 360 mendukung Create (BR-001), Search (BR-003), penanganan Case, dan pencegahan duplikat (BR-014).

## Actors

Agent, Handler, Supervisor, Regional, Pusat, System (compose read-model)

## Preconditions

CustomerId diketahui; aktor berwenang melihat 360; Master dapat dipanggil atau cache valid; data operasional ECMP accessible sesuai scope.

## Trigger

Buka dari Complaint, dari pencarian pelanggan, dari Case, atau dari hasil validasi pelanggan.

## Normal Flow

1. Sistem mengambil profil Master (atau cache).
2. Sistem mengumpulkan data operasional ECMP terkait CustomerId dalam lingkup hak.
3. Sistem menampilkan bagian-bagian 360 secara terstruktur.
4. Aktor menavigasi ke Complaint/Case detail tanpa meninggalkan jejak konteks pelanggan.
5. Statistik dihitung dari sumber operasional (bukan angka manual).

## Alternative Flow

### A1 — Master unavailable

Tampilkan bagian operasional ECMP + penanda profil stale/unavailable.

### A2 — Masking

Role non-frontline melihat kontak tersembunyi.

### A3 — Multi-Complaint aktif

Sorot semua aktif untuk mencegah duplikat dan mendorong Case baru pada Complaint yang tepat.

## Exception Flow

### E1 — Tanpa hak akses

Ditolak.

### E2 — Upaya edit profil dari 360

Ditolak (BR-002).

## Business Validation

CustomerId valid; section visibility by role; statistik reconcile-able.

## Business Constraints

Read-only terhadap master; 360 bukan SoR; tidak menampilkan data luar lingkup org kecuali role enterprise; Attachment history mengikuti BR-012 security.

## Data Affected

Read-model/cache saja; audit akses.

## Notifications

Tidak ada (view).

## Audit Trail

Customer360Viewed (untuk akses sensitif).

## Security Considerations

Need-to-know; masking; cegah scraping melalui 360; pantau akses massal.

## KPI Impact

% handling dengan 360 dibuka; korelasi ke penurunan duplikat; time-to-context.

## Future Enhancement

Risk flags dari sistem eksternal; journey timeline lintas kanal; consent-aware display.

---


# BR-011 — Communication History

## Nama Rule

Communication History

## Purpose

Menjamin setiap interaksi komunikasi terkait Complaint/Case tercatat lengkap, dapat ditelusuri, dan ikut berpindah utuh saat eskalasi, sehingga tidak ada pengulangan pertanyaan kepada pelanggan atau kehilangan konteks antar jenjang.

## Business Description

Communication History adalah jejak kronologis komunikasi yang berkaitan dengan penanganan keluhan: telepon ringkasan, email masuk/keluar, pesan portal, surat, dan ringkasan percakapan kanal lain yang diakui. Setiap entri tertaut ke Complaint dan, bila relevan, ke Case spesifik.

Communication History berbeda dari Comment/Note internal (BR-013): komunikasi menekankan interaksi dengan pihak eksternal (pelanggan atau pihak terkait pelanggan), meskipun salinan atau ringkasan dapat terlihat internal. Saat eskalasi, **seluruh** Communication History termasuk Escalation Package (BR-007).

Prinsip: Full Traceability, No Duplicate Work (petugas pusat membaca history sebelum menghubungi pelanggan ulang), Auditability.

## Actors

Agent, Case Handler, Supervisor, Petugas Regional/Pusat, System (ingest dari kanal/Notification delivery log bila dikonfigurasi), Administrator (tipe komunikasi)

## Preconditions

Complaint ada; aktor berwenang menambah/melihat komunikasi pada lingkupnya; tipe komunikasi aktif; bila mengirim keluar, kanal keluar tersedia melalui dependency terkait.

## Trigger

Aktor mencatat komunikasi manual; sistem menerima inbound dari channel boundary; notifikasi keluar yang dikonfigurasi untuk dijejak sebagai komunikasi; eskalasi mereview history.

## Normal Flow

1. Aktor memilih Complaint/Case dan “Tambah Komunikasi”.
2. Aktor mengisi arah (inbound/outbound), kanal, waktu kejadian, lawan bicara, ringkasan, hasil, referensi pesan.
3. Sistem menautkan entri ke Complaint dan Case (opsional wajib menurut policy).
4. Sistem menulis Timeline event “Communication Logged”.
5. Audit mencatat siapa menambah entri.
6. Entri muncul di Communication History dan Customer 360 (sesuai hak).

## Alternative Flow

### A1 — Inbound otomatis dari kanal

Payload kanal membentuk entri dengan status “system-captured”; Agent dapat memperkaya ringkasan.

### A2 — Komunikasi tanpa Case spesifik

Dianchor ke Complaint saja bila belum ada Case atau bersifat umum.

### A3 — Koreksi ringkasan

Koreksi menambah revisi; entri asli tidak dihapus (append-only semantic).

## Exception Flow

### E1 — Menghapus komunikasi

Ditolak. Hanya “void” dengan alasan yang meninggalkan jejak.

### E2 — Mencatat pada Complaint CLOSED tanpa reopen

Ditolak atau terbatas pada catatan pasca-close sesuai policy (default tolak write operasional).

### E3 — Data sensitif berlebihan pada ringkasan

Peringatan kebijakan; field tertentu dapat dibatasi.

## Business Validation

Arah & kanal wajib; ringkasan wajib; timestamp tidak di masa depan tidak wajar; tautan Complaint wajib.

## Business Constraints

Append-only (void bukan delete); ikut eskalasi; tidak menggantikan Resolution; bukan media penyimpanan file besar (file ke BR-012 dengan tautan).

## Data Affected

Communication entries; Timeline; Audit; 360; Escalation Package contents.

## Notifications

Opsional ke assignee saat inbound baru.

## Audit Trail

CommunicationAdded/Voided/Revised.

## Security Considerations

Isi dapat berisi PII; masking pada role tertentu; retensi sesuai compliance; akses outbound history terbatas.

## KPI Impact

First response time (dari komunikasi); jumlah kontak ulang; % eskalasi tanpa komunikasi ulang ke pelanggan.

## Future Enhancement

Threading percakapan; sentimen ringkas; template komunikasi outbound terukur.

---

# BR-012 — Attachment Management

## Nama Rule

Attachment Management

## Purpose

Mengatur unggah, klasifikasi, versi, akses, dan retensi bukti pendukung (dokumen, foto, video, berkas lain) agar bukti tersedia sepanjang lifecycle dan tidak hilang saat eskalasi.

## Business Description

Attachment adalah artefak bukti yang ditautkan ke Complaint dan/atau Case. Jenis mencakup dokumen, foto, video, dan berkas lain yang diizinkan kebijakan. Attachment History mencatat siapa mengunggah, kapan, tipe, hash/integritas, dan status (aktif/void/superseded).

Keputusan domain mengunci bahwa Attachment — termasuk dokumen, foto, video — **wajib** ikut Escalation Package. Petugas pusat harus dapat membuka bukti yang sama dengan cabang.

ECMP mengelola metadata dan hak akses bisnis; penyimpanan biner dapat berada pada dependency storage enterprise, tetapi dari sudut bisnis Attachment tetap bagian jejak Complaint Management.

## Actors

Agent/Handler (upload), Supervisor (review), Regional/Pusat (akses setelah eskalasi), System (scan/validasi tipe), Administrator (policy tipe/ukuran), Compliance

## Preconditions

Objek anchor (Complaint/Case) ada dan mengizinkan upload; aktor berwenang; tipe MIME/ekstensi di allowlist; ukuran dalam batas; pemindaian keamanan dependency lulus bila diwajibkan.

## Trigger

Upload pada create/penanganan; permintaan evidence pada resolusi; ingest kanal; eskalasi memverifikasi keberadaan file.

## Normal Flow

1. Aktor memilih file dan klasifikasi (bukti pelanggan, bukti internal, surat resmi, dsb.).
2. Sistem validasi tipe/ukuran/nama.
3. Dependency keamanan memindai bila dikonfigurasi.
4. Sistem menyimpan metadata + referensi penyimpanan, status `ACTIVE`.
5. Attachment History & Timeline diperbarui.
6. Audit mencatat upload.
7. Attachment tampil di 360 (Attachment History) dan detail Case/Complaint.

## Alternative Flow

### A1 — Versi baru menggantikan

File baru menandai lama sebagai `SUPERSEDED`; lama tetap dapat diakses untuk audit.

### A2 — Upload wajib sebelum resolusi

BR-008 memanggil kelengkapan attachment kategori.

### A3 — Bulk upload terbatas

Beberapa file dalam satu aksi; masing-masing entri history.

## Exception Flow

### E1 — Tipe/ukuran ilegal

Ditolak.

### E2 — Scan gagal / malware

Ditolak; kejadian diaudit keamanan.

### E3 — Hapus fisik oleh user

Ditolak. Void dengan alasan; retensi mengikuti kebijakan legal hold.

### E4 — Akses tanpa hak

Ditolak; khususnya lampiran internal vs pelanggan.

## Business Validation

Allowlist tipe; max size; klasifikasi wajib; anchor wajib; virus scan status wajib sebelum `ACTIVE` bila policy on.

## Business Constraints

Tidak hilang saat eskalasi; history append-only; legal hold menahan void/purge; Complaint closure tidak menghapus attachment.

## Data Affected

Attachment metadata/history; Timeline; Audit; 360; Escalation manifest.

## Notifications

Opsional ke Supervisor saat evidence kritikal diunggah.

## Audit Trail

AttachmentUploaded/Superseded/Voided/Accessed (untuk sensitif).

## Security Considerations

Malware; DLP; enkripsi at-rest oleh platform storage; URL tidak boleh publik tanpa otorisasi; watermark kebijakan opsional.

## KPI Impact

% Case resolved dengan evidence lengkap; waktu tunggu kelengkapan dokumen; eskalasi karena bukti hilang (harus mendekati nol).

## Future Enhancement

OCR metadata; auto-classify dokumen; customer self-upload portal terintegrasi.

---

# BR-013 — Comment Management

## Nama Rule

Comment Management

## Purpose

Menyediakan mekanisme catatan kerja internal dan eksternal yang terstruktur agar kolaborasi antar petugas berjalan tanpa kehilangan konteks, dengan pemisahan jelas antara catatan internal dan catatan yang boleh diekspos ke jejak pelanggan/komunikasi.

## Business Description

Comment/Note mendukung kolaborasi pada Complaint/Case:

- **Internal Note**: hanya untuk petugas berwenang; berisi analisis, hipotesis, instruksi Supervisor, catatan risiko.
- **External Note**: catatan yang bersifat dapat dibagikan pada komunikasi/jejak eksternal atau ringkasan untuk pelanggan (bukan pengganti Communication History formal, tetapi dapat merujuknya).

Keduanya termasuk Escalation Package. Mengedit dilakukan sebagai revisi append-only atau marked edit dengan jejak, bukan silent overwrite yang menghilangkan teks lama bila kebijakan audit mengharuskan immutability konten.

## Actors

Handler, Supervisor, Regional, Pusat, Agent, System (auto-note untuk peristiwa tertentu)

## Preconditions

Anchor Complaint/Case ada; status mengizinkan comment; aktor punya hak internal dan/atau external note.

## Trigger

Aktor menambah catatan; Supervisor memberi instruksi; sistem menambah note otomatis pada peristiwa (assign, escalate) bila dikonfigurasi.

## Normal Flow

1. Aktor memilih jenis note (internal/external).
2. Menulis isi + opsional mention role/unit.
3. Sistem menyimpan, menampilkan di Timeline sebagai event “Note Added”.
4. Audit mencatat.
5. Penerima mention mendapat notifikasi (Notification Platform).

## Alternative Flow

### A1 — Catatan pada eskalasi

Wajib ringkas “handover note” selain alasan eskalasi.

### A2 — Pin note

Supervisor menyematkan note penting; tetap dalam history.

### A3 — Void note salah

Void + alasan; konten asli tertutup dari view operasional tetapi ada di audit bila diwajibkan.

## Exception Flow

### E1 — Menyimpan data master pelanggan sebagai “sumber baru” di note

Dilarang sebagai SoR; note boleh mengutip sementara tetapi BR-002 tetap berlaku.

### E2 — External note berisi instruksi internal sensitif

Validasi/peringatan; kebijakan dapat memblok kata kunci tertentu.

### E3 — Comment pada entitas closed

Default ditolak tanpa reopen.

## Business Validation

Jenis note wajib; isi tidak kosong; panjang maksimum; hak jenis note.

## Business Constraints

Internal ≠ External; ikut eskalasi; tidak menggantikan Resolution/Communication formal; append-only/void.

## Data Affected

Notes; Timeline; Audit; Escalation Package; notifikasi mention.

## Notifications

Mention; opsional Supervisor on escalation handover note.

## Audit Trail

NoteAdded/Voided/Pinned.

## Security Considerations

Internal notes lebih ketat; cegah kebocoran ke kanal pelanggan; pantau copy-paste massal PII.

## KPI Impact

Kualitas handover (subjektif/QA); pengurangan rework karena miss-context.

## Future Enhancement

Template note per kategori; checklist handover otomatis.

---

# BR-014 — Duplicate Complaint

## Nama Rule

Duplicate Complaint

## Purpose

Mencegah penggandaan Aggregate Complaint untuk keluhan yang sama secara substansial, mendorong penambahan Case pada Complaint existing, dan menjaga No Duplicate Work serta kualitas data operasional.

## Business Description

Duplicate detection membandingkan Complaint baru (atau kandidat) terhadap Complaint aktif/recent milik `CustomerId` yang sama dan/atau kemiripan atribut (kategori, subjek, rentang waktu, kanal). Hasilnya berupa skor dan daftar kandidat.

Respons bisnis:

1. **Peringatan** kepada Agent dengan opsi buka existing.
2. **Link possible-duplicate** bila tetap buat baru dengan justifikasi.
3. **Hard block** hanya jika policy kategori tertentu menyatakan wajib (jarang; default warning + justification).

Duplikat yang benar secara bisnis seringkali diselesaikan dengan **Create Case** pada Complaint yang sama (BR-004), bukan Create Complaint baru.

## Actors

Agent, Supervisor (override), System (scoring), Administrator (threshold/policy)

## Preconditions

CustomerId teridentifikasi atau kunci pencarian ada; indeks Complaint searchable; policy threshold aktif.

## Trigger

Sebelum konfirmasi Create Complaint; manual “cek duplikat”; berkala pada UNVERIFIED setelah verify.

## Normal Flow

1. Sistem mencari kandidat berdasarkan CustomerId + window waktu + kategori/kemiripan.
2. Menampilkan kandidat dengan status dan Case terbuka.
3. Agent memilih: batalkan create / lanjut dengan justifikasi / tambah Case ke existing.
4. Keputusan dicatat di Audit + History.

## Alternative Flow

### A1 — False positive

Override berjustifikasi; Complaint baru sah; ditandai reviewed.

### A2 — Merge keputusan bisnis

Tidak menghapus Aggregate; menautkan “related/duplicate of”; kerja dilanjutkan di survivor yang ditetapkan Supervisor. History kedua Aggregate tetap ada (No Information Lost).

### A3 — Duplikat lintas unit

Tetap ditampilkan bila hak memungkinkan; eskalasi/koordinasi mengikuti BR-007 bila perlu.

## Exception Flow

### E1 — Deteksi gagal (indeks down)

Create boleh lanjut dengan flag `duplicateCheckDegraded`; wajib review kemudian.

### E2 — Override tanpa justifikasi saat wajib

Ditolak.

## Business Validation

Threshold; window hari; field pembanding; justifikasi min length.

## Business Constraints

Tidak silent drop Complaint; tidak hard-delete “duplikat”; prefer Case baru vs Complaint baru; keputusan tertelusur.

## Data Affected

Link relasi duplicate/related; Audit; History; possibly block create.

## Notifications

Supervisor bila override sering / hard-block attempt.

## Audit Trail

DuplicateWarned/Overridden/Linked/ResolvedAsCaseOnExisting.

## Security Considerations

Hasil search tetap scoped; jangan bocorkan Complaint unit lain melebihi hak.

## KPI Impact

Duplicate rate; override rate; % converted to additional Case; rework.

## Future Enhancement

Model kemiripan teks terkendali; golden Complaint selection rules.

---

# BR-015 — Complaint Reopen

## Nama Rule

Complaint Reopen

## Purpose

Mengizinkan pembukaan kembali Complaint yang sudah ditutup dalam batas kebijakan yang ketat, agar isu yang muncul kembali tertangani pada Aggregate yang sama dengan Full Traceability, bukan membuat silo baru yang memutus sejarah.

## Business Description

Reopen mengubah Complaint `CLOSED` menjadi `REOPENED` lalu `IN_PROGRESS`, dengan alasan wajib dan window waktu sejak closure (nilai default enterprise dapat mengikuti kebijakan Administrator, misalnya 30 hari kalender — dapat dikonfigurasi). Reopen umumnya menciptakan **Case baru** untuk pekerjaan ulang, sambil mempertahankan seluruh Case/Resolution/Timeline lama (tidak dihapus, tidak di-reset seolah tidak pernah closed).

Ini mendukung No Duplicate Work dan No Information Lost: petugas melihat penutupan sebelumnya dan alasan reopen.

## Actors

Supervisor (utama), Agent (jika diizinkan terbatas), Regional/Pusat untuk Case yang sebelumnya dieskalasikan, Administrator (window & role matrix)

## Preconditions

Complaint `CLOSED`; masih dalam window reopen; aktor berwenang; alasan termasuk katalog atau free-text wajib; bukan legal hold yang melarang reopen write (jarang).

## Trigger

Keluhan pelanggan berulang; QA menemukan closure prematur; permintaan formal reopen; keputusan Ombudsman/internal escalate-after-close.

## Normal Flow

1. Aktor memilih Complaint closed dan aksi Reopen.
2. Mengisi alasan + referensi bukti.
3. Sistem validasi window & hak.
4. Status Complaint → `REOPENED`/`IN_PROGRESS`; mencatat `reopenedAt`, `reopenedBy`.
5. Sistem memicu Create Case penanganan ulang (BR-004) atau mengizinkan aktor memilih Case lama untuk dilanjutkan hanya jika policy mengizinkan (default: Case baru).
6. Timeline, History, Audit mencatat reopen dan menautkan ke closure sebelumnya.
7. Notifikasi ke unit terkait.
8. SLA Case baru dimulai menurut BR-006 (tidak menghapus SLA History Case lama).

## Alternative Flow

### A1 — Reopen di luar window

Hanya role tertinggi + justifikasi khusus + audit elevated; atau wajib buat Complaint baru bertaut related (policy).

### A2 — Reopen untuk koreksi administratif

Tanpa Case baru; hanya koreksi atribut penutupan — harus dibatasi ketat agar tidak disalahgunakan.

## Exception Flow

### E1 — Window habis tanpa elevated right

Ditolak.

### E2 — Reopen berulang melebihi ambang

Memerlukan approval tambahan; flag quality risk.

### E3 — Mencoba reopen dengan menghapus history closure

Ditolak keras.

## Business Validation

Alasan wajib; window; role; linkage ke closure event.

## Business Constraints

History closure tetap; Case lama tetap; SLA lama immutable; prefer reopen vs duplicate Complaint; ikut terlihat di 360.

## Data Affected

Complaint status; Case baru; Timeline; History; Audit; KPI reopen.

## Notifications

Assignee unit, Supervisor, Agent awal (opsional).

## Audit Trail

ComplaintReopened dengan alasan dan window evaluation.

## Security Considerations

Elevated reopen dilog khusus; cegah reopen massal.

## KPI Impact

Reopen rate; time-to-reopen; closure quality inverse indicator.

## Future Enhancement

Customer-initiated reopen request workflow; auto-link related tickets kanal.

---

# BR-016 — Audit Trail

## Nama Rule

Audit Trail

## Purpose

Menjamin setiap aktivitas bisnis signifikan pada Complaint Management tercatat secara lengkap, anti-rusak (immutable dari sudut bisnis modul), dan dapat diaudit lintas waktu — termasuk saat eskalasi dan setelah closure.

## Business Description

Audit Trail adalah fondasi Auditability dan Full Traceability. Untuk setiap aksi signifikan (create, validate, assign, escalate, resolve, close, reopen, ubah prioritas, void attachment, override duplikat, SLA adjust, dsb.), sistem menghasilkan catatan audit berisi siapa, apa, kapan, di mana (unit), objek, before/after ringkas, dan korelasi ke Complaint/Case.

ECMP menulis jejak bisnis audit modul. **Audit Platform** eksternal dapat menerima salinan/stream, tetapi ketiadaan platform eksternal tidak boleh membuat modul kehilangan jejak minimum yang diwajibkan rule ini. Penghapusan atau edit isi audit oleh Administrator modul **dilarang**.

Seluruh Audit Trail terkait Case/Complaint termasuk Escalation Package (minimal referensi/manifest yang memungkinkan petugas/auditor melihat jejak yang sama).

## Actors

System (penulis utama), semua aktor manusia (sumber peristiwa), Compliance/Auditor (pembaca), Administrator (tidak berhak hapus)

## Preconditions

Aksi signifikan terjadi; identitas aktor terpetakan dari Identity dependency; waktu sistem tepercaya.

## Trigger

Setiap write bisnis signifikan; selected sensitive reads (360, attachment); kegagalan otorisasi yang perlu diaudit.

## Normal Flow

1. Aksi bisnis divalidasi.
2. Perubahan data dan audit ditulis dalam satu konsistensi bisnis (tidak boleh sukses bisnis tanpa audit wajib).
3. Entri audit mendapat identifier dan tautan entity.
4. Tersedia untuk pencarian audit oleh role Compliance.

## Alternative Flow

### A1 — Emit ke Audit Platform

Selain simpan jejak modul, kirim salinan; kegagalan kirim diletakkan outbox bisnis/ops — tetap ada jejak lokal modul.

### A2 — System actor

Untuk auto-escalation/SLA breach, aktor = System dengan ruleId pemicu.

## Exception Flow

### E1 — Gagal tulis audit

Transaksi bisnis wajib gagal (untuk aksi yang mensyaratkan audit mandatory).

### E2 — Permintaan hapus audit

Ditolak.

### E3 — Clock skew mencurigakan

Tandai; jangan diam-diam menormalisasi tanpa jejak.

## Business Validation

Mandatory fields audit lengkap; action catalog dikenal; entity type dikenal.

## Business Constraints

Immutable; mandatory pada aksi list kritikal; ikut eskalasi (visibility); retensi panjang sesuai compliance; tidak berisi secret authentication.

## Data Affected

Audit records; outbox ke Audit Platform; laporan compliance.

## Notifications

Alert keamanan pada pola audit anomali (opsional Security).

## Audit Trail

Rule ini adalah pembuat audit; meta-audit perubahan konfigurasi audit policy juga wajib.

## Security Considerations

Akses baca audit terbatas; lindungi dari tampering; pisahkan log keamanan autentikasi (milik Identity) dari audit bisnis modul.

## KPI Impact

Audit completeness; % transactions with audit; temuan compliance.

## Future Enhancement

Cryptographic chaining; legal hold packages; advanced query for investigators.

---

# BR-017 — Timeline

## Nama Rule

Timeline

## Purpose

Menyajikan urutan peristiwa bisnis yang mudah dipahami manusia untuk satu Complaint dan Case-nya, sebagai tulang punggung pemahaman kronologi bagi petugas cabang maupun pusat.

## Business Description

Timeline adalah proyeksi kronologis peristiwa: created, validated customer, case added, assigned, communicated, commented, attached, escalated, SLA paused/breached, resolved, closed, reopened, dsb. Timeline bukan sekadar log teknis; ia adalah **bahasa operasional** yang harus dibaca petugas penerima eskalasi sebelum bertindak.

Timeline Aggregate Complaint menggabungkan peristiwa Complaint-level dan Case-level dengan penanda Case. Filter per Case tersedia. Timeline termasuk Escalation Package secara penuh.

## Actors

System (menyusun dari peristiwa domain), semua petugas (pembaca), QA/Compliance

## Preconditions

Peristiwa sumber terjadi dan diaudit; aktor punya hak lihat Timeline pada objek.

## Trigger

Pembukaan detail Complaint/Case; penyusunan Escalation Package; export ringkas untuk reporting tertentu.

## Normal Flow

1. Sistem mengumpulkan peristiwa terkait Aggregate.
2. Mengurutkan berdasarkan waktu.
3. Menampilkan ringkasan manusiawi per event.
4. Aktor memfilter Case/jenis peristiwa.
5. Drill-down ke artefak (attachment, note, resolution).

## Alternative Flow

### A1 — Compact vs full

Role operasional melihat compact; investigator melihat full termasuk event sistem.

### A2 — Timeline setelah reopen

Peristiwa closure tetap muncul; reopen menjadi event baru — tidak menghapus masa lalu.

## Exception Flow

### E1 — Event hilang dari Timeline tetapi ada di Audit

Dianggap defect integritas; wajib rekonsiliasi. Eskalasi dapat ditahan bila checklist No Information Lost gagal.

### E2 — Reordering manual oleh user

Ditolak.

## Business Validation

Event type dikenal; timestamp ada; entity link ada.

## Business Constraints

Tidak editable sebagai sejarah palsu; lengkap untuk eskalasi; selaras Audit; performa baca tidak boleh mengorbankan kelengkapan bisnis (paging diizinkan).

## Data Affected

Timeline projection; dibaca 360/detail; Escalation Package.

## Notifications

Tidak langsung, kecuali event tertentu memicu notifikasi terpisah.

## Audit Trail

Akses timeline sensitif dapat diaudit; penyusunan event merujuk auditId.

## Security Considerations

Filter event internal dari mata yang tidak berhak; tetap hadir untuk role berhak di tujuan eskalasi.

## KPI Impact

Time-to-understand (kualitatif/QA); pengurangan pertanyaan ulang.

## Future Enhancement

Highlight “what changed since escalation”; customer-safe timeline export.

---

# BR-018 — Complaint History

## Nama Rule

Complaint History

## Purpose

Menyimpan riwayat perubahan atribut dan status Aggregate Complaint (dan ringkasan perubahan Case terkait yang relevan di tingkat Aggregate) agar setiap mutasi bisnis dapat dijelaskan di kemudian hari.

## Business Description

Complaint History berfokus pada jejak perubahan state/atribut: prioritas berubah, kategori berubah, unit berubah, status REGISTERED→IN_PROGRESS→RESOLVED→CLOSED→REOPENED, tautan duplikat, verifikasi pelanggan, closure code, dsb. Berbeda dari Timeline yang menampilkan peristiwa operasional kaya, History menekankan **before/after** field bisnis.

History mendukung Reporting, Audit, dan 360 “Riwayat Complaint”. Tidak boleh hilang saat eskalasi maupun closure.

## Actors

System, Supervisor (pembaca), Compliance, Handler

## Preconditions

Perubahan atribut/status sah menurut workflow; audit tertulis.

## Trigger

Setiap perubahan atribut/status Complaint yang dikonfigurasi sebagai history-worthy.

## Normal Flow

1. Aksi mengubah field/status.
2. Sistem merekam old value, new value, reason (bila wajib), aktor, waktu.
3. History entry tersedia di detail dan 360.

## Alternative Flow

### A1 — Perubahan massal administratif

Setiap Complaint tetap punya entry sendiri; tidak ada “silent bulk” tanpa history.

### A2 — Koreksi data entry

Reason code `CORRECTION`; old value tetap.

## Exception Flow

### E1 — Update tanpa history pada field kritikal

Dilarang.

### E2 — User mengedit history

Ditolak.

## Business Validation

Field list kritikal; reason on sensitive changes; workflow transition allowed (configuration-first).

## Business Constraints

Append-only; selaras BR-016; terlihat pasca-eskalasi; tidak menggantikan Assignment/SLA History yang lebih detail di Case.

## Data Affected

History records; 360; reports.

## Notifications

Opsional pada perubahan prioritas ke CRITICAL.

## Audit Trail

Selalu berkorelasi; history adalah view bisnis dari mutasi yang juga diaudit.

## Security Considerations

Before/after mungkin berisi data sensitif; batasi role.

## KPI Impact

Churn prioritas; koreksi rate; compliance readiness.

## Future Enhancement

Field-level diff visualization; policy-driven history retention tiers.

---

# BR-019 — Dashboard KPI

## Nama Rule

Dashboard KPI

## Purpose

Menyediakan indikator kinerja operasional Complaint Management yang bersumber dari peristiwa nyata agar Supervisor dan manajemen memantau beban, SLA, eskalasi, dan kualitas tanpa mengubah data transaksi.

## Business Description

Dashboard KPI bersifat **read-only**. Angka berasal dari agregasi Case/Complaint events: volume create, open backlog, % SLA met (Working Day), breach, escalation rate, assignment aging, reopen rate, duplicate override, dsb. Tampilan mengikuti role dan organisasi aktor (unit/regional/pusat).

Single Source of Truth tetap transaksi Case/Complaint; dashboard adalah proyeksi. Lag data harus ditandai “as of”. Drill-down wajib menuju daftar Case/Complaint sumber (Full Traceability).

## Actors

Supervisor, Operations Lead, Management, System (projection), Administrator (konfigurasi widget yang diizinkan)

## Preconditions

Aktor berwenang dashboard; projection tersedia; scope org diketahui.

## Trigger

Pembukaan dashboard; refresh; jadwal materialisasi KPI.

## Normal Flow

1. Aktor membuka dashboard sesuai role.
2. Sistem menampilkan KPI dalam lingkup org.
3. Aktor memfilter periode/kategori/unit.
4. Drill-down ke daftar transaksi.
5. Tidak ada aksi write dari dashboard.

## Alternative Flow

### A1 — Perbandingan antar unit

Hanya role lintas-unit.

### A2 — Fokus SLA breach

Antrian breach Working Day dari BR-006.

## Exception Flow

### E1 — Angka tidak reconcile

Tampilkan banner data issue; jangan sembunyikan.

### E2 — Upaya edit target KPI dari dashboard operasional

Ditolak; ubah target lewat Administration governance.

## Business Validation

Periode valid; filter diizinkan; KPI terdaftar punya formula/owner.

## Business Constraints

Read-only; role scoped; traceable ke transaksi; tidak mencampur data di luar Complaint Module sebagai fakta seolah milik modul tanpa sumber.

## Data Affected

Read projection saja.

## Notifications

Opsional alert breach threshold ke Supervisor.

## Audit Trail

Akses dashboard eksekutif dapat diaudit; perubahan konfigurasi widget diaudit.

## Security Considerations

Sembunyikan PII di widget; drill-down tetap enforce authz.

## KPI Impact

Rule ini **mendefinisikan konsumsi** KPI; kualitasnya bergantung kepatuhan BR-001…BR-018.

## Future Enhancement

Persona packs; forecast backlog; SLA risk scoring.

---

# BR-020 — Reporting

## Nama Rule

Reporting

## Purpose

Menghasilkan laporan formal operasional dan manajerial mengenai Complaint/Case yang akurat, dapat diaudit, dan tidak melanggar keamanan data — untuk operasi, compliance, dan perbaikan berkelanjutan.

## Business Description

Reporting mencakup laporan terjadwal dan ad-hoc: volume, aging, SLA Working Day achievement, escalation, resolution codes, reopen, duplicate, workload handler, lampiran outstanding, dsb. Laporan dapat diekspor sesuai kebijakan. Berbeda dari dashboard yang interaktif, reporting menekankan artefak yang dapat didistribusikan dan diarsipkan.

Setiap angka laporan harus dapat ditelusuri ke populasi transaksi. Reporting **tidak** mengubah transaksi. Parameter laporan (periode, unit, kategori) wajib tercatat pada run history untuk Auditability.

## Actors

Operations, Supervisor, Management, Compliance, System (scheduler), Administrator (template laporan)

## Preconditions

Hak reporting; template aktif; periode tidak melebihi jendela yang diizinkan untuk tipe laporan; masking rules diketahui.

## Trigger

Jadwal; permintaan ad-hoc; permintaan audit; penutupan periode operasional.

## Normal Flow

1. Aktor/system memilih template + parameter.
2. Sistem mengotorisasi scope.
3. Sistem menyusun dataset dari sumber operasional/projection yang disetujui.
4. Menjalankan masking.
5. Menghasilkan artefak laporan + metadata run.
6. Menyimpan run history (siapa, kapan, parameter, checksum jumlah baris).
7. Distribusi melalui kanal yang diizinkan (bukan email massal PII tanpa kontrol).

## Alternative Flow

### A1 — Laporan compliance detail

Termasuk audit samples; akses sangat terbatas.

### A2 — Laporan eskalasi No Information Lost

Menilai kelengkapan package (checklist) sebagai metrik kualitas handover.

## Exception Flow

### E1 — Export melebihi batas baris

Ditolak atau dipecah; cegah data dump.

### E2 — Parameter di luar hak unit

Ditolak.

### E3 — Menyusun laporan dari data manual non-traceable sebagai fakta inti

Ditolak untuk KPI inti.

## Business Validation

Template dikenal; periode; size limits; mandatory metadata run.

## Business Constraints

Read-only terhadap transaksi; traceability; retensi artefak laporan sesuai kebijakan; tidak menggantikan Audit Trail mentah.

## Data Affected

Report runs/artifacts metadata; tidak mengubah Complaint/Case.

## Notifications

Laporan terjadwal siap; kegagalan job pelaporan ke Operations.

## Audit Trail

ReportRequested/Generated/Downloaded/Distributed.

## Security Considerations

PII minimization; watermark; akses download diaudit; larangan kirim ke penerima di luar daftar.

## KPI Impact

Ketersediaan laporan tepat waktu; jumlah koreksi laporan; temuan audit eksternal.

## Future Enhancement

Parameterized self-service dengan guardrail; data mashup terkendali ke data warehouse enterprise.

---

# Lampiran A — Matriks Ketergantungan Antar Rule

| Rule | Bergantung Utama Pada |
|---|---|
| BR-001 Create Complaint | BR-002, BR-014, BR-010, BR-016, BR-017 |
| BR-002 Customer Validation | Dependency Master Customer |
| BR-003 Complaint Search | BR-001 data, otorisasi |
| BR-004 Create Case | BR-001, BR-005/006 lanjutan |
| BR-005 Assignment | BR-004, BR-007 |
| BR-006 Working Day SLA | BR-004, Calendar Platform, SLA Policy |
| BR-007 Escalation | BR-005, BR-011…BR-013, BR-016…BR-018, BR-006; DEC-F4 |
| BR-008 Resolution | BR-004, BR-012, BR-006; DEC-F4 (`result_visibility`) |
| BR-009 Closure | BR-008, seluruh Case |
| BR-010 Customer 360 | BR-002, data BR-001…BR-015 |
| BR-011 Communication | BR-001/004 |
| BR-012 Attachment | BR-001/004, BR-008 |
| BR-013 Comment | BR-001/004, BR-007 |
| BR-014 Duplicate | BR-001, BR-003, BR-010 |
| BR-015 Reopen | BR-009, BR-004 |
| BR-016 Audit | Seluruh rule write |
| BR-017 Timeline | Seluruh peristiwa |
| BR-018 History | Perubahan Complaint |
| BR-019 Dashboard KPI | BR-006 dan event operasional |
| BR-020 Reporting | Populasi transaksi + audit run |

# Lampiran B — Checklist Eskalasi “No Information Lost”

Sebelum eskalasi Case dianggap lengkap, sistem/aktor memastikan package memuat (atau secara eksplisit menandai kosong dengan alasan):

1. Timeline lengkap
2. Assignment History
3. Escalation History sebelumnya
4. Internal Notes
5. External Notes
6. Communication History
7. Attachments (dokumen/foto/video) + history
8. Resolution History (jika ada)
9. SLA History + policy version
10. Audit Trail / manifest audit

Kegagalan checklist → eskalasi tidak boleh diselesaikan sebagai sukses.

# Lampiran C — Status Dokumen & Langkah Governance

| Item | Nilai |
|---|---|
| Status | Locked v1.3 (+ Mode A Delivery Baseline policy notes 2026-08-01; Transition Matrix unchanged) |
| Model domain | Complaint Aggregate → multi Case |
| Konflik dengan SoT Sprint-01 | Ya (case-centric delivery BR-0xx) — perlu DEC remapping sebelum implementasi menggantikan SoT |
| Keputusan terkunci yang dihormati | Prinsip pembuka dokumen + path Branch↔HO; **DEC-F4 detail** retained as catalog/provisional (not Mode A BR force until countersign) on BR-007 / BR-008 |
| DEC terkait | `18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`; `ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md`; `ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md` |
| FRD Batch 1 | **Tidak diubah** (LOCKED FRD-CM-001 v1.1); DEC-F4 untuk batch eskalasi/resolusi berikutnya |
| Rekomendasi berikutnya | Countersign Architecture Board; Impact Analysis BR-007/BR-008; petakan ke FRD batch eskalasi; formalisasi UAT-F4 di Test Strategy |

---

## Document History

| Version | Date | Notes |
|---|---|---|
| 1.0 | 2026-07-29 | Draft awal BR-CM-CAT-001 (BR-001…BR-020) |
| 1.1 | 2026-07-29 | DEC-F4: jalur Cabang→Pusat; Return reason code+note; `result_visibility`; F4-OQ-01/02 closed (min note 10; branch read-only at Pusat) |
| 1.2 | 2026-08-01 | BU-02: Case Aggregate Transition Matrix menggantikan State Machine Ringkas untuk Case; governing DEC-BQ001 O3 APPROVED; Complaint state machine tidak diubah; status dokumen tetap Draft |
| 1.3 | 2026-08-01 | BU-04: Status Draft → **Locked** setelah BU-01 (DEC-BQ001 O3 APPROVED) + BU-02 (Transition Matrix SoT); tidak mengubah Business Rules, Transition Matrix, atau Complaint state machine |
| 1.3+notes | 2026-08-01 | DEC-MODEA-B2-001: Mode A Delivery Baseline policy notes (CAP-008); Transition Matrix **unchanged** |
| 1.3.1 | 2026-08-05 | Alignment patch P-01…P-08 vs BC/BW baseline: Working Day Deferred/24×7 note; persona → Complaint Officer + Manager; DEC-F4 Reserved qualify; BC/BW precedence; BQ-002 working day wording; Regional OOS Mode A. **No rule redesign.** |

---

*Akhir dokumen BR-CM-CAT-001 v1.3.1 — ECMP Complaint Management Module Business Rules (+ Mode A Delivery Baseline notes; governance alignment).*
