# WF-001-01 — Global Shell & Header

| Field | Value |
|---|---|
| Document ID | WF-001-01 |
| Title | Global Shell & Header |
| Status | Draft — revisi mengikuti merge persona PDS-001 (UX-001 Documentation Update); menunggu Review/Approval |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Version | 1.2 |
| Date | 2026-08-05 |
| Parent | WF-000 |
| Backlog Item | WF-PLAN-001 §2 — WF-001-01 (Release 1, P0) |
| Dependencies | — *(tidak ada; item pertama backlog)* |
| Subordination | ECMP-CONSTITUTION-001 → PDS-001 → PWDM-001 → IA-001 → NAV-001 → WF-000 → WF-PLAN-001 → **WF-001-01** · WF-001-R1 |
| Revision note | Customer Service dan Resolver/Handler digabung menjadi **Complaint Officer** (mode intake / mode penanganan) di seluruh referensi persona. `PDS-000` di dokumen ini diperbarui ke `PDS-001`. **2026-08-05:** dirujuk sebagai bagian paket `WF-001-R1`. |

## Single responsibility

> Menetapkan **struktur frame persisten tingkat modul** — region yang selalu ada sepanjang sesi, terlepas dari case, persona mode, dan destinasi navigasi yang sedang aktif.

Spesifikasi ini bersifat struktural, bukan visual. Tidak ada gambar, tata letak, komponen, warna, tipografi, spasi, atau implementasi di dalamnya.

WF-001-01 tidak mendefinisikan ulang Persona (PDS-001), Workflow (PWDM-001), Information Architecture (IA-001), Navigasi (NAV-001), atau aturan layout (WF-000). Bagian A–D di bawah adalah **kosakata dan kontrak** yang berlaku untuk seluruh WF-001; Bagian 1–13 adalah **badan spesifikasi** item ini.

---

# Bagian A — Template Contract

WF-001-01 menetapkan **struktur tetap** yang wajib dipakai WF-001-02 sampai WF-001-21 (WF-PLAN-001 §2).

### A.1 Bagian yang mengikat

Ketiga belas judul pada Bagian 1–13 adalah urutan dan penamaan baku. Setiap wireframe berikutnya memuat ketiga belas judul yang sama, dalam urutan yang sama, tanpa menambah atau menghapus judul.

Bagian A–D **tidak diulang** di WF-001-02 s.d. WF-001-21 — cukup dirujuk (`WF-001-01 §A–§D`). Menyalinnya adalah duplikasi yang dilarang Bagian C.4.

### A.2 Bagian yang tidak berlaku

Sebuah bagian **tidak wajib berisi**. Jawaban `Tidak ada` atau `Tidak berlaku` adalah jawaban yang sah, dengan tiga syarat:

1. **Ketiadaan itu dapat dirujuk.** Sebutkan baris baseline yang menetapkannya. Contoh yang berlaku di dokumen ini: Bagian 9 dijawab `Tidak ada` karena PWDM-001 §2 mencatat `Login` sebagai *"Tidak ada keputusan formal"* pada ketiga persona.
2. **Ketiadaan dinyatakan, bukan dikosongkan.** Bagian tidak boleh dihapus, dibiarkan kosong, atau diisi tanda hubung tanpa keterangan.
3. **Ketiadaan tidak diisi pengganti.** Dilarang mengisi bagian dengan materi yang tidak punya sumber baseline hanya agar template terlihat penuh — ini penerapan langsung WF-000 §9 poin 1 dan PDS-001 §7 poin 7.

### A.3 Batas isi

Isi setiap bagian hanya boleh berupa hal yang sudah ditetapkan PDS-001, PWDM-001, IA-001, NAV-001, atau WF-000. Kondisi, keadaan, atau perilaku yang tidak dikenal kelima baseline itu **tidak diinvensikan** — bagian yang bersangkutan dijawab `Tidak berlaku` menurut A.2.

---

# Bagian B — Kosakata: Destination ≠ Region

Dua sistem penamaan berbeda dipakai bersama sepanjang WF-001. Keduanya **tidak boleh dipertukarkan, disingkat menjadi satu, atau dipakai berdampingan seolah setara.**

| Istilah | Sumber | Artinya |
|---|---|---|
| **Destination** *(Destinasi)* | NAV-001 prinsip 1 — closed set | **Ke mana** pengguna bernavigasi. Enam: Dashboard, Queue, Complaint Workspace, Supporting Views, History, Return to Queue. |
| **Region** | WF-000 §3 — closed set | **Di mana** isi ditempatkan dalam frame. Enam: Header, Entry Area, Primary Workspace, Supporting Workspace, History Area, Reference Area. |
| **Zone** *(Zona)* | IA-001 §4 — closed set | **Pengelompokan logis objek informasi.** Enam: Context, Current Work, Evidence, Decision, History, Reference. |

Tiga pasang nama di bawah ini mirip tetapi bukan hal yang sama, dan paling sering tertukar:

- **Supporting Views** (Destination) ≠ **Supporting Workspace** (Region) — lihat Bagian D.
- **History** (Destination) ≠ **History Area** (Region) ≠ **History** (Zone).
- **Dashboard** (Destination) ≠ **Entry Area** / **Reference Area** (Region).

Aturan penulisan: bila satu kalimat menyebut lebih dari satu kategori, kategorinya disebut eksplisit — misalnya *"destinasi Supporting Views dibuka di region Supporting Workspace"*, bukan *"membuka Supporting Views atau Reference Area"*.

---

# Bagian C — Visibilitas Informasi ≠ Kehadiran Struktural

**Klarifikasi permanen. Berlaku untuk seluruh WF-001.**

IA-001 dan WF-000 sama-sama memakai kata **"Hidden"**, untuk dua hal yang berbeda. Keduanya benar di ranahnya masing-masing. Tidak satu pun didefinisikan ulang di sini.

### C.1 Dua konsep

| Konsep | Sumber | Pertanyaan yang dijawab |
|---|---|---|
| **Visibilitas Informasi** | IA-001 §2 (legenda `H` = *"Hidden by Default — tidak tampil kecuali dinavigasi eksplisit"*) dan IA-001 §3 (tingkat `Hidden` = *"tidak tampil default, hanya melalui navigasi eksplisit"*) | **Apakah informasi ini tampil tanpa diminta?** Jawaban "tidak" **tetap berarti informasi itu terjangkau.** |
| **Kehadiran Struktural** | WF-000 §4 (status `Hidden` = *"tidak memiliki footprint … secara struktural tidak hadir"*) | **Apakah region ini ada dalam frame persona tersebut?** Jawaban "tidak" berarti region itu **tidak ada sama sekali.** |

### C.2 Aturan mengikat

> **Tingkat visibilitas IA-001 tidak pernah diterjemahkan langsung menjadi status kehadiran WF-000.**

Status kehadiran sebuah region dibaca **hanya** dari tabel WF-000 §4. Tabel itu sudah melakukan penerjemahannya, dan hasilnya bukan pemetaan kata-per-kata. Wireframe tidak menurunkan sendiri status region dari tingkat IA-001.

### C.3 Mengapa aturan ini ada

Penerjemahan langsung menghasilkan hasil yang salah dan dapat diperagakan:

- IA-001 §3 menempatkan **Related Cases** pada tingkat `Hidden` bagi Complaint Officer (mode penanganan), dengan catatan kaki eksplisit *"tersembunyi default, **tetap bisa dinavigasi**"*. Diterjemahkan langsung menjadi status WF-000 `Hidden` ("tidak hadir"), Related Cases akan lenyap — padahal NAV-001 §1 mewajibkannya sebagai Secondary Navigation mode penanganan dan WF-PLAN-001 mengalokasikan WF-001-12 untuknya.
- Pola yang sama mengancam **Customer Interaction History**: tingkat `Hidden` bagi Complaint Officer (mode intake) di IA-001 §3, tetapi destinasi wajib di NAV-001 §1 dan item WF-001-21.

WF-000 §4 sendiri sudah menyelesaikan kedua kasus ini dengan benar — region Reference ditandai **Contextual**, bukan Hidden, bagi Complaint Officer. Itulah bukti bahwa penerjemahan kata-per-kata tidak berlaku.

### C.4 Sumber tunggal

WF-000 tetap satu-satunya sumber status region. Bila status suatu region terasa keliru, jalurnya adalah revisi IA-001/WF-000 — bukan penyesuaian di dokumen wireframe (WF-000 §9 poin 7–8).

---

# Bagian D — Pemetaan Destination ↔ Region

**Pemetaan permanen. Dipakai ulang oleh seluruh WF-001, tidak diturunkan ulang per dokumen.**

Enam destinasi closed set NAV-001 (prinsip 1) dan enam region WF-000 §3 **bukan pemetaan satu-lawan-satu.** Tabel berikut hanya menyatakan relasi yang sudah ada di kedua baseline; tidak ada destinasi baru, region baru, atau relasi baru yang diperkenalkan.

| Destination (NAV-001 prinsip 1) | Region (WF-000 §3) | Dasar |
|---|---|---|
| **Dashboard** | **Entry Area** — yang bagi Manager sekaligus **Reference Area** | WF-000 §3: Entry Area = *"Dashboard (Manager)"*; Reference Area = *"untuk Manager region ini **adalah** Entry Area (Dashboard)"* |
| **Queue** | **Entry Area** | WF-000 §3: Entry Area = *"Queue (Complaint Officer mode penanganan/Supervisor)"* |
| **Complaint Workspace** | **Primary Workspace** | WF-000 §3: Primary Workspace = *"Destinasi Complaint Workspace"* |
| **Supporting Views** | **Supporting Workspace** *dan/atau* **Reference Area** — bercabang, lihat D.1 | WF-000 §3: Supporting Workspace = *"Destinasi Supporting Views"*; Reference Area = *"diakses on-demand dari Supporting Workspace"* |
| **History** | **History Area** | WF-000 §3: History Area = *"Destinasi History"* |
| **Return to Queue** | **Tidak memiliki region tersendiri** — mengembalikan ke **Entry Area** (Queue) | NAV-001 prinsip 5; tidak ada region ketujuh di WF-000 §3 |
| *(tidak ada destinasi)* | **Header** | Header tidak termasuk closed set destinasi NAV-001 (prinsip 1) |

### D.1 Percabangan Supporting Views

Satu destinasi, dua region — ditentukan oleh **zona** isi yang dituju (IA-001 §4), bukan oleh persona:

| Isi yang dituju | Zona (IA-001 §4) | Region |
|---|---|---|
| Evidence / Attachment | Evidence | **Supporting Workspace** |
| Related Cases · Customer Interaction History · tren per unit/kategori/periode | Reference | **Reference Area** |

Konsekuensinya, satu item backlog dapat melintasi dua region: WF-001-12 (*"Supporting Views — Evidence & Related Cases"*, WF-PLAN-001 §2) menempati Supporting Workspace **dan** Reference Area. Ini bukan dua destinasi — tetap satu destinasi Supporting Views.

### D.2 Tiga asimetri yang harus dipahami

1. **Header** adalah region tanpa destinasi — tidak dituju, tidak dimasuki.
2. **Return to Queue** adalah destinasi tanpa region — ia mengembalikan pengguna ke Entry Area yang sama, bukan membuka wadah baru.
3. **Supporting Views** adalah satu destinasi atas dua region (D.1).

Jumlah destinasi dan region kebetulan sama-sama enam; itu **bukan** tanda korespondensi satu-lawan-satu.

---

# Bagian 1–13 — Spesifikasi WF-001-01

### Catatan sifat dokumen

WF-001-01 adalah **satu-satunya item backlog yang bukan wireframe case-level** (WF-PLAN-001 §2: Primary Persona *"(semua)"*, scope *"tidak spesifik-case"*). Karena itu Bagian 9 dan Bagian 11 dijawab dengan ketiadaan menurut Bagian A.2 — bukan dengan isi yang dikarang agar template terisi.

---

## 1. Purpose

Menyediakan frame yang **persisten di seluruh sesi** dan menjadi wadah bagi kelima region lain pada WF-000 §3.

Frame menegakkan tiga ketetapan baseline yang tidak bisa ditegakkan oleh wireframe case-level mana pun sendirian:

- **Stable Workspace** (WF-000 §1.6, §9 poin 9) — penegakan ini properti frame, bukan properti satu layar case.
- **Closed Destination Set** (NAV-001 prinsip 1; WF-000 §9 poin 3).
- **Work Mode, Not Account** (PDS-001 §7 poin 9; IA-001 §8 poin 10; NAV-001 prinsip 11) — populasi region mengikuti persona mode yang aktif, bukan akun.

Frame **bukan**: pembawa informasi case, penawar aksi, atau destinasi navigasi.

---

## 2. Primary Persona

**Seluruh persona.** WF-001-01 adalah satu-satunya item backlog yang berlaku setara bagi ketiganya (WF-PLAN-001 §2).

| Persona | Region Entry Area | Dasar |
|---|---|---|
| Complaint Officer — mode intake | Tidak ada | NAV-001 §1; WF-000 §3 |
| Complaint Officer — mode penanganan | Ada — destinasi Queue | NAV-001 §1; WF-000 §3 |
| Supervisor | Ada — destinasi Queue | NAV-001 §1; WF-000 §3 |
| Manager | Ada — destinasi Dashboard, sekaligus Reference Area | WF-000 §3; Bagian D |

Frame tidak memiliki varian per persona. Yang berbeda hanya **region mana yang hadir**, dan itu dibaca dari WF-000 §4 — tidak diputuskan di sini.

Karena satu akun dapat mengaktifkan lebih dari satu persona pada waktu berbeda (PDS-001 §7 poin 9), frame tidak mengikat dirinya ke satu persona secara permanen.

---

## 3. Related Workflow

Frame memetakan **hanya** dua tahap PWDM-001 §1–§2 yang berada di luar penanganan case, dan tahap itu sama bagi ketiga persona:

| Tahap PWDM-001 | Peran frame |
|---|---|
| `Login` | Frame hadir; persona mode aktif menentukan kehadiran region |
| `Primary objective` | Tidak ada peran — PWDM-001 §2 mencatat tahap ini tanpa informasi dan tanpa keputusan bagi ketiga persona |
| *(sepanjang sesi)* | Frame tetap ada tanpa berubah |
| `Logout` | Frame berakhir bersama sesi |

`Routine work`, `Interruptions`, dan `Critical decisions` seluruhnya case-level dan menjadi ruang lingkup WF-001-02 s.d. WF-001-21. Bagian 5 menyebut satu interupsi hanya untuk menyatakan bahwa ia **bukan** exit frame — itu putusan tentang batas frame, bukan pemetaan interupsi.

---

## 4. Navigation Entry

Frame hadir pada `Login`, sebelum destinasi mana pun aktif (NAV-001 §1, ketiga persona).

Tujuan pertama sesudahnya ditentukan Entry Point persona pada NAV-001 §1 — frame tidak memilihkannya:

| Persona mode aktif | Destinasi pertama |
|---|---|
| Complaint Officer — mode intake | **Complaint Workspace** langsung (tanpa Dashboard, tanpa Queue) |
| Complaint Officer — mode penanganan | **Queue** (assigned, urut sisa SLA) |
| Supervisor | **Queue** (eskalasi → SLA → unassigned, urutan tetap dan tunggal) |
| Manager | **Dashboard** (tujuan akhir, bukan transit) |

Frame sendiri **tidak dituju dan tidak dimasuki** — ia bukan anggota closed set destinasi NAV-001 (prinsip 1) (Bagian D.2 poin 1). Tidak ada jalur navigasi yang berujung di frame.

---

## 5. Navigation Exit

Frame keluar hanya pada `Logout` (NAV-001 §1, ketiga persona). Tidak ada exit lain.

Yang **bukan** exit, dan karenanya tidak menutup frame:

| Peristiwa | Dasar |
|---|---|
| Membuka destinasi Supporting Views (region Supporting Workspace atau Reference Area, per Bagian D.1) | NAV-001 §1: dibuka *dari dalam* Workspace; WF-000 §1.6 |
| Membuka destinasi History (region History Area) | NAV-001 §1; WF-000 §1.6 |
| Destinasi **Return to Queue** | NAV-001 prinsip 5 — mengembalikan ke region Entry Area yang sama; anggota closed set destinasi, tetapi tanpa region tersendiri (Bagian D.2 poin 2) |
| Interupsi kontak baru pada Complaint Officer (mode intake) | NAV-001 §1: *"navigasi **tidak berubah**"* |
| Perpindahan persona mode dalam satu akun | PDS-001 §7 poin 9 — mengubah kehadiran region di dalam frame, tidak mengakhiri frame |

Kondisi `Logout` per persona sudah ditetapkan PWDM-001 §1 dan tidak diulang di sini.

---

## 6. Information Zones

**Frame tidak memuat satu pun zona dari closed set IA-001 §4.**

Keenam zona bersifat case-specific atau lintas-case operasional (IA-001 §4), sedangkan frame bersifat *"tidak spesifik-case"* (WF-000 §3). Relasinya berlapis: **frame menampung region; region menampung zona.**

| Region | Zona yang dihosting | Destinasi terkait |
|---|---|---|
| **Header** | — *(tidak ada)* | — *(Bagian D.2 poin 1)* |
| **Entry Area** | Current Work *(Queue)* · Reference *(Dashboard)* | Queue · Dashboard |
| **Primary Workspace** | Context · Current Work · Decision | Complaint Workspace |
| **Supporting Workspace** | Evidence | Supporting Views *(cabang Evidence — Bagian D.1)* |
| **History Area** | History | History |
| **Reference Area** | Reference | Supporting Views *(cabang Reference)* · Dashboard *(Manager)* |

**Status kehadiran setiap region per persona dibaca dari tabel WF-000 §4.** Tabel itu tidak disalin ke sini — WF-000 tetap sumber tunggal (Bagian C.4). Pembacaannya tunduk pada Bagian C.2: tingkat visibilitas IA-001 tidak diterjemahkan langsung menjadi status kehadiran.

Tidak ada objek dari Information Inventory IA-001 §1 (21 objek) yang berada di Header. Menempatkan salah satunya di sana melanggar WF-000 §9 poin 8.

---

## 7. Information Priority

Frame tidak memuat objek informasi (Bagian 6), sehingga prioritas di sini adalah **prioritas perhatian antar region**, mengikuti WF-000 §3–§4:

| Peringkat | Region |
|---|---|
| 1 | **Primary Workspace** — atau **Entry Area** bagi Manager, yang sekaligus Reference Area (Bagian D) |
| 2 | **Entry Area** |
| 3 | **Supporting Workspace** · **History Area** · **Reference Area** |
| — | **Header** — tidak pernah menempati peringkat pertama |

Dasar peringkat terakhir: seluruh item tier *Immediate* PDS-001 §4 — untuk ketiga persona tanpa kecuali — berada di zona Context, Current Work, Decision, atau Reference; tidak satu pun di frame. **Persistensi bukan prioritas.**

Prinsip **Information First** (WF-000 §1.1, §9 poin 5) berlaku pada isi region, bukan pada frame; frame tidak menunda kemunculan konteks case.

---

## 8. Primary Reading Flow

Frame memiliki alur baca **sekali per sesi**, bukan per case:

1. **Orientasi sesi** — persona mode aktif menentukan kehadiran region. Sekali, pada `Login` (PWDM-001 §1; PDS-001 §7 poin 9).
2. **Serah terima ke Entry Point** — perhatian berpindah ke region Entry Area (Complaint Officer mode penanganan, Supervisor, Manager) atau langsung ke Primary Workspace (Complaint Officer mode intake), per NAV-001 §1.
3. **Alur baca WF-000 §2 berlaku di dalam region** — Top → Middle → Lower → Reference/History. Frame tidak berpartisipasi dan tidak dibaca ulang tiap case.

Tiga aturan WF-000 yang mengikat frame, dirujuk tanpa diulang isinya: **urutan baca = visual = keyboard** (§9 poin 10) — frame tidak menyisipkan titik fokus yang memecah urutan §2; **Focus Preservation** (§8) — frame tidak pernah menjadi tujuan pengembalian fokus; **responsif mengurangi keserempakan, bukan prioritas** (§7, §9 poin 11) — peringkat Bagian 7 tidak berubah di ukuran perangkat mana pun.

---

## 9. Primary Decision Point

**Tidak ada.**

PWDM-001 §2 mencatat tahap `Login` sebagai *"Tidak ada keputusan formal"* pada ketiga baris persona tanpa kecuali, dan tahap `Primary objective` dengan kolom Keputusan `—` di ketiganya. Frame hanya memetakan kedua tahap itu (Bagian 3).

Seluruh Critical Decision PWDM-001 §2 bersifat case-level dan menjadi ruang lingkup WF-001-02 s.d. WF-001-21. **One Primary Action** (WF-000 §1.3, §9 poin 6) karenanya terpenuhi secara trivial: nol keputusan, sehingga tidak mungkin ada dua yang bersaing.

Menambahkan keputusan apa pun ke frame akan menciptakan keputusan yang tidak ada di PWDM-001 §2 — dilarang IA-001 §7 dan NAV-001 §4 (*No dual workflow*).

*Jawaban ini adalah penerapan Bagian A.2: ketiadaan yang dirujuk, bukan bagian yang dikosongkan.*

---

## 10. Progressive Disclosure

Frame sendiri **tidak mengalami disclosure**: persisten sepanjang sesi, tidak pernah terlipat, tertunda, atau bertahap (Bagian 1, Bagian 5).

Yang diatur frame adalah **penegakan status region** — dan definisi tiap status berikut perilakunya sudah ditetapkan **WF-000 §4**, dirujuk di sini tanpa disalin (Bagian C.4). Frame tidak menambah, mengurangi, atau menafsirkan ulang status mana pun.

Tiga batas yang mengikat frame:

1. Frame **tidak menaikkan** status region mana pun di luar WF-000 §4 — perubahan status mensyaratkan revisi IA-001, bukan keputusan wireframe (WF-000 §9 poin 7–8).
2. Membuka region ber-disclosure **tidak menutup** Primary Workspace (WF-000 §1.6, §9 poin 9).
3. Perpindahan persona mode mengubah kehadiran region sesuai WF-000 §4 untuk mode baru — tanpa menambah region di luar closed set (IA-001 §8 poin 10).

---

## 11. Empty State

**Tidak berlaku.** Frame persisten dan tidak menampung objek informasi (Bagian 6), sehingga tidak ada isi yang bisa kosong.

Yang perlu ditegaskan justru tiga kondisi yang **bukan** empty state dan tidak boleh diperlakukan demikian:

| Kondisi | Perlakuan yang benar | Dasar |
|---|---|---|
| Complaint Officer (mode intake) tanpa region Entry Area | Region **tidak hadir** — bukan Queue kosong, bukan pesan "tidak ada antrian" | NAV-001 prinsip 6 (*"bukan Queue placeholder"*); IA-001 §7 |
| Manager tanpa region Primary Workspace | Region **tidak hadir** — bukan workspace kosong | PDS-001 §7 poin 3; NAV-001 prinsip 9 |
| Region berstatus `Hidden` per WF-000 §4 | **Tidak hadir secara struktural** — tidak dirender sebagai wadah kosong | WF-000 §4; dibaca menurut Bagian C.2 |

Kondisi kosong yang sesungguhnya — Queue tanpa item, Dashboard tanpa penyimpangan indikator — milik region yang bersangkutan (WF-001-02, WF-001-03, WF-001-19), bukan frame.

*Jawaban ini adalah penerapan Bagian A.2.*

---

## 12. Error State

Frame hanya mengenal kondisi yang **secara struktural sudah dilarang baseline**. Keduanya bersifat navigasi/otorisasi struktural; kegagalan teknis adalah implementasi dan berada di luar ruang lingkup dokumen ini.

| Kondisi | Perilaku | Dasar |
|---|---|---|
| **Destinasi di luar closed set NAV-001 (prinsip 1) diminta** | Ditolak; tidak ada destinasi baru yang boleh terbentuk lewat frame | NAV-001 prinsip 1; WF-000 §9 poin 3 |
| **Destinasi diminta pada sel `—` PDS-001 §5** bagi persona mode aktif | Tetap tidak terjangkau; frame tidak menyediakan jalur alternatif | NAV-001 prinsip 8; IA-001 §8 poin 5 |

Tidak ada kondisi error struktural lain yang ditetapkan kelima baseline bagi frame. Sesuai Bagian A.3, tidak ada yang ditambahkan.

Error state case-level (kegagalan submit, penolakan review, konflik status) milik wireframe case-level masing-masing.

---

## 13. Completion Criteria

Diambil dari WF-PLAN-001 §5, diterapkan pada WF-001-01:

| # | Kriteria (WF-PLAN-001 §5) | Penerapan |
|---|---|---|
| 1 | Zona sesuai Zone Priority | Frame tidak memuat zona; status kehadiran region dibaca dari WF-000 §4 tanpa disalin dan tanpa dinaikkan (Bagian 6, C.2) |
| 2 | Reading Flow konsisten | Urutan baca, visual, dan keyboard identik; frame tidak memecah urutan WF-000 §2 (Bagian 8) |
| 3 | Satu Primary Action | Terpenuhi dengan nol keputusan (Bagian 9) |
| 4 | Tertelusur ke baseline | Setiap pernyataan merujuk baris spesifik PDS-001, PWDM-001, IA-001, NAV-001, atau WF-000 |
| 5 | Tidak ada destinasi/zona/persona baru | Frame bukan destinasi; closed set NAV-001 (prinsip 1), IA-001 §4, dan WF-000 §3 utuh; tiga persona utuh |
| 6 | Continuity terpenuhi | **Tidak berlaku** — WF-PLAN-001 §5 poin 6 membatasi kriteria ini pada WF-001-09, 10, 11, 16, 17 |
| 7 | Dependency terpenuhi | Terpenuhi — tanpa dependency (WF-PLAN-001 §2) |

Kriteria tambahan khusus item ini, diturunkan dari Purpose (Bagian 1) dan status template (Bagian A):

8. **Stable Workspace terbukti** — dinyatakan eksplisit bahwa membuka region pendukung tidak menutup atau memindahkan Primary Workspace (Bagian 5, Bagian 10).
9. **Tidak ada region placeholder** — setiap region berstatus `Hidden` dinyatakan tidak hadir secara struktural, bukan kosong (Bagian 6, Bagian 11).
10. **Kosakata terjaga** — Destination, Region, dan Zone tidak pernah dipertukarkan (Bagian B).
11. **Tanpa duplikasi baseline** — tabel dan definisi milik WF-000 dirujuk, tidak disalin (Bagian C.4).

---

## Related
- `docs/ux/WF-001-R1-Wireframe-Package.md` — Release 1 package (mengindeks item ini)
- `docs/ux/PDS-001-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/NAV-001-Navigation-Architecture.md`
- `docs/ux/WF-000-Wireframe-Constitution-Layout-System.md`
- `docs/ux/WF-PLAN-001-Wireframe-Roadmap-Backlog.md`

## Future Work
Item backlog case-level (WF-001-02 s.d. 21): spesifikasi R1 ada di **WF-001-R1**; R2/R3 menyusul.
