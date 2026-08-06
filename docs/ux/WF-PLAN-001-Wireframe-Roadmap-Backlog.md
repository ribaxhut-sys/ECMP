# WF-PLAN-001 — Wireframe Roadmap & Backlog

| Field | Value |
|---|---|
| Document ID | WF-PLAN-001 |
| Title | Wireframe Roadmap & Backlog |
| Status | Draft — revisi mengikuti merge persona PDS-001 (UX-001 Documentation Update) |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Version | 1.1 |
| Date | 2026-08-05 |
| Parent | WF-000 |
| Subordination | ECMP-CONSTITUTION-001 → PDS-001 → PWDM-001 → IA-001 → NAV-001 → WF-000 → **WF-PLAN-001** → (future) WF-001 |
| Revision note | Kolom Primary/Secondary Persona digabung dari Customer Service dan Resolver/Handler menjadi **Complaint Officer** di seluruh backlog (Bagian 2). Item backlog dan Baseline rujukan tidak dihapus atau dikurangi — hanya ownership persona yang digabung, mengikuti task item 5 (merge screen ownership tanpa menghapus fungsionalitas). |

## Single responsibility

> Mengorganisasi pekerjaan wireframe masa depan menjadi **backlog yang bisa dikerjakan** — daftar wireframe yang dibutuhkan, prioritas, dan pengelompokan rilis.

WF-PLAN-001 **tidak** mendesain wireframe apa pun. Dokumen ini adalah rencana kerja untuk WF-001 (Low Fidelity Wireframes), bukan WF-001 itu sendiri.

WF-PLAN-001 **bukan** tempat mendefinisikan: Persona (PDS-001), Workflow/Decision (PWDM-001), Information Architecture/Zona (IA-001), Navigasi/Destinasi (NAV-001), atau aturan layout (WF-000). Setiap item backlog di sini hanya merujuk kombinasi persona × workflow × destinasi × zona yang sudah ada di kelima baseline tersebut — tidak ada workflow, destinasi, zona, atau persona baru yang diperkenalkan.

## Penomoran

Setiap item backlog adalah pecahan dari deliverable **WF-001** yang sudah dirujuk sebagai Future Work di UX-FOUNDATION-000, IA-001, NAV-001, dan WF-000. Untuk menghindari tabrakan ID dengan WF-001 itu sendiri, setiap item diberi ID **WF-001-NN**. WF-PLAN-001 tidak menciptakan dokumen wireframe baru — ia memberi nomor pada bagian-bagian WF-001 yang akan dikerjakan.

---

## 1. Metode Identifikasi

Setiap wireframe pada Bagian 2 diturunkan dari salah satu dari dua sumber, tidak ada sumber lain:

1. **Kombinasi Destinasi × Persona** pada NAV-001 §1–§2 (Entry Point, Primary/Secondary Navigation).
2. **Cabang Routine Work / Interruption / Critical Decision** yang eksplisit disebut PWDM-001 §1–§2 per persona — dipecah menjadi wireframe terpisah hanya bila PWDM-001 sendiri sudah membedakannya sebagai keputusan atau informasi yang berbeda.

Tidak ada wireframe di bawah yang dibuat dari asumsi tambahan di luar kedua sumber ini.

---

## 2. Wireframe Backlog

Legenda kolom **Baseline**: rujukan bagian dokumen sumber. **Dependencies**: item backlog lain yang harus tersedia sebagai referensi struktural sebelum item ini dikerjakan (bukan urutan pengerjaan wajib, hanya prasyarat rujukan).

| ID | Name | Primary Persona | Secondary Personas | Scope | Baseline | Dependencies |
|---|---|---|---|---|---|---|
| WF-001-01 | Global Shell & Header | *(semua)* | — | Frame orientasi tingkat modul, persisten, tidak spesifik-case | WF-000 §3 (Header) | — |
| WF-001-02 | Queue — Assigned List | Complaint Officer (mode penanganan) | — | Daftar case assigned, diurut sisa SLA; Entry Point mode penanganan | NAV-001 §1 Complaint Officer; IA-001 §5 | WF-001-01 |
| WF-001-03 | Queue — Priority Backlog | Supervisor | — | Eskalasi baru → SLA mendekati/lewat → antrian belum ter-assign, urutan tetap | NAV-001 §1, §2 Supervisor; PDS-001 §4 | WF-001-01 |
| WF-001-04 | Complaint Workspace — New Intake | Complaint Officer (mode intake) | — | Mencatat case baru; tidak ada case terkait aktif/closed | PWDM-001 §1 Complaint Officer Routine work | WF-001-01 |
| WF-001-05 | Complaint Workspace — Follow-up | Complaint Officer (mode intake) | — | Menjawab follow-up pada case aktif milik pelanggan tanpa tanya ulang | PWDM-001 §1 Complaint Officer Routine work | WF-001-04 |
| WF-001-06 | Complaint Workspace — Reopen Routing | Complaint Officer (mode intake) | Supervisor | Meneruskan permintaan reopen atas case closed ke Supervisor | PWDM-001 §1 Complaint Officer Routine work; IA-001 objek #13 | WF-001-04 |
| WF-001-07 | Complaint Workspace — Active Handling | Complaint Officer (mode penanganan) | — | Memulai/melanjutkan penanganan; memantau sisa SLA; aksi yang boleh dilakukan sekarang | PWDM-001 §1 Complaint Officer Routine work; IA-001 zona Current Work | WF-001-02 |
| WF-001-08 | Complaint Workspace — Submit for Review | Complaint Officer (mode penanganan) | Supervisor | Mengajukan hasil penanganan dengan bukti pendukung | PWDM-001 §2 Complaint Officer Critical decisions; IA-001 objek #7, #8 | WF-001-07 |
| WF-001-09 | Complaint Workspace — Rejected Resubmission | Complaint Officer (mode penanganan) | — | Menangani hasil ditolak reviewer; perbaiki & resubmit | PWDM-001 §1 Complaint Officer Interruptions; IA-001 §8 poin 9 | WF-001-08, WF-001-13 |
| WF-001-10 | Complaint Workspace — Reopened Continuation | Complaint Officer (mode penanganan) | — | Melanjutkan case lama yang dibuka kembali dengan riwayat penanganan utuh | PWDM-001 §1 Complaint Officer Interruptions; IA-001 §8 poin 9 | WF-001-07, WF-001-13 |
| WF-001-11 | Complaint Workspace — Escalation Context Handover | Complaint Officer (mode penanganan) | Supervisor | Memberi konteks yang diminta Supervisor untuk eskalasi berjalan, tanpa kehilangan progres case | PWDM-001 §1 Complaint Officer Interruptions; JTBD §3 | WF-001-07, WF-001-16 |
| WF-001-12 | Supporting Views — Evidence & Related Cases | Complaint Officer (mode penanganan) | — | Evidence/Attachment (Supporting); Related Cases (on-demand) | NAV-001 §1 Complaint Officer Secondary Nav; IA-001 objek #7, #21 | WF-001-07 |
| WF-001-13 | History — Decision History (Complaint Officer) | Complaint Officer (mode penanganan) | — | Alasan penolakan reviewer; riwayat penanganan sebelumnya | NAV-001 §1 Complaint Officer Secondary Nav; IA-001 §8 poin 9 | WF-001-07 |
| WF-001-14 | Complaint Workspace — Assignment | Supervisor | Complaint Officer (mode penanganan) | Distribusi case baru berdasar kapasitas unit | PWDM-001 §1 Supervisor Routine work; IA-001 objek #4, #15 | WF-001-03 |
| WF-001-15 | Complaint Workspace — Approval Review | Supervisor | Complaint Officer (mode penanganan) | Menilai pengajuan hasil Complaint Officer; approve/reject | PWDM-001 §2 Supervisor Critical decisions; IA-001 objek #8, #16 | WF-001-03, WF-001-08 |
| WF-001-16 | Complaint Workspace — Escalation Handling | Supervisor | Complaint Officer (mode penanganan) | Menangani atau meneruskan eskalasi baru | PWDM-001 §1 Supervisor Interruptions; IA-001 objek #12 | WF-001-03 |
| WF-001-17 | Complaint Workspace — Reopen Approval | Supervisor | Complaint Officer (kedua mode) | Menyetujui/menolak permintaan reopen atas case closed | PWDM-001 §1 Supervisor Interruptions; IA-001 objek #13 | WF-001-03, WF-001-06, WF-001-18 |
| WF-001-18 | History — Closure & Escalation Record (Supervisor) | Supervisor | — | Riwayat closure untuk reopen; alasan & konteks eskalasi | NAV-001 §1 Supervisor Secondary Nav; IA-001 §8 poin 9 | WF-001-03 |
| WF-001-19 | Dashboard — Aggregate KPI/Trend | Manager | — | Indikator agregat menyimpang dari target; tren per unit/kategori/periode | NAV-001 §1 Manager Entry Point; IA-001 §4 | WF-001-01 |
| WF-001-20 | Supporting Views — Unit Drill-down | Manager | — | Drill-down ke detail unit saat angka agregat mencurigakan, by exception | PDS-001 §4 Manager On-demand; NAV-001 §1 Manager Secondary Nav | WF-001-19 |
| WF-001-21 | Supporting Views — Customer Interaction History | Complaint Officer (mode intake) | — | Riwayat lengkap seluruh interaksi historis pelanggan, on-demand | IA-001 §5 Complaint Officer Secondary Nav; objek #20 | WF-001-04 |

**Catatan penggabungan (task item 5 — merge screen ownership tanpa menghapus fungsionalitas):** WF-001-04 (Complaint Registration/New Intake), WF-001-05 (Follow-up), dan WF-001-06 (Reopen Routing) — sebelumnya beratribusi ke persona Customer Service — kini menjadi bagian **Complaint Officer Workspace** dalam mode intake. WF-001-02, 07–13, 21 — sebelumnya beratribusi ke Resolver/Case Handler — kini menjadi bagian **Complaint Officer Workspace** dalam mode penanganan. Tidak ada item backlog yang dihapus, digabung fisik menjadi satu layar, atau kehilangan Scope/Baseline-nya; hanya kepemilikan persona (kolom Primary/Secondary) yang direvisi mengikuti PDS-001.

Total: 21 item backlog. Tidak ada wireframe terpisah untuk **Return to Queue** — ini adalah kembalinya pengguna ke WF-001-02/WF-001-03 yang sudah ada, bukan layar baru (NAV-001: "Return Path" kembali ke Queue yang sama).

---

## 3. Prioritas

Prioritas diturunkan langsung dari ranking eksplisit **PWDM-001 §3** ("Prioritas optimisasi tertinggi"), bukan penilaian baru:

> 1. Complaint Officer — kelengkapan data intake dan kesadaran SLA berkelanjutan. 2. Supervisor — distribusi beban & respons eskalasi. 3. Manager — frekuensi jauh lebih rendah, bukan prioritas optimisasi utama.

**P0 — Inti operasional harian** *(Continuous/Hourly/Many-times-per-hour per PWDM-001 §3, jalur primer NAV-001)*
WF-001-01, WF-001-02, WF-001-03, WF-001-04, WF-001-05, WF-001-07, WF-001-08, WF-001-14, WF-001-15

**P1 — Jalur pengecualian & kontinuitas** *(Daily/rare per PWDM-001 §3, tetap kritikal terhadap Continuity IA-001 §8 poin 9)*
WF-001-06, WF-001-09, WF-001-10, WF-001-11, WF-001-12, WF-001-13, WF-001-16, WF-001-17, WF-001-18, WF-001-21

**P2 — Lapisan pelaporan Manager** *(Daily/Weekly/Rare, eksplisit bukan prioritas optimisasi utama — PWDM-001 §3 poin 4)*
WF-001-19, WF-001-20

---

## 4. Pengelompokan Rilis

Rilis mengikuti urutan prioritas Bagian 3 satu-lawan-satu — tidak ada pengelompokan lain yang dipertimbangkan, karena PWDM-001 §3 sudah memberi urutan optimisasi yang mengikat.

### Release 1 — Inti Operasional (P0)
Menyelesaikan loop harian penuh: intake Complaint Officer → antrian & penanganan Complaint Officer → assignment & approval Supervisor. Tanpa rilis ini, Complaint Module tidak punya alur kerja end-to-end yang bisa didemonstrasikan.
Item: WF-001-01, 02, 03, 04, 05, 07, 08, 14, 15.

**Paket spesifikasi LF (implementation-oriented):** `docs/ux/WF-001-R1-Wireframe-Package.md` (WF-001-R1) — index, layout per layar, navigation map, component inventory, batch FE, readiness. Shell detail tetap di `WF-001-01-Global-Shell-Header.md`.

### Release 2 — Kontinuitas & Pengecualian (P1)
Menutup celah continuity yang sudah diidentifikasi PWDM-001 §4/§6: reject/resubmit, reopen, eskalasi, dan panel pendukung (Evidence, History, Interaction History). Tanpa rilis ini, jalur pengecualian yang sudah dipetakan baseline tidak punya representasi wireframe.
Item: WF-001-06, 09, 10, 11, 12, 13, 16, 17, 18, 21.

**Paket spesifikasi LF (implementation-oriented):** `docs/ux/WF-001-R2-Wireframe-Package.md` (WF-001-R2) — index, layout per layar, navigation map, component inventory, batch FE, readiness, completion traceability. R1 tetap baseline; R2 tidak mendesain ulang item P0.

### Release 3 — Pelaporan Manager (P2)
Dashboard agregat dan drill-down unit. Berdiri independen dari Release 1–2 karena Manager tidak pernah memasuki Complaint Workspace operasional (PDS-001 §7 poin 3) — tidak ada dependency silang ke rilis lain.
Item: WF-001-19, 20.

---

## 5. Completion Criteria

Satu item backlog dinyatakan **selesai** hanya bila seluruhnya berikut terpenuhi — merujuk langsung ke WF-000:

1. **Zona sesuai Zone Priority** — setiap zona yang muncul berstatus sesuai tabel WF-000 §4 untuk persona tersebut; tidak ada zona yang dinaikkan visibilitasnya tanpa revisi IA-001 (WF-000 §9 poin 7–8).
2. **Reading Flow konsisten** — urutan tampilan mengikuti Top→Middle→Lower→Reference/History (WF-000 §2); urutan visual, baca, dan keyboard identik (WF-000 §9 poin 10).
3. **Satu Primary Action** — tepat satu Critical Decision aktif per case pada wireframe tersebut, sesuai PWDM-001 §2 (WF-000 §9 poin 6).
4. **Tertelusur ke baseline** — setiap elemen informasi pada wireframe dapat dirunut ke satu baris di PDS-001/PWDM-001/IA-001/NAV-001; tidak ada informasi yang tidak punya sumber (WF-000 §9 poin 1).
5. **Tidak ada destinasi/zona/persona baru** — wireframe hanya memakai closed set yang sudah ada (WF-000 §9 poin 2–3).
6. **Continuity terpenuhi** — bila wireframe adalah hasil reject/reopen/eskalasi (WF-001-09, 10, 11, 16, 17), History terkait wajib hadir dalam wireframe yang sama, bukan langkah navigasi terpisah (IA-001 §8 poin 9; WF-000 §9 poin 9).
7. **Dependency terpenuhi** — seluruh item pada kolom Dependencies (Bagian 2) sudah berstatus selesai atau tersedia sebagai rujukan struktural.

Sebuah **rilis** (Bagian 4) dinyatakan selesai hanya bila seluruh item backlog di dalamnya memenuhi ketujuh kriteria di atas.

---

## Related
- `docs/ux/WF-001-R1-Wireframe-Package.md` — **Release 1 LF package (otoritatif untuk implementasi R1)**
- `docs/ux/WF-001-R2-Wireframe-Package.md` — **Release 2 LF package (otoritatif untuk implementasi R2)**
- `docs/ux/UX-DISC-001-Complete-UX-Discovery.md` — Complete UX Discovery (screen inventory & readiness)
- `docs/ux/PDS-001-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/NAV-001-Navigation-Architecture.md`
- `docs/ux/WF-000-Wireframe-Constitution-Layout-System.md`
- `docs/ux/WF-001-01-Global-Shell-Header.md`

## Future Work
WF-001 Release 3 wireframe package; High Fidelity / prototype — di luar ruang lingkup dokumen ini.
Release 1 LF specification: **selesai sebagai Draft di WF-001-R1** (bukan gambar visual).
Release 2 LF specification: **selesai sebagai Draft di WF-001-R2** (bukan gambar visual).
