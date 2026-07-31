# ENTERPRISE TARGET ARCHITECTURE
## Complaint Management Module — Future State Blueprint

| Field | Value |
|---|---|
| Document ID | **EA-TARGET-CM-001** |
| Program pack | `../../18 Architecture Governance/ECMP_PROGRAM_BOARD_008_EA_TARGET_PLATFORM_Draft_Pack_v0.1.md` |
| Version | 1.0 |
| Date | 2026-07-31 |
| Lifecycle (BR-002) | **DRAFT** — Architecture Board intake (bukan BASELINE / SoT) |
| Status | 🟡 **Draft for Architecture Board** — pelengkap ADR-014…018; **bukan** tiket implementasi |
| Owner | Chief Enterprise Architect |
| Reviewer | Chief Solution Architect · Integration Architect · Security Architect · Enterprise Application Owner |
| Approver | Architecture Board **dan** pemilik Enterprise Application (bilateral) |
| Companion index | `../../26 Traceability/ECMP_DTM_001_Decision_Traceability_Matrix_v0.1.md` |
| Scope | **Hanya** Complaint Management Module. Enterprise Application dianggap sudah ada dan tidak diubah |
| Supersedes | Tidak ada. Melengkapi ADR-014 v1.4, ADR-015 v1.3, ADR-016/017/018 — **tidak** menggantikan ADR Accepted |

---

## Board framing (wajib dibaca)

| Aturan | Isi |
|---|---|
| **Bukan tiket coding** | Body BAB 6–18 = *target state*. Sprint 1+ **tidak** boleh dijadwalkan sebagai work item engineering sampai gate di bawah hijau. |
| **Mode B tetap CLOSED** | PROGRAM-BOARD-006 **C-B6-1** / **C-7** — Identity Adapter, Entitlement Gate runtime, org sync produk, OpenAPI enterprise `securitySchemes`, SSO UI = **BLOCKED** sampai Board Resolution membuka. |
| **HOST-first** | Seluruh `[ASUMSI]` / `[BUTUH INFO]` sisi Enterprise Application (K1–K11, F1–F4) **harus** terselesaikan atau di-waiver Board **sebelum** implementasi yang bergantung pada kontrak tersebut. Lihat DTM-001 kolom *HOST dependency*. |
| **Mode A parallel** | Delivery Mode A (AUTHORIZED WITH CONDITIONS) boleh lanjut di jalur terpisah; **bukan** pengganti menyelesaikan asumsi HOST. |
| **DEC-020** | Konvergensi dual-SoT tanpa Retirement DEC — **dilarang** force-merge / silent foundation cutover. |

## Konvensi label

| Label | Arti |
|---|---|
| **[FAKTA]** | Terbukti dari file repository |
| **[DESAIN]** | Keputusan desain target yang diusulkan dokumen ini |
| **[ASUMSI]** | Dugaan yang belum didukung bukti — wajib dikonfirmasi |
| **[BUTUH INFO]** | Informasi yang belum tersedia; disertai penyedia dan alasan |

> **Peringatan governance.** Dokumen ini mendesain *target state*. Ia **tidak** mengotorisasi implementasi. PROGRAM-BOARD-006 **C-B6-1** dan **C-7** menyatakan Mode B *"coding not authorized"*. Seluruh isi dokumen ini tunduk pada pembukaan C-7 **dan** penutupan HOST assumptions (lihat BAB 18 / DTM-001).

---

# BAB 1 — VISION

## 1.1 Pernyataan visi

> **Complaint Management Module adalah satu-satunya tempat di dalam Enterprise Application di mana makna sebuah keluhan pelanggan didefinisikan, dijaga, dan dipertanggungjawabkan — dan bukan tempat lain untuk apa pun selain itu.**

## 1.2 Tujuan modul

| # | Tujuan |
|---|---|
| V1 | Menerima keluhan dari seluruh kanal yang disediakan Enterprise Application, dan menjadikannya satu catatan bisnis yang dapat ditelusuri |
| V2 | Menjamin setiap keluhan memiliki pemilik, tenggat, dan jalur eskalasi yang jelas |
| V3 | Menegakkan aturan bisnis keluhan (SLA, eskalasi, resolusi, penutupan) secara konsisten tanpa bergantung pada disiplin manusia |
| V4 | Menyediakan bukti penanganan yang dapat diaudit sepanjang siklus hidup keluhan |
| V5 | Memublikasikan fakta domain keluhan agar kapabilitas lain di Enterprise Application dapat menggunakannya tanpa menyalin logikanya |

## 1.3 Nilai bisnis

**[FAKTA]** — Business Blueprint v2.1 (DEC-001) mendefinisikan ECMP sebagai *end-to-end complaint & inquiry management*.

| # | Nilai |
|---|---|
| N1 | **Kepatuhan** — bukti penanganan keluhan lengkap dan tidak dapat disangkal |
| N2 | **SLA terukur** — komitmen waktu ke pelanggan dapat dijanjikan karena ditegakkan sistem |
| N3 | **Akuntabilitas** — setiap perpindahan tanggung jawab tercatat (assignment, escalation, resolution) |
| N4 | **Satu kebenaran** — seluruh unit organisasi melihat status keluhan yang sama |
| N5 | **Efisiensi** — modul tidak membangun ulang autentikasi, notifikasi, penyimpanan, atau pelaporan yang sudah ada |

## 1.4 Mengapa modul ini ada — dan mengapa bukan aplikasi

**[FAKTA]** — ADR-014 v1.4 §Problem Statement mendaftar akibat bila ECMP mempertahankan identitas sendiri: halaman login ganda, basis pengguna ganda, reset password terpisah, logout tidak konsisten, audit identitas terfragmentasi.

**[DESAIN]** Prinsip pendirian modul:

> Keluhan adalah **proses bisnis**, bukan sistem. Proses bisnis membutuhkan tempat tinggal, bukan rumah sendiri.

## 1.5 Non-tujuan (eksplisit)

Modul ini **tidak** bertujuan menjadi: sistem identitas · master pelanggan (ADR-002) · master organisasi · mesin workflow umum · mesin notifikasi umum · portal · sistem pelaporan enterprise · penyimpanan berkas.

---

# BAB 2 — ENTERPRISE CONTEXT

## 2.1 Posisi modul

```
┌──────────────────────────────────────────────────────────────────────┐
│                      ENTERPRISE APPLICATION                          │
│                        (sudah ada, tidak diubah)                     │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │  EXPERIENCE LAYER                                              │  │
│  │  Portal · Shell · Navigation · Theme · Shared UI · Layout      │  │
│  └───────────────────────────┬────────────────────────────────────┘  │
│                              │ (embed / mount)                       │
│  ┌───────────────────────────┴────────────────────────────────────┐  │
│  │  SHARED SERVICES                                               │  │
│  │  Identity · SSO · Entitlement · Organization · User Directory  │  │
│  │  Notification · Audit Store · Logging · Monitoring             │  │
│  │  Workflow Engine · Scheduler · Search Index · File Service     │  │
│  │  Configuration · Reporting Surface · Event Bus                 │  │
│  └───────────────────────────┬────────────────────────────────────┘  │
│                              │ (kontrak: token, API, event)          │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
        ╔══════════════════════▼═══════════════════════════════════╗
        ║      COMPLAINT MANAGEMENT MODULE (yang didesain)         ║
        ║                                                          ║
        ║  ┌────────────────────────────────────────────────────┐  ║
        ║  │ INTEGRATION LAYER (Adapters — port ke Enterprise)  │  ║
        ║  │ Identity · Entitlement · Organization · Notify     │  ║
        ║  │ Audit · File · Search · Config · Telemetry · Event │  ║
        ║  └───────────────────────┬────────────────────────────┘  ║
        ║  ┌───────────────────────▼────────────────────────────┐  ║
        ║  │ APPLICATION LAYER (use case, orkestrasi)           │  ║
        ║  └───────────────────────┬────────────────────────────┘  ║
        ║  ┌───────────────────────▼────────────────────────────┐  ║
        ║  │ DOMAIN LAYER (Complaint BC — invariant & aturan)   │  ║
        ║  │ Complaint · Assignment · Escalation · Resolution   │  ║
        ║  │ SLA · Timeline · Attachment(meta) · Appointment    │  ║
        ║  └───────────────────────┬────────────────────────────┘  ║
        ║  ┌───────────────────────▼────────────────────────────┐  ║
        ║  │ PERSISTENCE (hanya tabel domain keluhan)           │  ║
        ║  └────────────────────────────────────────────────────┘  ║
        ╚══════════════════════════════════════════════════════════╝
```

## 2.2 Hubungan antar komponen

| Dari | Ke | Sifat | Arah |
|---|---|---|---|
| Portal Enterprise | UI Modul | Embed / mount | Enterprise → Modul |
| Identity Enterprise | Identity Adapter | Token (OIDC) | Enterprise → Modul |
| Entitlement Enterprise | Entitlement Gate | Klaim atau API | Enterprise → Modul |
| Organization Enterprise | Org Adapter | Sinkronisasi referensi | Enterprise → Modul |
| Modul | Notification Enterprise | Perintah kirim (intent) | Modul → Enterprise |
| Modul | Audit Store Enterprise | Event audit | Modul → Enterprise |
| Modul | Search Index Enterprise | Proyeksi terindeks | Modul → Enterprise |
| Modul | File Service Enterprise | Simpan/ambil berkas | Modul → Enterprise |
| Modul | Event Bus Enterprise | Domain event | Modul → Enterprise |
| Modul | Telemetry Enterprise | Log, metric, trace | Modul → Enterprise |

**[DESAIN]** Aturan arah: **modul tidak pernah memanggil modul lain secara langsung.** Semua komunikasi antar-modul melalui Enterprise Application (event bus atau API terdaftar).

## 2.3 Prinsip pemisahan yang menyelesaikan konflik kepemilikan

**[DESAIN] — prinsip inti dokumen ini:**

> **Enterprise Application memiliki KAPABILITAS. Modul memiliki MAKNA.**

Audit sebelumnya menemukan konflik: brief menyerahkan Authorization, Notification, Dashboard, Audit, Workflow, dan Search ke Enterprise, sementara ADR-014 v1.4 (Approved) memberikan *Complaint Authorization* dan *Complaint KPI* ke ECMP.

Konflik itu **larut** ketika kapabilitas dipisahkan dari semantik:

| Kapabilitas | Enterprise memiliki | Modul memiliki |
|---|---|---|
| Authorization | Entitlement ke modul; identitas; mekanisme | Arti "boleh mengeskalasi keluhan" |
| Notification | Kanal, template engine, pengiriman, preferensi global | Kapan keluhan layak memicu pemberitahuan, dan isinya |
| Dashboard / Reporting | Permukaan, agregasi lintas-modul, distribusi | Definisi metrik keluhan (apa itu "breach", "aging") |
| Audit | Penyimpanan, retensi, pencarian, non-repudiation | Peristiwa domain apa yang layak diaudit |
| Workflow | Mesin, penjadwalan, retry, kompensasi | State machine keluhan dan invariannya |
| Search | Index, query engine, ranking | Apa yang layak dicari dan bagaimana diproyeksikan |
| File | Penyimpanan, enkripsi, antivirus, kuota | Kebijakan lampiran keluhan (tipe, jumlah, keterkaitan) |

**Konsekuensi:** ADR-014 dan brief keduanya benar pada level yang berbeda. Rekomendasi: adopsi prinsip ini sebagai klarifikasi resmi, bukan revisi ADR-014.

---

# BAB 3 — MODULE BOUNDARY

## 3.1 Tanggung jawab modul (IN)

| # | Tanggung jawab | Alasan |
|---|---|---|
| I1 | Siklus hidup keluhan: register → triage → assign → process → escalate → resolve → close → reopen | Inti domain |
| I2 | Invarian & aturan bisnis keluhan (BR-CM-*) | Tidak dapat didelegasikan tanpa kehilangan makna |
| I3 | Assignment & kepemilikan penanganan | Domain |
| I4 | Eskalasi berjenjang (cabang → pusat) | Domain, per DEC-F4 |
| I5 | Perhitungan SLA, tenggat, deteksi breach | Domain |
| I6 | Resolusi & penutupan, termasuk `result_visibility` | Domain |
| I7 | Timeline keluhan (riwayat domain, **bukan** audit sistem) | Domain |
| I8 | Metadata & kebijakan lampiran keluhan | Domain; **byte** disimpan Enterprise |
| I9 | Appointment terkait eskalasi | Domain |
| I10 | Antrian kunjungan (queue/ticket) — **[ASUMSI]** milik domain layanan keluhan | Perlu konfirmasi (§3.4) |
| I11 | **Complaint Permission Matrix** — arti setiap izin di dalam modul | ADR-014 + ADR-008 |
| I12 | Definisi metrik keluhan | Semantik, bukan permukaan |
| I13 | Publikasi domain event keluhan | Kontrak keluar |
| I14 | Preferensi pengguna ber-scope modul | ADR-014 |

## 3.2 BUKAN tanggung jawab modul (OUT)

| # | Bukan tanggung jawab | Pemilik |
|---|---|---|
| O1 | Autentikasi, SSO, MFA, sesi, logout | Enterprise |
| O2 | Direktori pengguna, password, provisioning identitas | Enterprise |
| O3 | Struktur organisasi (organization/branch/department) | Enterprise |
| O4 | Entitlement akses ke modul | Enterprise |
| O5 | Portal, shell, navigasi, tema, komponen UI bersama | Enterprise |
| O6 | Pengiriman notifikasi (kanal, template engine, retry) | Enterprise |
| O7 | Penyimpanan audit, retensi, pencarian audit | Enterprise |
| O8 | Logging sink, metrics store, tracing backend, alerting | Enterprise |
| O9 | Mesin workflow umum, scheduler | Enterprise |
| O10 | Index & mesin pencarian | Enterprise |
| O11 | Penyimpanan berkas, antivirus, enkripsi at-rest | Enterprise |
| O12 | Konfigurasi lintas-modul | Enterprise |
| O13 | Permukaan dashboard & distribusi laporan | Enterprise |
| O14 | Master data pelanggan | Enterprise (ADR-002) |
| O15 | Event bus / broker | Enterprise |

## 3.3 Yang dihapus dari repository saat ini

**[FAKTA]** modul-modul berikut ada di `backend/app/modules` dan menamai dirinya sendiri sebagai platform/foundation/reusable:

| Modul | LOC | Docstring |
|---|---:|---|
| `auth` | 1.025 | AuthN lokal |
| `users` | 966 | Direktori pengguna |
| `iam` | 3.029 | Role/Permission/UserRole/DataScope storage |
| `branches` | 127 | Master organisasi |
| `notification` | 2.281 | *"Notification **platform module**"* |
| `audit` | 635 | *"Audit Log **platform service**"* |
| `search` | 494 | *"**reusable** Search & Filtering"* |
| `settings` | 466 | *"System Settings"* |
| `workflow` | 553 | *"Workflow **Foundation**"* |
| `execution` | 1.862 | *"Execution **Foundation**"* |
| `delivery` | 415 | *"**Shared** delivery preparation infrastructure"* |
| `transport` | 269 | *"Provider abstraction"* |
| `provider_executor` | 343 | *"**Generic** execution layer"* |
| `provider_contract` | 290 | *"**Reusable** contracts"* |
| `email` | 130 | Abstraksi email |
| **Total** | **±12.900** | |

**[DESAIN]** Seluruhnya digantikan **adapter tipis** ke kapabilitas Enterprise. Perkiraan pengganti: ±1.500 LOC adapter. **Penghematan neto ±11.400 LOC yang tidak perlu dirawat.**

## 3.4 Batas yang masih harus diputuskan

**[BUTUH INFO]**

| # | Pertanyaan | Penyedia | Mengapa penting |
|---|---|---|---|
| Q1 | Apakah `queue` (antrian kunjungan cabang, 4.434 LOC) domain keluhan atau layanan pelanggan umum? | Business Owner + Enterprise App Owner | Menentukan 13% backend tetap atau pindah |
| Q2 | Apakah Enterprise memiliki *Case/Ticket* generik yang beririsan dengan Complaint? | Enterprise App Owner | Risiko duplikasi konsep inti |
| Q3 | Apakah Appointment milik modul atau kapabilitas penjadwalan Enterprise? | Enterprise App Owner | 909 LOC |

---

# BAB 4 — CAPABILITY OWNERSHIP MATRIX

**[DESAIN]** Ini artefak yang menutup blocker **BLK-C1**. Disusun memakai prinsip §2.3.

Legenda **Integration Method**: `TOKEN` = klaim di access token · `API` = panggilan sinkron · `EVENT` = asinkron via bus · `EMBED` = penanaman UI · `SYNC` = replikasi referensi berkala · `LOCAL` = sepenuhnya di dalam modul

| # | Capability | Owner | Consumer | Integration Method | Status | Reason |
|---:|---|---|---|---|---|---|
| 1 | **Authentication** | Enterprise | Modul | `TOKEN` (OIDC RS256) | 🟡 Validator ada; issuer nyata belum | ADR-014: AuthN eksternal |
| 2 | **Entitlement ke modul** | Enterprise | Modul | `TOKEN` atau `API` | 🔴 Belum ada | ADR-014/017: AuthN saja tidak memberi akses |
| 3 | **Authorization dalam modul** | **Modul** | Modul | `LOCAL` | 🟢 Ada (`PermissionResolver`) | ADR-014 + ADR-008: arti izin milik domain |
| 4 | **Identity (SoT)** | Enterprise | Modul | `TOKEN` + `API` | 🔴 `external_user_id` belum ada | ADR-015 |
| 5 | **User profile modul** | **Modul** | Modul | `LOCAL` | 🟡 Ada tapi bercampur direktori | ADR-014: preferensi modul |
| 6 | **User Directory** | Enterprise | Modul | `API` + `SYNC` | 🔴 Modul masih punya CRUD | ADR-014 |
| 7 | **Organization / Branch / Department** | Enterprise | Modul | `SYNC` | 🔴 `branches` masih master | ADR-014 + ADR-018 |
| 8 | **Session & logout** | Enterprise | Modul | `TOKEN` + `EVENT` | 🔴 Modul punya `refresh_tokens` | ADR-014 |
| 9 | **Notification delivery** | Enterprise | Modul | `EVENT` atau `API` | 🔴 Modul punya engine sendiri | Kapabilitas ≠ makna |
| 10 | **Notification intent keluhan** | **Modul** | Enterprise | `EVENT` | 🟡 Sebagian | Makna domain |
| 11 | **Audit store** | Enterprise | Modul | `EVENT` | 🔴 Modul punya tabel sendiri | Kapabilitas |
| 12 | **Audit event keluhan** | **Modul** | Enterprise | `EVENT` | 🟢 `security_events` ada | Makna domain |
| 13 | **Logging sink** | Enterprise | Modul | `stdout` JSON | 🟡 Format ✅ sink ❌ | Kapabilitas |
| 14 | **Monitoring / Metrics / Tracing** | Enterprise | Modul | `API` / agen | 🔴 Nol | Kapabilitas |
| 15 | **Workflow engine** | Enterprise | Modul | `API` / `EVENT` | 🔴 Modul punya 3.632 LOC sendiri | Kapabilitas |
| 16 | **Complaint state machine** | **Modul** | Modul | `LOCAL` | 🟢 `lifecycle.py` | Invarian domain |
| 17 | **Scheduler** | Enterprise | Modul | `API` / callback | 🔴 Tidak ada | Kapabilitas |
| 18 | **Search index** | Enterprise | Modul | `EVENT` (proyeksi) | 🔴 Modul punya `search` sendiri | Kapabilitas |
| 19 | **Definisi searchable keluhan** | **Modul** | Enterprise | `EVENT` | 🟡 | Makna domain |
| 20 | **Reporting surface** | Enterprise | Modul | `EVENT` / `API` | 🔴 Modul punya `reports` | Kapabilitas |
| 21 | **Dashboard surface** | Enterprise | Modul | `EMBED` / `API` | 🔴 Modul punya `dashboard` | Kapabilitas |
| 22 | **Definisi metrik keluhan (KPI)** | **Modul** | Enterprise | `API` / `EVENT` | 🟢 `kpi` ada | ADR-014: Complaint KPI = ECMP |
| 23 | **Configuration lintas-modul** | Enterprise | Modul | `API` | 🔴 Modul punya `settings` | Kapabilitas |
| 24 | **Configuration domain keluhan** | **Modul** | Modul | `LOCAL` | 🟡 Bercampur | SLA policy, kategori |
| 25 | **File storage** | Enterprise | Modul | `API` | 🔴 `LocalStorageProvider` | Kapabilitas |
| 26 | **Attachment metadata & policy** | **Modul** | Modul | `LOCAL` | 🟢 Ada | Makna domain |
| 27 | **Antivirus** | Enterprise | Modul | `API` | 🔴 Stub selalu clean | Kapabilitas |
| 28 | **Complaint** | **Modul** | Enterprise | `API` + `EVENT` | 🟡 3 model paralel | Inti domain |
| 29 | **Complaint Timeline** | **Modul** | Modul | `LOCAL` | 🟡 2 model | Domain, bukan audit |
| 30 | **Complaint SLA** | **Modul** | Modul | `LOCAL` | 🟡 2 model | Domain |
| 31 | **Complaint Escalation** | **Modul** | Modul | `LOCAL` | 🟡 2 model | Domain |
| 32 | **Complaint Assignment** | **Modul** | Modul | `LOCAL` | 🟡 2 model | Domain |
| 33 | **Complaint Resolution** | **Modul** | Modul | `LOCAL` | 🟢 | Domain |
| 34 | **Complaint Analytics** | **Modul** | Enterprise | `API` / `EVENT` | 🟢 | ADR-014 |
| 35 | **Customer (master)** | Enterprise | Modul | `API` | 🟡 Adapter ada, stub | ADR-002 |
| 36 | **Appointment** | **Modul** *(sementara)* | Modul | `LOCAL` | 🟡 | §3.4 Q3 |
| 37 | **Queue / Ticket kunjungan** | **Modul** *(sementara)* | Modul | `LOCAL` | 🟡 | §3.4 Q1 |
| 38 | **Master data referensi** | Enterprise | Modul | `SYNC` | 🔴 | Kapabilitas |
| 39 | **Permission (storage)** | **Modul** | Modul | `LOCAL` | 🟢 | ADR-008 |
| 40 | **Role (enterprise)** | Enterprise | Modul | `TOKEN` | 🟢 `RoleMapper` menolak privileged | ADR-015 §6 |
| 41 | **Role (modul)** | **Modul** | Modul | `LOCAL` | 🟢 | ADR-014 |
| 42 | **Theme** | Enterprise | Modul | `EMBED` | 🔴 Modul punya sendiri | Konsistensi UX |
| 43 | **Layout / Shell** | Enterprise | Modul | `EMBED` | 🔴 Modul punya sendiri | Kapabilitas |
| 44 | **Navigation / Menu** | Enterprise | Modul | `EMBED` + manifest | 🔴 `nav.ts` milik modul | Kapabilitas |
| 45 | **Settings UI** | Enterprise | Modul | `EMBED` | 🔴 | Kapabilitas |
| 46 | **Event bus** | Enterprise | Modul | `EVENT` | 🔴 Outbox tanpa consumer | Kapabilitas |

**Ringkasan:** dari 46 kapabilitas — **17 milik Modul**, **29 milik Enterprise**. Saat ini modul mengimplementasikan sendiri ±20 kapabilitas milik Enterprise.

---

# BAB 5 — DOMAIN MODEL

**[FAKTA]** `backend/app/modules/complaint/domain/models.py` sudah memakai `@dataclass(frozen=True, slots=True)` — objek domain immutable. Ini fondasi DDD yang benar dan **dipertahankan**.

## 5.1 Bounded Context

**[DESAIN]** Target: **satu** BC utama + dua BC pendukung.

| BC | Isi | Catatan |
|---|---|---|
| **Complaint** (inti) | Complaint, Assignment, Escalation, Resolution, SLA, Timeline, Attachment(meta) | Hasil konvergensi DEC-020 dari 3 model paralel |
| **Appointment** (pendukung) | Appointment, CheckIn, Completion, NoShow | Pending §3.4 Q3 |
| **Queue** (pendukung) | Queue, QueueTicket, Counter | Pending §3.4 Q1 |

## 5.2 Aggregate

| Aggregate Root | Invarian utama | Entity di dalamnya |
|---|---|---|
| **Complaint** | Status hanya berpindah lewat transisi sah; satu assignment aktif; SLA terikat kebijakan saat registrasi | Assignment, Escalation, Resolution, ComplaintSLA, TimelineEntry, AttachmentRef |
| **SLAPolicy** | Kebijakan aktif unik per (kategori, prioritas) | — |
| **Appointment** | Tidak dapat check-in sebelum dijadwalkan; tidak dapat complete sebelum check-in | — |
| **Queue** | Nomor tiket monoton per hari per counter | QueueTicket, Counter |

**[DESAIN]** Aturan: **satu transaksi = satu aggregate.** Konsistensi lintas-aggregate lewat domain event.

## 5.3 Value Object

**[FAKTA]** sudah ada: `ComplaintStatus`, `ComplaintPriority`, `AssigneeType`, `EscalationLevel`.

**[DESAIN]** ditambahkan: `ComplaintNumber` · `SLADeadline` · `OrgUnitRef` · `ExternalUserRef` · `CustomerRef` · `AttachmentRef` · `ResultVisibility` · `EscalationReason`

**[DESAIN] penting:** `ExternalUserRef`, `OrgUnitRef`, dan `CustomerRef` adalah **referensi opaque** ke entitas milik Enterprise — modul tidak menyimpan atributnya, hanya identitasnya.

## 5.4 Business Rule

**[FAKTA]** — `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-CM-CAT-001 v1.1) dan BR-003 / BR-CRM-01 / BR-CRM-02.

**[DESAIN]** Aturan penempatan:

| Jenis aturan | Lapisan |
|---|---|
| Invarian aggregate (selalu benar) | **Domain** — di dalam aggregate |
| Aturan lintas-aggregate | **Domain Service** |
| Aturan orkestrasi / urutan use case | **Application** |
| Aturan otorisasi | **Integration** (gate) + Permission Matrix |
| Aturan format / validasi input | **API layer** |

## 5.5 Domain Event

**[FAKTA]** — `08 Event Catalog/events/events.yaml` (EVT-CAT-001 v0.7, Status **Approved**, SoT normatif), 40 event, `delivery_guarantee: at-least-once (ADR-001); all consumers MUST be idempotent`.

**[DESAIN]** Katalog ini **dipertahankan sebagai kontrak keluar modul**. Detail di BAB 10.

## 5.6 Domain Service

| Service | Tanggung jawab |
|---|---|
| `ComplaintLifecycleService` | Validasi transisi status |
| `SLACalculationService` | Tenggat dari kebijakan + kalender kerja |
| `EscalationRoutingService` | Menentukan target eskalasi berdasarkan hierarki org |
| `AssignmentPolicyService` | Kelayakan penerima tugas |
| `DuplicateDetectionService` | **[FAKTA]** sudah ada di `cm_batch1/duplicate_engine.py` |

## 5.7 Repository (port di domain)

```
ComplaintRepository · AssignmentRepository · EscalationRepository
SLARepository · SLAPolicyRepository · TimelineRepository
AttachmentMetadataRepository · AppointmentRepository · QueueRepository
```

**[DESAIN]** Seluruhnya `Protocol`/ABC di lapisan domain; implementasi SQLAlchemy di infrastructure. **[FAKTA]** pola ini sudah diterapkan di `complaint/domain/repositories.py`.

---

# BAB 6 — TARGET BACKEND ARCHITECTURE

## 6.1 Gaya arsitektur

**[DESAIN]** **Modular Monolith** dengan **Hexagonal (Ports & Adapters)** di dalam, **satu deployable unit**.

**Alasan menolak microservice:**

| Kriteria | Penilaian |
|---|---|
| Ukuran tim | Satu tim — microservice menambah biaya operasi tanpa manfaat |
| Batas transaksi | Aggregate keluhan sering butuh konsistensi kuat — distribusi menambah kompleksitas |
| Enterprise sudah menyediakan | Bus, scheduler, observability — modul tidak perlu jadi mesh |
| **[FAKTA]** ADR-009 | Message broker sengaja ditunda |
| Kebutuhan skala | **TIDAK DAPAT DIVERIFIKASI** — tidak ada uji beban di repository |

**Modul tetap satu unit; batas ditegakkan oleh struktur paket dan lint, bukan oleh jaringan.**

## 6.2 Struktur folder target

```
backend/
├── app/
│   ├── main.py
│   ├── bootstrap/                 ← wiring, DI container, lifespan
│   │
│   ├── domain/                    ← MURNI. Tanpa import framework/ORM/HTTP
│   │   ├── complaint/             (aggregate, VO, event, rule, repo port)
│   │   ├── appointment/
│   │   ├── queue/
│   │   └── shared/                (Identifier, Money, DateRange, Result)
│   │
│   ├── application/               ← use case, orkestrasi, DTO
│   │   ├── complaint/  (commands/ queries/ services/ dto/)
│   │   ├── appointment/
│   │   └── queue/
│   │
│   ├── ports/                     ← KONTRAK KELUAR (Protocol saja)
│   │   ├── identity.py            IdentityProvider
│   │   ├── entitlement.py         EntitlementProvider
│   │   ├── organization.py        OrganizationDirectory
│   │   ├── notification.py        NotificationPublisher
│   │   ├── audit.py               AuditPublisher
│   │   ├── file_storage.py        FileStorage
│   │   ├── search_index.py        SearchIndexPublisher
│   │   ├── configuration.py       ConfigurationProvider
│   │   ├── telemetry.py           MetricsSink, TraceSink
│   │   ├── event_bus.py           DomainEventPublisher
│   │   ├── scheduler.py           SchedulerClient
│   │   └── customer.py            CustomerProvider   ← [FAKTA] sudah ada
│   │
│   ├── adapters/                  ← IMPLEMENTASI PORT
│   │   ├── enterprise/            (Mode B — ke Enterprise Application)
│   │   ├── standalone/            (Mode A — harness dev/CI saja)
│   │   └── inmemory/              (test)
│   │
│   ├── infrastructure/            ← persistence milik modul
│   │   ├── persistence/  (orm/ repositories/ mappers/ migrations/)
│   │   └── outbox/
│   │
│   ├── api/                       ← HTTP adapter
│   │   ├── v1/complaints/ appointments/ queues/
│   │   ├── internal/              (health, ready, version, module manifest)
│   │   └── middleware/
│   │
│   └── security/                  ← pipeline otorisasi
│       ├── identity_adapter.py    ← [FAKTA] dinamai ADR-014
│       ├── entitlement_gate.py
│       ├── principal.py
│       ├── permission_matrix.py
│       ├── data_scope.py
│       └── org_scope.py
└── tests/  (unit/ integration/ contract/ e2e/)
```

## 6.3 Aturan dependensi (ditegakkan lint)

```
api ──► application ──► domain
 │           │             ▲
 │           ▼             │
 └──────► ports ◄──────────┘
             ▲
             │
         adapters ──► (Enterprise Application)

infrastructure ──► domain (implementasi repository port)
```

**[DESAIN]** Aturan wajib:

| # | Aturan |
|---|---|
| D1 | `domain` **tidak** mengimpor apa pun di luar `domain/shared` dan stdlib |
| D2 | `application` mengimpor `domain` + `ports`; **tidak** mengimpor `adapters`/`infrastructure`/`api` |
| D3 | `adapters` mengimpor `ports`; **tidak** mengimpor `application`/`domain` internal |
| D4 | `api` mengimpor `application`; **tidak** mengimpor `domain` langsung |
| D5 | **Tidak ada** `security`/`bootstrap` yang diimpor oleh `domain` |
| D6 | Divergensi Mode A/B **hanya** di `adapters` + `bootstrap` |

**[FAKTA]** kondisi sekarang melanggar D5: `core/authorization/*` mengimpor `app.modules.iam` dan `app.modules.audit`. Target memperbaikinya lewat `ports`.

## 6.4 Contoh port

```python
# ports/entitlement.py
class EntitlementProvider(Protocol):
    def has_module_entitlement(self, subject: ExternalUserRef) -> bool: ...

# ports/notification.py
class NotificationPublisher(Protocol):
    def publish(self, intent: NotificationIntent) -> None: ...

# ports/file_storage.py
class FileStorage(Protocol):
    def put(self, content: bytes, meta: FileMeta) -> FileHandle: ...
    def get(self, handle: FileHandle) -> bytes: ...
    def delete(self, handle: FileHandle) -> None: ...
```

**[DESAIN]** Setiap port punya **tiga** implementasi: `enterprise` (produksi), `standalone` (dev/CI), `inmemory` (test). Default produksi **fail-closed** bila adapter enterprise tidak terkonfigurasi.

---

# BAB 7 — TARGET FRONTEND ARCHITECTURE

## 7.1 Pembagian

| Lapisan | Pemilik | Isi |
|---|---|---|
| **Shell** | Enterprise | Header, sidebar, breadcrumb, user menu, notifikasi global |
| **Navigation** | Enterprise | Menu didaftarkan modul lewat manifest |
| **Theme / Design tokens** | Enterprise | Warna, tipografi, spacing, dark mode |
| **Shared UI** | Enterprise | Button, Input, Modal, Table, Toast, Form |
| **Auth UI** | Enterprise | Login, logout, lupa/ubah password |
| **Business Component** | **Modul** | Form keluhan, daftar keluhan, timeline, panel SLA, dialog eskalasi |
| **Business Page** | **Modul** | Halaman yang dirakit dari business component |
| **Domain client** | **Modul** | Klien API keluhan, tipe, validasi |

## 7.2 Struktur target

```
frontend/
├── src/
│   ├── module.manifest.ts     ← rute, menu, izin, ikon (dibaca portal)
│   ├── entry.tsx              ← titik mount tunggal
│   ├── features/              ← [FAKTA] 12.170 baris — DIPERTAHANKAN
│   │   ├── complaints/ assignments/ escalations/ resolutions/
│   │   ├── appointments/ sla/ timeline/ attachments/ queue/ analytics/
│   ├── domain/                ← tipe & aturan tampilan
│   ├── api/                   ← klien HTTP (tanpa penanganan auth sendiri)
│   └── platform/              ← ADAPTER ke Enterprise UI (satu-satunya titik kontak)
│       ├── ui.ts              re-export komponen Enterprise
│       ├── auth.ts            useCurrentUser, usePermissions dari host
│       ├── navigation.ts      useNavigate dari host
│       ├── notification.ts    toast dari host
│       └── i18n.ts
└── (DIHAPUS: shared/ui, shared/layouts, shared/theme, app/login, app/forgot-password, …)
```

**[DESAIN]** `platform/` adalah **anti-corruption layer UI**. Bila Enterprise mengganti design system, hanya folder ini yang berubah.

## 7.3 Metode integrasi

**[BUTUH INFO] — kritikal**

| # | Informasi | Penyedia | Mengapa penting |
|---|---|---|---|
| F1 | Metode embed: module federation / iframe / route mount / build-time package | Enterprise App Owner | Menentukan seluruh struktur di §7.2 |
| F2 | Framework & versi host (React? versi?) | Enterprise App Owner | Kompatibilitas `features/**` |
| F3 | Kontrak design system / paket komponen | Enterprise App Owner | Isi `platform/ui.ts` |
| F4 | Format manifest modul | Enterprise App Owner | `module.manifest.ts` |

**[ASUMSI]** Host memakai React sehingga `features/**` (React 19 + TS) dapat dipakai ulang. **Bila host bukan React, seluruh 12.170 baris harus ditulis ulang** — ini risiko terbesar frontend dan harus dikonfirmasi lebih dulu.

---

# BAB 8 — DATABASE OWNERSHIP

**[FAKTA]** saat ini 33 tabel, 44 migrasi.

## 8.1 Milik Complaint Module (dipertahankan)

| Tabel target | Asal |
|---|---|
| `complaint_cases` | SoT hasil konvergensi DEC-020 |
| `complaint_case_assignments` | |
| `complaint_case_escalations` | |
| `complaint_resolutions` | |
| `complaint_sla_policies` | |
| `complaint_case_slas` | |
| `timeline_entries` | |
| `complaint_attachments` (metadata) | dari `attachments` |
| `appointments` | pending §3.4 Q3 |
| `queues`, `queue_tickets`, `queue_counters` | pending §3.4 Q1 |
| `complaint_categories` | **BARU** — [FAKTA] belum ada sebagai tabel |
| `outbox` | publikasi event |
| `idempotency_keys` | dari `cm_batch1_idempotency` |

## 8.2 Milik Enterprise Application (dihapus dari modul)

| Tabel | Pengganti |
|---|---|
| `users` | Identity Adapter + `external_user_id` |
| `refresh_tokens`, `password_reset_tokens` | Sesi Enterprise |
| `branches` | Org reference (§8.3) |
| `customers` | Customer API |
| `settings` | Configuration port |
| `audit_logs`, `audit_logs_legacy` | Audit event ke Enterprise |
| `notification_templates`, `notification_queue` | Notification port |

## 8.3 Referensi tersinkronisasi (read-only cache milik modul)

**[DESAIN]** Modul boleh menyimpan **cache referensi**, bukan master:

| Tabel | Isi | Sumber |
|---|---|---|
| `ref_org_units` | `external_id`, `parent_external_id`, `level`, `name`, `last_synced_at` | Organization Enterprise |
| `ref_users` | `external_user_id`, `display_name`, `last_synced_at` | User Directory Enterprise |
| `ref_customers` | `customer_id`, atribut minimal, `last_synced_at` | Customer Master (ADR-002) |

**[DESAIN]** Aturan cache: hanya-baca · wajib `last_synced_at` · **tidak boleh** menjadi FK target dari tabel domain (pakai kolom referensi opaque tanpa constraint lintas-kepemilikan) · basi > ambang → fail-closed pada operasi yang membutuhkannya.

## 8.4 Shared

**[DESAIN]** **Tidak ada tabel shared.** Modul memiliki skema sendiri; Enterprise memiliki skemanya. Tidak ada tabel yang ditulis dua pihak.

## 8.5 Masalah FK yang harus diselesaikan

**[FAKTA]** 16 FK menunjuk `users.id`, 4 di antaranya `ondelete="RESTRICT"`.

**[DESAIN]** Target: seluruh referensi aktor menjadi kolom `external_user_id` (string opaque) **tanpa FK**. Integritas dijaga aplikasi + adapter, bukan constraint lintas-sistem.

---

# BAB 9 — API CONTRACT

## 9.1 API yang DIMILIKI modul

**[FAKTA]** DEC-020 sudah menetapkan namespace `/api/v1/cm` (API-500…512).

**[DESAIN]** Seluruh API modul berada di bawah **satu namespace**:

| Grup | Contoh |
|---|---|
| Complaint | `POST /api/v1/cm/complaints` · `GET /{id}` · `PATCH /{id}` |
| Lifecycle | `POST /{id}/start` · `/resolve` · `/close` · `/reopen` |
| Assignment | `POST /{id}/assign` · `/reassign` · `/unassign` |
| Escalation | `POST /{id}/escalate` · `/escalations/{eid}/return` |
| SLA | `GET /{id}/sla` · `POST /{id}/sla/recalculate` |
| Timeline | `GET /{id}/timeline` |
| Attachment | `POST /{id}/attachments` (metadata; byte ke File Service) |
| Appointment | `POST /escalations/{id}/appointments` · `/check-in` · `/complete` |
| Queue | `GET /api/v1/cm/queues` · `/tickets` |
| Analytics | `GET /api/v1/cm/analytics/kpi` |

## 9.2 API yang DIKONSUMSI dari Enterprise

| # | API | Untuk | Status |
|---|---|---|---|
| C1 | OIDC discovery + JWKS | Validasi token | **[BUTUH INFO]** issuer nyata |
| C2 | Entitlement | Gate akses modul | **[BUTUH INFO]** mekanisme |
| C3 | User Directory | Profil + rekonsiliasi | **[BUTUH INFO]** |
| C4 | Organization | Hierarki org | **[BUTUH INFO]** |
| C5 | File Service | Simpan/ambil lampiran | **[BUTUH INFO]** |
| C6 | Notification | Kirim pemberitahuan | **[BUTUH INFO]** |
| C7 | Customer Master | Validasi pelanggan | **[FAKTA]** INT-001A RFI ada |
| C8 | Configuration | Config lintas-modul | **[BUTUH INFO]** |
| C9 | Scheduler | Job SLA breach | **[BUTUH INFO]** |

## 9.3 API yang DIPUBLIKASIKAN untuk Enterprise / modul lain

| # | API | Konsumen |
|---|---|---|
| P1 | `GET /api/v1/cm/complaints/{id}` (proyeksi ringkas) | Portal, modul lain |
| P2 | `GET /api/v1/cm/analytics/kpi` | Reporting Enterprise |
| P3 | `GET /internal/module/manifest` | Registrasi portal |
| P4 | `GET /internal/health` · `/ready` | Monitoring |
| P5 | `GET /internal/permissions/catalog` | Admin izin Enterprise |

## 9.4 API yang TIDAK BOLEH dimiliki modul

**[FAKTA]** semuanya ada hari ini dan harus dihapus di Mode B:

`/api/v1/auth/*` (6) · `/api/v1/users` create/update/reset (≥5) · `/api/v1/branches` · `/api/v1/customers` · `/api/v1/settings` · `/api/v1/audit` · `/api/v1/notifications`, `/api/v1/notification/templates` (12) · `/api/v1/dashboard`, `/api/v1/reports`

**Total ±40 dari 108 endpoint dihapus atau diganti proyeksi.**

## 9.5 Aturan kontrak API

**[DESAIN]** Versioning `/api/v1/cm` (ADR-006) · envelope `{data, meta}` / `{code, message, details}` **[FAKTA]** sudah konsisten · pagination **satu** konvensi `page`/`pageSize` · `Idempotency-Key` wajib pada seluruh POST yang mengubah state · OpenAPI di-generate dari kode dan **diverifikasi contract test** (gap saat ini).

---

# BAB 10 — EVENT CONTRACT

**[FAKTA]** — `08 Event Catalog/events/events.yaml` (EVT-CAT-001 v0.7, **Approved**, SoT normatif), 40 event, `delivery_guarantee: at-least-once (ADR-001); all consumers MUST be idempotent`.

## 10.1 Event yang DIPUBLIKASIKAN modul

| Event | Publisher | Subscriber (indikatif) | Payload inti |
|---|---|---|---|
| `ComplaintRegistered` | Modul | Notification · Search · Reporting · Audit | `complaintId, customerRef, category, priority, orgUnitRef, registeredAt, registeredBy` |
| `ComplaintAssigned` | Modul | Notification · Reporting · Audit | `complaintId, assigneeRef, assigneeType, assignedBy, assignedAt, reason?` |
| `ComplaintEscalated` | Modul | Notification · Reporting · Audit | `complaintId, fromOrgUnit, toOrgUnit, level, reason, escalatedBy, escalatedAt` |
| `ComplaintReturned` | Modul | Notification · Audit | `complaintId, reasonCode, note, returnedBy` (DEC-F4) |
| `ComplaintResolved` | Modul | Notification · Search · Reporting · Audit | `complaintId, resolutionCode, resultVisibility, resolvedBy, resolvedAt` |
| `ComplaintClosed` | Modul | Reporting · Audit | `complaintId, closedBy, closedAt` |
| `ComplaintReopened` | Modul | Notification · Audit | `complaintId, reason, reopenedBy` |
| `SLADeadlineSet` | Modul | Scheduler · Reporting | `complaintId, deadlineAt, policyId` |
| `SLABreached` | Modul | Notification · Reporting · Audit | `complaintId, breachedAt, breachType` |
| `AttachmentAttached` | Modul | Search · Audit | `complaintId, attachmentId, fileHandle, mimeType, size` |
| `ComplaintProjectionUpdated` | Modul | Search Index | proyeksi ringkas untuk index |

## 10.2 Event yang DIKONSUMSI modul

| Event | Publisher | Aksi modul |
|---|---|---|
| `UserDeactivated` | Enterprise Identity | Nonaktifkan profil lokal; assignment aktif ditandai perlu realokasi |
| `OrganizationChanged` | Enterprise Organization | Refresh `ref_org_units`; evaluasi ulang scope |
| `EntitlementRevoked` | Enterprise Entitlement | Cabut akses; akhiri sesi modul |
| `SessionTerminated` | Enterprise Identity | Invalidasi konteks |

## 10.3 Reliabilitas

**[DESAIN]**

| Aspek | Keputusan |
|---|---|
| Pola publikasi | **Transactional Outbox** — [FAKTA] tabel `cm_batch1_outbox` sudah ada, consumer belum |
| Jaminan | At-least-once (**[FAKTA]** ADR-001) |
| Idempotensi | **Wajib di konsumen**; setiap event membawa `eventId` + `occurredAt` |
| Urutan | Dijamin per `complaintId`, tidak global |
| Retry | Eksponensial backoff, milik Enterprise bus |
| **Dead Letter** | DLQ milik Enterprise. Modul menyediakan endpoint reproses `POST /internal/outbox/{id}/replay` |
| Retensi outbox | Dihapus setelah dikonfirmasi bus + periode grace |
| Skema | Versioned; perubahan payload = event baru, bukan modifikasi |

**[BUTUH INFO]** Teknologi bus, format envelope, mekanisme ack, dan kebijakan DLQ Enterprise — **penyedia: Enterprise App Owner**. Tanpa ini, adapter outbox tidak dapat diselesaikan.

---

# BAB 11 — INTEGRATION CONTRACT

Format seragam per kapabilitas: **Port → Adapter → Mode kegagalan**.

| # | Kapabilitas | Port | Metode | Mode kegagalan | Status info |
|---|---|---|---|---|---|
| 1 | **Identity** | `IdentityProvider` | Token OIDC RS256 + JWKS | **Fail-closed** — token invalid = tolak | **[BUTUH INFO]** issuer, audience, nama klaim |
| 2 | **Entitlement** | `EntitlementProvider` | Klaim atau API | **Fail-closed** — default deny | **[BUTUH INFO]** mekanisme |
| 3 | **Organization** | `OrganizationDirectory` | Sync berkala + cache | Cache basi > ambang → tolak operasi ber-scope | **[BUTUH INFO]** API, hierarki, frekuensi |
| 4 | **Notification** | `NotificationPublisher` | Event / API | **Fail-open** — kegagalan notifikasi tidak menggagalkan transaksi domain; masuk outbox | **[BUTUH INFO]** kontrak |
| 5 | **Audit** | `AuditPublisher` | Event | **Fail-closed** untuk peristiwa wajib-audit | **[BUTUH INFO]** skema |
| 6 | **Workflow** | — | Tidak dipakai untuk state keluhan | — | State machine tetap di domain |
| 7 | **Reporting** | — | Event + API proyeksi | Fail-open | **[BUTUH INFO]** |
| 8 | **Search** | `SearchIndexPublisher` | Event proyeksi | Fail-open; rekonsiliasi berkala | **[BUTUH INFO]** |
| 9 | **Storage / File** | `FileStorage` | API | **Fail-closed** — unggah gagal = operasi gagal | **[BUTUH INFO]** API, kuota, AV |
| 10 | **Configuration** | `ConfigurationProvider` | API + cache | Fail-closed saat startup bila config wajib hilang | **[BUTUH INFO]** |
| 11 | **Monitoring** | `MetricsSink` | Pull `/metrics` atau push | Fail-open | **[BUTUH INFO]** |
| 12 | **Logging** | stdout JSON | **[FAKTA]** formatter sudah ada | Fail-open | **[BUTUH INFO]** sink |
| 13 | **Scheduler** | `SchedulerClient` | API + callback | Fail-closed untuk job SLA | **[BUTUH INFO]** |
| 14 | **Customer** | `CustomerProvider` | API | Fail-open (unverified) | **[FAKTA]** INT-001A RFI ada |

## 11.1 Prinsip integrasi

**[DESAIN]**

| # | Prinsip |
|---|---|
| G1 | **Satu port per kapabilitas.** Tidak ada panggilan langsung dari `application`/`domain` |
| G2 | **Anti-corruption layer.** Model Enterprise tidak masuk ke domain; adapter menerjemahkan |
| G3 | **Fail-closed untuk keamanan, fail-open untuk kenyamanan** (tabel di atas) |
| G4 | **Nama klaim & endpoint dari konfigurasi**, tidak di-hardcode — agar kontrak nyata cukup diisi, bukan ditulis ulang |
| G5 | **Timeout & circuit breaker** pada setiap adapter sinkron |
| G6 | **Degradasi terdefinisi.** Setiap adapter mendeklarasikan perilaku saat Enterprise tidak tersedia |

## 11.2 Ringkasan informasi yang kurang

| # | Informasi | Penyedia | Mengapa penting | Dampak bila tidak ada |
|---|---|---|---|---|
| K1 | **Contoh access token nyata (ter-decode)** | Enterprise App Owner | Menentukan nama klaim identitas, org, peran, entitlement | Seluruh lapisan identitas berbasis tebakan |
| K2 | Discovery URL, audience, client id | Enterprise App Owner | Validasi token | Mode B tidak dapat dijalankan |
| K3 | Mekanisme entitlement | Enterprise App Owner | Desain gate | Semua pegawai dapat akses modul |
| K4 | Model & API organisasi | Enterprise App Owner | Org scope + eskalasi | Eskalasi lintas unit gagal |
| K5 | Metode embed UI + framework host | Enterprise App Owner | Struktur frontend | 12.170 baris berisiko ditulis ulang |
| K6 | Kontrak event bus & DLQ | Enterprise App Owner | Adapter outbox | Event domain tidak pernah keluar |
| K7 | API File Service | Enterprise App Owner | Lampiran | Modul tetap menyimpan berkas sendiri |
| K8 | Kontrak Notification | Enterprise App Owner | Pemberitahuan | Modul mempertahankan engine ganda |
| K9 | Sink observability | Enterprise DevOps | Monitoring | Modul tidak terpantau |
| K10 | Format module manifest | Enterprise App Owner | Registrasi | Modul tidak dapat didaftarkan |

---

# BAB 12 — SECURITY MODEL

## 12.1 Pipeline otorisasi

**[DESAIN]** Urutan **wajib**, setiap tahap fail-closed:

```
1. Token diterima
2. IDENTITY ADAPTER          ← [FAKTA] dinamai ADR-014
   ├─ validasi signature (RS256, alg pinning)
   ├─ validasi iss / aud / exp / nbf
   ├─ validasi klaim wajib (ADR-015)   → gagal = 401
   └─ pemetaan klaim → ExternalUserRef (nama klaim dari konfigurasi)
3. ENTITLEMENT GATE                     → tanpa entitlement = 403
4. IDENTITY CORRELATION
   └─ external_user_id → profil lokal (JIT provisioning bila berhak)
5. PRINCIPAL terbentuk
6. PERMISSION CHECK (matrix modul, dari DB)   → 403
7. ORG SCOPE (hierarkis)                       → 403
8. DATA SCOPE (di layer repository)            → filter, bukan opsional
9. Use case dijalankan
```

**[FAKTA]** Tahap 2 (sebagian), 6 sudah ada. Tahap 3, 4 belum ada. Tahap 7 parsial (14 call site). Tahap 8 **tidak pernah dipanggil**.

## 12.2 Authentication

| Aturan | Keputusan |
|---|---|
| Penerbit token | **Hanya Enterprise.** Modul tidak pernah menerbitkan kredensial |
| Algoritma | RS256, alg pinning, **[FAKTA]** sudah diterapkan |
| Klaim wajib | ADR-015; absen = tolak |
| Kredensial lokal | **[FAKTA]** `ECMP_LOCAL_CREDENTIAL_AUTH` fail-closed; dilarang di staging/production |
| Sesi | Milik Enterprise; modul stateless |

## 12.3 Authorization

**[DESAIN]** Tiga lapis terpisah:

| Lapis | Pemilik | Pertanyaan |
|---|---|---|
| **Entitlement** | Enterprise | Boleh masuk modul? |
| **Permission** | **Modul** | Boleh melakukan aksi ini? |
| **Scope** | Modul (data dari Enterprise) | Boleh atas objek yang mana? |

**[FAKTA]** aturan yang sudah benar dan dipertahankan: permission **tidak pernah** dari token; `RoleMapper` menolak `ADMIN`/`ADMINISTRATOR`/`SUPER_ADMIN` dari klaim IdP (ADR-015 §6).

## 12.4 Data Scope & Organization Scope

**[DESAIN] — perubahan paling penting dari kondisi sekarang:**

> Data scope ditegakkan di **layer repository**, bukan opt-in per endpoint.

Setiap query domain menerima `ScopeFilter` dari Principal. Repository yang tidak menerapkannya **gagal di test arsitektur**, bukan lolos diam-diam.

Org scope memakai hierarki (`ref_org_units.parent_external_id`), mendukung relasi leluhur–turunan — prasyarat eskalasi cabang → pusat (DEC-F4).

## 12.5 Audit

| Jenis | Pemilik | Tujuan |
|---|---|---|
| Identity audit (login, logout, MFA) | Enterprise | Store Enterprise |
| **Domain audit** (siapa mengeskalasi, kapan, alasan) | **Modul** → publikasi | Store Enterprise |
| Timeline keluhan | **Modul** | DB modul — [FAKTA] ADR: *"Not Complaint Timeline"* |

**[DESAIN]** Modul **tidak** menyimpan audit store sendiri; ia menerbitkan event audit. Timeline tetap milik modul karena ia **bagian dari domain**, bukan log sistem.

---

# BAB 13 — DEPLOYMENT MODEL

## 13.1 Bentuk deployment

**[BUTUH INFO] K11 — informasi paling menentukan bab ini**

| Skenario | Bentuk modul | Konsekuensi |
|---|---|---|
| **A. Enterprise mendukung modul out-of-process** | Container/servis terpisah di belakang gateway Enterprise | **[DESAIN] direkomendasikan** — modul rilis mandiri |
| **B. Enterprise mengharapkan plugin in-process** | Library yang dimuat host | Backend harus dikemas ulang sebagai paket, bukan servis |
| **C. Enterprise monolit tanpa mekanisme modul** | Kode dilebur ke repo Enterprise | Biaya tertinggi; modul kehilangan rilis mandiri |

**[ASUMSI]** Skenario A. Alasan: **[FAKTA]** modul sudah punya Dockerfile, compose produksi, migrasi Alembik sendiri, dan health probe — artefak yang hanya bermakna pada deployment out-of-process.

**Bila asumsi ini salah, BAB 6, 7, dan 13 harus dirancang ulang.** Konfirmasi ini prasyarat sebelum sprint implementasi mana pun.

## 13.2 Startup (fail-fast)

**[FAKTA]** `validate_runtime_config` sudah menerapkan pola ini. **[DESAIN]** urutan target:

```
1. Muat konfigurasi          → gagal = keluar
2. Validasi konfigurasi wajib (termasuk endpoint Enterprise)
3. Uji konektivitas DB
4. Jalankan/verifikasi migrasi (job terpisah, bukan entrypoint)
5. Resolusi adapter Enterprise (identity, entitlement, org, file, …)
6. Verifikasi discovery/JWKS dapat dijangkau
7. Bangun permission matrix cache
8. Daftarkan modul ke portal (manifest)
9. Tandai READY
```

**[DESAIN]** Perubahan dari kondisi sekarang: **[FAKTA]** `docker-entrypoint.sh` menjalankan `alembic upgrade head` setiap start — di target, migrasi menjadi job terpisah dengan advisory lock agar aman multi-replika.

## 13.3 Shutdown

Berhenti menerima request baru → selesaikan in-flight (grace 30s, **[FAKTA]** sudah ada) → flush outbox → deregistrasi dari portal → tutup pool → keluar.

## 13.4 Health check

| Endpoint | Memeriksa | Untuk |
|---|---|---|
| `/internal/live` | Proses hidup | **[FAKTA]** sudah ada |
| `/internal/ready` | Startup + DB | **[FAKTA]** sudah ada |
| `/internal/ready/deep` | + adapter Enterprise terjangkau | **BARU** |
| `/internal/version` | Provenance build | **[FAKTA]** sudah ada |

## 13.5 Versioning

**[DESAIN]** SemVer modul terpisah dari Enterprise. `MAJOR` = perubahan kontrak yang memutus (API/event). Matriks kompatibilitas modul ↔ Enterprise dideklarasikan di manifest. **[FAKTA]** provenance build (commit/branch/tree_state) sudah ada dan dipertahankan.

---

# BAB 14 — MODULE LIFE CYCLE

**[BUTUH INFO] K10** — format dan mekanisme registrasi milik Enterprise. Bab ini adalah **[DESAIN]** kontrak minimum yang harus dipenuhi modul.

| Fase | Yang dilakukan modul | Prasyarat |
|---|---|---|
| **Install** | Sediakan artefak (image/paket) + manifest + skrip migrasi | Registry tersedia |
| **Register** | Publikasikan manifest: id, versi, rute, menu, katalog izin, event, kompatibilitas | Portal menerima manifest |
| **Enable** | Aktifkan rute & konsumsi event; verifikasi adapter; READY | Entitlement terkonfigurasi |
| **Disable** | Tolak request baru (403 `MODULE_DISABLED`); hentikan konsumsi; data tetap utuh | — |
| **Upgrade** | Migrasi maju kompatibel; dual-read selama transisi; kontrak lama didukung satu versi | Backup terverifikasi |
| **Rollback** | Kembali ke versi sebelumnya; migrasi punya `downgrade` — **[FAKTA]** 44/44 migrasi punya | Snapshot DB |
| **Remove** | Ekspor data domain; deregistrasi; hapus skema setelah retensi | Persetujuan data owner |

**[DESAIN]** Contoh manifest:

```yaml
module:
  id: complaint-management
  version: 2.0.0
  compatibleWith: { enterprisePlatform: ">=1.4 <2.0" }
  routes:    [{ path: /complaints, entry: entry.tsx }]
  menu:      [{ label: Keluhan, icon: inbox, permission: complaints:read }]
  permissions: [complaints:read, complaints:create, complaints:assign, complaints:escalate, complaints:resolve, complaints:close]
  entitlementKey: complaint-management
  publishes: [ComplaintRegistered, ComplaintAssigned, ComplaintEscalated, ComplaintResolved, ComplaintClosed, SLABreached]
  subscribes: [UserDeactivated, OrganizationChanged, EntitlementRevoked]
  health: { live: /internal/live, ready: /internal/ready }
```

---

# BAB 15 — OBSERVABILITY

**[FAKTA]** kondisi sekarang: JSON logging ada; metrics, tracing, alerting **nol**.

**[DESAIN]** Prinsip: **modul menghasilkan sinyal; Enterprise memiliki penyimpanan, dashboard, dan alert.**

| Pilar | Modul menghasilkan | Enterprise memiliki |
|---|---|---|
| **Logging** | JSON terstruktur ke stdout, ber-korelasi `requestId`/`correlationId`, tanpa PII/secret (**[FAKTA]** redaction ada) | Sink, retensi, pencarian |
| **Metrics** | `/internal/metrics` — RED (rate/error/duration) per endpoint + metrik domain | Prometheus, dashboard, alert |
| **Tracing** | Span OpenTelemetry, propagasi trace context dari Enterprise | Collector, backend |
| **Audit** | Event audit domain | Store, non-repudiation |
| **Alert** | Mendeklarasikan kondisi alert di manifest | Alertmanager |
| **Dashboard** | Menyediakan definisi metrik | Permukaan dashboard |

**[DESAIN]** Metrik domain minimum: `complaints_registered_total` · `complaints_resolved_total` · `complaint_resolution_seconds` (histogram) · `sla_breached_total` · `escalations_total{level}` · `outbox_pending` · `enterprise_adapter_failures_total{capability}`

---

# BAB 16 — DEFINITION OF DONE

## 16.1 Boundary

- [ ] Tidak ada endpoint AuthN/user-directory/organization/settings/audit/notification di modul
- [ ] Tidak ada tabel `users`, `refresh_tokens`, `password_reset_tokens`, `branches`, `settings`, `audit_logs`, `notification_*`
- [ ] Tidak ada FK dari tabel domain ke entitas milik Enterprise
- [ ] `grep -r "workflow\|execution\|delivery\|transport\|provider_" app/modules` → hanya adapter
- [ ] Capability Ownership Matrix (BAB 4) disetujui kedua pihak

## 16.2 Identitas & keamanan

- [ ] Modul tidak pernah menerbitkan kredensial atau token
- [ ] `external_user_id` menjadi satu-satunya kunci identitas
- [ ] Entitlement Gate aktif, default-deny, **teruji dengan test yang membuktikan penolakan**
- [ ] JIT provisioning + deaktivasi + rekonsiliasi berjalan
- [ ] Permission tetap milik modul, tidak pernah dari token
- [ ] Data scope ditegakkan di **layer repository**; ada test arsitektur yang menggagalkan repository tanpa scope
- [ ] Org scope hierarkis; eskalasi cabang → pusat lolos uji
- [ ] Tidak ada referensi yatim di Mode B

## 16.3 Domain

- [ ] **Satu** model komplain (DEC-020 tuntas); tabel legacy dihapus
- [ ] `domain/` tidak mengimpor framework, ORM, atau HTTP — diverifikasi lint
- [ ] Seluruh invarian ada di aggregate, bukan di service/router
- [ ] Business Rule tertelusur ke BR-CM-* lewat RTM

## 16.4 Integrasi

- [ ] Semua port punya adapter enterprise + standalone + inmemory
- [ ] Nama klaim & endpoint dari konfigurasi, bukan hardcode
- [ ] Outbox punya consumer; DLQ terhubung
- [ ] Event sesuai EVT-CAT-001; konsumen idempoten
- [ ] INT-003 Integration Contract **v1.0** (bukan Draft) disetujui bilateral

## 16.5 Frontend

- [ ] Tidak ada shell, sidebar, header, tema, atau halaman login di modul
- [ ] Satu titik mount (`entry.tsx`) + `module.manifest.ts`
- [ ] Seluruh kontak dengan host lewat `platform/`
- [ ] Pengguna tidak melihat halaman login kedua

## 16.6 Operasi

- [ ] Migrasi sebagai job terpisah dengan advisory lock
- [ ] `/internal/metrics` + tracing aktif
- [ ] Log JSON tanpa PII, ber-korelasi
- [ ] Backup + verifikasi restore terjadwal
- [ ] Manifest terdaftar di portal

## 16.7 Kualitas

- [ ] Coverage ≥ 90% (**[FAKTA]** gate sudah ada)
- [ ] Contract test OpenAPI ↔ implementasi
- [ ] Contract test event ↔ EVT-CAT-001
- [ ] E2E minimal 5 alur kritis
- [ ] CI hijau pada matriks `standalone` **dan** `enterprise`
- [ ] Lint blocking (**[FAKTA]** sudah aktif)

---

# BAB 17 — TARGET PROJECT STRUCTURE

```
ecmp-complaint-module/
├── README.md
├── module.manifest.yaml                    ← BARU
│
├── backend/                                ← TETAP (direstrukturisasi)
│   ├── app/  (bootstrap domain application ports adapters infrastructure api security)
│   ├── migrations/
│   └── tests/  (unit integration contract e2e architecture)
│
├── frontend/                               ← TETAP (dipangkas)
│   └── src/  (module.manifest.ts entry.tsx features/ domain/ api/ platform/)
│
├── contracts/                              ← BARU — kontrak keluar modul
│   ├── openapi/complaint-module.v1.yaml
│   ├── events/complaint-events.v1.yaml
│   ├── permissions/catalog.yaml
│   └── integration/INT-003.md
│
├── docs/                                   ← DIRAMPINGKAN
│   ├── architecture/  domain/  integration/  operations/
│
├── governance/                             ← dari folder 00–27
│   ├── adr/  decisions/  board/  traceability/
│
└── deploy/  (Dockerfile.backend, Dockerfile.frontend, compose.dev.yml, migration-job.yaml)
```

## 17.1 Yang DIHAPUS

| Item | LOC | Alasan |
|---|---:|---|
| `app/modules/auth`, `users`, `iam`, `branches` | 5.147 | Milik Enterprise |
| `notification`, `audit`, `search`, `settings`, `email` | 4.006 | Kapabilitas Enterprise |
| `workflow`, `execution`, `delivery`, `transport`, `provider_*` | 3.632 | Duplikasi Workflow Engine |
| `frontend/src/shared/{ui,layouts,theme}` | 1.939 | Milik Enterprise |
| `frontend/src/app/{login,forgot-password,reset-password,change-password}` | ±400 | Milik Enterprise |
| Tabel legacy komplain | — | Setelah DEC-020 |
| `implementation/` | 7.588 | Status canonical kabur |
| `ai/`, `ai-platform/`, `site/` | — | **[DESAIN]** pindah ke repo perkakas terpisah |
| **Total kode dihapus** | **±22.700** | |

## 17.2 Yang DIPINDAHKAN

| Dari | Ke |
|---|---|
| Folder `00`–`27` | `governance/` + `docs/` |
| `07 API Catalog/openapi` | `contracts/openapi/` |
| `08 Event Catalog` | `contracts/events/` |
| Logika izin | `contracts/permissions/catalog.yaml` |

## 17.3 Yang TETAP

Domain komplain (±16.000 LOC) · `frontend/src/features/**` (12.170 baris) · migrasi domain · security foundation (config validation, secret redaction, alg pinning, fail-closed) · pola `integrations/customer` · Business Rules, FRD, RTM, UAT · Event Catalog

---

# BAB 18 — TARGET ROADMAP

> **Framing Board:** bab ini adalah *usulan urutan target-state*, **bukan** backlog aktif. Jangan memecah Sprint 1–6 menjadi ticket Jira/GitHub sebelum gate hijau.

### Gate sebelum Sprint ≥ 1 (semua wajib)

| Gate | Syarat | Otoritas |
|---|---|---|
| **G-HOST** | K1–K11 + F1–F4 (dan H* terkait di EA-PLATFORM-001) **Closed** atau waiver bertanggal dari Board + EP Owner | Enterprise App Owner + Board |
| **G-ORG** | Org-gap prerequisite evidence (C-B6-3) pada bar yang disepakati | BOARD-006 / org-gap plan |
| **G-OWN** | Capability Ownership Matrix (BAB 4) disetujui bilateral | Board + EP Owner |
| **G-C7** | Board Resolution membuka Mode B / C-7 (coding authorized) | Architecture Board |
| **G-DTM** | Keputusan yang diimplementasikan terindeks di DTM-001 dengan bukti | Documentation / SA |

Prasyarat mutlak implementasi yang bergantung kontrak HOST/Mode B: **G-HOST ∧ G-ORG ∧ G-OWN ∧ G-C7**. Mode A delivery **tidak** memakai Sprint 2–5 sebagai alasan coding Mode B.

## Sprint 0 — Menutup ketidakpastian (tanpa coding Mode B)

| # | Pekerjaan | Output |
|---|---|---|
| 0.1 | Sesi teknis Enterprise App Owner — kumpulkan **K1–K11** + **F1–F4** | Paket kontrak HOST (tutup G-HOST) |
| 0.2 | Setujui Capability Ownership Matrix (BAB 4) | Menutup BLK-C1 / G-OWN |
| 0.3 | Konfirmasi bentuk deployment (§13.1 / K11) | Mengunci BAB 6/7/13 |
| 0.4 | Org-gap evidence path (C-B6-3) + kriteria pembukaan C-7 | Input G-ORG / G-C7 |
| 0.5 | Terbitkan / sinkron INT-003 / bilateral profiles | Kontrak bilateral |
| 0.6 | Perbarui DTM-001 (keputusan + HOST dependency Closed) | Indeks audit |

**Hanya Sprint 0 yang boleh dikerjakan sekarang sebagai pekerjaan Board/governance.** Pekerjaan Mode A (complaint lab, FE Aggregate berdampingan, hygiene DEC-020) tetap di `GOV-MODEA-NEXT-001`.

## Sprint 1 — Keamanan yang tidak menunggu — **POST G-C7** *(atau Mode A subset tanpa kontrak enterprise)*

| # | Pekerjaan | Gate note |
|---|---|---|
| 1.1 | **Data scope ke layer repository** + test arsitektur | Mode A boleh jika tidak mengasumsikan org sync enterprise |
| 1.2 | Org scope hierarkis & menyeluruh | **Memerlukan G-HOST (K4) + G-ORG** bila memakai hierarki EP |
| 1.3 | Matriks CI `standalone` + `enterprise` | Label `enterprise` = **POST G-C7** |
| 1.4 | Contract test OpenAPI ↔ implementasi | Mode A: catalog yang sudah ada |
| 1.5 | Metrics + tracing + `/internal/metrics` | Sink HOST = **G-HOST (K9)** |

## Sprint 2 — Ports & Adapters — **POST G-C7 + G-HOST ONLY**

| # | Pekerjaan |
|---|---|
| 2.1 | Buat seluruh `ports/` |
| 2.2 | Identity Adapter + peta klaim berbasis konfigurasi |
| 2.3 | `external_user_id` + korelasi + JIT provisioning |
| 2.4 | Entitlement Gate default-deny |
| 2.5 | Organization adapter + `ref_org_units` + sinkronisasi |
| 2.6 | Outbox consumer + DLQ replay |

## Sprint 3 — Konvergensi domain — **POST G-C7**; retire legacy butuh **Retirement DEC**

| # | Pekerjaan |
|---|---|
| 3.1 | Eksekusi DEC-020 sampai tuntas; retire tabel legacy **hanya dengan Retirement DEC** |
| 3.2 | Restrukturisasi ke `domain/application/ports/adapters` |
| 3.3 | Satu persistence stack (async) |
| 3.4 | `security/` lepas dari `modules` |
| 3.5 | Test arsitektur penegak aturan dependensi |

## Sprint 4 — Pelepasan kapabilitas platform — **POST G-C7 + G-HOST**

| # | Pekerjaan |
|---|---|
| 4.1 | Ganti `notification` dengan `NotificationPublisher` |
| 4.2 | Ganti `audit` dengan `AuditPublisher` |
| 4.3 | Ganti storage lampiran dengan `FileStorage` |
| 4.4 | Ganti `search` dengan `SearchIndexPublisher` |
| 4.5 | Ganti `settings` dengan `ConfigurationProvider` |
| 4.6 | Hapus `workflow`/`execution`/`delivery`/`transport`/`provider_*` |
| 4.7 | Hapus `auth`/`users`/`iam`/`branches` *(jangan di Mode A hedge)* |

## Sprint 5 — Modularisasi frontend — **POST G-C7 + G-HOST (F1–F4)**

| # | Pekerjaan |
|---|---|
| 5.1 | Buat `platform/` sebagai ACL UI |
| 5.2 | `entry.tsx` + `module.manifest.ts` |
| 5.3 | Hapus shell, tema, halaman auth |
| 5.4 | Integrasi ke portal sesuai metode yang dikonfirmasi |
| 5.5 | E2E 5 alur kritis di dalam portal |

## Sprint 6 — Kesiapan produksi — **POST G-C7**

| # | Pekerjaan |
|---|---|
| 6.1 | Migrasi sebagai job + advisory lock |
| 6.2 | Backup + verifikasi restore otomatis |
| 6.3 | Registrasi manifest + uji lifecycle enable/disable/upgrade/rollback |
| 6.4 | Uji beban + penetapan SLO |
| 6.5 | Integrasi percobaan di environment uji Enterprise |

**Total ±22 minggu (±5,5 bulan)** *setelah* Sprint 0 **dan** gate G-HOST/G-ORG/G-OWN/G-C7 hijau — bukan estimasi mulai hari ini.

---

# BAB 19 — MIGRATION PLAN

## 19.1 Urutan yang benar

**[DESAIN]** Prinsip: **identitas lebih dulu, karena semua hal lain bergantung padanya.**

```
1. Identitas & entitlement   ← fondasi; tanpa ini yang lain tak dapat diuji di Mode B
2. Organisasi                ← prasyarat scope & eskalasi
3. Konvergensi domain        ← modul harus punya SATU model sebelum mengekspos kontrak
4. Kapabilitas platform      ← notification, audit, file, search, config
5. Frontend                  ← paling terlihat pengguna; butuh backend stabil
6. Operasi                   ← observability, backup, lifecycle
```

## 19.2 Yang paling berisiko

| # | Risiko | Mengapa | Mitigasi |
|---|---|---|---|
| M1 | **Korelasi identitas pengguna lama** | UUID lokal tidak akan pernah sama dengan `sub` Enterprise | Migrasi pemetaan dengan verifikasi manual; email hanya sebagai *petunjuk sekali pakai*, bukan kunci |
| M2 | **Konvergensi 3 model komplain** | Data produksi aktif; risiko kehilangan riwayat | Parallel-write → parallel-read → verifikasi hitungan → cutover → retensi legacy 1 rilis |
| M3 | **Frontend bila host bukan React** | 12.170 baris berisiko ditulis ulang | **Konfirmasi K5 sebelum Sprint 5** |
| M4 | Penghapusan FK ke `users.id` | 16 FK, 4 `RESTRICT` | Migrasi bertahap: tambah kolom → backfill → lepas FK → hapus kolom lama |
| M5 | Kehilangan lampiran saat pindah ke File Service | Berkas fisik berpindah | Salin → verifikasi checksum → alih baca → hapus sumber |
| M6 | Perubahan kontrak event | Konsumen Enterprise bergantung | Versioning event; dukung dua versi satu siklus |

## 19.3 Yang dapat berjalan paralel

| Jalur | Isi | Bergantung? |
|---|---|---|
| **A. Keamanan internal** | Data scope, org scope, contract test | ❌ Tidak menunggu siapa pun |
| **B. Observability** | Metrics, tracing, log sink | ❌ (sink perlu K9) |
| **C. Konvergensi domain** | DEC-020 | ❌ Murni internal |
| **D. Restrukturisasi folder** | domain/application/ports | ❌ Refactor internal |
| **E. Integrasi identitas** | Adapter, entitlement, org | ✅ Menunggu K1–K4 |
| **F. Frontend** | Modularisasi | ✅ Menunggu K5 |

**[DESAIN]** Jalur A, B, C, D dapat dimulai **segera** tanpa melanggar C-7, karena tidak satu pun merupakan *Mode B coding* — semuanya perbaikan internal yang berlaku di kedua mode.

---

# BAB 20 — FINAL ARCHITECT RECOMMENDATION

## 20.1 Bila memulai dari awal, apakah arsitekturnya sama?

**Tidak. Ada empat perbedaan mendasar.**

### Perbedaan 1 — Batas ditetapkan sebelum baris pertama

Repository ini membangun autentikasi, direktori pengguna, notifikasi, workflow, dan pencarian sendiri karena diasumsikan standalone. **[FAKTA]** ±12.900 LOC kini menjadi kandidat penghapusan.

Bila memulai dari awal: **Capability Ownership Matrix adalah artefak pertama**, sebelum ADR teknologi. Ia menentukan apa yang **tidak** dibangun — dan itu keputusan yang lebih bernilai daripada memilih framework.

### Perbedaan 2 — Ports & Adapters sejak hari pertama, bukan setelah realignment

**[FAKTA]** pola port/adapter sudah dikuasai tim — terbukti di `app/integrations/customer/`. Tetapi hanya diterapkan pada satu integrasi.

Bila memulai dari awal: **setiap** kapabilitas di luar domain masuk lewat port sejak commit pertama, dengan adapter `inmemory` sebagai default. Modul dapat berjalan penuh tanpa Enterprise, dan integrasi menjadi pengisian adapter — bukan pembongkaran.

### Perbedaan 3 — Satu model domain, selamanya

**[FAKTA]** tiga model komplain paralel (`complaints`, `complaint_cases`, `cm_batch1_complaints`) plus enam pasang tabel turunan.

Bila memulai dari awal: satu aggregate, satu tabel per konsep. Ketika arsitektur perlu berubah, **model lama dimigrasikan, bukan didampingi**. Strangler pattern hanya sah bila ada tanggal pensiun sejak awal.

### Perbedaan 4 — Frontend sebagai modul sejak awal

**[FAKTA]** `features/**` (12.170 baris) sudah terpisah dari shell — ini kebetulan yang menguntungkan, bukan desain.

Bila memulai dari awal: `platform/` (ACL UI) dibuat di commit pertama, dengan implementasi lokal untuk pengembangan mandiri. Mengganti host menjadi mengganti satu folder.

## 20.2 Yang akan saya pertahankan tanpa ragu

| # | Keputusan | Mengapa tepat |
|---|---|---|
| K1 | **Domain object immutable** (`frozen=True, slots=True`) | Invarian tidak dapat dirusak diam-diam |
| K2 | **Permission tidak pernah dari token** | Memisahkan AuthN (platform) dari AuthZ (modul) secara teknis |
| K3 | **Fail-fast configuration validation** | Kesalahan konfigurasi tertangkap saat startup, bukan saat insiden |
| K4 | **Secret redaction menyeluruh** | Modul menangani data keluhan pelanggan — kebocoran log adalah risiko nyata |
| K5 | **Strategy pattern untuk AuthN** | Alasan utama biaya realignment ini tetap terkendali |
| K6 | **Event Catalog sebagai SoT normatif** | Kontrak keluar modul sudah ada sebelum dibutuhkan |
| K7 | **Governance-as-code** (ADR, DEC, Board, RTM, generator) | Di atas rata-rata industri; ia yang menemukan masalah arah ini lebih dulu |
| K8 | **Migrasi linear dengan `downgrade` 100%** | Prasyarat lifecycle upgrade/rollback modul |

## 20.3 Rekomendasi akhir

**Satu kalimat:**

> Berhentilah membangun kapabilitas, dan mulailah membangun **batas**.

**Tiga tindakan dengan dampak terbesar:**

1. **Sepakati Capability Ownership Matrix (BAB 4) minggu ini.** Ia menentukan nasib ±12.900 LOC. Tanpa itu, setiap sprint berisiko membangun atau membongkar hal yang salah. Biayanya satu rapat.

2. **Ambil satu access token nyata dari Enterprise Application.** Satu artefak menjawab enam pertanyaan sekaligus: nama klaim identitas, bentuk klaim organisasi, keberadaan entitlement, nama klaim peran, status kepegawaian, dan nilai `iss`/`aud`. Selama ini belum ada, seluruh lapisan identitas adalah hipotesis.

3. **Kerjakan jalur A, B, C, D (§19.3) sekarang.** Data scope, org scope, observability, konvergensi domain, dan restrukturisasi folder tidak menunggu siapa pun dan tidak melanggar C-7. Empat jalur ini menyerap ±9 minggu kerja yang seluruhnya tetap benar apa pun bentuk kontrak akhirnya.

**Satu peringatan yang harus dipegang:**

**[FAKTA]** Governance sudah berbentuk Mode B, tetapi delivery masih Mode A — dan Mode A sedang dipermanenkan (CI frontend kini memiliki langkah tetap *"Mode A credential route inventory"*, dengan catatan *"Mode A delivery may keep login/password routes"*). Setiap sprint tanpa kriteria pembukaan C-7 menambah permukaan yang nanti harus dibongkar. Ini persis risiko **W-19** dan **M-17** yang Architecture Board sendiri sudah tandai.

Beri C-7 tanggal atau pemicu terukur. Itu tindakan paling murah dengan dampak terbesar dalam seluruh dokumen ini.

---

## Lampiran A — Ringkasan informasi yang kurang

| Kode | Informasi | Penyedia | Memblokir |
|---|---|---|---|
| K1 | Contoh access token nyata (ter-decode) | Enterprise App Owner | BAB 12, Sprint 2 |
| K2 | Discovery URL, audience, client id | Enterprise App Owner | BAB 12 |
| K3 | Mekanisme entitlement | Enterprise App Owner | BAB 12, BLK-C3 |
| K4 | Model & API organisasi | Enterprise App Owner | BAB 8, 12 |
| K5 | Metode embed UI + framework host | Enterprise App Owner | **BAB 7 — risiko tertinggi** |
| K6 | Kontrak event bus & DLQ | Enterprise App Owner | BAB 10 |
| K7 | API File Service | Enterprise App Owner | BAB 11 |
| K8 | Kontrak Notification | Enterprise App Owner | BAB 11 |
| K9 | Sink observability | Enterprise DevOps | BAB 15 |
| K10 | Format module manifest | Enterprise App Owner | BAB 14 |
| K11 | Bentuk deployment (in/out-of-process) | Enterprise App Owner | **BAB 6, 7, 13** |
| Q1 | Kepemilikan `queue` | Business Owner | BAB 3 |
| Q2 | Keberadaan Case/Ticket generik | Enterprise App Owner | BAB 3 |
| Q3 | Kepemilikan Appointment | Enterprise App Owner | BAB 3 |

## Lampiran B — Status dokumen sebagai SoT

Dokumen ini menjadi Single Source of Truth **setelah**: (1) BAB 4 disetujui bilateral, (2) K1–K11 terisi, (3) Architecture Board menerimanya sebagai `EA-TARGET-CM-001 v1.0`, dan (4) ADR-007/009/010/011/012/013 direkonsiliasi terhadapnya.

Sampai keempatnya terpenuhi, dokumen ini berstatus **usulan target architecture**, bukan SoT.

---

*Dokumen desain. Tidak ada file repository yang diubah dalam penyusunannya.*
