# WF-000 — Wireframe Constitution & Layout System

| Field | Value |
|---|---|
| Document ID | WF-000 |
| Title | Wireframe Constitution & Layout System |
| Status | Draft |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Version | 1.0 |
| Date | 2026-08-03 |
| Parent | NAV-001 |
| Subordination | ECMP-CONSTITUTION-001 → PDS-000 → PWDM-001 → IA-001 → NAV-001 → **WF-000** → (future) WF-001 |

## Single responsibility

> Menetapkan **aturan struktural yang wajib dipatuhi setiap wireframe di masa depan** — filosofi layout, hierarki visual, alur baca, zonasi workspace, filosofi spasi, dan aturan konsistensi.

WF-000 **tidak** mendesain layar. Dokumen ini adalah cetak biru untuk seluruh wireframe masa depan (WF-001 dan seterusnya), bukan salah satu dari wireframe itu sendiri.

WF-000 **bukan** tempat mendefinisikan: Business Rule, Persona (PDS-000), Workflow/Decision (PWDM-001), Information Architecture/Zona/Objek Informasi (IA-001), Navigasi/Destinasi (NAV-001), komponen UI, warna, tipografi, ikon, atau teknologi implementasi (React/Tailwind/CSS). Semua istilah zona, destinasi, persona, dan tier informasi yang dipakai di sini sudah ada di keempat baseline tersebut — WF-000 hanya merujuk, tidak mendefinisikan ulang.

---

## 1. Wireframe Principles

Enam prinsip berikut mengikat setiap wireframe turunan.

### 1.1 Information First
Informasi ditampilkan sebelum aksi ditawarkan. Menegakkan **Work Before Screen** (IA-001 §8 poin 2) dan **Work Before Interface** (PDS-000 §7 poin 4): pengguna harus bisa memahami konteks case sebelum dihadapkan pada pilihan tindakan.

### 1.2 Actions After Context
Aksi (Decision zone) selalu diletakkan setelah konteks (Context zone) dalam urutan perhatian pengguna — tidak pernah sebaliknya. Ini bukan aturan visual, melainkan aturan urutan: pengguna tidak boleh diminta memutuskan sebelum tahu apa yang sedang diputuskan.

### 1.3 One Primary Action
Setiap tampilan case memiliki tepat satu keputusan utama yang ditawarkan pada satu waktu, selaras dengan **Critical Decisions** tunggal per tahap (PWDM-001 §2) dan **One Primary Path** (NAV-001 prinsip 2). Tidak ada dua aksi setara yang bersaing untuk keputusan yang sama.

### 1.4 Progressive Disclosure
Informasi ditampilkan sesuai tier-nya (IA-001 §3, §6): Primary/Secondary selalu terlihat, Supporting/Contextual muncul saat dibutuhkan, Hidden hanya lewat navigasi eksplisit. Wireframe tidak boleh menaikkan tier informasi secara diam-diam — perubahan tier adalah revisi IA-001, bukan keputusan wireframe.

### 1.5 Never Duplicate Context
Satu Complaint Workspace (IA-001 §7, NAV-001 §4) berarti satu wireframe layout dasar untuk Customer Service, Handler, dan Supervisor — bukan tiga layout terpisah dengan versi konteks case yang berbeda-beda. Duplikasi konteks pada wireframe adalah pelanggaran terhadap "satu identitas case yang konsisten" (PDS-000 §6).

### 1.6 Stable Workspace
Membuka Supporting Views atau History tidak boleh mengganti destinasi (NAV-001: "navigasi tidak berubah" pada interupsi CS; "dari dalam Workspace" untuk Handler/Supervisor). Workspace utama tetap ada dan tidak ditutup selama panel pendukung dibuka.

---

## 2. Reading Flow

Alur baca mengikuti lima band, dipetakan langsung dari Information Hierarchy (IA-001 §3) dan Workspace Zones (IA-001 §4) — bukan urutan visual baru.

| Band | Isi | Alasan |
|---|---|---|
| **Top** | Zona Context (Primary/Secondary tier persona yang aktif) | Yang harus terlihat pertama tanpa dicari (PDS-000 §4 Immediate) — identitas case/pelanggan/assignment. |
| **Middle** | Zona Current Work + Zona Decision | Di sinilah Critical Decision terjadi (PWDM-001 §2); aksi selalu setelah konteks (Prinsip 1.2). |
| **Lower** | Zona Evidence (Supporting tier) | Bukti yang mendukung satu keputusan spesifik, bukan latar belakang umum — dibaca setelah keputusan diidentifikasi, sebelum diambil. |
| **Reference** | Zona Reference (Contextual/On-demand tier) | Lintas-case/agregat, tidak terikat satu case operasional (IA-001 §4) — diakses, bukan disodorkan. |
| **History** | Zona History | Apa yang terjadi sebelumnya; wajib menyertai Decision saat reject/reopen/eskalasi (IA-001 §8 poin 9; NAV-001 prinsip 4) — dibaca untuk kontinuitas, bukan bagian alur keputusan utama. |

Reference dan History berada di luar alur baca linear utama (Top→Middle→Lower) karena keduanya bersifat on-demand/kondisional, bukan default — konsisten dengan Progressive Disclosure (Prinsip 1.4).

---

## 3. Workspace Grid

Enam region logis. Tidak ada piksel, tidak ada CSS — hanya penempatan relatif terhadap Zona IA-001 dan Destinasi NAV-001.

| Region | Definisi Logis | Sumber |
|---|---|---|
| **Header** | Orientasi tingkat modul, tidak spesifik-case; persisten di seluruh sesi | Setara tahap `Login` (PWDM-001 §1) — bukan bagian dari case manapun. |
| **Entry Area** | Titik masuk sebelum case dipilih: Queue (Handler/Supervisor) atau Dashboard (Manager); tidak ada untuk CS | Entry Point per persona (NAV-001 §1). |
| **Primary Workspace** | Zona Context + Zona Current Work + Zona Decision, digabung dalam satu region operasional | Destinasi **Complaint Workspace** (IA-001 §5; NAV-001 §1) — inti case yang sedang dikerjakan. |
| **Supporting Workspace** | Zona Evidence, dibuka dari dalam Primary Workspace, tidak menggantikannya | Destinasi **Supporting Views** (IA-001 §5; NAV-001 "dari dalam Workspace"). |
| **History Area** | Zona History, dibuka dari dalam Primary Workspace | Destinasi **History** (IA-001 §5; NAV-001 "dari dalam Workspace"). |
| **Reference Area** | Zona Reference; untuk Manager region ini **adalah** Entry Area (Dashboard), untuk persona lain diakses on-demand dari Supporting Workspace | IA-001 §4: "Zona primer Manager: Reference". |

Primary Workspace tidak pernah kosong dan tidak pernah digantikan oleh region lain — ini menegakkan Stable Workspace (Prinsip 1.6).

---

## 4. Zone Priority

Diturunkan **hanya** dari IA-001 (§3 Information Hierarchy, §4 Workspace Zones, §6 Progressive Disclosure). Lima status:

- **Always Visible** — zona berisi informasi tier Primary/Secondary bagi persona tersebut.
- **Conditionally Visible** — zona berisi informasi tier Supporting; muncul saat mendukung satu keputusan spesifik.
- **Contextual** — zona berisi informasi tier Contextual/On-demand; diakses lewat navigasi eksplisit, tidak disodorkan.
- **Collapsed** — zona ada dalam workspace persona tersebut tetapi didominasi tier Hidden; terlipat default.
- **Hidden** — zona tidak memiliki footprint di workspace persona tersebut sama sekali (bukan sekadar terlipat — secara struktural tidak hadir).

| Zona | Customer Service | Resolver/Handler | Supervisor | Manager |
|---|---|---|---|---|
| **Context** | Always Visible *(Customer Information, Complaint Identity — Primary/Secondary)* | Always Visible *(Assignment — Primary)* | Contextual *(Case Summary/Complaint Identity — Contextual tier)* | Hidden *(IA-001 §4: tanpa footprint default)* |
| **Current Work** | Hidden *(§3: Current Work eksplisit Hidden bagi CS)* | Always Visible *(SLA, Current Work — Secondary)* | Always Visible *(SLA, Queue — Secondary)* | Hidden |
| **Evidence** | Conditionally Visible *(Data Completeness Status — Supporting)* | Conditionally Visible *(Evidence/Attachment — Supporting)* | Conditionally Visible *(Evidence/Attachment, Workload — Supporting)* | Hidden |
| **Decision** | Conditionally Visible *(Reopen Request routing — Supporting; sisa objek zona ini Hidden bagi CS)* | Contextual *(Escalation — Contextual "saat diminta konteks"; Handler tidak approve sendiri)* | Always Visible *(Escalation — Primary)* | Hidden *(IA-001 §5: tidak ada Decision sebagai destinasi navigasi Manager)* |
| **History** | Hidden *(§3: Decision History eksplisit Hidden bagi CS)* | Conditionally Visible *(Decision History — Supporting, "bila reject/reopen")* | Contextual *(Decision History — Contextual, "riwayat closure")* | Hidden |
| **Reference** | Contextual *(Customer Interaction History — on-demand, "tersembunyi default, tetap bisa dinavigasi")* | Contextual *(Related Cases — on-demand, pola sama)* | Hidden *(§3: Aggregate KPI/Trend & Reconciliation Status eksplisit Hidden bagi Supervisor)* | Always Visible *(Aggregate KPI/Trend — Primary; satu-satunya zona rumah Manager)* |

---

## 5. Interaction Philosophy

Tanpa UI — ini adalah aturan urutan keputusan, bukan pola interaksi visual.

- **Context Before Action** — pengguna tidak boleh diberi pilihan aksi sebelum konteks case yang relevan sudah tersaji (Prinsip 1.2).
- **Primary Action Isolation** — satu keputusan kritikal per case per waktu (PWDM-001 §2 Critical Decisions); tidak ada dua aksi Decision-zone yang ditawarkan berdampingan pada case yang sama.
- **One Decision at a Time** — hasil dari satu Critical Decision (mis. approve/reject) harus tuntas sebelum Decision berikutnya pada case yang sama muncul.
- **Preserve Focus** — membuka Supporting Workspace atau History Area tidak memindahkan pengguna keluar dari Primary Workspace (Prinsip 1.6; NAV-001 "dari dalam Workspace").
- **Avoid Context Switching** — saat Decision zone membuka kembali case (reject/reopen/eskalasi), History Area wajib tersedia tanpa pengguna mencarinya terpisah, menegakkan Continuity (PWDM-001 §4; IA-001 §8 poin 9).

---

## 6. Cross Persona Consistency

### Harus identik untuk semua persona
- **Struktur zona yang sama** — enam zona (Context, Current Work, Evidence, Decision, History, Reference) adalah closed set (IA-001 §8 poin 6); setiap wireframe menggunakan struktur region yang sama dari Bagian 3, meski sebagian zona Hidden bagi persona tertentu.
- **Satu Primary Workspace** — CS, Handler, dan Supervisor berbagi wireframe Complaint Workspace yang sama; tidak ada versi berbeda dari case yang sama (PDS-000 §6 Common; IA-001 §7).
- **Destinasi navigasi yang sama** — closed set Dashboard/Queue/Complaint Workspace/Supporting Views/History/Return to Queue berlaku untuk semua wireframe (NAV-001 §4).
- **Reading Flow yang sama** — urutan Top→Middle→Lower→Reference/History (Bagian 2) tidak berubah antar persona; yang berubah adalah zona mana yang mengisi Top bagi persona itu.

### Boleh berbeda per persona
- **Prioritas zona** (Bagian 4) — zona mana Always Visible vs Hidden berbeda per persona, tapi selalu diturunkan dari IA-001, bukan preferensi wireframe.
- **Kehadiran Entry Area** — Queue untuk Handler/Supervisor, Dashboard untuk Manager, tidak ada untuk CS (NAV-001 §1).
- **Penekanan default** — zona mana yang mendominasi Top band berbeda (Context untuk CS, Current Work untuk Handler, Decision untuk Supervisor, Reference untuk Manager) — ini "different priorities", bukan "different destinations" (NAV-001 §4).

---

## 7. Responsive Philosophy

Tanpa CSS, tanpa breakpoint. Hanya urutan pengurangan hierarki.

- **Desktop** — seluruh zona berstatus Always Visible dan Conditionally Visible (Bagian 4) dapat berdampingan pada waktu yang sama; pengguna melihat hierarki penuh tanpa menyembunyikan apa pun yang tergolong wajib tampil.
- **Tablet** — zona Always Visible tetap tampil bersamaan; zona Conditionally Visible dan Contextual mundur menjadi panel yang dipanggil, tidak lagi berdampingan permanen. Primary Workspace tetap menjadi jangkar utama (Prinsip 1.6).
- **Mobile** — hanya satu zona ditampilkan pada satu waktu, mengikuti urutan Reading Flow (Bagian 2): zona Always Visible tertinggi ditampilkan dulu, zona lain dijangkau lewat navigasi eksplisit satu langkah, bukan digulir sekaligus.

Yang berubah antar perangkat hanyalah **berapa banyak zona bisa terlihat bersamaan** — bukan zona mana yang ada, bukan urutan prioritasnya (Bagian 4 tetap berlaku di semua ukuran). Zona berstatus Hidden/Collapsed adalah yang pertama mengalah saat ruang menyempit; zona Always Visible adalah yang terakhir.

---

## 8. Accessibility Principles

Tanpa warna, tanpa komponen.

- **Reading Order** — urutan navigasi (keyboard/assistive) mengikuti Reading Flow (Bagian 2): Top → Middle → Lower → Reference/History. Urutan ini identik dengan urutan visual, tidak boleh divergen.
- **Keyboard Flow** — perpindahan fokus mengikuti Zone Priority (Bagian 4): zona Always Visible dapat dijangkau langsung; zona Conditionally Visible/Contextual dijangkau lewat titik navigasi eksplisit yang sama dengan yang dipakai mouse/sentuh (Supporting Views, History — NAV-001 §1).
- **Focus Preservation** — saat Supporting Workspace atau History Area ditutup, fokus kembali ke titik asal di Primary Workspace, bukan ke awal halaman — menegakkan Preserve Focus (Bagian 5) dan Stable Workspace (Prinsip 1.6).
- **Information Grouping** — enam zona (Bagian 3–4) adalah unit pengelompokan semantik; setiap wireframe turunan wajib mengelompokkan informasi menurut keanggotaan zona IA-001 §4, bukan menurut kemiripan visual atau kemudahan tata letak.

---

## 9. Wireframe Constitution

Aturan permanen — mengikat WF-001 dan seluruh wireframe turunan berikutnya.

1. **Reference, Don't Redesign** — WF-000 dan turunannya tidak mendefinisikan ulang Persona (PDS-000), Workflow (PWDM-001), Information Architecture (IA-001), atau Navigasi (NAV-001). Wireframe hanya menyusun tata letak dari apa yang sudah ditetapkan.
2. **Closed Zone Set** — enam zona (Context, Current Work, Evidence, Decision, History, Reference) adalah satu-satunya unit pengelompokan; zona baru memerlukan revisi IA-001, bukan keputusan wireframe.
3. **Closed Destination Set** — enam destinasi NAV-001 (Dashboard, Queue, Complaint Workspace, Supporting Views, History, Return to Queue) adalah satu-satunya region navigasi; wireframe tidak menciptakan destinasi baru.
4. **One Primary Workspace** — CS, Handler, dan Supervisor berbagi satu wireframe Complaint Workspace; tidak ada wireframe case terpisah per persona.
5. **Information First, Always** — setiap wireframe menampilkan Context sebelum Decision (Prinsip 1.1–1.2); tidak ada pengecualian tanpa revisi WF-000.
6. **One Primary Action per Case** — setiap wireframe case menawarkan tepat satu Critical Decision aktif pada satu waktu (Prinsip 1.3, 1.5).
7. **Progressive Disclosure Mengikat** — tier informasi (IA-001 §3) menentukan status zona (Bagian 4); menaikkan visibilitas suatu zona pada wireframe tanpa revisi IA-001 adalah pelanggaran konstitusi ini.
8. **Zone Priority Tidak Boleh Ditimpa per Layar** — status Always Visible/Conditionally Visible/Contextual/Collapsed/Hidden pada Bagian 4 berlaku untuk seluruh wireframe persona itu; satu layar tidak boleh mengubah status zona demi preferensi tampilan.
9. **Stable Workspace, Preserved Focus** — membuka Supporting Workspace, History Area, atau Reference Area tidak pernah menutup atau memindahkan Primary Workspace; fokus kembali ke titik asal saat ditutup.
10. **Reading Order = Visual Order = Keyboard Order** — ketiganya wajib identik (Bagian 2, Bagian 8); divergensi di antara ketiganya adalah cacat wireframe, bukan variasi desain yang sah.
11. **Responsive Mengurangi Keserempakan, Bukan Prioritas** — di ukuran perangkat mana pun, urutan prioritas zona (Bagian 4) tidak berubah; yang berubah hanya berapa zona tampil bersamaan (Bagian 7).
12. **No Persona-Specific Screens** — mengikuti PDS-000 §7 poin 9 (persona memodelkan mode kerja, bukan akun tetap): wireframe dibangun per zona/destinasi, bukan per akun pengguna.

---

## Related
- `docs/ux/UX-FOUNDATION-000-Complaint-Module-UX-Foundation.md`
- `docs/ux/PDS-000-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/NAV-001-Navigation-Architecture.md`

## Future Work
WF-001 Low Fidelity Wireframes — penerapan konstitusi ini ke layar nyata per persona/zona — di luar ruang lingkup dokumen ini.
