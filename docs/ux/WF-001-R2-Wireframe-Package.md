# WF-001-R2 — Wireframe Package Release 2 (Implementation-Oriented)

| Field | Value |
|---|---|
| Document ID | WF-001-R2 |
| Title | WF-001 Release 2 — Wireframe Package |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | **Draft — Wireframe R2 Complete (siap Review; belum Approved)** |
| Milestone | WF-001 Release 2 — Kontinuitas & Pengecualian (P1) |
| Parent | WF-PLAN-001 · WF-000 |
| Applicability | Mode A · Complaint Management Module only |
| Subordination | BC/BW (locked) → UX-DISC-001 → PDS-001 · PWDM-001 · IA-001 · NAV-001 → WF-000 → WF-PLAN-001 → **WF-001-R2** (extends WF-001-R1) |
| Does not | Discovery ulang · ubah BC/BW/governance · redesign R1 · gambar hi-fi · tema visual · kode React/CSS · API · DB · Mode B · Manager Dashboard (R3) |

## Cara baca

Paket ini adalah **spesifikasi wireframe fungsional** agar frontend dapat mengimplementasikan Release 2 tanpa dokumen discovery tambahan. R1 tetap baseline inti operasional; R2 **melengkapi** jalur kontinuitas & pengecualian.

| Deliverable | Lokasi |
|---|---|
| 1. Wireframe Index | §1 |
| 2. Screen definitions | §2 |
| 3. Low Fidelity layout specs | §3 |
| 4. Navigation Map | §4 |
| 5. Component Inventory | §5 |
| 6. Frontend Implementation Batches | §6 |
| 7. Frontend Readiness Checklist | §7 |
| 8. Completion Criteria Traceability | §8 |

**Reuse (jangan duplikasi):**

| Artefak | Peran |
|---|---|
| WF-PLAN-001 §4 Release 2 | Daftar item P1 yang mengikat |
| WF-001-R1 | Shell, Queue, intake/handling/submit/assign/approval — **tidak diubah** |
| WF-000 | Konstitusi layout / zona / responsif / continuity |
| WF-001-01 | Shell & kontrak template A–D (rujuk) |
| NAV-001 | Jalur navigasi; Secondary = Supporting Views / History dari dalam Workspace |
| UX-DISC-001 §6 / §8.2 / §11 Batch R2 | SCR-ID & cabang reject·reopen·eskalasi |
| PDS-001 / PWDM-001 / IA-001 / BW-000 | Persona, keputusan, zona, tahap workflow |

**Aturan kontinuitas mengikat (IA-001 §8 poin 9; WF-PLAN-001 §5 poin 6; WF-000 §5):**

> Bila wireframe adalah hasil reject / reopen / eskalasi (**WF-001-09, 10, 11, 16, 17**), **History terkait wajib hadir dalam wireframe yang sama**, bukan langkah navigasi terpisah yang harus dicari pengguna.

SCR-HX-01 / SCR-HX-02 adalah destinasi **History** (closed set) yang **embedded** di Workspace terkait — Stable Workspace (WF-000 §1.6): membuka History tidak mengganti destinasi Complaint Workspace.

**Di luar paket ini:**

- Redesign atau rewrite R1 screens
- Manager Dashboard / Unit Drill-down (Release 3: WF-001-19, 20)
- SCR-SET-01 Settings hygiene (disebut UX-DISC Batch R2 item 5, **bukan** item WF-PLAN-001 Release 2)
- Mode B / SSO / portal enterprise

---

## 1. Wireframe Index — Release 2

Item resmi WF-PLAN-001 Release 2: **WF-001-06, 09, 10, 11, 12, 13, 16, 17, 18, 21**.

| # | WF ID | SCR ID | Screen Name | Primary Persona | Destinasi NAV |
|---|---|---|---|---|---|
| 1 | WF-001-06 | SCR-WS-03 | Workspace — Reopen Routing | Complaint Officer (intake) | Complaint Workspace |
| 2 | WF-001-09 | SCR-WS-06 | Workspace — Rejected Resubmission | Complaint Officer (penanganan) | Complaint Workspace (+ History wajib) |
| 3 | WF-001-10 | SCR-WS-07 | Workspace — Reopened Continuation | Complaint Officer (penanganan) | Complaint Workspace (+ History wajib) |
| 4 | WF-001-11 | SCR-WS-08 | Workspace — Escalation Context Handover | Complaint Officer (penanganan) | Complaint Workspace (+ History/konteks) |
| 5 | WF-001-12 | SCR-SV-01 | Supporting — Evidence & Related Cases | Complaint Officer (penanganan) | Supporting Views |
| 6 | WF-001-13 | SCR-HX-01 | History — Decision History (Officer) | Complaint Officer (penanganan) | History |
| 7 | WF-001-16 | SCR-WS-11 | Workspace — Escalation Handling | Supervisor | Complaint Workspace (+ History wajib) |
| 8 | WF-001-17 | SCR-WS-12 | Workspace — Reopen Approval | Supervisor | Complaint Workspace (+ History wajib) |
| 9 | WF-001-18 | SCR-HX-02 | History — Closure & Escalation Record | Supervisor | History |
| 10 | WF-001-21 | SCR-SV-02 | Supporting — Customer Interaction History | Complaint Officer (intake) | Supporting Views |

**Prasyarat struktural R1 (bukan scope implementasi ulang):** SCR-SHELL-01, SCR-Q-01, SCR-Q-02, SCR-WS-01/02/04/05/09/10 — tersedia sebagai rujukan (WF-PLAN Dependencies).

**Return to Queue:** bukan layar — return path ke SCR-Q-01 atau SCR-Q-02 (NAV-001).

**Pemetaan Batch R2 UX-DISC-001 §11 ↔ item ini:**

| UX-DISC Batch R2 | WF / SCR dalam paket |
|---|---|
| 1. Reject/Resubmit + History Officer | WF-001-09, 13 → SCR-WS-06 + SCR-HX-01 |
| 2. Reopen routing + approval + continuation | WF-001-06, 17, 10 → SCR-WS-03, 12, 07 (+ SCR-HX-02 pada approval) |
| 3. Escalation handling + handover | WF-001-16, 11 → SCR-WS-11, 08 (+ SCR-HX-02) |
| 4. Supporting Evidence/Related + Interaction History | WF-001-12, 21 → SCR-SV-01, SCR-SV-02 |
| 5. Settings hygiene | **Di luar** WF-PLAN R2 — tidak ada wireframe di paket ini |

---

## 2. Screen Definitions

### 2.1 WF-001-06 / SCR-WS-03 — Workspace — Reopen Routing

| Field | Content |
|---|---|
| Screen ID | SCR-WS-03 |
| WF ID | WF-001-06 |
| Purpose | Meneruskan permintaan reopen atas **case closed** milik pelanggan ke Supervisor — tanpa mencatat case baru (hindari duplikat) |
| Primary Persona | Complaint Officer (mode intake) |
| Secondary | Supervisor (penerima keputusan di SCR-WS-12) |
| Entry Points | Dari SCR-WS-01 lookup: kontak + case terkait **closed** ditemukan; shell → Workspace intake |
| Exit Points | Route reopen sukses → tetap Workspace siap kontak berikutnya (bukan Queue); batal → SCR-WS-01 / konteks pelanggan |
| Main Components | Case closed identity; customer reference; reopen reason form; closure summary ringkas; primary Route |
| Main Actions | **Route reopen request** (satu primary); Cancel |
| Business Rules References | BC-8.2; PDS-001 §5 `REOPENED` Officer R (meneruskan); ECMP bukan Customer Master SoR |
| Workflow References | PWDM-001 Routine intake (meneruskan reopen); IA-001 objek #13 Reopen Request; BW-000 reopen path |
| Continuity | Ringkasan closure terakhir di Context; History formal Supervisor = SCR-HX-02 saat approval — **bukan** wajib full Decision History di layar routing Officer |
| Dependencies (WF-PLAN) | WF-001-04 (SCR-WS-01) |

### 2.2 WF-001-09 / SCR-WS-06 — Workspace — Rejected Resubmission

| Field | Content |
|---|---|
| Screen ID | SCR-WS-06 |
| WF ID | WF-001-09 |
| Purpose | Menangani hasil penanganan yang **ditolak reviewer**: perbaiki & resubmit dengan alasan penolakan terbawa |
| Primary Persona | Complaint Officer (mode penanganan) |
| Entry Points | SCR-Q-01 item kembali `IN_PROGRESS` setelah Reject dari SCR-WS-10; open dari queue assigned |
| Exit Points | Resubmit sukses → Return to Queue (`PENDING_REVIEW`); simpan progres → Return to Queue; Logout |
| Main Components | Case context; **History Area wajib** (SCR-HX-01: alasan reject + riwayat); correction / resolution panel; evidence; primary Resubmit |
| Main Actions | **Resubmit for review** (satu primary saat siap); Record correction (bila belum siap — tidak dua primary setara) |
| Business Rules References | BC reject → kembali penanganan; PDS-001 Officer R/A pada `IN_PROGRESS` |
| Workflow References | PWDM-001 Interruptions (hasil ditolak); IA-001 §8 poin 9 Continuity |
| Continuity | **Wajib:** SCR-HX-01 embedded (alasan penolakan reviewer) — dilarang layar resubmit tanpa History |
| Dependencies | WF-001-08, WF-001-13 |

### 2.3 WF-001-10 / SCR-WS-07 — Workspace — Reopened Continuation

| Field | Content |
|---|---|
| Screen ID | SCR-WS-07 |
| WF ID | WF-001-10 |
| Purpose | Melanjutkan **case lama** yang dibuka kembali (`REOPENED` / jalur setelah reopen disetujui) dengan riwayat penanganan utuh — bukan investigasi dari nol |
| Primary Persona | Complaint Officer (mode penanganan) |
| Entry Points | SCR-Q-01 setelah assignment reopen; open case reopened |
| Exit Points | Lanjut proses → Return to Queue; siap review → SCR-WS-05 (reuse R1 submit); Logout |
| Main Components | Case context (status reopen); **History Area wajib** (SCR-HX-01: riwayat penanganan + closure sebelumnya); Current Work; primary Continue |
| Main Actions | **Continue prior case** / Record progress (satu primary); CTA ke Submit when ready (sama pola R1 WS-04→WS-05) |
| Business Rules References | PDS-001 §5 `REOPENED`; BC reopen window (aturan bisnis terkunci — wireframe tidak mengarang window) |
| Workflow References | PWDM-001 Interruptions (case reopened); IA-001 Continuity |
| Continuity | **Wajib:** SCR-HX-01 embedded dengan riwayat penanganan sebelumnya |
| Dependencies | WF-001-07, WF-001-13 |

### 2.4 WF-001-11 / SCR-WS-08 — Workspace — Escalation Context Handover

| Field | Content |
|---|---|
| Screen ID | SCR-WS-08 |
| WF ID | WF-001-11 |
| Purpose | Memberi **konteks yang diminta Supervisor** untuk eskalasi berjalan, tanpa kehilangan progres case Officer |
| Primary Persona | Complaint Officer (mode penanganan) |
| Secondary | Supervisor |
| Entry Points | Dari SCR-WS-04 saat diminta konteks eskalasi; notifikasi/permintaan konteks pada case assigned |
| Exit Points | Handover konteks sukses → Return to Queue (progres case tetap); batal → SCR-WS-04 |
| Main Components | Case context; SLA; **History/konteks** ringkas (apa yang sudah dikerjakan); context package untuk Supervisor; primary Submit context |
| Main Actions | **Provide escalation context** (satu primary); Cancel |
| Business Rules References | PDS-001 §5 Escalation Officer **C**; JTBD handover |
| Workflow References | PWDM-001 Interruptions (konteks eskalasi diminta); IA-001 objek #12 |
| Continuity | History/progres terkait eskalasi **hadir di wireframe yang sama** (bukan navigasi History terpisah dulu); Supervisor menerima di SCR-WS-11 + SCR-HX-02 |
| Dependencies | WF-001-07, WF-001-16 |

### 2.5 WF-001-12 / SCR-SV-01 — Supporting — Evidence & Related Cases

| Field | Content |
|---|---|
| Screen ID | SCR-SV-01 |
| WF ID | WF-001-12 |
| Purpose | Supporting Views formal: **Evidence/Attachment** + **Related Cases** (on-demand) dari Workspace penanganan — tidak mengganti Primary Workspace |
| Primary Persona | Complaint Officer (mode penanganan) |
| Entry Points | Dari SCR-WS-04 / SCR-WS-05 / SCR-WS-06 / SCR-WS-07 (secondary nav Context Navigation) |
| Exit Points | Tutup panel → kembali fokus Workspace asal (destinasi tidak berubah) |
| Main Components | Evidence list + add/attach (izin state); Related Cases list (case lain pelanggan yang sama — referensi, bukan master) |
| Main Actions | Attach/view evidence; Open related case (read / navigate bila assigned & diizinkan); Close supporting view |
| Business Rules References | IA-001 objek #7 Evidence, #21 Related Cases; ECMP bukan Customer Master SoR |
| Workflow References | NAV-001 Secondary Nav Officer penanganan; PWDM-001 evidence untuk critical decision |
| Continuity | Tidak menggantikan History wajib pada reject/reopen — pelengkap Evidence |
| Dependencies | WF-001-07 |
| Catatan vs R1 | R1 memakai C-EVID-MIN di WS-05/10; R2 **mengangkat** Supporting Views formal tanpa menghapus daftar minimal di Decision path |

### 2.6 WF-001-13 / SCR-HX-01 — History — Decision History (Officer)

| Field | Content |
|---|---|
| Screen ID | SCR-HX-01 |
| WF ID | WF-001-13 |
| Purpose | Menampilkan **alasan penolakan reviewer** dan/atau **riwayat penanganan sebelumnya** agar Officer tidak merekonstruksi dari nol |
| Primary Persona | Complaint Officer (mode penanganan) |
| Entry Points | **Embedded wajib** di SCR-WS-06 dan SCR-WS-07; on-demand dari Workspace penanganan lain bila Continuity relevan |
| Exit Points | Tetap di Workspace induk (History Area / destinasi History dari dalam Workspace) |
| Main Components | Decision History list: reject reason + actor + time; prior handling notes/status transitions; read-only |
| Main Actions | Baca / expand entri; tidak ada primary decision di History sendiri |
| Business Rules References | IA-001 objek #9 Decision History; PWDM-001 §4 Continuity |
| Workflow References | NAV-001 Secondary Nav; WF-000 History band |
| Continuity | Wajib menyertai Decision pada reject/reopen Officer paths |
| Dependencies | WF-001-07 |

### 2.7 WF-001-16 / SCR-WS-11 — Workspace — Escalation Handling

| Field | Content |
|---|---|
| Screen ID | SCR-WS-11 |
| WF ID | WF-001-16 |
| Purpose | Supervisor **menangani atau meneruskan** eskalasi baru — dengan alasan & konteks eskalasi terbawa |
| Primary Persona | Supervisor |
| Secondary | Complaint Officer (mode penanganan) |
| Entry Points | SCR-Q-02 segmen **Escalation baru** (aksi penuh — menutup PARTIAL R1) |
| Exit Points | Keputusan eskalasi selesai → Return to Queue SCR-Q-02; minta konteks Officer → jalur ke SCR-WS-08 (logis lintas persona) |
| Main Components | Case context ringkas; **History Area wajib** (SCR-HX-02: alasan & konteks eskalasi); Decision: Handle vs Forward; optional request context |
| Main Actions | **Handle escalation** **atau** **Forward escalation** (mutual exclusive One Primary Action); optional Request officer context (bukan primary kedua setara — mode terpisah / secondary) |
| Business Rules References | BC-8.3; PDS-001 §5 Escalation Supervisor R/A |
| Workflow References | PWDM-001 Interruptions (eskalasi baru); IA-001 objek #12 |
| Continuity | **Wajib:** SCR-HX-02 embedded |
| Dependencies | WF-001-03 |

### 2.8 WF-001-17 / SCR-WS-12 — Workspace — Reopen Approval

| Field | Content |
|---|---|
| Screen ID | SCR-WS-12 |
| WF ID | WF-001-17 |
| Purpose | Supervisor **menyetujui atau menolak** permintaan reopen atas case closed |
| Primary Persona | Supervisor |
| Secondary | Complaint Officer (kedua mode — routing dari intake; continuation di penanganan) |
| Entry Points | SCR-Q-02 (item reopen pending); dari aliran SCR-WS-03 |
| Exit Points | Approve → case masuk jalur `REOPENED` / assignment lanjut → Return to Queue; Reject reopen → Return to Queue |
| Main Components | Reopen request (alasan pelanggan/Officer); **History Area wajib** (SCR-HX-02: riwayat closure); Decision Approve/Reject reopen |
| Main Actions | **Approve reopen** **atau** **Reject reopen** (mutual exclusive) |
| Business Rules References | PDS-001 §5 `REOPENED` Supervisor A; BC reopen rules terkunci |
| Workflow References | PWDM-001 Interruptions (permintaan reopen); IA-001 objek #13 |
| Continuity | **Wajib:** SCR-HX-02 (riwayat closure) embedded |
| Dependencies | WF-001-03, WF-001-06, WF-001-18 |

### 2.9 WF-001-18 / SCR-HX-02 — History — Closure & Escalation Record (Supervisor)

| Field | Content |
|---|---|
| Screen ID | SCR-HX-02 |
| WF ID | WF-001-18 |
| Purpose | **Riwayat closure** untuk keputusan reopen; **alasan & konteks eskalasi** untuk keputusan eskalasi |
| Primary Persona | Supervisor |
| Entry Points | **Embedded wajib** di SCR-WS-11 dan SCR-WS-12; on-demand dari Workspace Supervisor saat Continuity relevan |
| Exit Points | Tetap di Workspace induk |
| Main Components | Closure record (kapan/siapa/resolution); Escalation reason & context package; read-only timeline/status |
| Main Actions | Baca / expand; tidak ada primary decision di History sendiri |
| Business Rules References | IA-001 objek #9, #12; PWDM-001 §4 Continuity Supervisor |
| Workflow References | NAV-001 Secondary Nav Supervisor |
| Continuity | Wajib menyertai Decision pada reopen·eskalasi Supervisor |
| Dependencies | WF-001-03 |

### 2.10 WF-001-21 / SCR-SV-02 — Supporting — Customer Interaction History

| Field | Content |
|---|---|
| Screen ID | SCR-SV-02 |
| WF ID | WF-001-21 |
| Purpose | Riwayat lengkap **seluruh interaksi historis pelanggan** (on-demand) — mendukung follow-up personal tanpa tanya ulang |
| Primary Persona | Complaint Officer (mode intake) |
| Entry Points | Dari SCR-WS-01 / SCR-WS-02 / SCR-WS-03 (Supporting Views secondary) |
| Exit Points | Tutup → tetap Workspace intake |
| Main Components | Interaction list (waktu, kanal, ringkasan); filter scoped pelanggan; read-only dari cache/CRM referensi |
| Main Actions | Lookup / expand entri; Close supporting view |
| Business Rules References | IA-001 objek #20; PDS-001 §4 On-demand; **bukan** Customer Master SoR — referensi/cache saja |
| Workflow References | NAV-001 Secondary Nav Officer intake; IA-001 §5 |
| Dependencies | WF-001-04 |
| Catatan | Terpisah dari Related Cases (objek #21) dan dari Decision History case (#9) — jangan digabung |

---

## 3. Low Fidelity Wireframe Specification

Konvensi sama dengan WF-001-R1 §3. Pemetaan region prompt → WF-000. Jawaban `Tidak ada` wajib beralasan.

**Reading flow:** Top (Context) → Middle (Current Work + Decision) → Lower (Evidence) → Reference/History on-demand atau **wajib** pada continuity screens.

---

### 3.1 SCR-WS-03 — Reopen Routing

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Judul “Reopen routing”; indikator mode intake; identitas case closed |
| Filter Area | Tidak ada |
| Search | Tidak ada (case closed sudah terpilih dari lookup) |
| Main Content | **Context:** customer ref + case_id + status `CLOSED` + tanggal closure. **Current Work:** ringkasan closure (resolution code/summary read-only). **Decision:** form alasan permintaan reopen |
| Side Panel | Closure summary (Contextual) |
| Timeline Area | Ringkas last-closure saja; full Supervisor History di SCR-HX-02 saat approval — tidak menipu data fiktif |
| Action Buttons | Primary: **Route reopen request**; Secondary: **Cancel** |
| Dialogs | Confirm route |
| Notifications | Validasi alasan wajib; error bila case bukan closed |
| Empty State | Tidak applicable bila entry mensyaratkan case closed |
| Loading State | Load case closed + submit in flight |
| Error State | Case aktif → arahkan Follow-up (SCR-WS-02); tidak ada case → New Intake |
| Permission Visibility | Officer intake + izin create/route reopen request; sembunyikan Approve reopen / Assign |
| Responsive Behaviour | Context → Summary → Reason → Action (WF-000) |

**Region WF-000:** Primary Workspace (Context + Decision Conditionally Visible). Destinasi: Complaint Workspace.

---

### 3.2 SCR-WS-06 — Rejected Resubmission

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Return to Queue; case_id; status `IN_PROGRESS` (post-reject); badge “Rejected” |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | **Context:** customer, assignment, SLA. **History (wajib, Always/Conditionally Visible di layar ini):** SCR-HX-01 — alasan reject + reviewer + waktu. **Current Work:** koreksi resolution / catatan perbaikan. **Evidence:** list + link buka SCR-SV-01 |
| Side Panel | History compact (desktop) atau History section di atas Decision (mobile) — **tidak boleh dihilangkan** |
| Timeline Area | = History Area (SCR-HX-01); wajib |
| Action Buttons | Primary: **Resubmit for review** (saat siap); bila belum siap: Primary **Save correction** saja — tidak dua primary setara |
| Dialogs | Confirm resubmit |
| Notifications | Peringatan bila mencoba resubmit tanpa membaca/expand reject reason (boleh soft-gate UX, bukan business rule baru) |
| Empty State | History kosong = **Error State** Continuity — tampilkan “Riwayat penolakan tidak tersedia” + blokir primary resubmit sampai data ada atau retry |
| Loading State | Load case + history |
| Error State | 409 conflict; history fetch gagal |
| Permission Visibility | Assignee; permission transition ke `PENDING_REVIEW` |
| Responsive Behaviour | History **sebelum** correction form pada mobile (Continuity sebelum aksi) |

**Region WF-000:** Primary Workspace + History Area (wajib). Continuity screens: WF-PLAN §5 poin 6.

---

### 3.3 SCR-WS-07 — Reopened Continuation

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Return to Queue; case_id; status `REOPENED` / in-progress setelah reopen; badge Reopened |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | **Context:** customer, prior closure marker, assignment. **History wajib (SCR-HX-01):** riwayat penanganan + closure sebelumnya. **Current Work:** lanjutkan pekerjaan (bukan form intake baru). **Evidence:** Conditionally Visible + link SCR-SV-01 |
| Side Panel | Prior history compact |
| Timeline Area | History Area wajib |
| Action Buttons | Primary dinamis satu: **Continue handling** / **Record progress** / CTA **Submit for review** (ke SCR-WS-05) — pola sama Active Handling R1 |
| Dialogs | Konfirmasi “lanjutkan case lama” saat first open (opsional) |
| Notifications | SLA setelah reopen |
| Empty State | History kosong = Error Continuity (sama pola WS-06) |
| Loading State | Load case + history |
| Error State | Permission / state conflict |
| Permission Visibility | Officer penanganan pada case assigned/reopened |
| Responsive Behaviour | History → Current Work → Action |

**Region WF-000:** Primary Workspace + History Area (wajib).

---

### 3.4 SCR-WS-08 — Escalation Context Handover

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Return to Queue / Back to handling; case_id; indikator “Escalation context requested” |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | **Context:** case + SLA + requester (Supervisor). **History/progres:** ringkasan apa yang sudah dikerjakan (boleh subset SCR-HX-01). **Decision:** paket konteks (catatan terstruktur / checklist yang diminta) |
| Side Panel | Escation request summary |
| Timeline Area | Progress/history terkait — hadir di wireframe yang sama |
| Action Buttons | Primary: **Submit context to Supervisor**; Secondary: Cancel |
| Dialogs | Confirm submit context |
| Notifications | Sukses — case progres Officer **tidak direset** |
| Empty State | Tidak ada permintaan konteks → jangan entry layar ini |
| Loading State | Load request + case |
| Error State | Eskalasi sudah ditutup / tidak lagi membutuhkan konteks |
| Permission Visibility | Officer pada case; bukan tombol Handle/Forward eskalasi Supervisor |
| Responsive Behaviour | Request summary → Context package → Action |

**Region WF-000:** Primary Workspace; Decision Conditionally Visible (Escalation context). Continuity: WF-001-11.

---

### 3.5 SCR-SV-01 — Evidence & Related Cases

| Region | Spec |
|---|---|
| Header | Via shell (Workspace induk tetap) |
| Toolbar | Judul Supporting: “Evidence & Related”; kontrol Close |
| Filter Area | Tab atau segmen: Evidence | Related Cases (dua objek terpisah — jangan digabung jadi satu list) |
| Search | Cari nama file / case_id related dalam scope pelanggan |
| Main Content | **Evidence:** daftar attachment (nama, tipe, waktu, status); aksi view/download/add sesuai permission & state. **Related Cases:** daftar case lain pelanggan (id, status, subject) — read/referensi |
| Side Panel | Tidak mengganti Primary Workspace — panel/overlay Supporting Workspace (WF-000 §3) |
| Timeline Area | Tidak ada (bukan History Decision) |
| Action Buttons | Add evidence (bila diizinkan); Open related (bila diizinkan); **Close** |
| Dialogs | Confirm discard upload gagal |
| Notifications | Upload error; file type/size (aturan bisnis terkunci — tidak mengarang limit di wireframe) |
| Empty State | “Belum ada evidence” / “Tidak ada related cases” |
| Loading State | Skeleton list |
| Error State | Retry; 403 hide add |
| Permission Visibility | Officer penanganan; Supervisor boleh read saat approval (reuse); Manager Hidden |
| Responsive Behaviour | Full-screen sheet di mobile; split tab Evidence/Related |

**Region WF-000:** Supporting Workspace. Destinasi: Supporting Views. **Stable Workspace:** Primary tetap di belakang.

---

### 3.6 SCR-HX-01 — Decision History (Officer)

| Region | Spec |
|---|---|
| Header | Via shell / toolbar Workspace induk |
| Toolbar | “Decision history”; Close bila on-demand (pada WS-06/07: tidak closeable hingga Continuity terpenuhi — boleh collapse visual tetapi data wajib loaded) |
| Filter Area | Opsional filter tipe: Reject reasons | Handling notes | Status changes — **tidak** menghapus reject reason dari default view pada WS-06 |
| Search | Tidak wajib |
| Main Content | Chronological / reverse-chronological entries: actor, action type, reason text, timestamp; expand detail |
| Side Panel | Embedded in Workspace (lihat 3.2 / 3.3) |
| Timeline Area | **Ini** adalah Timeline/History Area |
| Action Buttons | Tidak ada primary business decision |
| Dialogs | Tidak ada |
| Notifications | Fetch error |
| Empty State | Hanya acceptable di jalur non-continuity on-demand; pada WS-06/07 = error continuity |
| Loading State | Skeleton entries |
| Error State | Retry |
| Permission Visibility | Officer pada case; read-only |
| Responsive Behaviour | Full width under Context |

**Region WF-000:** History Area. Destinasi: History.

---

### 3.7 SCR-WS-11 — Escalation Handling

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Return to Queue; case_id; badge Escalation; prioritas segmen Q-02 |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | **Context:** case identity + SLA. **History wajib (SCR-HX-02):** alasan eskalasi + konteks (+ hasil SCR-WS-08 bila ada). **Decision:** mode Handle **atau** mode Forward |
| Side Panel | Escalation context package |
| Timeline Area | History Area wajib |
| Action Buttons | Satu primary mode: **Handle** **atau** **Forward**; kontrol secondary: **Request officer context** (men-trigger jalur SCR-WS-08 — bukan primary kedua) |
| Dialogs | Confirm Handle / Confirm Forward |
| Notifications | Validasi alasan forward bila wajib aturan bisnis |
| Empty State | History eskalasi kosong = Error Continuity |
| Loading State | Load escalation + history |
| Error State | 409; already resolved |
| Permission Visibility | Supervisor escalation R/A; Officer read-only bila URL tersesat |
| Responsive Behaviour | History → Decision sticky bottom mobile |

**Region WF-000:** Primary Workspace (Decision Always Visible Supervisor) + History Area. Menutup gap R1 PARTIAL pada aksi eskalasi Q-02.

---

### 3.8 SCR-WS-12 — Reopen Approval

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Return to Queue; case_id; status `CLOSED` + pending reopen request |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | **Context:** case + customer. **Request:** alasan reopen (dari SCR-WS-03). **History wajib (SCR-HX-02):** riwayat closure. **Decision:** Approve reopen **atau** Reject reopen |
| Side Panel | Closure record compact |
| Timeline Area | History Area wajib |
| Action Buttons | Mutual exclusive: **Approve reopen** / **Reject reopen** (+ reason pada reject) |
| Dialogs | Confirm approve; Confirm reject |
| Notifications | Validasi |
| Empty State | Closure history kosong = Error Continuity |
| Loading State | Load request + closure history |
| Error State | Request sudah diputuskan; window reopen ditolak oleh aturan bisnis → pesan + disable Approve |
| Permission Visibility | Supervisor; Officer tidak Approve |
| Responsive Behaviour | History → Request → Decision |

**Region WF-000:** Primary Workspace + History Area (wajib).

---

### 3.9 SCR-HX-02 — Closure & Escalation Record (Supervisor)

| Region | Spec |
|---|---|
| Header | Via shell / Workspace induk |
| Toolbar | “Closure & escalation history” |
| Filter Area | Segmen: Closure record | Escalation context — default mengikuti Workspace induk (WS-12 → Closure; WS-11 → Escalation) |
| Search | Tidak wajib |
| Main Content | Closure: resolution, closer, closed_at, prior notes. Escalation: reason, severity/context, officer context package, timestamps |
| Side Panel | Embedded |
| Timeline Area | History Area |
| Action Buttons | Tidak ada primary decision |
| Dialogs | Tidak ada |
| Notifications | Fetch error |
| Empty State | Error pada continuity parents |
| Loading State | Skeleton |
| Error State | Retry |
| Permission Visibility | Supervisor; read-only |
| Responsive Behaviour | Full width under Context |

**Region WF-000:** History Area.

---

### 3.10 SCR-SV-02 — Customer Interaction History

| Region | Spec |
|---|---|
| Header | Via shell (Workspace intake tetap) |
| Toolbar | “Interaction history”; Close |
| Filter Area | Filter kanal / rentang waktu (scoped pelanggan aktif) |
| Search | Cari dalam interaksi pelanggan ini |
| Main Content | List interaksi historis: waktu, kanal, ringkasan, referensi case bila ada — **read-only** |
| Side Panel | Supporting panel / sheet — tidak ganti Workspace |
| Timeline Area | Bukan Decision History case — Interaction History = zona **Reference** (IA-001 objek #20) |
| Action Buttons | Close; tidak create case dari sini sebagai primary |
| Dialogs | Tidak ada |
| Notifications | Sumber data referensi tidak tersedia |
| Empty State | “Belum ada interaksi tercatat” |
| Loading State | Skeleton |
| Error State | Retry; jangan tulis ke Customer Master |
| Permission Visibility | Officer intake; on-demand (default collapsed sampai dibuka) |
| Responsive Behaviour | Full-screen sheet mobile |

**Region WF-000:** Reference Area via Supporting Views. Destinasi: Supporting Views.

---

## 4. Navigation Map — Release 2

Melengkapi peta R1. Shell & happy path R1 tetap berlaku; di bawah hanya **cabang P1**.

```
═══ REUSE R1 (tidak digambar ulang) ═══
SCR-AUTH-01 → SCR-SHELL-01
  Officer intake: SCR-WS-01 ◄──► SCR-WS-02
  Officer handling: SCR-Q-01 → SCR-WS-04 → SCR-WS-05 → Return Q-01
  Supervisor: SCR-Q-02 → SCR-WS-09 | SCR-WS-10 → Return Q-02

═══ R2 — REJECT / RESUBMIT ═══
SCR-WS-10 Reject (R1)
        │ status → IN_PROGRESS
        ▼
SCR-Q-01 (item rejected)
        │ open
        ▼
SCR-WS-06 Rejected Resubmission
        ├── History embedded: SCR-HX-01 (wajib)
        ├── Supporting on-demand: SCR-SV-01
        │ resubmit
        ▼
Return to Queue → SCR-Q-01 (PENDING_REVIEW)
        │
        ▼
SCR-Q-02 → SCR-WS-10 (R1 approval ulang)

═══ R2 — REOPEN ═══
SCR-WS-01 lookup → case CLOSED
        ▼
SCR-WS-03 Reopen Routing
        │ route request
        ▼
(tetap Workspace intake — siap kontak berikutnya)

SCR-Q-02 → SCR-WS-12 Reopen Approval
        ├── History embedded: SCR-HX-02 (closure, wajib)
        │
        ├─ Approve → jalur REOPENED / assign
        │         ▼
        │   SCR-Q-01 → SCR-WS-07 Reopened Continuation
        │         ├── History embedded: SCR-HX-01 (wajib)
        │         └── siap → SCR-WS-05 (R1) → …
        │
        └─ Reject reopen → Return to Queue SCR-Q-02

═══ R2 — ESCALATION ═══
SCR-Q-02 segmen Escalation
        │ open (aksi penuh R2)
        ▼
SCR-WS-11 Escalation Handling
        ├── History embedded: SCR-HX-02 (wajib)
        ├── optional Request context
        │         ▼
        │   (Officer) SCR-WS-08 Escalation Context Handover
        │         └── Return to Queue SCR-Q-01 (progres tetap)
        │
        └─ Handle | Forward → Return to Queue SCR-Q-02

═══ R2 — SUPPORTING (on-demand) ═══
Officer penanganan Workspace (WS-04/05/06/07)
        └── SCR-SV-01 Evidence & Related Cases
              (Stable Workspace — tutup kembali ke induk)

Officer intake Workspace (WS-01/02/03)
        └── SCR-SV-02 Customer Interaction History
              (Stable Workspace — tutup kembali ke induk)

Logout ← selalu dari Shell
```

**Aturan:**

- Supporting Views / History **tidak** menjadi Entry Point sesi.
- Tidak ada destinasi baru di luar closed set IA-001.
- Return to Queue tetap return path, bukan layar.
- Manager / Dashboard **tidak** masuk peta R2.

---

## 5. Component Inventory (Reusable)

Komponen **baru atau diperluas** untuk R2. Komponen R1 (C-SHELL, C-TABLE, C-CASE-HDR, …) **di-reuse** tanpa redesign.

| Component ID | Name | Dipakai di | Catatan |
|---|---|---|---|
| C-HIST-OFF | Decision History Panel (Officer) | HX-01; embedded WS-06, WS-07, (08) | Alasan reject + prior handling |
| C-HIST-SUP | Closure & Escalation History Panel | HX-02; embedded WS-11, WS-12 | Closure record / escalation context |
| C-REOPEN-REQ | Reopen Request Form | WS-03 | Alasan reopen; case closed context |
| C-REOPEN-DEC | Reopen Decision Panel | WS-12 | Approve/Reject reopen mutual exclusive |
| C-REJECT-CONT | Rejection Continuity Banner | WS-06 | Highlight reject reason summary |
| C-REOPEN-BADGE | Reopened State Badge | WS-07, Q-01 row | Status continuity |
| C-ESC-CTX | Escalation Context Package | WS-08, WS-11, HX-02 | Konteks untuk Supervisor |
| C-ESC-DEC | Escalation Decision Panel | WS-11 | Handle vs Forward |
| C-EVID-FULL | Evidence Supporting Panel | SV-01 | Mengangkat C-EVID-MIN R1 |
| C-REL-CASES | Related Cases List | SV-01 | Objek #21 — terpisah Interaction History |
| C-INTERACT | Customer Interaction History List | SV-02 | Objek #20 — Reference / on-demand |
| C-SUP-SHEET | Supporting Views Host | SV-01, SV-02 | Overlay/sheet; Stable Workspace |
| C-HIST-HOST | History Area Host | HX-01, HX-02 | Embedded wajib pada continuity parents |
| C-CONT-GATE | Continuity Empty/Error Gate | WS-06, 07, 11, 12 | Blokir primary bila History wajib gagal load |

**Reuse dari R1 tanpa perubahan kontrak:** C-SHELL, C-NAV, C-CASE-HDR, C-CUST, C-BADGE-*, C-ACT, C-DIALOG, C-TOAST, C-EMPTY, C-LOAD, C-ERR, C-PERM, C-RESOLVE, C-EVID-MIN (tetap pada jalur submit/approval cepat).

**Tidak di R2:** Manager KPI cards, Unit drill-down, portal chrome enterprise, Comment Panel generik di luar History/Interaction yang sudah didefinisikan.

---

## 6. Frontend Implementation Batches

Vertical slices R2; mengasumsikan R1 B0–B5 (dan B6 list eskalasi) sudah ada atau paralel setelah R1 minimal demo.

| Batch | Nama | Screens | Definisi “Done” slice |
|---|---|---|---|
| **R2-B1** | Reject continuity | SCR-HX-01 (embedded), SCR-WS-06 | Setelah Reject R1: Officer buka case → lihat alasan reject → resubmit → `PENDING_REVIEW` |
| **R2-B2** | Reopen chain | SCR-WS-03, SCR-HX-02 (closure), SCR-WS-12, SCR-WS-07 | Intake route reopen → Supervisor approve/reject → Officer continuation + history |
| **R2-B3** | Escalation full | SCR-WS-11, SCR-WS-08, SCR-HX-02 (escalation) | Q-02 eskalasi → Handle/Forward; optional context handover tanpa reset progres |
| **R2-B4** | Supporting Evidence/Related | SCR-SV-01 | Buka dari WS-04/05/06/07; attach/view; related list; close kembali Workspace |
| **R2-B5** | Interaction History | SCR-SV-02 | Buka dari WS-01/02/03; read-only referensi; close kembali intake |

**Urutan rekomendasi:** R2-B1 → R2-B2 → R2-B3 → R2-B4 → R2-B5  
*(selaras UX-DISC §11 Batch R2 poin 1–4; Continuity dulu sebelum Supporting on-demand).*

**Demo cabang minimal:** R1 happy path + R2-B1 (reject/resubmit).  
**Demo kontinuitas penuh:** + R2-B2 + R2-B3.

Jangan campur silent cutover dual-SoT (DEC-020) — pilih satu permukaan per batch, sama catatan R1.

---

## 7. Frontend Readiness Checklist

| Screen | Status | Alasan |
|---|---|---|
| SCR-WS-03 Reopen Routing | **READY** | Spec lengkap; bedakan jelas dari New Intake & Follow-up |
| SCR-WS-06 Rejected Resubmission | **READY** | Continuity gate + HX-01 wajib terspesifikasi |
| SCR-WS-07 Reopened Continuation | **READY** | History wajib; reuse Submit R1 |
| SCR-WS-08 Escalation Handover | **READY** | Satu primary; progres tidak direset |
| SCR-SV-01 Evidence & Related | **READY** | Supporting host + dua objek terpisah |
| SCR-HX-01 Decision History Officer | **READY** | Embedded kontrak jelas |
| SCR-WS-11 Escalation Handling | **READY** | Menutup PARTIAL R1 Q-02 aksi eskalasi |
| SCR-WS-12 Reopen Approval | **READY** | HX-02 closure wajib |
| SCR-HX-02 Closure & Escalation | **READY** | Dua segmen sesuai parent |
| SCR-SV-02 Interaction History | **READY** | On-demand Reference; no SoR write |

### Blockers lintas-layar (bukan discovery)

| ID | Item | Dampak R2 |
|---|---|---|
| R2-B1 | Paket UX masih Draft | Lab OK; sign-off menunggu Approval |
| R2-B2 | R1 belum diimplementasi | Implementasi R2 bergantung Shell/Queue/WS R1 sebagai prasyarat struktural |
| R2-B3 | Data Continuity (reject reason / closure / escalation context) di API | Wireframe READY; slice FE boleh PARTIAL teknis sampai field history tersedia — **jangan** fake timeline |
| R2-B4 | Interaction History sumber referensi | UX READY; kosong + retry lebih baik daripada invent data |
| R2-B5 | Dual route legacy vs CM Aggregate | Sama R1 — satu permukaan per batch |

### Verdict

**Frontend developer dapat memulai implementasi Release 2 dari paket ini** setelah (atau berdampingan terkontrol dengan) R1, mulai **R2-B1**.

Tidak diperlukan dokumen UX Discovery tambahan. Tidak ada artefak bisnis/governance yang diubah oleh milestone ini. R1 **tidak** di-rewrite.

---

## 8. Completion Criteria Traceability

Setiap item Release 2 diuji terhadap WF-PLAN-001 §5 (tujuh kriteria). Matriks di bawah adalah **klaim spesifikasi** paket ini (bukan status implementasi FE).

| WF ID | SCR | Zona/Priority | Reading Flow | One Primary Action | Tertelusur baseline | No destinasi baru | Continuity History | Dependencies rujukan |
|---|---|---|---|---|---|---|---|---|
| WF-001-06 | SCR-WS-03 | §3.1 Decision Cond. Visible intake | §3.1 | Route reopen | PWDM Routine intake; IA #13; NAV intake | Workspace only | N/A* | WF-001-04 |
| WF-001-09 | SCR-WS-06 | History Cond. Visible wajib | History sebelum Decision | Resubmit / Save correction | PWDM Interrupt reject; IA §8.9 | + History destinasi | **HX-01 wajib** | 08, 13 |
| WF-001-10 | SCR-WS-07 | History wajib | History → Work → Action | Continue / Submit CTA | PWDM Interrupt reopen; IA §8.9 | + History | **HX-01 wajib** | 07, 13 |
| WF-001-11 | SCR-WS-08 | Decision Cond. + history/progres | Context → package → Action | Provide context | PWDM Interrupt eskalasi konteks; IA #12 | Workspace | History/progres sama wireframe | 07, 16 |
| WF-001-12 | SCR-SV-01 | Evidence Cond.; Related Reference | Supporting host | Close / attach (bukan decision case) | NAV Secondary; IA #7 #21 | Supporting Views | Pelengkap, bukan pengganti HX | 07 |
| WF-001-13 | SCR-HX-01 | History | History band | Tidak ada primary decision | IA #9; PWDM Continuity | History | Menyediakan Continuity | 07 |
| WF-001-16 | SCR-WS-11 | Decision Always Vis. Supervisor | History → Decision | Handle **atau** Forward | PWDM Interrupt eskalasi; IA #12 | + History | **HX-02 wajib** | 03 |
| WF-001-17 | SCR-WS-12 | Decision + History | History → Request → Decision | Approve **atau** Reject reopen | PWDM Interrupt reopen; IA #13 | + History | **HX-02 wajib** | 03, 06, 18 |
| WF-001-18 | SCR-HX-02 | History | History band | Tidak ada primary decision | IA #9 #12; NAV Supervisor | History | Menyediakan Continuity | 03 |
| WF-001-21 | SCR-SV-02 | Reference Contextual | On-demand Supporting | Close / lookup | IA #20; NAV intake Secondary | Supporting Views | N/A (bukan reject path) | 04 |

\*WF-001-06 bukan layar Decision yang “membuka kembali” case di zona Decision penanganan; Continuity closure penuh ditegakkan di WF-001-17 + WF-001-18 (WF-PLAN §5 poin 6 mendaftar 09, 10, 11, 16, 17).

**Rilis 2 selesai (spesifikasi)** bila seluruh baris di atas terwakili di §2–§3 dan tidak ada item P1 WF-PLAN yang hilang — **terpenuhi oleh dokumen ini**.

---

## Related

- `docs/ux/WF-PLAN-001-Wireframe-Roadmap-Backlog.md` — §3 P1 · §4 Release 2
- `docs/ux/WF-001-R1-Wireframe-Package.md` — baseline R1 (tidak diubah)
- `docs/ux/WF-000-Wireframe-Constitution-Layout-System.md`
- `docs/ux/WF-001-01-Global-Shell-Header.md`
- `docs/ux/NAV-001-Navigation-Architecture.md`
- `docs/ux/UX-DISC-001-Complete-UX-Discovery.md` — §6 inventory · §8.2 cabang · §11 Batch R2
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/PDS-001-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`

## Future Work

- WF-001 Release 3 (Manager P2: WF-001-19, 20) — wireframe package berikutnya  
- SCR-SET-01 hygiene (di luar WF-PLAN R2) — bila dijadwalkan terpisah  
- UI-001 High Fidelity / prototype clickable — setelah LF R1+R2 stabil  
- Implementasi frontend R2 batches — **bukan** bagian dokumen ini  
