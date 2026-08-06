# BO-WS-000 — Business Owner Resolution Workshop (Priority 1)

| Field | Value |
|---|---|
| Document ID | BO-WS-000 |
| Title | Business Owner Resolution Workshop — Priority 1 |
| Version | 1.0 |
| Date | 2026-08-05 |
| Milestone | Governance Phase 0 — G0.2C (Workshop) |
| Status | **CLOSED — Business Owner P1 decisions recorded 2026-08-05** |
| Inputs | DL-000 · DRR-000 · BO-000 (+ artefak yang dirujuk) |
| Purpose | Memungkinkan Business Owner menyetujui seluruh keputusan P1 dalam satu workshop |
| Does not | Memutuskan bisnis · memodifikasi DL/DRR/BO-000 · membuat BC-000 · mengubah kode · menginfer approval |

**Cara pakai:** Untuk tiap topik, pilih Option A / B / C, isi slot keputusan di akhir bagian. Setelah lima slot terisi, BC-000 drafting boleh dimulai (lihat Governance Readiness).

---

## Merge recommendation (bukan merge otomatis)

| Topik | Apakah isu yang sama? | Rekomendasi |
|---|---|---|
| **BO-001** + **BO-005** | Keduanya = carve-out terhadap **DEC-001 / DL-002** (lingkup yang semula OOS) | **Boleh digabung** menjadi satu keputusan BO berjudul *“DEC-001 Scope Consolidation”* dengan dua klausul (Escalation · Appointment). Tetap dua suara terpisah jika BO ingin menolak satu dan menyetujui yang lain. |
| BO-002 | Berdiri sendiri (aturan SLA) | Jangan digabung |
| BO-003 + BO-004 | Berdekatan (persona vs status paket UX) tetapi **beda objek keputusan** | Jangan digabung; urutkan berurutan (lihat Approval Order) |
| BO-003 vs BO-011 (P3) | Manager persona vs aktivasi Executive/FR-030 | Jangan digabung di P1 |

*Tidak digabung di dokumen ini. BO memutuskan apakah menggabungkan suara BO-001+BO-005.*

---

# BO-001 — Head Office Escalation Scope

## Problem Statement

Baseline resmi (DEC-001) menyatakan Head Office escalation **di luar lingkup**, tetapi produk dan keputusan lain sudah memperlakukan eskalasi sebagai kapabilitas yang ada — tanpa DEC yang mencabut status out-of-scope itu. Tanpa disposisi Business Owner, pasal Lingkup pada Business Constitution tidak dapat ditulis secara benar.

## Current Repository Position

Eskalasi **dipakai** (model Cabang→Pusat, UI, SLA, prasyarat appointment) tetapi **belum diotorisasi sebagai pencabutan OOS** terhadap DEC-001. DEC-F4 terkunci di workshop bisnis, formalitas DEC masih Proposed.

## Repository Evidence

| Bukti | Isi |
|---|---|
| DEC-001 / DL-002 | “Branch Officer / Head Office escalation / Schedule Slot / Appointment / Work Order” = OOS sampai revisi Blueprint |
| DRR C-08 | Grep DEC-\*: eskalasi hanya sebagai *prasyarat*, bukan otorisasi lingkup |
| DEC-007…011 | Appointment & Final Resolution Approved; butuh escalation `APPROVED` |
| DEC-F4 / DL-012 | F4…F4.5 Locked; status berkas 🟡 Proposed |
| DEC-013 | Tahap SLA `escalation` |
| Constitution §3 | Modul menyediakan Escalation — batas kapabilitas, bukan DEC lingkup |

## Business Context

Ini keputusan **apa yang boleh diklaim sebagai lingkup produk complaint**, bukan keputusan teknis autentikasi atau Mode B. Business Owner adalah Approver DEC-001. Pola yang sudah dipakai untuk Appointment (partial supersession eksplisit) belum diterapkan ke eskalasi.

## Current Risks

- Konstitusi mengutip DEC-001 mentah → pernyataan lingkup **salah**.
- Konstitusi mengabaikan DEC-001 tanpa DEC baru → pelanggaran governance.
- Appointment & F4 bergantung pada eskalasi yang secara formal masih OOS.

## Available Options

### Option A

Cabut OOS “Head Office escalation” melalui DEC Business Owner. Batasi lingkup (minimal jalur Cabang → Pusat; tanpa Regional / Calendar / Work Order kecuali DEC terpisah).

### Option B

Tegakkan OOS. Eskalasi = non-normatif / lab hedge. Tidak masuk pasal Lingkup sebagai kapabilitas resmi.

### Option C

Ratifikasi retrospektif: akui bahwa F4 + rantai appointment sudah memberi otorisasi implisit; perilaku tidak diubah; terbitkan DEC pencatatan.

## Advantages

| Opsi | Keunggulan |
|---|---|
| A | Selaras praktik & F4; dasar kuat untuk konstitusi; pola sama Appointment |
| B | Patuh ketat teks DEC-001; memaksa pembersihan dulu |
| C | Biaya rendah; tutup gap cepat; lab tetap jalan |

## Disadvantages

| Opsi | Kelemahan |
|---|---|
| A | Perlu DEC + batas OOS yang jelas; mungkin ikut penertiban Blueprint/FRD |
| B | Bertentangan F4, appointment, SLA, UI; biaya rollback tinggi |
| C | Melemahkan disiplin supersession eksplisit |

## Recommended Option

**Option A** (atau **C** jika BO menilai hanya formalitas yang kurang). Option B hanya jika BO sengaja menarik eskalasi dari produk.

*Rekomendasi fasilitator — bukan keputusan.*

## Consequences

| Dimensi | A | B | C |
|---|---|---|---|
| **Business** | Eskalasi resmi terbatas | Eskalasi bukan janji produk | Sama A untuk perilaku |
| **UX** | Escalation Detail tetap normatif | UI dilabeli non-binding | Sama A |
| **Architecture** | Fondasi batch FRD eskalasi | Dual narasi lab vs baseline | Sama A, kutipan lebih longgar |
| **Domain** | Jalur Cabang→Pusat masuk lingkup | Domain tanpa eskalasi resmi | Sama A |
| **Implementation** | Tidak ubah kode sekarang; DEC dulu | Potensi penandaan/lab quarantine | Dokumentasi saja |
| **Governance** | Menutup C-08 | C-08 “tertutup” dengan biaya konflik artefak | Menutup C-08 secara pencatatan |

## Affected Artifacts

DEC-001 · DL-002 · DEC-F4 · DL-012 · DEC-007…011 · DEC-013 · BR-007 · API/Event Catalog · UI Escalation / NAV Supervisor · pasal Lingkup BC-000

## Future Scalability

| Opsi | Skala ke depan |
|---|---|
| A / C | Eskalasi jadi fondasi batch berikutnya; Regional/WO tetap terkunci |
| B | Fitur terkait jadi utang atau dibongkar sebelum skala |

## Business Owner Decision

| Field | Value |
|---|---|
| **Status** | **APPROVED** |
| Selected option | **A** |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Decision Summary | Head Office Escalation menjadi bagian resmi Complaint Lifecycle ECMP. Lingkup dibatasi pada Branch ↔ Head Office. Regional Office, Work Order, Calendar/Schedule, Mode B, dan integrasi enterprise tetap Out of Scope sampai keputusan governance baru. |
| Merge with BO-005 | **YES** — satu Scope Consolidation Mode A (lihat DL-066) |
| Notes / batas OOS yang dipertahankan | Regional · Work Order · Calendar/Scheduling · Mode B · Enterprise Integration |

---

# BO-002 — SLA Constitution

## Problem Statement

Ada dua (atau tiga) pernyataan aturan waktu layanan yang tampak saling meniadakan: Mode A **mengikat** kebijakan SLA tetapi **tidak menjalankan** jam hitung mundur; jalur Foundation **menghitung deadline dan menandai breach**; model bisnis CAP-006 terkunci tetapi runtime ditunda. Business Constitution tidak dapat menulis satu pasal Komitmen Layanan yang jujur tanpa kejelasan ruang berlaku.

## Current Repository Position

| Jalur | Perilaku | Status |
|---|---|---|
| Foundation | Deadline + BREACHED | DEC-012/013 Approved |
| Aggregate Mode A | Bind tanpa clock | BQ-005 LOCKED |
| CAP-006 | Model bisnis; runtime Deferred | FRD-005 LOCKED |

## Repository Evidence

| Bukti | Isi |
|---|---|
| DL-024 BQ-005 | Bind-without-clock Mode A |
| DL-016 / DL-017 | Snapshot due-at; evaluasi BREACHED/COMPLETED |
| DL-005 | Target numerik baseline (reversibel via DEC) |
| DL-019 | CAP-006 bisnis ditutup; 3 butir DEFERRED |
| BQ-CAP006-15 | Jalur DEC-012/013 ≠ pemenuhan CAP-006 |
| DEC-020 / dual SoT | Koeksistensi Foundation & Aggregate |

## Business Context

Ini keputusan **makna bisnis** “apakah jam SLA berjalan, di jalur mana, dan apa arti target numerik” — bukan keputusan memilih scheduler. Konvergensi mekanisme nanti milik Architecture Board; BO menetapkan apa yang boleh diklaim di konstitusi.

## Current Risks

- Operator/auditor tidak tahu apakah breach lab mengikat Mode A.
- Pasal SLA tampak kontradiktif → hilangnya kepercayaan pada konstitusi.
- Membuka ulang BQ Mode A yang residual ZERO tanpa niat sadar.

## Available Options

### Option A

Pemisahan eksplisit per jalur: Foundation clock berlaku; Mode A bind-without-clock sampai runtime CAP-006; target DL-005 = komitmen policy; CAP-006 = model target (bukan = DEC-012/013).

### Option B

Seragamkan: clock **tidak** berjalan di Mode A maupun Foundation sampai CAP-006 runtime; DEC-012/013 non-normatif bagi konstitusi.

### Option C

Seragamkan: clock **aktif** di Aggregate Mode A; revisi/cabut BQ-005; manfaatkan investasi DEC-012/013.

## Advantages

| Opsi | Keunggulan |
|---|---|
| A | Selaras dual SoT; tanpa rollback; tanpa buka ulang BQ pack |
| B | Satu kalimat konstitusi sederhana |
| C | Satu perilaku operasional di semua jalur |

## Disadvantages

| Opsi | Kelemahan |
|---|---|
| A | Dualitas SLA tetap sampai konvergensi |
| B | Mencabut makna normatif DEC yang sudah berjalan; dampak KPI/tes |
| C | Membuka keputusan Mode A terkunci; butuh otorisasi runtime |

## Recommended Option

**Option A.**

*Rekomendasi fasilitator — bukan keputusan.*

## Consequences

| Dimensi | A | B | C |
|---|---|---|---|
| **Business** | Klaim SLA per jalur jelas | Klaim “belum ada clock produk” | Klaim clock penuh Mode A |
| **UX** | Label ruang berlaku pada SLA/KPI | Sembunyikan/non-normatifkan breach lab | Tampilkan countdown Aggregate |
| **Architecture** | Mempertahankan dual track | Menekan Foundation ke non-normatif | Memaksa aktifkan clock Aggregate |
| **Domain** | Aturan waktu bergantung SoT | Aturan waktu ditunda | Aturan waktu seragam aktif |
| **Implementation** | Dokumentasi klausul | Penurunan status normatif lab | Perubahan FRD/OpenAPI Mode A |
| **Governance** | Menutup C-12 dengan kualifikasi | Menutup C-12 dengan biaya besar | Menutup C-12 dengan revisi BQ |

## Affected Artifacts

DL-005 · DL-004 · DL-016…019 · DL-024 BQ-005 · FRD-005 · SLA Matrix · API-314…318 · KPI · pasal Komitmen Layanan & Waktu BC-000

## Future Scalability

Option A menjaga pintu konvergensi CAP-006 tanpa memalsukan keadaan hari ini. Option B menunda skala metrik. Option C mempercepat keseragaman dengan risiko membuka ulang baseline Mode A.

## Business Owner Decision

| Field | Value |
|---|---|
| **Status** | **APPROVED** |
| Selected option | **A** |
| Explicit statement for constitution (BO draft) | ECMP menggunakan satu SLA Constitution resmi untuk seluruh Complaint Lifecycle. SLA dihitung berdasarkan aturan bisnis yang seragam; seluruh perubahan SLA wajib tercatat sebagai Timeline Events. Detail implementasi teknis mengikuti Business Constitution dan Business Rules. |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Notes | Berlaku Mode A. Konvergensi mekanisme runtime CAP-006 tetap follow-up Board/arsitektur (bukan membuka Mode B). |

---

# BO-003 — Manager Persona vs Dashboard

## Problem Statement

Model pengalaman menetapkan **Manager** sebagai salah satu dari tiga persona operasional dengan rumah kerja Dashboard, sementara keputusan bisnis dashboard v0.1 hanya mengotorisasi **Supervisor** dan menunda Manager. Konstitusi tidak boleh menjanjikan aktor tanpa kejelasan apakah yang dijamin adalah *persona bisnis* atau *workspace yang harus tersedia*.

## Current Repository Position

Manager ada di closed set UX; Dashboard = entry point Manager; delivery dashboard = Supervisor-only v0.1; role teknis Manager belum ada.

## Repository Evidence

| Bukti | Isi |
|---|---|
| DL-001 / PDS-001 | Closed set: Complaint Officer · Supervisor · Manager |
| NAV-001 / IA-001 | Manager: Login → Dashboard; zona Reference |
| BQ-CAP007-04 / DL-062 | Approve Supervisor-only v0.1; Defer Manager/Executive |
| FRD-006 · SEC-RAM | Aktor v0.1 = Supervisor unit-scoped |
| PDS-001 catatan | Manager belum punya padanan peran teknis |

## Business Context

Menentukan **siapa aktor bisnis modul** dan **apa yang dijanjikan kepada mereka pada v0.1**. Bukan keputusan membuat layar baru di workshop ini. Executive/FR-030 = backlog P3 terpisah.

## Current Risks

- Konstitusi mengklaim tiga persona seolah semua punya permukaan kerja resmi.
- Mengeluarkan Manager dari set memundurkan kerja UX yang baru diseragamkan.
- Memaksa Workspace sekarang membuka ulang CAP-007 yang sudah ditutup.

## Available Options

### Option A

Manager tetap di closed set sebagai **Business Persona**; Manager Workspace tetap **Deferred**; konstitusi menulis kualifikasi jujur (dashboard v0.1 = Supervisor).

### Option B

Manager Workspace **diwajibkan** sekarang; tarik deferral untuk Manager (bukan Executive); role + FRD sebelum pasal Persona tanpa kualifikasi deferral.

### Option C

Keluarkan Manager dari closed set sampai dashboard & role siap (sementara: dua persona).

## Advantages

| Opsi | Keunggulan |
|---|---|
| A | Pertahankan model persona; hormati CAP-007; konstitusi jujur |
| B | Closed set = kapabilitas nyata |
| C | Hanya klaim aktor yang punya permukaan kerja |

## Disadvantages

| Opsi | Kelemahan |
|---|---|
| A | Persona tanpa rumah kerja resmi — harus dijelaskan |
| B | Buka ulang CAP-007; tunda BC; melebar ke delivery |
| C | Cascade revisi seluruh paket UX; batalkan sebagian DL-001 |

## Recommended Option

**Option A.**

*Rekomendasi fasilitator — bukan keputusan.*

## Consequences

| Dimensi | A | B | C |
|---|---|---|---|
| **Business** | Tiga aktor; janji delivery Manager ditunda | Janji Workspace Manager aktif | Dua aktor sementara |
| **UX** | Model Manager tetap; label deferral | Rilis Dashboard Manager dipercepat | Revisi PDS→WF |
| **Architecture** | Role mapping nanti | Slot role + entitlement sekarang | Hapus asumsi Manager |
| **Domain** | Tidak berubah | Sama + permukaan agregat | Domain aktor menyempit |
| **Implementation** | Tidak wajib kode sekarang | Backlog M-26 + SEC-RAM | Dokumentasi UX besar |
| **Governance** | Menutup C-09 dengan kualifikasi | Menutup C-09 dengan delivery gate | Menutup C-09 dengan revisi persona |

## Affected Artifacts

PDS-001 · PWDM/IA/NAV/WF · DL-001 · DL-062 · FRD-006 · SEC-RAM · API dashboard · pasal Aktor BC-000

## Future Scalability

Option A menyisakan jalur Release pelaporan Manager (P2 wireframe) tanpa memaksa v0.1. Option B mempercepat skala agregat. Option C menunda skala persona sampai dibangun ulang.

## Business Owner Decision

| Field | Value |
|---|---|
| **Status** | **APPROVED** |
| Selected option | **A** |
| Manager in closed set? | **Yes** — Business Persona yang sah |
| Manager Workspace required now? | **No** — boleh ditunda; keberadaan persona tidak bergantung pada kesiapan UI |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Notes | Dashboard Manager/Executive delivery tetap Deferred (BQ-CAP007-04) sampai DEC baru |

---

# BO-004 — UX Package Status Synchronization

## Problem Statement

Dokumen payung UX Foundation menyatakan dua status berbeda untuk paket yang sama (READY vs Draft). Business Owner tidak dapat menyetujui paket yang statusnya tidak seragam, sehingga substansi pengalaman di luar prinsip yang sudah dikunci tidak dapat diangkat sebagai pasal mengikat.

## Current Repository Position

Paket baseline pasca-merge persona berada dalam keadaan **Draft menunggu Review ulang**; §2 payung masih salah menyebut sebagian dokumen READY FOR APPROVAL.

## Repository Evidence

| Dokumen | Status header / klausul |
|---|---|
| UX-FOUNDATION-000 header & §6 | Draft — BUKAN READY; READY sebelumnya **dicabut** |
| UX-FOUNDATION-000 §2 PWDM/IA | READY FOR APPROVAL *(inkonsisten)* |
| PDS-001 · PWDM-001 · IA-001 | Draft |
| NAV-001 · WF-000 · WF-PLAN · WF-001-01 | Draft |
| PDS-000 | Superseded (konsisten) |
| DL-001 · DL-027 | APPROVED — satu-satunya UX yang layak BC tanpa paket Approved |

## Business Context

Approver paket UX Foundation adalah Business Owner. Ini keputusan **kesiapan untuk Review/Approval**, bukan redesign layar. Tanpa sinkronisasi, klaim “closed set destinasi/zona” tidak mengikat.

## Current Risks

- Approve pada dokumen yang bilang Draft dan READY sekaligus.
- BC mengangkat substansi UX Draft sebagai norma.
- Review tidak dapat dimulai secara sah.

## Available Options

### Option A

Sinkronkan semua ke **Draft**; koreksi §2; jalankan Review; baru READY → Approval BO.

### Option B

Naikkan PWDM/IA ke READY sekarang; selaraskan §6; BO Approve segera.

### Option C

Biarkan inkonsistensi; tulis BC hanya dari DL-001/DL-027.

## Advantages

| Opsi | Keunggulan |
|---|---|
| A | Sesuai pencabutan §6; jalur approval bersih |
| B | Percepat pengikatan IA/workflow |
| C | Tidak menunda pasal non-UX |

## Disadvantages

| Opsi | Kelemahan |
|---|---|
| A | Substansi UX mengikat menunggu Review |
| B | Melanggar catatan “Review wajib” di §6 |
| C | C-07 tetap terbuka (dampak BC tinggi per DRR) |

## Recommended Option

**Option A.**

*Rekomendasi fasilitator — bukan keputusan. BO tetap Approver akhir setelah Review.*

## Consequences

| Dimensi | A | B | C |
|---|---|---|---|
| **Business** | Approval setelah Review | Approval cepat, risiko prematur | Tanpa Approval paket |
| **UX** | Status seragam → Review | Klaim READY tanpa Review ulang | Baseline tetap kabur |
| **Architecture** | Rendah | Rendah | Ketertelusuran lemah |
| **Domain** | Tidak berubah | Tidak berubah | Tidak berubah |
| **Implementation** | Edit metadata dokumen saja | Idem + Approve | Tidak ada perbaikan |
| **Governance** | Menutup C-07 dengan benar | Menutup C-07 dengan risiko proses | Tidak menutup C-07 |

## Affected Artifacts

UX-FOUNDATION-000 · PDS-001 · PWDM-001 · IA-001 · turunan NAV/WF · pasal Persona & Prinsip Pengalaman BC-000

## Future Scalability

Option A memastikan setiap turunan wireframe/UI lahir dari baseline yang benar-benar disetujui. Option B mempercepat tetapi merapuhkan fondasi. Option C membiarkan utang governance membesar.

## Business Owner Decision

| Field | Value |
|---|---|
| **Status** | **APPROVED** |
| Selected option | **A** |
| Authorize status-sync documentation edits? | **Yes** — administratif; tidak mengubah keputusan bisnis |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Notes | §2 UX-FOUNDATION-000 disinkronkan ke Draft (G0.2D). Paket tetap Draft sampai Review → READY → Approval formal isi paket. |

---

# BO-005 — Appointment Scope Consolidation

## Problem Statement

Appointment awalnya di luar lingkup, lalu diperluas lewat lima keputusan berantai tanpa pernyataan lingkup **kumulatif** tunggal. Mengutip baseline lama tanpa carve-out menghasilkan pernyataan produk yang sudah tidak benar.

## Current Repository Position

**In scope (hasil rantai, belum digabung resmi):** booking, check-in, completion, no-show, Final Resolution sekali setelah completion — selalu terkait escalation `APPROVED`.

**Tetap OOS:** Calendar, Slot Generator, Work Order, notifikasi/survey/auto-close terkait appointment, closure via paket appointment.

## Repository Evidence

| DL / DEC | Efek |
|---|---|
| DEC-001 | Appointment OOS (teks masih ada) |
| DEC-007 | Booking in scope |
| DEC-008 | Check-in in scope |
| DEC-009 | Completion in scope |
| DEC-010 | No-show in scope |
| DEC-011 | Final Resolution in scope (bukan state appointment) |
| DRR §8.2 / §9.3 | Carve-out wajib; risiko #1 konstitusi salah |

## Business Context

Keputusan **batas janji produk untuk janji temu & resolusi akhir**, tanpa membuka kembali model “schedule slot + work order” penuh yang ditolak baseline. Sangat terkait BO-001 karena prasyarat eskalasi.

## Current Risks

- Penulis BC mengutip DEC-001 atau DEC-007 saja → lingkup usang.
- Membuka Calendar/WO tanpa niat.
- Tanpa BO-001, pernyataan appointment bergantung pada eskalasi yang formalnya OOS.

## Available Options

### Option A

Terbitkan pernyataan lingkup kumulatif resmi (DEC/klausul BO) yang mencabut OOS Appointment pada DEC-001 **hanya** untuk kapabilitas in-scope di atas, dan menegaskan OOS yang tersisa.

### Option B

Tanpa konsolidasi; setiap kutipan BC harus merangkai DEC-007…011 lengkap.

### Option C

Tarik kembali sebagian/seluruh perluasan appointment ke OOS DEC-001.

## Advantages

| Opsi | Keunggulan |
|---|---|
| A | Satu kalimat akurat; hilangkan jebakan supersession |
| B | Tidak ada artefak baru |
| C | Baseline sederhana |

## Disadvantages

| Opsi | Kelemahan |
|---|---|
| A | Perlu formalisasi tertulis; terkait BO-001 |
| B | Rawan kutipan parsial (gagal tujuan anti-salah) |
| C | Rollback besar terhadap API/UI/SLA yang Approved |

## Recommended Option

**Option A.**

*Rekomendasi fasilitator — bukan keputusan.*

**Draf teks kumulatif (untuk diedit BO — bukan keputusan):**

> Appointment atas eskalasi `APPROVED` in scope terbatas pada: booking satu appointment aktif, check-in, completion (`COMPLETED` \| `PARTIALLY_COMPLETED`), no-show, serta Final Resolution sekali per complaint setelah completion (DEC-007…011). Tetap out of scope: Calendar View, Slot Generator, Work Order, notifikasi/survey/rating/auto-close terkait appointment, dan penutupan complaint/escalation melalui paket appointment.

## Consequences

| Dimensi | A | B | C |
|---|---|---|---|
| **Business** | Janji temu terbatas jelas | Janji tersebar di lima DEC | Janji temu ditarik |
| **UX** | Kontrol appointment tetap normatif | Sama, tanpa payung kutipan | UI appointment non-normatif |
| **Architecture** | Partial supersession terkunci | Rantai rapuh | Rollback lingkup |
| **Domain** | State appointment + Final Resolution resmi | Sama secara de facto | Domain menyempit |
| **Implementation** | Dokumentasi konsolidasi | Tidak ada | Potensi quarantine fitur |
| **Governance** | Menutup BO-05 / risiko #1 DRR | Tidak menutup risiko kutipan | Menutup dengan biaya tinggi |

## Affected Artifacts

DEC-001 · DEC-007…011 · DL-002 · DL-007…011 · API-305…310 · UI Escalation/Final Resolution · DEC-013 (completion fact) · pasal Lingkup BC-000

## Future Scalability

Option A menjaga pintu Calendar/WO tetap tertutup sampai DEC baru, sambil mengamankan jalur janji temu yang sudah diotorisasi. Option C memundurkan kapabilitas yang sudah diinvestasikan.

## Business Owner Decision

| Field | Value |
|---|---|
| **Status** | **APPROVED** |
| Selected option | **A** |
| Approve cumulative scope text? | **Yes** — Appointment bagian resmi Mode A sesuai batasan yang disetujui; mengikuti Complaint Lifecycle yang sama (bukan lifecycle terpisah) |
| Merge vote with BO-001? | **Yes** |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Notes | OOS tetap: Calendar · Slot Generator · Work Order · notifikasi/survey/auto-close terkait appointment (sampai DEC baru) |

---

# Cross Analysis

## Decision Dependency Matrix

| Keputusan | Bergantung pada | Menopang |
|---|---|---|
| **BO-001** Escalation | — (akar lingkup) | BO-005 (prasyarat `APPROVED` escalation); pasal Lingkup |
| **BO-005** Appointment | **BO-001** (disarankan sebelum atau bersama) | Pasal Lingkup (carve-out kumulatif) |
| **BO-002** SLA | Tidak bergantung P1 lain; terkait dual SoT (sudah diputuskan) | Pasal Komitmen Layanan & Waktu |
| **BO-003** Manager | Tidak bergantung BO-001/002/005 | BO-004 (isi persona yang di-Review); pasal Aktor |
| **BO-004** UX status | **BO-003** disarankan dulu (agar Review tahu nasib Manager) | Pengikatan substansi UX ke BC; memperkuat pasal Aktor/Pengalaman |

```
BO-001 ──► BO-005 ──► pasal Lingkup
BO-002 ─────────────► pasal SLA
BO-003 ──► BO-004 ──► pasal Aktor / UX mengikat
```

## Decision Priority Matrix

| Urutan | ID | Alasan prioritas |
|---|---|---|
| 1 | **BO-001** | Akar pernyataan lingkup; membuka/menutup fondasi eskalasi |
| 2 | **BO-005** | Carve-out lingkup yang bergantung eskalasi; bersama BO-001 bisa digabung |
| 3 | **BO-002** | Independen; memblokir pasal SLA |
| 4 | **BO-003** | Menentukan apakah Manager tetap di set sebelum Review UX |
| 5 | **BO-004** | Hygiene + Approval path setelah isi persona jelas |

## Conflict Matrix

Apakah memilih opsi di baris **mempersulit / mengubah makna** opsi di kolom?

| ↓ memengaruhi → | BO-001 | BO-002 | BO-003 | BO-004 | BO-005 |
|---|---|---|---|---|---|
| **BO-001 A/C** | — | Tidak langsung | Tidak | Tidak | **Memperkuat** A (prasyarat sah) |
| **BO-001 B** | — | Tidak | Tidak | Tidak | **Melemahkan** A (appointment tanpa eskalasi normatif) → BO-005 C jadi lebih masuk akal |
| **BO-002 A/B/C** | Tidak | — | Tidak | Tidak | Tidak (kecuali narasi SLA appointment stage) |
| **BO-003 A** | Tidak | Tidak | — | Review UX tetap tiga persona | Tidak |
| **BO-003 B** | Tidak | Tidak | — | Review harus sertakan Workspace Manager | Tidak |
| **BO-003 C** | Tidak | Tidak | — | **Cascade** revisi PDS→WF sebelum sync status | Tidak |
| **BO-004 A** | Tidak | Tidak | Tidak mengubah isi | — | Tidak |
| **BO-004 B** | Tidak | Tidak | Risiko Approve persona sebelum Review | — | Tidak |
| **BO-004 C** | Tidak | Tidak | Pasal Aktor tetap hanya DL-001 | — | Tidak |
| **BO-005 A** | Membutuhkan eskalasi jelas | Sedikit (completion fact) | Tidak | Tidak | — |
| **BO-005 C** | Mengurangi tekanan pada BO-001 | Mengurangi completion fact | Tidak | Tidak | — |

**Konflik terkuat:** BO-001 Option B ↔ BO-005 Option A.

## BC-000 Readiness

| BC Chapter (usulan) | Kesiapan hari ini | Menunggu |
|---|---|---|
| Mukadimah / Misi / Batas Produk / Target Architecture | **READY** | — |
| Kendali Perubahan | **READY** | — |
| Lingkup Bisnis | **BLOCKED** | BO-001, BO-005 |
| Terminologi & Rujukan Aturan | **READY** | — |
| Aturan Bisnis Dasar | **READY** | — |
| Komitmen Layanan (SLA/NFR) | **BLOCKED** | BO-002 |
| Model Komplain | **READY** | — |
| Lifecycle / Case State Machine | **PARTIALLY READY** | Kualifikasi dual SoT (C-04 / BO-09 P2) |
| Aturan Case Mode A | **PARTIALLY READY** | Catatan clock → BO-002 |
| Waktu & SLA (CAP-006 bisnis) | **BLOCKED** | BO-002 |
| Kepemilikan Konfigurasi | **READY** | — |
| Klasifikasi Aturan | **READY** | — |
| Kepemilikan Data | **READY** | — |
| Kepemilikan Otorisasi | **READY** | — |
| Aktor / Persona | **BLOCKED** | BO-003, BO-004 |
| Prinsip Pengalaman Kerja (CWX) | **PARTIALLY READY** | DL-027 READY; turunan UX → BO-004 |
| Kewajiban / Integritas / Audit Konfigurasi | **READY** | — |
| Integrasi Enterprise | **BLOCKED** | Mode B CLOSED (Board — di luar P1) |

## Governance Readiness

### Can BC-000 start today?

# YES — dengan kondisi dokumentasi (lihat GC-000)

### Remaining blockers (P1)

**Tidak ada.** Seluruh BO-001…005 APPROVED (2026-08-05); BO-001+BO-005 digabung sebagai Scope Consolidation.

### Setelah P1 terisi

- BC-000 **boleh disusun** dari 19 kandidat APPROVED (DRR §7) + DL-066…069 / teks keputusan P1.
- Follow-up: DEC formal pencatatan (disarankan), Review paket UX, countersign DEC-F4 (P2), butir Board.
- Mode B / integrasi enterprise **tetap di luar** pasal penuh; batas minimal dari DL-046.

## Recommended Business Owner Approval Order

1. **BO-001** (Escalation)  
2. **BO-005** (Appointment) — atau **satu keputusan gabungan** DEC-001 Scope Consolidation  
3. **BO-002** (SLA)  
4. **BO-003** (Manager)  
5. **BO-004** (UX status) — otorisasi sync + jalur Review/Approval  

**Mengapa:** Lingkup dulu (hindari konstitusi salah), lalu aturan layanan, lalu aktor, lalu kebersihan dokumen pengalaman agar Approval tidak mendahului isi.

---

# Executive Summary

**Untuk:** Business Owner  
**Dari:** Fasilitasi Governance Phase 0 (G0.2C)  
**Perihal:** Lima keputusan yang harus Anda ambil sebelum Business Constitution (BC-000) boleh ditulis  
**Panjang:** ringkas untuk satu sidang

### Situasi

Log keputusan dan review kesiapan sudah selesai. Paket resolusi (BO-000) sudah menyiapkan pilihan. **Lima isu Prioritas 1 masih kosong.** Tanpa lima keputusan ini, konstitusi bisnis berisiko salah di tiga tempat paling sensitif: **lingkup produk**, **janji waktu layanan (SLA)**, dan **siapa penggunanya**.

### Apa yang diminta dari Anda hari ini

Bukan desain ulang sistem. Bukan persetujuan Mode B / SSO. Hanya memilih **A / B / C** untuk setiap isu di bawah, dengan bahasa bisnis.

| # | Pertanyaan bisnis | Rekomendasi fasilitator |
|---|---|---|
| 1 | Apakah **eskalasi ke Kantor Pusat** resmi masuk lingkup produk? | **Ya, terbatas** (jalur cabang→pusat; tanpa membuka regional/work order) |
| 2 | Saat Mode A “mengikat SLA tapi tidak menjalankan jam”, sedangkan lab sudah menghitung breach — **aturan mana yang berlaku di dokumen resmi?** | **Keduanya, dengan ruang berlaku berbeda** (lab vs Mode A), sampai model SLA target diaktifkan penuh |
| 3 | Apakah **Manager** tetap aktor resmi meskipun dashboard Manager belum diantar di v0.1? | **Tetap aktor**; workspace ditunda; jangan janji seolah sudah live |
| 4 | Paket fondasi pengalaman pengguna statusnya campur aduk — **apa yang Anda izinkan?** | **Rapikan ke Draft → Review → baru Anda Approve** |
| 5 | Appointment sudah diperluas bertahap — **apa pernyataan lingkup tunggal yang Anda sahkan?** | **Kunci lingkup kumulatif yang sudah diizinkan**; Calendar/Work Order tetap di luar |

### Menggabungkan keputusan?

Isu **1 dan 5** adalah dua sisi dari dokumen lingkup yang sama. Anda **boleh** menggabungkannya menjadi satu keputusan “Konsolidasi Lingkup Baseline”, dengan dua klausul. Jangan digabung otomatis di sidang ini kecuali Anda meminta.

### Urutan sidang yang disarankan

Eskalasi → Appointment (atau gabungan) → SLA → Manager → Status paket UX.

### Hasil yang diharapkan dari sidang

Setelah lima (atau empat jika 1+5 digabung) keputusan Anda tercatat:

- Tim governance dapat menulis **BC-000** dari keputusan yang sudah disetujui.  
- Tidak ada coding, migrasi, atau perubahan aplikasi di tahap ini.  
- Integrasi ke aplikasi enterprise induk **tetap tertutup** sampai Board membuka — itu di luar sidang ini.

### Putusan hari ini tentang memulai BC-000

**Belum bisa dimulai** sampai slot keputusan di dokumen workshop ini diisi.  
Setelah diisi: **boleh dimulai**.

---

## Workshop Sign-off Sheet

| ID | Topik | Option dipilih | Paraf BO | Tanggal |
|---|---|---|---|---|
| BO-001 | Head Office Escalation Scope | ☑ **A** | Business Owner – ECMP | 2026-08-05 |
| BO-005 | Appointment Scope Consolidation | ☑ **A** | Business Owner – ECMP | 2026-08-05 |
| BO-001+005 | Gabungan lingkup DEC-001 | ☑ **Ya** — Scope Consolidation Mode A | Business Owner – ECMP | 2026-08-05 |
| BO-002 | SLA Constitution | ☑ **A** | Business Owner – ECMP | 2026-08-05 |
| BO-003 | Manager Persona vs Dashboard | ☑ **A** | Business Owner – ECMP | 2026-08-05 |
| BO-004 | UX Package Status Sync | ☑ **A** | Business Owner – ECMP | 2026-08-05 |

**Business Owner name:** Business Owner – ECMP  
**Session date:** 2026-08-05  
**Decision Status:** APPROVED  
**Recorded in:** DL-066 · DL-067 · DL-068 · DL-069 · GC-000

---

## Related (read-only)

- `docs/governance/GC-000-Governance-Closure-BC-Readiness.md`
- `docs/governance/DL-000-Decision-Log.md`
- `docs/governance/DRR-000-Decision-Readiness-Review.md`
- `docs/governance/BO-000-Business-Owner-Resolution-Pack.md`

## Document control

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-08-05 | Initial P1 workshop pack — all decisions Pending |
| 1.1 | 2026-08-05 | BO decisions recorded APPROVED; sign-off complete; link DL-066…069 / GC-000 |

---

*End of BO-WS-000. Business Owner Priority-1 decisions recorded 2026-08-05.*
