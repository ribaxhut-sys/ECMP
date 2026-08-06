# UX-CU-003 — Redesign "Create User" sebagai Application Authorization

| Field | Value |
|---|---|
| Document ID | UX-CU-003 |
| Status | Draft — for review by CTO, Product Owner, UI/UX Team, Security Team, Enterprise Architecture Review |
| Lifecycle | Draft → Reviewed → Approved → Baseline → Locked |
| Date | 2026-08-05 |
| Scope | Layar administrasi pengguna ECMP (`CreateUserModal`) — domain ECMP saja |
| Batas domain | **LOCKED** (keputusan arsitektur, 2026-08-05) — lihat §2. Enterprise memiliki Identity, Authentication, User Management, Enterprise Directory, Login, Password, MFA, dan User Lifecycle. ECMP memiliki **hanya** Application Authorization. |
| Predecessor | [UX-CU-001](UX-CU-001-Create-User-Redesign.md) (Mode A), [UX-CU-002](UX-CU-002-Create-User-Authorization-Redesign.md) (Mode B, draft desain) |
| Status implementasi | Requirement 1, 2, dan sebagian 4–8 **sudah diimplementasikan** di kode saat ini (lihat §9, §10, §16). Requirement 3 **belum** — dilaporkan sebagai *repository gap*, bukan diasumsikan selesai. |
| Out of scope | Kode, kontrak API, skema basis data. Kapabilitas Enterprise: Identity · SSO · Directory · Authentication · Enterprise APIs · User Management · Password · Email · MFA · Login · User Lifecycle. |

---

## 1. Executive Summary

Batas domain sudah **LOCKED**: Enterprise memiliki seluruh Identity dan Authentication; ECMP memiliki **hanya** Application Authorization. Dengan batas itu, pertanyaan yang tersisa untuk ECMP hanya satu: **setelah SSO berhasil, apa yang ECMP putuskan?** Jawabannya bukan "siapa orang ini" (sudah selesai di Enterprise), melainkan "apa yang orang ini boleh lakukan di dalam ECMP" — peran apa, unit mana, permission apa, dan apakah akses modul aktif.

**Makna bisnis resmi "Create User":**

> **"Create User" berarti memberikan akses aplikasi ECMP kepada Enterprise User yang sudah ada. Ia TIDAK membuat identitas Enterprise, TIDAK membuat akun login, dan TIDAK menerbitkan kredensial apa pun.**

Setiap kata di layar, dokumen, dan pelatihan yang menyiratkan ECMP membuat akun login wajib diganti mengikuti definisi ini. Layar hari ini belum memenuhinya: ia masih memuat field password dan namanya masih menjanjikan pembuatan akun. Redesign ini menetapkan ulang layar sebagai **Application Authorization** — registrasi Enterprise User ke ECMP, ditambah penetapan Peran, Unit, dan Permission; tidak lebih.

Dua dari enam requirement (rename Unit, kunci Unit ke cakupan administrator) **sudah dikodekan** di repo saat ini, terverifikasi lewat pembacaan langsung `CreateUserModal.tsx` dan `backend/app/modules/users/router.py`. Satu requirement (hapus seluruh field otentikasi) **belum bisa dikodekan** karena bertabrakan dengan gerbang keamanan yang sudah ada dan didokumentasikan (ADR-014 / audit K-3) — ini dilaporkan di §5 dan §11 sebagai *repository gap*, bukan diinvestasikan sebagai asumsi selesai.

---

## 2. Business Boundary — **LOCKED**

```
┌─────────────────────────────── ENTERPRISE (di luar ECMP) ───────────────────────────────┐
│                                                                                            │
│  Identity · Authentication · SSO · Login · Password · MFA ·                              │
│  User Management · Enterprise Directory · User Lifecycle                                 │
│                                                                                            │
│  Sudah bekerja dan menghasilkan: Enterprise User terautentikasi dengan                    │
│  identitas yang dipercaya.                                                                │
└─────────────────────────────────────────┬──────────────────────────────────────────────┘
                                            │  identitas terpercaya (bukan kredensial)
                                            ▼
┌─────────────────────────────────── ECMP (domain ini) ───────────────────────────────────┐
│                                                                                            │
│  Application Authorization — dan hanya itu:                                              │
│  Register Enterprise User ke ECMP → Assign Role → Assign Unit →                          │
│  Assign Permission → Enable/Disable ECMP Access                                          │
│                                                                                            │
│  ECMP tidak pernah menerbitkan, menyimpan, atau menyampaikan kredensial.                  │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

Batas ini **terkunci** oleh keputusan arsitektur dan konsisten dengan repo: ADR-014 (tabel
kepemilikan §154 — Enterprise Platform memiliki *Authentication, SSO, User Directory,
Password/MFA, Session*; ECMP memiliki *complaint lifecycle* dan *Complaint Roles*) dan ADR-017
(Enterprise Entitlement adalah **module-admission grant**, dievaluasi di Identity Adapter
**sebelum** Complaint Roles mapping — bukan sesuatu yang ECMP terbitkan).

Batas ini dinyatakan sekali di sini dan **tidak diulang** di bagian lain dokumen; §3, §4, dan
§11 hanya merujuk kembali ke sini.

---

## 3. ECMP Responsibility

| Kapabilitas | Bukti di repo |
|---|---|
| Registrasi pengguna enterprise ke profil lokal ECMP | `User` model — `username`, `email`, `full_name` (`backend/app/models/__init__.py:83-121`) |
| Assign Role | `User.role_id` + `UserRole` junction, disinkronkan lewat `ensure_user_role` (`users/repository.py:87`) |
| Assign Unit | `User.branch_id`, ditegakkan lewat `_ensure_branch_for_role` (`users/service.py:150-163`) |
| Assign Permission | Role-Permission Matrix — **ADR-008, SoT = ECMP/Core Platform** |
| Enable/Disable ECMP Access | `User.is_active`, endpoint `PATCH /users/{id}/status` (`users/router.py:170-183`) |
| Validasi least-privilege pada assignment | `_ensure_assignable_role` (UAT-020) — admin tidak dapat memberi peran ≥ perannya sendiri |
| Validasi scope Unit terhadap admin | `OrgUnitResolver` + `enforce_org_scope` (SECMIG-P4) — **sudah disambungkan** ke `users:create` |

Tidak satu pun dari kapabilitas ini menyentuh kredensial atau autentikasi.

**ECMP tidak melakukan:** membuat Enterprise User · mengautentikasi pengguna · mengelola
kredensial · mengubah identitas Enterprise.

### 3.1 Sumber data Enterprise User

Informasi Enterprise User berasal dari **Enterprise Directory melalui Enterprise API**. Aturan
yang mengikat:

1. ECMP **hanya mencari** Enterprise User yang sudah ada — tidak pernah membuat.
2. ECMP **tidak pernah mengubah** identitas Enterprise User.
3. ECMP **tidak pernah menduplikasi** master data Enterprise. Yang disimpan hanyalah
   **referensi** ke Enterprise User, bukan salinan direktori.

> **Status repo:** integrasi Enterprise API **belum ada**. Lihat repository gap §5.1.

### 3.2 Data otorisasi yang ECMP simpan

ECMP menyimpan **hanya** data otorisasi yang dibutuhkan aplikasi:

| Data | Wujud di repo |
|---|---|
| Enterprise User Reference | `User.username` (ID pegawai 16 digit) — kunci rujukan ke direktori |
| Role | `User.role_id` + `UserRole` |
| Unit | `User.branch_id` |
| Permission | Diturunkan dari Role (ADR-008) — tidak disimpan per pengguna |
| Status | `User.is_active` |

Tidak ada satu pun yang berkaitan dengan autentikasi. Field `password_hash` dan
`force_password_change` yang masih ada di model adalah sisa Mode A — bagian dari repository
gap §5.2, bukan bagian dari desain ini.

---

## 4. Enterprise Responsibility

Daftar kapabilitas Enterprise sudah ditetapkan di §2 dan tidak diulang di sini. Satu hal yang
**tidak** tercakup daftar itu dan sering tertukar dengan tanggung jawab ECMP:

**Entitlement (ADR-017)** — keputusan *"apakah subjek ini diizinkan masuk modul ECMP sama
sekali"* — dimiliki **Enterprise**, dievaluasi di Identity Adapter **sebelum** ECMP memetakan
Peran apa pun.

Konsekuensinya: **"Enable/Disable ECMP Access"** yang ECMP miliki (`User.is_active`) adalah
toggle **lokal ECMP** yang mengasumsikan Entitlement Gate Enterprise sudah lolos. Ia bukan
pengganti Entitlement, dan layar ini tidak boleh diberi label seolah-olah ia adalah keputusan
admisi tingkat enterprise.

---

## 5. Current UX Problems

Dibaca langsung dari `CreateUserModal.tsx` **setelah** implementasi Requirement 1 dan 2
(lihat §9) — bukan dari versi lama.

| ID | Masalah | Status |
|---|---|---|
| UX-1 | Nama layar "Create User" masih menjanjikan pembuatan akun, padahal alur memaksa pemilihan dari direktori dan Unit sudah diturunkan otomatis | Belum direname — lihat §18 |
| UX-2 | Field password (`CreateUserModal.tsx:391-402`) masih berdiri di tengah alur otorisasi murni (Peran, Unit) | **Repository gap §5.2** |
| UX-3 | Tidak ada indikasi eksplisit di layar bahwa "membuat" di sini berarti "memberi akses", bukan "membuat akun" | Belum ada penjelasan on-screen |
| UX-4 | Pencarian pengguna berjalan di atas seed JSON lokal, bukan Enterprise Directory | **Repository gap §5.1** |

### 5.1 Repository gap — integrasi Enterprise Directory belum ada

Pencarian Enterprise User hari ini **tidak** membaca Enterprise API. Ia membaca berkas seed
statis yang ikut dibundel ke frontend: `frontend/src/features/users/data/moduleUserCandidates.json`,
dimuat lewat `import candidatesJson from "./data/moduleUserCandidates.json"`
(`moduleUserCandidates.ts:1`). Isinya data lab (`"cohort": "DIRECTORY_POOL"`, email
`@lab.ecmp.local`) dengan field: `username`, `displayName`, `email`, `homeBranchCode`,
`homeBranchName`, `region`, `cohort`.

Dua konsekuensi yang harus dinyatakan terbuka:

1. **Prinsip "jangan duplikasi master data Enterprise" hari ini belum terpenuhi** — seed itu
   secara teknis adalah salinan lokal data direktori. Ia dapat diterima sebagai fixture lab,
   tetapi bukan desain target.
2. **Field `Department`, `Position`, dan `Organization` tidak ada di repo mana pun** —
   tidak di seed direktori, tidak di model `User`, tidak di tipe frontend. Ketiganya
   didokumentasikan di §10 sebagai *target read-only* yang datang bersama Enterprise API,
   **bukan** sebagai field yang ada hari ini. Tidak ada field yang dikarang untuk menutup
   celah ini.

> **Integrasi Enterprise API akan diimplementasikan hanya setelah dukungan repository dan
> milestone implementasi resmi tersedia.** Sampai saat itu, dokumen ini tidak boleh dibaca
> sebagai klaim bahwa integrasi Enterprise Directory sudah ada.

### 5.2 Repository gap — field password belum dapat dihapus

Field password tidak dapat dihapus tanpa mengubah gerbang keamanan yang sudah ada dan
terdokumentasi. `UserCreateRequest.password` bersifat wajib (`users/schemas.py:21`,
`min_length=8`, tanpa default), dan endpoint `create_user` bergantung pada
`require_local_credential_auth` (`local_credential_auth.py`), yang dalam docstring-nya sendiri
menyatakan: *"password login / forgot / reset / change / admin reset / **user create** /
user update-password must fail closed"* ketika kredensial lokal dinonaktifkan, dan *"Mode B
unlock remains gated by **Architecture Board (C-7 / C-B6-1)**."*

Menghapus field ini berarti mengubah kontrol keamanan yang keputusannya secara eksplisit
diserahkan ke Architecture Board — bukan keputusan yang boleh diambil lewat redesign UX.
Ditandai **STOP**, dilaporkan di §11 dan §18, tidak diasumsikan selesai.

---

## 6. Business Problems

| ID | Masalah |
|---|---|
| BP-1 | Nama modul ("Create User") tidak sesuai model bisnis yang sudah disepakati — ECMP tidak pernah menjadi pemilik identitas, tapi namanya menyiratkan sebaliknya |
| BP-2 | Tanpa pemisahan eksplisit "Grant Access" vs "Create Account", tim non-teknis (Product Owner, auditor enterprise) sulit memverifikasi bahwa ECMP benar-benar tidak menyimpan kredensial hanya dari membaca UI |
| BP-3 | `User.is_active` (toggle lokal ECMP) berisiko disalahpahami sebagai representasi Entitlement Enterprise (ADR-017) bila layar tidak menjelaskan bedanya |

---

## 7. Security Problems

| ID | Temuan | Status |
|---|---|---|
| T-1 (historis) | Administrator dapat menempatkan pengguna di Unit di luar cakupannya sendiri — privilege escalation lintas unit | **Sudah ditutup** — `enforce_org_scope` disambungkan ke `users:create`; lihat §16 |
| T-2 | Field password yang masih ada memperbesar permukaan yang harus diaudit setiap kali otorisasi direview, meski secara fungsional terpisah dari keputusan Peran/Unit | Terbuka — terikat repository gap §5 |
| T-3 | Tidak ada indikasi bahwa `is_active` ≠ Entitlement enterprise; risiko kesalahpahaman audit (BP-3) | Terbuka — masalah komunikasi UI, bukan celah teknis |

---

## 8. Design Goals

| ID | Goal |
|---|---|
| G-1 | Layar dan aksi dinamai sesuai fungsi sebenarnya: pemberian otorisasi, bukan pembuatan akun |
| G-2 | Unit selalu berupa nilai turunan yang ditegakkan server — tidak pernah pilihan bebas |
| G-3 | Kosakata "Unit" netral organisasi |
| G-4 | Setiap field di layar dapat dijawab dengan jelas: "ini milik ECMP" atau "ini bukan" |
| G-5 | Field otentikasi dihapus sepenuhnya **begitu gerbang K-3/Architecture Board memberi jalan** — dilacak sebagai item terbuka, bukan diselesaikan diam-diam |
| G-6 | Tidak ada satu pun kapabilitas Enterprise (SSO, Identity, Directory, Password, dst.) yang didesain ulang atau ditiru ECMP |

---

## 9. Screen Redesign

### 9.1 Rename (Requirement 1) — **sudah diimplementasikan**

| Elemen | Sebelumnya | Sekarang (kode saat ini) |
|---|---|---|
| Label field | "Cabang (Optional)" | **"Unit"** (atau "Unit — Tidak berlaku" untuk peran kantor pusat) — `CreateUserModal.tsx:422` |
| Kunci terjemahan | `branchOptional`, `branchRequired`, `headOfficeFixed`, `selectBranch`, `noBranch` | `unit`, `unitNotApplicable`, `unitDerivedHint`, `unitHeadOfficeHint`, `unitScopeMissing` (`frontend/messages/{id,en}.json`, namespace `users`) |

**Alasan UX.** "Cabang" adalah *jawaban* untuk satu bentuk struktur organisasi (jaringan
cabang fisik). "Unit" adalah *pertanyaan* yang benar — "bagian organisasi mana" — tanpa
menetapkan bentuknya. Administrator dari organisasi berstruktur Divisi, Departemen, atau
Region tidak perlu menerjemahkan istilah setiap kali membaca layar.

**Alasan bisnis.** ECMP ditujukan untuk banyak organisasi dengan model struktur berbeda.
Istilah yang salah pada layar administrasi menimbulkan biaya nyata: pelatihan yang harus
mengoreksi kosakata, dan SOP pelanggan yang tidak cocok dengan layar.

**Mengapa "Unit" adalah terminologi enterprise yang lebih baik.** ADR-018 §14 mencatat
fondasi ECMP saat ini branch-centric, sementara ADR-015 mensyaratkan tiga level referensi
(`organization_id`, `branch_id`, `department_id`). "Unit" adalah satu-satunya istilah dari dua
kandidat yang tetap benar pada ketiga level itu; "Cabang" hanya benar pada satu level. Ini
murni rename lapisan presentasi — kunci referensi (`branch_id`, kelak `organization_id`)
tidak berubah, tetap milik ADR-015.

### 9.2 Kunci Unit (Requirement 2) — **sudah diimplementasikan**

Field Unit di `CreateUserModal.tsx:420-433` sekarang adalah `<Input>` read-only (bukan
`<Select>`), nilainya dihitung dari `useAuth().user.branchId` — profil administrator yang
sedang login — bukan dari state form yang bisa diubah. Tidak ada `onChange` untuknya sama
sekali; field ini secara struktural tidak dapat ditulis, bukan sekadar "disabled".

```
Unit
┌──────────────────────────────────────────────┐
│  Regional Jawa Barat                          │
└──────────────────────────────────────────────┘
Ditentukan otomatis dari cakupan otorisasi Anda.
```

Penegakan sisi server: `backend/app/modules/users/router.py` sekarang meresolusi
`Branch.code` dari `branch_id` yang dikirim, lalu memanggil `enforce_org_scope(principal,
declared_org, settings)` — reuse `OrgUnitResolver`/`OrgUnitGuard` (SECMIG-P4) yang sudah
dipakai 6 endpoint lain di repo. Detail keamanan di §16.

### 9.3 Rename layar (belum diimplementasikan — direkomendasikan §18)

| Elemen | Rekomendasi |
|---|---|
| Judul modal | "Create User" → **"Grant Application Access"** |
| Tombol submit | "Create User" → **"Grant Access"** |
| Deskripsi modal | Tambahkan satu kalimat: "ECMP tidak membuat akun login. Layar ini memberikan akses ke Complaint Module bagi pengguna enterprise yang sudah ada." |

---

## 10. Field Analysis (Requirement 6)

### 10.1 Informasi Enterprise — **read-only, ditampilkan saja**

Field berikut berasal dari **Enterprise Directory**. ECMP hanya menampilkannya; tidak pernah
mengubah, memvalidasi ulang, atau menjadikannya sumber kebenaran.

| Field | Ada di repo hari ini? | Catatan |
|---|---|---|
| Employee ID | **Ya** — `username` (ID 16 digit) | Sekaligus Enterprise User Reference (§3.2) |
| Full Name | **Ya** — `displayName` / `full_name` | Read-only di UI |
| Email | **Ya** — `email` | Read-only di UI |
| Department | **Tidak** | Target read-only; tiba bersama Enterprise API (§5.1) |
| Position | **Tidak** | Target read-only; tiba bersama Enterprise API (§5.1) |
| Organization | **Tidak** | Target read-only; tiba bersama Enterprise API (§5.1) |

Tiga baris terakhir sengaja tidak ditambahkan ke desain layar sebagai field yang "ada" —
repo tidak memuatnya, dan mengarang field bukan bagian dari pekerjaan ini.

### 10.2 Data otorisasi ECMP — dapat diputuskan administrator

| Field | Milik ECMP? | Rekomendasi |
|---|---|---|
| Pencarian direktori / pemilihan orang | Ya — titik masuk registrasi | **Pertahankan** |
| Unit | Ya — Authorization scope | **Pertahankan** — sudah read-only/derived (§9.2) |
| Peran (Role) | Ya — ADR-008 Role-Permission SoT | **Pertahankan** — satu-satunya keputusan bebas administrator |
| Permission | Ya — diturunkan dari Role (ADR-008) | Tidak ada field terpisah; konsekuensi otomatis |
| Status aktif (`isActive`) | Ya — toggle akses lokal ECMP (bukan Entitlement, §4) | **Pertahankan**, dengan label yang membedakannya dari Entitlement |
| **Password** | **Tidak** — Enterprise (§2) | **Hapus** — repository gap §5.2 |

Tidak ada field baru yang direkomendasikan atau diciptakan di luar yang sudah ada di kode.

---

## 11. Removed Fields (Requirement 3)

| Konsep yang diminta dihapus | Status di kode saat ini | Keterangan |
|---|---|---|
| Password | **Masih ada** (`CreateUserModal.tsx:391-402`) | **Repository gap §5.2** |
| Confirm Password | Tidak pernah ada di kode | Tidak ada yang perlu dihapus |
| Temporary Password (field UI terpisah) | Tidak ada sebagai field; hanya representasi via `force_password_change` (hint teks di bawah password) | Akan hilang bersamaan saat password field dihapus |
| Email Verification | Tidak ada di layar ini | Tidak ada yang perlu dihapus |
| Forgot Password | Tidak ada di layar ini (ada di layar terpisah — `/forgot-password`) | Di luar cakupan modul Create User |
| Reset Password | Tidak ada di layar Create User (ada endpoint terpisah `users:reset_password`) | Di luar cakupan modul Create User; item terpisah untuk direview jika Mode B diaktifkan |
| Activation Link | Tidak pernah ada di kode | Tidak ada yang perlu dihapus |
| Login | Tidak ada di layar ini | Tidak ada yang perlu dihapus |

**Mengapa konsep-konsep ini di luar tanggung jawab ECMP.** Setiap satu dari delapan konsep di
atas menjawab pertanyaan *"bagaimana pengguna membuktikan dirinya"* (autentikasi) — bukan
*"apa yang pengguna ini boleh lakukan di ECMP"* (otorisasi). Seluruhnya berada di kolom
Enterprise pada batas terkunci §2. Mencampur keduanya di satu layar membuat batas tanggung
jawab kabur bagi siapa pun yang membaca kode ini kelak — termasuk auditor yang memverifikasi
bahwa ECMP benar-benar tidak menyimpan kredensial.

---

## 12. Business Rules

Hanya aturan yang berada dalam kepemilikan ECMP.

| ID | Aturan | Status |
|---|---|---|
| BR-01 | ECMP tidak membuat identitas Enterprise; pemberian akses hanya berlaku untuk Enterprise User yang sudah ada di direktori. | Berlaku (desain saat ini) |
| BR-01a | ECMP tidak menduplikasi master data Enterprise — yang disimpan hanya **referensi** (§3.2). | Target — belum terpenuhi (§5.1) |
| BR-01b | ECMP tidak pernah mengubah identitas Enterprise User. | **Diimplementasikan** (field identitas read-only) |
| BR-02 | Employee ID, nama, dan email berasal dari direktori dan tidak dapat diubah dari layar ini. | **Diimplementasikan** |
| BR-03 | Unit pengguna baru ditentukan dari profil administrator yang login (`branchId` miliknya), bukan dipilih bebas. | **Diimplementasikan** (§9.2) |
| BR-04 | Server menolak permintaan bila Unit yang dideklarasikan tidak sama dengan Unit administrator (fail-closed, hanya aktif saat `ECMP_AUTH_MODE=jwt`). | **Diimplementasikan** (§16) |
| BR-05 | Peran ber-scope unit wajib memiliki Unit; peran kantor pusat wajib tidak memiliki Unit. | Sudah ada — `users/service.py:150-163` |
| BR-06 | Administrator tidak dapat memberikan peran yang setara atau lebih tinggi dari perannya sendiri. | Sudah ada — UAT-020 |
| BR-07 | `isActive` adalah toggle akses lokal ECMP, dievaluasi **setelah** Enterprise Entitlement Gate (ADR-017) — bukan pengganti keputusan entitlement. | Berlaku secara arsitektural; belum dikomunikasikan di UI (§7 T-3) |
| BR-08 | Password tidak boleh diminta, ditampilkan, atau disimpan oleh administrator ECMP. | **Belum berlaku** — repository gap §5.2 |

Tidak ada aturan Enterprise Identity yang didefinisikan di sini (format kredensial, kebijakan
MFA, siklus hidup akun enterprise, aturan direktori) — seluruhnya di luar batas terkunci §2.

---

## 13. Authorization Flow

Perbedaan Authentication vs Application Authorization, dipetakan langsung ke pipeline yang
sudah ditetapkan ADR-016 → ADR-015 → ADR-017/014 → ADR-008 (dikutip ADR-018 §273):

| Tahap | Pertanyaan yang dijawab | Pemilik | Jawaban dipakai ECMP sebagai |
|---|---|---|---|
| Trust (ADR-016) | Apakah presentasi identitas ini otentik? | Enterprise | Prasyarat — bukan keputusan ECMP |
| Identity Contract (ADR-015) | Siapa subjek ini? | Enterprise | Klaim yang diterima, bukan diverifikasi ulang |
| **Entitlement Gate (ADR-017)** | **Apakah subjek ini diizinkan masuk modul ECMP sama sekali?** | **Enterprise** | Gerbang admisi — dievaluasi **sebelum** ECMP memetakan apa pun |
| Complaint Roles mapping (ADR-014) | Peran ECMP apa yang berlaku untuk subjek ini? | **ECMP** | **Ini yang diputuskan layar Create User** |
| Permissions (ADR-008) | Apa yang boleh dilakukan peran ini? | **ECMP** | Konsekuensi otomatis dari Peran yang dipilih |

**Authentication** menjawab "siapa dan apakah ia otentik" — seluruhnya di atas garis
Entitlement Gate, seluruhnya Enterprise. **Application Authorization** menjawab "apa yang
boleh dilakukan di ECMP" — dua baris terakhir tabel, seluruhnya ECMP. Layar Create User
beroperasi murni di dua baris terakhir. Ia tidak pernah menyentuh, meniru, atau
menggantikan Entitlement Gate.

---

## 14. User Journey

Enterprise User **sudah ada**. Administrator hanya memberi akses ECMP.

| # | Langkah | Yang terlihat | Yang diputuskan administrator |
|---|---|---|---|
| 1 | Buka "Beri Akses Aplikasi" | Panel pencarian Enterprise Directory | — |
| 2 | **Search Enterprise User** | Hasil pencarian direktori | — |
| 3 | **Select Enterprise User** | Kandidat terpilih | Orang yang benar |
| 4 | **Review Enterprise Information (Read Only)** | Employee ID · Nama · Email — dari direktori, tidak dapat diubah (§10.1) | — |
| 5 | **Assign Role** | Daftar peran yang boleh diberikan aktor (UAT-020) | **Satu-satunya keputusan bebas** |
| 6 | **Assign Unit** | Terisi otomatis dari cakupan administrator, terkunci (§9.2) | — (diturunkan sistem) |
| 7 | **Assign Permission** | Ditampilkan sebagai konsekuensi Role (ADR-008), bukan pilihan terpisah | — |
| 8 | **Save ECMP Membership** | Ringkasan: Enterprise User Reference + Role + Unit + Status | — |
| 9 | Server memvalidasi & mencatat | Status akses + jejak audit | — |
| 10 | **Enterprise User dapat mengakses ECMP** | — | — |

Dua catatan kejujuran terhadap kode hari ini: langkah 2–4 masih berjalan di atas seed JSON
lokal, bukan Enterprise API (§5.1); dan langkah 8 masih menyertakan field password (§5.2).
Tabel ini menggambarkan alur target, bukan klaim bahwa keduanya sudah beres.

---

## 15. ASCII Workflow

```
        ENTERPRISE (di luar ECMP — tidak didesain di sini)
        Identity · Authentication · SSO · Directory · User Lifecycle
                            │
                            │  Enterprise User sudah ada & terautentikasi
                            ▼
┌───────────────────────────────────────────────────────────┐
│ ADMINISTRATOR membuka "Beri Akses Aplikasi"                 │
└───────────────────────────┬───────────────────────────────┘
                            ▼
             ┌──────────────────────────────────┐
             │ SEARCH Enterprise User            │
             │ (sumber: Enterprise Directory     │
             │  via Enterprise API — §5.1)       │
             └────────────┬───────────────────────┘
                           ▼
             ┌──────────────────────────────────┐
             │ SELECT Enterprise User            │
             └────────────┬───────────────────────┘
                           ▼
             ┌──────────────────────────────────┐
             │ REVIEW Enterprise Information     │
             │ 🔒 READ ONLY — ditampilkan saja   │
             │ Employee ID · Nama · Email        │
             │ (Department/Position/Organization │
             │  menyusul via Enterprise API)     │
             └────────────┬───────────────────────┘
                           ▼
             ┌──────────────────────────────────┐
             │ ASSIGN ROLE                       │
             │ (difilter: peran ≤ peran admin)   │
             └────────────┬───────────────────────┘
                           ▼
             ┌──────────────────────────────────┐
             │ ASSIGN UNIT                       │
             │ = f(cakupan otorisasi admin)      │
             │ 🔒 diturunkan, tidak dapat diubah │
             └────────────┬───────────────────────┘
                           ▼
             ┌──────────────────────────────────┐
             │ ASSIGN PERMISSION                 │
             │ (konsekuensi otomatis dari Role,  │
             │  ADR-008 — bukan pilihan terpisah)│
             └────────────┬───────────────────────┘
                           ▼
             ┌──────────────────────────────────┐
             │ SERVER — validasi gabungan        │
             │  · Unit diturunkan, bukan diterima│
             │    dari klien                     │
             │  · Peran × Unit konsisten          │
             │  · Peran ≤ peran admin             │
             └────────────┬───────────────────────┘
                           │
                    valid? ── TIDAK ──▶ TOLAK + audit
                           │
                          YA
                           ▼
             ┌──────────────────────────────────┐
             │ SAVE ECMP MEMBERSHIP              │
             │ Disimpan: Enterprise User Ref ·   │
             │ Role · Unit · Status              │
             │ TIDAK ADA kredensial & TIDAK ADA  │
             │ salinan master data Enterprise    │
             └────────────┬───────────────────────┘
                           ▼
             ┌──────────────────────────────────┐
             │ AUDIT: aktor · subjek · peran ·   │
             │ unit · waktu                      │
             └────────────┬───────────────────────┘
                           ▼
        Enterprise User dapat mengakses ECMP

Catatan: Entitlement Gate Enterprise (ADR-017) — "apakah subjek boleh masuk modul ECMP
sama sekali" — terjadi SEBELUM diagram ini, di Identity Adapter, dan bukan langkah yang
ECMP putuskan atau tampilkan di layar ini.
```

---

## 16. Security Review

Fokus murni pada lima hal yang diminta — Authorization, Scope Validation, Role Validation,
Permission Validation, Least Privilege. Autentikasi tidak direview (di luar cakupan).

### 16.1 Authorization & Scope Validation — **sudah diimplementasikan**

`backend/app/modules/users/router.py`, fungsi `create_user`: setelah permission check
(`require_permissions("users:create")`), server meresolusi `Branch.code` dari `branch_id`
yang dideklarasikan, lalu memanggil `enforce_org_scope(principal, declared_org, settings)`.
Ini reuse langsung dari `OrgUnitResolver`/`OrgUnitGuard` (SECMIG-P4) — mekanisme yang sama
persis dipakai 6 router lain (complaints, escalations, cm_batch1, cm_case, assignments,
resolutions). Perilaku:

- Unit administrator (`principal.org_unit_id`, klaim JWT) ≠ Unit yang dideklarasikan →
  **403 `ORG_SCOPE_DENIED`**.
- Klaim Unit administrator kosong → **403** (fail-closed, bukan default terbuka).
- Tidak aktif di Mode A (`ECMP_AUTH_MODE=dev`) — `org_scope_enforcement_enabled()`
  mengembalikan `False`, sehingga perilaku Mode A yang sudah ada tidak berubah.

Diverifikasi dengan test HTTP end-to-end (`tests/test_secmig_p4_org_scope.py`): unit sama →
201; unit berbeda → 403; klaim hilang → 403; Mode A → tidak terpengaruh.

**Batasan yang diwarisi (bukan celah baru):** `OrgUnitGuard` adalah pembanding 1:1, tanpa
bypass GLOBAL/kantor-pusat. Administrator kantor pusat yang membuat pengguna tanpa Unit
(`branch_id=None`) akan **ditolak** begitu Mode B enforcement aktif — perilaku ini identik
dengan bagaimana CM Batch 1 sudah memperlakukan `recordingUnitId` opsional hari ini, bukan
aturan baru yang diciptakan untuk layar ini. Dicatat sebagai item terbuka untuk keputusan
produk (apakah kantor pusat perlu jalur berbeda), bukan diselesaikan diam-diam.

### 16.2 Role Validation — sudah ada, tidak diubah

`_ensure_assignable_role` (UAT-020, `users/service.py:108-120`) menolak permintaan yang
memberi peran setara atau lebih tinggi dari peran aktor. Tidak disentuh oleh redesign ini.

### 16.3 Permission Validation

Permission diturunkan sepenuhnya dari Peran (ADR-008 Role-Permission Matrix) — tidak ada
pemilihan permission terpisah di layar ini, sesuai repo saat ini. Tidak ada celah baru yang
ditemukan pada dimensi ini.

### 16.4 Least Privilege

Sebelum §16.1 diimplementasikan, least privilege hanya ditegakkan pada satu sumbu (Peran).
Sumbu kedua (Unit) memiliki celah aktif — administrator dapat menempatkan pengguna di Unit
mana pun. **Celah ini sudah ditutup** oleh implementasi §16.1: kedua sumbu (Peran × Unit)
kini konsisten dan ditegakkan bersama sebelum commit.

### 16.5 Item yang tidak direview di sini

Kekuatan kebijakan password, keamanan token SSO, dan siklus hidup sesi enterprise **tidak**
direview — seluruhnya di kolom Enterprise pada batas terkunci §2.

---

## 17. Expected Benefits

| Pemangku kepentingan | Manfaat |
|---|---|
| **CTO** | Batas ECMP vs Enterprise eksplisit dan dapat diverifikasi langsung dari kode; celah otorisasi lintas-unit sudah tertutup dengan komponen yang sudah teraudit sebelumnya |
| **Product Owner** | Layar mencerminkan model bisnis yang sudah disepakati (ECMP = otorisasi, bukan identitas), siap dikomunikasikan ke pelanggan enterprise |
| **Security** | Least privilege ditegakkan pada kedua sumbu (Peran, Unit); repository gap pada penghapusan password dilaporkan secara eksplisit, bukan disembunyikan sebagai "selesai" |
| **UI/UX** | Form dua keputusan nyata (Peran; Unit turunan otomatis), field yang tersisa masing-masing dapat dijelaskan kepemilikannya |
| **Enterprise Architecture Review** | Tidak ada satu pun kapabilitas Enterprise yang ditiru atau didesain ulang; setiap keputusan ECMP dipetakan eksplisit ke posisinya di pipeline ADR-016→015→017/014→008 |

---

## 18. Final Recommendation

1. **Rename layar, aksi, dan seluruh kosakata yang menyiratkan pembuatan akun** ("Create
   User" → "Grant Application Access", §9.3), mengikuti makna bisnis resmi di §1. Murah,
   tidak berisiko, memperkuat batas domain yang sudah benar di kode.
2. **Requirement 1 dan 2 sudah selesai di kode** — tidak perlu tindakan lanjutan kecuali
   menyelesaikan item terbuka §16.1 (jalur administrator kantor pusat) sebagai keputusan
   produk terpisah.
3. **Requirement 3 (hapus field otentikasi) tetap repository gap §5.2.** Tindakan yang tepat:
   bawa temuan itu ke Architecture Board (rujukan eksplisit di kode: *"Mode B unlock remains
   gated by Architecture Board (C-7 / C-B6-1)"*) — mengubah gerbang
   `require_local_credential_auth` dan sifat wajib `UserCreateRequest.password` bukan
   keputusan desain UX.
4. **Integrasi Enterprise Directory API tetap repository gap §5.1** — dikerjakan **hanya
   setelah** dukungan repository dan milestone implementasi resmi tersedia. Sampai saat itu,
   seed lokal tetap dipakai sebagai fixture lab dan **tidak boleh** disebut sebagai integrasi
   Enterprise. Field Department/Position/Organization menyusul bersama integrasi ini, bukan
   sebelumnya.
5. **Tambahkan penjelasan on-screen** yang membedakan `isActive` (toggle akses lokal ECMP)
   dari Entitlement Enterprise (ADR-017), menutup BP-3/T-3 — perubahan teks kecil, risiko
   rendah, menutup potensi kesalahpahaman audit.
6. **Jangan mulai pekerjaan apa pun di kolom Enterprise pada batas terkunci §2** — Identity,
   SSO, Directory, Authentication, Enterprise API, User Management, Password, Email, MFA,
   Login, User Lifecycle. Tidak ada temuan di dokumen ini yang mengubah itu.

> *Future Work — Di luar ruang lingkup Complaint Management Module: seluruh kolom Enterprise
> pada batas terkunci §2 (Identity · SSO · Directory · Authentication · Enterprise APIs ·
> User Management · Password · Email · MFA · Login · User Lifecycle). Tidak dibahas di
> dokumen ini.*
