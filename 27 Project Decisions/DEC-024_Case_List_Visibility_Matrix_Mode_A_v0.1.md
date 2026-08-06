# Decision Record — Case List Visibility Matrix (Mode A Lab)

| Field | Value |
|---|---|
| ID | DEC-024 |
| Version | 0.1 |
| Owner | Solution Architect (draft) / Business Owner (sign-off) |
| Status | 🟢 Accepted (lab) — OQ-1…4 decided; implementation authorized Mode A |
| Date | 2026-08-06 |
| Related | DEC-020 (dual-SoT); CAP-008 Mode A API-530…535; FRD-CM-B2; OrgUnitGuard / SECMIG-P4; ADR-008 |
| Type | Project Decision (visibility rules) — **not** Mode B unlock · **not** Retirement DEC |

---

## 1. Intent

Agent dan pejabat cabang/Pusat membutuhkan **Daftar Case** yang:

- Agent hanya melihat Case yang relevan baginya  
- Supervisor / Manager cabang melihat Case di lingkup cabang  
- Supervisor / Manager Pusat melihat lingkup Pusat (+ eskalasi), bukan otomatis seluruh enterprise kecuali diputuskan  
- Admin modul melihat semua  

Saat ini Mode A CAP-008 **tidak menspesifikasikan** Case list API (API-530…535 = create/get/status/resolve/close only). UI mengingat Case ID di browser — **bukan** SoT visibility.

Dokumen ini mengunci **aturan visibility** sebelum OpenAPI/FR list diotorisasi untuk lab.

---

## 2. Decision (proposed)

### 2.1 Dua lapisan AuthZ (binding)

1. **Permission gate** — tanpa izin baca Case/Complaint yang disepakati → 403 / empty denied.  
   Interim lab: `complaints:read` (atau permission Case khusus bila ditambahkan ke matriks ADR-008).  
2. **Row visibility** — filter **server-side** saja (bukan hanya FE):

| Visibility class | Rule (SQL/filter sense) |
|---|---|
| `SELF` | **Mode A (BQ-006 — assigned user not stored):** `created_by = principal.user_id`. **Target after assigned-user unlock:** `assigned_user_id = me` **OR** (`assigned` null **AND** `created_by = me`). Riwayat create/reassign tetap di timeline Case. |
| `UNIT` | `owning_unit_id` sama dengan `principal.org_unit_id` (cabang masing-masing; tidak lintas cabang). |
| `PUSAT` | `owning_unit_id` ∈ pusat unit codes (default `PUSAT`). **Eskalasi:** filter status/jalur eskalasi ditambahkan saat API-520 aktif — Mode A slice = unit Pusat saja sampai escalate shipped. |
| `ALL` | Tidak ada filter unit/creator (admin modul). |

### 2.2 Matriks peran → visibility class

Pemetaan ke kode peran Mode A yang sudah dipakai di IAM lab (bukan IdP enterprise):

| Peran bisnis | Kode lab (contoh) | Visibility | Catatan |
|---|---|---|---|
| Agent | `AGENT`, `CS_AGENT`, `HANDLER` | **SELF** | Produksi target: utamakan **assigned**. Lab: `created_by` jika belum di-assign. |
| Supervisor / Manager Pusat | peran HO non-admin *(perlu seed eksplisit)* | **PUSAT** | **Decided:** Pusat + eskalasi saja — **bukan** ALL / semua cabang |
| Admin modul | `ADMIN`, `ADMINISTRATOR` | **ALL** | Bukan dari IdP roles[] (ADR-014/015 hardening) |
| Super Admin | `SUPER_ADMIN` | **ALL** | Lab/break-glass |
| Supervisor cabang · Manager cabang | `SUPERVISOR`, `BRANCH_SUPERVISOR` (+ manager via permission) | **UNIT** | **Decided:** masing-masing **hanya Case cabang/unit sendiri** (tidak lintas cabang). Manager & Supervisor **sama visibility**; beda wewenang via **permission** |

> Cabang-scoped vs head-office-scoped sudah ada di `BRANCH_SCOPED_ROLE_CODES` / `HEAD_OFFICE_SCOPED_ROLE_CODES` — list Case harus konsisten dengan itu.

### 2.3 Apa yang **tidak** diputuskan di sini

| Topik | Status |
|---|---|
| Force-merge daftar pengaduan ke satu URL (`/complaints` only) | Tetap **DEC-020** — butuh Retirement DEC |
| Mode B SSO / Identity Adapter / enterprise org sync | **CLOSED** (C-B6-1) |
| API-526 FRD-CM-002 Search/List Cases (visibility penuh eskalasi) | Rujukan masa depan; lab boleh slice lebih kecil |
| Menyamakan Pusat = lihat semua cabang | **Default TOLAK** sampai BO override tertulis |

### 2.4 Kontrak list (arah implementasi setelah sign-off)

Usulan lab (nama final saat masuk OpenAPI):

- `GET /api/v1/cm/cases` (atau path setara yang disetujui katalog)  
- Query: `page`, `pageSize`, optional `status`, optional `complaintId`  
- Server menerapkan matriks §2.2  
- Response: proyeksi ringkas Case (sudah ada skema compact di `cm-case-management.v1.yaml`)  
- FE: halaman **Daftar Case** + link dari dashboard/agent home; halaman per-pengaduan `/complaints/cm/{id}/cases` tetap (subset filter `complaintId`)

**Dilarang:** list “semua Case” di client lalu sembunyikan baris.

---

## 3. Acceptance criteria (lab)

1. Agent A tidak melihat Case assigned/created oleh Agent B (unit sama atau beda).  
2. Supervisor cabang X melihat Case `owning_unit_id` = X; tidak melihat cabang Y.  
3. Admin melihat Case lintas unit.  
4. Request tanpa permission baca → ditolak.  
5. Uji otomatis untuk tiap visibility class (minimal SELF / UNIT / ALL).  
6. Tidak mengubah dual-SoT pengaduan DEC-020.

---

## 4. Open questions (BO)

| ID | Pertanyaan | Default draft | Keputusan BO |
|---|---|---|---|
| OQ-1 | Agent: assigned saja atau assigned∨createdBy? | **Active queue:** `assigned = me` **OR** (`assigned` null **AND** `createdBy = me`). **Jangan** “createdBy tanpa batas”. Riwayat create/reassign ada di **timeline Case** (bukan memperluas list agent). Opsional belakangan: tab “Pernah saya tangani” dengan permission/scope terpisah. | **Decided (2026-08-06)** — active queue + timeline; no unbounded createdBy |
| OQ-2 | Pusat: hanya Pusat+eskalasi atau seluruh cabang? | Pusat+eskalasi saja | **Decided (2026-08-06)** — Pusat **hanya** Case unit Pusat **+** Case yang dieskalasi ke Pusat; **bukan** semua cabang |
| OQ-3 | Manager cabang: role code terpisah atau permission di atas SUPERVISOR? | Permission beda, scope UNIT sama | **Decided (2026-08-06)** — Manager & Supervisor cabang **hanya melihat Case cabang masing-masing** (UNIT sendiri, tidak lintas cabang). Visibility keduanya sama; beda wewenang lewat **permission** |
| OQ-4 | Permission baru `cases:read` atau pakai `complaints:read`? | Interim `complaints:read` | **Decided (2026-08-06)** — lab pakai **`complaints:read`**; `cases:read` belakangan bila matriks ADR-008 dipisah |

---

## 5. Sign-off

| Peran | Nama | Tanggal | Setuju draft untuk implementasi lab? |
|---|---|---|---|
| Business Owner | | | Ya / Tidak / Revisi OQ-… |
| Solution Architect | | | |
| Catatan | | | |

Setelah **Ya**: lanjut OpenAPI + service filter + UI Daftar Case (Mode A).  
Bukan izin cutover 1 SoT pengaduan dan bukan unlock Mode B.

---

## 6. Next engineering slice (setelah sign-off)

1. Jawab OQ-1…4 di atas.  
2. Tambah operasi list ke `cm-case-management.v1.yaml` + FR trace.  
3. Repository filter by visibility class + org scope.  
4. FE `/complaints/cm/cases` (atau route setara) — daftar sesuai principal.  
5. Tes matriks §3.  
6. Update `deploy/UAT_LAB_BATCH1_AGENT_10_MIN.md` (langkah “lihat Case saya”).
