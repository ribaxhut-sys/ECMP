# PDS-001 — Persona Design Specification (Revisi Merge: Complaint Officer)

| Field | Value |
|---|---|
| Document ID | PDS-001 |
| Status | Draft — menggantikan PDS-000 untuk closed set persona; menunggu Review/Approval |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Date | 2026-08-05 |
| Supersedes | `PDS-000-Persona-Design-Specification.md` (v1.0, status Reviewed) |
| Parent | ECMP-CONSTITUTION-001 |
| Subordination | Board → ADR → EA → ECMP-CONSTITUTION-001 → **PDS-001** → PWDM-001 → IA-001 → NAV-001 → WF-000 → WF-001 |
| Trigger | UX-001 Documentation Update — hasil UX Review: memisahkan Front Office/Customer Service dari Complaint Officer menciptakan kompleksitas UX yang tidak perlu; sistem memodelkan satu persona operasional |

## Single responsibility

> Mendefinisikan **siapa pengguna Complaint Management Module dan apa yang membentuk pekerjaan mereka** — versi revisi setelah keputusan UX Review menggabungkan Customer Service dan Resolver/Case Handler menjadi satu persona **Complaint Officer**.

PDS-001 **bukan** tempat mendefinisikan: Business Rules, API, Domain Model, Data Ownership, Authorization/role code, Workflow Engine, Architecture Pattern, UI Component, atau Wireframe. Yang sudah punya Source of Truth lain hanya dirujuk, tidak didefinisikan ulang.

## Kenapa PDS-001, bukan overwrite PDS-000

PDS-000 §7 poin 5 (*"No Persona Redefinition Without Version Bump"*) mengikat dirinya sendiri: perubahan tujuan/boundary persona menghasilkan dokumen versi baru, bukan overwrite diam-diam. PDS-001 adalah pemenuhan aturan itu. PDS-000 tetap ada sebagai baseline historis (tidak dihapus) dan diberi penanda superseded di berkasnya sendiri.

## Ringkasan Perubahan dari PDS-000

- **Customer Service** dan **Resolver / Case Handler** digabung menjadi satu persona: **Complaint Officer**.
- Closed set berubah dari **empat** menjadi **tiga**: Complaint Officer · Supervisor · Manager.
- Perbedaan otoritas (mis. siapa yang boleh assign/close case) **tidak lagi dimodelkan sebagai batas persona** — itu menjadi urusan Role & Permission (Authorization), sejalan dengan PDS-000 §7 poin 2 (*"Persona ≠ Role String"*) yang sudah berlaku sebelum revisi ini.
- Administrator **tetap** di luar closed set, tidak berubah dari keputusan cakupan PDS-000 (lih. "Keputusan Cakupan: Administrator" di bawah, dipertahankan apa adanya).
- Model **People vs Work Mode** (PDS-000) tidak berubah — hanya jumlah dan batas work mode yang direvisi.

## Keputusan Cakupan: Administrator

*(Dipertahankan dari PDS-000 tanpa perubahan substansi.)*

Administrator **tidak dihilangkan secara diam-diam** — ini keputusan cakupan yang disengaja. Administrator dikeluarkan dari closed set karena pekerjaannya adalah **konfigurasi platform** (workflow, SLA, role-permission, approval config), bukan **penanganan case operasional**. PDS-001 khusus memodelkan persona yang bekerja di dalam Complaint Workspace sehari-hari untuk menangani case.

Administrator tetap persona yang sah di ranah Authorization/Administration internal ECMP — tapi didefinisikan di dokumen lain, bukan di PDS-001.

## Model Persona: People vs Work Mode

*(Dipertahankan dari PDS-000, tidak direvisi.)*

PDS-001 memodelkan **work mode** (jenis pekerjaan yang sedang dilakukan), bukan individu manusia yang tetap. Satu akun bisa mengaktifkan lebih dari satu persona pada waktu berbeda, masing-masing tunduk pada Workspace Goal dan JTBD personanya sendiri saat mode itu aktif.

Konsekuensi merge: penggabungan Customer Service dan Resolver/Handler menjadi Complaint Officer **memperkuat** prinsip ini, bukan menyimpanginya — kedua work mode itu sudah lama diakui bisa dirangkap satu orang di unit kecil (catatan PDS-000 §"Model Persona"). PDS-001 mengangkat pengakuan itu menjadi satu persona formal, bukan dua persona yang kebetulan sering dirangkap.

## Status dokumen sebelumnya

`12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` (status Draft, 2026-07-21, ID dokumen UX-001) berisi lima persona level *service journey* (P-01 CS Agent, P-02 Supervisor, P-03 Administrator, P-04 Handler, P-05 Manager/Executive) — direvisi mengikuti merge ini (lih. dokumen tsb, bagian Persona P-01/P-04 digabung menjadi Complaint Officer). Untuk pertanyaan **"siapa & tujuan persona"**, PDS-001 adalah rujukan tunggal, menggantikan baik PDS-000 maupun dokumen UX-001 tsb untuk pertanyaan itu.

---

## 1. Persona Catalog

| Persona | Posisi dalam Case Lifecycle | Tujuan Utama | Bukan tanggung jawabnya |
|---|---|---|---|
| **Complaint Officer** | Titik masuk komplain **hingga** eksekusi penanganan setelah assignment | Mencatat complaint/inquiry cepat & akurat sejak kontak pertama; menyelesaikan case sesuai SLA; mengajukan hasil penanganan untuk review dengan bukti yang cukup | Tidak melakukan assignment awal ke unit/officer lain, tidak approve closure sendiri, tidak melihat backlog lintas unit lain — **kecuali diberi izin eksplisit oleh Authorization** (lih. Bagian 7 poin 2 dan Catatan Otoritas di bawah) |
| **Supervisor** | Pengawas unit & gatekeeper transisi kritikal | Distribusi beban kerja adil; approve/reject hasil penanganan; menangani eskalasi unit; menjaga tidak ada case terlantar | Tidak menangani case end-to-end sendiri (mendelegasikan), tidak mengubah konfigurasi platform |
| **Manager** | Pemantau kinerja layanan lintas unit | Melihat tren antrian, SLA achievement, dan KPI tanpa menyentuh data transaksi | Tidak create/assign/close case, tidak melihat detail transaksi individual kecuali by exception |

**Catatan Otoritas (Assign/Close "if permitted"):** tugas *assign complaint* dan *close complaint* muncul pada tanggung jawab Complaint Officer hanya sebagai kapabilitas kondisional — dijalankan bila Authorization memberi izin (mis. unit kecil tanpa Supervisor terpisah). Secara default, R/A untuk `ASSIGNED` dan `CLOSED` tetap milik Supervisor (lih. Bagian 5). Ini bukan pengecualian ad hoc: PDS-000 §7 poin 2 sudah menetapkan **Persona ≠ Role String** sebelum revisi ini — kapabilitas kondisional semacam ini adalah keputusan Authorization, bukan definisi ulang persona.

**Catatan peran teknis (referensi, bukan definisi):** Complaint Officer dan Supervisor punya padanan peran operasional yang sudah dikenal sistem Authorization saat ini (gabungan padanan Customer Service + Resolver/Handler sebelumnya). **Manager belum punya padanan peran teknis khusus** di Authorization — gap terbuka yang dicatat, bukan diselesaikan di dokumen ini.

---

## 2. Workspace Goal

### Complaint Officer
Sesi kerja berhasil bila **setiap komplain yang masuk hari itu tercatat lengkap dan akurat sejak kontak pertama**, dan **setiap case yang sedang ditangani bergerak maju** — selesai diajukan untuk review, atau statusnya jelas dan bisa dipertanggungjawabkan. Tidak ada case yang harus diperbaiki ulang pihak lain karena data intake tidak lengkap, dan tidak ada case yang diam tanpa progres yang bisa dipertanggungjawabkan.

*(Gabungan langsung dari Workspace Goal Customer Service + Resolver/Case Handler di PDS-000 §2 — tidak ada target baru yang ditambahkan.)*

### Supervisor
Sesi kerja berhasil bila tidak ada case yang menunggu tanpa pemilik jelas, tidak ada SLA yang terlewat tanpa diketahui lebih dulu, dan setiap pengajuan hasil sudah diputuskan (approve/reject) sebelum sesi berakhir.

### Manager
Sesi kerja berhasil bila gambaran kinerja layanan hari itu (SLA, backlog, tren) sudah dipahami dan cukup untuk mengambil atau mengonfirmasi keputusan — tanpa perlu verifikasi manual ke data operasional.

---

## 3. Job-to-be-Done Matrix

Format: *Ketika [situasi] → saya ingin [motivasi] → sehingga [hasil]*.

### Complaint Officer
*(Gabungan JTBD Customer Service + Resolver/Case Handler dari PDS-000 §3 — tidak ada job baru.)*

- Ketika pelanggan menghubungi dengan keluhan baru → saya ingin mencatatnya cepat dan lengkap → sehingga tidak ada informasi hilang di titik masuk.
- Ketika pelanggan follow-up → saya ingin melihat status/riwayat case tanpa bertanya ulang ke pelanggan → sehingga interaksi terasa personal, bukan birokratis.
- Ketika informasi pelanggan tidak lengkap → saya ingin tahu apa yang kurang saat itu juga → sehingga saya melengkapinya sebelum case berpindah tangan, bukan setelahnya.
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

| Persona | Immediate (urut prioritas) | Contextual | On-demand |
|---|---|---|---|
| Complaint Officer | 1. Identitas pelanggan yang sedang dilayani (mode intake) *atau* case yang sedang assigned (mode penanganan)<br>2. Ada/tidaknya case aktif miliknya (mode intake) *atau* sisa SLA (mode penanganan)<br>3. Aksi yang boleh dilakukan sekarang (mode penanganan) | Kategori/kanal komplain sebelumnya; status case yang sedang berjalan; evidence/attachment terkait; catatan penanganan sebelumnya (bila reopened) | Riwayat lengkap seluruh interaksi historis pelanggan; riwayat case lain milik pelanggan yang sama (referensi, bukan aksi) |
| Supervisor | 1. Eskalasi baru masuk<br>2. Case mendekati/lewat SLA<br>3. Antrian belum ter-assign | Beban kerja tiap handler/unit; hasil penanganan menunggu approval | Detail lengkap satu case saat melakukan assignment/approval spesifik |
| Manager | 1. Indikator agregat yang menyimpang dari target (SLA breach rate, backlog growth) *(item tunggal — tidak ada kompetisi prioritas)* | Tren per unit/kategori/periode | Drill-down ke detail unit saat angka agregat mencurigakan (bukan detail transaksi individual) |

**Catatan penggabungan:** Complaint Officer memiliki dua mode kerja situasional (intake vs penanganan aktif) yang sebelumnya adalah dua persona terpisah. Immediate #1–#3 di atas **bukan** tiga item yang bersaing serentak — melainkan dua pasang item yang aktif bergantian sesuai konteks case yang sedang dibuka (intake baru vs case assigned). Ini konsisten dengan Bagian 3 IA-001 revisi (lih. PDS-001 tidak menghapus perbedaan konteks, hanya menyatukan siapa yang mengerjakannya).

---

## 5. Workspace Responsibility Matrix

Dipetakan terhadap status Case baseline (`DOM-ECMF-003` — Case State Machine). R = Responsible (mengerjakan) · A = Accountable (bertanggung jawab atas keputusan) · C = Consulted (sumber konteks) · I = Informed (perlu tahu, tidak bertindak) · — = tidak terlibat.

Matriks ini diturunkan langsung dari penggabungan baris Customer Service dan Resolver/Handler di PDS-000 §5, mengambil nilai terkuat pada tahap yang tumpang tindih.

| Tahap Lifecycle | Complaint Officer | Supervisor | Manager |
|---|---|---|---|
| `REGISTERED` (intake) | R | I | — |
| `ASSIGNED` (distribusi) | I | R/A | — |
| `IN_PROGRESS` (penanganan) | R/A | I *(pantau progres & SLA)* | — |
| Eskalasi *(lintas tahap, kondisional)* | C | R/A | — |
| `PENDING_REVIEW` (pengajuan hasil) | R | A | — |
| Reject Review *(`PENDING_REVIEW → IN_PROGRESS`, ditolak reviewer)* | R | A | — |
| `CLOSED` (penutupan) | I | A | I *(masuk agregat KPI)* |
| `REOPENED` | R *(pengajuan ulang oleh pelanggan maupun kelanjutan penanganan)* | A | I *(mempengaruhi tren agregat)* |

**Catatan penggabungan per tahap:**
- `REGISTERED`: Customer Service sebelumnya R, Handler tidak terlibat (—) → Complaint Officer mewarisi **R**.
- `ASSIGNED`: kedua persona lama sama-sama **I** → tidak berubah.
- `IN_PROGRESS`: Handler sebelumnya R/A, Customer Service C *(bila follow-up)* → Complaint Officer mewarisi **R/A** (nilai terkuat); kontak follow-up pelanggan pada case yang sedang ditangani tetap bagian pekerjaan yang sama, bukan konsultasi lintas persona lagi.
- Eskalasi: Handler sebelumnya **C**, Customer Service **I** → Complaint Officer mewarisi **C** (nilai terkuat).
- `PENDING_REVIEW`/Reject Review: hanya Handler yang punya baris (**R**); Customer Service tidak terlibat → Complaint Officer **R**, tidak berubah secara substansi.
- `CLOSED`: kedua persona lama **I** → tidak berubah.
- `REOPENED`: Customer Service **R** *("pengajuan ulang oleh pelanggan")*, Handler **R** *(melanjutkan penanganan)* → keduanya sudah **R**, digabung menjadi satu baris **R** yang mencakup kedua konteks.

Tidak ada kenaikan otoritas: Assignment dan Closure **tetap** R/A milik Supervisor. Penggabungan ini menyatukan siapa yang mengerjakan intake dan penanganan, bukan memindahkan keputusan gatekeeping dari Supervisor ke Complaint Officer.

---

## 6. Common vs Unique Analysis

### Common — berlaku untuk ketiga persona
- Butuh satu identitas case yang konsisten — tidak boleh ada versi berbeda tentang status/pemilik case yang sama antar persona.
- Sadar SLA, meski granularitasnya beda (Complaint Officer: sisa waktu case-nya; Manager: tren agregat).
- Butuh tahu **apa yang berubah sejak terakhir dilihat**, tanpa membaca ulang seluruh riwayat.
- Kualitas data di titik intake kini menjadi tanggung jawab persona yang sama yang juga menanganinya (Complaint Officer) — Supervisor dan Manager tetap mewarisi kualitas data itu dari Complaint Officer.

### Unique — per persona
- **Complaint Officer**: satu-satunya persona dengan dua mode kerja situasional dalam satu closed set — kecepatan & akurasi input saat intake, kedalaman konteks per-case saat menangani. Ini adalah **tension internal** yang sebelumnya terbagi ke dua persona berbeda (PDS-000 §6); revisi ini menyatukannya secara sengaja sebagai satu rentang kerja, bukan menghilangkan kompleksitasnya. Turunan berikutnya (PWDM-001, IA-001) wajib memperlakukan kedua mode ini sebagai konteks yang berbeda dalam satu persona, bukan mengasumsikan satu mode saja.
- **Supervisor**: satu-satunya persona yang butuh pandangan lintas-case (queue-level) **sekaligus** otoritas keputusan pada titik kritikal (assign, approve, eskalasi).
- **Manager**: satu-satunya persona yang bekerja di level agregat/tren, bukan case individual; satu-satunya yang secara desain sepenuhnya read-only.

---

## 7. Persona Design Constitution

Aturan yang mengikat semua pekerjaan UX turunan (workflow analysis, wireframe, dashboard redesign) yang merujuk persona:

1. **Three Personas, Closed Set** — Complaint Officer, Supervisor, Manager. Menambah atau memecah persona memerlukan revisi PDS berikutnya, bukan asumsi implisit di dokumen turunan.
2. **Persona ≠ Role String** — padanan ke peran teknis adalah referensi, bukan definisi ulang Authorization. Perubahan role code (termasuk kapabilitas kondisional assign/close "if permitted") adalah keputusan Authorization, bukan PDS.
3. **Manager is Read-Only by Design** — persona Manager tidak pernah mendapat kemampuan create/assign/close/edit. Begitu ada kebutuhan itu, itu bukan lagi persona Manager.
4. **Work Before Interface** — setiap turunan wajib menjawab "pekerjaan apa" sebelum "layar apa".
5. **No Persona Redefinition Without Version Bump** — perubahan tujuan/boundary persona menghasilkan dokumen versi berikutnya (PDS-002, dst.), bukan overwrite diam-diam di PDS-001.
6. **Reference, Don't Redefine** — state machine (`DOM-ECMF-003`) dan peran teknis existing hanya dirujuk di sini, tidak didefinisikan ulang.
7. **Business Rule Silence = Open Gap, Not Invented Answer** — bila ketentuan tidak eksplisit di Business Rules/FRD existing, PDS mencatatnya sebagai gap terbuka, bukan mengarang penyelesaian.
8. **Single Source for "Who"** — begitu PDS-001 mencapai status Approved/Baseline pada lifecycle dokumennya, ia menjadi rujukan tunggal untuk pertanyaan siapa persona dan apa tujuannya, menggantikan PDS-000 dan `ECMP_Personas_And_Journeys_v0.1.md` untuk pertanyaan itu secara spesifik.
9. **Personas Model Work, Not People** — satu individu bisa menjalankan lebih dari satu persona tergantung pekerjaan yang sedang dilakukan. Desain turunan tidak boleh mengasumsikan satu akun = satu persona tetap.
10. **Responsibility Follows JTBD** — Workspace Responsibility Matrix (Bagian 5) tidak boleh memuat R/A/C untuk persona mana pun tanpa job yang mendasarinya di Bagian 3. Revisi matriks wajib disertai revisi JTBD yang sepadan, atau sebaliknya.
11. **Administrator Out of Workspace Scope** — Administrator adalah persona konfigurasi platform, bukan persona operasional Complaint Workspace, dan tidak termasuk closed set PDS-001 (lih. "Keputusan Cakupan: Administrator"). Ini keputusan cakupan dokumen, bukan penilaian relevansi Administrator bagi ECMP.
12. **Merge Preserves Function, Not Just Name** — penggabungan Customer Service dan Resolver/Handler menjadi Complaint Officer (Bagian 1–6) tidak menghilangkan satu pun tanggung jawab, JTBD, atau kebutuhan informasi dari kedua persona lama; keduanya digabung utuh ke dalam satu closed set, bukan salah satunya diprioritaskan atas yang lain.

## Related
- `18 Architecture Governance/ECMP_CONSTITUTION_001_Complaint_Management_Module_Constitution_v1.1.md`
- `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` (DOM-ECMF-003)
- `docs/ux/PDS-000-Persona-Design-Specification.md` (superseded — dipertahankan sebagai baseline historis)
- `12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` (superseded untuk "siapa & tujuan"; journey level tetap berlaku, direvisi mengikuti merge ini)
- `03 Functional Requirements/` — FRD Complaint Management, Case Management, Escalation & Resolution, Dashboard & Queue, KPI & SLA

## Future Work
Revisi PWDM-001, IA-001, NAV-001, WF-000, WF-001-01, dan WF-PLAN-001 mengikuti closed set tiga-persona PDS-001 — dikerjakan sebagai bagian dari paket UX-001 Documentation Update yang sama, bukan penugasan terpisah.
