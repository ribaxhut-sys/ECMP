# WF-001-R1 — Wireframe Package Release 1 (Implementation-Oriented)

| Field | Value |
|---|---|
| Document ID | WF-001-R1 |
| Title | WF-001 Release 1 — Wireframe Package |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | **Draft — Wireframe R1 Complete (siap Review; belum Approved)** |
| Milestone | WF-001 Release 1 — Inti Operasional (P0) |
| Parent | WF-PLAN-001 · WF-000 |
| Applicability | Mode A · Complaint Management Module only |
| Subordination | BC/BW (locked) → UX-DISC-001 → PDS-001 · PWDM-001 · IA-001 · NAV-001 → WF-000 → WF-PLAN-001 → **WF-001-R1** (+ WF-001-01) |
| Does not | Discovery ulang · ubah BC/BW/governance · gambar hi-fi · tema visual · kode React/CSS · API · DB · Mode B |

## Cara baca

Paket ini adalah **spesifikasi wireframe fungsional** agar frontend dapat mengimplementasikan Release 1 tanpa dokumen discovery tambahan.

| Deliverable | Lokasi |
|---|---|
| 1. Wireframe Index | §1 |
| 2. Screen definitions | §2 |
| 3. Low Fidelity layout specs | §3 |
| 4. Navigation Map | §4 |
| 5. Component Inventory | §5 |
| 6. Frontend Implementation Batches | §6 |
| 7. Frontend Readiness Checklist | §7 |

**Reuse (jangan duplikasi):**

| Artefak | Peran |
|---|---|
| WF-PLAN-001 §4 Release 1 | Daftar item P0 yang mengikat |
| WF-000 | Konstitusi layout / zona / responsif |
| WF-001-01 | Shell & kontrak template A–D (rujuk, tidak disalin) |
| NAV-001 | Jalur navigasi |
| UX-DISC-001 §6 | SCR-ID |
| PDS-001 / PWDM-001 / IA-001 / BW-000 | Persona, keputusan, zona, tahap workflow |

**Catatan status baseline:** UX-DISC-001 dan baseline UX terkait berstatus Draft menunggu Review/Approval. Paket ini **tidak** mengubah governance; FE boleh mulai dari spesifikasi ini dengan asumsi Draft-as-working-baseline sampai Approval.

**Login Mode A:** SCR-AUTH-01 bukan item WF-PLAN R1, tetapi prasyarat sesi. Dicakup ringkas di §2.0 / §3.0 agar vertical slice berjalan.

---

## 1. Wireframe Index — Release 1

Item resmi WF-PLAN-001 Release 1: **WF-001-01, 02, 03, 04, 05, 07, 08, 14, 15**.

| # | WF ID | SCR ID | Screen Name | Primary Persona | Destinasi NAV |
|---|---|---|---|---|---|
| 0 | *(prasyarat)* | SCR-AUTH-01 | Login (Mode A) | Semua | — (pra-destinasi) |
| 1 | WF-001-01 | SCR-SHELL-01 | Global Shell & Header | Semua | Frame (bukan destinasi) |
| 2 | WF-001-02 | SCR-Q-01 | Queue — Assigned List | Complaint Officer (penanganan) | Queue |
| 3 | WF-001-03 | SCR-Q-02 | Queue — Supervisor Priority | Supervisor | Queue |
| 4 | WF-001-04 | SCR-WS-01 | Workspace — New Intake | Complaint Officer (intake) | Complaint Workspace |
| 5 | WF-001-05 | SCR-WS-02 | Workspace — Follow-up | Complaint Officer (intake) | Complaint Workspace |
| 6 | WF-001-07 | SCR-WS-04 | Workspace — Active Handling | Complaint Officer (penanganan) | Complaint Workspace |
| 7 | WF-001-08 | SCR-WS-05 | Workspace — Submit for Review | Complaint Officer (penanganan) | Complaint Workspace |
| 8 | WF-001-14 | SCR-WS-09 | Workspace — Assignment | Supervisor | Complaint Workspace |
| 9 | WF-001-15 | SCR-WS-10 | Workspace — Approval Review | Supervisor | Complaint Workspace |

**Di luar R1 (jangan diimplementasi sebagai bagian paket ini):** reopen, reject-resubmit, eskalasi, History wajib, Supporting Evidence/Related/Interaction History formal, Manager Dashboard (R2/R3).

**Return to Queue:** bukan layar — return path ke SCR-Q-01 atau SCR-Q-02 (NAV-001).

---

## 2. Screen Definitions

### 2.0 SCR-AUTH-01 — Login (prasyarat sesi)

| Field | Content |
|---|---|
| Screen ID | SCR-AUTH-01 |
| WF ID | — (bukan item WF-PLAN; prasyarat Mode A) |
| Purpose | Autentikasi credential Mode A; serah terima ke Entry Point persona |
| Primary Persona | Semua (akun) |
| Entry Points | URL modul; redirect unauthenticated |
| Exit Points | Sukses → SCR-SHELL-01 + Entry Point NAV-001; gagal → tetap di login |
| Main Components | Credential form; error banner |
| Main Actions | Sign in |
| Business Rules References | BC Mode A delivery; credential routes Mode A (bukan redesign identity) |
| Workflow References | PWDM-001 tahap `Login` |

### 2.1 WF-001-01 / SCR-SHELL-01 — Global Shell & Header

| Field | Content |
|---|---|
| Screen ID | SCR-SHELL-01 |
| Purpose | Frame persisten tingkat modul sepanjang sesi |
| Primary Persona | Semua |
| Entry Points | Setelah Login sukses |
| Exit Points | Logout saja |
| Main Components | Module identity; persona-mode awareness; global nav ke destinasi yang diizinkan; logout |
| Main Actions | Navigasi global; Logout |
| Business Rules References | BC-8.1 persona closed set; PDS-001 §7 Work Mode Not Account |
| Workflow References | PWDM-001 `Login` … `Logout` |
| Spec detail | **`docs/ux/WF-001-01-Global-Shell-Header.md`** (otoritatif untuk shell) |

### 2.2 WF-001-02 / SCR-Q-01 — Queue — Assigned List

| Field | Content |
|---|---|
| Screen ID | SCR-Q-01 |
| Purpose | Menampilkan case **assigned ke Officer aktif**, diurut sisa SLA; Entry Point mode penanganan |
| Primary Persona | Complaint Officer (mode penanganan) |
| Entry Points | Login mode penanganan; Return to Queue setelah keputusan kritis |
| Exit Points | Pilih baris → SCR-WS-04 (atau SCR-WS-05 jika sudah di jalur submit); Logout via shell |
| Main Components | Case table/list; SLA remaining indicator; status badge; paginator |
| Main Actions | Open case; (opsional) refresh list |
| Business Rules References | BC-8.2 Complaint Officer; PDS-001 §4 Immediate mode penanganan (Assignment, SLA) |
| Workflow References | PWDM-001 Officer Routine work (penanganan); BW-000 WS-03/WS-04 handling path; state `ASSIGNED` / `IN_PROGRESS` / `PENDING_REVIEW` milik assignee |

### 2.3 WF-001-03 / SCR-Q-02 — Queue — Supervisor Priority

| Field | Content |
|---|---|
| Screen ID | SCR-Q-02 |
| Purpose | Antrian keputusan Supervisor dengan **prioritas tetap tunggal:** eskalasi baru → SLA mendekati/lewat → unassigned |
| Primary Persona | Supervisor |
| Entry Points | Login Supervisor; Return to Queue |
| Exit Points | Pilih item → SCR-WS-09 (unassigned) atau SCR-WS-10 (pending approval); item eskalasi → R2 (SCR-WS-11) — **di R1 tampilkan di queue tetapi aksi eskalasi boleh PARTIAL** |
| Main Components | Priority sections atau sorted list; SLA badge; workload hint (contextual); paginator |
| Main Actions | Open item for decision |
| Business Rules References | BC-8.3 Supervisor; PDS-001 §4 Immediate Supervisor |
| Workflow References | PWDM-001 Supervisor Login/Routine; BW-000 WS-02 Assignment; approval pada `PENDING_REVIEW` |

### 2.4 WF-001-04 / SCR-WS-01 — Workspace — New Intake

| Field | Content |
|---|---|
| Screen ID | SCR-WS-01 |
| Purpose | Mencatat complaint/inquiry baru saat tidak ada case terkait aktif/closed |
| Primary Persona | Complaint Officer (mode intake) |
| Entry Points | Login intake; kontak baru tanpa case terkait; shell → Workspace |
| Exit Points | Setelah terima/teruskan → tetap Workspace siap kontak berikutnya (bukan Queue); Logout |
| Main Components | Customer reference block; intake form; completeness checklist; primary action |
| Main Actions | Save/forward when complete; Hold to complete (keputusan kritis intake) |
| Business Rules References | BC-8.2; ECMP bukan Customer Master SoR (referensi saja); BC write-audit on create |
| Workflow References | PWDM-001 Routine intake (case baru); BW-000 WS-01 / EP-01; state → `REGISTERED` |

### 2.5 WF-001-05 / SCR-WS-02 — Workspace — Follow-up

| Field | Content |
|---|---|
| Screen ID | SCR-WS-02 |
| Purpose | Menjawab follow-up pelanggan pada **case aktif** tanpa menanya ulang konteks |
| Primary Persona | Complaint Officer (mode intake) |
| Entry Points | Kontak + case aktif ditemukan (dari SCR-WS-01 lookup / konteks pelanggan) |
| Exit Points | Setelah update/jawab → tetap Workspace siap kontak berikutnya |
| Main Components | Case identity + status; customer context; note/update area; read-only summary |
| Main Actions | Record follow-up note / update; (tidak create case duplikat) |
| Business Rules References | BC-8.2; PDS-001 JTBD follow-up |
| Workflow References | PWDM-001 Routine intake (follow-up); case tetap pada status lifecycle berjalan |

### 2.6 WF-001-07 / SCR-WS-04 — Workspace — Active Handling

| Field | Content |
|---|---|
| Screen ID | SCR-WS-04 |
| Purpose | Memulai/melanjutkan penanganan case assigned; kesadaran SLA; aksi yang boleh sekarang |
| Primary Persona | Complaint Officer (mode penanganan) |
| Entry Points | SCR-Q-01 pilih case |
| Exit Points | Lanjut proses tercatat → Return to Queue; siap submit → SCR-WS-05; Logout |
| Main Components | Context header (case/customer/assignment); SLA; current work panel; primary action |
| Main Actions | Start handling (`ASSIGNED`→`IN_PROGRESS` bila applicable); record progress; navigate to Submit when ready |
| Business Rules References | BC-8.2; PDS-001 §5 `IN_PROGRESS` R/A |
| Workflow References | PWDM-001 Routine penanganan + Critical decisions; BW-000 WS-04 |

### 2.7 WF-001-08 / SCR-WS-05 — Workspace — Submit for Review

| Field | Content |
|---|---|
| Screen ID | SCR-WS-05 |
| Purpose | Mengajukan hasil penanganan beserta bukti yang relevan untuk review Supervisor |
| Primary Persona | Complaint Officer (mode penanganan) |
| Entry Points | Dari SCR-WS-04 saat penanganan siap diajukan |
| Exit Points | Submit sukses → Return to Queue (`PENDING_REVIEW`); batal → kembali SCR-WS-04 |
| Main Components | Resolution summary; evidence list (R1: attachment list minimal); confirm submit |
| Main Actions | Submit for review (satu primary action); Cancel |
| Business Rules References | BC closure path via review; evidence bila tipe COMPLAINT sesuai aturan bisnis terkunci |
| Workflow References | PWDM-001 Critical decision ajukan review; BW-000 resolve/review → `PENDING_REVIEW` |

**Catatan R1:** Supporting Views Evidence formal = R2 (WF-001-12). R1 memakai **daftar lampiran minimal di zona Evidence Conditionally Visible** di dalam workspace yang sama — bukan destinasi Supporting Views terpisah.

### 2.8 WF-001-14 / SCR-WS-09 — Workspace — Assignment

| Field | Content |
|---|---|
| Screen ID | SCR-WS-09 |
| Purpose | Assign case unassigned ke Complaint Officer/unit berdasarkan kapasitas |
| Primary Persona | Supervisor |
| Entry Points | SCR-Q-02 item unassigned / REGISTERED menunggu assign |
| Exit Points | Assign sukses → Return to Queue; batal → Queue |
| Main Components | Case context; assignee/unit selector; workload/capacity hint; primary Assign |
| Main Actions | Assign (satu primary action) |
| Business Rules References | BC-8.3; PDS-001 §5 `ASSIGNED` Supervisor R/A |
| Workflow References | PWDM-001 Supervisor Routine assign; BW-000 WS-02 → `ASSIGNED` |

### 2.9 WF-001-15 / SCR-WS-10 — Workspace — Approval Review

| Field | Content |
|---|---|
| Screen ID | SCR-WS-10 |
| Purpose | Menilai pengajuan hasil Officer; **Approve & Close** atau **Reject** (satu keputusan pada satu waktu) |
| Primary Persona | Supervisor |
| Entry Points | SCR-Q-02 item `PENDING_REVIEW` |
| Exit Points | Approve → `CLOSED` → Return to Queue; Reject → `IN_PROGRESS` → Return to Queue |
| Main Components | Case context; resolution + evidence summary; Approve form; Reject reason |
| Main Actions | Approve & Close **atau** Reject (mutual exclusive primary) |
| Business Rules References | BC-5.5 / BC closure; Supervisor A pada `CLOSED`; reject kembali ke penanganan |
| Workflow References | PWDM-001 Critical decision approve/reject; BW-000 WS-07 closure path |

**Catatan R1:** Setelah Reject, Officer memakai jalur R2 (SCR-WS-06 + History). Di R1, Reject **mengubah status** dan mengembalikan ke queue Officer; UI resubmit continuity penuh = R2.

---

## 3. Low Fidelity Wireframe Specification

Konvensi: deskripsi **layout fungsional** saja. Pemetaan ke region WF-000 dicantumkan. Jawaban `Tidak ada` wajib beralasan (kontrak WF-001-01 §A.2).

Kosakata prompt → region WF-000:

| Prompt region | Biasanya memetakan ke |
|---|---|
| Header | Header (shell) |
| Toolbar | Chrome di Header atau Entry Area |
| Filter Area / Search | Entry Area (Queue) atau Context lookup (Intake) |
| Main Content | Entry Area list **atau** Primary Workspace |
| Side Panel | Context strip / Supporting Workspace (minimal R1) |
| Timeline Area | History Area — **umumnya Tidak ada di R1** (R2) |
| Action Buttons | Zona Decision di Primary Workspace |
| Dialogs | Overlay keputusan / konfirmasi |
| Notifications | Feedback sesi (bukan Global Notification Enterprise) |

---

### 3.0 SCR-AUTH-01 — Login

| Region | Spec |
|---|---|
| Header | Identitas modul saja (pra-shell penuh) |
| Toolbar | Tidak ada |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | Form credential (identifier + secret); CTA Sign in |
| Side Panel | Tidak ada |
| Timeline Area | Tidak ada |
| Action Buttons | Sign in (primary) |
| Dialogs | Tidak ada |
| Notifications | Inline error auth gagal |
| Empty State | Tidak ada |
| Loading State | Disable form + indikator saat submit |
| Error State | Pesan gagal auth; tetap di layar |
| Permission Visibility | Layar publik Mode A |
| Responsive Behaviour | Form tunggal full-width pada mobile (WF-000 §7: satu zona perhatian) |

### 3.1 SCR-SHELL-01 — Global Shell

Spesifikasi struktural lengkap: **WF-001-01**. Ringkas LF untuk implementasi:

| Region | Spec |
|---|---|
| Header | Selalu: module label; indikator persona/mode aktif; kontrol Logout |
| Toolbar | Nav global terbatas ke destinasi diizinkan: Queue (bila Entry Area hadir), Workspace (intake), **tanpa** Dashboard Manager di R1 |
| Filter / Search / Main / Side / Timeline | Tidak ada di shell — milik child destination |
| Action Buttons | Logout |
| Dialogs | Konfirmasi logout (opsional) |
| Notifications | Slot feedback modul-scoped (toast/banner) — bukan case timeline |
| Empty / Loading / Error | Tidak ada (shell); error navigasi → child |
| Permission Visibility | Item nav hanya jika persona mode + permission mengizinkan destinasi (NAV-001 prinsip 8) |
| Responsive Behaviour | Header persist; nav boleh collapse menjadi menu satu langkah di mobile |

### 3.2 SCR-Q-01 — Queue Assigned

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Judul “Assigned queue”; kontrol refresh |
| Filter Area | Filter status terbatas milik assignee (`ASSIGNED`, `IN_PROGRESS`, `PENDING_REVIEW`); **bukan** backlog lintas unit |
| Search | Cari case_id / subject dalam populasi assigned (bukan Search workspace baru) |
| Main Content | Tabel/list: case_id, subject, status, priority, **SLA remaining** (sort default); klik baris = open |
| Side Panel | Tidak ada (R1) |
| Timeline Area | Tidak ada |
| Action Buttons | Tidak ada primary decision di queue — aksi = open row |
| Dialogs | Tidak ada |
| Notifications | Banner bila list gagal dimuat |
| Empty State | “Tidak ada case assigned” + arahan menunggu assignment |
| Loading State | Skeleton/list placeholder |
| Error State | Retry load |
| Permission Visibility | Hanya Officer mode penanganan (+ permission read assigned) |
| Responsive Behaviour | Tablet: filter collapse; Mobile: satu list full-width, sort SLA tetap |

**Region WF-000:** Entry Area (Current Work / Queue).

### 3.3 SCR-Q-02 — Queue Supervisor Priority

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Judul “Supervisor queue”; refresh |
| Filter Area | **Tidak mengganti urutan prioritas tetap.** Filter sekunder opsional di dalam segmen (mis. unit) tanpa menaikkan unassigned di atas eskalasi/SLA |
| Search | Cari dalam populasi queue Supervisor |
| Main Content | Tiga segmen berurutan **wajib**: (1) Escalation baru (2) SLA at-risk/overdue (3) Unassigned. Item menampilkan identitas case, alasan segmen, SLA |
| Side Panel | Workload/capacity ringkas (Contextual) — boleh collapsed default |
| Timeline Area | Tidak ada |
| Action Buttons | Open item |
| Dialogs | Tidak ada |
| Notifications | Highlight count eskalasi baru |
| Empty State | Per segmen: “Tidak ada item” |
| Loading State | Skeleton per segmen |
| Error State | Retry; jangan kosongkan prioritas |
| Permission Visibility | Supervisor (+ assign/approve permissions untuk aksi di workspace tujuan) |
| Responsive Behaviour | Segmen ditumpuk vertikal; mobile satu segmen per view dengan next-segmen nav |

**Region WF-000:** Entry Area.

### 3.4 SCR-WS-01 — New Intake

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Judul “New intake”; indikator mode intake |
| Filter Area | Tidak ada |
| Search | Lookup referensi pelanggan (bukan SoR tulis-master); hasil menampilkan identitas cache/referensi |
| Main Content | **Top/Context:** pelanggan + kelengkapan. **Middle:** form subject/description/category/channel/priority. **Lower/Evidence:** checklist field wajib vs terisi (Data Completeness) |
| Side Panel | Checklist kelengkapan (boleh berdampingan desktop) |
| Timeline Area | Tidak ada (R1) |
| Action Buttons | Primary: **Forward / Register when complete** · Secondary: **Hold to complete** (satu keputusan kritis aktif — tidak keduanya setara bersamaan; Hold menonaktifkan Forward) |
| Dialogs | Konfirmasi register bila perlu |
| Notifications | Validasi field kurang |
| Empty State | Form kosong siap isi setelah pelanggan dipilih/diisi |
| Loading State | Saat simpan |
| Error State | Gagal simpan; pertahankan input |
| Permission Visibility | `cases:create` (atau padanan Mode A); sembunyikan Assign/Close |
| Responsive Behaviour | Desktop: form + checklist berdampingan; Mobile: Context → Form → Completeness → Action berurutan (WF-000 reading flow) |

**Region WF-000:** Primary Workspace (Context + Current Work + Decision Conditionally Visible).

### 3.5 SCR-WS-02 — Follow-up

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Judul “Follow-up”; link identitas case aktif |
| Filter Area | Tidak ada |
| Search | Tidak ada (konteks case sudah terpilih) |
| Main Content | Context: customer + case identity + status. Current Work: ringkasan case + area catatan follow-up |
| Side Panel | Read-only case summary |
| Timeline Area | Tidak ada sebagai destinasi History (R2); ringkasan status terakhir boleh di Context |
| Action Buttons | Primary: **Save follow-up**; dilarang “Create new case” sebagai primary |
| Dialogs | Tidak ada / konfirmasi simpan opsional |
| Notifications | Sukses simpan |
| Empty State | Tidak applicable bila entry mensyaratkan case aktif |
| Loading State | Load case context; save in progress |
| Error State | Case tidak ditemukan / bukan aktif → arahkan ke New Intake atau Reopen Routing (R2) |
| Permission Visibility | Officer intake + read case |
| Responsive Behaviour | Summary di atas form catatan pada mobile |

### 3.6 SCR-WS-04 — Active Handling

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Back/Return to Queue; case_id; status; priority |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | **Context:** customer ref, case identity, assignment. **Current Work:** SLA remaining, allowed actions now, progress notes |
| Side Panel | SLA + assignment summary (desktop) |
| Timeline Area | Tidak ada (R1) — placeholder terlarang sebagai fitur palsu; kosong lebih baik daripada data fiktif |
| Action Buttons | Primary dinamis satu: **Start handling** (jika `ASSIGNED`) **atau** **Continue / Record progress** (jika `IN_PROGRESS`) **atau** CTA ke **Submit for review** (kesiapan) — tidak bersamaan dua primary |
| Dialogs | Konfirmasi start handling |
| Notifications | Peringatan SLA mendekati batas |
| Empty State | Tidak ada (masuk dari queue dengan case) |
| Loading State | Load case |
| Error State | 409 state conflict → refetch; permission denied |
| Permission Visibility | Hanya aksi yang diizinkan Authorization + state machine; Officer bukan default Assign/Close |
| Responsive Behaviour | Context → Current Work → Action; side panel jadi section di bawah pada tablet/mobile |

### 3.7 SCR-WS-05 — Submit for Review

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Case identity; status `IN_PROGRESS` |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | Context ringkas; Resolution input; Evidence list minimal (nama file / status terlampir) |
| Side Panel | Checklist “bukti cukup?” (Conditionally Visible) |
| Timeline Area | Tidak ada |
| Action Buttons | Primary: **Submit for review**; Secondary: **Cancel** (kembali handling) |
| Dialogs | Confirm submit |
| Notifications | Validasi resolution/evidence kurang |
| Empty State | Evidence list kosong + peringatan bila wajib |
| Loading State | Submit in flight |
| Error State | Gagal transisi; tetap di layar |
| Permission Visibility | Assignee / permission status transition ke `PENDING_REVIEW` |
| Responsive Behaviour | Form linear; confirm dialog full-screen mobile |

### 3.8 SCR-WS-09 — Assignment

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Return to Queue; case_id; status `REGISTERED` (atau setara menunggu assign) |
| Filter Area | Tidak ada pada workspace; filter ada di queue asal |
| Search | Cari assignee dalam unit (scoped) |
| Main Content | Context case; Assignment panel: unit + officer; workload hint |
| Side Panel | Workload/capacity list (Supporting) |
| Timeline Area | Tidak ada |
| Action Buttons | Primary: **Assign**; Cancel → Queue |
| Dialogs | Confirm assign |
| Notifications | Konflik sudah di-assign orang lain → refetch |
| Empty State | Tidak ada candidate assignee → pesan kapasitas |
| Loading State | Load case + candidates |
| Error State | 403/409 dengan pesan |
| Permission Visibility | `cases:assign` (atau padanan); sembunyikan bila bukan Supervisor path |
| Responsive Behaviour | Capacity list di bawah selector pada mobile |

### 3.9 SCR-WS-10 — Approval Review

| Region | Spec |
|---|---|
| Header | Via shell |
| Toolbar | Return to Queue; case_id; `PENDING_REVIEW` |
| Filter Area | Tidak ada |
| Search | Tidak ada |
| Main Content | Context; Resolution + evidence summary (read); Decision area |
| Side Panel | Evidence summary |
| Timeline Area | Tidak ada wajib R1; ringkasan “diajukan oleh / waktu” di Context cukup |
| Action Buttons | **Tepat satu primary decision mode:** mode Approve (resolutionCode wajib bila aturan bilang demikian) **atau** mode Reject (reason). UI boleh punya dua kontrol tetapi menegakkan One Primary Action — tidak submit keduanya |
| Dialogs | Confirm Approve & Close; Confirm Reject |
| Notifications | Validasi field approve/reject |
| Empty State | Tidak ada |
| Loading State | Load submission; action in flight |
| Error State | State conflict → refetch |
| Permission Visibility | Supervisor review permissions; Officer melihat read-only bila tersesat ke URL |
| Responsive Behaviour | Decision controls sticky bottom pada mobile |

---

## 4. Navigation Map — Release 1

```
SCR-AUTH-01 Login
        │
        ▼
SCR-SHELL-01 Shell (persist)
        │
        ├── Officer INTAKE ──────────────────────────────┐
        │         ▼                                      │
        │   SCR-WS-01 New Intake ◄──► SCR-WS-02 Follow-up│
        │         │  (tetap Workspace; bukan Queue)      │
        │         └──────────────────────────────────────┘
        │
        ├── Officer HANDLING ────────────────────────────┐
        │         ▼                                      │
        │   SCR-Q-01 Assigned Queue                      │
        │         │ open                                 │
        │         ▼                                      │
        │   SCR-WS-04 Active Handling                    │
        │         │ ready                                │
        │         ▼                                      │
        │   SCR-WS-05 Submit for Review                  │
        │         │ success                              │
        │         ▼                                      │
        │   Return to Queue → SCR-Q-01                   │
        │                                                │
        └── Supervisor ──────────────────────────────────┤
                  ▼                                      │
            SCR-Q-02 Priority Queue                      │
                  │                                      │
          ┌───────┴────────┐                             │
          ▼                ▼                             │
   SCR-WS-09 Assign   SCR-WS-10 Approval                 │
          │                │                             │
          └────────┬───────┘                             │
                   ▼                                     │
          Return to Queue → SCR-Q-02                     │
                                                         │
Happy path lintas persona (logis, bukan satu sesi):      │
  WS-01 REGISTERED → Q-02 → WS-09 ASSIGNED               │
    → Q-01 → WS-04 IN_PROGRESS → WS-05 PENDING_REVIEW    │
    → Q-02 → WS-10 CLOSED                                │
                                                         │
Logout ← selalu dari Shell                               │
```

**Aturan:** Supporting Views / History formal **tidak** ada di peta R1. Escalation/Reopen nodes **tidak** digambar sebagai target implementasi R1.

---

## 5. Component Inventory (Reusable)

Hanya komponen yang dibutuhkan R1. Bukan design system expansion.

| Component ID | Name | Dipakai di | Catatan |
|---|---|---|---|
| C-SHELL | App Shell Header | Semua | WF-001-01 |
| C-NAV | Global Nav (destinasi terbatas) | Shell | Persona-aware |
| C-TABLE | Complaint/Case Table | Q-01, Q-02 | Sort + row open |
| C-SEG | Priority Segment Stack | Q-02 | Urutan tetap 3 segmen |
| C-BADGE-STATUS | Status Badge | Queue, Workspace | State machine labels |
| C-BADGE-SLA | SLA Remaining / Risk | Q-01, Q-02, WS-04 | Immediate Officer/Supervisor |
| C-BADGE-PRIO | Priority Badge | Queue, Workspace | LOW…CRITICAL |
| C-FILTER | Queue Filter Bar | Q-01, Q-02 | Tidak boleh melanggar prioritas Supervisor |
| C-SEARCH | Scoped Search | Q-01, Q-02, WS-01, WS-09 | Bukan destinasi Search |
| C-PAGE | Paginator | Q-01, Q-02 | |
| C-CASE-HDR | Case Context Header | Semua WS-* | Identity + status + priority |
| C-CUST | Customer Reference Block | WS-01, 02, 04 | Read/cache; bukan master write |
| C-FORM-INTAKE | Intake Form | WS-01 | |
| C-COMPLETE | Completeness Checklist | WS-01 | Data Completeness Status |
| C-NOTE | Follow-up / Progress Note | WS-02, WS-04 | |
| C-ASSIGN | Assignment Card/Panel | WS-09 | Unit + assignee |
| C-WORKLOAD | Workload Hint List | WS-09, (Q-02 side) | Capacity |
| C-RESOLVE | Resolution Panel | WS-05, WS-10 | |
| C-EVID-MIN | Evidence List (minimal) | WS-05, WS-10 | Bukan full Supporting Views R2 |
| C-APPROVE | Approval Panel | WS-10 | Approve mode |
| C-REJECT | Reject Panel | WS-10 | Reject mode; mutual exclusive dgn Approve |
| C-ACT | Primary Action Bar | Semua WS-* | One Primary Action |
| C-DIALOG | Confirm Dialog | Auth optional, WS-* | |
| C-TOAST | Module Notification | Shell slot | Modul-scoped |
| C-EMPTY | Empty State Block | Queue, lists | |
| C-LOAD | Loading Placeholder | Semua | |
| C-ERR | Error / Retry Block | Semua | |
| C-PERM | Permission Gate | Semua | Hide/disable by authz |

**Tidak di R1:** Timeline Panel penuh, Comment Panel generik, Related Cases panel, Interaction History panel, Manager KPI cards, Escalation panel.

---

## 6. Frontend Implementation Batches

Vertical slices terkecil yang demonstrable.

| Batch | Nama | Screens | Definisi “Done” slice |
|---|---|---|---|
| **B0** | Session | SCR-AUTH-01, SCR-SHELL-01 | Login → shell → logout; nav persona-aware |
| **B1** | Supervisor Assign loop | SCR-Q-02 (segmen unassigned saja dulu), SCR-WS-09 | REGISTERED → ASSIGNED → kembali queue |
| **B2** | Officer Queue + Handle | SCR-Q-01, SCR-WS-04 | Lihat assigned → start/continue handling |
| **B3** | Intake | SCR-WS-01, SCR-WS-02 | Catat baru + follow-up tanpa Queue |
| **B4** | Submit | SCR-WS-05 | IN_PROGRESS → PENDING_REVIEW → Return Q-01 |
| **B5** | Approval close | SCR-Q-02 (segmen pending), SCR-WS-10 | PENDING_REVIEW → CLOSED (dan Reject status-only) |
| **B6** | Queue Supervisor full priority | Lengkapi SCR-Q-02 segmen SLA + eskalasi **tampil** | Urutan eskalasi→SLA→unassigned tegak; aksi eskalasi boleh stub ke R2 |

**Urutan rekomendasi:** B0 → B3 (intake mandiri) **paralel** B1 → B2 → B4 → B5 → B6.

**Slice demo end-to-end minimal:** B0+B3+B1+B2+B4+B5 (tanpa B6 eskalasi).

Jangan campur rute legacy `/complaints/*` vs `/complaints/cm/*` dalam satu slice tanpa keputusan coexistence (DEC-020) — pilih **satu permukaan** per batch R1 untuk Complaint Workspace.

---

## 7. Frontend Readiness Checklist

| Screen | Status | Alasan |
|---|---|---|
| SCR-AUTH-01 Login | **READY** | Mode A credential sudah ada di FE lab; wireframe cukup |
| SCR-SHELL-01 Shell | **READY** | WF-001-01 + §3.1; batasi nav ke destinasi R1 |
| SCR-Q-01 Assigned Queue | **READY** | Spec lengkap; sort SLA jelas |
| SCR-Q-02 Supervisor Queue | **PARTIAL** | Unassigned + pending approval READY; segmen eskalasi **tampil** READY untuk list, **aksi eskalasi BLOCKED→R2**; pastikan urutan prioritas diimplementasi |
| SCR-WS-01 New Intake | **READY** | Spec lengkap; Customer Master write tetap terlarang |
| SCR-WS-02 Follow-up | **READY** | Bergantung kemampuan temukan case aktif pelanggan (boleh PARTIAL teknis bila lookup tipis — UX wireframe READY) |
| SCR-WS-04 Active Handling | **READY** | Satu primary action per state; no fake timeline |
| SCR-WS-05 Submit for Review | **PARTIAL** | Submit READY; evidence “penuh” Supporting Views = R2 — R1 pakai C-EVID-MIN |
| SCR-WS-09 Assignment | **READY** | Spec lengkap |
| SCR-WS-10 Approval Review | **PARTIAL** | Approve/Reject READY; post-reject Officer continuity UI = R2; History wajib = R2 |

### Blockers lintas-layar (bukan discovery)

| ID | Item | Dampak R1 |
|---|---|---|
| R1-B1 | Paket UX masih Draft (belum Approved) | Implementasi lab OK; “production design sign-off” menunggu Approval |
| R1-B2 | Rekonsiliasi UX-SCR-001 vs zona IA / Officer merge | Hindari dua layout case detail bertentangan — map ke SCR-WS-04/05/09/10 |
| R1-B3 | Evidence/History formal R2 | Jangan blokir B4/B5; pakai minimal list + tanpa timeline palsu |
| R1-B4 | Dual route legacy vs CM Aggregate | Pilih permukaan implementasi per batch (coexistence, no silent merge) |

### Verdict

**Frontend developer dapat memulai implementasi Release 1 dari paket ini** (mulai B0).

Tidak diperlukan dokumen UX Discovery tambahan. Tidak ada artefak bisnis/governance yang diubah oleh milestone ini.

---

## Related

- `docs/ux/WF-PLAN-001-Wireframe-Roadmap-Backlog.md`
- `docs/ux/WF-000-Wireframe-Constitution-Layout-System.md`
- `docs/ux/WF-001-01-Global-Shell-Header.md`
- `docs/ux/NAV-001-Navigation-Architecture.md`
- `docs/ux/UX-DISC-001-Complete-UX-Discovery.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/PDS-001-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`

## Future Work

- WF-001 Release 2 (P1 continuity) — wireframe package berikutnya  
- WF-001 Release 3 (Manager P2)  
- UI-001 High Fidelity / prototype clickable — setelah LF R1 stabil  
