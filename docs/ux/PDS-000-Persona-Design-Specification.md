# PDS-000 — Persona Design Specification

| Field | Value |
|---|---|
| Document ID | PDS-000 |
| Status | **Superseded by PDS-001** (2026-08-05) — dipertahankan sebagai baseline historis, bukan rujukan aktif untuk closed set persona |
| Lifecycle | Draft → Reviewed → Approved → Baseline → **Superseded** |
| Date | 2026-08-03 |
| Parent | ECMP-CONSTITUTION-001 |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → **PDS-000 (superseded)** → `PDS-001-Persona-Design-Specification.md` |

> **Catatan supersession:** Setelah UX Review, persona **Customer Service** dan **Resolver / Case Handler** di dokumen ini digabung menjadi satu persona **Complaint Officer** di `PDS-001-Persona-Design-Specification.md`. Dokumen ini tidak diedit lebih lanjut untuk mencerminkan closed set baru — lih. PDS-001 untuk model tiga-persona yang berlaku (Complaint Officer · Supervisor · Manager). Isi di bawah ini dipertahankan apa adanya sebagai jejak keputusan sebelum merge.

## Single responsibility

> Mendefinisikan **siapa pengguna Complaint Management Module dan apa yang membentuk pekerjaan mereka.**

PDS-000 **bukan** tempat mendefinisikan: Business Rules, API, Domain Model, Data Ownership, Authorization/role code, Workflow Engine, Architecture Pattern, UI Component, atau Wireframe. Yang sudah punya Source of Truth lain hanya dirujuk, tidak didefinisikan ulang.

## Scope

- Complaint Management Module saja — bukan Enterprise Platform (Auth/SSO/Org Directory ada di luar dokumen ini).
- Empat persona baku, **closed set**: **Customer Service** · **Resolver / Case Handler** · **Supervisor** · **Manager**.
- Tidak ada perubahan Business Rule, API, Database, Entity, atau arsitektur.
- Tidak ada wireframe atau desain layar — itu turunan terpisah, menunggu penugasan berikutnya.

## Keputusan Cakupan: Administrator

Administrator **tidak dihilangkan secara diam-diam** dari lima persona di draft sebelumnya — ini keputusan cakupan yang disengaja.

Administrator dikeluarkan dari closed set PDS-000 karena pekerjaannya adalah **konfigurasi platform** (workflow, SLA, role-permission, approval config), bukan **penanganan case operasional**. PDS-000 khusus memodelkan persona yang bekerja di dalam Complaint Workspace sehari-hari untuk menangani case — sejalan dengan Single Responsibility dokumen ini, yang eksplisit bukan tempat mendefinisikan Workflow Engine atau konfigurasi platform.

Administrator tetap persona yang sah di ranah Authorization/Administration internal ECMP — tapi didefinisikan di dokumen lain, bukan di PDS-000. Pengeluaran ini spesifik untuk PDS-000; bukan pernyataan bahwa Administrator tidak relevan bagi ECMP secara keseluruhan.

## Model Persona: People vs Work Mode

PDS-000 memodelkan **work mode** (jenis pekerjaan yang sedang dilakukan), bukan individu manusia yang tetap.

Draft sebelumnya mencatat bahwa di unit kecil, satu orang bisa merangkap Customer Service dan Handler. PDS-000 tidak membantah realitas itu — satu orang tetap bisa berpindah antar persona tergantung pekerjaan yang sedang dikerjakan pada saat itu. Yang tetap berbeda antar persona adalah **job, prioritas informasi, dan tanggung jawab per mode kerja** (Bagian 2–5), bukan siapa orangnya.

Konsekuensi bagi turunan berikutnya: desain tidak boleh mengasumsikan satu akun = satu persona secara permanen. Satu akun bisa mengaktifkan lebih dari satu persona pada waktu berbeda, masing-masing tunduk pada Workspace Goal dan JTBD personanya sendiri saat mode itu aktif.

## Status dokumen sebelumnya

`12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` (status Draft, 2026-07-21) berisi lima persona termasuk Administrator dan level *service journey*. Untuk pertanyaan **"siapa & tujuan persona"**, PDS-000 menggantikannya sebagai baseline. Detail journey API-level di dokumen tsb tetap berlaku sampai direvisi terpisah — PDS-000 tidak mendefinisikan journey.

---

## 1. Persona Catalog

| Persona | Posisi dalam Case Lifecycle | Tujuan Utama | Bukan tanggung jawabnya |
|---|---|---|---|
| **Customer Service** | Titik masuk komplain | Mencatat complaint/inquiry cepat & akurat; memastikan konteks pelanggan terekam sejak awal | Tidak menentukan assignment, tidak menutup case, tidak approve resolution |
| **Resolver / Case Handler** | Eksekutor penanganan setelah assignment | Menyelesaikan case sesuai SLA; mengajukan hasil penanganan untuk review dengan bukti yang cukup | Tidak melakukan assignment awal, tidak approve closure sendiri, tidak melihat backlog lintas unit lain |
| **Supervisor** | Pengawas unit & gatekeeper transisi kritikal | Distribusi beban kerja adil; approve/reject hasil penanganan; menangani eskalasi unit; menjaga tidak ada case terlantar | Tidak menangani case end-to-end sendiri (mendelegasikan), tidak mengubah konfigurasi platform |
| **Manager** | Pemantau kinerja layanan lintas unit | Melihat tren antrian, SLA achievement, dan KPI tanpa menyentuh data transaksi | Tidak create/assign/close case, tidak melihat detail transaksi individual kecuali by exception |

**Catatan peran teknis (referensi, bukan definisi):** Customer Service, Resolver/Handler, dan Supervisor punya padanan peran operasional yang sudah dikenal sistem Authorization saat ini. **Manager belum punya padanan peran teknis khusus** di Authorization — ini gap terbuka yang dicatat, bukan diselesaikan di dokumen ini (menyelesaikannya adalah perubahan Authorization, di luar scope PDS).

---

## 2. Workspace Goal

Bukan Mission (tujuan jangka panjang persona, Bagian 1) dan bukan JTBD (job situasional, Bagian 3). Workspace Goal menjawab satu pertanyaan: **seperti apa satu sesi kerja yang selesai dengan baik?**

### Customer Service
Sesi kerja berhasil bila setiap komplain yang masuk hari itu tercatat lengkap dan akurat sejak kontak pertama — tidak ada case yang harus diperbaiki ulang oleh pihak lain karena data intake tidak lengkap.

### Resolver / Case Handler
Sesi kerja berhasil bila setiap case yang assigned pada hari itu bergerak maju — selesai diajukan untuk review, atau statusnya jelas dan bisa dijelaskan — tidak ada case yang diam tanpa progres yang bisa dipertanggungjawabkan.

### Supervisor
Sesi kerja berhasil bila tidak ada case yang menunggu tanpa pemilik jelas, tidak ada SLA yang terlewat tanpa diketahui lebih dulu, dan setiap pengajuan hasil sudah diputuskan (approve/reject) sebelum sesi berakhir.

### Manager
Sesi kerja berhasil bila gambaran kinerja layanan hari itu (SLA, backlog, tren) sudah dipahami dan cukup untuk mengambil atau mengonfirmasi keputusan — tanpa perlu verifikasi manual ke data operasional.

---

## 3. Job-to-be-Done Matrix

Format: *Ketika [situasi] → saya ingin [motivasi] → sehingga [hasil]*.

### Customer Service
- Ketika pelanggan menghubungi dengan keluhan baru → saya ingin mencatatnya cepat dan lengkap → sehingga tidak ada informasi hilang di titik masuk.
- Ketika pelanggan follow-up → saya ingin melihat status/riwayat case tanpa bertanya ulang ke pelanggan → sehingga interaksi terasa personal, bukan birokratis.
- Ketika informasi pelanggan tidak lengkap → saya ingin tahu apa yang kurang saat itu juga → sehingga saya melengkapinya sebelum case berpindah tangan, bukan setelahnya.

### Resolver / Case Handler
- Ketika case masuk ke antrian saya → saya ingin langsung paham apa yang harus dilakukan → sehingga saya tidak membuang waktu memahami ulang konteks.
- Ketika saya menangani case → saya ingin tahu sisa SLA → sehingga saya bisa memprioritaskan tanpa dikejutkan keterlambatan.
- Ketika penanganan selesai → saya ingin mengajukan hasil dengan bukti yang relevan sekaligus → sehingga proses review tidak bolak-balik.
- Ketika hasil penanganan saya ditolak reviewer → saya ingin tahu alasan penolakan secara spesifik → sehingga saya bisa memperbaiki tanpa mengulang investigasi dari awal.
- Ketika case yang pernah saya tangani dibuka kembali (reopened) → saya ingin melanjutkan dengan konteks penanganan sebelumnya utuh → sehingga saya tidak mengulang dari nol.
- Ketika case yang saya tangani dieskalasi ke Supervisor → saya ingin tahu informasi apa yang diminta dari saya → sehingga saya bisa memberi konteks tanpa kehilangan pemahaman atas case tersebut.

### Supervisor
- Ketika case baru masuk → saya ingin tahu siapa yang punya kapasitas → sehingga distribusi adil dan tidak ada unit overload.
- Ketika ada case mendekati/melewati SLA → saya ingin diberi tahu sebelum menjadi masalah → sehingga saya bisa intervensi lebih awal.
- Ketika handler mengajukan hasil → saya ingin menilai kelengkapannya dengan cepat dan memutuskan approve atau reject → sehingga closure atau pengembalian ke handler tidak tertunda tanpa alasan jelas.
- Ketika eskalasi masuk → saya ingin tahu alasan dan konteksnya sekaligus → sehingga saya tidak menelusuri ulang seluruh riwayat case.
- Ketika ada permintaan reopen atas case yang sudah closed → saya ingin melihat alasan reopen dan riwayat closure sebelumnya → sehingga saya bisa menyetujui dengan konteks lengkap, bukan asumsi.

### Manager
- Ketika mulai bekerja → saya ingin tahu kondisi layanan hari ini secara agregat → sehingga saya tahu ke mana mengarahkan perhatian.
- Ketika melihat tren SLA → saya ingin tahu unit mana yang berisiko → sehingga saya mengambil keputusan tanpa membaca setiap case.
- Ketika laporan diminta pihak lain → saya ingin angka yang saya lihat sudah rekonsiliasi dengan operasional → sehingga saya tidak perlu verifikasi manual.

---

## 4. Information Priority Matrix

Tiga tingkat: **Immediate** (harus terlihat pertama, tanpa dicari) · **Contextual** (dibutuhkan saat mengambil keputusan, tidak harus paling depan) · **On-demand** (dicari hanya saat dibutuhkan).

Item Immediate diurutkan berdasarkan urgensi pengambilan keputusan, bukan volume data — bila lebih dari satu item bersaing untuk perhatian pertama, urutan di bawah menentukan mana yang menang.

| Persona | Immediate (urut prioritas) | Contextual | On-demand |
|---|---|---|---|
| Customer Service | 1. Identitas pelanggan yang sedang dilayani<br>2. Ada/tidaknya case aktif miliknya | Kategori/kanal komplain sebelumnya; status case yang sedang berjalan | Riwayat lengkap seluruh interaksi historis pelanggan |
| Resolver / Handler | 1. Case yang sedang assigned<br>2. Sisa SLA<br>3. Aksi yang boleh dilakukan sekarang | Evidence/attachment terkait; catatan penanganan sebelumnya (bila reopened) | Riwayat case lain milik pelanggan yang sama (referensi, bukan aksi) |
| Supervisor | 1. Eskalasi baru masuk<br>2. Case mendekati/lewat SLA<br>3. Antrian belum ter-assign | Beban kerja tiap handler/unit; hasil penanganan menunggu approval | Detail lengkap satu case saat melakukan assignment/approval spesifik |
| Manager | 1. Indikator agregat yang menyimpang dari target (SLA breach rate, backlog growth) *(item tunggal — tidak ada kompetisi prioritas)* | Tren per unit/kategori/periode | Drill-down ke detail unit saat angka agregat mencurigakan (bukan detail transaksi individual) |

---

## 5. Workspace Responsibility Matrix

Dipetakan terhadap status Case baseline (`DOM-ECMF-003` — Case State Machine). R = Responsible (mengerjakan) · A = Accountable (bertanggung jawab atas keputusan) · C = Consulted (sumber konteks) · I = Informed (perlu tahu, tidak bertindak) · — = tidak terlibat.

Matriks ini **diturunkan dari JTBD di Bagian 3** — setiap R/A/C pada tabel berikut mengacu ke job yang sudah dinyatakan di sana. Sel tanpa job pendukung diberi `—`, bukan diasumsikan.

| Tahap Lifecycle | Customer Service | Resolver / Handler | Supervisor | Manager |
|---|---|---|---|---|
| `REGISTERED` (intake) | R | — | I | — |
| `ASSIGNED` (distribusi) | I | I | R/A | — |
| `IN_PROGRESS` (penanganan) | C *(bila pelanggan follow-up)* | R/A | I *(pantau progres & SLA)* | — |
| Eskalasi *(lintas tahap, kondisional)* | I | C | R/A | — |
| `PENDING_REVIEW` (pengajuan hasil) | — | R | A | — |
| Reject Review *(`PENDING_REVIEW → IN_PROGRESS`, ditolak reviewer)* | — | R | A | — |
| `CLOSED` (penutupan) | I | I | A | I *(masuk agregat KPI)* |
| `REOPENED` | R *(pengajuan ulang oleh pelanggan)* | R | A | I *(mempengaruhi tren agregat)* |

---

## 6. Common vs Unique Analysis

### Common — berlaku untuk keempat persona
- Butuh satu identitas case yang konsisten — tidak boleh ada versi berbeda tentang status/pemilik case yang sama antar persona.
- Sadar SLA, meski granularitasnya beda (Handler: sisa waktu case-nya; Manager: tren agregat).
- Butuh tahu **apa yang berubah sejak terakhir dilihat**, tanpa membaca ulang seluruh riwayat.
- Bergantung pada kelengkapan data di titik intake (Customer Service) — semua persona lain mewarisi kualitas data itu.

### Unique — per persona
- **Customer Service**: ukuran sukses adalah kecepatan & akurasi input, bukan penyelesaian case.
- **Resolver/Handler**: bekerja mendalam pada sedikit case dalam satu waktu — kedalaman konteks per-case lebih penting daripada pandangan lintas-case.
- **Supervisor**: satu-satunya persona yang butuh pandangan lintas-case (queue-level) **sekaligus** otoritas keputusan pada titik kritikal (assign, approve, eskalasi). Ini titik tegang yang perlu diperhatikan turunan berikutnya — bukan sesuatu yang diselesaikan di sini.
- **Manager**: satu-satunya persona yang bekerja di level agregat/tren, bukan case individual; satu-satunya yang secara desain sepenuhnya read-only.

---

## 7. Persona Design Constitution

Aturan yang mengikat semua pekerjaan UX turunan (workflow analysis, wireframe, dashboard redesign) yang merujuk persona:

1. **Four Personas, Closed Set** — Customer Service, Resolver/Handler, Supervisor, Manager. Menambah persona kelima memerlukan revisi PDS, bukan asumsi implisit di dokumen turunan.
2. **Persona ≠ Role String** — padanan ke peran teknis adalah referensi, bukan definisi ulang Authorization. Perubahan role code adalah keputusan Authorization, bukan PDS.
3. **Manager is Read-Only by Design** — persona Manager tidak pernah mendapat kemampuan create/assign/close/edit. Begitu ada kebutuhan itu, itu bukan lagi persona Manager.
4. **Work Before Interface** — setiap turunan wajib menjawab "pekerjaan apa" sebelum "layar apa".
5. **No Persona Redefinition Without Version Bump** — perubahan tujuan/boundary persona menghasilkan PDS-001, bukan overwrite diam-diam di PDS-000.
6. **Reference, Don't Redefine** — state machine (`DOM-ECMF-003`) dan peran teknis existing hanya dirujuk di sini, tidak didefinisikan ulang.
7. **Business Rule Silence = Open Gap, Not Invented Answer** — bila ketentuan tidak eksplisit di Business Rules/FRD existing (contoh: Manager belum punya role code resmi), PDS mencatatnya sebagai gap terbuka, bukan mengarang penyelesaian.
8. **Single Source for "Who"** — begitu PDS-000 mencapai status Approved/Baseline pada lifecycle dokumennya, ia menjadi rujukan tunggal untuk pertanyaan siapa persona dan apa tujuannya, menggantikan `ECMP_Personas_And_Journeys_v0.1.md` untuk pertanyaan itu secara spesifik.
9. **Personas Model Work, Not People** — satu individu bisa menjalankan lebih dari satu persona tergantung pekerjaan yang sedang dilakukan (lih. "Model Persona: People vs Work Mode"). Desain turunan tidak boleh mengasumsikan satu akun = satu persona tetap.
10. **Responsibility Follows JTBD** — Workspace Responsibility Matrix (Bagian 5) tidak boleh memuat R/A/C untuk persona mana pun tanpa job yang mendasarinya di Bagian 3. Revisi matriks wajib disertai revisi JTBD yang sepadan, atau sebaliknya.
11. **Administrator Out of Workspace Scope** — Administrator adalah persona konfigurasi platform, bukan persona operasional Complaint Workspace, dan tidak termasuk closed set PDS-000 (lih. "Keputusan Cakupan: Administrator"). Ini keputusan cakupan dokumen, bukan penilaian relevansi Administrator bagi ECMP.

## Related
- `18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md`
- `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` (DOM-ECMF-003)
- `12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` (superseded untuk "siapa & tujuan"; journey level tetap berlaku)
- `03 Functional Requirements/` — FRD Complaint Management, Case Management, Escalation & Resolution, Dashboard & Queue, KPI & SLA

## Future Work
Persona Workflow & Decision Model (analisis alur kerja harian per persona) dan wireframe adalah turunan terpisah dari PDS-000 — di luar ruang lingkup dokumen ini.
