# CAP-008 Case Management — Business Capability Specification

| Field | Value |
|---|---|
| Document ID | BCS-CAP-008-001 |
| Capability ID | **CAP-008** (former working ID `CAP-02` — retired to avoid collision with `CAP-002`) |
| Title | Case Management — Business Capability Specification |
| Version | 1.2 |
| Status | 🟢 BUSINESS LOCK READY · Residual BQ **ZERO** · FRD-CM-B2-001 🔒 **LOCKED** |
| Batch | Batch-2 Mode A |
| Owner | Product Owner / Business Analyst / Solution Architect (Product Team) |
| Reviewer | Domain PO ECMF, Operations Lead, Compliance |
| Approver | Business Owner / Architecture Board |
| Module | Complaint Management Module only |
| Last Review | 2026-08-01 |
| Related SoT | `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001 🔒 **Locked** — Case Aggregate Transition Matrix) |
| Related Batch-1 | `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` (FRD-CM-001 🔒 LOCKED; CTO D-02) |
| Related DEC | DEC-020 (dual SoT); **DEC-BQ001** Option O3; **DEC-MODEA-B2-001** Mode A Delivery Baseline BQ Lock Pack (`18 Architecture Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md`); CTO D-02 |
| Explicitly excluded | Mode B · Identity redesign · Enterprise Platform · AI · SDK · Assignment Engine · SLA Engine · Notification Engine · Dashboard · Reporting |

> **Kualitas dokumen:** Business only. Tidak ada spesifikasi implementasi, database, API/OpenAPI, UI, atau sequence diagram.
>
> **Aturan SoT:** Merujuk BR-CM-CAT-001, FRD-CM-001 terkunci, dan keputusan Mode A Delivery Baseline (DEC-MODEA-B2-001). BQ-001…BQ-014 **LOCKED**.
>
> **Koreksi istilah wajib (vs prompt awal):** SoT Batch-1 mengunci *Complaint contains one or many Cases* dan *Add Case on existing Complaint*. Frasa *Add Complaint to Existing Case* **salah arah** dan **tidak dipakai** di dokumen ini.

---

# 1 Purpose

## 1.1 Why Case exists

Per BR-CM-CAT-001 (glosarium + BR-004):

- **Complaint** adalah Aggregate Root — kesatuan bisnis keluhan/permintaan pelanggan.
- **Case** adalah **unit kerja operasional** di bawah Complaint.

Case ada agar pekerjaan dapat:

1. Ditangani sebagai potongan kerja independen (mis. isu tagihan vs isu layanan dalam satu keluhan yang sama).
2. Memiliki ownership operasional (Assignment) pada level Case — bukan Complaint (keputusan terkunci FRD-CM-001 §3 / BR-005).
3. Diukur dengan SLA Working Day pada level Case — bukan Complaint (keputusan terkunci / BR-006).
4. Dieskalasikan, diselesaikan (Resolution), dan ditutup sebagai siklus kerja tanpa memecah Single Source of Truth Aggregate Complaint (BR-004, BR-007, BR-008).

Tanpa Case, Batch-1 meninggalkan Complaint berstatus `REGISTERED` tanpa unit kerja operasional (CTO D-02 / FRD-CM-001 A4). CAP-02 menutup celah itu untuk Batch-2 Mode A.

## 1.2 Why Complaint is NOT a work item

Per BR-001 dan prinsip arsitektur BR-CM-CAT-001:

- Complaint **bukan** Case.
- Complaint adalah **wadah bisnis** (Aggregate Root): identitas keluhan, `CustomerId`, klasifikasi intake, jejak audit/timeline Aggregate.
- Assignment **tidak** boleh ada di level Complaint.
- SLA **tidak** boleh dihitung di level Complaint.
- Petugas mengerjakan **Case**, bukan “mengerjakan Complaint” sebagai tiket kerja tunggal.

Oleh karena itu Complaint **bukan work item operasional**. Work item = Case.

## 1.3 Why Case becomes the primary *operational* business object

Clarifikasi SoT (tanpa meredesain Batch-1):

| Lapisan | Objek primer | Alasan |
|---|---|---|
| Aggregate / identitas bisnis | **Complaint** (tetap Aggregate Root) | Keputusan terkunci FRD-CM-001 §3 #1–#2 |
| Operasional harian (assign, SLA, resolve, close kerja) | **Case** | BR-004…BR-008 |

Untuk CAP-02 Case Management, Case adalah objek bisnis **primer pada jalur operasional**. Complaint tetap induk Aggregate dan batasan konsistensi. CAP-02 **tidak** memindahkan Aggregate Root ke Case dan **tidak** membalik relasi menjadi “Case contains Complaints”.

---

# 2 Scope

## 2.1 IN SCOPE (Batch-2 Mode A — CAP-02)

| Capability slice | Business meaning (SoT) | Primary BR |
|---|---|---|
| Create Case | Membentuk Case pertama / Case baru di bawah Complaint yang sudah ada | BR-004 |
| Add Case to Existing Complaint | Menambah Case pada Complaint aktif (termasuk jalur “lanjutkan keluhan existing”) — **bukan** menambah Complaint ke Case | BR-004, BR-014 |
| View Case | Membaca Case dalam batas Aggregate + otorisasi role/unit | BR-004 constraints; BR-017 read |
| Case Timeline | Melihat kronologi peristiwa Case (dan konteks Aggregate yang relevan) | BR-017 |
| Update Case Status | Transisi status Case yang diizinkan state machine bisnis (tanpa Assignment Engine / SLA Engine) | BR-CM-CAT state Case; BR-016/017 |
| Resolution | Mencatat / mengajukan / menerima resolusi Case | BR-008 |
| Close Case | Menutup siklus kerja Case setelah resolusi memenuhi syarat | BR-008 (+ kontribusi ke BR-009, tanpa mengeksekusi Complaint Closure penuh kecuali diputuskan terpisah — lihat §5) |

Reuse wajib dari Batch-1 (tidak di-redesain):

- Complaint Aggregate Root + `CustomerId` only (FRD-CM-001 locked decisions).
- Complaint Batch-1 selalu lahir tanpa Case (CTO D-02); CAP-02 menyediakan jalur Create Case setelahnya.
- Anchor membership: bila artefak menunjuk Case, Case **MUST** milik Complaint yang sama (FRD-CM-001 FR-004).
- Mode B **CLOSED**. Identity redesign **OUT**. Authorization tetap ECMP-internal (FRD-CM-001 §4.1) — detail Identity tidak dibahas di BCS ini.

## 2.2 OUT OF SCOPE

| Area | Catatan |
|---|---|
| Assignment Engine | BR-005 penuh (claim, auto-route, bulk reassignment, skill matrix) di luar CAP-02 |
| SLA Engine | BR-006 kalkulasi Working Day / breach / pause-resume otomatis di luar CAP-02 |
| Notification Engine | Permintaan notifikasi platform di luar CAP-02 |
| Dashboard | BR-019 |
| Reporting | BR-020 |
| Mode B | Tertutup untuk misi ini |
| Identity | Tidak didesain ulang di CAP-02 |
| AI | Dilarang dibahas / dimasukkan |
| Escalation Engine (BR-007 penuh) | Bukan slice CAP-02; DEC-F4 / FRD-CM-002 terpisah |
| Complaint Closure Aggregate (BR-009 penuh) | Bukan pengganti Close Case; hubungan Aggregate dicatat sebagai pertanyaan bisnis bila perlu |
| Reopen Case / Complaint Reopen (BR-015) | Tidak ada di daftar IN SCOPE prompt; tidak di-lock sebagai capability CAP-02 |
| Redesign Batch-1 intake (FR-001…FR-004) | Dilarang |
| Enterprise Platform / SDK | Dilarang |

---

# 3 Actors

Sumber: BR-CM-CAT-001 §Aktor Bisnis + FRD-CM-001 §5, dibatasi pada slice CAP-02.

## 3.1 Agent / Petugas Frontline

| Aspek | Definisi |
|---|---|
| Responsibilities | Memilih Complaint induk; memicu Create Case / Add Case saat keluhan membutuhkan unit kerja; mengisi atribut Case awal; melihat Case & Timeline |
| Permissions | Create Case pada lingkup unit yang diizinkan; View Case dalam scope org/role; tidak meng-assign lintas wewenang Assignment Engine (OOS) |
| Business goals | Mengubah Complaint `REGISTERED` menjadi punya Case operasional; mencegah duplicate Aggregate dengan menambah Case pada Complaint existing |

## 3.2 Case Handler

| Aspek | Definisi |
|---|---|
| Responsibilities | Melihat Case yang menjadi tanggung jawabnya; memperbarui status sesuai transisi diizinkan; menambah konteks kerja yang diizinkan scope; menyusun usulan Resolution |
| Permissions | View Case; Update Status dalam guard role; Resolve (ajukan) sesuai BR-008; akses Timeline/Attachment/Comment sesuai hak |
| Business goals | Menyelesaikan unit kerja Case dengan resolusi lengkap dan tertelusur |

## 3.3 Supervisor Unit

| Aspek | Definisi |
|---|---|
| Responsibilities | Memastikan Complaint tanpa Case tidak menua tanpa tindakan; menyetujui/menolak resolusi bila policy approval aktif; menutup Case bila berwenang; oversight multi-Case pada satu Complaint |
| Permissions | Create Case; View Case lintas handler dalam unit; approve/reject Resolution; Close Case sesuai wewenang; override terbatas hanya jika dikonfigurasi + beraudit |
| Business goals | Throughput Case; kualitas closure Case; No Duplicate Work |

## 3.4 Administrator

| Aspek | Definisi |
|---|---|
| Responsibilities | Mengonfigurasi tipe/kategori Case, katalog resolusi, kebijakan “wajib Case awal” (efek ke Batch-2+), batas maksimum Case per Complaint, parameter workflow status |
| Permissions | Configuration-first atas master kebijakan Case (bukan mengerjakan Case harian) |
| Business goals | Aturan operasional konsisten, dapat diaudit, effective-dated |

## 3.5 System

| Aspek | Definisi |
|---|---|
| Responsibilities | Generate Case Number; enforce preconditions/validasi; tulis Audit (BR-016) + Timeline (BR-017); cegah Case tanpa Complaint; cegah hard-delete Case; evaluasi dampak status Complaint `REGISTERED` → `IN_PROGRESS` saat Case pertama dibuat (BR-004) |
| Permissions | Otomasi aturan bisnis; bukan aktor manusia |
| Business goals | Integritas Aggregate, auditability, full traceability |

## 3.6 Customer

| Aspek | Definisi |
|---|---|
| Responsibilities | Sumber keluhan (tidak login ke modul dalam scope ini) |
| Permissions | Tidak ada akses langsung CAP-02 Mode A |
| Business goals | Masalahnya ditangani sebagai Case yang jelas, bukan Complaint “mengambang” tanpa kerja |

> **Petugas Regional / Pusat:** relevan untuk Escalation/Resolution DEC-F4. Karena Escalation Engine OUT OF SCOPE CAP-02, aktor Pusat/Regional **tidak** menjadi aktor primer CAP-02 kecuali Business Owner memasukkan Resolve-by-Pusat ke scope (saat ini tidak).

---

# 4 Business Objects

## 4.1 Complaint

| Aspek | Definisi (SoT) |
|---|---|
| Purpose | Aggregate Root — wadah bisnis keluhan; menyimpan `CustomerId`; induk satu atau banyak Case |
| Owner | Domain PO ECMF / Complaint Management Module |
| Lifecycle | `REGISTERED` → `IN_PROGRESS` → `RESOLVED` → `CLOSED` · cabang `REOPENED` → `IN_PROGRESS` (BR-CM-CAT-001 ringkas). Batch-1 menghasilkan `REGISTERED` tanpa Case |
| Relationships | 1 Complaint : 0..N Case (Batch-1 = 0 Case; CAP-02 membuat N≥1). Referensi pelanggan hanya `CustomerId` |

## 4.2 Case

| Aspek | Definisi (SoT) |
|---|---|
| Purpose | Unit kerja operasional di bawah Complaint |
| Owner | Domain PO ECMF (operasional Case) |
| Lifecycle | SoT BR-CM-CAT-001 (DEC-BQ001 O3): `CREATED` → `ASSIGNED` → `IN_PROGRESS` → `PENDING` / `ESCALATED` → `RESOLVED` → `CLOSED` · cabang `CANCELLED` (sebelum resolusi final, berjustifikasi). DOM-ECMF-003 tetap SoT Sprint terpisah — tidak interchangeable |
| Relationships | N Case : 1 Complaint. Case tidak berdiri sendiri. Assignment/SLA/Resolution melekat Case (meski engine Assignment/SLA OOS di CAP-02) |

## 4.3 Timeline

| Aspek | Definisi (SoT) |
|---|---|
| Purpose | Proyeksi kronologis peristiwa bisnis yang dapat dibaca manusia (BR-017) |
| Owner | System menyusun; petugas berwenang membaca |
| Lifecycle | Append-only projection dari peristiwa domain; tidak diedit ulang sebagai sejarah palsu |
| Relationships | Timeline Aggregate menggabungkan event Complaint-level + Case-level dengan penanda Case; filter per Case tersedia |

## 4.4 Resolution

| Aspek | Definisi (SoT) |
|---|---|
| Purpose | Pernyataan hasil penanganan Case: kode, ringkasan, tindakan, dampak, evidence, history usulan/reject/accept (BR-008) |
| Owner | Case Handler (menyusun); Supervisor (approve bila wajib) |
| Lifecycle | Proposed → (Pending Approval) → Accepted / Rejected; multi-attempt history append-only; final Accepted menjadi prasyarat Case `RESOLVED`/`CLOSED` |
| Relationships | Terikat Case; berkontribusi pada evaluasi Complaint Closure (BR-009) tanpa otomatis menutup Complaint kecuali policy terpisah |

## 4.5 Attachment

| Aspek | Definisi (SoT) |
|---|---|
| Purpose | Bukti pendukung ditautkan Complaint dan/atau Case (BR-012); Batch-1 sudah mengunci upload + transfer staged evidence |
| Owner | Uploader (Agent/Handler); metadata dikelola modul; binary boleh di storage enterprise |
| Lifecycle | `ACTIVE` / `SUPERSEDED` / void-with-reason; hard-delete user dilarang |
| Relationships | Anchor Complaint wajib; Case opsional tetapi MUST membership Aggregate yang sama |

## 4.6 Comment

| Aspek | Definisi (SoT) |
|---|---|
| Purpose | Catatan kerja Internal vs External pada Complaint/Case (BR-013) |
| Owner | Handler/Supervisor/Agent sesuai jenis note |
| Lifecycle | Append-only / void-with-reason; bukan silent overwrite bila immutability diwajibkan |
| Relationships | Anchor Complaint/Case; muncul di Timeline sebagai event “Note Added”; **mutasi Comment bukan use case wajib CAP-02** — objek didefinisikan untuk kelengkapan model; apakah write Comment masuk delivery CAP-02 = Open Question |

---

# 5 Business Questions

Semua BQ Mode A Delivery Baseline (**BQ-001 … BQ-014**) berstatus **LOCKED** per Product Owner Decision Session + `DEC-MODEA-B2-001`. Residual = **ZERO**.

| ID | Question | Business impact | Blocking level | Locked decision | Approver |
|---|---|---|---|---|---|
| BQ-CAP02-001 | Case state machine SoT Batch-2 Mode A | Update/Resolve/Close | **LOCKED** | DEC-BQ001 O3 — Aggregate = BR-CM-CAT Definition B; Sprint = DOM-ECMF-003 | Architecture Board / BO |
| BQ-CAP02-002 | Mandatory Case after REGISTERED / aging | Wajib Case; KPI aging | **LOCKED** | Complaint MAY register without Case; MUST have ≥1 Case within **1 business day** after REGISTERED; Supervisor Queue MUST display exceedances | Product Owner |
| BQ-CAP02-003 | Max Case per Complaint | Parallel Case | **LOCKED** | Default maximum **5** Cases per Complaint; future override **outside Mode A** | Product Owner |
| BQ-CAP02-004 | Case Number format | Identity / search / audit | **LOCKED** | Independent of Complaint Number; format `CASE-YYYY-NNNN` (e.g. `CASE-2026-0002`) | Product Owner |
| BQ-CAP02-005 | SLA bind without SLA Engine | BR-004/006 consistency | **LOCKED** | Case SHALL bind SLA Policy Version; countdown **NOT** activated in Mode A | Product Owner |
| BQ-CAP02-006 | Assignment without Assignment Engine | Update/Resolve preconditions | **LOCKED** | Assignment at **Unit level only**; Assigned User **outside Mode A** | Product Owner |
| BQ-CAP02-007 | Close Case vs auto Complaint Closure | Aggregate vs Case | **LOCKED** | Close Case → Case `CLOSED` only; **MUST NOT** auto-close Complaint (BR-009 separate) | Product Owner |
| BQ-CAP02-008 | RESOLVED / CLOSED + approval | Resolve/Close acceptance | **LOCKED** | Mode A: `IN_PROGRESS` → `RESOLVED` → Supervisor Approval → `CLOSED` | Product Owner |
| BQ-CAP02-009 | PENDING / ESCALATED delivery | State subset Mode A | **LOCKED** | States remain in Aggregate State Machine; Mode A Delivery **does NOT expose** them | Product Owner |
| BQ-CAP02-010 | Comment / Attachment on Case | Resolve artefacts | **LOCKED** | Resolve **requires** Comment; Attachment **optional**; Complaint Attachment may be reused | Product Owner |
| BQ-CAP02-011 | Wajib Case awal vs D-02 | Intake coexistence | **LOCKED** | D-02 retained (no Case-at-intake); mandatory timing after REGISTERED = BQ-002 | Product Owner |
| BQ-CAP02-012 | CAP-02 vs CAP-002 ID collision | Traceability | **LOCKED** | Final capability ID **CAP-008** (register `CAP-0xx`); CAP-002 Assignment unchanged | Product Owner / BA |
| BQ-CAP02-013 | BR-CM-CAT lock prerequisite | Enforceability | **LOCKED** | BR-CM-CAT-001 Locked | Architecture Board |
| BQ-CAP02-014 | CANCELLED in Mode A | Non-resolution close | **LOCKED** | `CANCELLED` **included** in Mode A; reasons include Duplicate, Wrong Input, Customer Cancellation | Product Owner |

---

# 6 Business Rules

Rules di bawah **direuse** dari BR-CM-CAT-001 / keputusan terkunci Batch-1. Tidak ada rule baru yang mengarang perilaku di luar SoT. Field *Validation* / *Blocking Level* menjelaskan kesiapan lock untuk CAP-02.

| Rule ID | Description | Reason | Priority | Related Use Case | Validation | Blocking Level |
|---|---|---|---|---|---|---|
| BR-CAP02-R01 (← BR-004) | Case MUST berada di bawah Complaint yang valid; Case tidak berdiri sendiri | Aggregate boundary | Must | UC-Create Case; UC-Add Case | ComplaintId ada; status Complaint mengizinkan Case baru | Locked principle |
| BR-CAP02-R02 (← FRD-CM-001 §3 #2) | Satu Complaint MAY memiliki satu atau banyak Case | Multi-Case locked | Must | UC-Add Case | Relasi 1:N terjaga | Locked principle |
| BR-CAP02-R03 (← BR-001 / D-02) | Complaint Batch-1 lahir tanpa Case; CAP-02 menyediakan Create Case setelahnya | Intake vs work separation | Must | UC-Create Case | Tidak mengasumsikan Case pada create Complaint Batch-1 | Locked (Batch-1) |
| BR-CAP02-R04 (← BR-004) | Assignment & SLA secara bisnis melekat Case, bukan Complaint — meskipun engine OOS di CAP-02 | Keputusan arsitektur bisnis | Must | All Case UCs | Tidak membuat Assignment/SLA di level Complaint | **LOCKED** — BQ-005/006 (DEC-MODEA-B2-001) |
| BR-CAP02-R05 (← BR-004) | Create Case MUST menghasilkan Case Number unik (`CASE-YYYY-NNNN`, independen Complaint Number) + status awal Case + Timeline/Audit | Traceability / SoT identity | Must | UC-Create Case; UC-Add Case | Number unique; Timeline “Case Created”; Audit CaseCreated | **LOCKED** — BQ-004 |
| BR-CAP02-R06 (← BR-004) | Saat Case pertama dibuat pada Complaint `REGISTERED`, status Complaint menjadi `IN_PROGRESS` bila belum lebih lanjut | Sinkron Aggregate | Must | UC-Create Case | Transisi Complaint terdokumentasi + history | Locked in BR-004 narrative |
| BR-CAP02-R07 (← BR-004 E1 / BR-015) | Create Case pada Complaint `CLOSED` MUST ditolak; arahkan Reopen (di luar scope CAP-02 kecuali diputuskan) | Integrity closure | Must | UC-Create Case; UC-Add Case | Reject + alasan bisnis | Locked principle |
| BR-CAP02-R08 (← BR-004 E3) | Create Case MUST ditolak jika batas maksimum Case per Complaint tercapai | Kontrol operasional | Must | UC-Add Case | Compare count vs **max 5** (Mode A) | **LOCKED** — BQ-003 |
| BR-CAP02-R09 (← BR-004) | Hard-delete Case dilarang; pembatalan via `CANCELLED` + alasan Mode A (Duplicate / Wrong Input / Customer Cancellation) | Auditability | Must | UC-Update Status / Close | No physical delete | **LOCKED** — BQ-014 |
| BR-CAP02-R10 (← BR-014 / D-02) | Duplikat bisnis sebaiknya diselesaikan dengan Add Case on existing Complaint, bukan Complaint baru | No Duplicate Work | Must | UC-Add Case | Prefer existing Complaint | Locked principle |
| BR-CAP02-R11 (← BR-017) | Setiap Create / Status change / Resolve / Close Case MUST menghasilkan entri Timeline yang dapat dibaca | Bahasa operasional | Must | UC-Timeline; all writes | Event type dikenal; timestamp; entity link | Locked principle |
| BR-CAP02-R12 (← BR-016) | Setiap write signifikan Case MUST menulis Audit Trail immutable | Auditability | Must | All mutating UCs | Actor, action, entity, time | Locked principle |
| BR-CAP02-R13 (← BR-008) | Mode A: `IN_PROGRESS` → `RESOLVED` → Supervisor Approval → `CLOSED` | Evidence-based closure | Must | UC-Resolve; UC-Close | Kode resolusi valid; Comment wajib (BQ-010); Supervisor approve sebelum CLOSED | **LOCKED** — BQ-008 |
| BR-CAP02-R14 (← BR-008) | Resolution History append-only; reject/approve tidak menghapus usulan lama | No information lost | Must | UC-Resolve | History retained | Locked principle |
| BR-CAP02-R15 (← BR-008) | Close Case MUST NOT otomatis menutup Complaint; BR-009 terpisah | Batas Close Case vs Complaint Closure | Must | UC-Close Case | Close Case tidak silent-close Aggregate | **LOCKED** — BQ-007 |
| BR-CAP02-R16 (← BR-012 / FR-004) | Jika Attachment di-anchor ke Case, Case MUST milik Complaint yang sama | Aggregate membership | Must | View/Resolve (evidence) | Membership check | Locked (Batch-1) |
| BR-CAP02-R17 (← BR-013) | Resolve Mode A **requires** Comment; Attachment optional; Complaint Attachment may be reused; Comment ≠ Resolution formal | Keamanan & kejelasan | Must | UC-Resolve | Comment wajib pada Resolve | **LOCKED** — BQ-010 |
| BR-CAP02-R18 (← BR-CM-CAT Case Aggregate Transition Matrix) | Status Case hanya berubah melalui transisi yang diizinkan SoT BR-CM-CAT-001 (DEC-BQ001 O3) | Configuration-first | Must | UC-Update Status | Reject forbidden transition | **LOCKED** — matrix SoT BR-CM-CAT-001 |
| BR-CAP02-R19 (← BR-004 Actors) | Hanya aktor berwenang unit/role yang boleh Create Case / Update Status / Resolve / Close | Authorization internal ECMP | Must | All UCs | AuthZ deny + audit | Locked principle (Mode B OOS) |
| BR-CAP02-R20 (← DEC-F4 / BR-008) | `result_visibility` hanya relevan Resolve-by-Pusat setelah eskalasi | Scope CAP-02 | Could / Deferred | — | Tidak menerapkan DEC-F4 di CAP-02 Mode A kecuali Escalate masuk scope | Deferred (Escalation OOS) |

---

# 7 State Machine

> **SoT:** Case status & transitions untuk CAP-02 / Batch-2 Mode A = **BR-CM-CAT-001 Case Aggregate Transition Matrix** (🔒 Locked).  
> **Governing decision:** `ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md` — Option **O3 APPROVED**.  
> **Dual SoT:** DOM-ECMF-003 tetap SoT Case pada jalur Sprint / case-centric — **bukan** SoT CAP-02.  
> **BQ-CAP02-001 = LOCKED.** Ringkasan di bawah merujuk SoT BR-CM-CAT-001; detail allowed/forbidden/guards/events = dokumen BR.

## 7.1 Allowed states (BR-CM-CAT-001 SoT)

| State | Meaning (bisnis) |
|---|---|
| `CREATED` | Case terbentuk; belum tentu ada assignee |
| `ASSIGNED` | Ada kepemilikan assignee/queue |
| `IN_PROGRESS` | Sedang dikerjakan |
| `PENDING` | Menunggu pihak eksternal/pelanggan/dokumen |
| `ESCALATED` | Dalam jalur eskalasi (Pusat per DEC-F4) |
| `RESOLVED` | Resolusi Accepted; kerja selesai menunggu/menuju close |
| `CLOSED` | Siklus Case ditutup (**terminal**) |
| `CANCELLED` | Dibatalkan sebelum resolusi final + justifikasi (**terminal**) |

## 7.2 Allowed transitions (BR-CM-CAT-001 SoT)

| From | To | Entry intent |
|---|---|---|
| — | `CREATED` | Create Case / Add Case |
| — | `ASSIGNED` | Create Case + Assignment sekaligus (BR-004 A1) |
| `CREATED` | `ASSIGNED` | Assign pertama |
| `CREATED` | `CANCELLED` | Batalkan sebelum resolusi final + alasan |
| `ASSIGNED` | `IN_PROGRESS` | Mulai penanganan |
| `ASSIGNED` | `ASSIGNED` | Reassign / claim (ownership) |
| `ASSIGNED` | `PENDING` | Tunggu kelengkapan |
| `ASSIGNED` | `ESCALATED` | Eskalasi |
| `ASSIGNED` | `CANCELLED` | Batalkan + alasan |
| `IN_PROGRESS` | `PENDING` | Tunggu kelengkapan |
| `IN_PROGRESS` | `ASSIGNED` | Reassign |
| `IN_PROGRESS` | `ESCALATED` | Eskalasi |
| `IN_PROGRESS` | `RESOLVED` | Resolution Accepted |
| `IN_PROGRESS` | `CANCELLED` | Batalkan + alasan |
| `PENDING` | `IN_PROGRESS` | Lanjut kerja |
| `PENDING` | `ASSIGNED` | Reassign |
| `PENDING` | `ESCALATED` | Eskalasi |
| `PENDING` | `RESOLVED` | Resolution Accepted (PENDING selesai) |
| `PENDING` | `CANCELLED` | Batalkan + alasan |
| `ESCALATED` | `ASSIGNED` | Assign di unit tujuan |
| `ESCALATED` | `IN_PROGRESS` | Return ke cabang asal |
| `ESCALATED` | `RESOLVED` | Resolution Accepted (Pusat) |
| `ESCALATED` | `CANCELLED` | Batalkan sebelum resolusi final + alasan |
| `RESOLVED` | `CLOSED` | Close Case |

> AuthZitative matrix (guards, events, invariants): **BR-CM-CAT-001 Case Aggregate Transition Matrix**.

## 7.3 Forbidden transitions (BR-CM-CAT-001 SoT)

- Apapun → hard-delete / hilang tanpa status.
- `CLOSED` → any Case status (tidak ada Case `REOPENED`; reopen via Complaint BR-015 + Case baru).
- `CANCELLED` → any.
- `RESOLVED`/`CLOSED` → `CANCELLED`.
- `CREATED` → `IN_PROGRESS` / `PENDING` / `ESCALATED` / `RESOLVED` / `CLOSED` (harus melalui `ASSIGNED` kecuali create+assign → `ASSIGNED`).
- `ASSIGNED` → `RESOLVED` / `CLOSED` (tanpa jalur kerja / Accepted resolution).
- `RESOLVED` → `IN_PROGRESS` / `ASSIGNED` / `PENDING` / `ESCALATED`.
- Memakai enum DOM-ECMF-003 (`REGISTERED`, `PENDING_REVIEW`, Case `REOPENED`) pada Case Aggregate CAP-02.
- Transisi yang menggerakkan Assignment/SLA di **level Complaint**.
- Membalik relasi menjadi Case induk Complaint.

## 7.4 Entry criteria (Case)

1. Complaint induk ada dan tidak `CLOSED` (tanpa reopen).
2. Aktor berwenang.
3. Tipe/kategori/prioritas Case valid menurut konfigurasi aktif.
4. Belum melampaui max Case per Complaint (**max = 5**, Mode A / BQ-003 LOCKED).
5. CustomerId Complaint ada (verified atau UNVERIFIED sesuai kebijakan Batch-1 yang sudah ada).
6. Transisi target ada di **BR-CM-CAT-001 Case Aggregate Transition Matrix**.

## 7.5 Exit criteria

| Exit | Criteria |
|---|---|
| `RESOLVED` | Resolution Accepted; evidence wajib terpenuhi bila kategori mensyaratkan |
| `CLOSED` | Case `RESOLVED` + aktor close berwenang + checklist Case terpenuhi |
| `CANCELLED` | Alasan wajib; hanya sebelum resolusi final |

## 7.6 Business validation

- Transisi hanya dari **BR-CM-CAT-001 Case Aggregate Transition Matrix** (BQ-001 LOCKED / DEC-BQ001 O3).
- Reason wajib untuk override Administrator / cancel / reject resolution.
- Timeline + Audit wajib per transisi sukses.
- Resolve oleh non-assignee tanpa hak Supervisor ditolak (BR-008 E3).

---

# 8 Use Cases

## 8.1 UC-CAP02-01 — Create Case

| Field | Content |
|---|---|
| Actors | Agent, Supervisor, System (± Case Handler bila diberi hak create) |
| Trigger | Aktor memilih “Create Case” pada Complaint `REGISTERED`/`IN_PROGRESS` yang belum/berhak mendapat Case baru; atau kebijakan auto setelah intake (hanya jika BQ-011 mengizinkan) |
| Preconditions | Complaint ada; tidak `CLOSED`; aktor berwenang; tipe Case aktif; di bawah max Case |
| Main Flow | 1) Pilih Complaint induk 2) Isi tipe/kategori/subjek/deskripsi/prioritas/unit tujuan awal 3) System buat Case Number + status awal 4) Timeline/Audit 5) Complaint `REGISTERED`→`IN_PROGRESS` bila berlaku 6) Tampilkan Case |
| Alternative Flow | A1 Create with Unit assignment only (Mode A / BQ-006) — no Assigned User. A2 Multiple Case paralel pada Complaint yang sama (max 5) |
| Exception Flow | E1 Complaint CLOSED → tolak. E2 Max Case → tolak. E3 Atribut wajib kurang → tolak. E4 Tidak berwenang → tolak + audit |
| Business Rules | R01–R08, R11, R12, R19 |
| Acceptance Criteria | Lihat §9 AC-01… |

## 8.2 UC-CAP02-02 — Add Case to Existing Complaint

| Field | Content |
|---|---|
| Actors | Agent, Supervisor, System |
| Trigger | Duplikat/keluhan lanjutan pada Complaint existing; pecah isu (split) disetujui Supervisor; atau manual “Add Case” |
| Preconditions | Sama Create Case; Complaint aktif mengizinkan Case tambahan |
| Main Flow | 1) Buka Complaint existing 2) Add Case dengan atribut kerja baru 3) System persist Case anak 4) Timeline “Case Created” pada Aggregate & Case 5) Tidak membuat Complaint baru |
| Alternative Flow | A1 Dari peringatan duplikat Batch-1 (recommend-only) → eksekusi Add Case di Batch-2. A2 Split isu multi-Case |
| Exception Flow | Sama E1–E4 Create Case; E5 Salah memilih membuat Complaint baru padahal konteks sama → cegah lewat guidance duplikat (bisnis), bukan Case-under-Case |
| Business Rules | R02, R08, R10, R05, R11, R12 |
| Acceptance Criteria | §9 AC-02… |

> **Normatif:** Ini adalah nama SoT untuk slice yang pada prompt keliru disebut “Add Complaint to Existing Case”.

## 8.3 UC-CAP02-03 — View Case

| Field | Content |
|---|---|
| Actors | Agent, Case Handler, Supervisor, System |
| Trigger | Buka Case dari Complaint detail / antrian aging / search operasional |
| Preconditions | Case ada; aktor punya hak baca scope org/role |
| Main Flow | 1) System tampilkan header Case + status + Complaint induk + CustomerId 2) Tampilkan ringkasan atribut 3) Sediakan akses Timeline 4) Tampilkan Resolution/Attachment/Comment sesuai hak (read) |
| Alternative Flow | A1 View dari konteks Complaint multi-Case (daftar Case). A2 Masking field sensitif untuk role terbatas |
| Exception Flow | E1 Tidak berwenang → tolak. E2 CaseId bukan milik Complaint konteks → tolak (membership) |
| Business Rules | R01, R16, R19 |
| Acceptance Criteria | §9 AC-03… |

## 8.4 UC-CAP02-04 — Update Case Status

| Field | Content |
|---|---|
| Actors | Case Handler, Supervisor, System |
| Trigger | Aktor memilih transisi status diizinkan |
| Preconditions | Case tidak `CLOSED`/`CANCELLED` (kecuali path khusus yang dikunci); transisi ada di matriks; aktor berwenang |
| Main Flow | 1) Pilih target status 2) Isi reason jika wajib 3) System validasi matriks 4) Persist status 5) Timeline + Audit |
| Alternative Flow | A1 PENDING/ESCALATED **not exposed** in Mode A Delivery (BQ-009) — states remain in Aggregate matrix only. A2 CANCELLED with Mode A reasons (Duplicate / Wrong Input / Customer Cancellation) — BQ-014 LOCKED |
| Exception Flow | E1 Forbidden transition → tolak. E2 Reason kurang → tolak. E3 Assignment only at Unit level (BQ-006); Assigned User rejected in Mode A |
| Business Rules | R11, R12, R18, R19 |
| Acceptance Criteria | §9 AC-04… — BQ-001/006/009/014 LOCKED |

## 8.5 UC-CAP02-05 — Resolve Case

| Field | Content |
|---|---|
| Actors | Case Handler (ajukan), Supervisor (approve bila wajib), System |
| Trigger | “Ajukan Resolusi” / “Selesaikan Case” |
| Preconditions | Case pada status yang mengizinkan resolusi; katalog resolusi aktif; evidence policy diketahui; Unit assignment Mode A (BQ-006); Comment wajib pada Resolve (BQ-010) |
| Main Flow | 1) Isi kode/ringkasan/tindakan/dampak/evidence 2) Validasi kelengkapan 3) Approval bila wajib 4) Resolution Accepted 5) Case → `RESOLVED` (BR-CM-CAT SoT) 6) Timeline/Audit/History |
| Alternative Flow | A1 Reject → kembali kerja + reason. A2 Multi-attempt history. A3 Partial/workaround code + follow-up Case baru |
| Exception Flow | E1 Evidence wajib hilang → tolak. E2 Resolve milik orang lain tanpa hak → tolak. E3 Katalog kode invalid → tolak |
| Business Rules | R13, R14, R11, R12, R17 |
| Acceptance Criteria | §9 AC-05… |

## 8.6 UC-CAP02-06 — Close Case

| Field | Content |
|---|---|
| Actors | Supervisor (utama), Case Handler bila dikonfigurasi, System |
| Trigger | “Close Case” setelah Resolution Accepted / Case `RESOLVED` |
| Preconditions | Resolution final memenuhi syarat; aktor berwenang close; Case belum `CLOSED` |
| Main Flow | 1) Evaluasi checklist Case 2) Supervisor Approval setelah `RESOLVED` (BQ-008) 3) Set `CLOSED` + timestamp + closedBy 4) Timeline/Audit 5) **MUST NOT** menutup Complaint Aggregate (BQ-007 LOCKED) |
| Alternative Flow | A1 Close setelah CANCELLED path — **bukan** close-with-resolution; gunakan CANCELLED (BQ-014 LOCKED). A2 Usulan Complaint Closure jika semua Case selesai (hanya sinyal bisnis; eksekusi BR-009 di luar CAP-008 default) |
| Exception Flow | E1 Belum Resolved → tolak. E2 Evidence/resolusi kurang → tolak. E3 Tidak berwenang → tolak |
| Business Rules | R13, R15, R11, R12 |
| Acceptance Criteria | §9 AC-06… |

## 8.7 UC-CAP02-07 — View Case Timeline

| Field | Content |
|---|---|
| Actors | Semua petugas berwenang, System |
| Trigger | Buka tab/panel Timeline pada Case |
| Preconditions | Hak baca Case |
| Main Flow | 1) Kumpulkan event Case (+ penanda Aggregate relevan) 2) Urut waktu 3) Filter jenis event 4) Drill-down ke artefak |
| Alternative Flow | A1 Compact vs full by role |
| Exception Flow | E1 Reorder manual → tolak. E2 Event hilang vs Audit → defect integritas (bisnis: jangan diam) |
| Business Rules | R11 |
| Acceptance Criteria | §9 AC-07… |

---

# 9 Acceptance Criteria

Kriteria bersifat terukur. Item bertanda **[LOCKED]** merujuk keputusan Mode A Delivery Baseline (DEC-MODEA-B2-001).

## Create Case / Add Case

| ID | Criterion |
|---|---|
| AC-01 | Given Complaint aktif non-`CLOSED` dan aktor berwenang, when Create Case dengan atribut wajib lengkap, then Case baru terbentuk dengan Case Number format `CASE-YYYY-NNNN` dan status awal sesuai BR-CM-CAT-001 serta entri Timeline “Case Created” + Audit ada. **[LOCKED BQ-004]** |
| AC-02 | Given Complaint Batch-1 `REGISTERED` tanpa Case, when Create Case sukses, then jumlah Case pada Complaint = 1 dan status Complaint = `IN_PROGRESS`. |
| AC-03 | Given Complaint sudah punya N Case dan N < 5, when Add Case, then N menjadi N+1 tanpa Complaint baru; when N = 5, Add Case ditolak. **[LOCKED BQ-003]** |
| AC-04 | Given Complaint `CLOSED`, when Create/Add Case, then ditolak dan Case tidak bertambah. |
| AC-05 | Given upaya membuat Case tanpa Complaint induk, when divalidasi, then ditolak 100% percobaan. |
| AC-05b | Given Complaint `REGISTERED` tanpa Case melewati **1 business day**, when Supervisor Queue dibuka, then Complaint muncul sebagai aging exceedance. **[LOCKED BQ-002]** |

## View Case / Timeline

| ID | Criterion |
|---|---|
| AC-06 | Given aktor berwenang, when View Case, then ditampilkan minimal: Case Number, status, Complaint induk, CustomerId, prioritas/tipe (yang ada). |
| AC-07 | Given CaseId tidak milik Complaint konteks, when View/attach konteks silang, then ditolak. |
| AC-08 | Given minimal satu write Case sukses, when View Timeline, then event terkait write tersebut muncul berurut waktu dan tidak dapat diedit ulang oleh user. |

## Update Status

| ID | Criterion |
|---|---|
| AC-09 | Given matriks status BR-CM-CAT-001 terkunci (BQ-001 LOCKED), when transisi allowed, then status berubah tepat ke target dan Timeline+Audit tercatat. |
| AC-10 | Given transisi forbidden per BR-CM-CAT-001, when attempted, then status tidak berubah. |
| AC-11 | Given Mode A, when Assignment dilakukan, then hanya **Unit level**; Assigned User ditolak / di luar Mode A. **[LOCKED BQ-006]** |
| AC-11b | Given Mode A Delivery, when aktor mencoba expose `PENDING`/`ESCALATED`, then delivery tidak mengekspos state tersebut (matrix tetap mendefinisikan). **[LOCKED BQ-009]** |
| AC-11c | Given Mode A, when Cancel Case dengan alasan Duplicate / Wrong Input / Customer Cancellation, then Case → `CANCELLED`. **[LOCKED BQ-014]** |

## Resolution / Close

| ID | Criterion |
|---|---|
| AC-12 | Given Case eligible, Comment hadir, resolusi lengkap, when Resolve, then Case berstatus `RESOLVED`. **[LOCKED BQ-008 / BQ-010]** |
| AC-13 | Given evidence wajib kategori tidak ada, when Resolve, then ditolak dan status Case tidak menjadi Resolved/Closed. |
| AC-14 | Given Case `RESOLVED` dan Supervisor Approval selesai, when Close Case, then Case = `CLOSED` dengan closedBy + timestamp. **[LOCKED BQ-008]** |
| AC-15 | Given Close Case sukses dan masih ada Case lain open pada Complaint yang sama, when dicek, then status Complaint **tidak** menjadi `CLOSED` semata karena close satu Case. |
| AC-16 | Given Close Case pada Case terakhir open, when dicek, then Complaint **tetap terbuka** (Close Case ≠ auto Complaint Closure). **[LOCKED BQ-007]** |

## SLA / Assignment scope honesty

| ID | Criterion |
|---|---|
| AC-17 | Given CAP-008 tanpa SLA Engine, when Create Case, then SLA Policy Version **bound** dan countdown **NOT** activated; breach Working Day tidak dihitung. **[LOCKED BQ-005]** |
| AC-18 | Given CAP-008 tanpa Assignment Engine, when Create Case, then sistem **tidak** menjalankan auto-route/claim/bulk reassignment; Unit assignment only. **[LOCKED BQ-006]** |

## Mode / non-goals

| ID | Criterion |
|---|---|
| AC-19 | Mode B flows tidak menjadi acceptance CAP-008. |
| AC-20 | Tidak ada AC yang mensyaratkan Dashboard, Reporting, Notification Engine, atau AI. |

---

# 10 Open Questions

**Residual Business Questions for Mode A Delivery Baseline: ZERO.**

BQ-CAP02-001 … BQ-CAP02-014 semuanya **LOCKED** (DEC-BQ001; DEC-MODEA-B2-001). Tidak ada BQ terbuka yang memblokir authoring FRD Batch-2 Mode A.

Prinsip Aggregate Batch-1 yang sudah dikunci tetap **LOCKED**. Mode B tetap **CLOSED**.

---

## Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-08-01 | ECMP Product Team (PO/BA/SA) | Initial BCS CAP-02 dari SoT BR-CM-CAT-001 + FRD-CM-001; koreksi istilah Add Case; daftar BQ blocking; status BUSINESS LOCK NOT READY |
| 1.1 | 2026-08-01 | ECMP Product Owner | BU-03: sync setelah BU-01/02/04 — BQ-001 LOCKED (DEC-BQ001 O3); BQ-013 LOCKED (BR-CM-CAT Locked); §7 State Machine = SoT BR-CM-CAT; status **BUSINESS LOCK READY** |
| 1.2 | 2026-08-01 | Repository Synchronization Coordinator | DEC-MODEA-B2-001: lock BQ-002…012,014 + countersign BQ-007/011; rename capability ID **CAP-008**; Residual BQ **ZERO**; FRD Batch-2 prerequisite **READY** |

---

## BUSINESS LOCK VERDICT

# BUSINESS LOCK READY

### Locked (Board Unlock + Mode A Delivery Baseline)

1. **BQ-CAP02-001** — **LOCKED** — DEC-BQ001 Option O3.
2. **Case Aggregate Transition Matrix** — SoT di BR-CM-CAT-001.
3. **BQ-CAP02-013** — **LOCKED** — BR-CM-CAT-001 Status = Locked.
4. **§7 State Machine** — merujuk BR-CM-CAT-001 sebagai official SoT.
5. **BQ-CAP02-002 … BQ-CAP02-012, BQ-CAP02-014** — **LOCKED** — DEC-MODEA-B2-001 (Product Owner Decision Session 2026-08-01).
6. **Capability ID** — **CAP-008** (former `CAP-02` retired).

### Residual open questions (Mode A Delivery Baseline)

**NONE (ZERO).**

### FRD Batch-2 prerequisite

**READY** — residual BQ gate cleared. Authoring FRD Batch-2 Mode A may proceed from this baseline. This BCS is not the FRD.
