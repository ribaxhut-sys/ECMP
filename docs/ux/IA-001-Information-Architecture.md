# IA-001 — Information Architecture

| Field | Value |
|---|---|
| Document ID | IA-001 |
| Status | Draft — revisi mengikuti merge persona PDS-001 (UX-001 Documentation Update) |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Date | 2026-08-05 |
| Parent | PWDM-001 |
| Subordination | ECMP-CONSTITUTION-001 → PDS-001 → PWDM-001 → **IA-001** → (future) Wireframe |
| Revision note | Kolom Customer Service dan Resolver/Handler digabung menjadi **Complaint Officer** di seluruh matriks, mengikuti PDS-001 §1. Ownership diambil dari nilai terkuat antara dua kolom lama (P > S > R > H); tidak ada objek atau kepemilikan yang dihapus. |

## Single responsibility

> Menentukan **apa informasi yang dibutuhkan tiap persona, kapan, di mana ia berada, bagaimana dikelompokkan, dan bagaimana navigasi mengalir** — di atas kerja yang sudah dipetakan PWDM-001. Bukan layar, bukan komponen, bukan visual.

IA-001 tidak mendefinisikan ulang persona (PDS-001), workflow/keputusan (PWDM-001), Business Rule, Authorization, atau CWX. Semua istilah informasi yang dipakai di sini sudah muncul di PDS-001 §4 (Information Priority Matrix), PDS-001 §5 (Workspace Responsibility Matrix), PWDM-001 §2 (Decision Model), atau entity Complaint Module yang sudah ada (`06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md`, `20 Domain Architecture/ECMF/CASE_AGGREGATE.md`).

---

## 1. Information Inventory

| # | Information Object | Definisi (istilah existing) | Sumber |
|---|---|---|---|
| 1 | **Complaint Identity** | case_id, case_type, priority, status, subject | Case Header (Data Dictionary); "case aktif/closed" (PWDM-001) |
| 2 | **Customer Information** | Identitas & kanal kontak pelanggan yang sedang dilayani | Customer Reference (Data Dictionary); PDS-001 §4 Immediate Complaint Officer (mode intake) |
| 3 | **Case Summary** | Kategori/kanal komplain, ringkasan (subject/description) | PDS-001 §4 Contextual Complaint Officer; Case Header |
| 4 | **Assignment** | Case yang sedang assigned ke Complaint Officer; assignment context | PDS-001 §4 Immediate Complaint Officer (mode penanganan); §5 `ASSIGNED` |
| 5 | **Priority** | LOW/MEDIUM/HIGH/CRITICAL | Asal-usul bukan teks literal PDS-001/PWDM-001 — sumbernya Case Aggregate value object (Data Dictionary/DOM-ECMF-002). Dimasukkan karena mengoperasionalkan "urgensi"/"case mana dikerjakan lebih dulu" yang disebut PWDM-001 §2 Complaint Officer tanpa menyebut nama field. Bila field ini belum dianggap bagian resmi vocabulary PDS-001/PWDM-001, objek ini gugur dari inventori sampai dirujuk eksplisit di salah satu baseline. |
| 6 | **SLA** | Sisa SLA per case; status mendekati/lewat SLA | PDS-001 §4 Immediate Complaint Officer (mode penanganan) & Supervisor |
| 7 | **Evidence / Attachment** | Bukti/berkas pendukung penanganan | PDS-001 §4 Contextual Complaint Officer; PWDM-001 Critical decisions Complaint Officer |
| 8 | **Resolution** | Hasil penanganan yang menutup case | PDS-001 §5 `PENDING_REVIEW`/`CLOSED`; PWDM-001 |
| 9 | **Decision History** | Alasan penolakan reviewer; riwayat closure; catatan penanganan sebelumnya | PWDM-001 §4 Continuity; §2 Interruptions (Complaint Officer/Supervisor) |
| 10 | **Timeline** | Apa yang berubah sejak terakhir dilihat; riwayat status | PDS-001 §6 Common; Status History (Data Dictionary) |
| 11 | **Current Work** | Case yang sedang dikerjakan; aksi yang boleh dilakukan sekarang | PDS-001 §4 Immediate Complaint Officer (mode penanganan) |
| 12 | **Escalation** | Eskalasi baru; alasan & konteks eskalasi | PDS-001 §4 Immediate Supervisor |
| 13 | **Reopen Request** | Permintaan reopen; alasan reopen; riwayat closure terkait | PDS-001 §5 `REOPENED`; PWDM-001 §2 |
| 14 | **Queue / Unassigned Backlog** | Antrian case belum ter-assign | PDS-001 §4 Immediate Supervisor |
| 15 | **Workload / Capacity** | Beban kerja tiap Complaint Officer/unit | PDS-001 §4 Contextual Supervisor |
| 16 | **Pending Approval** | Hasil penanganan menunggu approval Supervisor | PDS-001 §4 Contextual Supervisor |
| 17 | **Aggregate KPI / Trend** | Indikator agregat menyimpang dari target (SLA breach rate, backlog growth); tren per unit/kategori/periode | PDS-001 §4 Immediate & Contextual Manager |
| 18 | **Reconciliation Status** | Hasil pembandingan angka agregat dengan data operasional | PWDM-001 §2 Manager Interruptions |
| 19 | **Data Completeness Status** | Field yang kurang lengkap; checklist field wajib vs terisi | PWDM-001 §2 Complaint Officer Interruptions/Critical decisions (mode intake) |
| 20 | **Customer Interaction History** | Riwayat lengkap seluruh interaksi historis pelanggan | PDS-001 §4 On-demand **Complaint Officer**; Data Dictionary entity "Interaction History" (CRM) |
| 21 | **Related Cases** | Riwayat case lain milik pelanggan yang sama (referensi, bukan aksi) | PDS-001 §4 On-demand **Complaint Officer**; Data Dictionary entity "Related Cases" (CRM) |

Objek 20 dan 21 tetap terpisah — asalnya berbeda: §4 memberi Complaint Officer on-demand *"riwayat interaksi historis pelanggan"* (Interaction History, dari mode intake) dan *"riwayat case lain milik pelanggan yang sama"* (Related Cases, dari mode penanganan) — dua entity berbeda di Data Dictionary, bukan satu objek dengan dua nama. Merge persona **tidak** menggabungkan objek informasi ini menjadi satu; keduanya kini sama-sama on-demand milik satu persona, bukan satu objek per persona.

Tidak ada objek di luar 21 ini digunakan pada bagian berikutnya.

---

## 2. Information Ownership Matrix

Legenda: **P** = Primary (pemilik kerja utama) · **S** = Secondary (dipakai, bukan pemilik) · **R** = Reference Only (konteks, tidak bertindak) · **H** = Hidden by Default (tidak tampil kecuali dinavigasi eksplisit).

**Catatan lensa:** untuk objek yang terikat ke satu tahap lifecycle Case, huruf P/S/R/H di bawah mengikuti Responsibility (R/A/C/I) PDS-001 §5 pada tahap itu — **R/A → P, C → S, I → R, "—" → H**. Untuk objek lintas-tahap atau tanpa baris §5 eksplisit (mis. SLA, Priority, Aggregate KPI), ownership merujuk pada Information Priority Matrix PDS-001 §4.

**Catatan penggabungan kolom:** kolom Complaint Officer di bawah ini digabung dari kolom Customer Service dan Resolver/Handler versi sebelumnya, mengambil nilai terkuat (P > S > R > H) di antara keduanya — merefleksikan bahwa Complaint Officer sekarang memegang kedua mode kerja itu sekaligus, bukan salah satunya.

| # | Information Object | Complaint Officer | Supervisor | Manager | Why |
|---|---|---|---|---|---|
| 1 | Complaint Identity | P | S | H* | Complaint Officer mencatat (R §5 `REGISTERED`) dan mengerjakan (R/A `IN_PROGRESS`) — keduanya P, digabung P. Supervisor mengawasi (R/A titik transisi). Manager hanya agregat (§1, §6 Unique). *kecuali by exception. |
| 2 | Customer Information | P | R | H | Immediate mode intake Complaint Officer (§4); Manager tidak menyentuh data transaksi (§1). |
| 3 | Case Summary | P | S | R* | Dicatat & dipakai Complaint Officer (kedua mode, keduanya P); Supervisor menilai saat keputusan; Manager hanya *by exception*. |
| 4 | Assignment | S | P | H | Supervisor **R/A** (§5 `ASSIGNED`) — satu-satunya pemilik keputusan assignment default. Complaint Officer **I** pada tahap ini (§5) digabung dengan kebutuhan melihat hasil assignment sebagai Immediate mode penanganan (§4) — nilai terkuat antara dua kolom lama (CS: R, Handler: S) adalah **S**. |
| 5 | Priority | P | P | H | Memengaruhi urutan kerja Complaint Officer (mode penanganan) & distribusi Supervisor; dicatat Complaint Officer (mode intake), bukan diputuskan; Manager hanya agregat. |
| 6 | SLA (per case) | P | P | H* | Immediate Complaint Officer (mode penanganan) & Supervisor (§4); Manager melihat bentuk agregatnya (objek #17), bukan SLA per case. |
| 7 | Evidence / Attachment | P | S | H | Contextual Complaint Officer (§4, mode penanganan); Supervisor menilai kelengkapan saat approve/reject. |
| 8 | Resolution | P | P | H* | Complaint Officer mengajukan (R), Supervisor approve/reject (A, §5); pelanggan diinformasikan pasca closure lewat Complaint Officer yang sama. |
| 9 | Decision History | P | P | H | Dibutuhkan Complaint Officer (reject/reopen) & Supervisor (reopen) per JTBD §3; tidak Immediate/Contextual bagi Manager di §4. |
| 10 | Timeline | P | P | R* | Basis progres & SLA bagi Complaint Officer/Supervisor; Manager hanya via drill-down. |
| 11 | Current Work | P | S | H | Immediate mode penanganan Complaint Officer (§4); Supervisor **I** (§5 `IN_PROGRESS`, "pantau progres & SLA"). |
| 12 | Escalation | S | P | H | Supervisor **R/A** (§5) — Immediate (§4). Complaint Officer **C** (§5) — dikonsultasi sesuai JTBD §3; nilai terkuat antara dua kolom lama (CS: R, Handler: S) adalah **S**. Manager **"—"** (§5) — tidak terlibat sama sekali pada eskalasi individual; masuk hanya via agregat KPI/Trend (objek #17). |
| 13 | Reopen Request | P | P | H | Complaint Officer meneruskan permintaan pelanggan (R §5) dan melanjutkan setelah disetujui (R) — digabung P; Supervisor memutuskan (A); Manager hanya Informed agregat. |
| 14 | Queue / Unassigned Backlog | H | P | R* | Immediate #3 Supervisor (§4); Complaint Officer tidak melihat backlog lintas unit (§1); Manager hanya via tren backlog growth. |
| 15 | Workload / Capacity | H | P | R* | Contextual Supervisor (§4, dasar keputusan assign); Manager hanya via agregat, bukan per-officer. |
| 16 | Pending Approval | S | P | H | Contextual Supervisor (§4, Critical decision approve/reject); Complaint Officer menunggu (JTBD). |
| 17 | Aggregate KPI / Trend | H | R | P | Satu-satunya persona level agregat/tren (§6 Unique); Supervisor hanya referensi bila relevan ke unit sendiri. |
| 18 | Reconciliation Status | H | H | P | Muncul hanya di JTBD/Interruptions Manager (§3, PWDM-001). |
| 19 | Data Completeness Status | P | S | H | Critical decision Complaint Officer mode intake (PWDM-001); Supervisor mewarisi dampaknya (§6 Common). |
| 20 | Customer Interaction History | P | H | H | On-demand Complaint Officer (§4: "riwayat interaksi historis pelanggan") — mendukung follow-up personal tanpa bertanya ulang (JTBD §3). |
| 21 | Related Cases | P | H | H | On-demand Complaint Officer (§4: "riwayat case lain milik pelanggan yang sama, referensi bukan aksi"). |

---

## 3. Information Hierarchy

Lima tingkat per persona, diturunkan dari ranking eksplisit PDS-001 §4 (Immediate diurutkan berdasarkan urgensi keputusan) dan kolom Informasi Dibutuhkan PWDM-001 §2. Tingkat Complaint Officer di bawah digabung dari tingkat Customer Service dan Resolver/Handler versi sebelumnya, mengambil tingkat tertinggi per objek (Primary > Secondary > Supporting > Contextual > Hidden) — kedua mode kerja (intake dan penanganan) kini sama-sama milik satu persona.

**Primary** = harus terlihat pertama, tanpa dicari · **Secondary** = item Immediate lain, ranking di bawah Primary · **Supporting** = langsung memberi bukti untuk satu Critical Decision · **Contextual** = latar belakang, dibutuhkan tapi tidak mendorong satu keputusan spesifik · **Hidden** = tidak tampil default, hanya melalui navigasi eksplisit.

### Complaint Officer
| Tingkat | Information Object | Asal (sebelum merge) |
|---|---|---|
| Primary | Customer Information *(mode intake)*; Assignment *(mode penanganan)* | CS Primary; Handler Primary |
| Secondary | Complaint Identity; SLA; Current Work | CS Secondary; Handler Secondary |
| Supporting | Data Completeness Status; Reopen Request (routing); Evidence/Attachment; Decision History (bila reject/reopen) | CS Supporting; Handler Supporting |
| Contextual | Case Summary; Escalation (saat diminta konteks) | CS Contextual; Handler Contextual |
| Hidden | Pending Approval, Workload/Capacity, Aggregate KPI/Trend, Reconciliation Status, Queue, Customer Interaction History*, Related Cases* | CS/Handler Hidden (gabungan) |

*Customer Interaction History dan Related Cases: On-demand per PDS-001 §4 — tersembunyi default, tetap bisa dinavigasi (lih. Bagian 1, catatan pemisahan objek).

### Supervisor
| Tingkat | Information Object |
|---|---|
| Primary | Escalation |
| Secondary | SLA (case mendekati/lewat), Queue/Unassigned Backlog |
| Supporting | Workload/Capacity, Pending Approval, Evidence/Attachment (menilai kelengkapan submission) |
| Contextual | Decision History/Reopen Request (riwayat closure), Complaint Identity/Case Summary case yang sedang direview |
| Hidden | Customer Information, Current Work (langkah-demi-langkah milik Complaint Officer), Aggregate KPI/Trend, Reconciliation Status, Data Completeness Status, Customer Interaction History, Related Cases |

### Manager
| Tingkat | Information Object |
|---|---|
| Primary | Aggregate KPI/Trend — indikator agregat menyimpang dari target *(item tunggal, §4)* |
| Secondary | — *(tidak ada kompetisi prioritas, §4)* |
| Supporting | Reconciliation Status |
| Contextual | Tren per unit/kategori/periode |
| Hidden | Complaint Identity, Customer Information, Case Summary, Assignment, Priority, SLA (per case), Evidence, Resolution, Decision History, Timeline, Current Work, Escalation, Reopen Request, Queue, Workload/Capacity, Pending Approval, Data Completeness Status, Customer Interaction History, Related Cases — semua hanya lewat drill-down *by exception* |

---

## 4. Workspace Zones

Enam zona logis — sudah cukup, tidak ada zona baru:

| Zona | Definisi (case-specific kecuali disebutkan) | Isi (dari Information Inventory) |
|---|---|---|
| **Context** | Siapa/apa case ini sekarang | Customer Information, Complaint Identity, Case Summary, Assignment |
| **Current Work** | Apa yang sedang dikerjakan pada case ini sekarang | Current Work, Priority, SLA, Queue/Unassigned Backlog, Workload/Capacity |
| **Evidence** | Bukti pendukung case ini untuk satu keputusan | Evidence/Attachment, Data Completeness Status |
| **Decision** | Hal yang menunggu/menghasilkan satu keputusan pada case ini | Pending Approval, Escalation, Reopen Request, Resolution |
| **History** | Apa yang terjadi sebelumnya pada case ini | Decision History, Timeline |
| **Reference** | Lintas-case / agregat / lookup — tidak terikat satu case operasional, diakses on-demand | Aggregate KPI/Trend, Tren per unit/kategori/periode, Reconciliation Status, Customer Interaction History, Related Cases |

**Keanggotaan objek pada satu zona bersifat tetap** (tabel di atas) — sama untuk semua persona, bukan turunan otomatis dari tingkat persona (Bagian 3). Tingkat (Bagian 3) menentukan **kapan/bagi siapa** suatu zona menonjol (lih. Bagian 6 Progressive Disclosure); zona itu sendiri hanyalah pengelompokan logis objek berdasarkan sifatnya (case-specific vs lintas-case), bukan sinyal visibilitas.

**Zona primer Manager: Reference.** Manager adalah satu-satunya persona yang seluruh kebutuhan intinya (Aggregate KPI/Trend sebagai Primary-tier, Tren per unit/kategori/periode sebagai Contextual-tier, Reconciliation Status sebagai Supporting-tier — Bagian 3) berada di zona Reference, karena semuanya bersifat lintas-case/agregat, bukan tentang satu case operasional. Ini konsisten dengan PDS-001 §6 Unique: "satu-satunya persona yang bekerja di level agregat/tren, bukan case individual." Manager tidak memiliki footprint default di Context/Current Work/Evidence/Decision/History (semua objek case-level ada di tingkat Hidden bagi Manager, Bagian 3).

---

## 5. Navigation Architecture

Titik navigasi yang sudah tersedia: **Dashboard, Queue, Complaint Workspace, Supporting Views, History, Return to Queue.** Tidak ada tujuan baru.

### Complaint Officer
Complaint Officer memiliki **dua jalur navigasi**, sesuai dua mode kerja PWDM-001 §1 — keduanya tetap satu persona, bukan dua entry point milik dua persona berbeda:

- **Mode intake**: `Login` → tidak ada Dashboard/Queue backlog (PDS-001 §1: mode intake tidak melihat backlog) → langsung **Complaint Workspace** (case baru atau case aktif pelanggan) → **Supporting Views** (Customer Interaction History, on-demand) → keputusan (teruskan/tahan, atau routing Reopen Request ke Supervisor) → kembali ke posisi siap-menerima-kontak berikutnya (bukan Queue).
- **Mode penanganan**: `Login` → **Queue** (daftar case assigned, diurut sisa SLA) → pilih case → **Complaint Workspace** (Context + Current Work + Decision aktif) → **Supporting Views** (Evidence, Related Cases) dan/atau **History** (Decision History, bila reject/reopen) dibuka dari dalam Workspace → keputusan (submit review / lanjutkan) → **Return to Queue** → ulangi hingga Completion.

`Logout` menutup sesi terlepas mode mana yang terakhir aktif (PWDM-001 §1 Complaint Officer Completion/Logout).

### Supervisor
`Login` → **Queue** = eskalasi baru → SLA mendekati/lewat → antrian belum ter-assign, dalam urutan itu (PDS-001 §4/PWDM-001 Login) → pilih item → **Complaint Workspace** (assign/approve/eskalasi/reopen) → **History** (riwayat closure untuk reopen, alasan eskalasi) dibuka dari dalam Workspace → keputusan → **Return to Queue** → `Logout`.

### Manager
`Login` → **Dashboard** (Aggregate KPI/Trend — tujuan akhir, bukan transit) → opsional **Supporting Views** (drill-down unit, *by exception*, PDS-001 §4 On-demand) → tidak ada **Complaint Workspace** dalam pengertian operasional (Manager read-only, Konstitusi PDS-001 #3), tidak ada **Decision** zone, tidak ada **Return to Queue** (Manager tidak memiliki Queue) → `Logout`.

---

## 6. Progressive Disclosure Model

Dipetakan langsung dari Bagian 3 (tingkat) dan kolom "Tidak boleh mengganggu alur kerja" PWDM-001 §5 (Workspace Success Model).

| Persona | Selalu terlihat (Primary + Secondary) | Muncul saat dibutuhkan (Supporting + Contextual) | Tetap collapsed (Hidden) | Tidak boleh mengganggu (PWDM-001 §5) |
|---|---|---|---|---|
| Complaint Officer | Customer Information/ada-tidaknya case (mode intake); Assignment, SLA, Current Work (mode penanganan) | Data Completeness Status, Reopen Request routing, Case Summary, Evidence, Decision History, Escalation context | Queue lintas unit, Workload, Aggregate KPI, Reconciliation Status, dll. | Keputusan assignment awal/closure akhir (kecuali diberi izin); aktivitas Supervisor/Manager di luar case miliknya |
| Supervisor | Escalation, SLA, Queue/Unassigned Backlog | Workload/Capacity, Pending Approval, Evidence, Decision History | Aggregate KPI/Trend, Reconciliation Status | Detail langkah-demi-langkah penanganan case yang sedang dikerjakan Complaint Officer |
| Manager | Indikator agregat menyimpang dari target | Reconciliation Status, Tren per unit/kategori/periode | Semua objek case-level | Detail transaksi individual case, kecuali by exception |

---

## 7. Cross-Persona Consistency

- **Satu inventori, prioritas berbeda** — semua 21 objek di Bagian 1 dipakai bersama; tidak ada objek yang di-duplikasi dengan nama berbeda per persona (mis. "Case Summary" adalah objek yang sama baik dicatat maupun dibaca Complaint Officer/Supervisor). Objek dengan asal berbeda tidak digabung (lih. Bagian 1 catatan pemisahan Customer Interaction History vs Related Cases).
- **Satu Complaint Workspace** — Complaint Officer dan Supervisor menuju destinasi navigasi yang sama (Bagian 5); yang berbeda hanya zona mana yang aktif dan mode kerja mana yang sedang berjalan (Bagian 3–4), bukan workspace terpisah per persona atau per mode. Ini menegakkan PDS-001 §6 Common: "satu identitas case yang konsisten — tidak boleh ada versi berbeda tentang status/pemilik case yang sama antar persona."
- **Tidak ada navigasi ganda** — Queue ada untuk Complaint Officer (mode penanganan) dan Supervisor (masing-masing populasinya berbeda: assigned list vs eskalasi/SLA/unassigned); Complaint Officer mode intake dan Manager sengaja tidak memiliki Queue, bukan diberi Queue kosong sebagai placeholder.
- **Tidak ada workflow ganda** — navigasi di Bagian 5 hanya mengekspos keputusan yang sudah ada di PWDM-001 §2; tidak ada langkah navigasi yang menciptakan keputusan baru.

---

## 8. Information Architecture Constitution

Prinsip yang mengikat setiap dashboard/workspace turunan di masa depan:

1. **Satu Inventori, Banyak Prioritas** — objek informasi (Bagian 1) tidak boleh diduplikasi dengan nama lain per persona; yang berbeda hanya tingkat (Bagian 3).
2. **Work Before Screen** — turunan berikutnya wajib menjawab "informasi apa, kapan" (dokumen ini) sebelum "layar apa" (PDS-001 §7 poin 4).
3. **Manager Tetap Read-Only & Agregat** — tidak ada Decision zone, tidak ada akses Complaint Workspace operasional untuk Manager, selamanya (PDS-001 §7 poin 3).
4. **Progressive Disclosure Mengikuti Information Priority Matrix** — Immediate → selalu terlihat, Contextual → muncul saat dibutuhkan, On-demand → collapsed default. Mempromosikan objek Hidden menjadi selalu-terlihat mensyaratkan revisi PDS-001 §4, bukan keputusan desain layar.
5. **Navigasi Mengikuti Responsibility, Bukan Kenyamanan** — persona hanya bernavigasi ke objek/zona tempat PDS-001 §5 memberi R/A/C/I; sel `—` di §5 tetap tidak terjangkau di navigasi persona itu.
6. **Zona Tertutup** — Context, Current Work, Evidence, Decision, History, Reference adalah closed set (Bagian 4); zona baru memerlukan revisi IA, bukan penambahan diam-diam per layar.
7. **Satu Complaint Workspace, Bukan Layar per Persona atau per Mode** — mencegah versi berbeda tentang case yang sama (PDS-001 §6 Common); berlaku juga antar dua mode kerja Complaint Officer (intake vs penanganan).
8. **Reference, Don't Redefine** — IA-001 tidak mendefinisikan ulang objek informasi; penambahan atau pengubahan objek adalah revisi PDS-001/PWDM-001/Data Dictionary, bukan IA.
9. **Kontinuitas Reopen/Eskalasi Wajib Terbawa** — setiap kali Decision zone membuka kembali case (reject/reopen/eskalasi), History zone wajib menyertakan Decision History terkait, menegakkan temuan Continuity PWDM-001 §4/§6.
10. **Tidak Ada Persona yang Memiliki Layar Permanen** — karena PDS-001 memodelkan work mode, bukan orang (§7 poin 9), populasi zona mengikuti persona mode yang aktif saat itu, bukan akun.

## Related
- `docs/ux/PDS-001-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `06 Data Dictionary/ECMP_Data_Dictionary_v1.0.md`
- `20 Domain Architecture/ECMF/CASE_AGGREGATE.md` (DOM-ECMF-002)
- `20 Domain Architecture/ECMF/CASE_STATE_MACHINE.md` (DOM-ECMF-003)

## Future Work
Wireframe / Information Design turunan dari IA-001 — di luar ruang lingkup dokumen ini.
