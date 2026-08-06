# UX-CU-002 — Redesign "Create User" sebagai Application Authorization (Mode B / Enterprise SSO)

| Field | Value |
|---|---|
| Document ID | UX-CU-002 |
| Status | Draft — for review by CTO, Product Owner, Security Team, UI/UX Team |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Date | 2026-08-05 |
| Scope | Layar administrasi pengguna ECMP (`CreateUserModal`), **konteks Mode B (Enterprise SSO)** |
| Parent | ECMP-CONSTITUTION-001 → ADR-014 → ADR-015 → ADR-017 → ADR-018 |
| Supersedes (untuk konteks Mode B) | [UX-CU-001](UX-CU-001-Create-User-Redesign.md) §3.4–3.7, §8.2–8.3 (Requirement 3–6 versi Mode A) |
| Out of scope | Kode, kontrak API, skema basis data, redesign SSO/Identity Platform |

---

## 0. Catatan penyesuaian scope terhadap prompt

Sebelum eksekusi, prompt diperiksa terhadap repo (aturan kerja tetap: *repo menang atas
prompt*). Satu klaim di "Repository Context" perlu diluruskan, bukan diikuti mentah:

> Prompt menyatakan "The project uses Enterprise SSO. Authentication is NOT owned by ECMP"
> sebagai fakta tunggal. **Repo tidak berkata demikian secara tunggal.** Repo mengimplementasikan
> **dua mode** (CLAUDE.md §2): `ECMP_AUTH_MODE=dev` (Mode A, ECMP masih menyimpan
> `password_hash`, memvalidasi kebijakan password, dan memiliki endpoint
> `users:reset_password`) dan `ECMP_AUTH_MODE=jwt` (Mode B, SSO). ADR-014 mewajibkan
> kredensial lokal mati **hanya** di Mode B. Klaim prompt **benar untuk Mode B, tidak benar
> untuk Mode A yang aktif hari ini**.

**Cara ditangani:** dokumen ini dikerjakan persis sesuai instruksi prompt — redesign
diasumsikan berjalan **di bawah Mode B / Enterprise SSO**, field kredensial dihapus total,
tanpa mekanisme pengganti apa pun. Ini konsisten dengan target arsitektur ADR-014 dan tidak
melanggar apa pun di repo. Yang ditandai secara eksplisit di §3 (Repository Findings) adalah
konsekuensinya: dokumen ini **bukan** desain untuk Mode A yang berjalan hari ini, dan
implementasi nyata baru berlaku setelah `ECMP_AUTH_MODE=jwt` aktif dengan kontrak identitas
enterprise yang terverifikasi (CLAUDE.md §2 — kontrak saat ini "karangan ECMP, belum
diverifikasi").

Selain itu, satu istilah di daftar kepemilikan prompt — **"Application Authorization"** —
tidak ditemukan di ADR mana pun di repo. Istilah ini dipetakan ke padanan yang benar-benar
ada: **Role-Permission Matrix (ADR-008)** ditambah **Data Scope** (lihat §3.3). Tidak ada
konsep baru yang diciptakan untuk memenuhi istilah tersebut.

---

## 1. Executive Summary

`CreateUserModal` hari ini adalah artefak Mode A: ia menyimpan password, memvalidasi
kebijakan password, dan menyertakan `force_password_change`. Di bawah Mode B, seluruh
permukaan itu tidak boleh ada — ADR-014 menyatakan Forgot/Reset/Change Password *disabled*
dan local credential storage *prohibited* saat Enterprise Mode aktif.

Redesign ini mendefinisikan ulang layar sebagai **pemberian otorisasi**, bukan pembuatan
akun: administrator menetapkan Profil (dipilih dari direktori, bukan diketik), Unit, dan
Peran/Permission. Tidak ada satu keputusan pun di layar ini yang menyentuh kredensial.

Repo sudah memiliki infrastruktur **Data Scope** (`DataScopeResolver`, `EffectiveScope`,
`OrgUnitGuard` — SECMIG-P4) yang persis cocok untuk menegakkan "Unit terkunci pada cakupan
administrator", tetapi infrastruktur ini **belum disambungkan** ke endpoint `users:create`.
Ini bukan celah kecil — ini kerentanan privilege-escalation yang sudah dikonfirmasi di kode
berjalan (lihat §6, T-1).

---

## 2. Current Problems

| ID | Masalah | Bukti repo |
|---|---|---|
| CP-1 | Layar bernama "Create User" tetapi tidak membuat identitas — identitas sudah dipilih dari direktori sebelum form terisi | `CreateUserModal.tsx:185–201` (`applyCandidate`) |
| CP-2 | Field password, validasi kebijakan password, dan `force_password_change` masih ada di jalur pembuatan pengguna | `CreateUserModal.tsx:390–401`; `backend/app/modules/users/service.py:199,211` |
| CP-3 | Label "Cabang (Optional)" tidak netral dan tidak jujur — field ini tidak pernah benar-benar opsional | `frontend/messages/id.json:1833`; `service.py:150–163` (`_ensure_branch_for_role`) |
| CP-4 | Administrator dapat memilih **Unit mana pun** dari seluruh daftar cabang, tanpa dibatasi cakupannya sendiri | `CreateUserModal.tsx:427–461` — `fetchBranches(100)` tanpa filter cakupan aktor |
| CP-5 | Infrastruktur Data Scope sudah ada di repo tapi tidak dipakai endpoint `users:create` | Tidak ada `require_data_scope`/`resolve_effective_scope` di `backend/app/modules/users/router.py` atau `service.py` (dikonfirmasi grep) |

---

## 3. Repository Findings

Bagian ini memuat **hanya** yang terverifikasi dari pembacaan kode dan ADR, bukan asumsi.

### 3.1 Mode ganda — kepemilikan kredensial bergantung mode

| | Mode A (`ECMP_AUTH_MODE=dev`) | Mode B (`ECMP_AUTH_MODE=jwt`) |
|---|---|---|
| `password_hash` di `User` | Diisi (`backend/app/models/__init__.py:106`) | Tidak boleh diisi (ADR-014 §Mode B) |
| Validasi kebijakan password | `self._policy().validate(payload.password)` — `service.py:199` | Tidak berlaku |
| `force_password_change` | Ditegakkan (`auth_strategy.py:_load_force_password_change`) | N/A — SSO yang mengelola sesi |
| `OrgUnitGuard` (data scope) | **No-op** — `org_scope_enforcement_enabled()` mengembalikan `False` di dev (`org_unit_guard.py:51-53`) | **Aktif** |

Dokumen ini secara sadar mendesain untuk kolom **Mode B**. Efeknya pada Mode A dibahas di
§9 (Risks) — implementasi tidak boleh dijalankan di Mode A sebelum SSO cutover selesai.

### 3.2 Kredensial yang sudah dikonfirmasi milik ECMP hari ini (harus dihapus di Mode B)

- `User.password_hash`, `User.force_password_change` (`backend/app/models/__init__.py:106,110`)
- Endpoint `users:reset_password` (`backend/app/modules/users/router.py:197`,
  `service.py:460`, fungsi `admin_reset_password`)
- Modul `backend/app/modules/auth/password_helpers.py`, `login_protection.py`
- SEC-PWD-001 (`10 Security and Access Standards/ECMP_Identity_Password_Management_v1.0.md`)
  — didaftarkan ADR-014 sebagai permukaan yang wajib mati di Mode B

Prompt meminta hapus "Password, Confirm Password, Generate Password, Temporary Password".
Repo hanya memuat **satu** field password bernama `password` di `CreateUserModal.tsx:390`
(`minLength={8}`, hint `forcePasswordChange`). **Tidak ada** field "Confirm Password" atau
tombol "Generate Password" di kode saat ini — keduanya tidak pernah dibangun. Ini dicatat
di §9 (Removed Fields) sebagai perbedaan antara yang diminta dihapus dan yang benar-benar
ada di repo.

### 3.3 Infrastruktur otorisasi yang sudah ada dan relevan (Reuse, bukan Create New)

Repo sudah memiliki mekanisme scope yang persis menjawab Requirement 2, dibangun untuk Mode B:

| Komponen | File | Fungsi |
|---|---|---|
| `Principal.org_unit_id` | `backend/app/core/authorization/principal.py:18` | Identitas caller sudah membawa slot unit organisasi |
| `DataScopeResolver` / `EffectiveScope` | `backend/app/modules/iam/data_scope_resolver.py` | Meresolusi scope aktor dari `User → UserRole → Role → DataScope` |
| `ScopeType` (`GLOBAL`, `ORGANIZATION`, `BRANCH`, `SELF`, `CUSTOM`) | `backend/app/modules/iam/data_scope/models.py:16-23` | Kosakata tingkat scope — sudah memuat `ORGANIZATION` dan `BRANCH` |
| `OrgUnitGuard`, `org_scope_enforcement_enabled()` | `backend/app/core/authorization/org_unit_guard.py` | Penegakan scope pasca permission-check; aktif hanya di Mode B |
| `require_data_scope` / `check_data_scope` | `backend/app/core/authorization/data_scope_check.py` | Pola opt-in untuk endpoint membatasi hasil pada scope aktor |
| `_ensure_assignable_role` (UAT-020) | `backend/app/modules/users/service.py:108-120` | **Sudah ada**: mencegah admin memberi peran ≥ perannya sendiri |

**Temuan kunci:** endpoint `POST /users` (`users:create`) **tidak memanggil**
`require_data_scope` maupun `resolve_effective_scope` di mana pun. Mekanisme yang tepat
untuk Requirement 2 sudah dibangun untuk kasus lain (SECMIG-P4) tetapi belum disambungkan ke
jalur pembuatan pengguna. Requirement 2 di dokumen ini karena itu adalah **penyambungan**
komponen yang sudah ada, bukan arsitektur baru — sejalan dengan constraint "Do NOT create new
architecture".

### 3.4 Yang repo BELUM putuskan — jangan dikarang

- **Tidak ada entitas `Organization`** di `backend/app/models/`. Hanya `Branch` yang ada
  sebagai tabel nyata (`models/__init__.py:53`). `ScopeType.ORGANIZATION` ada sebagai *nilai
  enum*, tetapi tidak ada tabel `organizations` yang mengisinya. ADR-018 §14 mencatat ini
  eksplisit: fondasi ECMP saat ini **branch-centric**, sedangkan ADR-015 mensyaratkan tiga
  level (`organization_id` + `branch_id` + `department_id`), dan menutup celah itu adalah
  **prasyarat Mode B**, belum selesai.
  → **STOP.** Dokumen ini tidak mendefinisikan model "Organization" karena repo belum
  memilikinya. "Organization Mapping" di §10 didefinisikan pada level yang repo benar-benar
  punya (Branch/Unit), dengan catatan eksplisit bahwa perluasan ke `organization_id` penuh
  adalah keputusan terpisah yang menunggu ADR-018 diselesaikan.
- **Definisi formal "cakupan administrator"** (satu unit vs subtree vs daftar unit) belum
  ada sebagai keputusan produk. `DataScopeResolver` menyediakan mekanismenya
  (`get_branches()`, `has_global()`), tetapi *aturan bisnis* — peran administrator mana
  mendapat `ScopeType` apa — belum ditetapkan di `02 Business Rules` atau ADR manapun yang
  diperiksa.
  → **STOP.** Ditandai sebagai blocker di §16, bukan diasumsikan.
- **Kontrak identitas Mode B belum diverifikasi** (CLAUDE.md §2) — klaim `org_unit_id`,
  format, dan issuer nyata belum diperoleh dari pemilik Enterprise Platform.

---

## 4. UX Problems

| ID | Masalah | Dampak |
|---|---|---|
| UX-1 | Nama layar "Create User" menjanjikan pembuatan akun, padahal alur sudah memaksa pemilihan dari direktori terlebih dulu | Model mental administrator keliru sejak judul |
| UX-2 | Field password hadir di tengah alur otorisasi (peran, unit) — memecah konsentrasi administrator ke domain yang bukan tanggung jawabnya | Beban kognitif tidak perlu; risiko salah isi kebijakan password yang sebetulnya bukan keputusan ECMP |
| UX-3 | Label "Cabang (Optional)" tidak konsisten dengan perilaku sebenarnya (wajib/terlarang tergantung peran) | Administrator tidak percaya label; harus mencoba-coba |
| UX-4 | Daftar Unit menampilkan seluruh cabang tanpa mempertimbangkan siapa yang login | Administrator harus mencari secara visual di antara opsi yang sebagian besar tidak relevan/tidak berhak |
| UX-5 | Tidak ada indikasi di UI bahwa nilai Unit berasal dari sistem, bukan pilihan bebas | Administrator tidak tahu mengapa field terkunci bila dikunci tanpa penjelasan |

---

## 5. Business Problems

| ID | Masalah | Konsekuensi bisnis |
|---|---|---|
| BP-1 | Modul menjanjikan kapabilitas (manajemen kredensial) yang bukan model bisnis ECMP di Mode B | Ekspektasi pelanggan enterprise yang salah; pertanyaan audit "mengapa aplikasi domain menyimpan password?" |
| BP-2 | Tidak ada pemisahan eksplisit antara "siapa berhak login" (Identity Platform) dan "apa yang boleh dilakukan di ECMP" (Authorization) | Sulit menjelaskan batas tanggung jawab saat integrasi enterprise dinegosiasikan |
| BP-3 | Unit tidak ter-scope ke administrator → risiko operasional: pengguna ditempatkan di unit yang salah memengaruhi routing komplain dan KPI unit | Data KPI per-unit tidak dapat dipercaya sebagai sumber keputusan bisnis |

---

## 6. Security Problems

| ID | Temuan | Bukti | Severity |
|---|---|---|---|
| **T-1** | **Privilege escalation lintas unit.** Admin dapat menempatkan pengguna di unit mana pun di luar cakupannya sendiri; server hanya memvalidasi kecocokan kategori peran↔unit, bukan kepemilikan aktor atas unit tersebut. | `CreateUserModal.tsx:427-461` (client tidak filter); `service.py:150-163` `_ensure_branch_for_role` (server tidak cek cakupan aktor); `users:create` tidak memanggil `require_data_scope` | **High** |
| T-2 | Mekanisme penegakan scope yang sudah dibangun (`OrgUnitGuard`, `DataScopeResolver`) tidak diaktifkan untuk jalur pembuatan pengguna, sehingga celah T-1 tetap terbuka meski komponennya sudah ada | §3.3 | High |
| T-3 | Password field dan validasi kebijakan password masih berada di jalur yang sama dengan keputusan otorisasi — memperbesar permukaan yang harus diaudit setiap kali otorisasi direview | `service.py:199,211` | Medium (terselesaikan sepenuhnya di Mode B oleh Req 3) |
| T-4 | Tidak ada indikasi endpoint memeriksa apakah *role* yang diberikan berada dalam kategori yang boleh dikelola cakupan aktor (hanya peran ≥ level dicek, bukan peran × unit × cakupan aktor secara gabungan) | `_ensure_assignable_role` hanya membandingkan level peran, terpisah dari cek unit | Medium |

---

## 7. Redesign Goals

| ID | Goal | Selaras dengan |
|---|---|---|
| G-1 | Nol elemen kredensial di layar — tidak ada field, tidak ada tombol, tidak ada teks bantuan tentang password | Req 3, ADR-014 §Mode B |
| G-2 | Unit diturunkan dan ditegakkan dari cakupan aktor, disambungkan ke infrastruktur Data Scope yang sudah ada | Req 2, §3.3 (Reuse) |
| G-3 | Kosakata "Unit" netral organisasi, menggantikan "Cabang" di seluruh layar administrasi pengguna | Req 1 |
| G-4 | Form mencerminkan keputusan otorisasi yang sebenarnya: Profil (dipilih), Unit (diturunkan), Peran (dipilih) | Req 4 |
| G-5 | Setiap penegakan yang tampak di UI punya penegakan yang setara di server (least privilege ditegakkan, bukan disarankan) | Req 8 |
| G-6 | Tidak menambah satu pun kapabilitas identitas baru (tidak ada notifikasi, tidak ada activation link, tidak ada generator password) | Constraints prompt |

---

## 8. UI Changes

### 8.1 Rename

| Elemen | Sekarang | Menjadi | Alasan |
|---|---|---|---|
| Judul modal | "Create User" | **"Grant Application Access"** / **"Beri Akses Aplikasi"** | Menghapus klaim pembuatan identitas; selaras Req 4 |
| Tombol submit | "Create User" | **"Grant Access"** / **"Beri Akses"** | Konsisten dengan judul |
| Label field cabang | "Cabang (Optional)" | **"Unit"** | Req 1 |

### 8.2 Requirement 1 — mengapa "Unit" lebih generik dari "Cabang"

**Alasan UX.** "Cabang" mendeskripsikan *satu* bentuk struktur organisasi (jaringan cabang
fisik). "Unit" mendeskripsikan *fungsi* field ini — pembagian tanggung jawab organisasi —
tanpa menetapkan bentuknya. Administrator dari organisasi yang berstruktur Divisi atau
Departemen tidak perlu menerjemahkan istilah setiap kali membaca layar.

**Alasan bisnis.** ADR-018 §14 mencatat fondasi ECMP hari ini branch-centric namun kontrak
target (ADR-015) tiga level: `organization_id`, `branch_id`, `department_id`. "Unit" adalah
satu-satunya dari dua istilah yang tetap benar pada ketiga level itu; "Cabang" hanya benar
pada satu level (`branch_id`).

**Skalabilitas.** Karena "Unit" adalah label presentasi, bukan nama field kontrak, ia dapat
tetap dipakai tanpa perubahan saat model organisasi ECMP diperluas dari satu level (Branch)
menjadi tiga level (Organization/Branch/Department) sesuai ADR-018 §14. Kunci referensi
kontrak (`branch_id`, kelak `organization_id`/`department_id`) **tidak berubah** — ADR-015
tetap memilikinya.

**Batas perubahan.** Ini murni rename lapisan tampilan. Nama field API, nama kolom database,
dan nama klaim identitas tidak disentuh oleh dokumen ini.

### 8.3 Requirement 2 — Unit tidak dapat diedit

**Tampilan field:**

```
Unit
┌──────────────────────────────────────────────┐
│  Regional Jawa Barat                    🔒   │
└──────────────────────────────────────────────┘
Ditentukan otomatis dari cakupan otorisasi Anda.
```

Field tetap **terlihat** (memenuhi permintaan eksplisit: "Display the field. Lock the
field."), diberi indikator visual terkunci, dan tidak dapat menerima input dari administrator.

**Turunan nilai — memakai infrastruktur yang sudah ada (§3.3), bukan yang baru:**

1. Server meresolusi `EffectiveScope` aktor via `DataScopeResolver.resolve_scopes()`.
2. Bila `EffectiveScope.has_global()` — aktor berwenang lintas unit; field Unit menjadi
   pemilih terbatas pada unit yang valid untuk peran target (bukan seluruh daftar).
3. Bila scope aktor berisi `BRANCH` dengan satu nilai — Unit dikunci ke nilai itu.
4. Bila scope aktor tidak dapat diresolusi (tidak ada entri Data Scope untuk peran aktor) —
   **tolak tindakan**, jangan jatuh ke nilai default.

Poin 2–4 memerlukan keputusan bisnis yang belum ada di repo (§3.4, blocker) — DataScopeResolver
menyediakan mekanismenya, tetapi peta "peran administrator → ScopeType apa" harus ditetapkan
Product Owner sebelum implementasi.

Karena UI **tidak pernah** menjadi kontrol keamanan yang berdiri sendiri, resolusi harus
terjadi di server; UI hanya menampilkan hasilnya.

---

## 9. Removed Fields

| Field/elemen yang diminta dihapus | Status di repo | Tindakan |
|---|---|---|
| Password | **Ada** — `CreateUserModal.tsx:390-401`, `minLength={8}` | Hapus seluruh input, `onChange`, dan state `form.password` |
| Confirm Password | **Tidak ada** di kode saat ini | Tidak ada yang perlu dihapus — dicatat agar tidak diasumsikan pernah dibangun |
| Generate Password (tombol) | **Tidak ada** di kode saat ini | Sama seperti di atas |
| Temporary Password | Direpresentasikan sebagai `force_password_change` (bukan field UI terpisah, hanya *hint* teks di bawah password — `t("forcePasswordChange")`) | Hapus hint bersamaan dengan field password |
| Credential Section | Tidak ada seksi terpisah — password menyatu dalam form utama | Tidak ada seksi untuk dihapus; cukup hapus field individual di atas |
| Email Credential Section | **Tidak ada** di kode saat ini | Tidak ada yang perlu dihapus |

**Field yang TETAP ada** (dikonfirmasi bukan milik Identity Platform — Repository Findings
§3.2–3.3):

| Field | Kepemilikan |
|---|---|
| Pencarian direktori / pemilihan orang | ECMP — titik masuk registrasi otorisasi |
| Nama, Username, Email (read-only, dari direktori) | ECMP menampilkan; Identity Platform memiliki nilainya |
| Unit | ECMP — Authorization scope |
| Peran (Role) | ECMP — ADR-008 Role-Permission SoT |
| Status aktif (`is_active`) | ECMP — status keanggotaan pengguna di modul |

Backend: field yang dihapus dari **payload pembuatan pengguna** adalah `password`.
`force_password_change` dan `password_hash` menjadi tidak relevan pada jalur ini karena
`User.password_hash` tidak lagi diisi ECMP di Mode B (ADR-014).

---

## 10. Updated Business Rules

Hanya aturan yang berada dalam kepemilikan ECMP (User Profile, Organization/Unit, Role,
Permission) — tidak ada aturan Identity Platform.

| ID | Aturan | Sumber |
|---|---|---|
| BR-CU-01 | ECMP tidak membuat identitas; pemberian akses hanya berlaku untuk orang yang sudah dikenali direktori enterprise. | Req 4; §3.2 |
| BR-CU-02 | Nama, username, email berasal dari direktori dan tidak dapat diubah dari layar ini. | Kondisi kode saat ini, `CreateUserModal.tsx:363-389` |
| BR-CU-03 | Unit pengguna baru ditentukan oleh cakupan otorisasi administrator, diresolusi via `DataScopeResolver`, bukan dipilih bebas. | §8.3; reuse §3.3 |
| BR-CU-04 | Administrator dengan `EffectiveScope` bertipe `BRANCH` tunggal tidak dapat memberikan akses ke unit lain. | §8.3 poin 3 |
| BR-CU-05 | Peran ber-scope unit wajib memiliki Unit; peran kantor pusat wajib tidak memiliki Unit. | Sudah ada — `service.py:150-163` |
| BR-CU-06 | Administrator tidak dapat memberikan peran yang setara atau lebih tinggi dari perannya sendiri. | Sudah ada — UAT-020, `service.py:108-120` |
| BR-CU-07 | Bila cakupan otorisasi administrator tidak dapat diresolusi, pemberian akses ditolak (fail-closed). | §3.4; ADR-018 §Fail-Closed |
| BR-CU-08 | Setiap pemberian akses menghasilkan peristiwa audit: aktor, subjek, peran, unit, waktu. | Req 8; least privilege |

**Tidak didefinisikan** (repo silent — lihat §3.4 dan §16): pemetaan resmi peran administrator
→ `ScopeType`, dan model `Organization` di luar `Branch`. Keduanya adalah keputusan Product
Owner / ADR follow-up, bukan aturan yang boleh dikarang di sini.

---

## 11. Authorization Review

Fokus murni tanggung jawab ECMP — Authentication/SSO tidak direview di sini.

### 11.1 Model saat ini vs target

| Dimensi | Saat ini | Target (dokumen ini) |
|---|---|---|
| Permission check | `require_permissions("users:create")` — ya, sudah berjalan | Tidak berubah |
| Scope check | **Tidak ada** pada endpoint `users:create` | `require_data_scope`/`resolve_effective_scope` disambungkan, hasil diterapkan sebagai batas pilihan Unit + validasi server |
| Role-hierarchy check | Ada (`_ensure_assignable_role`, UAT-020) | Tidak berubah — sudah memenuhi least privilege untuk dimensi peran |
| Kombinasi peran × unit × cakupan aktor | **Tidak diperiksa gabungan** — masing-masing dicek terpisah | Ketiganya wajib konsisten sebelum commit |

### 11.2 Least Privilege — celah spesifik

Least privilege saat ini hanya ditegakkan pada satu sumbu (peran ≥ peran aktor ditolak).
Sumbu kedua — **unit** — tidak ditegakkan sama sekali pada level yang setara. Administrator
ber-hak-akses "users:create" memiliki hak implisit yang lebih luas dari yang seharusnya:
ia dapat memberi akses ke unit mana pun, bukan hanya unit dalam cakupannya. Ini melanggar
prinsip least privilege pada dimensi organisasi, meski dimensi peran sudah benar.

### 11.3 Privilege Escalation — jalur yang dikonfirmasi

Jalur T-1 (§6) adalah privilege escalation *by data placement*, bukan privilege escalation
klasik (menaikkan peran sendiri). Efeknya setara: administrator dapat menghasilkan pengguna
dengan hak akses data (routing komplain, visibilitas antrean, KPI) di unit yang bukan haknya
untuk dikelola.

### 11.4 Unit Scope Validation

Belum ada. §8.3 dan §3.3 menetapkan mekanismenya (reuse `DataScopeResolver`); §3.4 menetapkan
keputusan bisnis yang masih hilang sebelum mekanisme itu dapat dikonfigurasi dengan benar.

### 11.5 Role Assignment Validation

Sudah memadai untuk dimensi peran (UAT-020). Rekomendasi: satukan pemeriksaan peran dan unit
dalam satu langkah validasi server agar kombinasi yang tidak konsisten (mis. peran valid untuk
unit A tapi aktor hanya berwenang di unit B) ditolak sebagai satu keputusan, bukan dua
pemeriksaan independen yang bisa lolos secara kebetulan.

---

## 12. Information Architecture Impact

| Perubahan | Detail |
|---|---|
| Kosakata | "Cabang" → "Unit" di seluruh layar administrasi pengguna (label presentasi saja) |
| Nama layar/aksi | "Create User" → "Grant Application Access" — memindahkan layar secara konseptual dari kategori "manajemen identitas" ke "manajemen otorisasi" |
| Struktur form | Dari 7 field datar menjadi 2 blok: **Profil** (dari direktori, read-only) dan **Otorisasi** (Unit turunan + Peran dipilih) |
| Objek informasi yang hilang | "Password", "Temporary Password" dihapus dari kosakata layar ini sepenuhnya |
| Dampak ke IA-001 | Entri *Unit Scope* perlu ditambahkan sebagai Information Object; entri kredensial (bila ada) dihapus dari cakupan layar ini |
| Dampak ke NAV-001 | Label navigasi menuju layar ini berubah mengikuti §8.1 |

Klaim identitas (`branch_id`, kelak `organization_id`) di lapisan kontrak **tidak berubah** —
IA hanya berubah di lapisan presentasi dan pengelompokan.

---

## 13. User Journey

| # | Langkah | Yang terlihat | Yang diputuskan administrator |
|---|---|---|---|
| 1 | Buka "Beri Akses Aplikasi" | Panel pencarian direktori | — |
| 2 | Cari & pilih orang | Profil terisi read-only (Nama, Username, Email) | Orang yang benar |
| 3 | Sistem menurunkan Unit | Field Unit terisi, terkunci, dengan penjelasan sumber | — |
| 4 | Pilih Peran | Daftar peran yang boleh diberikan aktor (sudah difilter UAT-020) | **Satu-satunya keputusan otorisasi tersisa** |
| 5 | Konfirmasi | Ringkasan: Profil + Unit + Peran | — |
| 6 | Server memvalidasi & mencatat | Status "Akses diberikan" + jejak audit | — |

Tidak ada langkah yang menyinggung password, email kredensial, atau aktivasi — sepenuhnya di
luar cakupan layar ini per Req 3–4 dan constraints prompt.

---

## 14. ASCII Process Flow

### 14.1 Alur lama (dihapus)

```
Create User
     │
     ▼
Create Password ─── administrator mengetik password
     │
     ▼
Save Password ────── password_hash disimpan ECMP
     │
     ▼
User Login ────────── ECMP memvalidasi password lokal
```

### 14.2 Alur baru — Grant Application Access (Mode B)

```
┌───────────────────────────────────────────────────────────┐
│ ADMINISTRATOR (terautentikasi via Enterprise SSO)          │
└───────────────────────────┬────────────────────────────────┘
                            │  buka "Beri Akses Aplikasi"
                            ▼
              ┌───────────────────────────┐
              │ Resolusi EffectiveScope   │
              │ aktor (DataScopeResolver) │
              └────────────┬──────────────┘
                           │
              dapat diresolusi?
                 │                │
              TIDAK              YA
                 │                │
                 ▼                ▼
     ┌─────────────────────┐  ┌────────────────────────────┐
     │ TOLAK (fail-closed, │  │ Cari orang di direktori     │
     │ BR-CU-07)           │  │ enterprise                  │
     └─────────────────────┘  └────────────┬─────────────────┘
                                           │ pilih orang
                                           ▼
                         ┌──────────────────────────────────┐
                         │ Profil terisi READ-ONLY           │
                         │ Nama · Username · Email           │
                         └────────────┬───────────────────────┘
                                     ▼
                         ┌──────────────────────────────────┐
                         │ UNIT = f(EffectiveScope aktor)    │
                         │ 🔒 TERKUNCI, ditampilkan          │
                         └────────────┬───────────────────────┘
                                     ▼
                         ┌──────────────────────────────────┐
                         │ Administrator memilih PERAN       │
                         │ (difilter: peran ≤ peran aktor,   │
                         │  UAT-020)                         │
                         └────────────┬───────────────────────┘
                                     ▼
                         ┌──────────────────────────────────┐
                         │ SERVER — validasi gabungan        │
                         │  · unit diturunkan, bukan diterima│
                         │    dari klien                     │
                         │  · peran × unit konsisten          │
                         │  · peran ≤ peran aktor             │
                         └────────────┬───────────────────────┘
                                     │
                              valid? ── TIDAK ──▶ TOLAK + audit
                                     │
                                    YA
                                     ▼
                         ┌──────────────────────────────────┐
                         │ Otorisasi ECMP dibuat:            │
                         │ Profil × Unit × Peran × Permission│
                         │ TIDAK ADA kredensial dibuat/diubah│
                         └────────────┬───────────────────────┘
                                     ▼
                         ┌──────────────────────────────────┐
                         │ AUDIT: aktor · subjek · peran ·   │
                         │ unit · waktu                      │
                         └────────────────────────────────────┘

Login pertama pengguna sepenuhnya di luar diagram ini — dilakukan lewat Enterprise SSO,
tidak melibatkan ECMP.
```

---

## 15. Security Considerations

### 15.1 Prinsip yang mengikat

1. **UI bukan kontrol keamanan.** Penguncian field Unit di UI wajib disertai penegakan
   server yang setara (§8.3, §11.4) — tanpa itu, T-1 tetap terbuka meski tampak sudah beres.
2. **Nilai turunan tidak boleh berasal dari klien.** Unit dihitung server dari
   `EffectiveScope`, bukan diterima dari payload permintaan.
3. **Fail-closed.** Cakupan aktor yang tidak dapat diresolusi menolak tindakan
   (BR-CU-07) — tidak ada nilai default.
4. **Reuse sebelum create.** Penegakan scope memakai `DataScopeResolver`/`OrgUnitGuard` yang
   sudah ada, bukan mekanisme baru — mengurangi permukaan yang harus diaudit ulang.
5. **Tidak ada perluasan permukaan identitas.** Sesuai constraints prompt, dokumen ini tidak
   menambah satu pun kapabilitas kredensial, notifikasi, atau aktivasi.

### 15.2 Kebutuhan audit

Setiap pemberian akses mencatat: identitas aktor, `EffectiveScope` aktor pada saat tindakan,
subjek, peran yang diberikan, unit yang ditetapkan, hasil validasi, dan stempel waktu. Tidak
ada kredensial yang tercatat karena tidak ada kredensial yang diproses layar ini.

---

## 16. Risks

| ID | Risiko | Dampak | Mitigasi |
|---|---|---|---|
| R-1 | Field Unit dikunci hanya di UI, server tetap menerima nilai dari payload | **Kritis** — T-1 tetap terbuka | Penegakan server via `DataScopeResolver` adalah syarat selesai, bukan opsi |
| R-2 | Dokumen ini dijalankan sebagai desain untuk Mode A (masih aktif hari ini) | Tinggi — menghapus field password akan mematahkan Mode A yang masih butuh kredensial lokal | Dokumen eksplisit berlaku untuk Mode B; Mode A tetap memakai UX-CU-001 sampai cutover SSO |
| R-3 | Pemetaan "peran administrator → ScopeType" belum diputuskan, implementasi berjalan dengan asumsi yang salah | Tinggi | §3.4/§16.1 — blocker wajib diputuskan Product Owner sebelum implementasi |
| R-4 | Model `Organization` diasumsikan ada padahal repo hanya punya `Branch` | Sedang — desain menabrak ADR-018 §14 yang menyatakan celah ini belum ditutup | §3.4 — dokumen ini tidak mendefinisikan Organization; ditandai open decision |
| R-5 | Kontrak identitas Mode B (klaim `org_unit_id` dsb.) berbeda dari asumsi | Tinggi | CLAUDE.md §2 — jangan implementasikan sebelum kontrak diverifikasi ke pemilik Enterprise Platform |

### 16.1 Blocker yang harus diputuskan sebelum implementasi

1. Pemetaan resmi peran administrator → `ScopeType` (`GLOBAL`/`BRANCH`/`ORGANIZATION`/
   `CUSTOM`) belum ada sebagai keputusan produk.
2. Model organisasi tiga level (ADR-018 §14) belum ditutup — "Unit" hari ini hanya dapat
   dipetakan ke `Branch`.
3. Kontrak identitas Mode B belum diverifikasi ke pemilik Enterprise Platform (CLAUDE.md §2).

Tanpa ketiganya, §8.3/§11.4 dapat didokumentasikan sebagai desain tetapi **tidak dapat**
diimplementasikan dengan aman.

---

## 17. Expected Benefits

| Pemangku kepentingan | Manfaat |
|---|---|
| **CTO** | Layar administrasi pengguna selaras penuh dengan ADR-014 target; nol permukaan kredensial baru untuk dibongkar saat SSO cutover |
| **Product Owner** | Batas tanggung jawab ECMP vs Identity Platform menjadi eksplisit dan dapat dikomunikasikan ke pelanggan enterprise |
| **Security** | Celah privilege-escalation lintas unit (T-1) tertutup memakai infrastruktur yang sudah diaudit sebelumnya (SECMIG-P4), bukan komponen baru yang belum teruji |
| **UI/UX** | Form dua keputusan (Peran; Unit turunan otomatis), nol field yang berada di luar tanggung jawab administrator |

---

## 18. Final Recommendation

1. **Implementasikan Requirement 1 (rename "Unit") segera** — murah, tidak berisiko, berlaku
   di kedua mode karena murni lapisan presentasi.
2. **Implementasikan Requirement 2 dengan menyambungkan `DataScopeResolver`/`OrgUnitGuard`
   yang sudah ada** ke endpoint `users:create` — ini menutup T-1, kerentanan yang sudah
   dikonfirmasi aktif di kode. **Tunggu** keputusan Product Owner atas blocker §16.1 poin 1
   sebelum menuliskan aturan pemetaan scope.
3. **Requirement 3 (hapus field password) hanya berlaku saat `ECMP_AUTH_MODE=jwt` aktif.**
   Jangan hapus field password dari Mode A sebelum SSO cutover selesai — itu akan mematahkan
   satu-satunya jalur login yang berfungsi hari ini. Untuk Mode A, rujuk UX-CU-001 §3.4–3.6.
4. **Requirement 6/7/8 (business rules, authorization review) berlaku sebagai target
   desain sekarang**, karena tidak bergantung pada mode — Role-Permission dan Data Scope
   adalah milik ECMP di kedua mode.
5. **Jangan mulai implementasi apa pun sebelum tiga blocker §16.1 diputuskan.** Ini bukan
   detail teknis — tanpa pemetaan scope resmi, "Unit terkunci" akan dikunci ke nilai yang
   salah, dan tanpa kontrak identitas terverifikasi, seluruh asumsi `org_unit_id` berisiko
   perlu ditulis ulang.

> *Future Work — Di luar ruang lingkup Complaint Management Module: desain ulang Enterprise
> SSO, Identity Platform, Notification Service, Activation Link. Tidak dibahas di dokumen ini
> sesuai instruksi.*
