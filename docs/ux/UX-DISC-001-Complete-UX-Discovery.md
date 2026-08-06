# UX-DISC-001 — Complete UX Discovery (Complaint Management Module)

| Field | Value |
|---|---|
| Document ID | UX-DISC-001 |
| Title | Complete UX Discovery — One-Pass Package |
| Milestone | UX-001 — Complete UX Discovery |
| Version | 1.0 |
| Date | 2026-08-05 |
| Status | **Draft — Discovery Complete (siap Review; belum Approved)** |
| Applicability | Mode A · Complaint Management Module only |
| Parent | UX-FOUNDATION-000 |
| Subordination | BC-000…BC-003 · BW-000 → UX-FOUNDATION-000 → **baseline** PDS-001 · PWDM-001 · IA-001 · NAV-001 · WF-000 · WF-PLAN-001 → **UX-DISC-001** → WF-001 (wireframe) |
| Does not | Mengubah BC/BW · redesign bisnis/workflow · menggambar wireframe · membuat prototype · menulis kode FE/BE · API · database · Mode B / Enterprise |

## Cara baca paket ini

Dokumen ini **menutup fase UX Discovery** dalam satu pass. Ia **tidak menduplikasi** baseline yang sudah ada; ia merangkum, menginventarisasi layar/workspace, merencanakan wireframe/prototype/implementasi, dan menyatakan kesiapan.

| # | Deliverable | Sumber otoritatif | Peran UX-DISC-001 |
|---|---|---|---|
| 1 | UX Discovery Summary | §1 di bawah | Ringkasan baru |
| 2 | User Personas | **PDS-001** | Review — model tetap |
| 3 | Business Journey | **PWDM-001** + §3 | Journey Customer + persona operasional |
| 4 | Information Architecture | **IA-001** | Finalisasi review |
| 5 | Navigation Structure | **NAV-001** + §5 | Empat lapisan navigasi |
| 6 | Screen Inventory | §6 | Inventori lengkap (baru) |
| 7 | Workspace Inventory | §7 | Inventori lengkap (baru) |
| 8 | Screen Flow | **NAV-001** §2 + §8 | Alur Login → Closure |
| 9 | Wireframe Planning | **WF-PLAN-001** | Rencana (tanpa gambar) |
| 10 | Prototype Planning | §10 | Rencana fidelity (baru) |
| 11 | Frontend Redesign Roadmap | §11 | Batch implementasi (baru) |
| 12 | UX Gap Analysis | §12 | Bandingkan FE vs model UX (baru) |
| 13 | Implementation Readiness | §13 | Gate kesiapan (baru) |

**Artefak yang dikunci bisnis (jangan diubah):** BC-000, BC-001, BC-002, BC-003, BW-000.

**Artefak UX baseline (reuse, bukan rebuild):** PDS-001, PWDM-001, IA-001, NAV-001, WF-000, WF-PLAN-001, UX-FOUNDATION-000.

---

## 1. UX Discovery Summary

### Module goals

Menyelesaikan **Complaint Management Module** sebagai modul bisnis Mode A: lifecycle komplain/case (intake → assign → handle → review → close, plus eskalasi/appointment/reopen dalam satu lifecycle) dengan pengalaman kerja yang stabil bagi persona operasional — tanpa mendesain ulang domain bisnis.

### User goals

| Aktor | Tujuan pengalaman |
|---|---|
| **Customer** *(pihak eksternal, bukan persona login)* | Keluhan tercatat akurat; follow-up tanpa mengulang cerita; hasil jelas setelah closure |
| **Complaint Officer** | Intake lengkap sekali jalan; case assigned bergerak maju dengan kesadaran SLA; submit review dengan bukti cukup |
| **Supervisor** | Distribusi adil; eskalasi/SLA/unassigned terlihat segera; approve/reject/reopen diputuskan tanpa menelusuri ulang |
| **Manager** | Gambaran agregat/KPI cukup untuk keputusan; tanpa menyentuh transaksi case *(workspace delivery MAY deferred — BC-8.4)* |

### Business goals

- Satu Complaint Lifecycle (BW-000); Escalation & Appointment di dalam lifecycle yang sama.
- Persona operasional closed set: Complaint Officer · Supervisor · Manager (BC-8.1).
- ECMP bukan Customer Master SoR — data pelanggan referensi/cache (BC).
- Write-audit & timeline untuk perubahan signifikan.
- Mode A: modul bisa dioperasikan tanpa menunggu integrasi Enterprise.

### UX goals

1. **Work before screen** — informasi & keputusan (PDS/PWDM/IA) mendahului layout.
2. **Satu Complaint Workspace** untuk Officer & Supervisor; zona & mode yang berbeda, bukan layar paralel per persona.
3. **Navigasi mengikuti tanggung jawab** (R/A/C/I), bukan kenyamanan.
4. **Progressive disclosure** mengikuti Information Priority Matrix.
5. **Kontinuitas** reject / reopen / eskalasi membawa History terkait.
6. **Tidak menambah destinasi** di luar closed set IA-001: Dashboard · Queue · Complaint Workspace · Supporting Views · History · Return to Queue.

---

## 2. User Personas — Review

| Keputusan | Hasil |
|---|---|
| Model yang disetujui | **PDS-001** — tiga persona operasional |
| Perubahan discovery ini | **Tidak ada** — model konsisten dengan BC-8.1 / BC-8.2 |
| Superseded | PDS-000 (historis); bagian “siapa & tujuan” di `12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md` digantikan PDS-001 untuk pertanyaan persona |

| Persona | Ringkas | Catatan |
|---|---|---|
| Complaint Officer | Intake + penanganan aktif (dua mode situasional) | Assign/close default Supervisor; kapabilitas kondisional via Authorization |
| Supervisor | Distribusi, approval, eskalasi unit, reopen gate | Entry Queue berprioritas tetap |
| Manager | Agregat / tren / KPI read-only | Persona valid; **Manager Workspace MAY deferred** (BC-8.4) |
| Administrator | Di luar closed set operasional | Konfigurasi — bukan fokus discovery operasional |
| Customer | Bukan persona sistem | Journey layanan §3.1 |

Detail JTBD, Information Priority, Responsibility → **PDS-001**.

---

## 3. Business Journey

Alur status mengikuti BW-000 / Case State Machine. UX tidak mengubah workflow.

### 3.1 Customer *(jalur layanan, bukan login ECMP)*

Customer tidak memiliki akun/workspace di modul. Interaksi melalui kanal kontak yang dilayani Complaint Officer (EP-01).

```
Butuh bantuan / keluhan
  → Kontak kanal (telepon/counter/dll.)
  → Dilayani Complaint Officer (intake)
       ├─ Case baru dicatat (REGISTERED)
       ├─ Follow-up pada case aktif → status dijelaskan tanpa tanya ulang
       └─ Case closed → permintaan reopen diteruskan ke Supervisor
  → Menunggu penanganan / update status (via Officer / notifikasi bisnis modul)
  → Hasil closure diinformasikan
  → (opsional) Reopen dalam jendela yang diizinkan aturan bisnis
```

**UX implication:** semua layar “customer-facing” di Mode A adalah **permukaan Officer** (Customer Information, Interaction History on-demand) — bukan portal pelanggan.

### 3.2 Complaint Officer

Sumber: PWDM-001 §1 + NAV-001.

**Mode intake:** Login → Complaint Workspace (new / follow-up / reopen routing) → Supporting Views (Interaction History) → siap kontak berikutnya → Logout.

**Mode penanganan:** Login → Queue (assigned, urut SLA) → Complaint Workspace → Supporting Views / History → keputusan (lanjut / submit review / handover konteks) → Return to Queue → … → Logout.

Lifecycle yang disentuh: `REGISTERED` (R) → informed pada `ASSIGNED` → `IN_PROGRESS` (R/A) → `PENDING_REVIEW` (R) → informed `CLOSED` / lanjut `REOPENED`.

### 3.3 Supervisor

Login → Queue (eskalasi → SLA → unassigned) → Complaint Workspace (assign / approve-reject / eskalasi / reopen) → History saat dibutuhkan → Return to Queue → Logout.

Lifecycle: R/A pada `ASSIGNED`, eskalasi, approval `PENDING_REVIEW`, `CLOSED`, `REOPENED`.

### 3.4 Manager

Login → Dashboard (agregat) → opsional Supporting Views (drill-down unit by exception) → Logout.

Tidak memasuki Complaint Workspace operasional. Tidak assign/close case.

---

## 4. Information Architecture — Finalisasi Review

| Aspek | Status | SoT |
|---|---|---|
| Information Inventory (21 objek) | Lengkap | IA-001 §1 |
| Ownership Matrix | Lengkap (pasca merge Officer) | IA-001 §2 |
| Hierarchy per persona | Lengkap | IA-001 §3 |
| Workspace Zones (6) | Closed set final | IA-001 §4 |
| Navigation destinations (6) | Closed set final | IA-001 §5 |
| Progressive disclosure | Lengkap | IA-001 §6–§8 |

**Keputusan discovery:** IA-001 **tidak diubah**. Tidak ada modul/navigasi/objek baru. Hierarki workspace & objek case dirangkum di §7.

---

## 5. Navigation Structure

Destinasi tetap closed set IA-001 / NAV-001. Di bawah ini empat **lapisan navigasi** untuk desain wireframe (tanpa menambah destinasi).

### 5.1 Global Navigation

Frame tingkat modul (selalu hadir sepanjang sesi setelah Login) — **WF-001-01 / WF-000 Header**.

| Elemen | Peran |
|---|---|
| Identitas modul / sesi | Orientasi “saya di Complaint Module” |
| Persona mode aktif | Menentukan region yang hadir (Work Mode, Not Account) |
| Akses destinasi tingkat modul | Dashboard *(Manager)* · Queue *(Officer handling / Supervisor)* · keluar ke Profile/Settings Mode A bila ada |
| Logout | Exit Point semua persona |

Tidak memuat aksi case-level.

### 5.2 Workspace Navigation

Perpindahan antar destinasi primer sesuai Entry Point persona (NAV-001 §1).

| Persona / mode | Destinasi primer |
|---|---|
| Officer — intake | Complaint Workspace |
| Officer — penanganan | Queue ↔ Complaint Workspace |
| Supervisor | Queue ↔ Complaint Workspace |
| Manager | Dashboard |

### 5.3 Context Navigation

Di dalam Complaint Workspace: perpindahan **zona** (Context · Current Work · Evidence · Decision · History · Reference) tanpa ganti destinasi. Secondary: Supporting Views & History dibuka dari Workspace (on-demand / wajib pada reject·reopen·eskalasi).

### 5.4 Action Navigation

Satu **Primary Action** per momen keputusan kritis (PWDM-001 §2 / WF-000). Contoh: Submit for Review · Approve/Reject · Assign · Escalate · Route Reopen. Return to Queue adalah **return path**, bukan layar baru.

Detail jalur → **NAV-001**.

---

## 6. Screen Inventory

Inventori layar untuk wireframe & implementasi. **SCR-ID** memetakan ke backlog **WF-001-NN** bila ada. Priority: P0 / P1 / P2 dari WF-PLAN-001 §3.

| Screen ID | Name | Purpose | Primary User | Entry Points | Main Actions | Dependencies | Priority |
|---|---|---|---|---|---|---|---|
| SCR-AUTH-01 | Login | Autentikasi Mode A credential | Semua persona operasional | URL modul / redirect unauth | Sign in | Config Mode A auth | P0 |
| SCR-SHELL-01 | Global Shell & Header | Frame persisten modul | Semua | Setelah Login | Nav global, logout, mode awareness | SCR-AUTH-01 | P0 |
| SCR-Q-01 | Queue — Assigned List | Daftar case assigned Officer | Complaint Officer (penanganan) | Login mode penanganan; Return to Queue | Buka case; urut SLA | SCR-SHELL-01 | P0 |
| SCR-Q-02 | Queue — Supervisor Priority | Eskalasi → SLA → unassigned | Supervisor | Login Supervisor; Return to Queue | Buka item keputusan | SCR-SHELL-01 | P0 |
| SCR-WS-01 | Workspace — New Intake | Catat case baru | Complaint Officer (intake) | Kontak baru tanpa case terkait | Simpan/teruskan; lengkapi data | SCR-SHELL-01 | P0 |
| SCR-WS-02 | Workspace — Follow-up | Jawab follow-up case aktif | Complaint Officer (intake) | Kontak + case aktif ditemukan | Update konteks; tanpa tanya ulang | SCR-WS-01 | P0 |
| SCR-WS-03 | Workspace — Reopen Routing | Teruskan permintaan reopen | Complaint Officer (intake) | Kontak + case closed terkait | Kirim reopen request | SCR-WS-01; SCR-WS-10 | P1 |
| SCR-WS-04 | Workspace — Active Handling | Kerjakan case assigned | Complaint Officer (penanganan) | SCR-Q-01 pilih case | Lanjut proses; pantau SLA | SCR-Q-01 | P0 |
| SCR-WS-05 | Workspace — Submit for Review | Ajukan hasil + bukti | Complaint Officer (penanganan) | SCR-WS-04 siap review | Submit PENDING_REVIEW | SCR-WS-04; SCR-SV-01 | P0 |
| SCR-WS-06 | Workspace — Rejected Resubmission | Perbaiki setelah reject | Complaint Officer (penanganan) | Queue item rejected | Perbaiki; resubmit | SCR-WS-05; SCR-HX-01 | P1 |
| SCR-WS-07 | Workspace — Reopened Continuation | Lanjut case REOPENED | Complaint Officer (penanganan) | Assignment reopen | Lanjut dengan riwayat utuh | SCR-WS-04; SCR-HX-01 | P1 |
| SCR-WS-08 | Workspace — Escalation Handover | Beri konteks ke Supervisor | Complaint Officer (penanganan) | Permintaan konteks eskalasi | Serahkan konteks | SCR-WS-04; SCR-WS-09 | P1 |
| SCR-WS-09 | Workspace — Assignment | Assign ke Officer/unit | Supervisor | SCR-Q-02 unassigned | Assign | SCR-Q-02 | P0 |
| SCR-WS-10 | Workspace — Approval Review | Approve/reject hasil | Supervisor | SCR-Q-02 pending approval | Approve close / Reject | SCR-Q-02; SCR-WS-05 | P0 |
| SCR-WS-11 | Workspace — Escalation Handling | Tangani/teruskan eskalasi | Supervisor | SCR-Q-02 eskalasi | Putuskan eskalasi | SCR-Q-02; SCR-HX-02 | P1 |
| SCR-WS-12 | Workspace — Reopen Approval | Setujui/tolak reopen | Supervisor | SCR-Q-02 / dari SCR-WS-03 | Approve/reject reopen | SCR-WS-03; SCR-HX-02 | P1 |
| SCR-SV-01 | Supporting — Evidence & Related Cases | Bukti & case terkait | Complaint Officer (penanganan) | Dari SCR-WS-04 | Lihat/lampirkan evidence | SCR-WS-04 | P1 |
| SCR-SV-02 | Supporting — Customer Interaction History | Riwayat interaksi pelanggan | Complaint Officer (intake) | Dari SCR-WS-01/02 | Lookup on-demand | SCR-WS-01 | P1 |
| SCR-SV-03 | Supporting — Unit Drill-down | Drill-down unit by exception | Manager | Dari SCR-DASH-01 | Inspect tren unit | SCR-DASH-01 | P2 |
| SCR-HX-01 | History — Decision (Officer) | Alasan reject / riwayat penanganan | Complaint Officer (penanganan) | Dari workspace reject/reopen | Baca konteks | SCR-WS-04 | P1 |
| SCR-HX-02 | History — Closure & Escalation (Supervisor) | Riwayat closure & konteks eskalasi | Supervisor | Dari SCR-WS-11/12 | Baca konteks | SCR-Q-02 | P1 |
| SCR-DASH-01 | Dashboard — Aggregate KPI/Trend | Indikator & tren agregat | Manager | Login Manager | Pantau; buka drill-down | SCR-SHELL-01 | P2 |
| SCR-ADM-01 | Administration (config) | Konfigurasi workflow/SLA/role *(bukan persona operasional)* | Administrator | Nav admin Mode A | Ubah config beraudit | Di luar closed set operasional | Deferred ops |
| SCR-SET-01 | Settings / Profile | Profil & keamanan akun Mode A | Semua (akun) | Global nav | Ubah profil / password Mode A | SCR-SHELL-01 | Hygiene P1 |

**Tidak ada layar terpisah “Return to Queue”** — kembali ke SCR-Q-01 atau SCR-Q-02.

**Search:** tidak ada destinasi Search terpisah di IA-001. Pencarian konteks pelanggan/case = perilaku di dalam Workspace / Supporting Views (SCR-WS-01, SCR-SV-02), bukan modul baru.

Pemetaan WF: SCR-SHELL-01↔WF-001-01 … SCR-SV-02↔WF-001-21 (lihat WF-PLAN-001 §2). SCR-AUTH-01 & SCR-SET-01 / SCR-ADM-01 di luar backlog wireframe case-level tetapi dibutuhkan alur Login→Closure Mode A.

---

## 7. Workspace Inventory

| Workspace | Destinasi IA | Pengguna primer | Wajib Mode A v0.x operasional? | Catatan |
|---|---|---|---|---|
| **Complaint Workspace** | Complaint Workspace | Officer, Supervisor | **Ya** | Satu workspace; zona/mode berbeda |
| **Queue Workspace** | Queue | Officer (penanganan), Supervisor | **Ya** | Dua populasi, satu konsep Queue |
| **Dashboard Workspace** | Dashboard | Manager | **MAY deferred** (BC-8.4) | Persona tetap valid |
| **Supporting Views** | Supporting Views | Officer, Manager (drill-down) | Ya (on-demand) | Bukan rumah kerja primer |
| **History** | History | Officer, Supervisor | Ya (on-demand / wajib continuity) | Sering embedded di Workspace |
| **Shell / Session** | (frame) | Semua | Ya | WF-001-01 |
| **Administration** | — (config) | Administrator | Terpisah dari closed set operasional | Jangan dicampur Dashboard Manager |
| **Settings / Profile** | — (akun) | Semua akun | Hygiene Mode A | Bukan case workspace |
| **Search** | — | — | **Tidak sebagai workspace** | Lihat §6 |

Tidak ada “Supervisor Workspace” atau “Manager Workspace” terpisah sebagai destinasi baru: Supervisor memakai Queue + Complaint Workspace; Manager memakai Dashboard (+ Supporting Views).

---

## 8. Screen Flow — Login → Complaint Closure

### 8.1 Happy path (Mode A)

```
SCR-AUTH-01 Login
  │
  ├─[Officer intake]──► SCR-SHELL-01 → SCR-WS-01 (new)
  │                         │
  │                         ▼ case REGISTERED
  │                    (siap kontak berikutnya / mode switch)
  │
  ├─[Supervisor]──────► SCR-SHELL-01 → SCR-Q-02
  │                         │ pilih unassigned
  │                         ▼
  │                    SCR-WS-09 Assignment → case ASSIGNED
  │                         │
  │                         ▼ Return to Queue
  │
  └─[Officer handling]─► SCR-SHELL-01 → SCR-Q-01
                            │ pilih assigned
                            ▼
                       SCR-WS-04 Active Handling → IN_PROGRESS
                            │
                            ▼
                       SCR-WS-05 Submit for Review → PENDING_REVIEW
                            │ Return to Queue
                            ▼
                       (Supervisor) SCR-Q-02 → SCR-WS-10 Approval
                            │ Approve
                            ▼
                       case CLOSED
                            │
                            ▼
                       Logout (SCR-SHELL-01)
```

### 8.2 Cabang penting (bukan happy path saja)

| Cabang | Alur singkat |
|---|---|
| Follow-up | Login → SCR-WS-02 |
| Intake tidak lengkap | SCR-WS-01 → tahan/lengkapkan (PWDM-001) |
| Reject review | SCR-WS-10 Reject → Officer SCR-WS-06 + SCR-HX-01 → resubmit |
| Escalation | Supervisor SCR-WS-11; Officer SCR-WS-08 bila diminta konteks |
| Reopen | Officer SCR-WS-03 → Supervisor SCR-WS-12 → Officer SCR-WS-07 |
| Manager | Login → SCR-DASH-01 → optional SCR-SV-03 → Logout |

Alur destinasi formal → **NAV-001 §2**.

---

## 9. Wireframe Planning

**Sumber rencana:** WF-PLAN-001 (21 item WF-001-01 … WF-001-21).

Discovery ini **tidak menggambar** wireframe. Daftar wajib:

| Tier | Item |
|---|---|
| P0 Release 1 | WF-001-01, 02, 03, 04, 05, 07, 08, 14, 15 |
| P1 Release 2 | WF-001-06, 09, 10, 11, 12, 13, 16, 17, 18, 21 |
| P2 Release 3 | WF-001-19, 20 |
| Tambahan alur sesi | Login (SCR-AUTH-01), Settings hygiene (SCR-SET-01) — wireframe ringan shell/auth, bukan case workspace |

Konstitusi layout → **WF-000**. Spesifikasi frame → **WF-001-01** (draft).

---

## 10. Prototype Planning

| Fidelity | Isi | Kapan | Catatan |
|---|---|---|---|
| **Low Fidelity** | WF-001 seluruh P0 lalu P1; zona IA + primary action saja | Segera setelah Approval discovery / paralel Review | Tidak ada visual brand |
| **Medium Fidelity** | Komponen pola, state kosong/error/permission, reading flow WF-000 | Setelah LF P0 stabil | Masih grayscale/system |
| **High Fidelity** | Visual design system modul (bukan portal Enterprise) | Setelah MF P0 + aturan UX writing | UI-001 future |
| **Clickable Prototype** | Jalur §8.1 + cabang reject & reopen | Setelah LF/MF P0–P1 terhubung | Demo UAT bisnis; Manager P2 boleh terpisah |

Urutan prototype clickable disarankan: Shell → Queue Officer/Supervisor → Intake → Handling → Submit → Approval → Closure; kemudian Reject/Resubmit; kemudian Reopen.

---

## 11. Frontend Redesign Roadmap

Tujuan: menyelaraskan FE Mode A yang ada ke model UX yang disetujui **tanpa** silent cutover kontrak dual-SoT di luar keputusan DEC yang berlaku; UI Aggregate berdampingan foundation bila relevan.

### Batch R1 — Inti operasional (P0)

1. Shell & navigation global sesuai NAV-001 / WF-001-01  
2. Queue Assigned (Officer) + Queue Supervisor priority  
3. Complaint Workspace: New Intake, Follow-up, Active Handling, Submit for Review  
4. Supervisor Assignment + Approval Review  
5. Alur Login → Closure demonstrable  

### Batch R2 — Kontinuitas (P1)

1. Reject/Resubmit + History Officer  
2. Reopen routing + Reopen approval + Continuation  
3. Escalation handling + handover konteks  
4. Supporting: Evidence/Related Cases + Interaction History  
5. Settings/Profile hygiene (bukan redesign identity platform)  

### Batch R3 — Manager (P2)

1. Dashboard Aggregate KPI/Trend  
2. Unit drill-down  
3. Hormati **MAY deferred** (BC-8.4) — batch ini boleh dijadwalkan belakangan tanpa memblokir R1  

### Batch R4 — Hygiene & keselarasan lab

1. Rapikan duplikasi rute legacy vs Aggregate `/complaints` vs `/complaints/cm` sesuai DEC-020 coexistence (bukan force-merge)  
2. Sembunyikan/nonaktifkan permukaan yang meniru “portal enterprise” berlebih di dalam modul  
3. Administrator config — hanya jika diperlukan operasi Mode A, terpisah dari Dashboard Manager  

**Urutan rekomendasi:** R1 → R2 → (R4 paralel hygiene) → R3.

---

## 12. UX Gap Analysis

Perbandingan **frontend saat ini** (`frontend/src/app`) terhadap model UX (§6–§7 / PDS–NAV).

### 12.1 Missing screens (relatif model UX)

| Gap | Model | FE saat ini |
|---|---|---|
| Queue Supervisor berprioritas tetap (eskalasi→SLA→unassigned) | SCR-Q-02 | Ada `/queue`, `/complaints/cm/supervisor` — perlu verifikasi prioritas & populasi vs model |
| Workspace modes intake vs handling sebagai satu Workspace | SCR-WS-* | Terpecah: `/complaints/new`, `/complaints/[id]`, `/complaints/cm/...` |
| History wajib pada reject/reopen/eskalasi | SCR-HX-* | Timeline sering placeholder / tidak lengkap per UX-SCR-001 gaps historis |
| Supporting Interaction History & Related Cases | SCR-SV-01/02 | Belum sebagai Supporting Views formal |
| Dashboard Manager agregat sesuai PDS | SCR-DASH-01 | `/dashboard`, `/reports` ada — belum terbukti selaras persona Manager-only agregat |
| Wireframe-backed empty/error/permission states | WF-000 | Sebagian ada ad hoc |

### 12.2 Duplicate / overlapping screens

| Temuan | Risiko |
|---|---|
| `/complaints/*` (legacy) berdampingan `/complaints/cm/*` (Aggregate) | Dua permukaan case — sesuai DEC-020 coexistence; **bukan** digabung diam-diam |
| `/assignments`, `/resolutions`, `/attachments` terpisah dari Workspace | Memecah One Complaint Workspace |
| `/dashboard` vs `/reports` | Potensi duplikasi destinasi Dashboard/Reference |

### 12.3 Navigation issues

- Entry point belum tegas per persona/mode (Officer intake tanpa Queue vs handling dengan Queue).  
- Global nav menampilkan banyak item setara (users, settings, reports, attachments) — cenderung “app shell” daripada closed set destinasi IA.  
- Return to Queue belum konsisten sebagai return path tunggal pasca keputusan kritis.

### 12.4 Information issues

- Prioritas Immediate/Contextual/On-demand belum ditegakkan per zona IA.  
- Customer 360 / Interaction History masih terbatas (bukan SoR; cache/referensi saja).  
- Continuity Decision History pada reject/reopen belum dijamin di UI.

### 12.5 Workspace issues

- Belum ada penegakan “satu Complaint Workspace” — banyak rute fungsional terpisah.  
- Manager vs Supervisor dashboard audience belum dipisahkan jelas (bisnis: Supervisor diotorisasi lebih dulu; Manager MAY deferred).  
- Administration (`/users`, config) bercampur navigasi operasional.

### 12.6 Yang sudah mendekati model

- Login Mode A & shell app ada.  
- Queue, complaint list/detail, new complaint, supervisor CM surface, dashboard — fondasi lab ada.  
- UX-SCR-001 Case Detail Workspace (Approved historis) — perlu **direkonsiliasi** ke persona merge Complaint Officer + zona IA (bukan dibuang tanpa mapping).

---

## 13. Implementation Readiness

### Verdict

**UX Discovery untuk Complaint Management Module dinyatakan LENGKAP untuk memulai wireframing (WF-001).**

Desainer FE boleh mulai Low Fidelity dari WF-PLAN-001 Release 1 tanpa menunggu dokumen discovery tambahan.

Implementasi frontend produksi/modul **belum** “langsung coding bebas discovery” sampai blocker di bawah ditutup atau diterima secara eksplisit sebagai asumsi sprint.

### Bukan blocker discovery (boleh jalan paralel wireframe)

- Approval formal paket Draft → Reviewed → Approved (governance review, bukan discovery gap).  
- Manager Workspace deferred (BC-8.4) — wireframe P2 boleh belakangan.  
- Detail visual design system / High Fidelity.  
- Keputusan teknis API (di luar scope discovery).

### Sisa UX blockers sebelum implementasi UI (bukan sebelum wireframe)

| ID | Blocker | Dampak |
|---|---|---|
| UX-B1 | Paket baseline PDS-001 · PWDM-001 · IA-001 · NAV-001 · UX-DISC-001 masih **Draft** (belum Reviewed/Approved) | Wireframe boleh draft; implementasi “Approved design” menunggu Approval |
| UX-B2 | Rekonsiliasi UX-SCR-001 (Case Detail) ke model zona IA + persona Complaint Officer | Cegah dua SoT screen bertentangan |
| UX-B3 | Aturan UX writing (label status/aksi) & state kosong/error/permission belum tertulis sebagai artefak UX | Diperlukan sebelum High Fidelity / coding polish |
| UX-B4 | Keputusan delivery Manager Dashboard (jadwalkan R3 vs defer eksplisit di rencana rilis UI) | Hindari setengah-bangun permukaan Manager |

**Tidak ada blocker discovery yang tersisa untuk memulai wireframe P0.**

---

## Traceability singkat

| Input bisnis | Dipakai di discovery sebagai |
|---|---|
| BC-000 persona & deferred Manager | §2, §7, §11, §13 |
| BC-001 principles (Business Before Technology, dll.) | §1 UX goals |
| BC-002 / BC-003 | Istilah & perilaku dirujuk lewat baseline; tidak diulang |
| BW-000 stages & entry points | §3 journeys, §8 flow |

| Artefak UX | Peran |
|---|---|
| PDS-001 | Persona SoT |
| PWDM-001 | Journey/decision SoT |
| IA-001 | IA SoT |
| NAV-001 | Navigation SoT |
| WF-000 / WF-PLAN-001 | Layout constitution & wireframe backlog |
| UX-FOUNDATION-000 | Payung baseline |
| **UX-DISC-001** | Paket discovery lengkap (dokumen ini) |

---

## Related

- `docs/ux/UX-FOUNDATION-000-Complaint-Module-UX-Foundation.md`
- `docs/ux/PDS-001-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/NAV-001-Navigation-Architecture.md`
- `docs/ux/WF-000-Wireframe-Constitution-Layout-System.md`
- `docs/ux/WF-PLAN-001-Wireframe-Roadmap-Backlog.md`
- `12 UI UX Spec/ECMP_Personas_And_Journeys_v0.1.md`
- `12 UI UX Spec/ECMP_Screen_Spec_Case_Detail_Workspace_v0.1.md`

## Future Work

- **WF-001 Release 1 LF:** `docs/ux/WF-001-R1-Wireframe-Package.md` (Draft complete).
- **WF-001 Release 2 LF:** `docs/ux/WF-001-R2-Wireframe-Package.md` (Draft complete).
- WF-001 Release 3 package; UI-001 High Fidelity · Prototype · Implementation.
- Mode B / Enterprise surfaces — **di luar ruang lingkup**.
