# DL-000 — ECMP Decision Log

| Field | Value |
|---|---|
| Document ID | DL-000 |
| Title | ECMP Decision Log (Consolidated Approved Decisions) |
| Version | 1.1 |
| Date | 2026-08-05 |
| Status | Draft — konsolidasi + P1 BO resolutions (G0.2D) |
| Milestone | Governance Phase 0 — G0.2A / G0.2D |
| Subordination | Board Resolution → ADR → EA Documents → ECMP-CONSTITUTION-001 → **DL-000** |
| Purpose | Menjadi satu-satunya input untuk **BC-000 (Business Constitution)** pada milestone berikutnya |
| Does not | Membuat keputusan baru · menafsir ulang keputusan lama · mendesain ulang sistem · membuka Mode B · membuat BC-000 |

---

## 1. Tentang dokumen ini

DL-000 mengkonsolidasikan **keputusan yang sudah disetujui secara eksplisit** di repositori ECMP ke dalam satu daftar otoritatif. Dokumen ini **tidak** menciptakan keputusan; setiap baris dapat dirunut ke berkas sumbernya.

**Aturan penyusunan yang dipatuhi:**

1. Hanya keputusan dengan status persetujuan eksplisit di berkas sumbernya (`Approved` · `Accepted` · `Accepted with Conditions` · `LOCKED` · `CLOSED — approved option` · `PROGRAM CLOSED`) yang menjadi record DL.
2. Keputusan berstatus `Proposed`, `Draft`, atau `Open` **tidak** menjadi record DL — dicatat di **Bagian 5 (Keputusan yang masih perlu dibahas)**.
3. Isi kolom `Decision` adalah ringkasan setia dari sumber, bukan tafsir baru. Bila sumber menyatakan sesuatu ditunda/dilarang, itu ikut dicatat.
4. Konflik antar sumber tidak diselesaikan di sini — dicatat apa adanya dan diangkat ke Bagian 5.

**Konvensi penomoran.** `DL-001` dialokasikan untuk keputusan merge persona (kategori UX) sesuai penetapan penugasan G0.2A. Nomor berikutnya (`DL-002` dan seterusnya) diberikan berurutan mengikuti urutan kategori pada Bagian 2. Karena itu kategori UX memuat `DL-001` di luar urutan blok nomornya — ini disengaja, bukan kesalahan penomoran.

**Definisi kategori** (dipakai konsisten sepanjang dokumen):

| Kategori | Cakupan |
|---|---|
| Business | Baseline bisnis, ruang lingkup produk, aturan bisnis, nilai baseline, model komplain |
| Organization | Kepemilikan & sinkronisasi struktur organisasi, scoping organisasi-lokasi |
| Timeline | Waktu: deadline SLA, deteksi breach, jam/kalender, riwayat kronologis case |
| Workflow | State machine, transisi, kontrak lifecycle, konfigurasi workflow |
| UX | Persona, pengalaman workspace, standar pengalaman pengguna |
| Architecture | Batas sistem, pola integrasi, stack, layering, kontrak enterprise |
| Governance | Otoritas, gate, konstitusi delivery, resolusi Board, penutupan program |
| Security | Autentikasi, otorisasi, entitlement, fail-closed, larangan kredensial |
| Reporting | KPI, dashboard, agregasi baca |
| Audit | Jejak audit, immutability, kewajiban pencatatan |

---

## 2. Isi dokumen

| Bagian | Isi |
|---|---|
| 3 | Decision Records — dikelompokkan per kategori |
| 4 | Decision Index (Deliverable 2) |
| 5 | Decision Dependency Matrix (Deliverable 3) |
| 6 | Keputusan yang masih perlu dibahas (Deliverable 4) |
| 7 | Dokumen repositori yang terdampak per keputusan (Deliverable 5) |

Urutan kategori pada Bagian 3: Business · Organization · Timeline · Workflow · UX · Architecture · Governance · Security · Reporting · Audit.

---

## 3. Decision Records

### 3.A Business

---

#### DL-002 — Business Baseline Source of Truth

| Field | Value |
|---|---|
| **Decision ID** | DL-002 |
| **Title** | Business Baseline Source of Truth = Blueprint v2.1 + FRD-001 |
| **Status** | Approved (DEC-001, Architecture Board, 2026-07-21) |

**Decision**
Baseline bisnis resmi ECMP adalah `01 Business Blueprint/ECMP_Business_Blueprint_v2.1.docx` + `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` (FRD-001) beserta katalog turunannya (BR, API, Event, Data Dictionary). Konsep **Branch Officer / Head Office escalation / Schedule Slot / Appointment / Work Order** dinyatakan **di luar lingkup** sampai ada revisi Blueprint yang di-approve Architecture Board. Dokumen "KAK" yang dirujuk brief discovery dinyatakan **superseded** oleh Blueprint v2.1 untuk keperluan implementasi.

**Business Context**
Sprint 0 discovery menemukan dua baseline bisnis yang bertentangan: baseline EKR (Blueprint v2.1 + FRD-001, model CS/ECMF case lifecycle) dan baseline brief discovery (model branch → Head Office escalation → schedule slot → work order) yang tidak ada di artefak mana pun yang di-approve.

**Reason**
Baseline EKR adalah satu-satunya yang ter-approve, konsisten lintas katalog, dan tertelusur (BP→BR→FR→API/EVT/TC). Mengkode terhadap model yang tidak terdokumentasi menghasilkan kerja buangan dan melanggar hard constraint "Do not invent Out of Scope features".

**Alternatives Considered**
- **A** — Blueprint v2.1 + FRD-001 sebagai satu-satunya baseline (dipilih).
- **B** — Revisi Blueprint/FRD/katalog untuk mengadopsi model branch/HO/scheduling.
- **C** — Jalankan keduanya paralel (dual baseline).

**Impact**
Ruang lingkup produk · Backlog · Traceability · Semua FRD turunan · Otorisasi implementasi.

**Affected Documents**
`01 Business Blueprint/` · `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` · `02 Business Rules/` · `07 API Catalog/` · `08 Event Catalog/` · `06 Data Dictionary/` · `26 Traceability/` · `27 Project Decisions/DEC-001_Business_Baseline_SoT_v1.0.md`

**Related Decisions**
DL-007 · DL-008 · DL-009 · DL-010 · DL-011 (pengecualian appointment bertahap) · DL-050 (otorisasi build)

**Supersedes**
Dokumen KAK (untuk keperluan implementasi).

**Notes**
DEC-001 sendiri sudah dicatat menerima *partial supersession* oleh DEC-007 (Appointment booking only). Setiap perluasan berikutnya diberikan lewat DEC terpisah, bukan pelonggaran DEC-001.

**G0.2D (2026-08-05):** Business Owner menyetujui **Scope Consolidation Mode A** (DL-066) yang mencabut OOS untuk **Head Office Escalation** (Branch ↔ Head Office) dan mengunci **Appointment** sebagai bagian resmi Mode A dalam Complaint Lifecycle yang sama. Teks Decision asli DEC-001/DL-002 di atas **tetap sebagai sejarah baseline**; carve-out normatif untuk BC-000 diambil dari **DL-066**. Regional · Work Order · Calendar/Schedule · Mode B · Enterprise Integration tetap OOS.

---

#### DL-003 — Skema ID Business Rule untuk Delivery

| Field | Value |
|---|---|
| **Decision ID** | DL-003 |
| **Title** | Skema ID Business Rule tunggal untuk delivery = `BR-0xx` |
| **Status** | Approved (DEC-003, 2026-07-21) |

**Decision**
1. SoT untuk implementasi/tes/traceability adalah **skema delivery `BR-0xx`** (`02 Business Rules/ECMP_Business_Rules_Sprint01_v0.1.md` dan penerusnya). Kode, PR, tes, dan traceability hanya boleh mengutip `BR-0xx`.
2. Katalog enterprise `BR-<Domain>-NN` tetap sebagai katalog referensi kebijakan; ID dokumennya diganti `BR-CAT-001` untuk menghilangkan bentrok.
3. Tabel pemetaan alias dipelihara di `ECMP_Business_Rules_v1.0.md`. Saat rule enterprise diangkat ke delivery, ia menerima `BR-0xx` baru.

**Business Context**
Dua skema ID Business Rule hidup berdampingan dan header dokumen enterprise memakai `BR-001` yang bentrok dengan rule delivery `BR-001`.

**Reason**
Menghilangkan ambiguitas kutipan aturan bisnis pada kode, tes, dan matriks keterlacakan tanpa membuang katalog kebijakan enterprise.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Business Rules · Traceability · Test Strategy · Review PR · Semua FRD.

**Affected Documents**
`02 Business Rules/ECMP_Business_Rules_Sprint01_v0.1.md` · `02 Business Rules/ECMP_Business_Rules_v1.0.md` (BR-CAT-001) · `26 Traceability/` · `13 Test Strategy/` · `27 Project Decisions/DEC-003_BR_ID_Scheme_v1.0.md`

**Related Decisions**
DL-002 · DL-004 · DL-023 (dual SoT state machine)

**Supersedes**
Penggunaan ID `BR-001` pada header katalog enterprise.

**Notes**
Baseline pemetaan alias per 2026-07-21 tercatat di DEC-003; pemetaan tersebut tidak diubah oleh DL-000.

---

#### DL-004 — Penutupan `[TBD]` Business Rules dengan Nilai Baseline

| Field | Value |
|---|---|
| **Decision ID** | DL-004 |
| **Title** | Business Rule Baseline Defaults (penutupan 10 butir `[TBD]`) |
| **Status** | Approved (DEC-004, reviewed ARB 2026-07-21) |

**Decision**
Seluruh `[TBD]` pada katalog `BR-CAT-001` ditutup dengan nilai baseline:

| Rule | Nilai Baseline |
|---|---|
| BR-CP-02 | Override otorisasi hanya oleh **Administrator** dengan justifikasi tercatat + audit trail |
| BR-CRM-02 | Kontak pelanggan (**phone/email**) dimask untuk role non-CS |
| BR-CRM-03 | Interaksi "penting" = interaksi yang **tertaut ke case** |
| BR-ECMF-02 | Aksi tulis hanya oleh **supervisor unit induk**; unit lain **read-only** |
| BR-ECMF-05 | Kalender SLA **24x7**; kalender kerja = konfigurasi fase berikut |
| BR-ECMF-06 | Evidence saat closure wajib untuk **COMPLAINT**, opsional untuk **INQUIRY** |
| BR-ECMF-07 | Jangka waktu reopen sejak closure = **30 hari kalender** |
| BR-NOTIF-04 | Retry maksimal **3x interval 5 menit**, lalu eskalasi **email ke supervisor** |
| BR-KPI-03 | **Tidak ada** KPI berinput manual di fase awal |
| BR-ADM-01 | Konfigurasi kritikal = **workflow config, SLA config, role-permission** |

Setiap nilai ditandai di katalog dengan "(baseline ARB 2026-07-21 — dapat direvisi BO via DEC)". **Business Owner** berwenang merevisi tiap nilai melalui **DEC baru**, bukan edit langsung katalog.

**Business Context**
10 butir `[TBD]` memblokir status Approved katalog dan membuat FRD-002…006 tidak bisa menulis acceptance criteria presisi.

**Reason**
Menunggu keputusan bisnis final per butir menunda baseline tanpa manfaat proporsional; nilai baseline reversibel lewat DEC menjaga kecepatan tanpa mengunci bisnis.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber (pola yang dipakai: tutup dengan baseline reversibel).

**Impact**
Business Rules · FRD-002…006 · SLA · Notification · KPI · Administration · Security (masking & override).

**Affected Documents**
`02 Business Rules/ECMP_Business_Rules_v1.0.md` · `03 Functional Requirements/` · `11 SLA and KPI Matrix/` · `10 Security and Access Standards/` · `27 Project Decisions/DEC-004_BR_Baseline_Defaults_v1.0.md`

**Related Decisions**
DL-005 (target numerik SLA/NFR) · DL-019 (kalender 24x7 CAP-006) · DL-064 (override + audit) · DL-015 (scoping organisasi)

**Supersedes**
Butir `[TBD]` pada BR-CAT-001.

**Notes**
BR-ECMF-05 (24x7) dan BR-ECMF-07 (30 hari) kemudian dirujuk ulang oleh keputusan SLA/CAP-006; nilainya tidak berubah.

---

#### DL-005 — Target Numerik SLA & NFR

| Field | Value |
|---|---|
| **Decision ID** | DL-005 |
| **Title** | SLA & NFR Baseline Targets |
| **Status** | Approved (DEC-005, reviewed ARB 2026-07-21) |

**Decision**
Seluruh target numerik SLA dan NFR ditutup dengan nilai baseline konservatif, ditandai "(baseline ARB 2026-07-21 — dapat direvisi BO via DEC)". Kalender **24x7** (mengikuti BR-ECMF-05 per DL-004).

| Priority | First Response | Resolution |
|---|---|---|
| CRITICAL | 30 menit | 4 jam |
| HIGH | 1 jam | 8 jam |
| MEDIUM | 4 jam | 2 hari (48 jam kalender) |
| LOW | 8 jam | 5 hari (120 jam kalender) |

Baseline berlaku seragam untuk semua case type (COMPLAINT, INQUIRY); diferensiasi per case type adalah kandidat revisi BO via DEC. Threshold breach & eskalasi (termasuk warning 80%) serta target NFR (availability/latency/throughput/kapasitas/RTO-RPO) ditetapkan pada dokumen yang sama.

**Business Context**
SLA Matrix (`11 SLA and KPI Matrix` §2) seluruhnya `[TBD]` sehingga memblok BR-ECMF-05, KPI-ECMF-03/04, dan desain eskalasi Notification; NFR target di Solution Architecture juga belum tercentang.

**Reason**
Pola yang sama dengan DL-004: menunggu workshop untuk tiap angka menunda baseline tanpa manfaat proporsional; angka konservatif reversibel lewat DEC.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
SLA Engine · KPI · Notification · Dashboard · NFR/Operasi · Test Strategy.

**Affected Documents**
`11 SLA and KPI Matrix/` · `04 Solution Architecture/` · `07 API Catalog/` · `27 Project Decisions/DEC-005_SLA_NFR_Baseline_Targets_v1.0.md`

**Related Decisions**
DL-004 · DL-016 · DL-017 · DL-019 (warning 80% dirujuk ke DEC-005)

**Supersedes**
Butir `[TBD]` target numerik SLA/NFR.

**Notes**
Diferensiasi target per case type tercatat **DEFERRED** juga oleh penutupan bisnis CAP-006 (lih. DL-019) — konsisten, bukan keputusan berbeda.

---

#### DL-006 — Multi-Source & Multi-Target Complaint

| Field | Value |
|---|---|
| **Decision ID** | DL-006 |
| **Title** | Complaint multi-sumber & multi-tujuan dalam satu aggregate |
| **Status** | Approved (DEC-018, 2026-07-24) |

**Decision**
Pertahankan **satu Complaint aggregate dan satu tabel**. Tambahkan field polimorfik: `source_type` (`CUSTOMER`, `BRANCH`, `HEAD_OFFICE`, `SYSTEM`), `source_id`, `target_type` (`BRANCH`, `HEAD_OFFICE`), `target_id`. Enum disimpan sebagai `VARCHAR` agar nilai masa depan dapat ditambah di kode aplikasi tanpa perubahan skema. Kolom legacy tetap: `customer_id` (diisi bila `source_type=CUSTOMER`) dan `branch_id` (diisi bila `target_type=BRANCH`, dikosongkan bila `HEAD_OFFICE`). Lifecycle **tidak berubah**.

**Business Context**
Complaint sebelumnya dimodelkan hanya berasal dari pelanggan dan ditujukan ke cabang; realitas operasional membutuhkan komplain yang berasal dari Branch, Head Office, atau System.

**Reason**
Memenuhi realitas operasional tanpa memecah Complaint aggregate dan tanpa mengubah lifecycle, Assignment, Timeline, Resolution, Appointment, Escalation, atau Authorization.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber (yang dicatat: tidak memecah aggregate).

**Impact**
Domain Complaint · Data model · API create complaint · Assignment context.

**Affected Documents**
`06 Data Dictionary/` · `20 Domain Architecture/ECMF/CASE_AGGREGATE.md` (DOM-ECMF-002) · `07 API Catalog/` · `27 Project Decisions/DEC-018_Multi_Source_Multi_Target_Complaint_TASK042_v1.0.md`

**Related Decisions**
DL-002 · DL-012 (jalur eskalasi Cabang → Pusat) · DL-015

**Supersedes**
Asumsi "complaint selalu customer-originated & branch-targeted".

**Notes**
Ini salah satu dari sedikit keputusan yang menyentuh Domain Complaint; dicatat sebagai perubahan yang dibutuhkan bisnis, bukan perluasan mekanisme integrasi.

---

#### DL-007 — Ruang Lingkup Appointment Booking

| Field | Value |
|---|---|
| **Decision ID** | DL-007 |
| **Title** | Appointment Booking Scope (TASK-014) |
| **Status** | Approved (DEC-007, 2026-07-23) |

**Decision**
**Partial supersession DEC-001 untuk Appointment booking saja.** In scope: booking satu appointment aktif (`BOOKED`) atas eskalasi ber-status `APPROVED`; read appointment by id; timeline event `complaint.appointment_booked`; form + detail card di Escalation Detail UI. Tetap **out of scope** (DEC-001 masih mengikat): Calendar View, Slot Generator, Completion/Cancel workflow, Notification, Work Order.

**Business Context**
DEC-001 menempatkan Appointment di luar lingkup sampai revisi Blueprint; TASK-014 mengirimkan Head Office Appointment booking untuk eskalasi yang disetujui (API-305/306).

**Reason**
Memberi otorisasi sempit dan eksplisit untuk kebutuhan nyata tanpa membuka kembali seluruh model branch/HO/scheduling yang ditolak DEC-001.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Domain Escalation/Appointment · API-305/306 · Timeline · UI Escalation Detail.

**Affected Documents**
`07 API Catalog/` · `08 Event Catalog/` · `27 Project Decisions/DEC-007_Appointment_Booking_Scope_TASK014_v1.0.md`

**Related Decisions**
DL-002 (disupersede sebagian) · DL-008 · DL-009 · DL-010 · DL-011

**Supersedes**
DEC-001 **sebagian** — hanya untuk Appointment booking.

**Notes**
Pola "partial supersession bertahap" ini berulang di DL-008…DL-011; setiap langkah butuh DEC sendiri.

---

#### DL-008 — Ruang Lingkup Customer Check-In

| Field | Value |
|---|---|
| **Decision ID** | DL-008 |
| **Title** | Appointment Check-In Scope (TASK-015) |
| **Status** | Approved (DEC-008, 2026-07-23) |

**Decision**
**Partial extension DEC-007 untuk Customer Check-In saja.** In scope: check-in sekali atas appointment `BOOKED` (`CHECKED_IN`); simpan `checkedInAt`/`checkedInBy`/catatan; timeline event `complaint.appointment_checked_in`; tombol + confirm dialog di Escalation Detail UI (API-307). Out of scope: Appointment Completion, Customer No Show, Notification/SLA/Auto Close, Calendar/Slot Generator.

**Business Context**
DEC-007 hanya mengizinkan booking; check-in belum berotorisasi.

**Reason**
Perluasan lingkup satu langkah, tetap dalam batas yang bisa diaudit terhadap DEC-001.

**Alternatives Considered**
Tidak dicatat di sumber.

**Impact**
Domain Appointment · API-307 · Timeline · UI Escalation Detail.

**Affected Documents**
`07 API Catalog/` · `08 Event Catalog/` · `27 Project Decisions/DEC-008_Appointment_CheckIn_Scope_TASK015_v1.0.md`

**Related Decisions**
DL-002 · DL-007 · DL-009 · DL-010

**Supersedes**
DEC-007 **sebagian** (butir "Check-In tetap out of scope").

**Notes**
—

---

#### DL-009 — Ruang Lingkup Appointment Completion

| Field | Value |
|---|---|
| **Decision ID** | DL-009 |
| **Title** | Appointment Completion Scope (TASK-016) |
| **Status** | Approved (DEC-009, 2026-07-23) |

**Decision**
**Partial extension DEC-007/008 untuk Appointment Completion saja.** In scope: menyelesaikan sekali appointment `CHECKED_IN` (`COMPLETED`); simpan `completionResult` (`COMPLETED` | `PARTIALLY_COMPLETED`), catatan, aktor, timestamp; timeline event `complaint.appointment_completed`; tombol + confirm dialog (API-308). Out of scope: Complaint/Escalation Close, Customer No Show, SLA/Notification/Survey/Rating, Calendar/Auto Close.

**Business Context**
DEC-008 berhenti di check-in; penyelesaian kunjungan belum berotorisasi.

**Reason**
Sama dengan DL-008: perluasan satu langkah yang eksplisit.

**Alternatives Considered**
Tidak dicatat di sumber.

**Impact**
Domain Appointment · API-308 · Timeline · UI.

**Affected Documents**
`07 API Catalog/` · `08 Event Catalog/` · `27 Project Decisions/DEC-009_Appointment_Completion_Scope_TASK016_v1.0.md`

**Related Decisions**
DL-007 · DL-008 · DL-010 · DL-011 · DL-017 (completion fact SLA)

**Supersedes**
DEC-008 **sebagian**.

**Notes**
`completed_at` appointment kemudian dipakai sebagai *completion fact* tahap Appointment pada evaluasi SLA (DL-017).

---

#### DL-010 — Ruang Lingkup Customer No Show

| Field | Value |
|---|---|
| **Decision ID** | DL-010 |
| **Title** | Customer No Show Scope (TASK-017) |
| **Status** | Approved (DEC-010, 2026-07-23) |

**Decision**
**Partial extension DEC-007 untuk Customer No Show saja.** In scope: menandai sekali appointment `BOOKED` menjadi `NO_SHOW` (API-309); simpan alasan, aktor, timestamp; timeline event terkait. Out of scope tetap mengikuti rantai DEC-007…009.

**Business Context**
Pelanggan yang tidak hadir tidak punya representasi status sebelum keputusan ini.

**Reason**
Melengkapi jalur pengecualian appointment tanpa membuka Calendar/Slot/Auto Close.

**Alternatives Considered**
Tidak dicatat di sumber.

**Impact**
Domain Appointment · API-309 · Timeline.

**Affected Documents**
`07 API Catalog/` · `08 Event Catalog/` · `27 Project Decisions/DEC-010_Appointment_NoShow_Scope_TASK017_v1.0.md`

**Related Decisions**
DL-007 · DL-008 · DL-009 · DL-011

**Supersedes**
DEC-007 **sebagian**.

**Notes**
`NO_SHOW` ditolak sebagai prasyarat Final Resolution (lih. DL-011).

---

#### DL-011 — Ruang Lingkup Final Resolution

| Field | Value |
|---|---|
| **Decision ID** | DL-011 |
| **Title** | Final Resolution Scope (TASK-018) |
| **Status** | Approved (DEC-011, 2026-07-23) |

**Decision**
**Perluas modul resolutions dan entitas `complaint_resolutions` yang sudah ada — jangan buat modul baru.** In scope: submit Final Resolution sekali per complaint setelah appointment `COMPLETED` (API-310); simpan summary, catatan, flag follow-up, aktor, timestamp; timeline event `complaint.final_resolution_submitted`; section Final Resolution di Complaint Detail UI. Business rules: complaint harus `IN_PROGRESS`; appointment harus `COMPLETED` (tolak `NO_SHOW`); satu Final Resolution per complaint; complaint **tetap** `IN_PROGRESS` dan escalation **tetap** `APPROVED` — **jangan** menutup keduanya. Out of scope: Closure, approval workflow, SLA/Notification/Survey, Auto Close.

**Business Context**
Hasil akhir penanganan setelah kunjungan selesai belum punya tempat penyimpanan resmi.

**Reason**
Menambah fakta bisnis tanpa menyentuh gerbang closure yang masih diatur keputusan lain.

**Alternatives Considered**
Tidak dicatat di sumber (yang dicatat: tidak membuat modul baru).

**Impact**
Domain Resolution · API-310 · Timeline · UI Complaint Detail · SLA (completion fact Resolution).

**Affected Documents**
`07 API Catalog/` · `08 Event Catalog/` · `27 Project Decisions/DEC-011_Final_Resolution_Scope_TASK018_v1.0.md`

**Related Decisions**
DL-009 · DL-010 · DL-017 · DL-024 (BQ-007/BQ-008 closure)

**Supersedes**
—

**Notes**
Pemisahan tegas "resolusi ≠ closure" di sini konsisten dengan BQ-007 (Close Case tidak otomatis menutup Complaint) pada DL-024.

---

#### DL-012 — Escalation Visibility, Return & Result Audience

| Field | Value |
|---|---|
| **Decision ID** | DL-012 |
| **Title** | Visibilitas eskalasi, pengembalian, dan audiens hasil (DEC-F4) |
| **Status** | **Locked pada level bisnis** (Business Owner workshop, 2026-07-29) — **menunggu countersign Architecture Board**; berkas DEC-F4 berstatus 🟡 Proposed |

**Decision**

| ID | Keputusan |
|---|---|
| F4 | Model visibilitas **B**: handler Pusat hanya mengerjakan case yang dieskalasi/di-assign ke Pusat; role analis/viewer boleh KPI/monitoring lintas cabang tanpa akses detail default ke case cabang yang tidak dieskalasi |
| F4.1 | **Tidak ada Regional** pada jalur eskalasi — jalur adalah **Cabang → Pusat** saja |
| F4.2 | Setelah Pusat **resolve**, cabang asal **selalu** boleh membaca hasil |
| F4.3 | Pusat memilih audiens hasil: `ORIGIN_BRANCH` atau `ALL_BRANCHES` |
| F4.3a | `result_visibility` ditetapkan saat Resolve dan **boleh diubah kemudian** (audit wajib) |
| F4.4 | Pusat boleh **mengembalikan** eskalasi ke cabang asal bila informasi/paket tidak lengkap |
| F4.5 | Return wajib **reason code** + **catatan bebas** |
| F4-OQ-01 | Panjang minimum `return_note` = **10** (trim lalu hitung) |
| F4-OQ-02 | Cabang asal **read-only** selama Case dimiliki Pusat; boleh menulis setelah Return |

**Business Context**
ECMP akan beroperasi sebagai Enterprise Business Module (ADR-014); dibutuhkan keputusan workshop tentang visibilitas Head Office, ada/tidaknya tier Regional, visibilitas hasil ke cabang, dan kemampuan mengembalikan eskalasi.

**Reason**
Menetapkan batas visibilitas dan kepemilikan kerja lintas cabang/pusat sebelum FRD Escalation/Resolution dan OpenAPI Planned berjalan.

**Alternatives Considered**
Model visibilitas A vs **B** (B dipilih); ada/tidaknya tier Regional (tidak ada).

**Impact**
Escalation · Resolution · Authorization/visibility · FRD lanjutan · OpenAPI Planned · Event Planned · Audit.

**Affected Documents**
`18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md` · `…/ECMP_DEC_F4_Architecture_Board_Countersign_Pack_v1.0.md` · `26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md` · `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` (BR-007/BR-008, Draft)

**Related Decisions**
DL-006 · DL-024 · DL-039 · DL-065

**Supersedes**
Tidak mengubah FRD-CM-001 Batch 1 (tetap LOCKED); DEC-F4 mengubah **BR-CM-CAT-001 Draft** sebagai spesifikasi bisnis target untuk batch FRD berikutnya.

**Notes**
Dicatat di DL-000 karena keputusan bisnisnya eksplisit **Locked** oleh Business Owner. Status governance-nya belum penuh (countersign Board belum tercatat) — diangkat juga di Bagian 6.

---

### 3.B Organization

---

#### DL-013 — Kepemilikan Struktur Organisasi

| Field | Value |
|---|---|
| **Decision ID** | DL-013 |
| **Title** | Enterprise Platform memiliki Organization / Branch / Department; ECMP menyimpan referensi saja |
| **Status** | Approved with Conditions (ADR-014 v1.4 — PROGRAM-BOARD-004 BR-009; kondisi C-1, C-3, C-7) |

**Decision**
Di bawah **Mode B**, Enterprise Platform memiliki kebenaran hierarki Organization, Branch, dan Department. ECMP menyimpan **referensi saja** (`organization_id`, `branch_id`, `department_id`) dan tidak boleh menjadi master hierarki organisasi. Organization Synchronization dinyatakan **Architecture Dependency** (bukan enhancement opsional) karena otorisasi bergantung pada hierarki organisasi yang tetap tersedia dan benar. Protokol, frekuensi, dan transport sinkronisasi ditunda ke ADR lanjutan.

**Business Context**
ECMP awalnya didesain standalone dengan identitas dan organisasinya sendiri; roadmap enterprise mengubahnya menjadi Business Module di dalam Enterprise Platform.

**Reason**
Menghilangkan duplikasi master organisasi antar modul dan menjaga otorisasi ECMP tetap berbasis kebenaran enterprise.

**Alternatives Considered**
Tercatat di ADR-014 §Options Considered (mempertahankan identitas/organisasi lokal vs menyerahkan ke Enterprise Platform); opsi enterprise dipilih.

**Impact**
Authorization scoping · Data model (referensi) · Integrasi · Mode B readiness.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4.md` · `…/ECMP_ADR_018_…_v1.0.md` · `06 Data Dictionary/` · `09 Integration Catalog/` · `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`

**Related Decisions**
DL-014 · DL-015 · DL-039 · DL-040 · DL-048 · DL-049

**Supersedes**
Asumsi desain standalone bahwa ECMP memiliki master organisasi.

**Notes**
Accept ini **tidak** membuka Mode B (C-7). Gap model organisasi tetap prasyarat unlock Mode B (C-B6-3, lih. DL-049).

---

#### DL-014 — Arsitektur Sinkronisasi Organisasi

| Field | Value |
|---|---|
| **Decision ID** | DL-014 |
| **Title** | Enterprise Organization Synchronization Architecture |
| **Status** | Approved with Conditions (ADR-018 v1.0 — PROGRAM-BOARD-006 BR-013; kondisi C-B6-1…C-B6-7) |

**Decision**
1. **Tujuan:** menjaga Organization Reference enterprise tetap *resolvable* untuk scoping otorisasi dan penggunaan operasional di bawah Mode B.
2. **System of Record:** Enterprise Platform memiliki kebenaran hierarki Organization/Branch/Department.
3. **Peran ECMP:** mengonsumsi dan memelihara **projeksi lokal non-otoritatif**, menyimpan referensi saja; tidak pernah mengarang kebenaran hierarki enterprise.
4. **Konsistensi:** eventual consistency dengan semantik **"as of"** eksplisit; kebenaran enterprise menang saat konflik.
5. **Kegagalan:** Organization Reference wajib yang tidak dapat di-resolve untuk AuthZ → **deny / fail closed** (tidak ada hierarki yang dikarang).
6. Transport, API, skema, penjadwalan, dan strategi cache **ditunda**.
7. ADR ini **tidak** membuka implementasi Mode B.

**Business Context**
ADR-014 menetapkan kepemilikan organisasi di Enterprise Platform tetapi menunda cara sinkronisasinya; tanpa arsitektur ini, tim bisa mengarang hierarki atau membuat ECMP menjadi SoR bayangan.

**Reason**
Otorisasi bergantung pada referensi organisasi yang dapat di-resolve; ketidakjelasan menghasilkan perilaku fail-open atau projeksi yang menjadi SoR terselubung.

**Alternatives Considered**
Tercatat di ADR-018 §4 Options Considered (mis. tanpa projeksi lokal, projeksi otoritatif, projeksi non-otoritatif); projeksi non-otoritatif dipilih.

**Impact**
Authorization · Integrasi · Data model projeksi · Operasi (sync) · Mode B readiness.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_018_Enterprise_Organization_Synchronization_Architecture_v1.0.md` · `09 Integration Catalog/` · `10 Security and Access Standards/` (SEC-ORG-SYNC-001) · `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md` · `18 Architecture Governance/ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md`

**Related Decisions**
DL-013 · DL-040 · DL-042 · DL-049

**Supersedes**
—

**Notes**
Dua turunan O-06 (descendant scope) dan O-07 (orphan remediation) **masih Proposed** — lih. Bagian 6.

---

#### DL-015 — Validasi Organisasi-Lokasi & Enforcement Permission Modul (Mode A)

| Field | Value |
|---|---|
| **Decision ID** | DL-015 |
| **Title** | ECMP-EBS-001 — Organization Location + Complaint Module Authorization |
| **Status** | Approved (EBS-001 v1.0.0, 2026-08-04; Mode A `ECMP_AUTH_MODE=dev`) — implementasi Commit 1–7, PR belum dibuka |

**Decision**
Menutup arah kedua validasi organisasi-lokasi untuk user: role ber-scope **head office tidak boleh membawa `branchId`** (cermin dari arah "branch wajib" yang sudah berlaku), dan memperluas enforcement model permission modul komplain ke dua permukaan frontend yang sebelumnya tanpa kontrol: navigasi sidebar dan rute `/complaints`. Klasifikasi role: `SUPER_ADMIN` (opsional), branch-scoped (`AGENT`, `CS_AGENT`, `BRANCH_OFFICER`, `SUPERVISOR`, `BRANCH_SUPERVISOR` — wajib), head-office scoped (`ADMIN`, `ADMINISTRATOR`, `HO_SCHEDULER`, `HEAD_OFFICE_SCHEDULER`, `SCHEDULER`, `HO_ENGINEER`, `HEAD_OFFICE_ENGINEER` — dilarang), unclassified (opsional). Ini **enforcement dan konsistensi UX**, bukan redesign: tidak ada model otorisasi, katalog permission, atau katalog role baru.

**Business Context**
Aturan organisasi-lokasi hanya ditegakkan satu arah, dan modul komplain tidak punya kontrol visibilitas/akses di frontend.

**Reason**
Menegakkan aturan bisnis Mode A dan permission modul komplain yang **sudah ada** secara konsisten di semua permukaan.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Users service (backend) · Navigasi & rute frontend · Otorisasi Mode A.

**Affected Documents**
`18 Architecture Governance/ECMP_EBS_001_Org_Location_Complaint_Authorization_v1.0.md` · `docs/governance/ECMP-EBS-001.md` · `deploy/evidence/EBS-001_Mode_A_Org_Location_Authorization_20260804.md`

**Related Decisions**
DL-004 (BR-ECMF-02) · DL-013 · DL-056

**Supersedes**
—

**Notes**
Sumber mencatat eksplisit **out of scope**: Mode B, Enterprise entitlement, OIDC, Identity Adapter, CAP-006, CAP-005, DEC-F4, M4, redesign permission/role, migrasi database, perubahan router. Tidak ada entri traceability baru karena tidak memperkenalkan FR/BR/API baru.

---

### 3.C Timeline (SLA, Deadline, Riwayat Kronologis)

---

#### DL-016 — SLA Deadline Calculator

| Field | Value |
|---|---|
| **Decision ID** | DL-016 |
| **Title** | Snapshot deadline SLA yang immutable saat complaint dibuat |
| **Status** | Approved (DEC-012, 2026-07-23) |

**Decision**
**Perluas modul `app/modules/sla` yang sudah ada** — tanpa modul baru, tanpa migrasi database. Saat complaint dibuat: wajib ada satu SLA policy aktif; policy dievaluasi **sekali** pada saat create; simpan snapshot due-at immutable pada `sla_records` (`assignment_due_at`, `appointment_due_at`, `resolution_due_at`, `escalation_due_at`, `overall_due_at` = `created_at` + target menit masing-masing). Seluruh status dimensi SLA tetap `PENDING`. Baris SLA complaint lama **tidak pernah** dihitung ulang saat policy berubah. Out of scope: breach detection, countdown timer, scheduler/background job, notifikasi.

**Business Context**
TASK-021 menyediakan fondasi `sla_records` (deadline NULL) dan TASK-022 menyediakan SLA policy yang dapat dikonfigurasi (maksimal satu aktif).

**Reason**
Snapshot immutable menjaga deadline sebuah case tidak berubah retroaktif ketika kebijakan SLA diubah.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber (yang dicatat: tidak membuat modul baru, tidak migrasi).

**Impact**
SLA · Complaint create · UI SLA card (API-314).

**Affected Documents**
`11 SLA and KPI Matrix/` · `07 API Catalog/` (API-314…317) · `27 Project Decisions/DEC-012_SLA_Deadline_Calculator_Scope_TASK023_v1.0.md`

**Related Decisions**
DL-005 · DL-017 · DL-018 · DL-019

**Supersedes**
—

**Notes**
DEC-012/013 dicatat sebagai **jalur terpisah** dari CAP-006 dan bukan pemenuhan CAP-006 (BQ-CAP006-15, lih. DL-019).

---

#### DL-017 — SLA Breach Detection

| Field | Value |
|---|---|
| **Decision ID** | DL-017 |
| **Title** | Evaluasi status SLA berbasis event, tanpa scheduler |
| **Status** | Approved (DEC-013, 2026-07-23) |

**Decision**
**Perluas `app/modules/sla`** — tanpa modul baru, tanpa migrasi. **Jangan pernah** membaca ulang SLA Policy saat evaluasi dan **jangan pernah** mengubah `*_due_at`. Aturan evaluasi per tahap (assignment/appointment/resolution/escalation/overall): selesai dan `completed_at <= due_at` → `COMPLETED`; selain itu bila `now <= due_at` → `PENDING`; selain itu → `BREACHED`. Fakta penyelesaian (bukan kebijakan): Assignment = `assigned_at` pertama; Appointment = `completed_at` appointment; Resolution = `final_resolution_at` atau `resolved_at`; Escalation = `closed_at` eskalasi; Overall = `closed_at` complaint. Evaluasi dipicu oleh event bisnis — **tanpa scheduler/cron/worker**.

**Business Context**
Snapshot deadline sudah ada (DL-016) tetapi statusnya belum pernah dievaluasi terhadap kenyataan operasional.

**Reason**
Evaluasi berbasis fakta operasional menjaga konsistensi dengan sumber data dan menghindari komponen runtime baru yang belum berotorisasi.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
SLA · Timeline (DL-018) · KPI (DL-060).

**Affected Documents**
`11 SLA and KPI Matrix/` · `07 API Catalog/` (API-314) · `27 Project Decisions/DEC-013_SLA_Breach_Detection_Scope_TASK024_v1.0.md`

**Related Decisions**
DL-016 · DL-018 · DL-019 · DL-020 · DL-060

**Supersedes**
—

**Notes**
Ketiadaan scheduler di sini konsisten dengan status **Deferred** runtime konkret CAP-006 (DL-021).

---

#### DL-018 — Integrasi SLA ke Timeline

| Field | Value |
|---|---|
| **Decision ID** | DL-018 |
| **Title** | Event SLA memakai `complaint_timelines`, aktor SYSTEM |
| **Status** | Approved (DEC-014, 2026-07-23) |

**Decision**
**Gunakan kembali `complaint_timelines`** — tanpa modul atau tabel timeline SLA terpisah. Setelah setiap evaluasi SLA, terbitkan timeline event **hanya bila** status suatu tahap berubah menjadi `COMPLETED` atau `BREACHED`; evaluasi ulang identik tidak menghasilkan event duplikat. Tipe event: `sla.<stage>.completed` / `sla.<stage>.breached` untuk assignment, appointment, resolution, escalation, overall. Aktor selalu **SYSTEM** (`actor_user_id` null; UI menampilkan "System"). Payload memuat stage, status lama/baru, `dueAt`, dan aktor. Out of scope: notifikasi (email/SMS/push/websocket), dashboard/reporting/KPI, scheduler/queue.

**Business Context**
Operator memerlukan jejak audit transisi SLA yang bermakna pada timeline complaint yang sudah ada.

**Reason**
Satu timeline operasional menghindari dua versi riwayat untuk case yang sama.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber (yang dicatat: tidak membuat timeline SLA terpisah).

**Impact**
Timeline · SLA · UI riwayat · Audit operasional.

**Affected Documents**
`08 Event Catalog/` · `07 API Catalog/` (API-209, API-314) · `27 Project Decisions/DEC-014_SLA_Timeline_Integration_Scope_TASK025_v1.0.md`

**Related Decisions**
DL-016 · DL-017 · DL-060 · DL-061

**Supersedes**
—

**Notes**
Aktor SYSTEM di timeline adalah satu-satunya aktor non-manusia yang disetujui pada jalur ini.

---

#### DL-019 — Penutupan Keputusan Bisnis CAP-006 (SLA Engine)

| Field | Value |
|---|---|
| **Decision ID** | DL-019 |
| **Title** | DEC-CAP006-BQ-001 — penutupan BQ-CAP006-01…15 |
| **Status** | CLOSED / Approved (Business Owner + Performance Owner, 2026-08-01; FRD-005 LOCKED pada B2-16) |

**Decision**

| BQ | Hasil |
|---|---|
| 01 SoT scope | CLOSED — Option A (FRD-005 / SLA-MTX / EVT-004) |
| 02 Calendar | CLOSED — **24x7** baseline; Working Day **DEFERRED** |
| 03 Clock ownership (runtime) | CLOSED — KPI service mengevaluasi & menerbitkan |
| 04 Clock start | CLOSED — **EVT-001** |
| 05 Clock stop | CLOSED — **EVT-005** |
| 06 Pause / Resume | **DEFERRED** — out of scope CAP-006 v1 |
| 07 Reopen / re-breach | CLOSED — **EVT-007**, re-breach diperbolehkan |
| 08 Scheduler mechanism | CLOSED (outcome) — mekanisme = ranah engineering/ADR |
| 09 Warning 80% | CLOSED — mengikuti DEC-005 |
| 10 Breach + EVT-004 | CLOSED — DEC-005 / FR-030 |
| 11 Notification | CLOSED — Notification + BR-NOTIF-04 |
| 12 Administration / Config | CLOSED — Administration memiliki SLA Config |
| 13 Runtime ownership | CLOSED — runtime KPI; governance Ops Lead |
| 14 Case-type differentiation | **DEFERRED** — seragam sampai ada DEC Business Owner |
| 15 Relasi DEC-012/013 | CLOSED — jalur terpisah, **bukan** pemenuhan CAP-006 |

**Business Context**
CAP-006 (SLA Engine) tidak dapat dikunci tanpa keputusan bisnis atas kalender, jam kerja, kepemilikan clock, dan pemicu event.

**Reason**
Menutup residual business question agar FRD-005 dapat dikunci tanpa mengarang mekanisme runtime.

**Alternatives Considered**
Tercatat per BQ pada paket keputusan B2-15 (mis. Option A untuk SoT scope).

**Impact**
SLA Engine · KPI runtime · Notification · Administration (SLA config) · FRD-005.

**Affected Documents**
`deploy/evidence/B2-15_CAP-006_Business_Decision_Closure_20260801.md` · `deploy/evidence/B2-16_CAP-006_FRD_Lock_Governance_Closure_20260801.md` · `03 Functional Requirements/` (FRD-005) · `11 SLA and KPI Matrix/` · `08 Event Catalog/`

**Related Decisions**
DL-004 · DL-005 · DL-016 · DL-017 · DL-020 · DL-021 · DL-060

**Supersedes**
—

**Notes**
Tiga butir **DEFERRED** (pause/resume v1, aktivasi Working Day, pemisahan target per case type) adalah penundaan eksplisit yang disetujui, bukan pertanyaan terbuka.

---

#### DL-020 — Kelas Mekanisme Evaluasi CAP-006 = Hybrid

| Field | Value |
|---|---|
| **Decision ID** | DL-020 |
| **Title** | ADR-CAP006-001 — mechanism class Hybrid + Time Source wajib |
| **Status** | Accepted (Architecture Board, 2026-08-01 — B2-20); runtime konkret **Deferred** |

**Decision**
Penetapan Board: Time Source **wajib** (ARC-CAP006-001); konsumsi lifecycle event **tetap wajib** (FRD-005 §6; DEC-CAP006-BQ-001); CAP-006 memerlukan **keduanya**; klasifikasi arsitektur = **Hybrid**. Hybrid berarti lifecycle event (EVT-001/003/005/007) memasok dan memperbarui **state** clock SLA (start, status, stop/finalize, reopen restart), sementara Time Source menyediakan stimulus evaluasi berbasis waktu. Runtime konkret (scheduler/job/poll/worker) **ditunda**.

**Business Context**
Deteksi breach mendekati real-time membutuhkan stimulus waktu, sementara state clock hanya bisa berasal dari event lifecycle domain.

**Reason**
Memilih satu saja (event-only atau time-only) tidak dapat memenuhi FRD-005; Hybrid mencatat kebutuhan keduanya tanpa memilih mekanisme implementasi.

**Alternatives Considered**
Tercatat di ADR-CAP006-001 (event-driven only · time-driven only · hybrid); hybrid dipilih.

**Impact**
SLA Engine · KPI · Event Catalog · Otorisasi implementasi FR-030.

**Affected Documents**
`05 Architecture Decision Records/ADR-CAP006-001_Evaluation_Mechanism.md` · `…/ARC-CAP006-001_Time_Source.md` · `deploy/evidence/B2-20_…md` · `deploy/evidence/B2-17E_…md`

**Related Decisions**
DL-017 · DL-019 · DL-021 · DL-030

**Supersedes**
—

**Notes**
Accept kelas mekanisme **bukan** izin membangun engine FR-030.

---

#### DL-021 — Arsitektur Runtime Konseptual CAP-006

| Field | Value |
|---|---|
| **Decision ID** | DL-021 |
| **Title** | ARC-CAP006-002 — runtime evaluasi CAP-006 berada di KPI & Performance |
| **Status** | Accepted (B2-21, 2026-08-01) — **bukan** otorisasi implementasi |

**Decision**
Penetapan Board: CAP-006 **bukan** domain baru dan **bukan** service produk baru; ia adalah **runtime concern** yang berjalan di dalam **KPI & Performance**. Accept konsep **bukan** izin membangun engine FR-030. `ARCH-EXEC-RT-001` (`20 Domain Architecture/Execution/EXECUTION_RUNTIME_ARCHITECTURE.md`) dinyatakan **bukan SoT CAP-006** dan tidak diadopsi sebagai Runtime Architecture CAP-006 pada B2-21.

**Business Context**
Tanpa penempatan runtime yang jelas, evaluasi SLA berisiko dibangun sebagai domain/service baru.

**Reason**
Menjaga batas domain: SLA evaluation adalah concern kinerja, bukan domain bisnis tambahan.

**Alternatives Considered**
Adopsi ARCH-EXEC-RT-001 sebagai runtime SoT (ditolak pada B2-21).

**Impact**
Domain Architecture · KPI · Roadmap implementasi CAP-006.

**Affected Documents**
`05 Architecture Decision Records/ARC-CAP006-002_Runtime_Architecture.md` · `20 Domain Architecture/` · `deploy/evidence/B2-21_…md` · `deploy/evidence/B2-22_CAP-006_Concrete_Runtime_Non_Invent_Gate_20260801.md` · `deploy/evidence/B2-24_CAP-006_Stay_Deferred_Confirmation_Blocker_Freeze_20260804.md`

**Related Decisions**
DL-019 · DL-020 · DL-060

**Supersedes**
—

**Notes**
B2-22 menetapkan gerbang "non-invent" untuk runtime konkret; B2-24 membekukan status Deferred tersebut.

---

### 3.D Workflow

---

#### DL-022 — G1 Contract Freeze

| Field | Value |
|---|---|
| **Decision ID** | DL-022 |
| **Title** | Pembekuan kontrak lifecycle (Sprint-02A, gate G1) |
| **Status** | Accepted — contract freeze (DEC-006, 2026-07-21) |

**Decision**

| ID | Putusan |
|---|---|
| D1 | Transisi/state ilegal → **HTTP 409** (konflik state resource), bukan 400. 400 tetap khusus `VALIDATION_ERROR`. Berlaku untuk API-004 transisi ilegal dan API-003 saat case tidak assignable |
| D2 | Nama permission transisi = **`cases:status`**; alias `cases:transition` dihapus dari seluruh dokumen delivery |
| D3 | Pola penamaan permission `cases:<action>` **dikunci**: `cases:create`, `cases:read`, `cases:assign` (Supervisor), `cases:status` (Handler) |
| D4 | Payload **EVT-002** `{caseId, assigneeId, unitId, assignedBy, previousAssigneeId?, assignedAt}` dan **EVT-003** `{caseId, fromStatus, toStatus, changedBy, changedAt, reason?}` **frozen**; `resolutionCode` (nullable, MANDATORY untuk →CLOSED) ditambahkan ke `StatusChangeRequest`; `reason` mandatory untuk override Administrator **dan** `CLOSED→REOPENED` |

Perubahan payload berikutnya memerlukan keputusan freeze baru.

**Business Context**
Entry gate G1 mensyaratkan kontrak API-003/API-004 dan payload EVT-002/EVT-003 ter-merge sebelum kode; review menemukan lima inkonsistensi terbuka.

**Reason**
Membedakan "perbaiki request" (400) dari "muat ulang state case" (409), menyeragamkan penamaan permission mengikuti endpoint, dan menutup celah antara guard closure (BR-ECMF-06) dengan payload EVT-005.

**Alternatives Considered**
D1: 400 vs **409**. D2: `cases:transition` vs **`cases:status`**.

**Impact**
API Catalog · Event Catalog · Security Role Access Matrix · Test cases · Implementasi Sprint-02B.

**Affected Documents**
`07 API Catalog/` (API-003, API-004, `case-actions.v1`) · `08 Event Catalog/events.yaml` · `10 Security and Access Standards/` (SEC-RAM-001) · `13 Test Strategy/` · `27 Project Decisions/DEC-006_Contract_Freeze_G1_Sprint02A_v1.0.md`

**Related Decisions**
DL-023 · DL-024 · DL-034 · DL-051 · DL-056

**Supersedes**
Acceptance criteria FRD-002 §6 yang menulis 400 untuk transisi ilegal; alias permission `cases:transition`.

**Notes**
Butir terbuka **U-1** (subset reopen) DEC-006 kemudian ditutup untuk Mode A oleh G2 mini-gate (lih. DL-051): `CLOSED→REOPENED` di luar Mode A DoD, EVT-007 tetap Proposed.

---

#### DL-023 — Case State Machine: Dual SoT (Option O3)

| Field | Value |
|---|---|
| **Decision ID** | DL-023 |
| **Title** | DEC-BQ001 — Sprint = Definition A, Aggregate = Definition B |
| **Status** | **APPROVED** (Business Owner / Architecture Board, 2026-08-01) |

**Decision**
Option **O3 — Dual SoT eksplisit**: state machine Case untuk jalur Sprint / case-centric adalah **DOM-ECMF-003 (Definition A)** (`REGISTERED → ASSIGNED → IN_PROGRESS → PENDING_REVIEW → CLOSED → REOPENED`), sementara Aggregate CAP-02 memakai **BR-CM-CAT Definition B** (`CREATED → ASSIGNED → IN_PROGRESS → PENDING/ESCALATED → RESOLVED → CLOSED`, dengan `CANCELLED` sebelum resolusi final). Tanpa redesign, tanpa opsi baru.

**Business Context**
Repositori memuat dua definisi status Case yang tidak kompatibel; CAP-02 (Create/Update/Resolve/Close Case) tidak dapat di-Business-Lock tanpa enum dan matriks kanonik.

**Reason**
Batch-1 sudah mengunci Complaint sebagai Aggregate Root dan Case sebagai child — semantik yang berbenturan dengan Case-as-intake pada DOM-ECMF-003. Dual SoT eksplisit mencegah salah satu definisi menimpa yang lain secara diam-diam.

**Alternatives Considered**
O1 / O2 / **O3** (rekomendasi paket keputusan BQ-001); O3 disetujui.

**Impact**
Domain Case · CAP-02/CAP-008 · FRD-CM-001 · Traceability · Implementasi dua namespace.

**Affected Documents**
`18 Architecture Governance/reviews/ECMP_DEC_BQ001_Case_State_Machine_O3_v1.0.md` · `…/ECMP_DEC_BQ001_Architecture_Board_Countersign_Pack_v1.0.md` · `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` · `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` · `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` · `docs/product/CAP-02_…_v1.0.md`

**Related Decisions**
DL-003 · DL-022 · DL-024 · DL-044

**Supersedes**
—

**Notes**
Menutup **BQ-001 / BQ-CAP02-001**. Konsisten dengan DL-044 (dual SoT tanpa forced merge).

---

#### DL-024 — Mode A Case Management Delivery Baseline (BQ-002…BQ-014)

| Field | Value |
|---|---|
| **Decision ID** | DL-024 |
| **Title** | Lock pack keputusan bisnis Batch-2 Mode A (CAP-008) |
| **Status** | **ALL LOCKED** (Product Owner Decision Session, 2026-08-01); residual BQ = **ZERO** |

**Decision**

| BQ | Keputusan terkunci |
|---|---|
| BQ-002 | Complaint **MAY** didaftarkan tanpa Case; setiap Complaint **MUST** punya ≥1 Case dalam **1 hari kerja** setelah `REGISTERED`; Supervisor Queue **MUST** menampilkan yang melewati ambang ini |
| BQ-003 | Maksimum default **5** Case per Complaint; kebijakan override di luar Mode A |
| BQ-004 | Case Number **independen** dari Complaint Number; format `CASE-YYYY-NNNNNN` |
| BQ-005 | Case **SHALL** mengikat SLA Policy Version; **countdown SLA tidak diaktifkan** di Mode A (bind-without-clock) |
| BQ-006 | Assignment **hanya pada level Unit**; Assigned User di luar Mode A |
| BQ-007 | Close Case = Case → `CLOSED` saja; **MUST NOT** otomatis menutup Complaint Aggregate |
| BQ-008 | Alur Mode A: `IN_PROGRESS → RESOLVED →` Supervisor Approval `→ CLOSED` |
| BQ-009 | State `PENDING`/`ESCALATED` tetap terdefinisi di Aggregate State Machine, tetapi **tidak diekspos** Mode A |
| BQ-010 | Resolve **wajib** Comment; Attachment opsional; Complaint Attachment boleh dipakai ulang |
| BQ-011 | CTO **D-02** tetap: intake Complaint tidak membuat Case saat registrasi; "wajib Case awal" tidak diaktifkan; timing wajib Case diatur BQ-002 |
| BQ-012 | Capability Identifier final = **CAP-008** |
| BQ-014 | `CANCELLED` **termasuk** Mode A; alasan mencakup Duplicate, Wrong Input, Customer Cancellation |

BQ-001/BQ-013 sudah terkunci lebih dulu lewat DL-023.

**Business Context**
Batch-2 Mode A Case Management memerlukan baseline bisnis yang tuntas sebelum FRD dan OpenAPI dapat dikunci.

**Reason**
Menghilangkan residual business question sehingga delivery Mode A dapat ditutup tanpa asumsi implisit di kode.

**Alternatives Considered**
Tercatat per BQ pada paket keputusan; hasil akhir seperti tabel di atas.

**Impact**
Domain Case · Supervisor Queue · SLA binding · Assignment · Resolution/Closure · CAP-008 · FRD-CM-B2-001 · OpenAPI API-530…535.

**Affected Documents**
`18 Architecture Governance/reviews/ECMP_DEC_ModeA_Delivery_Baseline_BQ_Lock_Pack_v1.0.md` · `…/ECMP_DM_ModeA_Delivery_Baseline_Decision_Matrix_v1.0.md` · `03 Functional Requirements/` (FRD-CM-B2-001) · `07 API Catalog/` · `26 Traceability/`

**Related Decisions**
DL-011 · DL-016 · DL-023 · DL-052

**Supersedes**
Menutup **OQ-CM-B1-004** (lewat BQ-002).

**Notes**
BQ-005 penting untuk BC-000: SLA **diikat** tapi **tidak berjalan** di Mode A.

---

#### DL-025 — Kepemilikan Konfigurasi Workflow

| Field | Value |
|---|---|
| **Decision ID** | DL-025 |
| **Title** | Workflow Config SoT = Administration; ECMF sebagai enforcer |
| **Status** | Approved (ADR-008, Accepted) |

**Decision**
Definisi status & transisi per kategori adalah **konfigurasi bisnis** (BR-001 / BR-ECMF-03) yang dimiliki **Administration**, diversi sesuai BR-ADM-03, dan dipublikasikan lewat **EVT-006 `ConfigChanged`**. **ECMF adalah enforcer**: memuat config aktif dan menolak transisi tidak valid; ECMF tidak mendefinisikan transisi sendiri.

**Business Context**
Tanpa kepemilikan yang jelas, definisi workflow bisa hidup di dua tempat (kode ECMF dan konfigurasi Administration).

**Reason**
Perubahan proses bisnis rutin tidak boleh membutuhkan deployment kode, sementara integritas transisi tetap ditegakkan satu komponen.

**Alternatives Considered**
Tercatat di ADR-008 (kepemilikan di ECMF vs Administration).

**Impact**
Administration · ECMF · Event Catalog (EVT-006) · Audit perubahan konfigurasi.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_008_RBAC_SoT_Workflow_Ownership_v1.0.md` · `08 Event Catalog/` · `06 Data Dictionary/` · `02 Business Rules/`

**Related Decisions**
DL-026 · DL-056 · DL-065

**Supersedes**
—

**Notes**
Butir kedua ADR-008; butir pertama (Role-Permission SoT) dicatat sebagai DL-056, butir ketiga (audit) sebagai DL-065.

---

#### DL-026 — Configuration-First Principle

| Field | Value |
|---|---|
| **Decision ID** | DL-026 |
| **Title** | Rule Configuration vs Hardcoded |
| **Status** | Approved (ADR-003, Accepted — Architecture Board 2026-07-21) |

**Decision**
Rule yang tergolong **Configuration** pada `02 Business Rules` (workflow transition, formula SLA, kategori/prioritas, mapping role-permission, notification rule) dibangun di atas **config engine dengan versioning dan effective date** (BR-ADM-03). Rule yang tergolong **Hardcoded** (autentikasi wajib, audit trail immutable, dashboard read-only, resolusi wajib saat closure) **tidak boleh** dijadikan opsi konfigurasi yang bisa dimatikan.

**Business Context**
Perubahan proses bisnis rutin (kategori baru, SLA baru) sebelumnya menuntut deployment kode.

**Reason**
Memisahkan aturan yang boleh berubah secara operasional dari aturan keamanan/integritas inti yang harus terlindungi dari kesalahan konfigurasi.

**Alternatives Considered**
Option A (semua hardcoded) vs **Option B** (config engine untuk kelas Configuration); B dipilih.

**Impact**
Administration · ECMF · SLA · Notification · Security · Dashboard.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_003_Configuration_First_Principle_v1.0.md` · `02 Business Rules/` · `04 Solution Architecture/`

**Related Decisions**
DL-004 · DL-025 · DL-061 · DL-064

**Supersedes**
—

**Notes**
Daftar "Hardcoded" adalah sumber langsung beberapa aturan Audit (DL-064) dan Reporting (dashboard read-only, DL-061).

---

### 3.E UX

---

#### DL-001 — Merge Front Office dan Complaint Officer

| Field | Value |
|---|---|
| **Decision ID** | DL-001 |
| **Title** | Merge Front Office / Customer Service dan Complaint Officer |
| **Status** | Approved (keputusan UX Review, UX-001 Documentation Update, 2026-08-05) — dokumen turunan (PDS-001, PWDM-001, IA-001, NAV-001, WF-000, WF-PLAN-001, WF-001-01) masih **Draft menunggu Review/Approval** |

**Decision**
Front Office / Customer Service dan Resolver / Case Handler digabung menjadi **satu persona UX bernama Complaint Officer**. Closed set persona operasional berubah dari **empat** menjadi **tiga**: **Complaint Officer · Supervisor · Manager**. Complaint Officer memiliki dua **mode kerja situasional** dalam satu persona: **intake** dan **penanganan aktif**. Penggabungan tidak menghilangkan satu pun tanggung jawab, JTBD, atau kebutuhan informasi dari kedua persona lama. Tidak ada kenaikan otoritas: `ASSIGNED` dan `CLOSED` **tetap** R/A milik Supervisor; kapabilitas assign/close pada Complaint Officer hanya kondisional bila diberi izin Authorization. Administrator tetap di luar closed set (persona konfigurasi platform, bukan persona operasional workspace).

**Business Context**
Hasil UX Review: memisahkan Front Office/Customer Service dari Complaint Officer menciptakan kompleksitas UX yang tidak perlu; sistem memodelkan satu persona operasional. Dokumen lama sudah mencatat bahwa kedua peran kerap dirangkap satu orang di unit kecil.

**Reason**
Perbedaan yang selama ini memisahkan keduanya adalah perbedaan **Role & Permission**, bukan perbedaan **Persona** — sejalan dengan prinsip "Persona ≠ Role String" yang sudah berlaku sebelum revisi ini.

**Alternatives Considered**
Mempertahankan empat persona terpisah (ditolak — kompleksitas UX tanpa dasar perbedaan pekerjaan); overwrite PDS-000 (ditolak — melanggar aturan "No Persona Redefinition Without Version Bump", karena itu dibuat PDS-001).

**Impact**
Persona · Workflow · Navigation · Information Architecture · Wireframe · Backlog wireframe (kepemilikan layar) · Screen ownership.

**Affected Documents**
`docs/ux/PDS-001-Persona-Design-Specification.md` · `docs/ux/PDS-000-Persona-Design-Specification.md` (superseded, baseline historis) · `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md` · `docs/ux/IA-001-Information-Architecture.md` · `docs/ux/NAV-001-Navigation-Architecture.md` · `docs/ux/WF-000-Wireframe-Constitution-Layout-System.md` · `docs/ux/WF-PLAN-001-Wireframe-Roadmap-Backlog.md` · `docs/ux/WF-001-01-Global-Shell-Header.md` · `docs/ux/UX-FOUNDATION-000-Complaint-Module-UX-Foundation.md` · `12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` (UX-001 v0.2)

**Related Decisions**
DL-027 · DL-028 · DL-029

**Supersedes**
`PDS-000` (untuk closed set persona) dan `ECMP_Personas_And_Journeys_v0.1.md` (untuk pertanyaan "siapa & tujuan persona"); pada UX-001, **P-01 CS Agent** + **P-04 Handler** → **P-01 Complaint Officer**.

**Notes**
Status paket UX Foundation sebelumnya (READY FOR APPROVAL) **dicabut** karena revisi ini; paket wajib melalui Review ulang. Manager tercatat **belum punya padanan peran teknis** di Authorization — gap terbuka, bukan keputusan.

---

#### DL-027 — Case Workspace Experience Constitution

| Field | Value |
|---|---|
| **Decision ID** | DL-027 |
| **Title** | CWX-000 — konstitusi produk pengalaman Case Workspace |
| **Status** | 🔒 **LOCKED** (2026-08-03) |

**Decision**
CWX mendefinisikan **bagaimana pengguna bekerja di dalam Case Workspace** dan **bukan** tempat mendefinisikan Business Rules, API, Domain Model, Data Ownership, SoR, Workflow Engine, atau Architecture Pattern (hanya merujuk). **Dual-SoT** ditegakkan: Foundation (`/api/v1/complaints`) dan Aggregate (`/api/v1/cm`) — *no silent merge, no rewrite without Architecture Decision, Mode B not unlocked*. Sembilan **Golden Rules**: Business First · Case is the Product (Queue = entry) · Context Before Action · Zero Duplicate Context · Progressive Disclosure · Context-Aware Experience · Experience Above Implementation · No Rewrite Without Decision · Reference, Don't Redefine. Living artifacts terbatas pada CWX-000 · M1 · M2 · M3 · M4 · CWX-R; tidak ada CWX-M5 / CWX-v2 / CWX-Architecture / CWX-Business Rules tanpa governance Kategori A.

**Business Context**
EPIC-CW-001 membutuhkan aturan pengalaman yang mengikat agar pengembangan workspace tidak menggeser domain bisnis atau menggabungkan dua SoT secara diam-diam.

**Reason**
Menjaga pengalaman kerja petugas konsisten tanpa memberi jalan bagi redesign domain atau pembukaan Mode B lewat pintu UX.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Seluruh pekerjaan UX/UI Case Workspace · Batas artefak CWX · Dual-SoT.

**Affected Documents**
`18 Architecture Governance/ECMP_CWX_000_Case_Workspace_Experience_Constitution_v1.0.md` · `docs/governance/ECMP-CWX-000.md` · `ECMP-CWX-M1…M4` · `ECMP-CWX-R` · `docs/governance/ECMP-CONSTITUTION-001.md`

**Related Decisions**
DL-001 · DL-028 · DL-044 · DL-046 · DL-047

**Supersedes**
—

**Notes**
CWX-000 tunduk pada ECMP-CONSTITUTION-001 dan tidak mengubah keputusan Board/ADR.

---

#### DL-028 — Penutupan EPIC-CW-001

| Field | Value |
|---|---|
| **Decision ID** | DL-028 |
| **Title** | EPIC-CW-001 Case Workspace Experience — dapat ditutup |
| **Status** | Approved sebagai laporan penutupan (2026-08-03); klasifikasi: **bukan** konstitusi, **bukan** ADR, **bukan** Board Resolution |

**Decision**
Rantai pengalaman **CWX-000 → M1 → M2 → M3 → M4 → CWX-R** telah dijalankan. Capability berstatus **READY** di-compose di atas Foundation (`/api/v1/complaints`) dan Aggregate (`/api/v1/cm`). Capability berstatus **BLOCKED** (Conversation, Notes, Decision Notes, Aggregate Activity Feed, Audit Summary) **tidak** diimplementasikan sesuai gate governance. Verdict: EPIC-CW-001 **dapat ditutup** untuk ruang lingkup pengalaman Case Workspace Mode A yang READY, dengan residual hygiene tercatat sebagai bukan utang domain.

**Business Context**
Petugas perlu menjawab berurutan: apa kasus ini · apa yang sedang terjadi · apa yang boleh saya kerjakan sekarang · apa yang sudah terjadi — tanpa meninggalkan Workspace.

**Reason**
Menutup EPIC dengan batas yang jujur: yang READY dikirim, yang BLOCKED tidak dikerjakan diam-diam.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Case Workspace UI · Backlog CWX · Release evidence v1.3.0-rc.1.

**Affected Documents**
`ECMP-EPIC-CW-001-CLOSURE.md` · `ECMP-CWX-M3.md` · `ECMP-CWX-M4.md` · `ECMP-CWX-R.md` · `deploy/evidence/EPIC-CW-001_Release_Evidence_v1.3.0-rc.1_20260803.md`

**Related Decisions**
DL-027 · DL-044 · DL-047

**Supersedes**
—

**Notes**
Capability BLOCKED tetap BLOCKED — penutupan EPIC bukan otorisasi implementasinya.

---

#### DL-029 — Target Aksesibilitas WCAG 2.2 AA

| Field | Value |
|---|---|
| **Decision ID** | DL-029 |
| **Title** | OD-FE-009 — WCAG 2.2 AA sebagai working target |
| **Status** | **CLOSED / Accepted** (working target) — tanpa klaim konformansi |

**Decision**
**WCAG 2.2 AA** diterima sebagai **working target** aksesibilitas frontend. **Tidak boleh** ada klaim konformansi tanpa audit UX (kondisi C-3).

**Business Context**
Standar aksesibilitas frontend sebelumnya merupakan open decision (OD-FE-009).

**Reason**
Memberi acuan kerja yang jelas bagi tim frontend/UX tanpa mengklaim kepatuhan yang belum diaudit.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Frontend standards · UX review · Definition of Done UI.

**Affected Documents**
`docs/frontend/OPEN_DECISIONS.md` · `docs/frontend/FRONTEND_DEVELOPMENT_STANDARDS_v1.0.md` · `docs/frontend/FRONTEND_ARCHITECTURE_v1.2.md`

**Related Decisions**
DL-045 · DL-001

**Supersedes**
Status OPEN OD-FE-009.

**Notes**
Pembedaan "working target" vs "conformance claim" wajib dipertahankan di dokumen turunan.

---

### 3.F Architecture

---

#### DL-030 — Integrasi Antar-Domain Event-Driven

| Field | Value |
|---|---|
| **Decision ID** | DL-030 |
| **Title** | ADR-001 — Event-Driven Domain Integration |
| **Status** | Approved / Accepted (Architecture Board, 2026-07-21) |

**Decision**
Gunakan **pola event-driven asynchronous** untuk integrasi antar domain: ECMF (dan domain relevan lain) mempublikasikan domain event; KPI, Dashboard, Notification, dan Core Platform (audit) berlangganan sebagai consumer independen. Teknologi broker **belum diputuskan** dan dicatat sebagai follow-up.

**Business Context**
Blueprint §8 sudah mendaftar event minimal antar domain (CaseCreated, CaseAssigned, StatusChanged, SLABreached, CaseClosed, ConfigChanged), tetapi pola integrasinya belum diformalkan.

**Reason**
ECMF adalah sumber kebenaran operasional; KPI/Dashboard/Notification tidak boleh memperlambat atau memblokir transaksi utama, dan domain harus bisa berkembang independen.

**Alternatives Considered**
Option A — Synchronous REST antar domain (ECMF jadi bottleneck); **Option B — Event-driven via message broker, at-least-once** (dipilih).

**Impact**
Semua domain konsumen · Event Catalog · Deteksi breach near-real-time · Skalabilitas.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_001_Event_Driven_Domain_Integration_v1.0.md` · `08 Event Catalog/` · `04 Solution Architecture/` · `01 Business Blueprint/`

**Related Decisions**
DL-020 · DL-035 · DL-060

**Supersedes**
—

**Notes**
Pemilihan broker dipisahkan ke DL-035 (deferral eksplisit).

---

#### DL-031 — ECMP Bukan System of Record Pelanggan

| Field | Value |
|---|---|
| **Decision ID** | DL-031 |
| **Title** | ADR-002 — local read-only cache untuk data pelanggan |
| **Status** | Approved / Accepted (Architecture Board, 2026-07-21) |

**Decision**
Data pelanggan di domain CRM disimpan sebagai **local read-only cache**, disinkronkan dari **Customer Master** melalui integrasi resmi (event atau scheduled pull). ECMP **tidak pernah** melakukan write-back ke Customer Master kecuali melalui integrasi resmi yang eksplisit diizinkan (selaras BR-CRM-01 dan BR-CRM-04).

**Business Context**
ECMP membutuhkan data pelanggan untuk konteks case, tetapi kepemilikan data pelanggan berada di luar ECMP.

**Reason**
CRM tetap responsif meski Customer Master lambat/down, dan batas tanggung jawab data menjadi jelas untuk audit kepatuhan.

**Alternatives Considered**
Option A (query langsung ke Customer Master) vs **Option B (local read-only cache)**; B dipilih.

**Impact**
Domain CRM · Integrasi · Data Dictionary · Audit kepatuhan data.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_002_ECMP_Not_System_Of_Record_v1.0.md` · `09 Integration Catalog/` · `06 Data Dictionary/` · `02 Business Rules/`

**Related Decisions**
DL-014 (pola projeksi non-otoritatif) · DL-040 · DL-051 (Customer Master tetap stub di Mode A)

**Supersedes**
—

**Notes**
Prinsip non-SoR ini kemudian menjadi dasar bagi larangan ECMP memodifikasi identitas enterprise (DL-040).

---

#### DL-032 — Stack Implementasi Backend

| Field | Value |
|---|---|
| **Decision ID** | DL-032 |
| **Title** | ADR-004 — Python/FastAPI + PostgreSQL + Alembic + OpenAPI 3 |
| **Status** | Approved / Accepted |

**Decision**
Untuk Sprint-01 dan fondasi awal: **Backend** Python 3.12+ dengan **FastAPI**; **Persistence** **PostgreSQL**; **Migrations** Alembic; **API Contract** OpenAPI 3 (sumber di `07 API Catalog/openapi`); **Events** contract-first via `08 Event Catalog/events/events.yaml` (teknologi broker follow-up).

**Business Context**
Fondasi implementasi memerlukan stack yang ditetapkan sebelum kode pertama.

**Reason**
Kontrak-first (OpenAPI + event schema) menjaga keterlacakan dari dokumen ke kode.

**Alternatives Considered**
Tercatat di ADR-004 §Options.

**Impact**
Backend · CI · Migrasi · API Catalog · Event Catalog.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_004_Implementation_Stack_Sprint01_v1.0.md` · `21 Technical Standards/` · `07 API Catalog/` · `08 Event Catalog/`

**Related Decisions**
DL-033 · DL-034 · DL-043 (Python 3.13 pada tree produksi) · DL-050

**Supersedes**
Menjawab sebagian **OQ-002** (stack backend dikunci; frontend tetap deferred).

**Notes**
DL-043 menyelaraskan versi Python CI dengan image produksi (3.13) — perubahan versi runtime, bukan perubahan stack.

---

#### DL-033 — Backend Layering

| Field | Value |
|---|---|
| **Decision ID** | DL-033 |
| **Title** | ADR-005 — minimal split presentation / application / domain-persistence |
| **Status** | Approved / Accepted |

**Decision**
Split minimal wajib untuk `implementation/backend`: `main.py` (Presentation — route FastAPI + error handler saja), `service.py` (Application — business action seperti `register_case`, `get_case`), dan lapisan persistence/domain terkait sesuai ADR-005. Scaffold 4-layer penuh tidak dibangun pada tahap ini.

**Business Context**
Slice awal membutuhkan struktur yang cukup untuk tumbuh tanpa over-engineering.

**Reason**
Memisahkan concern minimum yang benar-benar dibutuhkan, menunda struktur yang belum terbukti perlu.

**Alternatives Considered**
Tercatat di ADR-005 (termasuk deferral CQRS — lih. Notes).

**Impact**
Struktur kode backend · Review PR · Test.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_005_Backend_Layering_v1.0.md` · `22 Engineering Handbook/` · `21 Technical Standards/`

**Related Decisions**
DL-032 · DL-043 · DL-050

**Supersedes**
—

**Notes**
**OQ-003 (CQRS) Resolved: ditunda** — tidak relevan untuk slice 2-endpoint; revisit saat ada kebutuhan read-model nyata; deferral dicatat pada ADR-005.

---

#### DL-034 — API Versioning

| Field | Value |
|---|---|
| **Decision ID** | DL-034 |
| **Title** | ADR-006 — prefix `/v1`, semver kontrak, kebijakan deprecation |
| **Status** | Approved / Accepted |

**Decision**
1. Semua path API produk diprefix **`/v1`** (mis. `POST /v1/cases`); `/health` tetap tanpa versi.
2. **MAJOR** naik hanya untuk breaking change; field baru opsional = MINOR tanpa perubahan prefix.
3. **Deprecation:** versi lama hidup minimal 2 minor release setelah pengumuman; respons versi deprecated menyertakan header `Deprecation: true` + `Sunset: <date>`.
4. Penamaan file katalog `<service>.v<major>.yaml` di `07 API Catalog/openapi/`.
5. `info.version` = semver penuh kontrak.

**Business Context**
Kontrak API perlu aturan evolusi sebelum konsumen eksternal/modul lain bergantung padanya.

**Reason**
Memberi jaminan kompatibilitas yang dapat diprediksi kepada konsumen kontrak.

**Alternatives Considered**
Tercatat di ADR-006 §Options.

**Impact**
Semua kontrak API · Klien frontend · Katalog API.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_006_API_Versioning_v1.0.md` · `07 API Catalog/`

**Related Decisions**
DL-022 · DL-032 · DL-044

**Supersedes**
Konvensi penamaan `ECMP_API_...` pada README katalog.

**Notes**
Dua namespace HTTP produksi (`/api/v1/complaints` dan `/api/v1/cm`) hidup berdampingan di bawah DL-044, bukan pelanggaran ADR-006.

---

#### DL-035 — Deferral Message Broker + Transactional Outbox

| Field | Value |
|---|---|
| **Decision ID** | DL-035 |
| **Title** | ADR-009 (+ Addendum G2) — outbox sebagai transport resmi sementara |
| **Status** | Approved / Accepted; Addendum G2 **Accepted (Mode A)** — tidak mencabut deferral induk |

**Decision**
1. Pemilihan broker **DITUNDA secara eksplisit** — bukan open question, melainkan deferral yang diputuskan.
2. Sampai broker dipilih, **transactional outbox** adalah mekanisme resmi: event ditulis ke tabel `outbox` dalam transaksi yang sama dengan write bisnis; publisher in-process boleh menguras outbox di DEV.
3. **Trigger evaluasi broker** (mana yang lebih dulu): consumer lintas-service pertama dibangun (Notification/KPI), atau gate G2 dimulai. Kandidat saat itu: RabbitMQ, Kafka, cloud pub/sub.
4. **Dilarang** membangun framework publisher generik (retry backoff, DLQ, abstraksi multi-broker) sebelum broker nyata ada.
5. **Addendum G2:** deferral broker fisik dilanjutkan untuk Mode A SIT/UAT wave-1; in-process outbox drain **diperluas** sebagai transport Mode A; re-evaluasi wajib berikutnya saat proses terpisah harus mengonsumsi outbox (FR-030 event clock) atau deploy multi-instance memerlukan shared relay.

**Business Context**
ADR-001 menetapkan pola event-driven tetapi teknologi broker belum dapat dipilih tanpa consumer nyata.

**Reason**
Menghindari infrastruktur dan abstraksi yang dibangun sebelum kebutuhannya terbukti, tanpa kehilangan jaminan atomicity event.

**Alternatives Considered**
Memilih broker sekarang (RabbitMQ/Kafka/cloud pub-sub) vs deferral dengan outbox; deferral dipilih.

**Impact**
Event delivery · Infrastruktur · Roadmap KPI/Notification · Gate G2.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_009_Message_Broker_Deferral_v1.0.md` · `…/ECMP_ADR_009_Addendum_G2_InProcess_Extension_v1.0.md` · `08 Event Catalog/` · `04 Solution Architecture/`

**Related Decisions**
DL-030 · DL-051 · DL-021

**Supersedes**
Status "open question" pemilihan broker.

**Notes**
Larangan framework publisher generik sejalan dengan larangan perluasan ruang lingkup pada DL-046.

---

#### DL-036 — Baseline Platform Deployment

| Field | Value |
|---|---|
| **Decision ID** | DL-036 |
| **Title** | ADR-010 — DEV/CI diformalkan, SIT/UAT ditetapkan, PROD ditunda |
| **Status** | Approved / Accepted (Architecture Board, 2026-07-21 — gap remediation) |

**Decision**
1. **DEV** — formalisasi status quo: PostgreSQL 16 via compose; aplikasi jalan via `uvicorn` di host; fallback SQLite hanya untuk bootstrap lokal, PostgreSQL tetap wasit paritas.
2. **CI** — formalisasi status quo: GitHub Actions dengan service container PostgreSQL 16; urutan ruff → validate OpenAPI → `alembic upgrade head` → pytest sebagai gate wajib PR.
3. **SIT/UAT** — baseline diputuskan: container via Docker Compose pada **satu VM managed** + deploy via GitHub Actions; **hanya boleh diaktifkan setelah fase target auth ADR-007 (JWT/OIDC) aktif** (dev-token dilarang di shared environment). Aktivasi ini memicu deliverable Dockerfile, registry, dan tagging standard.
4. **PROD** — **ditunda eksplisit**; trigger evaluasi: UAT pertama sukses, atau data volume/beban nyata, atau keputusan budget/procurement sponsor. Kandidat: managed container service vs Kubernetes — tidak dipilih sekarang.

**Business Context**
Deployment sebelumnya berjalan tanpa baseline tertulis, sementara UAT membutuhkan lingkungan bersama.

**Reason**
Memformalkan yang sudah nyata, memutuskan yang dibutuhkan UAT, dan menunda secara eksplisit yang belum punya data.

**Alternatives Considered**
Memilih platform produksi sekarang (ditunda); mengaktifkan SIT/UAT tanpa auth target (ditolak).

**Impact**
CI/CD · Lingkungan · Keamanan lingkungan bersama · Rilis.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_010_Deployment_Platform_Baseline_v1.0.md` · `14 Deployment Standards/` · `15 Operations Runbook/` · `deploy/`

**Related Decisions**
DL-050 · DL-054 · DL-055 · DL-058 · DL-059

**Supersedes**
—

**Notes**
Kaitan "shared environment ⇒ wajib auth target" adalah alasan langsung gerbang konfigurasi fail-fast pada DL-055.

---

#### DL-037 — Deferral Frontend Produk

| Field | Value |
|---|---|
| **Decision ID** | DL-037 |
| **Title** | ADR-011 — ECMP API-first sampai trigger terpenuhi |
| **Status** | Approved / Accepted (Architecture Board, 2026-07-21 — gap remediation) |

**Decision**
1. **ECMP adalah API-first** — tidak ada frontend produk dibangun sampai trigger tersentuh.
2. **Trigger memulai frontend** (semua terpenuhi): slice create/get stabil dan gate **G1** lulus; kebutuhan UI **divalidasi Business Owner**; kebutuhan per persona **P-01…P-05** di UX-001 menjadi dasar scope layar.
3. **Saat trigger tersentuh:** buat **ADR stack frontend baru** dan tulis **screen spec** di `12 UI UX Spec` sebelum kode UI pertama.

**Business Context**
Sprint-01 berfokus pada slice API; membangun UI lebih dulu berisiko membuang kerja.

**Reason**
Menahan investasi UI sampai kontrak lifecycle stabil dan kebutuhan tervalidasi bisnis.

**Alternatives Considered**
Membangun frontend paralel sejak awal (ditolak).

**Impact**
Roadmap frontend · UX Spec · Otorisasi ADR-013.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_011_Frontend_Deferral_v1.0.md` · `12 UI UX Spec/` · `27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md`

**Related Decisions**
DL-038 · DL-045 · DL-050 · DL-001

**Supersedes**
—

**Notes**
Trigger ini terpenuhi dan menghasilkan ADR-013 (DL-038) serta screen spec `UX-SCR-001`.

---

#### DL-038 — Frontend Technology Stack (ADR-013)

| Field | Value |
|---|---|
| **Decision ID** | DL-038 |
| **Title** | ADR-013 — React 18 + TypeScript SPA, Vite, React Router, TanStack Query |
| **Status** | Approved / Accepted (keputusan CTO, Sprint-04, 2026-07-22); **tetap aktif** (PROGRAM-ADR-002 BR-007) |

**Decision**
**Framework:** React 18+ dengan TypeScript sebagai SPA client-rendered. **Build tool:** Vite — tanpa SSR/meta-framework. **Routing:** React Router (`/cases/:caseId` per `UX-SCR-001` §11). **Server-state:** TanStack Query untuk pemanggilan `GET`/`POST`. Target tree: `implementation/frontend`.

**Business Context**
Trigger ADR-011 terpenuhi sehingga stack frontend harus ditetapkan lewat ADR sebelum kode UI pertama.

**Reason**
SSR tidak dibutuhkan untuk internal tool di balik login; kompleksitasnya tidak diminta oleh screen spec.

**Alternatives Considered**
SSR/meta-framework (mis. Next.js) — ditolak pada saat keputusan diambil.

**Impact**
Frontend · Technical Standards · CI frontend.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_013_Frontend_Technology_Stack_v1.0.md` · `12 UI UX Spec/ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md` · `21 Technical Standards/` · `docs/frontend/OPEN_DECISIONS.md`

**Related Decisions**
DL-037 · DL-043 · DL-045 · DL-048 (BR-007)

**Supersedes**
Memenuhi follow-up ADR-004 untuk stack frontend.

**Notes**
**Konflik terdaftar:** tree produksi (`frontend/`, DL-043) memakai Next.js 15 + React 19 + Tailwind + Axios. Board menyatakan ADR-013 **tetap aktif** dan **tidak boleh** disupersede lewat dokumentasi frontend; perubahan stack memerlukan ADR terpisah (OD-FE-001). Lih. Bagian 6.

---

#### DL-039 — ECMP sebagai Enterprise Business Module

| Field | Value |
|---|---|
| **Decision ID** | DL-039 |
| **Title** | ADR-014 v1.4 — batas modul, kepemilikan AuthN/AuthZ |
| **Status** | **Accepted with Conditions** (PROGRAM-BOARD-004 BR-009; C-1, C-3, C-7); posture: *Accepted Architecture — Implementation Deferred* |

**Decision**
Kepemilikan **Authentication** dialihkan ke Enterprise Platform di bawah **Mode B**; ECMP **tidak lagi** bertindak sebagai Identity Provider di Mode B dan beroperasi sebagai **Business Module**. Authentication dan Authorization tetap tanggung jawab terpisah. Ringkasan: Enterprise Platform memiliki Authentication + Enterprise Identity; **ECMP memiliki Complaint Management**; **Complaint Authorization** dan **Complaint Roles mapping** tetap di dalam ECMP **setelah** Enterprise Entitlement Gate; **Role-Permission Matrix SoT = Core Platform (ADR-008)** — Enterprise Platform tidak memilikinya; klaim identitas wajib didefinisikan **ADR-015**, bukan di ADR ini. Asumsi tercatat: satu instance ECMP diperlakukan **single-tenant** terhadap referensi hierarki organisasi (multi-tenant packaging **out of scope** — non-decision eksplisit); Mode A tetap tersedia sebagai hedge delivery, bukan IdP fallback Mode B; **ADR-013 orthogonal dan tetap aktif**.

**Business Context**
Roadmap enterprise berubah: ECMP menjadi satu Business Module di dalam Enterprise Platform yang menyediakan Portal, Authentication, SSO, User Directory, Organization Structure, Navigation, Enterprise Global Notification, dan Session Management.

**Reason**
Bila ECMP terus memiliki autentikasi enterprise, muncul halaman login ganda, database user ganda, password management ganda, proses reset terpisah, logout tidak konsisten, audit identitas terfragmentasi, dan integrasi enterprise menjadi sulit.

**Alternatives Considered**
Tercatat di ADR-014 §Options Considered (mempertahankan identitas ECMP vs menyerahkan AuthN ke Enterprise Platform); opsi Business Module dipilih.

**Impact**
Authentication · Authorization · User Model · Organization · Notification · Deployment Mode · Seluruh roadmap identitas.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4.md` · `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md` · `10 Security and Access Standards/` (SEC-PWD-001, SEC-AUTH-001) · `04 Solution Architecture/`

**Related Decisions**
DL-013 · DL-040 · DL-041 · DL-042 · DL-048 · DL-055 · DL-056 · DL-057

**Supersedes**
Desain standalone ECMP sebagai pemilik autentikasi enterprise (untuk Mode B).

**Notes**
Accept **tidak** membuka Mode B (C-7). Larangan local auth di Mode B dicatat terpisah sebagai DL-057 karena berkategori Security.

---

#### DL-040 — Enterprise Identity Contract

| Field | Value |
|---|---|
| **Decision ID** | DL-040 |
| **Title** | ADR-015 v1.3 — kontrak identitas kanonik (Bilateral Contract) |
| **Status** | **Accepted with Conditions** (PROGRAM-BOARD-004 BR-010; C-1, C-3, C-7); di bawah **C-3** dinyatakan **Bilateral Contract**; Identity Contract Version **1.0** |

**Decision**
ECMP mengadopsi **Enterprise Identity Contract** kanonik antara Enterprise Platform dan ECMP: **Enterprise Platform memiliki identitas**; **ECMP mengonsumsi identitas**; **ECMP tidak boleh pernah memodifikasi identitas enterprise**. Kontrak mendefinisikan claim wajib, claim opsional, semantik claim, versioning, ekspektasi lifecycle, aturan fail-closed, aturan kompatibilitas, dan trust boundary. **Claim tidak dikenal diabaikan** kecuali ditandai wajib; **claim wajib yang hilang menyebabkan penolakan akses**; kontrak **diversi independen** dari implementasi. ADR-015 adalah **Source of Truth** klaim; ADR-014 menunjuk ke sini dan tidak memelihara daftar claim tandingan.

**Business Context**
Batas Mode B (ADR-014) perlu tetapi belum cukup: tanpa kontrak identitas berversi, tiap tim dapat mengasumsikan atribut, semantik kunci, dan perilaku kegagalan yang berbeda.

**Reason**
Mencegah ECMP memperlakukan atribut mutable/non-unik (mis. email) sebagai kunci identitas, mencegah penanganan claim hilang yang tidak deterministik, dan memisahkan evolusi identitas dari rilis ECMP.

**Alternatives Considered**
Tercatat di ADR-015 (kontrak implisit vs kontrak berversi eksplisit); kontrak berversi dipilih.

**Impact**
Identity Adapter · Authorization · Integrasi Mode B · Data profil lokal · Fail-closed posture.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_015_Enterprise_Identity_Contract_v1.3.md` · `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_…_v1.0.md` · `10 Security and Access Standards/` · `docs/frontend/OPEN_DECISIONS.md` (OD-FE-002)

**Related Decisions**
DL-013 · DL-014 · DL-039 · DL-041 · DL-042 · DL-048 · DL-049

**Supersedes**
Menjadi SoT claim, menggantikan daftar claim yang tersebar (termasuk model era ADR-012 sebagai wire fields).

**Notes**
**Peringatan kontrak identitas:** repositori tidak memuat artefak dari aplikasi enterprise nyata; seluruh referensi IdP menunjuk realm lokal yang di-provision ECMP sendiri. Kontrak ini **belum diverifikasi bilateral** ke pemilik platform — lih. Bagian 6.

---

#### DL-041 — Enterprise Protocol & Binding

| Field | Value |
|---|---|
| **Decision ID** | DL-041 |
| **Title** | ADR-016 v1.0 — bagaimana identitas disampaikan dan divalidasi |
| **Status** | **Accepted with Conditions** (PROGRAM-BOARD-006 BR-011; C-B6-1…C-B6-7) |

**Decision**
1. **Keluarga protokol yang didukung** dideklarasikan sebagai standards family, **tanpa** memilih produk IdP atau implementasi runtime.
2. Sebuah **Binding** memetakan presentasi wire dari keluarga yang diizinkan ke **claim kanonik ADR-015**.
3. **Trust** ditegakkan lewat validasi kriptografis presentasi ditambah pemeriksaan **issuer** dan **audience** yang wajib.
4. Validasi dan penerimaan claim bersifat **fail-closed**.
5. **Kepemilikan binding** berada di **Identity Adapter** ECMP untuk konsumsi/pemetaan; kepemilikan **Issuer** berada di **Enterprise Platform**.
6. ADR ini **tidak** membuka Mode B, Batch-2, Enterprise customer, OpenAPI `securitySchemes`, coding JWT, maupun implementasi OD-FE-002.

**Business Context**
ADR-014/015 secara eksplisit menunda pemilihan protokol, format kredensial, transport, validasi `aud`/`iss`, key management, dan pemetaan nama wire.

**Reason**
Tanpa ADR ini, implementer dapat mengarang asumsi conveyance yang tidak kompatibel, isolasi audience/issuer bisa hilang ("satu token membuka semuanya"), dan mode kegagalan bisa fail-open.

**Alternatives Considered**
Tercatat di ADR-016 §4 Options Considered (memilih satu protokol/produk vs mendeklarasikan keluarga protokol + binding); pendekatan binding dipilih.

**Impact**
Identity Adapter · Trust model · Validasi token/assertion · Key management · Versioning protokol.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_016_Enterprise_Protocol_Binding_v1.0.md` · `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_…_v1.0.md` · `…/ECMP_PROGRAM_AUDIT_K5_FailClosed_Subordination_v1.0.md` · `10 Security and Access Standards/`

**Related Decisions**
DL-039 · DL-040 · DL-042 · DL-049 · DL-055

**Supersedes**
Menutup butir tertunda ADR-014/015 tentang protokol & binding (F-5 PROGRAM-BOARD-004).

**Notes**
Pembuatan ADR ini **tidak** membuka Mode B (C-7 tetap berlaku).

---

#### DL-042 — Enterprise Entitlement Architecture

| Field | Value |
|---|---|
| **Decision ID** | DL-042 |
| **Title** | ADR-017 v1.0 — gerbang masuk modul (Entitlement Gate) |
| **Status** | **Accepted with Conditions** (PROGRAM-BOARD-006 BR-012; C-B6-1…C-B6-7) |

**Decision**
1. **Tujuan:** Entitlement adalah *grant* penerimaan masuk modul enterprise untuk ECMP Complaint.
2. **Kepemilikan:** Enterprise Platform memiliki entitlement sebagai kebenaran enterprise; ECMP mengonsumsi dan mengevaluasinya di Entitlement Gate; ECMP **tidak boleh** mengarang entitlement sebagai SoR enterprise.
3. **Urutan:** Trust (ADR-016) → Identity Contract (ADR-015) → **Entitlement Gate** → Complaint Roles mapping (ADR-014) → Permissions (ADR-008).
4. **Kegagalan:** entitlement hilang, tidak valid, dicabut, atau tidak berlaku → **deny (fail closed)**.
5. **Format representasi** (nama claim, field token, atribut direktori, pemanggilan API) **ditunda**, tetapi wajib mematuhi arsitektur ini.
6. ADR ini **tidak** membuka implementasi Mode B.

**Business Context**
ADR-014 menetapkan bahwa akses ke ECMP memerlukan entitlement enterprise eksplisit dan bahwa autentikasi enterprise saja tidak pernah memberi akses ECMP — tetapi representasi dan penerbitannya ditunda.

**Reason**
Tanpa arsitektur entitlement, tim dapat meleburkan entitlement ke dalam claim identitas, role OIDC, atau permission ECMP, dan gerbang dapat dianggap opsional.

**Alternatives Considered**
Tercatat di ADR-017 §4 Options Considered.

**Impact**
Identity Adapter · Authorization · Complaint Roles mapping · Fail-closed posture.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_017_Enterprise_Entitlement_Architecture_v1.0.md` · `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_…_v1.0.md` · `10 Security and Access Standards/`

**Related Decisions**
DL-039 · DL-040 · DL-041 · DL-049 · DL-056

**Supersedes**
Menutup butir tertunda ADR-014 tentang representasi entitlement (pada tingkat arsitektur, bukan format).

**Notes**
Urutan lima langkah pada butir 3 adalah rujukan penting bagi BC-000 saat menjelaskan batas otorisasi.

---

#### DL-043 — Canonical Trees Engineering Foundation

| Field | Value |
|---|---|
| **Decision ID** | DL-043 |
| **Title** | DEC-019 — `backend/` dan `frontend/` adalah tree produksi kanonik |
| **Status** | Approved (Engineering Manager via EPIC-001, 2026-07-25) |

**Decision**

| Tree | Klasifikasi | Pemilik CI |
|---|---|---|
| `backend/` | **Production backend (kanonik)** | `backend-ci.yml` (M1+) |
| `frontend/` | **Production frontend (kanonik)** | `frontend-ci.yml` (M3+) |
| `implementation/backend/` | **Legacy track** (Sprint-01 case-service) | di luar cakupan Backend CI |
| `implementation/frontend/` | **Legacy track** (Vite sprint UI) | di luar cakupan Frontend CI produk |

**Runtime Python** CI diselaraskan dengan image produksi: **Python 3.13**. **Formatter/linter** backend: **Ruff** (pinned) dengan konfigurasi di `backend/pyproject.toml`; Black tidak diperkenalkan.

**Business Context**
Repositori memuat dua tree aplikasi paralel; Go-Live v1.0.0 dikirim dari root `backend/` + `frontend/`, sementara Backend CI historisnya menyasar `implementation/backend/` sehingga kode Complaint/Queue produksi tidak pernah diuji CI.

**Reason**
Menghentikan rasa aman palsu dari CI hijau terhadap tree non-produksi, sambil menyimpan legacy track untuk sejarah tanpa mengklaim cakupan CI produksi.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
CI/CD · Rilis · Cakupan tes · Lokasi kode produksi.

**Affected Documents**
`27 Project Decisions/DEC-019_Engineering_Foundation_Canonical_Trees_EPIC001_v1.0.md` · `docs/releases/v1.0.0.md` · `.github/workflows/` · `backend/pyproject.toml`

**Related Decisions**
DL-032 · DL-038 (konflik stack) · DL-044 · DL-045

**Supersedes**
Asumsi bahwa `implementation/backend` adalah tree CI produksi.

**Notes**
Konsekuensi DEC-019 ini yang memunculkan konflik ADR-013 (Vite) vs Next.js produksi — lih. DL-038 dan Bagian 6.

---

#### DL-044 — Complaint Implementation SoT & Namespace Remapping

| Field | Value |
|---|---|
| **Decision ID** | DL-044 |
| **Title** | DEC-020 — dual SoT terkendali, tanpa tanggal pensiun tunggal |
| **Status** | 🟢 Approved (Architecture Board, 2026-07-30); menutup **OQ-CM-B1-001** |

**Decision**
**Tidak ada satu "tanggal penggantian" yang mempensiunkan Sprint delivery SoT sekarang.** Model Aggregate BR-CM-CAT-001 / FRD-CM-001 **tidak** menggantikan Sprint delivery SoT secara menyeluruh untuk semua implementasi complaint. Kebijakan yang berlaku: **tidak ada forced merge** antar implementasi; **controlled coexistence**; **cutover hanya lewat Decision**; gate governance tetap aktif (Mode B, Batch-2, real-customer, EX-A…H). Tiga implementasi complaint dan dua namespace HTTP hidup berdampingan secara sengaja: Legacy ECMF (`/api/v1/complaints`), Complaint CA BC (`complaint_cases*`, router foundation **unmounted**), dan CM Batch 1 Aggregate (`/api/v1/cm`). DEC ini **tidak** meng-Accept ADR-014/015, **tidak** membuka Mode B, Batch-2, atau produksi real-customer.

**Business Context**
FRD-CM-001 v1.1 LOCKED sebagai Batch 1 Aggregate SoT tetapi eksplisit tidak menaikkan BR-CM-CAT-001 (Draft) maupun menimpa Sprint delivery ID sampai remapping diputuskan.

**Reason**
Memaksa penggabungan implementasi tanpa keputusan formal berisiko menghancurkan kontrak yang sedang berjalan; koeksistensi terkendali menjaga keduanya tertelusur.

**Alternatives Considered**
Penggantian menyeluruh pada satu tanggal (ditolak); merge paksa (ditolak); **dual SoT + controlled coexistence** (dipilih).

**Impact**
Seluruh implementasi complaint · Namespace API · Traceability · Strategi rilis · Retirement plan.

**Affected Documents**
`27 Project Decisions/DEC-020_Complaint_Implementation_SoT_Namespace_Remapping_v1.0.md` · `03 Functional Requirements/ECMP_FRD_Complaint_Management_Batch1_v1.1.md` · `02 Business Rules/ECMP_Business_Rules_Complaint_Management_Module_v1.0.md` · `18 Architecture Governance/ECMP_PROGRAM_IMPLEMENTATION_001_Implementation_Authorization_Posture_v1.0.md`

**Related Decisions**
DL-023 · DL-027 · DL-034 · DL-043 · DL-051 · DL-052

**Supersedes**
—

**Notes**
**Retirement DEC** terpisah tetap diperlukan untuk mengakhiri dual tree — belum ada. Lih. Bagian 6. Perhatikan juga tabrakan ID DEC-020 (DL-053).

---

#### DL-045 — Baseline Arsitektur, Standar, dan Kebijakan CI Frontend

| Field | Value |
|---|---|
| **Decision ID** | DL-045 |
| **Title** | FE-ARCH-001 / FE-STD-001 BASELINE + FE-CI-POL-001 Accepted with Conditions |
| **Status** | FE-ARCH-001 **BASELINE** · FE-STD-001 **BASELINE** · FE-CI-POL-001 **Accepted with Conditions**; OD-FE-003/008/009/010 **CLOSED** |

**Decision**
`FRONTEND_ARCHITECTURE_v1.2.md` (FE-ARCH-001) dan `FRONTEND_DEVELOPMENT_STANDARDS_v1.0.md` (FE-STD-001) berstatus **BASELINE**; `FRONTEND_CI_QUALITY_POLICY_v1.0.md` (FE-CI-POL-001) **Accepted with Conditions** dengan ambang Phase B/C diterima dan **coverage hard-fail Phase C aktif**. Koreksi SoT Role/Permission diselesaikan di FE-ARCH §2.2. **BASELINE frontend tidak boleh diperlakukan sebagai bukti bahwa Mode B / identitas sudah Accepted untuk delivery** — Mode B tetap CLOSED (C-7), dan **ADR-013 tidak boleh disupersede** lewat dokumentasi frontend (BR-007).

**Business Context**
Program frontend memerlukan baseline arsitektur, standar pengembangan, dan gate kualitas CI yang disepakati.

**Reason**
Memberi acuan kerja frontend yang mengikat sekaligus mencegah dokumen frontend dipakai untuk membuka gate governance yang bukan wewenangnya.

**Alternatives Considered**
Tercatat pada dokumen kebijakan CI (ambang Phase B/C).

**Impact**
Frontend · CI · Quality gate · Technical Standards.

**Affected Documents**
`docs/frontend/FRONTEND_ARCHITECTURE_v1.2.md` · `docs/frontend/FRONTEND_DEVELOPMENT_STANDARDS_v1.0.md` · `docs/frontend/FRONTEND_CI_QUALITY_POLICY_v1.0.md` · `docs/frontend/FRONTEND_CI_QUALITY_POLICY_COUNTERSIGN_v1.0.md` · `docs/frontend/OPEN_DECISIONS.md` · `docs/UI_BASELINE.md`

**Related Decisions**
DL-029 · DL-038 · DL-043 · DL-048

**Supersedes**
Status OPEN OD-FE-003, OD-FE-008, OD-FE-009, OD-FE-010.

**Notes**
OD-FE-001, 002, 004, 005, 006, 007 **tetap OPEN** — lih. Bagian 6.

---

### 3.G Governance

---

#### DL-046 — Complaint Management Module Constitution

| Field | Value |
|---|---|
| **Decision ID** | DL-046 |
| **Title** | ECMP-CONSTITUTION-001 v1.1 — North Star & filter delivery |
| **Status** | 🔒 **LOCKED** (2026-07-31) — subordinat terhadap Board Resolution → ADR → EA |

**Decision**
**Misi tunggal:** *menyelesaikan Complaint Management Module dengan arsitektur yang benar, sehingga ketika pintu Enterprise Application terbuka, yang berubah hanyalah mekanisme integrasinya — bukan domain bisnisnya.* Produk yang dibangun adalah **Complaint Management Module**, **bukan** Enterprise Platform / Enterprise OS / Enterprise Engineering Framework / Generic SDK / Marketplace / Framework Multi Module / Enterprise Portal / Enterprise Runtime / Enterprise Module Registry. **Hierarki konflik:** Board Resolution → ADR → EA Documents → ECMP-CONSTITUTION-001 → ECMP MASTER PROMPT. **Mode A dan Mode B bukan dua arsitektur** — Target Architecture selalu SATU; Mode A = Authorized Delivery Strategy, Mode B = Enterprise Integration Strategy. Selama Mode B **CLOSED**, dilarang implementasi produksi untuk Identity Adapter Enterprise (runtime), Enterprise SSO/Embed UI/Portal, `securitySchemes` OpenAPI Enterprise, Organization Sync/Entitlement engine sebagai produk Mode B, dan integrasi Enterprise Notification produksi — yang boleh hanya menjelaskan status, mendokumentasikan kontrak, mendesain interface/kontrak, dan migration plan. **Stability Guard:** jangan redesign bagian yang accepted/stable/green kecuali karena regression bug, security issue, architecture defect, business requirement baru, atau keputusan Board. **Decision Filter** empat pertanyaan sebelum rekomendasi/desain/implementasi. **Completion Criteria:** modul COMPLETE bila Domain, Business Rule, UI (Mode A), API, Test, Architecture boundary, dan Observability selesai — **Enterprise Integration bukan syarat COMPLETE**.

**Business Context**
Sepanjang audit Juli 2026 pembahasan melebar dari "selesaikan modul komplain" menjadi desain platform untuk banyak modul masa depan; pelebaran itu dihentikan dan konstitusi ini ditetapkan.

**Reason**
Menjaga fokus delivery dan melindungi Domain Complaint dari perluasan ruang lingkup dan redesign yang tidak dibutuhkan bisnis.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Seluruh keputusan teknis, arsitektur, implementasi, review, dan dokumentasi ECMP.

**Affected Documents**
`18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md` · `docs/governance/ECMP-CONSTITUTION-001.md` · `18 Architecture Governance/ECMP_MASTER_PROMPT_001_…_v1.1.md` · `CLAUDE.md` · `.cursor/rules/`

**Related Decisions**
DL-047 · DL-048 · DL-049 · DL-044 · DL-039

**Supersedes**
—

**Notes**
Konstitusi ini **tidak** membuka Mode B dan **tidak** mengubah keputusan Board; ia adalah filter operasional, bukan Target Architecture baru. Menganggap Accept ADR-016/017/018 sebagai Mode B unlocked dinyatakan **Forbidden Behavior**.

---

#### DL-047 — Kategori Governance Delivery

| Field | Value |
|---|---|
| **Decision ID** | DL-047 |
| **Title** | GOV-001 — kategori A/B/C, DoR, dan DoD |
| **Status** | 🔒 **LOCKED** (2026-08-03) |

**Decision**
Setiap diskusi/delivery baru harus masuk **satu** kategori: **A — Constitution** (aturan permanen: Golden Rules, boundary, ADR, Mode B; sangat jarang), **B — Specification** (bagaimana sesuatu harus bekerja: CWX-M1…M4, Queue Spec; paling sering), **C — Implementation** (baru setelah Spec + DoR). Tanpa Board/ADR, **dilarang** mengusulkan secara spontan: ECOS baru, Workspace baru, Engine baru, Layer platform baru, Capability OOS, redesign menyeluruh. **Workflow:** Board/ADR → CWX Spec → Design Review → Implementation → Verification → Architecture Review. **DoR:** tujuan jelas · tidak bentrok Board/ADR/CONSTITUTION · UX Contract · AC · Out of Scope jelas. **DoD:** AC + Golden Rules + CWX-R + Dual-SoT intact + no Mode B + no SoR baru + Functional/Cognitive/Consistency.

**Business Context**
Diskusi delivery kerap bercampur antara aturan permanen, spesifikasi, dan implementasi sehingga keputusan sulit dilacak.

**Reason**
Memaksa setiap pekerjaan memilih kategori membuat jalur persetujuan dan bukti penyelesaiannya jelas.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Proses delivery · Backlog · Review · Definition of Ready/Done.

**Affected Documents**
`ECMP_GOV_001_Delivery_Governance_Categories_v1.0.md` · `docs/governance/ECMP-GOV-001.md` · `docs/governance/decision-tree.md` · `docs/governance/ownership-matrix.md`

**Related Decisions**
DL-027 · DL-028 · DL-046

**Supersedes**
—

**Notes**
GOV-001 adalah pintu masuk formal untuk menilai apakah sebuah usulan boleh dikerjakan tanpa Board/ADR baru.

---

#### DL-048 — Board Resolution PROGRAM-BOARD-004

| Field | Value |
|---|---|
| **Decision ID** | DL-048 |
| **Title** | Accept with Conditions ADR-014 v1.4 + ADR-015 v1.3 (BR-009 / BR-010) |
| **Status** | Approved — Architecture Board Resolution (2026-07-30) |

**Decision**
Architecture Board **ACCEPTS WITH CONDITIONS** ADR-014 v1.4 dan ADR-015 v1.3 sebagai paket terkoordinasi. Kondisi wajib: **C-1** (regenerasi canonical ADR Index + higiene supersession, termasuk mencatat BR-005/BR-006 sebagai disposisi historis), **C-3** (ADR-015 dinyatakan **Bilateral Contract**), **C-7** (**Mode B, Batch-2, dan Enterprise customer tetap CLOSED**). Acceptance mencatat kepemilikan arsitektur dan batas kontrak — **tidak** mengotorisasi implementasi Mode B, delivery Batch-2, atau produksi enterprise customer. **ADR-013 tetap aktif** (BR-007) dan **tidak** disupersede oleh paket ini; BASELINE FE tidak boleh diperlakukan sebagai bukti Mode B/identitas Accepted untuk delivery.

**Business Context**
ADR-014/015 sebelumnya berstatus "Revised — Pending Board Review" setelah disposisi Needs Revision (BR-005/BR-006).

**Reason**
Menerima arsitektur yang benar sambil menahan implementasi sampai prasyarat operasional dan kontrak nyata terpenuhi.

**Alternatives Considered**
Accept tanpa syarat · Needs Revision lanjutan · **Accept with Conditions** (dipilih).

**Impact**
Status ADR-014/015 · Semua pekerjaan identitas Mode B · Index ADR · Komunikasi otorisasi implementasi.

**Affected Documents**
`18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md` · `05 Architecture Decision Records/ADR_INDEX.generated.md` · `docs/architecture/adr-index.md` · `18 Architecture Governance/ECMP_PROGRAM_ADR_002_Board_Resolutions_v1.0.md`

**Related Decisions**
DL-039 · DL-040 · DL-049 · DL-046

**Supersedes**
Disposisi aktif BR-005 / BR-006 (menjadi historis).

**Notes**
C-7 adalah gerbang yang paling sering dirujuk seluruh repositori; setiap ADR/DEC berikutnya menegaskan tidak membukanya.

---

#### DL-049 — Board Resolution PROGRAM-BOARD-006

| Field | Value |
|---|---|
| **Decision ID** | DL-049 |
| **Title** | Accept with Conditions ADR-016 / ADR-017 / ADR-018 (BR-011 / BR-012 / BR-013) |
| **Status** | Approved — Architecture Board Resolution (2026-07-30) |

**Decision**
Architecture Board **ACCEPTS WITH CONDITIONS** ADR-016 v1.0, ADR-017 v1.0, dan ADR-018 v1.0 sebagai paket terkoordinasi. Kondisi wajib **C-B6-1…C-B6-7**: **C-B6-1** menegaskan ulang C-7 (Mode B, Batch-2, Enterprise customer tetap **CLOSED**); **C-B6-2** standar subordinasi fail-closed (K-5 / ADR-016 §9.3); **C-B6-3** **gap model organisasi adalah prasyarat unlock Mode B** (K-7); **C-B6-4** kewajiban Bilateral Contract diperluas (menegaskan C-3); **C-B6-5** urutan otorisasi coding Mode B; **C-B6-6** relasi ADR-007/ADR-012 **tetap Pending**; **C-B6-7** higiene canonical ADR Index. Board **tidak** mengesampingkan prasyarat gap organisasi lewat Accept saja, dan **tidak** melonggarkan fail-closed AuthN/AuthZ lewat subordinate profiles. Unlock Mode B di masa depan memerlukan Resolution terpisah (prasyarat gap organisasi + kesiapan operasional + unlock eksplisit Board).

**Business Context**
ADR-016/017/018 disiapkan untuk menutup butir yang ditunda ADR-014/015 pada ranah protokol, entitlement, dan organisasi.

**Reason**
Melengkapi desain Mode B tanpa memberi kesan bahwa desain yang lengkap sama dengan izin implementasi.

**Alternatives Considered**
Accept tanpa syarat · menunda Accept · **Accept with Conditions** (dipilih).

**Impact**
Status ADR-016/017/018 · Prasyarat unlock Mode B · Standar fail-closed · Index ADR.

**Affected Documents**
`18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md` · `…/ECMP_PROGRAM_BOARD_005_Architecture_Board_Review_v1.0.md` · `…/ECMP_PROGRAM_AUDIT_K5_FailClosed_Subordination_v1.0.md` · `…/ECMP_PROGRAM_MODE_B_ORG_GAP_PREREQUISITE_v1.0.md` · `05 Architecture Decision Records/ADR_INDEX.generated.md`

**Related Decisions**
DL-041 · DL-042 · DL-014 · DL-048 · DL-054 · DL-055

**Supersedes**
Disposisi "Proposed / Ready for Resolution" pada ADR-016/017/018.

**Notes**
**C-B6-6** menahan relasi ADR-007 vs ADR-012 sebagai **Pending** — ini pertanyaan terbuka resmi, lih. Bagian 6.

---

#### DL-050 — Otorisasi Build Sprint-01 vs Gate G0

| Field | Value |
|---|---|
| **Decision ID** | DL-050 |
| **Title** | DEC-002 — GO = slice create/get + platform floor G0 |
| **Status** | Approved / Accepted (Engineering Manager, 2026-07-21) |

**Decision**
1. **Sprint-01 GO** = otorisasi untuk bootstrap backend, slice create/get (FR-001/FR-002), **dan seluruh deliverable G0** (PostgreSQL + Alembic rev0 `cases`/`audit_log`/`outbox`, docker-compose, backend CI hijau, error envelope OpenAPI, Role matrix minimal, write-audit pada create).
2. **Build-1** (assign, status transition, SLA, notification, dashboard) hanya boleh dimulai setelah **G0 exit criteria** terpenuhi dan ditandatangani Tech Lead + Solution Architect.
3. **Non-goals Sprint-0/G0** (dilarang dibangun): assign/status transition, Notification delivery, Schedule Slot/Appointment/Work Order, Branch/HO escalation, frontend produk, idempotency key, audit-on-read, pemilihan broker, integrasi SSO/IdP, framework audit generik, scaffold 4-layer penuh.

**Business Context**
Sprint-01 menyatakan "APPROVED — GO for development" sementara roadmap kesiapan implementasi mensyaratkan gate G0 lebih dulu — dua sinyal otorisasi yang bertentangan.

**Reason**
Menutup celah "GO" dipakai untuk mengkode fitur di atas stub in-memory, tanpa memblokir pekerjaan fondasi yang justru diwajibkan ADR-004.

**Alternatives Considered**
**A** GO tanpa syarat · **B** GO = slice + G0 (dipilih) · **C** tahan semua coding sampai seluruh EKR Approved.

**Impact**
Urutan delivery · CI sebagai gate wajib PR · Ruang lingkup Sprint-01 · Audit.

**Affected Documents**
`27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md` · `ai/sprint/Sprint-01.md` · `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md` · `.github/workflows/backend-ci.yml`

**Related Decisions**
DL-002 · DL-032 · DL-037 · DL-063 · DL-051

**Supersedes**
Interpretasi "GO tanpa syarat" pada Sprint-01.

**Notes**
Non-goal "audit-on-read" dan "idempotency key" tetap berlaku sampai keputusan lain; lih. DL-063.

---

#### DL-051 — G2 Mini-Gate Mode A

| Field | Value |
|---|---|
| **Decision ID** | DL-051 |
| **Title** | DEC-021 (G2) — keluar gate G2 untuk Mode A lab |
| **Status** | Approved (Lab Architecture, W-SOD-1 disclosed, 2026-08-01) — **G2 mini-gate EXITED untuk Mode A lab** |

**Decision**
- **G2-S1 Broker:** tidak ada broker fisik untuk Mode A SIT/UAT wave-1; transport resmi tetap **transactional outbox + in-process drain**; consumer KPI/SLA multi-proses pertama (FR-030) memicu ulang evaluasi broker; jangan bangun framework multi-broker generik.
- **G2-S2 Customer Master:** tetap **stub**; API-010 tetap ditunda; jangan implementasi Customer 360 dengan field profil yang dikarang; Mode A DoD tidak mensyaratkan API-010.
- **G2-S3 Observability:** floor Mode A diterima — JSON logs + `X-Request-ID` pada kedua tree; Prometheus/Grafana/Sentry **out of scope**; TS-OBS-001 tetap Draft untuk metrik/APM penuh.
- **G2-S4 Regression pack & runbook:** diadopsi (`REGRESSION_PACK_G2.md`, `DEV_RUNBOOK.md`, `run_g2_regression.sh`).
- **DEC-006 U-1 Reopen subset:** **di luar Mode A DoD** — subset workflow terkonfigurasi mengecualikan `CLOSED→REOPENED`; EVT-007 tetap Proposed; tidak menghapus reopen dari DOM jangka panjang.
- **Dual-tree SIT SoT (di bawah DEC-020):** konformansi kontrak/lifecycle = `implementation/backend` + `case-service.v1.yaml`; lab edge/VPS operator surface = `backend/` + `/api/v1/complaints` (+ `cm_batch1` bila berlaku). **Tanpa forced merge**; Retirement DEC masih diperlukan.
- **Non-decision eksplisit:** Mode B / OIDC production issuer · mengarang stub profil Customer Master · klaim "Production Enterprise Ready" · memilih RabbitMQ/Kafka sekarang.

**Business Context**
Gate G2 memerlukan keputusan atas broker, Customer Master, observability, dan paket regresi sebelum Mode A lab dapat dinyatakan keluar gate.

**Reason**
Menutup gate dengan lantai yang jujur dan terbukti, tanpa membangun infrastruktur atau data yang belum punya sumber nyata.

**Alternatives Considered**
Tercatat per sub-keputusan (mis. memilih broker sekarang vs memperpanjang outbox).

**Impact**
Transport event · Integrasi Customer Master · Observability · Paket regresi · SoT dual tree.

**Affected Documents**
`27 Project Decisions/DEC-021_G2_Mini_Gate_Mode_A_v1.0.md` · `05 Architecture Decision Records/ECMP_ADR_009_Addendum_G2_InProcess_Extension_v1.0.md` · `deploy/evidence/G2_Mini_Gate_Mode_A_20260801.md` · `implementation/backend/REGRESSION_PACK_G2.md` · `implementation/backend/DEV_RUNBOOK.md`

**Related Decisions**
DL-022 (U-1) · DL-031 · DL-035 · DL-044 · DL-052

**Supersedes**
Menutup butir terbuka U-1 DEC-006 untuk perencanaan Mode A.

**Notes**
Tabrakan ID dengan DEC-021 (O-06) dicatat pada DL-053; gunakan path berkas + judul sebagai pembeda.

---

#### DL-052 — Penutupan Program CAP-008

| Field | Value |
|---|---|
| **Decision ID** | DL-052 |
| **Title** | GOV-CAP008-CLOSE-010 — PROGRAM CLOSED |
| **Status** | Approved — **PROGRAM CLOSED** (Architecture Review Board, 2026-08-01) |

**Decision**
Program delivery **CAP-008 Case Management Batch-2 Mode A** ditutup efektif 2026-08-01, dengan seluruh delapan kriteria terverifikasi PASS (Business Lock READY & residual BQ ZERO; FRD-CM-B2-001 LOCKED; OpenAPI API-530…535 Implemented (lab) normatif; Lab RC `v1.2.0-rc.1` PASS; Traceability TRC-L-011…016 Approved; Capability Register CAP-008 Implemented (lab); SoT Closure COMPLETE; closure pack 001–009 tercatat). **Efek mengikat:** tidak ada delivery fitur CAP-008 Mode A lanjutan di bawah program ini; follow-up atas FRD/BCS/BQ/OpenAPI Mode A yang terkunci = **NONE** tanpa CR baru; roadmap reset menjadi otoritatif untuk penjadwalan CAP-008; promote produksi dan Mode B tetap program/gate **terpisah**. **Non-decision eksplisit:** tidak mengotorisasi tag `v1.2.0` (REL-SEC-001 NO-GO), tidak membuka Mode B (C-7 tetap), tidak mempensiunkan dual SoT (butuh Retirement DEC), tidak mengarang OIDC/EVT ID.

**Business Context**
Batch-2 Mode A telah menyelesaikan seluruh gate bisnis, kontrak, dan bukti rilis lab.

**Reason**
Menutup program secara formal agar tidak ada penambahan lingkup diam-diam pada artefak yang sudah terkunci.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Roadmap · Backlog CAP-008 · Rilis · Traceability.

**Affected Documents**
`18 Architecture Governance/ECMP_PROGRAM_CAP008_010_Final_Closure_Decision_v1.0.md` · `…/ECMP_PROGRAM_CAP008_000_Program_Closure_Index_v1.0.md` · `…/ECMP_PROGRAM_CAP008_001…009` · `ai/sprint/CAP008_ROADMAP_RESET_v1.0.md` · `deploy/evidence/CAP-008_SoT_Closure_20260801.md`

**Related Decisions**
DL-023 · DL-024 · DL-044 · DL-051

**Supersedes**
—

**Notes**
Tag `v1.2.0` **tidak** diotorisasi oleh penutupan ini — pembatasan rilis tetap berlaku.

---

#### DL-053 — Penanganan Tabrakan ID DEC

| Field | Value |
|---|---|
| **Decision ID** | DL-053 |
| **Title** | DEC ID Collision Register — Board Option A |
| **Status** | **CLOSED — Board Option A** (`EXT-HD-RC-MA-B1-20260801`, 2026-08-01) |

**Decision**
Tabrakan ID DEC dicatat **hanya sebagai dokumentasi** — **tanpa renumber** dan **tanpa penulisan ulang isi DEC**. Tabrakan yang tercatat: **DEC-020** dipakai dua berkas Accepted (SoT/namespace remapping vs lab auth local-then-SSO) dan **DEC-021** dipakai dua berkas berbeda status/topik (O-06 descendant AuthZ berstatus Proposed vs G2 mini-gate berstatus Accepted). Sampai Board memilih opsi renumber, **path berkas + judul** diperlakukan sebagai pembeda; dilarang mengklaim satu makna tunggal untuk "DEC-021".

**Business Context**
Artefak G2 mengutip DEC-021 untuk gate G2, sementara OPEN_QUESTIONS dan ADR-018 mengutip DEC-021 untuk O-06 — dua makna berbeda pada satu ID.

**Reason**
Renumber massal berisiko memutus kutipan yang sudah tersebar; pencatatan integritas dokumentasi dipilih sebagai tindakan P0 tanpa efek samping.

**Alternatives Considered**
**A** dokumentasikan saja (dipilih) · **B** renumber G2 → ID bebas berikutnya · **C** suffix eksplisit (`DEC-020-A`/`DEC-020-B`) lewat kebijakan penomoran baru.

**Impact**
Integritas dokumentasi · Kutipan lintas artefak · Index DEC.

**Affected Documents**
`deploy/evidence/DEC_ID_Collision_Register_20260801.md` · `27 Project Decisions/README.md` · `27 Project Decisions/DEC-020_*` · `27 Project Decisions/DEC-021_*` · `27 Project Decisions/OPEN_QUESTIONS.md`

**Related Decisions**
DL-044 · DL-051 · DL-058

**Supersedes**
—

**Notes**
DL-000 mengikuti aturan ini: setiap rujukan ke DEC-020/DEC-021 di dokumen ini menyertakan topiknya, bukan ID saja.

---

### 3.H Security

---

#### DL-054 — Model Autentikasi Fase Slice

| Field | Value |
|---|---|
| **Decision ID** | DL-054 |
| **Title** | ADR-007 — Bearer token statis dari environment (DEV/CI lokal saja) |
| **Status** | Approved / Accepted; relasi ADR-007 ↔ ADR-012 **tetap Pending** (C-B6-6) |

**Decision**
1. AuthN fase slice = **Bearer token statis dari environment** (`ECMP_DEV_TOKEN`), **bukan** literal hardcoded di source.
2. Principal slice: `{userId, permissions[]}`; permission `cases:create`, `cases:read` selaras Role Matrix.
3. **Batasan terdaftar (known limitation):** tanpa expiry, tanpa user store, tanpa multi-principal — **hanya** untuk DEV lokal/CI; **dilarang** untuk shared UAT/PROD.
4. Semantik status: token hilang/salah → **401** (`UNAUTHENTICATED`); token sah tanpa permission → **403** (`FORBIDDEN`).

**Business Context**
Slice awal membutuhkan autentikasi minimal sebelum arsitektur auth target tersedia.

**Reason**
Memberi kontrol akses fungsional untuk pengembangan tanpa membangun IdP prematur, dengan batasan yang terdaftar sebagai limitasi resmi.

**Alternatives Considered**
Tercatat di ADR-007 §Options.

**Impact**
Backend AuthN · CI · Larangan lingkungan bersama · Kode status API.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_007_Authentication_Model_v1.0.md` · `10 Security and Access Standards/` · `14 Deployment Standards/` (DEP-001 §1)

**Related Decisions**
DL-036 · DL-055 · DL-049 (C-B6-6) · DL-058

**Supersedes**
—

**Notes**
Larangan dev-token di lingkungan bersama adalah dasar langsung syarat aktivasi SIT/UAT pada DL-036.

---

#### DL-055 — Target Authentication Architecture

| Field | Value |
|---|---|
| **Decision ID** | DL-055 |
| **Title** | ADR-012 — OIDC/OAuth2, Keycloak sebagai baseline IdP, mode switch fail-fast |
| **Status** | Approved / Accepted; relasi terhadap ADR-007 **tetap Pending** (C-B6-6) |

**Decision**
1. **Standar protokol, bukan vendor lock:** pengguna diautentikasi via **OIDC (Authorization Code + PKCE)**, service via **OAuth2 client_credentials**; validasi sisi ECMP hanya memakai permukaan standar (discovery, JWKS, token/revocation/logout) agar IdP dapat ditukar.
2. **Baseline IdP = Keycloak (Option A)**, dideploy sebagai container pada baseline compose ADR-010 untuk SIT/UAT; berpindah ke IdP korporat/managed kemudian adalah keputusan swap/brokering IdP, bukan perubahan aplikasi.
3. **Model token:** access token JWT RS256 divalidasi tiap request (signature via JWKS ter-cache, `iss`, `aud`, `exp`, `nbf`); umur access token **15 menit**; refresh token **rotating, 8 jam idle / 12 jam max session, reuse detection**; ID token hanya untuk pembentukan sesi login, tidak pernah dikirim ke API ECMP.
4. **Integrasi RBAC:** JWT membawa identitas + roles + org scope (`sub`, `preferred_username`, `roles[]`, `orgUnitId`, `sid`); **permission TIDAK disematkan di token** — Core Platform me-resolve `roles[] → permissions{}` saat request dari Role-Permission Matrix (SoT ADR-008, cache TTL pendek).
5. **Mekanisme dev-token dipertahankan hanya untuk DEV/CI lokal**, di balik mode switch eksplisit (`ECMP_AUTH_MODE=dev|jwt`); aplikasi **harus menolak start** dengan mode `dev` di lingkungan bersama mana pun.

**Business Context**
Fase slice memakai token statis yang tidak layak untuk lingkungan bersama; dibutuhkan arsitektur auth target sebelum SIT/UAT.

**Reason**
Menjaga IdP dapat ditukar, menjaga token tetap kecil, dan membuat perubahan permission berlaku dalam TTL cache alih-alih TTL token — sekaligus mempertahankan SoT tunggal.

**Alternatives Considered**
**Option A — Keycloak sebagai baseline** (dipilih) vs Option B — IdP korporat/managed sejak awal.

**Impact**
AuthN · Session · RBAC resolution · Deployment · Konfigurasi fail-fast · Frontend login flow.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_012_Target_Authentication_Architecture_v1.0.md` · `10 Security and Access Standards/ECMP_Target_Authentication_Architecture_v1.0.md` (SEC-AUTH-001) · `18 Architecture Governance/reviews/ECMP_ADR_012_Architecture_Board_Countersign_Pack_v1.0.md` · `14 Deployment Standards/`

**Related Decisions**
DL-036 · DL-039 · DL-041 · DL-054 · DL-056 · DL-057 · DL-058 · DL-059

**Supersedes**
Menjadi fase target bagi model AuthN slice ADR-007 (relasi formal keduanya masih Pending).

**Notes**
Posture fail-fast butir 5 adalah dasar gerbang konfigurasi yang menghentikan startup (production/staging mewajibkan `jwt`; `jwt` mewajibkan `OIDC_ISSUER`/`OIDC_AUDIENCE`/`OIDC_JWKS_URL`).

---

#### DL-056 — Role-Permission Matrix SoT

| Field | Value |
|---|---|
| **Decision ID** | DL-056 |
| **Title** | ADR-008 — SoT Role-Permission = Core Platform; Administration hanya konfigurator |
| **Status** | Approved / Accepted |

**Decision**
Entitas **Role, Permission, Role-Permission, User-Role** dimiliki dan ditegakkan **Core Platform**. **Administration hanya konfigurator** (UI/proses perubahan + approval BR-ADM-01) yang menulis melalui API Core Platform; Administration **tidak** menyimpan salinan otoritatif. Role-Permission di Administration ditandai sebagai "config view, non-SoT".

**Business Context**
Tanpa SoT tunggal, matriks role-permission berisiko punya dua salinan yang berbeda.

**Reason**
Menjaga satu sumber kebenaran otorisasi yang dapat diaudit dan ditegakkan konsisten.

**Alternatives Considered**
Tercatat di ADR-008 (SoT di Administration vs Core Platform).

**Impact**
Authorization · Administration UI · Data Dictionary · Audit · Resolusi permission Mode B.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_008_RBAC_SoT_Workflow_Ownership_v1.0.md` · `10 Security and Access Standards/` (SEC-RAM-001) · `06 Data Dictionary/` · `docs/frontend/FRONTEND_ARCHITECTURE_v1.2.md` §2.2

**Related Decisions**
DL-015 · DL-025 · DL-039 · DL-042 · DL-055 · DL-065

**Supersedes**
Klaim kepemilikan matriks role-permission oleh Administration.

**Notes**
ADR-014 menegaskan Enterprise Platform **tidak** mengambil alih SoT ini di Mode B.

---

#### DL-057 — Larangan Local Auth pada Enterprise Mode

| Field | Value |
|---|---|
| **Decision ID** | DL-057 |
| **Title** | ADR-014 — Enterprise Mode Local Auth Prohibition |
| **Status** | Approved with Conditions (bagian dari ADR-014 v1.4 — BR-009) |

**Decision**
Saat **Mode B** aktif: **Local Login dinonaktifkan · Forgot Password dinonaktifkan · Reset Password dinonaktifkan · Change Password dinonaktifkan · penyimpanan password lokal dilarang.** Route kredensial lokal tidak boleh tetap menjadi jalur autentikasi di bawah Mode B. Konfigurasi yang mengaktifkan Mode B **dan** local login sekaligus harus **fail closed (fail-fast)**, konsisten dengan posture kontrol ADR-012.

**Business Context**
ECMP versi standalone memiliki permukaan password management (SEC-PWD-001, API-410…413) yang menjadi utang saat ECMP menjadi modul.

**Reason**
Mencegah dua jalur autentikasi hidup bersamaan — sumber kebocoran akses dan audit identitas terfragmentasi.

**Alternatives Considered**
Mempertahankan local login sebagai fallback Mode B (ditolak — Mode A bukan IdP fallback).

**Impact**
AuthN · Route kredensial · Konfigurasi startup · Permukaan Mode A yang harus dijaga.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_014_ECMP_Enterprise_Business_Module_v1.4.md` · `10 Security and Access Standards/ECMP_Identity_Password_Management_v1.0.md` (SEC-PWD-001) · `…/ECMP_Target_Authentication_Architecture_v1.0.md` (SEC-AUTH-001) · guard `frontend` check auth-routes

**Related Decisions**
DL-039 · DL-055 · DL-058 · DL-059

**Supersedes**
Kelayakan password management lokal sebagai fitur ECMP di bawah Mode B.

**Notes**
ADR-014 mencatat ini sebagai **cross-reference dampak** — ADR tidak memindahkan atau menulis ulang standar SEC-PWD-001/SEC-AUTH-001.

---

#### DL-058 — Auth Lab: Local JWT Sekarang, SSO sebagai Target

| Field | Value |
|---|---|
| **Decision ID** | DL-058 |
| **Title** | DEC-020 (lab auth) — local JWT untuk lab, SSO/OIDC sebagai fase target |
| **Status** | 🟢 Accepted (ops working agreement, Product/Ops → Business Owner, 2026-07-31) |

**Decision**
**Opsi B.** (1) **Sekarang:** username/password lokal + JWT (user lab/seed di Postgres), cocok untuk lab Mode A dan cutover HTTPS pertama di balik Caddy. (2) **Nanti:** SSO/OIDC per ADR-007 target / ADR-012 (mis. Keycloak atau IdP korporat) sebagai login lingkungan bersama yang **dimaksudkan** — bukan jembatan sementara. (3) **Out of scope cutover VPS saat ini:** coding SSO enterprise Mode B, procurement IdP, dan fitur produk MFA.

**Business Context**
Stakeholder menginginkan subdomain publik dan sempat menyebut SSO sebagai "login sementara" — frasa yang bertentangan dengan ADR-007/ADR-012 yang menempatkan SSO/OIDC sebagai jalur **target**.

**Reason**
Membuka cutover subdomain + TLS tanpa memperluas ruang lingkup auth, dan menghindari membangun lalu membuang tumpukan IdP "sementara".

**Alternatives Considered**
**A** bangun SSO/OIDC sekarang bersamaan cutover subdomain · **B** local JWT dulu, SSO sebagai fase target (dipilih) · **C** SSO sebagai login sementara berumur pendek lalu diganti lagi.

**Impact**
Edge deploy (Caddy, compose) · Kredensial lab · Roadmap SSO · Runbook migrasi.

**Affected Documents**
`27 Project Decisions/DEC-020_Lab_Auth_Local_Then_SSO_Target_v1.0.md` · `deploy/Caddyfile` · `docker-compose.prod.yml` · `deploy/README.md`

**Related Decisions**
DL-053 (tabrakan ID) · DL-054 · DL-055 · DL-059 · DL-036

**Supersedes**
Framing "SSO sebagai login sementara".

**Notes**
Setiap pekerjaan SSO memerlukan keputusan/aktivasi ADR terpisah — dilarang dicampurkan ke compose Mode A tanpa sign-off.

---

#### DL-059 — Pintu Auth: Sekarang vs Nanti (Handoff Mode A → Mode B)

| Field | Value |
|---|---|
| **Decision ID** | DL-059 |
| **Title** | DEC-023 — fleksibel di pintu auth (adapter), bukan portal Enterprise palsu |
| **Status** | 🟢 Accepted (ops/stakeholder working agreement, 2026-08-04) — **bukan** unlock Mode B |

**Decision**
**Dua alamat tidak boleh dicampur:** apex (`layanankami.tech`) = landing statis lab (**bukan** produk SSO Enterprise Platform); subdomain (`pengaduan.layanankami.tech`) = modul Pengaduan ECMP Mode A. **Sekarang (Mode A):** pengguna membuka `/login` modul, login lokal (username/password + JWT per DEC-020 lab auth), memakai siklus complaint di dalam modul; tidak ada syarat "harus lewat portal dulu". **Nanti (Mode B, setelah Board unlock):** pengguna login di Enterprise Platform, memilih modul Pengaduan di navigasi EP, EP mengarahkan ke modul (deep-link/embed — detail protokol OD-FE-002 + ADR-016), ECMP menerima identitas lewat **Identity Adapter** (ADR-014/015) lalu AuthZ internal modul; **domain complaint tidak diubah** hanya karena cara login berganti. **Dilarang:** meniru halaman `/login` SSO portal di repo ECMP sebelum Board unlock dan kontrak IdP tersedia.

**Business Context**
Domain lab `layanankami.tech` memunculkan godaan membangun portal/login seolah Enterprise Platform sudah ada di apex domain.

**Reason**
Fleksibilitas yang diinginkan benar — saat Enterprise nyata datang, yang diganti hanya mekanisme masuk. Cara yang salah adalah membangun "mall mini" di ECMP yang nanti dibongkar.

**Alternatives Considered**
Membangun portal/SSO stand-in di ECMP (ditolak) · fleksibel di pintu auth lewat adapter (dipilih).

**Impact**
Topologi domain lab · Roadmap login · Batas ruang lingkup Mode A · Landing apex.

**Affected Documents**
`27 Project Decisions/DEC-023_Auth_Door_Now_vs_Later_Mode_A_Handoff_v1.0.md` · `deploy/APEX_LANDING_CUTOVER_CHECKLIST.md` · `deploy/evidence/Apex_Landing_Cutover_OpsiA_20260804.md` · `docs/frontend/OPEN_DECISIONS.md` (OD-FE-002)

**Related Decisions**
DL-039 · DL-041 · DL-055 · DL-057 · DL-058 · DL-046

**Supersedes**
Asumsi "apex = Enterprise Platform" sebagai dasar implementasi (hanya berlaku untuk diskusi desain + landing sementara).

**Notes**
Ini formulasi paling ringkas dari North Star pada ranah auth: yang berubah adalah pintu, bukan domain.

---

### 3.I Reporting

---

#### DL-060 — KPI Foundation

| Field | Value |
|---|---|
| **Decision ID** | DL-060 |
| **Title** | DEC-015 — modul KPI read-only tanpa tabel/materialized view |
| **Status** | Approved (DEC-015, 2026-07-23) |

**Decision**
**Buat `app/modules/kpi`** — tanpa migrasi database, tanpa tabel KPI, tanpa materialized view, tanpa scheduler, tanpa penulisan ke entitas operasional. `GET /api/v1/kpi/summary` (API-318) mengembalikan agregat live: total complaint (total/open/closed) dan jumlah SLA completed/breached per tahap (assignment, appointment, resolution, escalation, overall). Filter opsional: rentang tanggal (`reportedAt`), branch, category, priority. Permission: **`kpi:read`**. Out of scope: chart dashboard/realtime/caching/Redis, materialized view/scheduler, notifikasi/ekspor (Excel/PDF).

**Business Context**
Domain operasional sudah menyimpan fakta; konsumen dashboard/analitik membutuhkan agregasi atas fakta tersebut.

**Reason**
KPI **tidak boleh menjadi sumber kebenaran kedua**; menghitung agregat dari tabel operasional menjaga metrik konsisten dengan evaluasi SLA tanpa menduplikasi state.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber (yang dicatat: tanpa tabel/materialized view).

**Impact**
KPI · Dashboard · Permission catalog · Beban query operasional.

**Affected Documents**
`27 Project Decisions/DEC-015_KPI_Foundation_Scope_TASK026_v1.0.md` · `07 API Catalog/` (API-318) · `11 SLA and KPI Matrix/` · `docs/domain/kpi.md`

**Related Decisions**
DL-017 · DL-018 · DL-019 · DL-061 · DL-062

**Supersedes**
—

**Notes**
Prinsip "no second source of truth" di sini sejajar dengan larangan projeksi otoritatif pada DL-014.

---

#### DL-061 — Dashboard API

| Field | Value |
|---|---|
| **Decision ID** | DL-061 |
| **Title** | DEC-016 — modul dashboard sebagai orchestration layer saja |
| **Status** | Approved (DEC-016, 2026-07-23) |

**Decision**
**Buat `app/modules/dashboard` sebagai orchestration layer saja**: tidak memiliki business logic, tidak melakukan perhitungan KPI, tidak menyimpan data (tanpa migrasi/tabel dashboard), dan **tidak pernah** query database langsung — memanggil KPI Service, Timeline Service, dan Complaint Service. `GET /api/v1/dashboard/summary` (API-319) mengembalikan **Header** (total/open/closed dari KPI), **SLA Summary** (lima tahap, completed/breached dari KPI), dan **Recent Activity** (≤10 timeline event terbaru dengan tipe event, nomor complaint, timestamp, aktor). Permission: **`dashboard:read`**. Frontend mengganti banyak fetch dashboard dengan satu request API-319. Out of scope: chart/grafik/analitik, realtime websocket, caching/Redis, notifikasi/scheduler/queue, ekspor/reporting.

**Business Context**
UI dashboard sebelumnya menarik data dari beberapa endpoint terpisah.

**Reason**
Menyatukan pembacaan tanpa menciptakan domain kedua atau logika bisnis baru di lapisan dashboard.

**Alternatives Considered**
Tidak dicatat sebagai daftar opsi formal di sumber.

**Impact**
Dashboard API · Frontend dashboard · KPI/Timeline/Complaint service.

**Affected Documents**
`27 Project Decisions/DEC-016_Dashboard_API_Scope_TASK027_v1.0.md` · `07 API Catalog/` (API-319, API-318) · `docs/domain/dashboard.md`

**Related Decisions**
DL-018 · DL-026 (dashboard read-only hardcoded) · DL-060 · DL-062

**Supersedes**
—

**Notes**
Sifat read-only dashboard konsisten dengan daftar rule "Hardcoded" pada DL-026 dan persona Manager read-only pada DL-001.

---

#### DL-062 — Penutupan Keputusan Bisnis CAP-007 (Dashboard)

| Field | Value |
|---|---|
| **Decision ID** | DL-062 |
| **Title** | DEC-CAP007-BQ-001 — BQ-CAP007-01…05 |
| **Status** | CLOSED / Approved (2026-08-01); FRD CAP-007 dikunci pada B2-12 |

**Decision**

| BQ | Hasil |
|---|---|
| 01 | **Approve** Sprint ECMF Case SoT sebagai dasar dashboard |
| 02 | **Approve** permission **`dashboard:read`** |
| 03 | **Approve** drill-down hanya via **API-002/005** |
| 04 | **Approve** cakupan **Supervisor-only v0.1**; Manager/Executive **Defer** |
| 05 | **Defer** kolom FR-030 (konfirmasi penundaan sebelumnya) |

**Business Context**
CAP-007 (Dashboard) memerlukan penutupan pertanyaan bisnis sebelum FRD dan API-040 dapat dinormatifkan.

**Reason**
Menetapkan audiens, permission, dan jalur drill-down agar dashboard tidak melebar menjadi analitik penuh.

**Alternatives Considered**
Tercatat per BQ pada paket keputusan B2-11.

**Impact**
Dashboard · Permission · Audiens persona · FRD CAP-007 · API-040.

**Affected Documents**
`deploy/evidence/B2-11_CAP-007_Business_Decision_Closure_20260801.md` · `deploy/evidence/B2-12_CAP-007_FRD_Lock_Governance_Closure_20260801.md` · `deploy/evidence/B2-13_API-040_Normative_Closure_20260801.md` · `deploy/evidence/B2-14_CAP-007_Engineering_Implementation_20260801.md`

**Related Decisions**
DL-060 · DL-061 · DL-001 (persona Manager)

**Supersedes**
—

**Notes**
**BQ-04 penting untuk BC-000:** dashboard v0.1 secara resmi **Supervisor-only**; Manager/Executive ditunda — perlu dibaca bersama persona Manager pada DL-001.

---

### 3.J Audit

---

#### DL-063 — Write-Audit Wajib, Read-Audit Ditunda

| Field | Value |
|---|---|
| **Decision ID** | DL-063 |
| **Title** | OQ-007 — audit-on-write wajib; audit-on-read ditunda |
| **Status** | Resolved / Approved (Business Owner, 2026-07-21; tercatat pada FRD-001 §9 + DEC-002) |

**Decision**
**Write-audit wajib** (BR-008 / FR-001c) — termasuk write-audit pada create sebagai deliverable G0. **Read-audit ditunda**. **Idempotency key** berada di luar acceptance criteria Sprint-01. Membangun **framework audit generik** dinyatakan non-goal Sprint-0/G0.

**Business Context**
Pertanyaan terbuka OQ-007 menanyakan apakah audit-on-read wajib atau dapat ditunda.

**Reason**
Menjamin jejak perubahan data sejak hari pertama tanpa membangun infrastruktur audit yang belum terbukti dibutuhkan.

**Alternatives Considered**
Audit-on-read wajib sejak awal (ditolak/ditunda).

**Impact**
Audit log · Slice create/get · G0 exit criteria · Test.

**Affected Documents**
`27 Project Decisions/OPEN_QUESTIONS.md` · `27 Project Decisions/DEC-002_Build_Authorization_G0_v1.0.md` · `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` §9 · `02 Business Rules/` (BR-008)

**Related Decisions**
DL-050 · DL-064 · DL-065

**Supersedes**
Status Open OQ-007.

**Notes**
Penundaan read-audit belum pernah dicabut oleh keputusan berikutnya.

---

#### DL-064 — Audit Trail Immutable & Override Berjustifikasi

| Field | Value |
|---|---|
| **Decision ID** | DL-064 |
| **Title** | Audit immutable (hardcoded) + override otorisasi wajib berjustifikasi |
| **Status** | Approved (ADR-003 Accepted; BR-CP-02 baseline via DEC-004) |

**Decision**
**Audit trail immutable** termasuk kelas rule **Hardcoded** — tidak boleh dijadikan opsi konfigurasi yang bisa dimatikan (bersama autentikasi wajib, dashboard read-only, dan resolusi wajib saat closure). **Override otorisasi (BR-CP-02)** hanya boleh dilakukan **Administrator** dengan **justifikasi tercatat + audit trail**.

**Business Context**
Beberapa aturan integritas berisiko ikut menjadi konfigurasi ketika config engine diperkenalkan.

**Reason**
Melindungi aturan keamanan/integritas inti dari kesalahan konfigurasi operasional, dan menjadikan setiap penyimpangan otorisasi dapat dipertanggungjawabkan.

**Alternatives Considered**
Menjadikan seluruh rule dapat dikonfigurasi (ditolak pada ADR-003).

**Impact**
Audit · Administration config · Security · Dashboard.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_003_Configuration_First_Principle_v1.0.md` · `27 Project Decisions/DEC-004_BR_Baseline_Defaults_v1.0.md` · `02 Business Rules/` (BR-CP-02) · `17 Compliance/`

**Related Decisions**
DL-004 · DL-026 · DL-063 · DL-065

**Supersedes**
Butir `[TBD]` BR-CP-02.

**Notes**
Business Owner dapat merevisi nilai baseline BR-CP-02 lewat DEC baru, tetapi sifat immutable audit trail berasal dari ADR-003 dan bukan nilai baseline yang reversibel.

---

#### DL-065 — Audit Perubahan Role-Permission & Workflow Config

| Field | Value |
|---|---|
| **Decision ID** | DL-065 |
| **Title** | ADR-008 — audit kedua jenis perubahan wajib di Core Platform |
| **Status** | Approved / Accepted |

**Decision**
Audit atas **perubahan Role-Permission** dan **perubahan Workflow Config** adalah **wajib** (BR-008 / BR-ADM-02) dan dicatat di **Core Platform**.

**Business Context**
Perubahan otorisasi dan definisi workflow adalah perubahan berdampak tinggi yang sebelumnya tidak memiliki kewajiban audit tunggal.

**Reason**
Menjaga akuntabilitas atas dua konfigurasi paling sensitif dalam modul, konsisten dengan SoT masing-masing.

**Alternatives Considered**
Tercatat di ADR-008.

**Impact**
Audit · Administration · Core Platform · Compliance.

**Affected Documents**
`05 Architecture Decision Records/ECMP_ADR_008_RBAC_SoT_Workflow_Ownership_v1.0.md` · `02 Business Rules/` (BR-008, BR-ADM-02) · `17 Compliance/` · `10 Security and Access Standards/`

**Related Decisions**
DL-025 · DL-056 · DL-063 · DL-064 · DL-012 (audit perubahan `result_visibility`)

**Supersedes**
—

**Notes**
DEC-F4 (DL-012) menambahkan satu kewajiban audit domain-spesifik (`result_visibility` yang diubah setelah Resolve) — belum ter-countersign Board.

---

### 3.K Business Owner Priority-1 Resolutions (G0.2D)

Keputusan berikut **tidak menciptakan perilaku produk baru**; mereka mencatat disposisi Business Owner atas isu P1 (BO-WS-000 / BO-000) agar BC-000 dapat dikutip tanpa interpretasi tambahan.

---

#### DL-066 — Mode A Scope Consolidation (Escalation + Appointment)

| Field | Value |
|---|---|
| **Decision ID** | DL-066 |
| **Title** | Mode A Scope Consolidation — Head Office Escalation & Appointment |
| **Status** | Approved (Business Owner – ECMP, 2026-08-05) |
| **Source** | BO-001 Option A + BO-005 Option A · **Merged** per BO workshop (Merge = YES) |

**Decision**

1. **Head Office Escalation** adalah bagian resmi Complaint Lifecycle ECMP. Lingkup dibatasi pada **Branch ↔ Head Office**.
2. **Appointment** adalah bagian resmi ruang lingkup **Mode A**, mengikuti **Complaint Lifecycle yang sama** (bukan lifecycle terpisah), sesuai batasan yang telah disetujui pada rantai DEC-007…011.
3. Tetap **Out of Scope** sampai Decision Record + Governance Review baru: **Regional Office · Work Order · Calendar/Scheduling · Mode B · Enterprise Integration**.

**Business Context**
DRR C-08 dan BO-05: OOS DEC-001 untuk escalation tidak pernah dicabut secara eksplisit, sementara appointment diperluas berantai tanpa pernyataan kumulatif. Business Owner menggabungkan keduanya sebagai satu keputusan lingkup Mode A.

**Reason**
Menutup celah pencatatan lingkup agar pasal Lingkup BC-000 tidak mengutip DEC-001 mentah secara salah.

**Alternatives Considered**
A — otorisasi terbatas (dipilih) · B — tegakkan OOS · C — ratifikasi retrospektif saja (untuk escalation); untuk appointment: A konsolidasi · B tanpa konsolidasi · C tarik kembali.

**Impact**
Pasal Lingkup BC-000 · kutipan DL-002 · DEC-F4 (formalitas tetap P2) · rantai DEC-007…011.

**Affected Documents**
`docs/governance/BO-000-*` · `docs/governance/BO-WS-000-*` · `docs/governance/GC-000-*` · DEC-001 · DEC-007…011 · DEC-F4 · `07 API Catalog/` · `08 Event Catalog/`

**Related Decisions**
DL-002 · DL-007…011 · DL-012 · DL-017

**Supersedes**
Pernyataan OOS DEC-001 **hanya** untuk Head Office Escalation (Branch↔HO) dan Appointment dalam batas Mode A di atas — bukan untuk Regional/WO/Calendar/Mode B/Enterprise.

**Notes**
Berlaku Mode A. DEC formal pencatatan disarankan sebagai follow-up kebersihan, bukan prasyarat drafting BC bila teks keputusan ini dikutip utuh.

---

#### DL-067 — SLA Constitution (Business Owner)

| Field | Value |
|---|---|
| **Decision ID** | DL-067 |
| **Title** | Satu SLA Constitution resmi untuk Complaint Lifecycle |
| **Status** | Approved (Business Owner – ECMP, 2026-08-05) |
| **Source** | BO-002 Option A |

**Decision**
ECMP menggunakan **satu SLA Constitution resmi** untuk seluruh Complaint Lifecycle. SLA dihitung berdasarkan **aturan bisnis yang seragam**. Seluruh perubahan SLA **wajib tercatat sebagai Timeline Events**. Detail implementasi teknis mengikuti Business Constitution dan Business Rules.

**Business Context**
DRR C-12: aturan “bind-without-clock” Mode A (BQ-005) tampak bertentangan dengan perhitungan deadline/breach jalur Foundation (DEC-012/013). Business Owner menetapkan konstitusi SLA bisnis tunggal; detail teknis tidak diinventarisasi ulang di keputusan ini.

**Reason**
Menghilangkan dua aturan bisnis yang tampak saling meniadakan dari materi konstitusi.

**Alternatives Considered**
A — disposisi Option A workshop / konstitusi tunggal (dipilih) · B — clock non-normatif sampai CAP-006 · C — aktifkan clock Aggregate (revisi BQ-005).

**Impact**
Pasal Komitmen Layanan & Waktu BC-000 · pembacaan DL-005 / DL-019 / DL-024 BQ-005 · timeline SLA.

**Affected Documents**
`11 SLA and KPI Matrix/` · FRD-005 · DEC-012…014 · DL-005 · DL-016…019 · DL-024

**Related Decisions**
DL-004 · DL-005 · DL-016 · DL-017 · DL-018 · DL-019 · DL-024

**Supersedes**
Tidak mencabut DEC-012/013 atau BQ-005 sebagai artefak historis; menetapkan **makna bisnis** tunggal untuk kutipan konstitusi. Konvergensi mekanisme runtime CAP-006 tetap follow-up arsitektur (C-05 / M-18).

**Notes**
Mode A. Tidak mengotorisasi Mode B atau unlock runtime CAP-006.

---

#### DL-068 — Manager sebagai Business Persona (Workspace Deferred)

| Field | Value |
|---|---|
| **Decision ID** | DL-068 |
| **Title** | Manager adalah Business Persona sah; Workspace/Dashboard boleh ditunda |
| **Status** | Approved (Business Owner – ECMP, 2026-08-05) |
| **Source** | BO-003 Option A |

**Decision**
**Manager** adalah Business Persona yang sah dalam closed set operasional. **Workspace/Dashboard Manager dapat ditunda** implementasinya. Keberadaan persona **tidak bergantung** pada kesiapan UI.

**Business Context**
DRR C-09: PDS/NAV menetapkan Manager + Dashboard, sementara CAP-007 menunda Manager/Executive untuk dashboard v0.1.

**Reason**
Mempertahankan model aktor bisnis tanpa menjanjikan delivery UI yang belum diotorisasi.

**Alternatives Considered**
A — persona sah, workspace deferred (dipilih) · B — workspace wajib sekarang · C — keluarkan dari closed set.

**Impact**
Pasal Aktor BC-000 · PDS-001 · BQ-CAP007-04 (deferral delivery tetap).

**Affected Documents**
`docs/ux/PDS-001-*` · NAV-001 · IA-001 · FRD-006 · SEC-RAM · DL-001 · DL-062

**Related Decisions**
DL-001 · DL-062 · DL-069

**Supersedes**
—

**Notes**
Tidak mengaktifkan M-26/M-27. Role teknis Manager tetap gap pencatatan sampai DEC Authorization terpisah.

---

#### DL-069 — UX Package Status Synchronization (Administrative)

| Field | Value |
|---|---|
| **Decision ID** | DL-069 |
| **Title** | Sinkronisasi status artefak UX Foundation |
| **Status** | Approved (Business Owner – ECMP, 2026-08-05) |
| **Source** | BO-004 Option A |

**Decision**
Seluruh status artefak UX **wajib disinkronkan** agar konsisten. Dokumen dengan status bertentangan **harus diperbaiki**. Tindakan ini **administratif** dan **tidak mengubah** keputusan bisnis.

**Business Context**
DRR C-07: UX-FOUNDATION-000 §2 menyebut READY sementara §6 dan header anak = Draft.

**Reason**
Tanpa status seragam, Approval paket UX tidak sah dan substansi turunan tidak dapat diklaim mengikat.

**Alternatives Considered**
A — sync ke Draft lalu Review (dipilih) · B — naikkan ke READY sekarang · C — biarkan inkonsisten.

**Impact**
UX-FOUNDATION-000 · PDS/PWDM/IA headers · jalur Review → READY → Approval.

**Affected Documents**
`docs/ux/UX-FOUNDATION-000-*` · PDS-001 · PWDM-001 · IA-001 · turunan NAV/WF

**Related Decisions**
DL-001 · DL-027 · DL-068

**Supersedes**
Klaim READY FOR APPROVAL yang tidak selaras pada §2 payung (dikoreksi G0.2D).

**Notes**
Executed G0.2D: §2 PWDM-001 & IA-001 → Draft. Paket **belum** Approved; Review ulang tetap wajib sebelum READY.

---

## 4. Decision Index (Deliverable 2)

| DL | Judul | Kategori | Status | Artefak sumber | Tanggal |
|---|---|---|---|---|---|
| DL-001 | Merge Front Office & Complaint Officer | UX | Approved (dokumen turunan Draft) | UX-001 Documentation Update / PDS-001 | 2026-08-05 |
| DL-002 | Business Baseline SoT | Business | Approved | DEC-001 | 2026-07-21 |
| DL-003 | Skema ID Business Rule `BR-0xx` | Business | Approved | DEC-003 | 2026-07-21 |
| DL-004 | BR Baseline Defaults (10 `[TBD]`) | Business | Approved | DEC-004 | 2026-07-21 |
| DL-005 | Target numerik SLA & NFR | Business | Approved | DEC-005 | 2026-07-21 |
| DL-006 | Multi-source & multi-target complaint | Business | Approved | DEC-018 | 2026-07-24 |
| DL-007 | Appointment booking scope | Business | Approved | DEC-007 | 2026-07-23 |
| DL-008 | Appointment check-in scope | Business | Approved | DEC-008 | 2026-07-23 |
| DL-009 | Appointment completion scope | Business | Approved | DEC-009 | 2026-07-23 |
| DL-010 | Customer no-show scope | Business | Approved | DEC-010 | 2026-07-23 |
| DL-011 | Final resolution scope | Business | Approved | DEC-011 | 2026-07-23 |
| DL-012 | Escalation visibility, return & result audience | Business | Locked (bisnis) — menunggu countersign Board | DEC-F4 | 2026-07-29 |
| DL-013 | Kepemilikan struktur organisasi | Organization | Accepted with Conditions | ADR-014 v1.4 / BR-009 | 2026-07-30 |
| DL-014 | Organization Synchronization Architecture | Organization | Accepted with Conditions | ADR-018 v1.0 / BR-013 | 2026-07-30 |
| DL-015 | Org-location + complaint module authorization (Mode A) | Organization | Approved | ECMP-EBS-001 | 2026-08-04 |
| DL-016 | SLA deadline calculator (snapshot immutable) | Timeline | Approved | DEC-012 | 2026-07-23 |
| DL-017 | SLA breach detection (event-triggered) | Timeline | Approved | DEC-013 | 2026-07-23 |
| DL-018 | Integrasi SLA ke `complaint_timelines` | Timeline | Approved | DEC-014 | 2026-07-23 |
| DL-019 | Penutupan bisnis CAP-006 (BQ-01…15) | Timeline | CLOSED / Approved | DEC-CAP006-BQ-001 (B2-15/16) | 2026-08-01 |
| DL-020 | CAP-006 mechanism class = Hybrid | Timeline | Accepted | ADR-CAP006-001 (B2-20) | 2026-08-01 |
| DL-021 | CAP-006 runtime konseptual di KPI & Performance | Timeline | Accepted (bukan otorisasi implementasi) | ARC-CAP006-002 (B2-21) | 2026-08-01 |
| DL-022 | G1 Contract Freeze (409, `cases:status`, EVT-002/003) | Workflow | Accepted (contract freeze) | DEC-006 | 2026-07-21 |
| DL-023 | Case State Machine dual SoT (Option O3) | Workflow | APPROVED | DEC-BQ001 | 2026-08-01 |
| DL-024 | Mode A Case Mgmt baseline (BQ-002…014) | Workflow | ALL LOCKED | BQ Lock Pack | 2026-08-01 |
| DL-025 | Workflow Config SoT = Administration | Workflow | Approved | ADR-008 §2 | — |
| DL-026 | Configuration-First Principle | Workflow | Approved | ADR-003 | 2026-07-21 |
| DL-027 | CWX-000 Case Workspace Experience Constitution | UX | 🔒 LOCKED | CWX-000 | 2026-08-03 |
| DL-028 | Penutupan EPIC-CW-001 | UX | Approved (laporan penutupan) | ECMP-EPIC-CW-001-CLOSURE | 2026-08-03 |
| DL-029 | WCAG 2.2 AA sebagai working target | UX | CLOSED / Accepted | OD-FE-009 | 2026-07-30 |
| DL-030 | Event-driven domain integration | Architecture | Approved | ADR-001 | 2026-07-21 |
| DL-031 | ECMP bukan SoR pelanggan (read-only cache) | Architecture | Approved | ADR-002 | 2026-07-21 |
| DL-032 | Stack implementasi backend | Architecture | Approved | ADR-004 | — |
| DL-033 | Backend layering | Architecture | Approved | ADR-005 | — |
| DL-034 | API versioning `/v1` | Architecture | Approved | ADR-006 | — |
| DL-035 | Deferral broker + transactional outbox (+Addendum G2) | Architecture | Approved / Accepted | ADR-009 (+Addendum) | — / 2026-08-01 |
| DL-036 | Baseline platform deployment | Architecture | Approved | ADR-010 | 2026-07-21 |
| DL-037 | Deferral frontend produk (API-first) | Architecture | Approved | ADR-011 | 2026-07-21 |
| DL-038 | Frontend technology stack (React+Vite) | Architecture | Approved — tetap aktif (BR-007) | ADR-013 | 2026-07-22 |
| DL-039 | ECMP sebagai Enterprise Business Module | Architecture | Accepted with Conditions | ADR-014 v1.4 / BR-009 | 2026-07-30 |
| DL-040 | Enterprise Identity Contract (Bilateral) | Architecture | Accepted with Conditions | ADR-015 v1.3 / BR-010 | 2026-07-30 |
| DL-041 | Enterprise Protocol & Binding | Architecture | Accepted with Conditions | ADR-016 v1.0 / BR-011 | 2026-07-30 |
| DL-042 | Enterprise Entitlement Architecture | Architecture | Accepted with Conditions | ADR-017 v1.0 / BR-012 | 2026-07-30 |
| DL-043 | Canonical trees `backend/` + `frontend/` | Architecture | Approved | DEC-019 | 2026-07-25 |
| DL-044 | Dual SoT & namespace remapping | Architecture | Approved | DEC-020 (SoT remapping) | 2026-07-30 |
| DL-045 | FE-ARCH/FE-STD BASELINE + FE-CI-POL Accepted | Architecture | BASELINE / Accepted with Conditions | FE-ARCH-001, FE-STD-001, FE-CI-POL-001 | 2026-07-30 |
| DL-046 | ECMP-CONSTITUTION-001 (North Star) | Governance | 🔒 LOCKED | ECMP-CONSTITUTION-001 v1.1 | 2026-07-31 |
| DL-047 | GOV-001 kategori delivery A/B/C | Governance | 🔒 LOCKED | GOV-001 | 2026-08-03 |
| DL-048 | Board-004: Accept with Conditions ADR-014/015 | Governance | Approved (Resolution) | PROGRAM-BOARD-004 | 2026-07-30 |
| DL-049 | Board-006: Accept with Conditions ADR-016/017/018 | Governance | Approved (Resolution) | PROGRAM-BOARD-006 | 2026-07-30 |
| DL-050 | Otorisasi build Sprint-01 + G0 | Governance | Approved | DEC-002 | 2026-07-21 |
| DL-051 | G2 Mini-Gate Mode A (EXITED) | Governance | Approved | DEC-021 (G2) | 2026-08-01 |
| DL-052 | CAP-008 PROGRAM CLOSED | Governance | Approved | GOV-CAP008-CLOSE-010 | 2026-08-01 |
| DL-053 | DEC ID collision — Board Option A | Governance | CLOSED | DEC ID Collision Register | 2026-08-01 |
| DL-054 | Model AuthN fase slice (dev token) | Security | Approved (relasi ADR-012 Pending) | ADR-007 | — |
| DL-055 | Target Authentication Architecture (OIDC/Keycloak) | Security | Approved (relasi ADR-007 Pending) | ADR-012 | — |
| DL-056 | Role-Permission Matrix SoT = Core Platform | Security | Approved | ADR-008 §1 | — |
| DL-057 | Larangan local auth pada Mode B | Security | Accepted with Conditions | ADR-014 v1.4 | 2026-07-30 |
| DL-058 | Lab auth: local JWT sekarang, SSO target | Security | Accepted (ops) | DEC-020 (lab auth) | 2026-07-31 |
| DL-059 | Pintu auth Mode A → Mode B handoff | Security | Accepted (ops) | DEC-023 | 2026-08-04 |
| DL-060 | KPI Foundation (read-only) | Reporting | Approved | DEC-015 | 2026-07-23 |
| DL-061 | Dashboard API (orchestration only) | Reporting | Approved | DEC-016 | 2026-07-23 |
| DL-062 | Penutupan bisnis CAP-007 (dashboard) | Reporting | CLOSED / Approved | DEC-CAP007-BQ-001 (B2-11) | 2026-08-01 |
| DL-063 | Write-audit wajib, read-audit ditunda | Audit | Resolved / Approved | OQ-007 + DEC-002 + FRD-001 §9 | 2026-07-21 |
| DL-064 | Audit immutable + override berjustifikasi | Audit | Approved | ADR-003 + DEC-004 (BR-CP-02) | 2026-07-21 |
| DL-065 | Audit perubahan role-permission & workflow config | Audit | Approved | ADR-008 §3 | — |
| DL-066 | Mode A Scope Consolidation (Escalation + Appointment) | Business | Approved | BO-001+BO-005 merged | 2026-08-05 |
| DL-067 | SLA Constitution (satu konstitusi resmi) | Timeline | Approved | BO-002 Option A | 2026-08-05 |
| DL-068 | Manager Business Persona; Workspace deferred | UX | Approved | BO-003 Option A | 2026-08-05 |
| DL-069 | UX Package status synchronization | UX / Governance | Approved | BO-004 Option A | 2026-08-05 |

**Rekap jumlah per kategori:** Business 11 · Organization 3 · Timeline 6 · Workflow 5 · UX 4 · Architecture 16 · Governance 8 · Security 6 · Reporting 3 · Audit 3 — **total 65 keputusan**.

---

## 5. Decision Dependency Matrix (Deliverable 3)

Legenda hubungan:
**⤒ depends-on** = keputusan ini tidak berdiri tanpa keputusan itu · **⤓ enables** = keputusan ini membuka/menjadi prasyarat bagi keputusan itu · **⊘ constrains** = keputusan itu membatasi ruang gerak keputusan ini · **⇄ pairs-with** = paket terkoordinasi · **⊗ supersedes** = menggantikan sebagian/seluruhnya.

| DL | ⤒ Depends on | ⤓ Enables | ⊘ Constrained by | ⇄ / ⊗ |
|---|---|---|---|---|
| DL-001 | — | DL-027, DL-028, DL-029 | DL-046, DL-047 | ⊗ PDS-000, UX-001 P-01/P-04 |
| DL-002 | — | DL-003, DL-050 | DL-046 | ⊗ KAK |
| DL-003 | DL-002 | DL-023, DL-024 | — | — |
| DL-004 | DL-002, DL-003 | DL-005, DL-015, DL-019, DL-064 | — | ⊗ `[TBD]` BR-CAT-001 |
| DL-005 | DL-004 | DL-016, DL-017, DL-019 | — | ⊗ `[TBD]` SLA/NFR |
| DL-006 | DL-002 | DL-012, DL-015 | DL-046 (domain protection) | — |
| DL-007 | DL-002 | DL-008 | DL-002 | ⊗ DEC-001 (sebagian) |
| DL-008 | DL-007 | DL-009, DL-010 | DL-002 | ⊗ DEC-007 (sebagian) |
| DL-009 | DL-008 | DL-011, DL-017 | DL-002 | ⊗ DEC-008 (sebagian) |
| DL-010 | DL-007 | DL-011 | DL-002 | ⊗ DEC-007 (sebagian) |
| DL-011 | DL-009, DL-010 | DL-017, DL-024 | DL-002 | — |
| DL-012 | DL-006, DL-039 | DL-065 | DL-044 (FRD Batch-1 LOCKED), DL-048 | menunggu countersign Board |
| DL-013 | DL-039 | DL-014, DL-015, DL-042 | DL-048 (C-7) | ⇄ DL-039, DL-040 |
| DL-014 | DL-013 | DL-042, unlock Mode B (C-B6-3) | DL-049 | ⇄ DL-041, DL-042 |
| DL-015 | DL-004, DL-013, DL-056 | — | DL-046 (Mode A only) | — |
| DL-016 | DL-005 | DL-017, DL-018, DL-060 | — | — |
| DL-017 | DL-016 | DL-018, DL-060 | DL-021 (tanpa scheduler) | — |
| DL-018 | DL-017 | DL-061 | — | — |
| DL-019 | DL-004, DL-005 | DL-020, DL-021 | — | — |
| DL-020 | DL-019, DL-030 | DL-021 | DL-035 | — |
| DL-021 | DL-020 | (implementasi FR-030 — Deferred) | DL-035, DL-046 | — |
| DL-022 | DL-034 | DL-023, DL-024, DL-051 | — | ⊗ AC FRD-002 §6, alias `cases:transition` |
| DL-023 | DL-003, DL-022 | DL-024, DL-044 | DL-044 | ⊗ klaim SoT tunggal Case |
| DL-024 | DL-023 | DL-052 | DL-044, DL-046 | ⊗ OQ-CM-B1-004 |
| DL-025 | DL-026 | DL-065 | — | ⇄ DL-056 (ADR-008) |
| DL-026 | — | DL-025, DL-061, DL-064 | — | — |
| DL-027 | DL-001, DL-046, DL-047 | DL-028 | DL-044 (Dual-SoT) | — |
| DL-028 | DL-027 | — | DL-047 (gate capability) | — |
| DL-029 | DL-045 | — | — | ⊗ status OPEN OD-FE-009 |
| DL-030 | — | DL-035, DL-020, DL-060 | — | — |
| DL-031 | — | DL-051 | — | pola dipakai ulang DL-014 |
| DL-032 | — | DL-033, DL-034, DL-043 | — | ⊗ sebagian OQ-002 |
| DL-033 | DL-032 | — | — | catatan: CQRS ditunda (OQ-003) |
| DL-034 | DL-032 | DL-022, DL-044 | — | ⊗ konvensi penamaan lama |
| DL-035 | DL-030 | DL-051 | DL-046 (larangan framework generik) | — |
| DL-036 | DL-054, DL-055 | DL-058, DL-059 | DL-055 (fail-fast) | — |
| DL-037 | DL-050 | DL-038, DL-045 | — | — |
| DL-038 | DL-037 | DL-045 | DL-043 (konflik tree), DL-048 (BR-007) | konflik terbuka OD-FE-001 |
| DL-039 | DL-048 | DL-013, DL-040, DL-041, DL-042, DL-057 | DL-048 (C-1/C-3/C-7) | ⇄ DL-040 |
| DL-040 | DL-039, DL-048 | DL-041, DL-042 | DL-048 (C-3), DL-049 (C-B6-4) | ⇄ DL-039 |
| DL-041 | DL-040 | DL-042, DL-059 | DL-049 (C-B6-1/2/5) | ⇄ DL-042, DL-014 |
| DL-042 | DL-040, DL-041 | (AuthZ Mode B) | DL-049 | ⇄ DL-014 |
| DL-043 | DL-032 | DL-045, DL-052 | DL-038 (ADR-013 aktif) | ⊗ asumsi tree CI lama |
| DL-044 | DL-023, DL-034 | DL-051, DL-052, DL-027 | DL-046 (no force-merge) | butuh Retirement DEC |
| DL-045 | DL-037, DL-043 | DL-029 | DL-038, DL-048 | ⊗ OD-FE-003/008/009/010 |
| DL-046 | DL-048, DL-049 | seluruh keputusan delivery | Board & ADR (subordinasi) | — |
| DL-047 | DL-046 | DL-027, DL-028 | — | — |
| DL-048 | — | DL-039, DL-040, DL-049 | — | ⊗ disposisi BR-005/BR-006 |
| DL-049 | DL-048 | DL-041, DL-042, DL-014 | — | ⊗ disposisi Proposed ADR-016/017/018 |
| DL-050 | DL-002 | DL-032, DL-037, DL-063 | — | ⊗ "GO tanpa syarat" |
| DL-051 | DL-035, DL-044 | DL-052 | DL-046 | ⊗ butir U-1 DEC-006 |
| DL-052 | DL-024, DL-051 | — | DL-044 (dual SoT tetap) | — |
| DL-053 | — | keterbacaan DL-044, DL-051, DL-058 | — | — |
| DL-054 | — | DL-055 | DL-036 (larangan shared env) | relasi ADR-012 **Pending** |
| DL-055 | DL-054 | DL-036, DL-057, DL-058, DL-059 | DL-049 (C-B6-6) | relasi ADR-007 **Pending** |
| DL-056 | — | DL-015, DL-042, DL-065 | — | ⇄ DL-025 (ADR-008) |
| DL-057 | DL-039, DL-055 | — | DL-048 | — |
| DL-058 | DL-055 | DL-059 | DL-046, DL-053 | ⊗ framing "SSO sementara" |
| DL-059 | DL-058, DL-041 | (Mode B handoff) | DL-046, DL-048 (C-7) | ⊗ asumsi apex = Enterprise |
| DL-060 | DL-016, DL-017, DL-030 | DL-061, DL-062 | — | — |
| DL-061 | DL-018, DL-060 | DL-062 | DL-026 (dashboard read-only) | — |
| DL-062 | DL-060, DL-061 | — | DL-001 (persona Manager) | — |
| DL-063 | DL-050 | DL-064, DL-065 | — | ⊗ status Open OQ-007 |
| DL-064 | DL-004, DL-026 | DL-065 | — | ⊗ `[TBD]` BR-CP-02 |
| DL-065 | DL-025, DL-056, DL-063 | — | — | — |
| DL-066 | DL-002, DL-007…011, DL-012 | BC Lingkup | DL-067 (lifecycle bersama) | ⊗ OOS Regional/WO/Calendar/Mode B |
| DL-067 | DL-005, DL-016…019, DL-024 | BC SLA | DL-018 (timeline events) | ⊗ unlock runtime CAP-006 |
| DL-068 | DL-001, DL-062 | BC Aktor | DL-069 | ⊗ M-26 delivery |
| DL-069 | DL-001, DL-068 | Review UX paket | — | ⊗ klaim READY prematur |

### 5.1 Rantai dependensi kritis

1. **Rantai identitas enterprise:** DL-048 → DL-039 → DL-040 → DL-041 → DL-042, dengan DL-013/DL-014 sebagai cabang organisasi dan DL-049 sebagai gerbang kondisi. **Seluruh rantai ini CLOSED untuk implementasi** (C-7 / C-B6-1).
2. **Rantai dual SoT:** DL-003 → DL-023 → DL-044 → DL-051 → DL-052; berakhir tanpa Retirement DEC (terbuka).
3. **Rantai SLA:** DL-004 → DL-005 → DL-016 → DL-017 → DL-018 → DL-060 → DL-061; CAP-006 (DL-019 → DL-020 → DL-021) adalah jalur **terpisah** yang belum bertemu jalur DEC-012/013 (BQ-CAP006-15).
4. **Rantai lingkup appointment:** DL-002 → DL-007 → DL-008 → DL-009 → DL-010 → DL-011; setiap langkah adalah supersession parsial yang eksplisit.
5. **Rantai UX:** DL-001 → (PDS-001 → PWDM-001 → IA-001 → NAV-001 → WF-000 → WF-PLAN-001 → WF-001-01), berjalan paralel dengan DL-027 → DL-028 pada jalur CWX.

---

## 6. Keputusan yang masih perlu dibahas (Deliverable 4)

Daftar ini **bukan** keputusan. Isinya: butir yang berstatus Open/Proposed/Pending/Deferred, konflik terdaftar, dan kekosongan yang ditemukan saat konsolidasi. Semua diambil dari status yang tertulis di repositori — tidak ada yang disimpulkan sendiri.

### 6.1 Berstatus Proposed / Open (menunggu Accept)

| # | Topik | Status tertulis | Pemilik | Kenapa penting bagi BC-000 |
|---|---|---|---|---|
| M-01 | **Descendant org scope untuk AuthZ** (O-06) | 🟡 Proposed — DEC-021 (O-06) v0.1; aturan interim: **tanpa ekspansi descendant**, pakai referensi eksact, ambigu → deny | Solution Architect / Business Owner | Menentukan seberapa luas seorang pengguna melihat unit di bawahnya — aturan otorisasi bisnis inti |
| M-02 | **Upstream org restructure / orphan remediation** (O-07) | 🟡 Proposed — DEC-022 v0.1; interim: pertahankan referensi historis + fail-closed untuk aksi ber-scope baru | Solution Architect / Business Owner | Menentukan nasib komplain yang mereferensikan unit yang sudah dibubarkan |
| M-03 | **Channel app: fase 1 atau hanya integration boundary?** | OQ-001 **Open**, target keputusan TBD | Business Owner | Menentukan kanal masuk komplain yang termasuk lingkup modul |
| M-04 | **Konflik stack frontend** (ADR-013 Vite vs produksi Next.js) | OD-FE-001 **OPEN**, disposisi *Move to ADR*; Board melarang supersession lewat dokumen FE (BR-007) | Architecture Board / CTO / Frontend Lead | Dua pernyataan resmi tentang stack yang sama; memblokir klaim "standar stack frontend tunggal" |
| M-05 | **Protokol autentikasi enterprise** | OD-FE-002 **OPEN**; gated pada protocol ADR + Board unlock | Security Architect / Frontend Lead / Platform | Menentukan bagaimana modul dimasuki dari portal Enterprise |
| M-06 | **Aktivasi Technical Standards** | OD-FE-004 **OPEN** (menunggu OD-FE-001) | Tech Lead | Standar teknis belum punya SoT yang aktif |
| M-07 | **Konsolidasi spesifikasi UX** | OD-FE-005 **OPEN** | UX Lead / ECMF PO | Beririsan langsung dengan paket UX Foundation (M-11) |
| M-08 | **Library state/cache platform** | OD-FE-006 **OPEN** | Frontend Lead | Belum ada keputusan; ditunggu sampai muncul kebutuhan nyata |
| M-09 | **ADR Infrastruktur / deployment modul** | OD-FE-007 **OPEN**, disposisi *Move to ADR* | Infrastructure / Platform / Solution Architect | Prasyarat topologi modul saat Mode B |
| M-10 | **Relasi ADR-007 ↔ ADR-012** | **Pending** (C-B6-6); brief disposisi masih v0.1 | Architecture Board | Dua ADR autentikasi hidup berdampingan tanpa relasi formal (supersede? koeksistensi berfase?) |

### 6.2 Menunggu persetujuan formal atas dokumen yang sudah ditulis

| # | Topik | Status tertulis | Catatan |
|---|---|---|---|
| M-11 | **Paket UX Foundation** (PDS-001 · PWDM-001 · IA-001) + turunannya (NAV-001, WF-000, WF-PLAN-001, WF-001-01) | **DRAFT — status §2 disinkronkan (DL-069)**; belum READY FOR APPROVAL; Review ulang pasca-merge masih wajib | DL-001 merge Approved; DL-069 menutup inkonsistensi status; **isi** turunan belum mengikat sampai paket Approved |
| M-12 | **DEC-F4 countersign Architecture Board** | Berkas DEC-F4 🟡 *Proposed — awaiting formal DEC approval*; countersign pack 🟡 *Ready for countersign* | Keputusan bisnis F4…F4.5 sudah **Locked** oleh Business Owner; lingkup escalation Mode A dikunci DL-066; jalur countersign Board belum tertutup (lih. DL-012) |
| M-13 | **Retirement DEC untuk dual SoT** | Belum ada; disyaratkan eksplisit oleh DL-044, DL-051, DL-052, dan Forbidden Behavior DL-046 | Tanpa ini, dua namespace `/api/v1/complaints` dan `/api/v1/cm` tetap hidup berdampingan tanpa batas waktu |
| M-14 | **Resolution unlock Mode B** | Belum ada; disyaratkan C-B6-1 + C-B6-3 (prasyarat gap model organisasi) + kesiapan operasional | Seluruh rantai DL-039…DL-042 tetap desain sampai ada Resolution ini |

### 6.3 Ditunda secara sengaja (Deferred by decision) — perlu keputusan lanjutan bila diaktifkan

| # | Topik | Sumber penundaan |
|---|---|---|
| M-15 | Pause/Resume SLA (out of scope CAP-006 v1) | BQ-CAP006-06 (DL-019) |
| M-16 | Aktivasi Working Day / kalender kerja (saat ini 24x7) | BQ-CAP006-02 (DL-019), BR-ECMF-05 (DL-004) |
| M-17 | Diferensiasi target SLA per case type | BQ-CAP006-14 (DL-019), DL-005 |
| M-18 | Runtime konkret CAP-006 (scheduler/job/poll/worker) | ADR-CAP006-001 / B2-22 / B2-24 (DL-020, DL-021) |
| M-19 | Pemilihan message broker | ADR-009 + Addendum G2 (DL-035, DL-051) |
| M-20 | Platform deployment PROD (managed container vs Kubernetes) | ADR-010 §4 (DL-036) |
| M-21 | Reopen `CLOSED→REOPENED` + EVT-007 (masih Proposed) | DEC-006 U-1 → DEC-021 G2 (DL-022, DL-051) |
| M-22 | Read-audit (audit-on-read) | OQ-007 (DL-063) |
| M-23 | Integrasi Customer Master nyata / API-010 | ACR-002, G2-S2 (DL-031, DL-051) |
| M-24 | Kebijakan override maksimum Case per Complaint (>5) | BQ-003 (DL-024) |
| M-25 | Assigned User (assignment level user, bukan unit) | BQ-006 (DL-024) |
| M-26 | Dashboard untuk Manager/Executive | BQ-CAP007-04 (DL-062) — v0.1 Supervisor-only |
| M-27 | Kolom FR-030 pada dashboard | BQ-CAP007-05 (DL-062) |
| M-28 | Otorisasi tag rilis `v1.2.0` | REL-SEC-001 **NO-GO** (DL-052) |
| M-29 | Multi-tenant packaging / isolasi multi-org ECMP | Non-decision eksplisit ADR-014 (DL-039) |
| M-30 | Observability penuh (metrik/APM, Prometheus/Grafana/Sentry) | G2-S3, TS-OBS-001 masih Draft (DL-051) |

### 6.4 Konflik & kekosongan terdaftar yang ditemukan saat konsolidasi

| # | Temuan | Bukti | Rekomendasi tindakan (bukan keputusan) |
|---|---|---|---|
| M-31 | **Dua definisi Case state machine** hidup berdampingan | DOM-ECMF-003 (Definition A) vs BR-CM-CAT-001 (Definition B) | Sudah **disengaja** lewat DL-023 (Option O3); yang belum ada adalah rencana konvergensi — terkait M-13 |
| M-32 | **Tabrakan ID DEC-020 dan DEC-021** | DEC ID Collision Register | Register berstatus *CLOSED — Board Option A* dengan "Action taken: **documented only, no renumber**", sementara "Option A" pada tabel opsi di berkas yang sama berbunyi *renumber G2 → ID bebas berikutnya*. **Kedua pernyataan ini tidak konsisten** — perlu klarifikasi Board sebelum DL-000/BC-000 mengutip DEC-021 tanpa kualifikasi |
| M-33 | **`DEC-017` tidak ada di repositori** | Urutan berkas `27 Project Decisions/` melompat DEC-016 → DEC-018 | Konfirmasi apakah nomor sengaja dilewati atau berkasnya hilang |
| M-34 | **Manager belum punya padanan peran teknis** di Authorization | PDS-001 §1 catatan peran teknis | **Persona sah (DL-068)**; gap role teknis tetap terbuka untuk DEC Authorization — tidak memblokir pasal Aktor BC |
| M-35 | **Kontrak identitas belum diverifikasi bilateral** | ADR-015 di bawah C-3 adalah *Bilateral Contract*; repositori tidak memuat artefak dari aplikasi enterprise nyata (issuer produksi, spesifikasi entitlement/user directory/org, metode integrasi portal); seluruh referensi IdP menunjuk realm lokal yang di-provision ECMP sendiri | Sebelum pekerjaan identitas apa pun dinilai atau direncanakan, pastikan kontrak nyata dari pemilik platform sudah diperoleh |
| M-36 | **Dua jalur SLA berjalan paralel** | DEC-012/013 (implementasi lab) vs CAP-006 (FRD-005 LOCKED) — BQ-CAP006-15 menyatakan keduanya jalur terpisah dan DEC-012/013 **bukan** pemenuhan CAP-006 | Perlu keputusan konvergensi saat runtime CAP-006 diaktifkan (terkait M-18) |
| M-37 | **Frontend produksi berjalan di luar ADR stack yang aktif** | DL-038 vs DL-043 | Sama dengan M-04; dicatat terpisah karena berdampak pada CI dan rilis, bukan hanya standar |

---

## 7. Dokumen repositori yang terdampak per keputusan (Deliverable 5)

### 7.1 Ringkas: DL → dokumen/area utama

Daftar lengkap per keputusan ada pada field **Affected Documents** masing-masing record (Bagian 3). Tabel ini adalah ringkasan navigasi.

| DL | Dokumen / area utama yang terdampak |
|---|---|
| DL-001 | `docs/ux/*` (PDS-000/001, PWDM-001, IA-001, NAV-001, WF-000, WF-PLAN-001, WF-001-01, UX-FOUNDATION-000) · `12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` |
| DL-002 | `01 Business Blueprint/` · `03 Functional Requirements/` · `02 Business Rules/` · `07 API Catalog/` · `08 Event Catalog/` · `26 Traceability/` |
| DL-003 | `02 Business Rules/` (Sprint01 + BR-CAT-001) · `26 Traceability/` · `13 Test Strategy/` |
| DL-004 | `02 Business Rules/ECMP_Business_Rules_v1.0.md` · `03 Functional Requirements/` · `11 SLA and KPI Matrix/` · `10 Security and Access Standards/` |
| DL-005 | `11 SLA and KPI Matrix/` · `04 Solution Architecture/` · `07 API Catalog/` |
| DL-006 | `06 Data Dictionary/` · `20 Domain Architecture/ECMF/CASE_AGGREGATE.md` · `07 API Catalog/` |
| DL-007…DL-011 | `07 API Catalog/` (API-305…310) · `08 Event Catalog/` · `27 Project Decisions/DEC-007…011` |
| DL-012 | `18 Architecture Governance/reviews/ECMP_DEC_F4_*` · `26 Traceability/ECMP_IMPACT_DEC_F4_v1.0.md` · `02 Business Rules/…Complaint_Management_Module_v1.0.md` |
| DL-013 | `05 ADR/ECMP_ADR_014_*` · `05 ADR/ECMP_ADR_018_*` · `06 Data Dictionary/` · `09 Integration Catalog/` |
| DL-014 | `05 ADR/ECMP_ADR_018_*` · `09 Integration Catalog/` · `10 Security…/` (SEC-ORG-SYNC-001) · `18 Architecture Governance/…MODE_B_ORG_GAP_PREREQUISITE…` |
| DL-015 | `18 Architecture Governance/ECMP_EBS_001_*` · `docs/governance/ECMP-EBS-001.md` · `deploy/evidence/EBS-001_*` |
| DL-016…DL-018 | `11 SLA and KPI Matrix/` · `07 API Catalog/` (API-314…317, API-209) · `08 Event Catalog/` · `27 Project Decisions/DEC-012…014` |
| DL-019 | `deploy/evidence/B2-15_*`, `B2-16_*` · `03 Functional Requirements/` (FRD-005) · `11 SLA and KPI Matrix/` |
| DL-020 · DL-021 | `05 ADR/ADR-CAP006-001_*`, `ARC-CAP006-001_*`, `ARC-CAP006-002_*` · `20 Domain Architecture/` · `deploy/evidence/B2-19…B2-24` |
| DL-022 | `07 API Catalog/` · `08 Event Catalog/events.yaml` · `10 Security…/` (SEC-RAM-001) · `13 Test Strategy/` |
| DL-023 | `18 Architecture Governance/reviews/ECMP_DEC_BQ001_*` · `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` · `02 Business Rules/` · `03 Functional Requirements/` · `docs/product/CAP-02_*` |
| DL-024 | `18 Architecture Governance/reviews/ECMP_DEC_ModeA_*`, `ECMP_DM_ModeA_*` · `03 Functional Requirements/` · `07 API Catalog/` · `26 Traceability/` |
| DL-025 · DL-065 | `05 ADR/ECMP_ADR_008_*` · `08 Event Catalog/` · `02 Business Rules/` · `17 Compliance/` |
| DL-026 · DL-064 | `05 ADR/ECMP_ADR_003_*` · `02 Business Rules/` · `04 Solution Architecture/` · `17 Compliance/` |
| DL-027 · DL-028 | `18 Architecture Governance/ECMP_CWX_*` · `docs/governance/ECMP-CWX-*` · `ECMP-EPIC-CW-001-CLOSURE.md` · `deploy/evidence/EPIC-CW-001_*` |
| DL-029 · DL-045 | `docs/frontend/*` (ARCHITECTURE v1.2, DEVELOPMENT_STANDARDS, CI_QUALITY_POLICY, OPEN_DECISIONS) · `docs/UI_BASELINE.md` |
| DL-030 · DL-035 | `05 ADR/ECMP_ADR_001_*`, `ECMP_ADR_009_*` (+Addendum) · `08 Event Catalog/` · `04 Solution Architecture/` |
| DL-031 | `05 ADR/ECMP_ADR_002_*` · `09 Integration Catalog/` · `06 Data Dictionary/` |
| DL-032 · DL-033 · DL-034 | `05 ADR/ECMP_ADR_004/005/006_*` · `21 Technical Standards/` · `22 Engineering Handbook/` · `07 API Catalog/` |
| DL-036 | `05 ADR/ECMP_ADR_010_*` · `14 Deployment Standards/` · `15 Operations Runbook/` · `deploy/` |
| DL-037 · DL-038 | `05 ADR/ECMP_ADR_011_*`, `ECMP_ADR_013_*` · `12 UI UX Spec/` · `21 Technical Standards/` |
| DL-039 · DL-057 | `05 ADR/ECMP_ADR_014_*` · `10 Security…/` (SEC-PWD-001, SEC-AUTH-001) · `18 Architecture Governance/…BOARD_004…` |
| DL-040 | `05 ADR/ECMP_ADR_015_*` · `10 Security…/` · `docs/frontend/OPEN_DECISIONS.md` |
| DL-041 · DL-042 | `05 ADR/ECMP_ADR_016_*`, `ECMP_ADR_017_*` · `18 Architecture Governance/…BOARD_006…`, `…AUDIT_K5…` |
| DL-043 | `27 Project Decisions/DEC-019_*` · `.github/workflows/` · `backend/pyproject.toml` · `docs/releases/v1.0.0.md` |
| DL-044 | `27 Project Decisions/DEC-020_…Namespace_Remapping…` · `03 Functional Requirements/…Batch1_v1.1.md` · `02 Business Rules/` · `18 Architecture Governance/…IMPLEMENTATION_001…` |
| DL-046 · DL-047 | `18 Architecture Governance/ECMP_CONSTITUTION_001_*`, `ECMP_MASTER_PROMPT_001_*` · `ECMP_GOV_001_*` · `docs/governance/*` · `CLAUDE.md` · `.cursor/rules/` |
| DL-048 · DL-049 | `18 Architecture Governance/ECMP_PROGRAM_BOARD_004/005/006_*` · `05 ADR/ADR_INDEX.generated.md` · `docs/architecture/adr-index.md` |
| DL-050 | `27 Project Decisions/DEC-002_*` · `ai/sprint/Sprint-01.md` · `ai/sprint/IMPLEMENTATION_READINESS_ROADMAP.md` · `.github/workflows/backend-ci.yml` |
| DL-051 | `27 Project Decisions/DEC-021_G2_*` · `05 ADR/…ADR_009_Addendum_G2…` · `deploy/evidence/G2_Mini_Gate_Mode_A_*` · `implementation/backend/REGRESSION_PACK_G2.md`, `DEV_RUNBOOK.md` |
| DL-052 | `18 Architecture Governance/ECMP_PROGRAM_CAP008_000…010` · `ai/sprint/CAP008_ROADMAP_RESET_v1.0.md` · `deploy/evidence/CAP-008_SoT_Closure_*` |
| DL-053 | `deploy/evidence/DEC_ID_Collision_Register_*` · `27 Project Decisions/README.md`, `DEC-020_*`, `DEC-021_*`, `OPEN_QUESTIONS.md` |
| DL-054 · DL-055 | `05 ADR/ECMP_ADR_007_*`, `ECMP_ADR_012_*` · `10 Security…/ECMP_Target_Authentication_Architecture_v1.0.md` · `14 Deployment Standards/` |
| DL-056 | `05 ADR/ECMP_ADR_008_*` · `10 Security…/` (SEC-RAM-001) · `06 Data Dictionary/` · `docs/frontend/FRONTEND_ARCHITECTURE_v1.2.md` |
| DL-058 · DL-059 | `27 Project Decisions/DEC-020_Lab_Auth_*`, `DEC-023_*` · `deploy/` (Caddyfile, compose, APEX checklist) · `deploy/evidence/Apex_Landing_*` |
| DL-060 · DL-061 | `27 Project Decisions/DEC-015_*`, `DEC-016_*` · `07 API Catalog/` (API-318, API-319) · `docs/domain/kpi.md`, `docs/domain/dashboard.md` |
| DL-062 | `deploy/evidence/B2-11…B2-14` |
| DL-063 | `27 Project Decisions/OPEN_QUESTIONS.md`, `DEC-002_*` · `03 Functional Requirements/ECMP_FRD_ECMF_v0.1.md` §9 |

### 7.2 Indeks terbalik: dokumen/folder → keputusan yang mengikatnya

| Dokumen / folder | Keputusan yang mengikat |
|---|---|
| `01 Business Blueprint/` | DL-002 · DL-030 |
| `02 Business Rules/` | DL-002 · DL-003 · DL-004 · DL-006 · DL-012 · DL-023 · DL-025 · DL-026 · DL-044 · DL-063 · DL-064 · DL-065 |
| `03 Functional Requirements/` | DL-002 · DL-004 · DL-019 · DL-023 · DL-024 · DL-044 · DL-063 |
| `04 Solution Architecture/` | DL-005 · DL-026 · DL-030 · DL-035 · DL-039 |
| `05 Architecture Decision Records/` | DL-020 · DL-021 · DL-025 · DL-026 · DL-030…DL-042 · DL-048 · DL-049 · DL-054 · DL-055 · DL-056 · DL-057 |
| `06 Data Dictionary/` | DL-002 · DL-006 · DL-013 · DL-025 · DL-031 · DL-056 |
| `07 API Catalog/` | DL-002 · DL-005 · DL-006 · DL-007…DL-011 · DL-016…DL-018 · DL-022 · DL-024 · DL-032 · DL-034 · DL-060 · DL-061 |
| `08 Event Catalog/` | DL-002 · DL-007…DL-011 · DL-018 · DL-019 · DL-022 · DL-025 · DL-030 · DL-032 · DL-035 |
| `09 Integration Catalog/` | DL-013 · DL-014 · DL-031 |
| `10 Security and Access Standards/` | DL-004 · DL-014 · DL-022 · DL-039 · DL-040 · DL-041 · DL-042 · DL-054 · DL-055 · DL-056 · DL-057 · DL-065 |
| `11 SLA and KPI Matrix/` | DL-004 · DL-005 · DL-016 · DL-017 · DL-019 · DL-060 |
| `12 UI UX Spec/` | DL-001 · DL-037 · DL-038 |
| `13 Test Strategy/` | DL-003 · DL-022 |
| `14 Deployment Standards/` | DL-036 · DL-054 · DL-055 |
| `15 Operations Runbook/` | DL-036 |
| `17 Compliance/` | DL-064 · DL-065 |
| `18 Architecture Governance/` | DL-012 · DL-013 · DL-014 · DL-015 · DL-023 · DL-024 · DL-027 · DL-039…DL-042 · DL-044 · DL-046…DL-049 · DL-052 |
| `20 Domain Architecture/` | DL-006 · DL-021 · DL-023 |
| `21 Technical Standards/` | DL-032 · DL-033 · DL-034 · DL-037 · DL-038 |
| `22 Engineering Handbook/` | DL-033 |
| `26 Traceability/` | DL-002 · DL-003 · DL-012 · DL-024 |
| `27 Project Decisions/` | DL-002…DL-011 · DL-016…DL-018 · DL-022 · DL-043 · DL-044 · DL-050 · DL-051 · DL-053 · DL-058 · DL-059 · DL-060 · DL-061 · DL-063 |
| `docs/ux/` | DL-001 |
| `docs/frontend/` | DL-029 · DL-038 · DL-040 · DL-045 · DL-056 |
| `docs/governance/` | DL-015 · DL-027 · DL-028 · DL-046 · DL-047 |
| `docs/domain/` | DL-060 · DL-061 |
| `docs/product/` | DL-023 |
| `docs/releases/` | DL-043 |
| `deploy/` + `deploy/evidence/` | DL-015 · DL-019 · DL-021 · DL-028 · DL-036 · DL-051 · DL-052 · DL-053 · DL-058 · DL-059 · DL-062 |
| `implementation/backend/`, `implementation/frontend/` | DL-033 · DL-043 · DL-044 · DL-051 |
| `.github/workflows/` | DL-036 · DL-043 · DL-050 |
| `ai/sprint/` | DL-050 · DL-052 |
| `CLAUDE.md`, `.cursor/rules/` | DL-046 |

---

## 8. Catatan penutup untuk BC-000

Tiga hal yang perlu dibawa ke milestone berikutnya:

1. **Yang mengikat vs yang didesain.** Seluruh rantai enterprise (DL-013, DL-014, DL-039…DL-042, DL-057) berstatus *Accepted Architecture — Implementation Deferred*. BC-000 boleh mengutipnya sebagai arah, **tidak** sebagai kemampuan yang sudah ada.
2. **Dual SoT adalah keadaan yang disengaja**, bukan utang tak terkelola (DL-023, DL-044) — namun belum punya rencana pengakhiran (M-13).
3. **Sebagian besar substansi UX belum berstatus Approved** (M-11). Hanya keputusan merge persona (DL-001) dan konstitusi CWX (DL-027) yang dapat dipakai sebagai dasar mengikat saat ini.

---

## Related

- `18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md`
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_004_Architecture_Board_Resolution_v1.0.md`
- `18 Architecture Governance/ECMP_PROGRAM_BOARD_006_Architecture_Board_Resolution_v1.0.md`
- `05 Architecture Decision Records/ADR_INDEX.generated.md`
- `27 Project Decisions/README.md` · `27 Project Decisions/OPEN_QUESTIONS.md`
- `docs/frontend/OPEN_DECISIONS.md`
- `docs/ux/UX-FOUNDATION-000-Complaint-Module-UX-Foundation.md`

## Future Work

BC-000 (Business Constitution) — disusun pada milestone berikutnya dengan **DL-000 sebagai satu-satunya sumber**. Di luar ruang lingkup dokumen ini.

---

*End of DL-000.*
