# BO-000 — Business Owner Resolution Pack

| Field | Value |
|---|---|
| Document ID | BO-000 |
| Title | Business Owner Resolution Pack (atas DRR-000) |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | **CLOSED — Business Owner P1 decisions recorded 2026-08-05** |
| Milestone | Governance Phase 0 — G0.2C |
| Input | `docs/governance/DRR-000-Decision-Readiness-Review.md` · `docs/governance/DL-000-Decision-Log.md` |
| Subordination | Board Resolution → ADR → EA Documents → ECMP-CONSTITUTION-001 → DL-000 → DRR-000 → **BO-000** |
| Does not | Mengubah keputusan asli · memodifikasi DL-000/DRR-000 · membuat BC-000 · menyelesaikan konflik atas nama Business Owner · mengubah kode |

---

## 1. Purpose

Paket ini menyiapkan **disposisi eksplisit Business Owner** untuk setiap isu governance yang masih terbuka dan menyentuh isi Business Constitution (BC-000).

Dokumen ini:

- mengangkat isu dari Conflict Register dan Business Owner Review List DRR-000;
- merangkum situasi repositori dan dampaknya;
- menyajikan opsi dengan pro/kontra;
- mencatat rekomendasi Cursor **tanpa** membuat keputusan bisnis;
- slot keputusan Business Owner diisi pada **G0.2D** (seluruh P1 **APPROVED** 2026-08-05).

**BC-000 boleh dimulai dengan kondisi** — lihat `GC-000-Governance-Closure-BC-Readiness.md`.

---

## 2. Scope of This Pack

| Termasuk (P1 — memblokir pasal BC-000) | Tidak diselesaikan di sini |
|---|---|
| BO-001 Head Office Escalation Scope (C-08) | Konflik Architecture Board (C-01, C-02, C-03, C-05, C-06, C-11) |
| BO-002 SLA Constitution (C-12) | Mode B / ADR-014…018 (APPROVED WITH CONDITIONS) |
| BO-003 Manager Persona vs Dashboard (C-09) | Invent keputusan bisnis baru di luar opsi yang sudah ada di repositori |
| BO-004 UX Package Status Synchronization (C-07) | Implementasi, redesign, atau perubahan kode |
| BO-005 Appointment Scope Consolidation | BC-000 drafting |

Butir BO Review List DRR-000 nomor BO-06…BO-14 (P2/P3) dicatat di Resolution Summary sebagai backlog BO, bukan sebagai bagian disposisi wajib G0.2C.

---

# Resolution Topics

---

# BO-001

## Title

Head Office Escalation Scope (C-08)

## Background

DEC-001 (DL-002) menetapkan baseline bisnis resmi = Blueprint v2.1 + FRD-001, dan menyatakan konsep **Branch Officer / Head Office escalation / Schedule Slot / Appointment / Work Order** **di luar lingkup** sampai revisi Blueprint di-approve Architecture Board.

Appointment kemudian mendapat rantai **partial supersession eksplisit** (DEC-007…010 / DL-007…010) plus Final Resolution (DEC-011 / DL-011). **Tidak ada DEC setara yang mencabut atau mengonfirmasi ulang status out-of-scope untuk Head Office escalation itu sendiri.**

Sementara itu, banyak artefak memperlakukan eskalasi sebagai kapabilitas yang ada: DEC-F4 (model Cabang → Pusat, Locked di workshop), DEC-013 memakai tahap SLA `escalation`, Escalation Detail UI, BR-007, dan prasyarat appointment (“against an `APPROVED` escalation”).

## Current Repository Situation

| Artefak | Pernyataan terkait eskalasi |
|---|---|
| DEC-001 / DL-002 | Head Office escalation **out of scope** (belum dicabut) |
| DEC-007…011 | Appointment & Final Resolution diotorisasi; prasyarat eskalasi `APPROVED` diasumsikan |
| DEC-F4 / DL-012 | Model visibilitas/return Cabang→Pusat **Locked** di workshop; berkas masih 🟡 Proposed (countersign Board belum) |
| DEC-012/013 | Snapshot & evaluasi SLA mencakup tahap `escalation` |
| UI / API Foundation | Escalation Detail, alur appointment di atas eskalasi |
| Constitution §3 | “Complaint Management Module menyediakan: … Escalation …” (batas kapabilitas modul, bukan otorisasi lingkup DEC-001) |

DRR-000 memverifikasi: grep seluruh `27 Project Decisions/DEC-*.md` — eskalasi muncul sebagai *prasyarat*, bukan sebagai otorisasi lingkup yang mencabut DEC-001.

## Conflicting Documents

| Dokumen A | Dokumen B | Konflik |
|---|---|---|
| DEC-001 (DL-002) — escalation OOS | DEC-F4, DEC-007…011, DEC-013, UI Escalation | Kapabilitas dipakai tanpa DEC pencabutan OOS |
| DEC-F4 Locked (workshop) | DEC-F4 Status 🟡 Proposed | Keputusan bisnis belum formal-DEC |
| ECMP-CONSTITUTION-001 §3 menyebut Escalation | DEC-001 masih OOS untuk Head Office escalation | Batas modul vs baseline delivery |

## Business Impact

- BC-000 **tidak dapat** menulis pasal Lingkup Bisnis yang menyatakan eskalasi in-scope atau out-of-scope tanpa dasar keputusan BO.
- Risiko konstitusi **salah** (bukan sekadar tidak lengkap): mengutip DL-002 mentah akan mengunci ulang OOS yang sudah dilanggar praktiknya; mengabaikan DEC-001 tanpa DEC baru melanggar governance.

## Architecture Impact

- Dual-SoT / CAP-008 Mode A (BQ-009: `PENDING`/`ESCALATED` terdefinisi tapi tidak diekspos Mode A) bergantung pada apakah eskalasi adalah kapabilitas resmi atau lab-only.
- Mode B identity/org tidak tersentuh langsung; ini keputusan **lingkup domain complaint**.

## UX Impact

- Escalation Detail UI, alur Supervisor (NAV-001: keputusan eskalasi), dan wireframe terkait menjadi orphan governance jika OOS ditegakkan ulang.
- Jika OOS ditegakkan: UI/alur eskalasi harus ditandai non-normatif / lab-only sampai DEC baru.

## Implementation Impact

- Tidak ada perubahan kode di milestone ini.
- Setelah keputusan: mungkin perlu DEC pencabutan/konfirmasi; sinkron OpenAPI/Event/BR; dan disposisi formal DEC-F4 (bersama Board — P2).

## Available Options

### Option A

**Cabut status out-of-scope “Head Office escalation” via DEC Business Owner** (pola sama DEC-007 untuk Appointment). Nyatakan lingkup eskalasi yang diotorisasi (minimal: model Cabang → Pusat per F4.1; tanpa Regional; tanpa Work Order/Calendar kecuali DEC terpisah).

#### Pros

- Menyelaraskan keputusan dengan praktik repositori dan workshop F4.
- Memberi dasar sah bagi pasal Lingkup dan pasal terkait Supervisor/eskalasi di BC-000.
- Menutup celah pencatatan terbesar pada DL-002.

#### Cons

- Memerlukan DEC tertulis + kemungkinan revisi Blueprint/FRD batch (per DEC-001 follow-up asli).
- Membuka kewajiban menertibkan batas (apa yang masih OOS: Regional, Work Order, Schedule Slot, dsb.).

### Option B

**Tegakkan ulang OOS**: Head Office escalation tetap di luar lingkup produk sampai revisi Blueprint. Artefak yang mengasumsikan eskalasi ditandai *non-binding / lab hedge* dan tidak masuk pasal BC-000 sebagai kapabilitas resmi.

#### Pros

- Konsisten ketat dengan DEC-001 tertulis.
- Memaksa pembersihan sebelum konstitusi mengklaim eskalasi.

#### Cons

- Bertentangan dengan DEC-F4 Locked, rantai appointment, SLA tahap escalation, dan UI yang sudah ada.
- Biaya rollback dokumentasi/implementasi tinggi; BC-000 pasal Lingkup menjadi sempit dan tidak mencerminkan Mode A yang berjalan.

### Option C *(varian pencatatan)*

**Konfirmasi bahwa otorisasi sudah ada secara implisit** lewat rantai DEC-007…011 + F4, dan BO hanya menerbitkan **DEC ratifikasi retrospektif** tanpa mengubah perilaku.

#### Pros

- Biaya rendah; menutup gap dokumentasi.
- Mempertahankan perilaku lab saat ini.

#### Cons

- Melemahkan pola “partial supersession eksplisit” yang dipakai Appointment.
- Tetap perlu teks DEC yang jelas agar BC-000 punya kutipan.

## Cursor Recommendation

**Option A** (atau Option C bila BO menganggap substansi F4 + rantai appointment sudah cukup dan hanya formalitas yang kurang) — karena DRR menilai ini kemungkinan besar **celah pencatatan**, bukan penolakan sengaja terhadap eskalasi. Option B hanya rasional jika BO secara sadar ingin menarik kembali kapabilitas dari produk.

*(Ini rekomendasi teknis/governance — **bukan** keputusan bisnis.)*

## Business Owner Decision

**APPROVED — Option A** (2026-08-05)

| Field | Value |
|---|---|
| Selected option | **A** |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Follow-up DEC ID (jika ada) | Direkomendasikan DEC pencatatan Scope Consolidation (bersama BO-005 → DL-066) |
| Notes | Merge dengan BO-005 = YES. OOS tetap: Regional · Work Order · Calendar/Schedule · Mode B · Enterprise Integration |

## Implementation Notes

- Setelah keputusan: terbitkan DEC (atau ratifikasi) sebelum menulis pasal Lingkup BC-000.
- DEC-F4 tetap perlu countersign Architecture Board (DRR BO-06 / P2) — terpisah dari pencabutan OOS DEC-001.
- Jangan mengandalkan kutipan Constitution §3 sebagai pengganti DEC lingkup.

## Affected Artifacts

| Artifact | Role |
|---|---|
| DEC-001 / DL-002 | Pernyataan OOS yang harus dicabut/dikonfirmasi |
| DEC-F4 / DL-012 | Model eskalasi Cabang→Pusat |
| DEC-007…011 / DL-007…011 | Prasyarat `APPROVED` escalation |
| DEC-013 / DL-017 | Tahap SLA `escalation` |
| BR-CM-CAT-001 / BR-007 | Aturan eskalasi target |
| `07 API Catalog/` · `08 Event Catalog/` | Endpoint/event eskalasi & appointment |
| UI Escalation Detail / NAV-001 Supervisor | Permukaan kerja eskalasi |
| BC-000 pasal Lingkup Bisnis | Konsumen keputusan |

---

# BO-002

## Title

SLA Constitution (C-12)

## Background

Tiga lapisan keputusan SLA hidup di repositori tanpa pernyataan ruang berlaku yang eksplisit untuk pembaca konstitusi:

1. **Target numerik & kalender** — DL-005 (DEC-005) + DL-004 (BR-ECMF-05 24x7); reversibel via DEC BO.
2. **Jalur Foundation/lab** — DL-016/017/018 (DEC-012/013/014): deadline di-snapshot saat create; breach dievaluasi event-driven menjadi `BREACHED`/`COMPLETED`.
3. **Jalur Aggregate / Mode A CAP-008** — DL-024 BQ-005: Case **SHALL** bind SLA Policy Version; **countdown SLA TIDAK diaktifkan** di Mode A (*bind-without-clock*). Ditambah DL-019 (CAP-006 bisnis LOCKED) dengan runtime konkret **Deferred**.

C-05 (dua mekanisme paralel) adalah isu arsitektur konvergensi; **C-12** adalah isu **aturan bisnis** yang tampak bertentangan di konstitusi.

## Current Repository Situation

| Jalur | Perilaku SLA hari ini | Status keputusan |
|---|---|---|
| Foundation (`/api/v1/complaints` + modul `sla`) | Deadline dihitung; status bisa `BREACHED` | DEC-012/013 Approved |
| Aggregate Mode A (`/api/v1/cm`, CAP-008) | Bind policy version; clock tidak jalan | BQ-005 LOCKED |
| CAP-006 target bisnis | Kalender, start/stop, warning dikunci; runtime ditunda | FRD-005 LOCKED; runtime Deferred |
| Dual SoT (DEC-020) | Koeksistensi tanpa Retirement DEC | Approved; C-06 terbuka (Board) |

## Conflicting Documents

| Dokumen A | Dokumen B |
|---|---|
| DL-024 BQ-005 — no countdown Mode A | DL-016/017 — deadline + BREACHED aktif |
| DL-005 — target numerik berlaku | BQ-005 — clock tidak diaktifkan |
| DL-019 CAP-006 bisnis LOCKED | DEC-012/013 “Separate track ≠ CAP-006 fulfillment” (BQ-CAP006-15) |

## Business Impact

- Pasal **Komitmen Layanan / Waktu & SLA** di BC-000 akan tampak inkonsisten bagi pembaca bisnis.
- Operator/auditor tidak tahu: apakah breach di lab mengikat secara bisnis Mode A atau tidak.

## Architecture Impact

- Memperjelas apakah pemisahan per SoT **disengaja** (selaras C-04/C-05) atau harus diselaraskan.
- Konvergensi runtime CAP-006 (AB-10) tetap milik Architecture Board; BO hanya menetapkan **makna bisnis** ruang berlaku.

## UX Impact

- SLA card / Context Header / KPI summary menampilkan angka dari jalur Foundation; Aggregate Mode A menampilkan bind tanpa countdown — UX harus diberi label ruang berlaku setelah keputusan.

## Implementation Impact

- Dokumentasi/konstitusi dulu; kode tidak diubah di G0.2C.
- Setelah keputusan: mungkin perlu catatan SoT pada API-314…318 dan FRD terkait; bukan forced merge dual SoT.

## Available Options

### Option A

**Pemisahan eksplisit per SoT (rekomendasi pencatatan C-12):**

- Foundation/lab: clock & breach **berlaku** (DEC-012/013).
- Aggregate Mode A: **bind-without-clock** (BQ-005) sampai CAP-006 runtime diotorisasi.
- Target numerik DL-005 = komitmen konfigurasi/policy, bukan klaim bahwa kedua jalur menjalankan clock yang sama.
- CAP-006 = model bisnis target; pemenuhan ≠ jalur DEC-012/013.

#### Pros

- Konsisten dengan dual SoT yang sudah diputuskan (DEC-BQ001 O3, DEC-020).
- Tidak memaksa rollback lab atau mengaktifkan clock Mode A tanpa otorisasi.
- BC-000 dapat menulis pasal SLA dengan kualifikasi ruang berlaku yang jelas.

#### Cons

- Membakukan dualitas SLA sampai Retirement/convergence DEC.
- Pembaca harus selalu menyebut jalur SoT.

### Option B

**Selaraskan ke satu aturan bisnis sekarang:** clock SLA **tidak** berjalan di Mode A **maupun** Foundation sampai CAP-006 runtime — DEC-012/013 diturunkan statusnya menjadi lab non-normatif untuk konstitusi.

#### Pros

- Satu kalimat konstitusi yang sederhana.
- Selaras ketat dengan BQ-005 sebagai aturan Mode A.

#### Cons

- Mencabut makna normatif dari DEC Approved yang sudah diimplementasikan.
- KPI/timeline breach di lab menjadi non-bisnis — dampak luas pada tes dan ops.

### Option C

**Selaraskan ke clock aktif di semua jalur Mode A:** cabut/revisi BQ-005; aktifkan countdown pada Aggregate.

#### Pros

- Satu perilaku operasional.
- Memanfaatkan investasi DEC-012/013.

#### Cons

- Mengubah keputusan Mode A yang ALL LOCKED (residual ZERO) — memerlukan DEC BO baru dengan dampak FRD/OpenAPI CAP-008.
- Bertabrakan dengan deferral runtime CAP-006 kecuali BO juga mengotorisasi runtime.

## Cursor Recommendation

**Option A** — mencatat pemisahan yang sudah tersirat oleh dual SoT, tanpa invent perilaku baru dan tanpa membuka ulang BQ pack Mode A. Option B/C hanya jika BO secara sadar ingin menyeragamkan perilaku dengan biaya revisi keputusan terkunci.

*(Bukan keputusan bisnis.)*

## Business Owner Decision

**APPROVED — Option A** (2026-08-05)

| Field | Value |
|---|---|
| Selected option | **A** |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Explicit statement for BC-000 (draft text) | Satu SLA Constitution resmi untuk seluruh Complaint Lifecycle; aturan bisnis seragam; perubahan SLA wajib Timeline Events; detail teknis mengikuti BC & BR |
| Notes | Mode A. Record: DL-067 |

## Implementation Notes

- BC-000 pasal SLA **wajib** mengutip DL-005 + DL-019 + catatan ruang berlaku BQ-005 vs DEC-012/013 setelah keputusan.
- Angka baseline tetap **rujukan** (reversibel via DEC), jangan di-inline sebagai konstanta abadi.
- Konvergensi mekanisme (C-05 / AB-10) tetap di Architecture Board saat M-18.

### Affected artifacts — penjelasan per artefak

| Artifact | Bagaimana terdampak |
|---|---|
| DL-005 / DEC-005 | Target numerik — tetap rujukan; ruang “kapan dihitung” ditentukan BO |
| DL-004 BR-ECMF-05 | Kalender 24x7 — berlaku sebagai default config |
| DL-016 DEC-012 | Calculator — normatif hanya jika Option A/C memilih jalur Foundation |
| DL-017 DEC-013 | Breach detection — idem |
| DL-018 DEC-014 | Timeline SLA events — idem |
| DL-019 CAP-006 closure | Model bisnis target; 3 butir DEFERRED tetap |
| DL-020/021 | Hybrid + runtime placement — arsitektur, bukan pasal angka |
| DL-024 BQ-005 | Bind-without-clock Mode A — inti konflik |
| FRD-005 / SLA Matrix | Spesifikasi target vs runtime |
| API-314…318 / KPI | Permukaan yang menampilkan status SLA |
| BC-000 pasal Komitmen Layanan & Waktu | Konsumen keputusan |

## Affected Artifacts

Lihat tabel di Implementation Notes di atas.

---

# BO-003

## Title

Manager Persona vs Dashboard Availability (C-09)

## Background

DL-001 / PDS-001 menetapkan **closed set tiga persona operasional**: Complaint Officer · Supervisor · **Manager**. Manager adalah satu-satunya persona level agregat; entry point navigasi = **Dashboard** (NAV-001, IA-001).

DL-062 / BQ-CAP007-04 menutup CAP-007 dengan: **Approve Supervisor-only v0.1; Defer Manager/Executive**. FRD-006 dan Role Access Matrix menunda aktor Manager/Executive. PDS-001 juga mencatat: **Manager belum punya padanan peran teknis** di Authorization.

Akibatnya: persona Manager ada di model UX, tetapi **tidak punya permukaan kerja yang diotorisasi bisnis** untuk v0.1, dan belum punya role teknis.

## Current Repository Situation

| Lapisan | Status Manager |
|---|---|
| Persona (PDS-001) | Termasuk closed set; read-only agregat |
| Navigasi (NAV-001) | `Login → Dashboard` sebagai rumah kerja |
| IA / Wireframe plan | Zona Reference; WF-001-19/20 Release 3 (P2) |
| CAP-007 / FRD-006 | Dashboard v0.1 = Supervisor-only |
| Authorization | Gap — belum ada role padanan Manager |
| DL-001 untuk BC-000 | Kandidat YES, dengan kualifikasi C-09 |

## Conflicting Documents

| Dokumen A | Dokumen B |
|---|---|
| PDS-001 / NAV-001 / IA-001 — Manager + Dashboard wajib | BQ-CAP007-04 / FRD-006 — Manager Deferred v0.1 |
| PDS-001 “Three Personas, Closed Set” | Tidak ada role teknis Manager |

## Business Impact

- BC-000 tidak dapat menetapkan tiga persona sebagai closed set final tanpa menjelaskan status kapabilitas Manager.
- Risiko: konstitusi menjanjikan aktor yang produk v0.1 tidak layani.

## Architecture Impact

- Entitlement/role-permission (ADR-008) perlu slot role bila Manager Workspace diwajibkan.
- Tidak membuka Mode B; ini keputusan aktor modul.

## UX Impact

- Seluruh rantai UX Foundation mengasumsikan Manager.
- Jika Manager diturunkan dari closed set: revisi PDS-001 + seluruh turunan (PWDM, IA, NAV, WF).
- Jika tetap persona-only: UX harus membedakan **persona bisnis** vs **workspace yang di-deliver**.

## Implementation Impact

- G0.2C: dokumentasi saja.
- Option yang memilih Workspace wajib akan memicu backlog dashboard Manager (M-26) + role mapping — di luar BC drafting.

## Available Options

### Option A

**Manager tetap dalam closed set sebagai Business Persona**; Manager Workspace / dashboard lintas-unit **tetap Deferred** (selaras BQ-CAP007-04). BC-000 menulis tiga persona dengan klausul: kapabilitas dashboard Manager **bukan** bagian otorisasi v0.1; Supervisor adalah audiens dashboard yang diotorisasi saat ini.

#### Pros

- Tidak membuka ulang merge persona DL-001.
- Konsisten dengan deferral CAP-007 yang sudah CLOSED.
- Memungkinkan BC-000 pasal Aktor dengan kualifikasi jujur.

#### Cons

- Persona tanpa rumah kerja resmi — harus dijelaskan agar tidak dibaca sebagai janji delivery.
- Gap role teknis tetap terbuka sampai DEC terpisah.

### Option B

**Manager Workspace diwajibkan** sebagai bagian konstitusi pengalaman: BO menarik deferral BQ-CAP007-04 untuk jalur Manager (bukan Executive), menuntut role teknis + FRD revisi sebelum BC-000 mengunci pasal Persona tanpa kualifikasi deferral.

#### Pros

- Closed set = kapabilitas nyata.
- Menyelaraskan NAV-001 dengan otorisasi produk.

#### Cons

- Membuka ulang keputusan CAP-007 yang dikunci.
- Memblokir BC-000 lebih lama (butuh FRD/SEC-RAM/API).
- Melebar ke delivery, bukan hanya konstitusi.

### Option C

**Keluarkan Manager dari closed set operasional** sampai dashboard & role siap; closed set sementara = Complaint Officer · Supervisor saja.

#### Pros

- Konstitusi hanya mengklaim aktor yang punya permukaan kerja.

#### Cons

- Membatalkan sebagian DL-001 / PDS-001 (perlu revisi formal UX).
- Biaya cascade ke seluruh paket UX Foundation.
- Bertentangan dengan arah merge persona yang baru saja diseragamkan.

## Cursor Recommendation

**Option A** — mempertahankan closed set tiga persona sebagai model bisnis/UX, dengan kualifikasi eksplisit bahwa delivery dashboard Manager ditunda per CAP-007. Option B hanya jika BO siap membuka ulang FRD dashboard sekarang. Option C mahal dan memundurkan kerja UX yang baru diseragamkan.

*(Bukan keputusan bisnis.)*

## Business Owner Decision

**APPROVED — Option A** (2026-08-05)

| Field | Value |
|---|---|
| Selected option | **A** |
| Manager in closed set? | **Yes** |
| Manager Workspace required for BC-000? | **No** — boleh ditunda; persona tidak bergantung kesiapan UI |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Notes | Record: DL-068 |

## Implementation Notes

- Pisahkan keputusan ini dari BO-011 (P3) aktivasi kolom FR-030 / Executive.
- Authorization role mapping untuk Manager = follow-up teknis setelah Option A/B, bukan prasyarat silent.

## Affected Artifacts

| Artifact | Role |
|---|---|
| DL-001 / PDS-001 | Closed set persona |
| PWDM-001 · IA-001 · NAV-001 · WF-* | Rumah kerja Manager = Dashboard |
| DL-062 / BQ-CAP007-04 | Supervisor-only v0.1 |
| FRD-006 · SEC-RAM · TC dashboard | Cakupan aktor |
| DEC-016 / API dashboard | Orchestration layer |
| BC-000 pasal Aktor / Persona | Konsumen keputusan |

---

# BO-004

## Title

UX Package Status Synchronization (C-07)

## Background

UX-FOUNDATION-000 adalah dokumen payung paket baseline (PDS-001 · PWDM-001 · IA-001). Setelah merge persona (UX-001 Documentation Update), status paket **dicabut** dari READY FOR APPROVAL dan dikembalikan ke Draft untuk Review ulang.

Namun §2 dokumen payung masih mencantumkan PWDM-001 dan IA-001 sebagai **READY FOR APPROVAL**, sementara §6 menyatakan paket **DRAFT — BUKAN READY FOR APPROVAL**. Berkas anak sendiri berstatus **Draft**. Akibatnya tidak ada turunan UX yang dapat diklaim mengikat untuk BC-000 di luar DL-001 dan DL-027.

## Current Repository Situation — inventory status UX

| Document ID | Path | Header Status | Catatan inkonsistensi |
|---|---|---|---|
| UX-FOUNDATION-000 | `docs/ux/UX-FOUNDATION-000-…md` | Draft (payung) | §2 vs §6 saling bertentangan untuk PWDM/IA |
| PDS-001 | `docs/ux/PDS-001-…md` | Draft | Rujukan aktif closed set |
| PDS-000 | `docs/ux/PDS-000-…md` | Superseded by PDS-001 | Historis — OK |
| PWDM-001 | `docs/ux/PWDM-001-…md` | Draft | Payung §2 bilang READY FOR APPROVAL |
| IA-001 | `docs/ux/IA-001-…md` | Draft | Payung §2 bilang READY FOR APPROVAL |
| NAV-001 | `docs/ux/NAV-001-…md` | Draft | Turunan; bukan baseline §2 |
| WF-000 | `docs/ux/WF-000-…md` | Draft | — |
| WF-PLAN-001 | `docs/ux/WF-PLAN-001-…md` | Draft | Backlog 21 wireframe |
| WF-001-01 | `docs/ux/WF-001-01-…md` | Draft | — |
| UX-001 (legacy) | `12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` | Draft (direvisi merge) | Bukan SoT “siapa persona” (PDS-001) |

**Sumber kebenaran status yang dimaksud §6 payung:** seluruh paket baseline = **Draft, bukan READY FOR APPROVAL**, menunggu Review ulang pasca-merge.

## Conflicting Documents

| Lokasi | Klaim |
|---|---|
| UX-FOUNDATION-000 §2 (PWDM-001, IA-001) | READY FOR APPROVAL |
| UX-FOUNDATION-000 §6 + header payung | DRAFT — BUKAN READY FOR APPROVAL |
| Header PWDM-001 / IA-001 | Draft |

## Business Impact

- Approver UX Foundation = Business Owner (per DRR). Tanpa status sinkron, BO tidak bisa Approve paket yang dokumennya bilang Draft dan READY sekaligus.
- Substansi UX di luar prinsip CWX-000 (DL-027) dan fakta merge (DL-001) **tidak eligible** sebagai pasal mengikat BC-000.

## Architecture Impact

- Rendah langsung (bukan ADR). Tinggi untuk ketertelusuran UX → delivery.

## UX Impact

- Memblokir klaim “closed set destinasi/zona” dan backlog wireframe sebagai baseline disetujui.
- Review paket tidak dapat dimulai secara sah sampai status seragam.

## Implementation Impact

- Hanya koreksi metadata/status dokumen UX (setelah arahan BO) — **bukan** redesign.
- Tidak menyentuh `frontend/` code.

## Available Options

### Option A

**Sinkronkan semua status ke Draft (bukan READY)** sesuai §6 dan header berkas anak; koreksi §2 UX-FOUNDATION-000; jalankan Review paket; baru ajukan READY FOR APPROVAL → Approval BO.

#### Pros

- Sesuai catatan pencabutan status yang sudah tertulis di §6.
- Menghormati merge persona yang belum di-review ulang.
- Jalur approval bersih.

#### Cons

- Menunda pengikatan substansi UX ke BC-000 sampai Review selesai.
- Pasal Persona BC-000 sementara hanya mengandalkan DL-001 + kualifikasi.

### Option B

**Naikkan PWDM-001 & IA-001 ke READY FOR APPROVAL sekarang** (anggap merge sudah cukup), selaraskan §6 dan header anak ke READY, lalu BO Approve paket.

#### Pros

- Mempercepat pengikatan IA/workflow ke konstitusi.
- Mengurangi kualifikasi pada pasal pengalaman.

#### Cons

- Bertentangan dengan pernyataan eksplisit §6 bahwa READY **dicabut** dan Review ulang **wajib**.
- Risiko Approve tanpa Review pasca-merge.

### Option C

**Freeze status inkonsisten** dan tulis BC-000 hanya dari DL-001/DL-027 tanpa menunggu sinkronisasi.

#### Pros

- Tidak menunda pasal non-UX.

#### Cons

- Melanggar tujuan G0.2C (BO-04 P1).
- Meninggalkan C-07 terbuka — DRR menilai dampak BC **Tinggi**.

## Cursor Recommendation

**Option A** — satu-satunya opsi yang konsisten dengan dokumen payung §6 dan header aktual berkas anak. Option B melanggar catatan pencabutan yang sudah ada. Option C tidak menutup C-07.

**Urutan sinkronisasi yang disarankan (setelah BO memilih A):**

1. Koreksi tabel §2 UX-FOUNDATION-000: PWDM-001 & IA-001 → `Draft — menunggu Review/Approval setelah merge persona` (selaras PDS-001).
2. Pastikan header ketiga baseline = Draft.
3. UX Lead menjalankan Review checklist merge persona.
4. Baru set READY FOR APPROVAL secara seragam.
5. Business Owner Approval formal paket.

*(Bukan keputusan bisnis; BO tetap Approver akhir.)*

## Business Owner Decision

**APPROVED — Option A** (2026-08-05)

| Field | Value |
|---|---|
| Selected option | **A** |
| Authorize status sync edits? | **Yes** |
| Target package status after sync | Draft seragam (bukan READY) sampai Review ulang |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Notes | Record: DL-069. §2 UX-FOUNDATION-000 disinkronkan pada G0.2D |

## Implementation Notes

- Edits status = documentation hygiene; tetap di luar milestone coding.
- Jangan Approve diam-diam tanpa Review bila Option A dipilih.
- DL-001 (merge) dan DL-027 (CWX Golden Rules) tetap kandidat BC meski paket turunan Draft.

## Affected Artifacts

| Artifact | Action after decision |
|---|---|
| UX-FOUNDATION-000 §2 & §6 | Sinkron status |
| PDS-001 · PWDM-001 · IA-001 | Seragamkan header status |
| NAV-001 · WF-000 · WF-PLAN-001 · WF-001-01 | Tetap Draft sampai baseline Approved |
| PDS-000 | Tetap Superseded |
| BC-000 pasal Persona & Prinsip Pengalaman | Terikat hasil Approval |

---

# BO-005

## Title

Appointment Scope Consolidation

## Background

DEC-001 menempatkan **Appointment** (bersama Schedule Slot / Work Order) di luar lingkup. Kemudian lima keputusan Approved memperluas lingkup secara **bertahap** tanpa pernah menerbitkan pernyataan lingkup kumulatif tunggal:

| DL | DEC | Otorisasi | Klausul OOS lama yang digugurkan |
|---|---|---|---|
| DL-007 | DEC-007 | Booking (`BOOKED`) atas escalation `APPROVED` | Appointment booking OOS di DEC-001 |
| DL-008 | DEC-008 | Check-in (`CHECKED_IN`) | “Check-in OOS” di DEC-007 |
| DL-009 | DEC-009 | Completion (`COMPLETED` / `PARTIALLY_COMPLETED`) | “Completion OOS” di DEC-008 |
| DL-010 | DEC-010 | No-show (`NO_SHOW` dari `BOOKED`) | Melengkapi cabang status |
| DL-011 | DEC-011 | Final Resolution sekali / complaint setelah appointment `COMPLETED` | Bukan appointment state; terkait resolusi |

DRR memperingatkan: mengutip DL-002 tanpa carve-out berantai = **pernyataan lingkup yang salah** di BC-000.

## Current Repository Situation

**In scope (kumulatif, hasil pembacaan berantai — belum digabung resmi):**

- Satu appointment aktif per alur booking; read by id.
- Transisi: `BOOKED` → `CHECKED_IN` → `COMPLETED`/`PARTIALLY_COMPLETED`; atau `BOOKED` → `NO_SHOW`.
- Timeline events terkait; UI pada Escalation Detail / Complaint Detail (Final Resolution).
- Final Resolution: satu per complaint; tidak menutup complaint/escalation.

**Tetap out of scope (belum ada DEC pencabutan):**

- Calendar View, Slot Generator, Schedule Slot generik.
- Work Order.
- Notification / Survey / Rating / Auto Close terkait appointment.
- Closure workflow sebagai bagian paket appointment.
- Branch Officer sebagai konsep baseline brief discovery (terpisah dari eskalasi — lihat BO-001).

## Conflicting Documents

| Dokumen | Risiko bila dikutip mentah |
|---|---|
| DEC-001 | “Appointment OOS” — **salah** tanpa carve-out |
| DEC-007 saja | Menyebut check-in/completion masih OOS — **usang** |
| DEC-008/009 secara terpisah | Pembaca harus merakit sendiri |
| Tidak ada | Pernyataan kumulatif resmi untuk BC-000 |

## Business Impact

- Pasal Lingkup Bisnis membutuhkan **satu kalimat kumulatif** yang disetujui BO.
- Menghindari regresi ke model “branch → HO → schedule slot → work order” penuh yang ditolak DEC-001.

## Architecture Impact

- Mempertahankan partial supersession sempit (bukan membuka Calendar/WO).
- Bergantung BO-001 untuk prasyarat eskalasi.

## UX Impact

- Escalation Detail appointment controls tetap dalam lingkup bila konsolidasi mengunci in-scope di atas.
- Calendar/Slot tetap tidak digambar sebagai janji produk.

## Implementation Impact

- Dokumentasi konsolidasi (DEC atau klausul BC) — tanpa fitur baru.
- API-305…310 tetap dalam batas yang sudah Approved.

## Available Options

### Option A

**Terbitkan pernyataan lingkup kumulatif resmi** (DEC konsolidasi atau klausul yang ditandatangani BO) yang:

1. mencabut OOS Appointment pada DEC-001 **hanya** untuk kapabilitas pada tabel in-scope di atas;
2. menegaskan OOS yang masih berlaku (Calendar, Slot Generator, Work Order, Notification/Auto Close, dsb.);
3. merujuk DEC-007…011 sebagai rantai otorisasi, bukan mengulang task-specific ke pasal BC.

#### Pros

- Menghilangkan jebakan supersession parsial (risiko #1 DRR).
- BC-000 pasal Lingkup menjadi akurat dengan satu kutipan.
- Tidak menambah fitur.

#### Cons

- Memerlukan formalisasi tertulis BO.
- Harus dikaitkan dengan disposisi eskalasi (BO-001) karena prasyarat `APPROVED` escalation.

### Option B

**Jangan konsolidasi**; BC-000 selalu mengutip rantai DEC-007…011 secara penuh setiap kali menyebut lingkup.

#### Pros

- Tidak ada artefak baru.

#### Cons

- Rawan kutipan parsial/salah oleh penulis berikutnya.
- DRR secara eksplisit meminta BO-05 sebagai P1 untuk pasal Lingkup.

### Option C

**Tarik kembali** sebagian/seluruh perluasan appointment ke OOS DEC-001.

#### Pros

- Baseline sederhana.

#### Cons

- Rollback besar terhadap API/UI/SLA completion facts; tidak selaras delivery yang sudah Approved.

## Cursor Recommendation

**Option A** — konsolidasi pernyataan tanpa mengubah perilaku. Option B gagal memenuhi tujuan anti-salah-kutipan. Option C hanya jika BO menolak seluruh jalur appointment (tidak didukung oleh DEC yang sudah Approved).

**Draf pernyataan kumulatif (untuk diedit/disetujui BO — bukan keputusan):**

> Appointment untuk eskalasi berstatus `APPROVED` **in scope** terbatas pada: booking satu appointment aktif, check-in, completion (`COMPLETED` \| `PARTIALLY_COMPLETED`), no-show, serta Final Resolution sekali per complaint setelah completion, sebagaimana DEC-007…011. **Tetap out of scope:** Calendar View, Slot Generator, Work Order, notifikasi/survey/rating/auto-close terkait appointment, dan penutupan complaint/escalation melalui paket appointment. Status out-of-scope DEC-001 untuk Appointment digantikan oleh batas ini; konsep Schedule Slot generik dan Work Order tetap OOS.

## Business Owner Decision

**APPROVED — Option A** (2026-08-05)

| Field | Value |
|---|---|
| Selected option | **A** |
| Approve cumulative scope text? | **Yes** — Appointment bagian resmi Mode A; mengikuti Complaint Lifecycle yang sama |
| Decision date | 2026-08-05 |
| Approver | Business Owner – ECMP |
| Consolidation DEC ID (jika ada) | Digabung dengan BO-001 → DL-066 Scope Consolidation |
| Notes | Merge BO-001+BO-005 = YES |

## Implementation Notes

- Tulis konsolidasi **setelah atau bersama** BO-001 (prasyarat eskalasi).
- DL-007…011 tetap out-of-scope sebagai *record* pasal BC (task-specific), tetapi **efek lingkupnya** masuk kualifikasi DL-002.

## Affected Artifacts

| Artifact | Role |
|---|---|
| DEC-001 / DL-002 | OOS Appointment diganti batas kumulatif |
| DEC-007…011 / DL-007…011 | Rantai otorisasi |
| API-305…310 · Event appointment/resolution | Batas implementasi |
| UI Escalation Detail / Final Resolution | Permukaan in-scope |
| DEC-013 (completion fact appointment) | Bergantung completion in-scope |
| BC-000 pasal Lingkup Bisnis | Konsumen keputusan |

---

# Resolution Summary

| ID | Topic | Priority | Blocks BC-000 | Decision Needed |
|---|---|---|---|---|
| BO-001 | Head Office Escalation Scope (C-08) | P1 | **RESOLVED** (A) | APPROVED 2026-08-05 — merged → DL-066 |
| BO-002 | SLA Constitution (C-12) | P1 | **RESOLVED** (A) | APPROVED 2026-08-05 → DL-067 |
| BO-003 | Manager Persona vs Dashboard (C-09) | P1 | **RESOLVED** (A) | APPROVED 2026-08-05 → DL-068 |
| BO-004 | UX Package Status Synchronization (C-07) | P1 | **RESOLVED** (A) | APPROVED 2026-08-05 → DL-069 |
| BO-005 | Appointment Scope Consolidation | P1 | **RESOLVED** (A) | APPROVED 2026-08-05 — merged → DL-066 |
| BO-06 | DEC-F4 formal + Board countersign | P2 | NO (kualifikasi) | Formalisasi DEC-F4 |
| BO-07 | Penegasan baseline reversibel DL-004/005 | P2 | NO | Konfirmasi kutipan sebagai rujukan |
| BO-08 | DEFERRED CAP-006 (kalender kerja, pause, diferensiasi) | P2 | NO | Aktivasi atau tetap deferred |
| BO-09 | Dualitas Case State Machine (C-04) | P2 | NO (wajib kualifikasi) | Konfirmasi dualitas dikehendaki |
| BO-10 | Read-audit | P2 | NO | Pertahankan penundaan atau aktifkan |
| BO-11 | Dashboard Manager/Executive + FR-030 | P3 | NO | Jadwal aktivasi |
| BO-12 | OQ-001 Channel app | P3 | NO | Fase 1 vs integration boundary |
| BO-13 | Kebijakan di luar Mode A (BQ-003/006) | P3 | NO | Tetap outside / jadwalkan |
| BO-14 | DEC-021 (O-06) / DEC-022 (O-07) | P3 | NO | Accept/revisi (bersama Board) |

**P1 terbuka:** 0/5 — seluruhnya **APPROVED** (2026-08-05). Merge BO-001+BO-005 = YES.

---

# BC Readiness Checklist

Pemetaan pasal mengikuti peran usulan BC-000 Candidate List DRR-000 §7. Status: **READY** = dapat ditulis dari keputusan APPROVED tanpa menunggu disposisi BO P1; **BLOCKED** = menunggu satu atau lebih keputusan BO-001…005 (atau kualifikasi wajib yang belum diizinkan BO).

| BC Chapter (usulan) | Sumber DL utama | Status | Blocker |
|---|---|---|---|
| Mukadimah / Misi / Batas Produk / Target Architecture / Completion | DL-046 | **READY** | — |
| Kendali Perubahan Konstitusi | DL-047 (+ DL-046 §5) | **READY** | — |
| Lingkup Bisnis | DL-002 + DL-066 | **READY** | Carve-out eskalasi + appointment Mode A |
| Terminologi & Rujukan Aturan (`BR-0xx`) | DL-003 | **READY** | — |
| Aturan Bisnis Dasar (baseline defaults sebagai rujukan) | DL-004 | **READY** | BO-07 (P2) memperkuat, tidak memblokir |
| Komitmen Layanan (target SLA/NFR sebagai rujukan) | DL-005 + DL-067 | **READY** | Satu SLA Constitution (teks BO) |
| Model Komplain (multi-source/target) | DL-006 | **READY** | — |
| Lifecycle / Case State Machine | DL-023 | **READY*** | *wajib kualifikasi dual SoT; BO-09 P2 untuk konfirmasi |
| Aturan Case Mode A | DL-024 | **READY*** | *tandai outside Mode A; clock teknis → BC/BR per DL-067 |
| Waktu & SLA (model bisnis CAP-006) | DL-019 + DL-067 | **READY** | Runtime CAP-006 tetap Deferred |
| Kepemilikan Konfigurasi Workflow | DL-025 | **READY** | — |
| Klasifikasi Aturan (Configuration-First) | DL-026 | **READY** | — |
| Kepemilikan Data (bukan SoR pelanggan) | DL-031 | **READY** | — |
| Kepemilikan Otorisasi (Role-Permission SoT) | DL-056 | **READY** | — |
| Aktor / Persona | DL-001 + DL-068 | **READY** | Manager sah; Workspace deferred |
| Prinsip Pengalaman Kerja (CWX) | DL-027 | **READY*** | *turunan UX Draft sampai Review pasca DL-069 |
| Kewajiban Audit (write-audit) | DL-063 | **READY** | BO-10 P2 untuk read-audit |
| Integritas Audit (immutable + override) | DL-064 | **READY** | — |
| Audit Konfigurasi Kritikal | DL-065 | **READY** | — |
| Integrasi Enterprise / Mode B | — | **BLOCKED** | Mode B CLOSED (Board); batas minimal dari DL-046 saja |

**Ringkas (pasca G0.2D):** pasal bisnis P1 **READY**; integrasi enterprise tetap BLOCKED (disengaja).

---

# Artifact Impact Matrix

| Business Owner Decision | Affected Artifacts | Implementation Phases (setelah keputusan; bukan bagian G0.2C) |
|---|---|---|
| **BO-001** Escalation scope | DEC-001, DEC-F4, BR-007, API/Event eskalasi, UI Escalation, DL-002, BC Lingkup | Phase G1: DEC ratifikasi/pencabutan OOS → sync katalog → (opsional) countersign F4 dengan Board |
| **BO-002** SLA constitution | DL-005/016/017/018/019/024, FRD-005, SLA Matrix, API-314…318, KPI, BC pasal SLA | Phase G1: klausul ruang berlaku di BC & FRD notes → Phase M-18 (Board) konvergensi runtime CAP-006 |
| **BO-003** Manager persona | PDS-001, NAV/IA/WF, DL-062, FRD-006, SEC-RAM, BC pasal Persona | Phase G1: klausul BC → bila Option B: Phase delivery dashboard Manager + role mapping (M-26) |
| **BO-004** UX status sync | UX-FOUNDATION-000, PDS/PWDM/IA, turunan NAV/WF, BC substansi UX | Phase G1: edit status → Review → READY → BO Approval → baru kutip ke BC |
| **BO-005** Appointment cumulative | DEC-001, DEC-007…011, API-305…310, UI appointment/resolution, BC Lingkup | Phase G1: DEC/klausul konsolidasi → pastikan kutipan BC hanya ke pernyataan kumulatif |

```
Business Owner Decision (BO-001…005)
        ↓
Affected Artifacts (DEC / FRD / UX / API / DL kualifikasi)
        ↓
Implementation Phases (documentation sync → optional delivery backlog)
        ↓
BC-000 chapters unblocked
```

---

# Final Recommendation

## Can BC-000 start?

# YES — READY WITH CONDITIONS

## Why

1. **Seluruh keputusan P1 APPROVED** (2026-08-05) oleh Business Owner – ECMP; BO-001+BO-005 digabung sebagai Scope Consolidation Mode A (DL-066).
2. **C-07, C-08, C-09, C-12** mendapat disposisi BO; status UX §2 disinkronkan (DL-069).
3. **Kondisi yang tersisa tidak memblokir drafting pasal bisnis BC-000:** Mode B CLOSED (batas dari DL-046); dual SoT / C-04 sebagai kualifikasi; DEC formal & Review UX paket sebagai follow-up kebersihan; konflik Board (C-01…C-03, C-05, C-06, C-10, C-11) di luar P1.

## Overall Governance Recommendation

| Item | Recommendation |
|---|---|
| Mulai BC-000 sekarang? | **YES — WITH CONDITIONS** (lihat GC-000) |
| Sumber pasal | 19 kandidat DRR §7 + DL-066…069 + teks Decision Summary BO |
| Jangan | Coding Mode B · force-merge dual SoT · menganggap Accept ADR = unlock |
| Follow-up paralel | DEC pencatatan Scope Consolidation · Review UX Foundation · DEC-F4 countersign · Board AB items |

---

## Related

- `docs/governance/GC-000-Governance-Closure-BC-Readiness.md`
- `docs/governance/DL-000-Decision-Log.md`
- `docs/governance/DRR-000-Decision-Readiness-Review.md`
- `docs/governance/BO-WS-000-P1-Business-Owner-Workshop.md`
- `docs/ux/UX-FOUNDATION-000-Complaint-Module-UX-Foundation.md`
- `27 Project Decisions/DEC-001_Business_Baseline_SoT_v1.0.md`
- `18 Architecture Governance/reviews/ECMP_DEC_F4_Escalation_Visibility_Return_v1.0.md`
- `18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md`

## Document control

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-08-05 | Cursor (G0.2C) | Initial Business Owner Resolution Pack — decisions Pending |
| 1.1 | 2026-08-05 | Cursor (G0.2D) | P1 decisions recorded APPROVED; sync with DL-066…069 / GC-000 |

---

*End of BO-000.*
