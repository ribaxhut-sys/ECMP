# WF-PLAN-001 — Wireframe Roadmap & Backlog

| Field | Value |
|---|---|
| Document ID | WF-PLAN-001 |
| Title | Wireframe Roadmap & Backlog |
| Status | Draft |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Version | 1.0 |
| Date | 2026-08-03 |
| Parent | WF-000 |
| Subordination | ECMP-CONSTITUTION-001 → PDS-000 → PWDM-001 → IA-001 → NAV-001 → WF-000 → **WF-PLAN-001** → (future) WF-001 |

## Single responsibility

> Mengorganisasi pekerjaan wireframe masa depan menjadi **backlog yang bisa dikerjakan** — daftar wireframe yang dibutuhkan, prioritas, dan pengelompokan rilis.

WF-PLAN-001 **tidak** mendesain wireframe apa pun. Dokumen ini adalah rencana kerja untuk WF-001 (Low Fidelity Wireframes), bukan WF-001 itu sendiri.

WF-PLAN-001 **bukan** tempat mendefinisikan: Persona (PDS-000), Workflow/Decision (PWDM-001), Information Architecture/Zona (IA-001), Navigasi/Destinasi (NAV-001), atau aturan layout (WF-000). Setiap item backlog di sini hanya merujuk kombinasi persona × workflow × destinasi × zona yang sudah ada di kelima baseline tersebut — tidak ada workflow, destinasi, zona, atau persona baru yang diperkenalkan.

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
| WF-001-02 | Queue — Assigned List | Resolver/Handler | — | Daftar case assigned, diurut sisa SLA; Entry Point Handler | NAV-001 §1 Handler; IA-001 §5 | WF-001-01 |
| WF-001-03 | Queue — Priority Backlog | Supervisor | — | Eskalasi baru → SLA mendekati/lewat → antrian belum ter-assign, urutan tetap | NAV-001 §1, §2 Supervisor; PDS-000 §4 | WF-001-01 |
| WF-001-04 | Complaint Workspace — New Intake | Customer Service | — | Mencatat case baru; tidak ada case terkait aktif/closed | PWDM-001 §1 CS Routine work | WF-001-01 |
| WF-001-05 | Complaint Workspace — Follow-up | Customer Service | — | Menjawab follow-up pada case aktif milik pelanggan tanpa tanya ulang | PWDM-001 §1 CS Routine work | WF-001-04 |
| WF-001-06 | Complaint Workspace — Reopen Routing | Customer Service | Supervisor | Meneruskan permintaan reopen atas case closed ke Supervisor | PWDM-001 §1 CS Routine work; IA-001 objek #13 | WF-001-04 |
| WF-001-07 | Complaint Workspace — Active Handling | Resolver/Handler | — | Memulai/melanjutkan penanganan; memantau sisa SLA; aksi yang boleh dilakukan sekarang | PWDM-001 §1 Handler Routine work; IA-001 zona Current Work | WF-001-02 |
| WF-001-08 | Complaint Workspace — Submit for Review | Resolver/Handler | Supervisor | Mengajukan hasil penanganan dengan bukti pendukung | PWDM-001 §2 Handler Critical decisions; IA-001 objek #7, #8 | WF-001-07 |
| WF-001-09 | Complaint Workspace — Rejected Resubmission | Resolver/Handler | — | Menangani hasil ditolak reviewer; perbaiki & resubmit | PWDM-001 §1 Handler Interruptions; IA-001 §8 poin 9 | WF-001-08, WF-001-13 |
| WF-001-10 | Complaint Workspace — Reopened Continuation | Resolver/Handler | — | Melanjutkan case lama yang dibuka kembali dengan riwayat penanganan utuh | PWDM-001 §1 Handler Interruptions; IA-001 §8 poin 9 | WF-001-07, WF-001-13 |
| WF-001-11 | Complaint Workspace — Escalation Context Handover | Resolver/Handler | Supervisor | Memberi konteks yang diminta Supervisor untuk eskalasi berjalan, tanpa kehilangan progres case | PWDM-001 §1 Handler Interruptions; JTBD §3 | WF-001-07, WF-001-16 |
| WF-001-12 | Supporting Views — Evidence & Related Cases | Resolver/Handler | — | Evidence/Attachment (Supporting); Related Cases (on-demand) | NAV-001 §1 Handler Secondary Nav; IA-001 objek #7, #21 | WF-001-07 |
| WF-001-13 | History — Decision History (Handler) | Resolver/Handler | — | Alasan penolakan reviewer; riwayat penanganan sebelumnya | NAV-001 §1 Handler Secondary Nav; IA-001 §8 poin 9 | WF-001-07 |
| WF-001-14 | Complaint Workspace — Assignment | Supervisor | Resolver/Handler | Distribusi case baru berdasar kapasitas unit | PWDM-001 §1 Supervisor Routine work; IA-001 objek #4, #15 | WF-001-03 |
| WF-001-15 | Complaint Workspace — Approval Review | Supervisor | Resolver/Handler | Menilai pengajuan hasil handler; approve/reject | PWDM-001 §2 Supervisor Critical decisions; IA-001 objek #8, #16 | WF-001-03, WF-001-08 |
| WF-001-16 | Complaint Workspace — Escalation Handling | Supervisor | Resolver/Handler | Menangani atau meneruskan eskalasi baru | PWDM-001 §1 Supervisor Interruptions; IA-001 objek #12 | WF-001-03 |
| WF-001-17 | Complaint Workspace — Reopen Approval | Supervisor | Customer Service, Resolver/Handler | Menyetujui/menolak permintaan reopen atas case closed | PWDM-001 §1 Supervisor Interruptions; IA-001 objek #13 | WF-001-03, WF-001-06, WF-001-18 |
| WF-001-18 | History — Closure & Escalation Record (Supervisor) | Supervisor | — | Riwayat closure untuk reopen; alasan & konteks eskalasi | NAV-001 §1 Supervisor Secondary Nav; IA-001 §8 poin 9 | WF-001-03 |
| WF-001-19 | Dashboard — Aggregate KPI/Trend | Manager | — | Indikator agregat menyimpang dari target; tren per unit/kategori/periode | NAV-001 §1 Manager Entry Point; IA-001 §4 | WF-001-01 |
| WF-001-20 | Supporting Views — Unit Drill-down | Manager | — | Drill-down ke detail unit saat angka agregat mencurigakan, by exception | PDS-000 §4 Manager On-demand; NAV-001 §1 Manager Secondary Nav | WF-001-19 |
| WF-001-21 | Supporting Views — Customer Interaction History | Customer Service | — | Riwayat lengkap seluruh interaksi historis pelanggan, on-demand | IA-001 §5 CS Secondary Nav; objek #20 | WF-001-04 |

Total: 21 item backlog. Tidak ada wireframe terpisah untuk **Return to Queue** — ini adalah kembalinya pengguna ke WF-001-02/WF-001-03 yang sudah ada, bukan layar baru (NAV-001: "Return Path" kembali ke Queue yang sama).

---

## 3. Prioritas

Prioritas diturunkan langsung dari ranking eksplisit **PWDM-001 §3** ("Prioritas optimisasi tertinggi"), bukan penilaian baru:

> 1. Customer Service — kelengkapan data intake. 2. Resolver/Handler — kesadaran SLA berkelanjutan. 3. Supervisor — distribusi beban & respons eskalasi. 4. Manager — frekuensi jauh lebih rendah, bukan prioritas optimisasi utama.

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
Menyelesaikan loop harian penuh: intake CS → antrian & penanganan Handler → assignment & approval Supervisor. Tanpa rilis ini, Complaint Module tidak punya alur kerja end-to-end yang bisa didemonstrasikan.
Item: WF-001-01, 02, 03, 04, 05, 07, 08, 14, 15.

### Release 2 — Kontinuitas & Pengecualian (P1)
Menutup celah continuity yang sudah diidentifikasi PWDM-001 §4/§6: reject/resubmit, reopen, eskalasi, dan panel pendukung (Evidence, History, Interaction History). Tanpa rilis ini, jalur pengecualian yang sudah dipetakan baseline tidak punya representasi wireframe.
Item: WF-001-06, 09, 10, 11, 12, 13, 16, 17, 18, 21.

### Release 3 — Pelaporan Manager (P2)
Dashboard agregat dan drill-down unit. Berdiri independen dari Release 1–2 karena Manager tidak pernah memasuki Complaint Workspace operasional (PDS-000 §7 poin 3) — tidak ada dependency silang ke rilis lain.
Item: WF-001-19, 20.

---

## 5. Completion Criteria

Satu item backlog dinyatakan **selesai** hanya bila seluruhnya berikut terpenuhi — merujuk langsung ke WF-000:

1. **Zona sesuai Zone Priority** — setiap zona yang muncul berstatus sesuai tabel WF-000 §4 untuk persona tersebut; tidak ada zona yang dinaikkan visibilitasnya tanpa revisi IA-001 (WF-000 §9 poin 7–8).
2. **Reading Flow konsisten** — urutan tampilan mengikuti Top→Middle→Lower→Reference/History (WF-000 §2); urutan visual, baca, dan keyboard identik (WF-000 §9 poin 10).
3. **Satu Primary Action** — tepat satu Critical Decision aktif per case pada wireframe tersebut, sesuai PWDM-001 §2 (WF-000 §9 poin 6).
4. **Tertelusur ke baseline** — setiap elemen informasi pada wireframe dapat dirunut ke satu baris di PDS-000/PWDM-001/IA-001/NAV-001; tidak ada informasi yang tidak punya sumber (WF-000 §9 poin 1).
5. **Tidak ada destinasi/zona/persona baru** — wireframe hanya memakai closed set yang sudah ada (WF-000 §9 poin 2–3).
6. **Continuity terpenuhi** — bila wireframe adalah hasil reject/reopen/eskalasi (WF-001-09, 10, 11, 16, 17), History terkait wajib hadir dalam wireframe yang sama, bukan langkah navigasi terpisah (IA-001 §8 poin 9; WF-000 §9 poin 9).
7. **Dependency terpenuhi** — seluruh item pada kolom Dependencies (Bagian 2) sudah berstatus selesai atau tersedia sebagai rujukan struktural.

Sebuah **rilis** (Bagian 4) dinyatakan selesai hanya bila seluruh item backlog di dalamnya memenuhi ketujuh kriteria di atas.

---

## Related
- `docs/ux/PDS-000-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/NAV-001-Navigation-Architecture.md`
- `docs/ux/WF-000-Wireframe-Constitution-Layout-System.md`

## Future Work
WF-001 Low Fidelity Wireframes — pengerjaan aktual setiap item backlog (WF-001-01 s.d. WF-001-21) menjadi wireframe — di luar ruang lingkup dokumen ini.
