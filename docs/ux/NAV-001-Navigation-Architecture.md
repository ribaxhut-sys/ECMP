# NAV-001 — Navigation Architecture

| Field | Value |
|---|---|
| Document ID | NAV-001 |
| Title | Navigation Architecture |
| Status | Reviewed — revisi diterapkan per temuan Navigation Architecture Review; menunggu Approval |
| Version | 1.0 |
| Date | 2026-08-03 |
| Parent | IA-001 |
| Subordination | ECMP-CONSTITUTION-001 → PDS-000 → PWDM-001 → IA-001 → **NAV-001** → (future) WF-001 |

## Single responsibility

> Mendefinisikan **bagaimana pengguna bergerak antar destinasi navigasi** di Complaint Management Module — titik masuk, jalur utama, jalur sekunder, keluar, dan kembali.

NAV-001 **bukan** tempat mendefinisikan: layout, komponen, warna, wireframe, UI, API, Business Rule, entity baru, atau halaman baru. Destinasi navigasi adalah closed set dari IA-001 §5: **Dashboard · Queue · Complaint Workspace · Supporting Views · History · Return to Queue**. Tidak ada tujuan baru.

Semua rujukan persona → PDS-000. Semua rujukan alur kerja & keputusan → PWDM-001. Semua rujukan destinasi, zona, dan prioritas informasi → IA-001.

---

## 1. Navigation Model

### Customer Service

| Elemen | Definisi navigasi |
|---|---|
| **Entry Point** | `Login` → orientasi ke pelanggan yang sedang dilayani (PWDM-001 §1). Tidak ada Dashboard. Tidak ada Queue (PDS-000 §1; IA-001 §5, §7). |
| **Primary Navigation** | Langsung ke **Complaint Workspace** — case baru, case aktif pelanggan (follow-up), atau routing permintaan reopen. |
| **Secondary Navigation** | **Supporting Views** (Customer Interaction History, on-demand — PDS-000 §4; IA-001 §5). |
| **Exit Point** | `Logout` setelah sesi tanpa case tertinggal "belum lengkap" (PWDM-001 §1 Completion/Logout). |
| **Return Path** | Tetap di destinasi **Complaint Workspace** setelah keputusan intake selesai — siap menerima kontak berikutnya. Bukan destinasi baru. Bukan Return to Queue (CS tidak memiliki Queue — IA-001 §5). |
| **Interruption (kontak baru saat intake)** | Navigasi **tidak berubah** — tetap di **Complaint Workspace**. Tidak ada perpindahan destinasi (PWDM-001 §1: interupsi ini bukan keputusan formal; bagian dari urutan kerja rutin). |

### Resolver / Case Handler

| Elemen | Definisi navigasi |
|---|---|
| **Entry Point** | `Login` → **Queue** (daftar case assigned, diurut sisa SLA — IA-001 §5; PDS-000 §4 Immediate). |
| **Primary Navigation** | Queue → pilih case → **Complaint Workspace** (kerja pada case assigned). |
| **Secondary Navigation** | Dari dalam Workspace: **Supporting Views** (Evidence, Related Cases) dan/atau **History** (Decision History — wajib saat reject/reopen, IA-001 §8 poin 9). |
| **Exit Point** | `Logout` setelah semua case assigned berstatus jelas (PWDM-001 §1). |
| **Return Path** | **Return to Queue** setelah salah satu dari tiga hasil keputusan kritis PWDM-001 §1/§2: (1) lanjut proses tercatat, (2) ajukan review, atau (3) serahkan konteks ke Supervisor (handover) → ulangi hingga Completion. |

### Supervisor

| Elemen | Definisi navigasi |
|---|---|
| **Entry Point** | `Login` → **Queue** dengan prioritas tetap dan tunggal: eskalasi baru → SLA mendekati/lewat → antrian belum ter-assign (PDS-000 §4; PWDM-001 §1; IA-001 §5). Tidak ada prioritas Queue lain. |
| **Primary Navigation** | Queue → pilih item → **Complaint Workspace** untuk keputusan assign / approve / eskalasi / reopen (IA-001 §5). |
| **Secondary Navigation** | Dari dalam Workspace: **History** (riwayat closure untuk reopen; alasan/konteks eskalasi — IA-001 §5; PWDM-001 §4 Continuity). |
| **Exit Point** | `Logout` setelah semua keputusan tertunda diputuskan (PWDM-001 §1). |
| **Return Path** | **Return to Queue** → item prioritas berikutnya dalam urutan eskalasi → SLA → unassigned. |

### Manager

| Elemen | Definisi navigasi |
|---|---|
| **Entry Point** | `Login` → **Dashboard** (Aggregate KPI/Trend — tujuan akhir, bukan transit — IA-001 §5; PDS-000 §4 Immediate). |
| **Primary Navigation** | Tetap di **Dashboard**. Tidak ada Queue. Tidak ada Complaint Workspace operasional (PDS-000 §7 poin 3; IA-001 §5, §8 poin 3). |
| **Secondary Navigation** | Opsional **Supporting Views** — drill-down unit *by exception* saat angka agregat mencurigakan (PDS-000 §4 On-demand). Bukan detail transaksi individual. |
| **Exit Point** | `Logout` setelah gambaran kinerja hari itu cukup tanpa pertanyaan terbuka (PWDM-001 §1). |
| **Return Path** | Kembali ke **Dashboard** dari Supporting Views. Tidak ada Return to Queue. |

---

## 2. Navigation Flow

Destinasi yang dipakai di bawah ini hanya dari closed set IA-001 §5.

### Customer Service

```
Login
  → Complaint Workspace
       ├─ (on-demand) Supporting Views
       ├─ (interupsi kontak baru) tetap di Complaint Workspace — destinasi tidak berubah
       └─ keputusan intake / follow-up / routing reopen
  → tetap di Complaint Workspace (siap menerima kontak berikutnya)
  → (ulangi per kontak) …
  → Logout
```

Tidak melewati Dashboard. Tidak melewati Queue. Tidak memakai Return to Queue. Tidak ada destinasi return terpisah.

### Resolver / Case Handler

```
Login
  → Queue (assigned, urut sisa SLA)
  → Complaint Workspace
       ├─ (on-demand) Supporting Views
       └─ (on-demand / wajib saat reject·reopen) History
  → keputusan kritis (salah satu):
       (1) lanjut proses tercatat
       (2) ajukan review
       (3) serahkan konteks ke Supervisor (handover)
  → Return to Queue
  → (ulangi hingga Completion) …
  → Logout
```

Satu jalur primer: Queue ↔ Complaint Workspace. Ketiga hasil keputusan kritis memakai Return Path yang sama. Secondary hanya dari dalam Workspace. Handover tidak menambah destinasi.

### Supervisor

```
Login
  → Queue (eskalasi → SLA → unassigned)
  → Complaint Workspace
       └─ (wajib saat reopen·eskalasi) History
  → Return to Queue
  → (ulangi hingga Completion) …
  → Logout
```

**Definisi Queue Entry otoritatif (satu-satunya):** eskalasi baru → SLA mendekati/lewat → antrian belum ter-assign (IA-001 §5). Tidak diperluas. Urutan prioritas Queue tidak boleh diganti menjadi urutan kedatangan (PWDM-001 §6 Sequence; PDS-000 §4).

### Manager

```
Login
  → Dashboard
       └─ (opsional, by exception) Supporting Views
  → kembali ke Dashboard
  → Logout
```

Tidak ada Complaint Workspace. Tidak ada Queue. Tidak ada Decision sebagai destinasi navigasi. Tidak ada Return to Queue.

---

## 3. Entry / Exit Rules

### Kapan persona memasuki Complaint Workspace?

| Persona | Memasuki Complaint Workspace ketika… |
|---|---|
| **Customer Service** | Kontak pelanggan membutuhkan pencatatan case baru, follow-up pada case aktif, atau penerusan permintaan reopen — Entry Point sesi langsung ke Workspace (IA-001 §5). |
| **Resolver / Handler** | Satu case dipilih dari Queue assigned untuk dikerjakan (PWDM-001 Routine work; IA-001 §5). |
| **Supervisor** | Satu item dipilih dari Queue menurut definisi otoritatif: eskalasi → SLA → unassigned — untuk keputusan case-level assign / approve / eskalasi / reopen (PWDM-001 Critical decisions; IA-001 §5). |
| **Manager** | **Tidak pernah** memasuki Complaint Workspace operasional (PDS-000 §7 poin 3; IA-001 §5, §8 poin 3). Drill-down Manager berhenti di Supporting Views tingkat unit, bukan Workspace case. |

### Kapan persona meninggalkan Complaint Workspace?

| Persona | Meninggalkan ketika… |
|---|---|
| **Customer Service** | Hanya saat `Logout`. Setelah keputusan intake (teruskan / tahan / routing reopen), destinasi navigasi **tidak ditinggalkan** — tetap Complaint Workspace. |
| **Resolver / Handler** | Salah satu dari tiga hasil keputusan kritis selesai: (1) lanjut proses tercatat, (2) ajukan review, atau (3) serahkan konteks ke Supervisor — lalu **Return to Queue**. |
| **Supervisor** | Keputusan gatekeeper selesai (assign / approve·reject / tangani·teruskan eskalasi / setujui·tolak reopen) — lalu **Return to Queue**. |
| **Manager** | Tidak berlaku — Manager tidak berada di Complaint Workspace. |

### Kapan persona kembali?

| Persona | Kembali bagaimana… |
|---|---|
| **Customer Service** | Kontak berikutnya dilayani di destinasi yang sama: **Complaint Workspace**. Tidak ada perpindahan destinasi antar-kontak. Tidak melewati Queue. |
| **Resolver / Handler** | **Return to Queue** mengembalikan ke daftar assigned; pemilihan case berikutnya memasuki Workspace lagi — termasuk setelah handover konteks ke Supervisor. Context Switching (PWDM-001 §4) menuntut History/Decision History terbawa saat masuk ulang ke case reject/reopen. |
| **Supervisor** | **Return to Queue** mengembalikan ke item prioritas berikutnya dalam urutan eskalasi → SLA → unassigned. |
| **Manager** | Dari Supporting Views kembali ke **Dashboard** saja. |

---

## 4. Cross Persona Navigation

Verifikasi terhadap IA-001 §7 dan PDS-000 §6 Common:

| Aturan | Status |
|---|---|
| **Same destinations** | Closed set destinasi sama untuk modul: Dashboard, Queue, Complaint Workspace, Supporting Views, History, Return to Queue. Tidak ada destinasi persona-khusus di luar set ini. |
| **Different priorities** | Yang berbeda adalah **jalur & prioritas**, bukan destinasi baru: CS → Workspace langsung; Handler/Supervisor → Queue dulu (populasi Queue berbeda); Manager → Dashboard saja. |
| **No duplicated workspace** | Satu **Complaint Workspace** untuk CS, Handler, dan Supervisor. Bukan workspace terpisah per persona. Identitas case konsisten (PDS-000 §6 Common; IA-001 §7, §8 poin 7). |
| **No duplicate navigation** | Queue hanya untuk Handler dan Supervisor. CS dan Manager sengaja tanpa Queue — bukan Queue kosong (IA-001 §7). Manager tanpa Return to Queue. |
| **No dual workflow** | Setiap langkah navigasi hanya mengekspos keputusan yang sudah ada di PWDM-001 §2 — tidak menciptakan keputusan baru lewat jalur navigasi (IA-001 §7). |

---

## 5. Navigation Constitution

Prinsip permanen — diturunkan **hanya** dari PDS-000, PWDM-001, dan IA-001:

1. **Closed Destination Set** — hanya Dashboard, Queue, Complaint Workspace, Supporting Views, History, Return to Queue (IA-001 §5). Destinasi baru memerlukan revisi IA, bukan NAV.
2. **One Primary Path** — setiap persona punya satu jalur primer (IA-001 §5). Secondary hanya dipanggil on-demand dari jalur primer, bukan jalur sejajar yang bersaing.
3. **Minimal Navigation Depth** — kedalaman maksimal mengikuti alur IA-001 §5: Entry → (Queue bila ada) → Workspace atau Dashboard → Supporting Views/History → Return. Tidak ada lapisan destinasi tambahan.
4. **Never Lose Context** — perpindahan ke/dari Workspace tidak boleh memutus konteks case; History wajib menyertai Decision saat reject/reopen/eskalasi (PWDM-001 §4; IA-001 §8 poin 9).
5. **Always Return to Previous Work** — Handler dan Supervisor selalu **Return to Queue** setelah keputusan case (termasuk Handler handover ke Supervisor); CS tetap di **Complaint Workspace** siap kontak berikutnya; Manager kembali ke Dashboard (IA-001 §5; PWDM-001 Completion).
6. **No Duplicate Navigation** — satu Queue concept, populasi berbeda per persona; tidak ada Queue placeholder untuk CS/Manager (IA-001 §7).
7. **One Complaint Workspace** — bukan layar/workspace per persona (PDS-000 §6; IA-001 §8 poin 7).
8. **Navigation Follows Responsibility** — persona hanya bernavigasi ke destinasi yang didukung R/A/C/I di PDS-000 §5; sel `—` tidak terjangkau (IA-001 §8 poin 5).
9. **Manager Never Enters Operational Workspace** — Dashboard (+ Supporting Views by exception) saja; read-only & agregat selamanya (PDS-000 §7 poin 3; IA-001 §8 poin 3).
10. **Queue Priority Is Binding for Supervisor** — satu definisi otoritatif: eskalasi → SLA → unassigned; bukan urutan kedatangan; tidak diperluas (PDS-000 §4; PWDM-001 §1/§6; IA-001 §5).
11. **Work Mode, Not Account** — jalur navigasi mengikuti persona mode yang aktif, bukan akun tetap (PDS-000 §7 poin 9; IA-001 §8 poin 10).
12. **Reference, Don't Redefine** — NAV-001 tidak mengubah persona, workflow, inventori informasi, atau zona; perubahan itu adalah revisi PDS-000, PWDM-001, atau IA-001 (PDS-000 §7; IA-001 §8 poin 8).

---

## Related

- `docs/ux/PDS-000-Persona-Design-Specification.md`
- `docs/ux/PWDM-001-Persona-Workflow-Decision-Model.md`
- `docs/ux/IA-001-Information-Architecture.md`
- `docs/ux/UX-FOUNDATION-000-Complaint-Module-UX-Foundation.md`

## Future Work

WF-001 Low Fidelity Wireframes — di luar ruang lingkup dokumen ini.
